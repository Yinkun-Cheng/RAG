"""
Integration Services

This module provides clients for external services:
- BRConnectorClient: Claude API through BRConnector
- VolcanoEmbeddingService: Volcano Engine Embedding API
- WeaviateClient: Weaviate vector database
"""

from .brconnector_client import BRConnectorClient, BRConnectorError, RateLimitError, APIError
from .volcano_embedding import VolcanoEmbeddingService, VolcanoEmbeddingError
from .weaviate_client import WeaviateClient, WeaviateClientError

__all__ = [
    "BRConnectorClient",
    "BRConnectorError",
    "RateLimitError",
    "APIError",
    "VolcanoEmbeddingService",
    "VolcanoEmbeddingError",
    "WeaviateClient",
    "WeaviateClientError",
]
