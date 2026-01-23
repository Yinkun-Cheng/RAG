"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from app.config import Settings
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        BRCONNECTOR_API_KEY="test-key",
        VOLCANO_EMBEDDING_API_KEY="test-key",
        VOLCANO_EMBEDDING_ENDPOINT="http://test-endpoint"
    )
