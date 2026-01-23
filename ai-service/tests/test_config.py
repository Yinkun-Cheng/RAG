"""Tests for configuration management"""

import pytest
import os
from app.config import Settings, validate_settings


def test_settings_defaults():
    """Test default settings values"""
    settings = Settings(
        BRCONNECTOR_API_KEY="test-key",
        VOLCANO_EMBEDDING_API_KEY="test-key",
        VOLCANO_EMBEDDING_ENDPOINT="http://test"
    )
    
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 5000
    assert settings.LOG_LEVEL == "INFO"


def test_settings_from_env(monkeypatch):
    """Test loading settings from environment variables"""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("BRCONNECTOR_API_KEY", "test-key")
    monkeypatch.setenv("VOLCANO_EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("VOLCANO_EMBEDDING_ENDPOINT", "http://test")
    
    settings = Settings()
    
    assert settings.ENVIRONMENT == "production"
    assert settings.DEBUG is False
    assert settings.PORT == 8000
    assert settings.LOG_LEVEL == "DEBUG"


def test_cors_origins_parsing():
    """Test CORS origins parsing from comma-separated string"""
    settings = Settings(
        CORS_ORIGINS="http://localhost:3000,http://localhost:8080,https://example.com",
        BRCONNECTOR_API_KEY="test-key",
        VOLCANO_EMBEDDING_API_KEY="test-key",
        VOLCANO_EMBEDDING_ENDPOINT="http://test"
    )
    
    origins = settings.cors_origins_list
    assert len(origins) == 3
    assert "http://localhost:3000" in origins
    assert "https://example.com" in origins


def test_validate_settings_missing_brconnector_key(monkeypatch):
    """Test validation fails when BRConnector API key is missing"""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("BRCONNECTOR_API_KEY", "")
    monkeypatch.setenv("VOLCANO_EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("VOLCANO_EMBEDDING_ENDPOINT", "http://test")
    
    # Reload settings module to pick up new env vars
    from importlib import reload
    import app.config
    reload(app.config)
    
    with pytest.raises(ValueError) as exc_info:
        app.config.validate_settings()
    
    assert "BRCONNECTOR_API_KEY" in str(exc_info.value)


def test_validate_settings_missing_volcano_key(monkeypatch):
    """Test validation fails when Volcano API key is missing"""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("BRCONNECTOR_API_KEY", "test-key")
    monkeypatch.setenv("VOLCANO_EMBEDDING_API_KEY", "")
    monkeypatch.setenv("VOLCANO_EMBEDDING_ENDPOINT", "http://test")
    
    from importlib import reload
    import app.config
    reload(app.config)
    
    with pytest.raises(ValueError) as exc_info:
        app.config.validate_settings()
    
    assert "VOLCANO_EMBEDDING_API_KEY" in str(exc_info.value)


def test_validate_settings_all_required_present(monkeypatch):
    """Test validation passes when all required settings are present"""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("BRCONNECTOR_API_KEY", "test-key")
    monkeypatch.setenv("VOLCANO_EMBEDDING_API_KEY", "test-key")
    monkeypatch.setenv("VOLCANO_EMBEDDING_ENDPOINT", "http://test")
    
    from importlib import reload
    import app.config
    reload(app.config)
    
    # Should not raise any exception
    try:
        app.config.validate_settings()
    except ValueError:
        pytest.fail("validate_settings() raised ValueError unexpectedly")
