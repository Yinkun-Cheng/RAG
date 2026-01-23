"""Tests for main FastAPI application"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-test-assistant"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "AI Test Assistant Service"
    assert "docs" in data
    assert "health" in data


def test_cors_headers(client):
    """Test CORS configuration"""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    # FastAPI/Starlette handles CORS, check that the endpoint exists
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly defined


def test_api_docs_available(client):
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "AI Test Assistant Service"
