"""
Configuration Management

Loads configuration from environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # BRConnector (Claude API)
    BRCONNECTOR_API_KEY: str = ""
    BRCONNECTOR_BASE_URL: str = "https://d106f995v5mndm.cloudfront.net"
    BRCONNECTOR_MODEL: str = "claude-4-5-sonnet"
    
    # Volcano Engine Embedding API
    VOLCANO_EMBEDDING_API_KEY: str = ""
    VOLCANO_EMBEDDING_ENDPOINT: str = ""
    
    # Weaviate
    WEAVIATE_URL: str = "http://localhost:8009"
    
    # Go Backend
    GO_BACKEND_URL: str = "http://localhost:8080"
    
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
