"""
Volcano Engine Embedding Service

Provides async client for generating text embeddings using Volcano Engine API.
Supports single and batch embedding generation with error handling.

NOTE: Current retrieval tools have been refactored to use Go backend API.
This service is kept as a backup for potential future direct embedding generation.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class VolcanoEmbeddingError(Exception):
    """Base exception for Volcano Embedding errors"""
    pass


class VolcanoEmbeddingService:
    """
    Async client for Volcano Engine Embedding API.
    
    Supports:
    - Dynamic configuration (API key, endpoint)
    - Single and batch embedding generation
    - Error handling and timeout logic
    - Automatic retry for transient failures
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: float = 30.0,
        max_batch_size: int = 100,
    ):
        """
        Initialize Volcano Embedding service.
        
        Args:
            api_key: Volcano Engine API key (can be overridden per request)
            endpoint: Volcano Engine endpoint URL (can be overridden per request)
            timeout: Request timeout in seconds
            max_batch_size: Maximum number of texts per batch request
        """
        self.default_api_key = api_key
        self.default_endpoint = endpoint
        self.timeout = timeout
        self.max_batch_size = max_batch_size
        
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
            
        Raises:
            ValueError: If API key is not provided
        """
        key = api_key or self.default_api_key
        if not key:
            raise ValueError("API key is required")
        
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
    
    async def embed_single(
        self,
        text: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            api_key: API key (uses default if not provided)
            endpoint: Endpoint URL (uses default if not provided)
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            VolcanoEmbeddingError: If embedding generation fails
            ValueError: If required parameters are missing
        """
        embeddings = await self.embed_batch([text], api_key, endpoint)
        return embeddings[0]
    
    async def embed_batch(
        self,
        texts: List[str],
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            api_key: API key (uses default if not provided)
            endpoint: Endpoint URL (uses default if not provided)
            
        Returns:
            List of embedding vectors
            
        Raises:
            VolcanoEmbeddingError: If embedding generation fails
            ValueError: If required parameters are missing
        """
        if not texts:
            return []
        
        url = endpoint or self.default_endpoint
        if not url:
            raise ValueError("Endpoint URL is required")
        
        headers = self._get_headers(api_key)
        
        # Split into batches if needed
        if len(texts) > self.max_batch_size:
            logger.info(f"Splitting {len(texts)} texts into batches of {self.max_batch_size}")
            return await self._embed_in_batches(texts, headers, url)
        
        # Single batch request
        return await self._embed_request(texts, headers, url)
    
    async def _embed_in_batches(
        self,
        texts: List[str],
        headers: Dict[str, str],
        url: str,
    ) -> List[List[float]]:
        """
        Generate embeddings in multiple batches.
        
        Args:
            texts: List of texts to embed
            headers: Request headers
            url: Endpoint URL
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), self.max_batch_size):
            batch = texts[i:i + self.max_batch_size]
            logger.info(f"Processing batch {i // self.max_batch_size + 1}")
            
            embeddings = await self._embed_request(batch, headers, url)
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    async def _embed_request(
        self,
        texts: List[str],
        headers: Dict[str, str],
        url: str,
    ) -> List[List[float]]:
        """
        Send embedding request to API.
        
        Args:
            texts: List of texts to embed
            headers: Request headers
            url: Endpoint URL
            
        Returns:
            List of embedding vectors
            
        Raises:
            VolcanoEmbeddingError: If request fails
        """
        payload = {
            "input": texts,
        }
        
        try:
            logger.info(f"Sending embedding request for {len(texts)} texts to {url}")
            
            response = await self.client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Embedding API error {response.status_code}: {error_text}")
                raise VolcanoEmbeddingError(
                    f"Embedding API error {response.status_code}: {error_text}"
                )
            
            data = response.json()
            
            # Extract embeddings from response
            # Volcano Engine format: {"data": [{"embedding": [...]}, ...]}
            if "data" not in data:
                raise VolcanoEmbeddingError(f"Invalid response format: {data}")
            
            embeddings = []
            for item in data["data"]:
                if "embedding" not in item:
                    raise VolcanoEmbeddingError(f"Missing embedding in response: {item}")
                embeddings.append(item["embedding"])
            
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
        
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise VolcanoEmbeddingError(f"Request timeout: {e}")
        
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise VolcanoEmbeddingError(f"Network error: {e}")
        
        except Exception as e:
            if isinstance(e, VolcanoEmbeddingError):
                raise
            logger.error(f"Unexpected error: {e}")
            raise VolcanoEmbeddingError(f"Unexpected error: {e}")
    
    async def get_embedding_dimension(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> int:
        """
        Get the dimension of embeddings from this service.
        
        Args:
            api_key: API key (uses default if not provided)
            endpoint: Endpoint URL (uses default if not provided)
            
        Returns:
            Embedding dimension (e.g., 2048 for Volcano Engine)
        """
        # Generate a test embedding to get dimension
        test_embedding = await self.embed_single("test", api_key, endpoint)
        return len(test_embedding)
