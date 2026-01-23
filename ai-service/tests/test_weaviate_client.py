"""
Unit tests for WeaviateClient
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from weaviate.exceptions import WeaviateBaseError
from app.integration.weaviate_client import (
    WeaviateClient,
    WeaviateClientError,
)


@pytest.fixture
def client():
    """Create a test client"""
    return WeaviateClient(url="http://test:8009")


@pytest.fixture
def mock_weaviate_client():
    """Create a mock Weaviate client"""
    mock = MagicMock()
    mock.is_ready.return_value = True
    mock._connection.url = "http://test:8009"
    return mock


def test_client_initialization():
    """Test client initialization with default values"""
    client = WeaviateClient()
    
    assert client.default_url == "http://localhost:8009"
    assert client.timeout == 30


def test_client_context_manager(client):
    """Test client as context manager"""
    with client as c:
        assert c is not None
    
    # Client should be closed after context exit
    assert client._client is None


@patch("app.integration.weaviate_client.weaviate.Client")
def test_get_client_success(mock_weaviate_class, client, mock_weaviate_client):
    """Test successful client creation"""
    mock_weaviate_class.return_value = mock_weaviate_client
    
    result = client._get_client()
    
    assert result == mock_weaviate_client
    mock_weaviate_class.assert_called_once()


@patch("app.integration.weaviate_client.weaviate.Client")
def test_get_client_not_ready(mock_weaviate_class, client):
    """Test client creation when server is not ready"""
    mock = MagicMock()
    mock.is_ready.return_value = False
    mock_weaviate_class.return_value = mock
    
    with pytest.raises(WeaviateClientError, match="is not ready"):
        client._get_client()


@patch("app.integration.weaviate_client.weaviate.Client")
def test_get_client_connection_error(mock_weaviate_class, client):
    """Test client creation with connection error"""
    mock_weaviate_class.side_effect = WeaviateBaseError("Connection failed")
    
    with pytest.raises(WeaviateClientError, match="Failed to connect"):
        client._get_client()


@patch("app.integration.weaviate_client.weaviate.Client")
@pytest.mark.asyncio
async def test_search_similar_success(mock_weaviate_class, client, mock_weaviate_client):
    """Test successful vector search"""
    mock_weaviate_class.return_value = mock_weaviate_client
    
    # Mock query chain
    mock_query = MagicMock()
    mock_query.do.return_value = {
        "data": {
            "Get": {
                "TestClass": [
                    {"id": "1", "title": "Result 1", "_additional": {"certainty": 0.9}},
                    {"id": "2", "title": "Result 2", "_additional": {"certainty": 0.8}},
                ]
            }
        }
    }
    
    mock_weaviate_client.query.get.return_value.with_near_vector.return_value.with_limit.return_value.with_additional.return_value = mock_query
    
    results = await client.search_similar(
        class_name="TestClass",
        vector=[0.1, 0.2, 0.3],
        limit=10,
        threshold=0.7,
    )
    
    assert len(results) == 2
    assert results[0]["title"] == "Result 1"
    assert results[1]["title"] == "Result 2"


@pytest.mark.asyncio
async def test_search_similar_no_class_name(client):
    """Test search without class name raises error"""
    with pytest.raises(ValueError, match="Class name is required"):
        await client.search_similar(
            class_name="",
            vector=[0.1, 0.2],
        )


@pytest.mark.asyncio
async def test_search_similar_no_vector(client):
    """Test search without vector raises error"""
    with pytest.raises(ValueError, match="Query vector is required"):
        await client.search_similar(
            class_name="TestClass",
            vector=[],
        )


@pytest.mark.asyncio
async def test_search_similar_invalid_limit(client):
    """Test search with invalid limit raises error"""
    with pytest.raises(ValueError, match="Limit must be positive"):
        await client.search_similar(
            class_name="TestClass",
            vector=[0.1, 0.2],
            limit=0,
        )


@pytest.mark.asyncio
async def test_search_similar_invalid_threshold(client):
    """Test search with invalid threshold raises error"""
    with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
        await client.search_similar(
            class_name="TestClass",
            vector=[0.1, 0.2],
            threshold=1.5,
        )


@patch("app.integration.weaviate_client.weaviate.Client")
@pytest.mark.asyncio
async def test_search_similar_empty_results(mock_weaviate_class, client, mock_weaviate_client):
    """Test search with no results"""
    mock_weaviate_class.return_value = mock_weaviate_client
    
    # Mock query chain with empty results
    mock_query = MagicMock()
    mock_query.do.return_value = {
        "data": {
            "Get": {
                "TestClass": []
            }
        }
    }
    
    mock_weaviate_client.query.get.return_value.with_near_vector.return_value.with_limit.return_value.with_additional.return_value = mock_query
    
    results = await client.search_similar(
        class_name="TestClass",
        vector=[0.1, 0.2, 0.3],
    )
    
    assert results == []


@patch("app.integration.weaviate_client.weaviate.Client")
@pytest.mark.asyncio
async def test_search_similar_weaviate_error(mock_weaviate_class, client, mock_weaviate_client):
    """Test search with Weaviate error"""
    mock_weaviate_class.return_value = mock_weaviate_client
    
    # Mock query chain that raises error
    mock_weaviate_client.query.get.side_effect = WeaviateBaseError("Search failed")
    
    with pytest.raises(WeaviateClientError, match="Search failed"):
        await client.search_similar(
            class_name="TestClass",
            vector=[0.1, 0.2, 0.3],
        )


@patch("app.integration.weaviate_client.weaviate.Client")
@pytest.mark.asyncio
async def test_search_similar_with_filter(mock_weaviate_class, client, mock_weaviate_client):
    """Test search with where filter"""
    mock_weaviate_class.return_value = mock_weaviate_client
    
    # Mock query chain
    mock_query = MagicMock()
    mock_query.do.return_value = {
        "data": {"Get": {"TestClass": []}}
    }
    
    mock_chain = (
        mock_weaviate_client.query.get.return_value
        .with_near_vector.return_value
        .with_limit.return_value
        .with_additional.return_value
        .with_where.return_value
    )
    mock_chain.do = mock_query.do
    
    where_filter = {"path": ["status"], "operator": "Equal", "valueString": "active"}
    
    await client.search_similar(
        class_name="TestClass",
        vector=[0.1, 0.2, 0.3],
        where_filter=where_filter,
    )
    
    # Verify with_where was called
    mock_weaviate_client.query.get.return_value.with_near_vector.return_value.with_limit.return_value.with_additional.return_value.with_where.assert_called_once_with(where_filter)


@patch("app.integration.weaviate_client.weaviate.Client")
@pytest.mark.asyncio
async def test_search_similar_hybrid_success(mock_weaviate_class, client, mock_weaviate_client):
    """Test successful hybrid search"""
    mock_weaviate_class.return_value = mock_weaviate_client
    
    # Mock query chain
    mock_query = MagicMock()
    mock_query.do.return_value = {
        "data": {
            "Get": {
                "TestClass": [
                    {"id": "1", "title": "Result 1", "_additional": {"score": 0.9}},
                ]
            }
        }
    }
    
    mock_weaviate_client.query.get.return_value.with_hybrid.return_value.with_limit.return_value.with_additional.return_value = mock_query
    
    results = await client.search_similar_hybrid(
        class_name="TestClass",
        query_text="test query",
        vector=[0.1, 0.2, 0.3],
        alpha=0.5,
        limit=10,
    )
    
    assert len(results) == 1
    assert results[0]["title"] == "Result 1"


@pytest.mark.asyncio
async def test_search_similar_hybrid_no_query_text(client):
    """Test hybrid search without query text raises error"""
    with pytest.raises(ValueError, match="Query text is required"):
        await client.search_similar_hybrid(
            class_name="TestClass",
            query_text="",
            vector=[0.1, 0.2],
        )


@pytest.mark.asyncio
async def test_search_similar_hybrid_invalid_alpha(client):
    """Test hybrid search with invalid alpha raises error"""
    with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
        await client.search_similar_hybrid(
            class_name="TestClass",
            query_text="test",
            vector=[0.1, 0.2],
            alpha=1.5,
        )


@patch("app.integration.weaviate_client.weaviate.Client")
def test_is_ready_success(mock_weaviate_class, client, mock_weaviate_client):
    """Test is_ready returns True when server is ready"""
    mock_weaviate_class.return_value = mock_weaviate_client
    mock_weaviate_client.is_ready.return_value = True
    
    assert client.is_ready() is True


@patch("app.integration.weaviate_client.weaviate.Client")
def test_is_ready_failure(mock_weaviate_class, client):
    """Test is_ready returns False on error"""
    mock_weaviate_class.side_effect = Exception("Connection failed")
    
    assert client.is_ready() is False


@patch("app.integration.weaviate_client.weaviate.Client")
@pytest.mark.asyncio
async def test_dynamic_url_configuration(mock_weaviate_class, client):
    """Test dynamic URL configuration per request"""
    mock1 = MagicMock()
    mock1.is_ready.return_value = True
    mock1._connection.url = "http://test1:8009"
    
    mock2 = MagicMock()
    mock2.is_ready.return_value = True
    mock2._connection.url = "http://test2:8009"
    
    mock_weaviate_class.side_effect = [mock1, mock2]
    
    # First request with default URL
    client1 = client._get_client()
    assert client1._connection.url == "http://test1:8009"
    
    # Second request with override URL
    client2 = client._get_client(url="http://test2:8009")
    assert client2._connection.url == "http://test2:8009"
