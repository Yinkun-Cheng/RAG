"""
Configuration Management

Loads configuration from environment variables.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:8080"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # BRConnector (Claude API)
    BRCONNECTOR_API_KEY: str = os.getenv("BRCONNECTOR_API_KEY", "")
    BRCONNECTOR_BASE_URL: str = os.getenv(
        "BRCONNECTOR_BASE_URL",
        "https://d106f995v5mndm.cloudfront.net"
    )
    BRCONNECTOR_MODEL: str = os.getenv("BRCONNECTOR_MODEL", "claude-4-5-sonnet")
    
    # Volcano Engine Embedding API
    VOLCANO_EMBEDDING_API_KEY: str = os.getenv("VOLCANO_EMBEDDING_API_KEY", "")
    VOLCANO_EMBEDDING_ENDPOINT: str = os.getenv("VOLCANO_EMBEDDING_ENDPOINT", "")
    
    # Weaviate
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8009")
    
    # Go Backend
    GO_BACKEND_URL: str = os.getenv("GO_BACKEND_URL", "http://localhost:8080")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validate required settings
def validate_settings():
    """Validate that required settings are configured"""
    errors = []
    
    if not settings.BRCONNECTOR_API_KEY:
        errors.append("BRCONNECTOR_API_KEY is not set")
    
    if not settings.VOLCANO_EMBEDDING_API_KEY:
        errors.append("VOLCANO_EMBEDDING_API_KEY is not set")
    
    if not settings.VOLCANO_EMBEDDING_ENDPOINT:
        errors.append("VOLCANO_EMBEDDING_ENDPOINT is not set")
    
    if errors:
        raise ValueError(
            "Missing required configuration:\n" + "\n".join(f"  - {e}" for e in errors)
        )
