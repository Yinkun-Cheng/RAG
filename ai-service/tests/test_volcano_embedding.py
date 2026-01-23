"""
Unit tests for VolcanoEmbeddingService
"""

import pytest
import httpx
from unittest.mock import Mock, patch
from app.integration.volcano_embedding import (
    VolcanoEmbeddingService,
    VolcanoEmbeddingError,
)


@pytest.fixture
def service():
    """Create a test service"""
    return VolcanoEmbeddingService(
        api_key="test-key",
        endpoint="https://test.api.com/embeddings",
    )


@pytest.mark.asyncio
async def test_service_initialization():
    """Test service initialization with default values"""
    service = VolcanoEmbeddingService()
    
    assert service.timeout == 30.0
    assert service.max_batch_size == 100
    
    await service.close()


@pytest.mark.asyncio
async def test_service_context_manager():
    """Test service as async context manager"""
    async with VolcanoEmbeddingService(api_key="test-key") as service:
        assert service is not None
    
    # Service should be closed after context exit
    assert service.client.is_closed


@pytest.mark.asyncio
async def test_get_headers(service):
    """Test header generation"""
    headers = service._get_headers()
    
    assert headers["Authorization"] == "Bearer test-key"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_get_headers_with_override(service):
    """Test header generation with API key override"""
    headers = service._get_headers(api_key="override-key")
    
    assert headers["Authorization"] == "Bearer override-key"


@pytest.mark.asyncio
async def test_get_headers_no_key():
    """Test header generation without API key raises error"""
    service = VolcanoEmbeddingService()  # No API key
    
    with pytest.raises(ValueError, match="API key is required"):
        service._get_headers()
    
    await service.close()


@pytest.mark.asyncio
async def test_embed_single_success(service):
    """Test successful single embedding generation"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"embedding": [0.1, 0.2, 0.3, 0.4]}
        ]
    }
    
    with patch.object(service.client, "post", return_value=mock_response):
        embedding = await service.embed_single("test text")
        
        assert embedding == [0.1, 0.2, 0.3, 0.4]


@pytest.mark.asyncio
async def test_embed_batch_success(service):
    """Test successful batch embedding generation"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]},
        ]
    }
    
    with patch.object(service.client, "post", return_value=mock_response):
        embeddings = await service.embed_batch(["text1", "text2"])
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]


@pytest.mark.asyncio
async def test_embed_batch_empty_list(service):
    """Test embedding empty list returns empty list"""
    embeddings = await service.embed_batch([])
    
    assert embeddings == []


@pytest.mark.asyncio
async def test_embed_batch_large_batch(service):
    """Test embedding large batch splits into multiple requests"""
    service.max_batch_size = 2
    
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    
    # First batch
    mock_response.json.side_effect = [
        {"data": [{"embedding": [0.1]}, {"embedding": [0.2]}]},
        {"data": [{"embedding": [0.3]}]},
    ]
    
    with patch.object(service.client, "post", return_value=mock_response) as mock_post:
        embeddings = await service.embed_batch(["text1", "text2", "text3"])
        
        assert len(embeddings) == 3
        assert embeddings[0] == [0.1]
        assert embeddings[1] == [0.2]
        assert embeddings[2] == [0.3]
        
        # Verify two requests were made
        assert mock_post.call_count == 2


@pytest.mark.asyncio
async def test_embed_api_error(service):
    """Test API error handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch.object(service.client, "post", return_value=mock_response):
        with pytest.raises(VolcanoEmbeddingError, match="Embedding API error 500"):
            await service.embed_single("test")


@pytest.mark.asyncio
async def test_embed_timeout_error(service):
    """Test timeout error handling"""
    with patch.object(
        service.client,
        "post",
        side_effect=httpx.TimeoutException("Request timeout"),
    ):
        with pytest.raises(VolcanoEmbeddingError, match="Request timeout"):
            await service.embed_single("test")


@pytest.mark.asyncio
async def test_embed_network_error(service):
    """Test network error handling"""
    with patch.object(
        service.client,
        "post",
        side_effect=httpx.NetworkError("Network error"),
    ):
        with pytest.raises(VolcanoEmbeddingError, match="Network error"):
            await service.embed_single("test")


@pytest.mark.asyncio
async def test_embed_invalid_response_format(service):
    """Test invalid response format handling"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid": "format"}
    
    with patch.object(service.client, "post", return_value=mock_response):
        with pytest.raises(VolcanoEmbeddingError, match="Invalid response format"):
            await service.embed_single("test")


@pytest.mark.asyncio
async def test_embed_missing_embedding_field(service):
    """Test missing embedding field in response"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"no_embedding": "here"}]
    }
    
    with patch.object(service.client, "post", return_value=mock_response):
        with pytest.raises(VolcanoEmbeddingError, match="Missing embedding in response"):
            await service.embed_single("test")


@pytest.mark.asyncio
async def test_get_embedding_dimension(service):
    """Test getting embedding dimension"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"embedding": [0.1] * 2048}]  # 2048-dimensional embedding
    }
    
    with patch.object(service.client, "post", return_value=mock_response):
        dimension = await service.get_embedding_dimension()
        
        assert dimension == 2048


@pytest.mark.asyncio
async def test_dynamic_configuration(service):
    """Test dynamic configuration override"""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"embedding": [0.1, 0.2]}]
    }
    
    with patch.object(service.client, "post", return_value=mock_response) as mock_post:
        # Override configuration per request
        await service.embed_single(
            "test",
            api_key="override-key",
            endpoint="https://override.api.com/embed",
        )
        
        # Verify overridden values were used
        call_args = mock_post.call_args
        url = call_args.args[0]
        headers = call_args.kwargs["headers"]
        
        assert url == "https://override.api.com/embed"
        assert headers["Authorization"] == "Bearer override-key"


@pytest.mark.asyncio
async def test_embed_no_endpoint():
    """Test embedding without endpoint raises error"""
    service = VolcanoEmbeddingService(api_key="test-key")  # No endpoint
    
    with pytest.raises(ValueError, match="Endpoint URL is required"):
        await service.embed_single("test")
    
    await service.close()
