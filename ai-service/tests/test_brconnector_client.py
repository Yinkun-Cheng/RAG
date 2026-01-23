"""
Unit tests for BRConnectorClient
"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from app.integration.brconnector_client import (
    BRConnectorClient,
    BRConnectorError,
    RateLimitError,
    APIError,
)


@pytest.fixture
def client():
    """Create a test client"""
    return BRConnectorClient(
        api_key="test-key",
        base_url="https://test.api.com",
        model="test-model",
    )


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization with default values"""
    client = BRConnectorClient()
    
    assert client.default_base_url == "https://d106f995v5mndm.cloudfront.net"
    assert client.default_model == "claude-4-5-sonnet"
    assert client.timeout == 60.0
    assert client.max_retries == 3
    
    await client.close()


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager"""
    async with BRConnectorClient(api_key="test-key") as client:
        assert client is not None
    
    # Client should be closed after context exit
    assert client.client.is_closed


@pytest.mark.asyncio
async def test_get_headers(client):
    """Test header generation"""
    headers = client._get_headers()
    
    assert headers["Authorization"] == "Bearer test-key"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_get_headers_with_override(client):
    """Test header generation with API key override"""
    headers = client._get_headers(api_key="override-key")
    
    assert headers["Authorization"] == "Bearer override-key"


@pytest.mark.asyncio
async def test_get_headers_no_key():
    """Test header generation without API key raises error"""
    client = BRConnectorClient()  # No API key
    
    with pytest.raises(ValueError, match="API key is required"):
        client._get_headers()
    
    await client.close()


@pytest.mark.asyncio
async def test_chat_success(client):
    """Test successful chat request"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "msg_123",
        "content": [{"type": "text", "text": "Hello!"}],
        "model": "test-model",
    }
    
    with patch.object(client.client, "post", return_value=mock_response):
        messages = [{"role": "user", "content": "Hi"}]
        response = await client.chat(messages)
        
        assert response["id"] == "msg_123"
        assert response["content"][0]["text"] == "Hello!"


@pytest.mark.asyncio
async def test_chat_with_custom_params(client):
    """Test chat request with custom parameters"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "msg_123", "content": []}
    
    with patch.object(client.client, "post", return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Hi"}]
        await client.chat(
            messages,
            model="custom-model",
            temperature=0.5,
            max_tokens=2000,
        )
        
        # Verify the request payload
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        
        assert payload["model"] == "custom-model"
        assert payload["temperature"] == 0.5
        assert payload["max_tokens"] == 2000


@pytest.mark.asyncio
async def test_chat_rate_limit_error(client):
    """Test rate limit error handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"
    
    with patch.object(client.client, "post", return_value=mock_response):
        messages = [{"role": "user", "content": "Hi"}]
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            await client.chat(messages)


@pytest.mark.asyncio
async def test_chat_api_error(client):
    """Test API error handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch.object(client.client, "post", return_value=mock_response):
        messages = [{"role": "user", "content": "Hi"}]
        
        with pytest.raises(APIError, match="API error 500"):
            await client.chat(messages)


@pytest.mark.asyncio
async def test_chat_timeout_error(client):
    """Test timeout error handling"""
    with patch.object(
        client.client,
        "post",
        side_effect=httpx.TimeoutException("Request timeout"),
    ):
        messages = [{"role": "user", "content": "Hi"}]
        
        with pytest.raises(APIError, match="Request timeout"):
            await client.chat(messages)


@pytest.mark.asyncio
async def test_chat_network_error(client):
    """Test network error handling"""
    with patch.object(
        client.client,
        "post",
        side_effect=httpx.NetworkError("Network error"),
    ):
        messages = [{"role": "user", "content": "Hi"}]
        
        with pytest.raises(APIError, match="Network error"):
            await client.chat(messages)


@pytest.mark.asyncio
async def test_chat_simple(client):
    """Test simple chat interface"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "msg_123",
        "content": [{"type": "text", "text": "Hello, how can I help?"}],
    }
    
    with patch.object(client.client, "post", return_value=mock_response):
        response = await client.chat_simple("Hi there")
        
        assert response == "Hello, how can I help?"


@pytest.mark.asyncio
async def test_chat_simple_with_system(client):
    """Test simple chat with system message"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "msg_123",
        "content": [{"type": "text", "text": "Response"}],
    }
    
    with patch.object(client.client, "post", return_value=mock_response) as mock_post:
        await client.chat_simple(
            "User message",
            system="You are a helpful assistant",
        )
        
        # Verify system message was included
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        messages = payload["messages"]
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant"
        assert messages[1]["role"] == "user"


@pytest.mark.asyncio
async def test_handle_response_success(client):
    """Test successful response handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}
    
    result = client._handle_response(mock_response)
    
    assert result == {"result": "success"}


@pytest.mark.asyncio
async def test_handle_response_rate_limit(client):
    """Test rate limit response handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 429
    mock_response.text = "Rate limit"
    
    with pytest.raises(RateLimitError):
        client._handle_response(mock_response)


@pytest.mark.asyncio
async def test_handle_response_api_error(client):
    """Test API error response handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    
    with pytest.raises(APIError, match="API error 400"):
        client._handle_response(mock_response)


@pytest.mark.asyncio
async def test_dynamic_configuration(client):
    """Test dynamic configuration override"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "msg_123", "content": []}
    
    with patch.object(client.client, "post", return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Hi"}]
        
        # Override configuration per request
        await client.chat(
            messages,
            api_key="override-key",
            base_url="https://override.api.com",
            model="override-model",
        )
        
        # Verify overridden values were used
        call_args = mock_post.call_args
        url = call_args.args[0]
        headers = call_args.kwargs["headers"]
        payload = call_args.kwargs["json"]
        
        assert url == "https://override.api.com/v1/messages"
        assert headers["Authorization"] == "Bearer override-key"
        assert payload["model"] == "override-model"
