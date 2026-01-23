"""
BRConnector Client for Claude API

Provides async client for interacting with Claude API through BRConnector.
Supports streaming responses, retry logic, and dynamic configuration.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, AsyncIterator
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class BRConnectorError(Exception):
    """Base exception for BRConnector errors"""
    pass


class RateLimitError(BRConnectorError):
    """Raised when rate limit is exceeded"""
    pass


class APIError(BRConnectorError):
    """Raised when API returns an error"""
    pass


class BRConnectorClient:
    """
    Async client for Claude API through BRConnector.
    
    Supports:
    - Dynamic configuration (API key, model, base URL)
    - Streaming and non-streaming responses
    - Automatic retry with exponential backoff
    - Rate limit handling
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """
        Initialize BRConnector client.
        
        Args:
            api_key: BRConnector API key (can be overridden per request)
            base_url: BRConnector base URL (can be overridden per request)
            model: Default model name (can be overridden per request)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.default_api_key = api_key
        self.default_base_url = base_url or "https://d106f995v5mndm.cloudfront.net"
        self.default_model = model or "claude-4-5-sonnet"
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create async HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def _get_headers(self, api_key: Optional[str] = None) -> Dict[str, str]:
        """
        Get request headers.
        
        Args:
            api_key: API key (uses default if not provided)
            
        Returns:
            Headers dictionary
        """
        key = api_key or self.default_api_key
        if not key:
            raise ValueError("API key is required")
        
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Send chat completion request to Claude API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (uses default if not provided)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            api_key: API key (uses default if not provided)
            base_url: Base URL (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Response dictionary (non-streaming) or async iterator (streaming)
            
        Raises:
            RateLimitError: When rate limit is exceeded
            APIError: When API returns an error
            ValueError: When required parameters are missing
        """
        url = f"{base_url or self.default_base_url}/v1/messages"
        headers = self._get_headers(api_key)
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs,
        }
        
        logger.info(f"Sending chat request to {url} with model {payload['model']}")
        
        try:
            if stream:
                return self._stream_response(url, headers, payload)
            else:
                response = await self.client.post(url, json=payload, headers=headers)
                return self._handle_response(response)
        
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise APIError(f"Request timeout: {e}")
        
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise APIError(f"Network error: {e}")
    
    async def _stream_response(
        self,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream response from API.
        
        Args:
            url: API endpoint URL
            headers: Request headers
            payload: Request payload
            
        Yields:
            Parsed SSE events as dictionaries
        """
        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            
            if response.status_code >= 400:
                error_text = await response.aread()
                logger.error(f"API error {response.status_code}: {error_text}")
                raise APIError(f"API error {response.status_code}: {error_text.decode()}")
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    
                    if data == "[DONE]":
                        break
                    
                    try:
                        import json
                        event = json.loads(data)
                        yield event
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse SSE data: {data}")
                        continue
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle non-streaming API response.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed response dictionary
            
        Raises:
            RateLimitError: When rate limit is exceeded
            APIError: When API returns an error
        """
        if response.status_code == 429:
            logger.warning("Rate limit exceeded")
            raise RateLimitError("Rate limit exceeded")
        
        if response.status_code >= 400:
            error_text = response.text
            logger.error(f"API error {response.status_code}: {error_text}")
            raise APIError(f"API error {response.status_code}: {error_text}")
        
        try:
            return response.json()
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise APIError(f"Failed to parse response: {e}")
    
    async def chat_simple(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Simple chat interface for single-turn conversations.
        
        Args:
            prompt: User prompt
            system: Optional system message
            **kwargs: Additional parameters (model, temperature, etc.)
            
        Returns:
            Assistant's response text
        """
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat(messages, stream=False, **kwargs)
        
        # Extract text from response
        if "content" in response and len(response["content"]) > 0:
            return response["content"][0].get("text", "")
        
        return ""
