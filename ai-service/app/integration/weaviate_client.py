"""
Weaviate Client Wrapper

Provides async wrapper for Weaviate vector database operations.
Supports vector similarity search with error handling.
"""

import logging
from typing import List, Dict, Any, Optional
import weaviate
from weaviate.exceptions import WeaviateBaseError

logger = logging.getLogger(__name__)


class WeaviateClientError(Exception):
    """Base exception for Weaviate client errors"""
    pass


class WeaviateClient:
    """
    Async wrapper for Weaviate vector database client.
    
    Supports:
    - Vector similarity search
    - Connection pooling
    - Error handling for connection failures
    - Dynamic configuration
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Weaviate client.
        
        Args:
            url: Weaviate server URL (can be overridden per request)
            timeout: Request timeout in seconds
        """
        self.default_url = url or "http://localhost:8009"
        self.timeout = timeout
        self._client = None
    
    def _get_client(self, url: Optional[str] = None) -> weaviate.Client:
        """
        Get or create Weaviate client.
        
        Args:
            url: Weaviate server URL (uses default if not provided)
            
        Returns:
            Weaviate client instance
            
        Raises:
            WeaviateClientError: If connection fails
        """
        target_url = url or self.default_url
        
        try:
            # Create new client if URL changed or client doesn't exist
            if self._client is None or self._client._connection.url != target_url:
                if self._client is not None:
                    self._client = None  # Close old client
                
                logger.info(f"Connecting to Weaviate at {target_url}")
                self._client = weaviate.Client(
                    url=target_url,
                    timeout_config=(self.timeout, self.timeout),
                )
                
                # Test connection
                if not self._client.is_ready():
                    raise WeaviateClientError(f"Weaviate server at {target_url} is not ready")
            
            return self._client
        
        except WeaviateBaseError as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise WeaviateClientError(f"Failed to connect to Weaviate: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error connecting to Weaviate: {e}")
            raise WeaviateClientError(f"Unexpected error: {e}")
    
    def close(self):
        """Close the Weaviate client"""
        if self._client is not None:
            self._client = None
            logger.info("Weaviate client closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    async def search_similar(
        self,
        class_name: str,
        vector: List[float],
        limit: int = 10,
        threshold: float = 0.7,
        properties: Optional[List[str]] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Weaviate.
        
        Args:
            class_name: Weaviate class name to search in
            vector: Query vector
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1)
            properties: List of properties to return (None = all)
            where_filter: Optional filter conditions
            url: Weaviate server URL (uses default if not provided)
            
        Returns:
            List of search results with properties and similarity scores
            
        Raises:
            WeaviateClientError: If search fails
            ValueError: If required parameters are invalid
        """
        if not class_name:
            raise ValueError("Class name is required")
        
        if not vector:
            raise ValueError("Query vector is required")
        
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        try:
            client = self._get_client(url)
            
            logger.info(
                f"Searching {class_name} with vector of dimension {len(vector)}, "
                f"limit={limit}, threshold={threshold}"
            )
            
            # Build query
            query = (
                client.query
                .get(class_name, properties or [])
                .with_near_vector({"vector": vector, "certainty": threshold})
                .with_limit(limit)
                .with_additional(["certainty", "id"])
            )
            
            # Add filter if provided
            if where_filter:
                query = query.with_where(where_filter)
            
            # Execute query
            result = query.do()
            
            # Extract results
            if "data" not in result or "Get" not in result["data"]:
                logger.warning(f"No data in search result: {result}")
                return []
            
            class_results = result["data"]["Get"].get(class_name, [])
            
            logger.info(f"Found {len(class_results)} results")
            return class_results
        
        except WeaviateBaseError as e:
            logger.error(f"Weaviate search error: {e}")
            raise WeaviateClientError(f"Search failed: {e}")
        
        except Exception as e:
            if isinstance(e, (WeaviateClientError, ValueError)):
                raise
            logger.error(f"Unexpected error during search: {e}")
            raise WeaviateClientError(f"Unexpected error: {e}")
    
    async def search_similar_hybrid(
        self,
        class_name: str,
        query_text: str,
        vector: List[float],
        alpha: float = 0.5,
        limit: int = 10,
        properties: Optional[List[str]] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and keyword search.
        
        Args:
            class_name: Weaviate class name to search in
            query_text: Query text for keyword search
            vector: Query vector for similarity search
            alpha: Balance between vector (1.0) and keyword (0.0) search
            limit: Maximum number of results to return
            properties: List of properties to return (None = all)
            where_filter: Optional filter conditions
            url: Weaviate server URL (uses default if not provided)
            
        Returns:
            List of search results with properties and scores
            
        Raises:
            WeaviateClientError: If search fails
            ValueError: If required parameters are invalid
        """
        if not class_name:
            raise ValueError("Class name is required")
        
        if not query_text:
            raise ValueError("Query text is required")
        
        if not vector:
            raise ValueError("Query vector is required")
        
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")
        
        try:
            client = self._get_client(url)
            
            logger.info(
                f"Hybrid search in {class_name} with alpha={alpha}, limit={limit}"
            )
            
            # Build hybrid query
            query = (
                client.query
                .get(class_name, properties or [])
                .with_hybrid(
                    query=query_text,
                    vector=vector,
                    alpha=alpha,
                )
                .with_limit(limit)
                .with_additional(["score", "id"])
            )
            
            # Add filter if provided
            if where_filter:
                query = query.with_where(where_filter)
            
            # Execute query
            result = query.do()
            
            # Extract results
            if "data" not in result or "Get" not in result["data"]:
                logger.warning(f"No data in search result: {result}")
                return []
            
            class_results = result["data"]["Get"].get(class_name, [])
            
            logger.info(f"Found {len(class_results)} results")
            return class_results
        
        except WeaviateBaseError as e:
            logger.error(f"Weaviate hybrid search error: {e}")
            raise WeaviateClientError(f"Hybrid search failed: {e}")
        
        except Exception as e:
            if isinstance(e, (WeaviateClientError, ValueError)):
                raise
            logger.error(f"Unexpected error during hybrid search: {e}")
            raise WeaviateClientError(f"Unexpected error: {e}")
    
    def is_ready(self, url: Optional[str] = None) -> bool:
        """
        Check if Weaviate server is ready.
        
        Args:
            url: Weaviate server URL (uses default if not provided)
            
        Returns:
            True if server is ready, False otherwise
        """
        try:
            client = self._get_client(url)
            return client.is_ready()
        except Exception as e:
            logger.error(f"Failed to check Weaviate readiness: {e}")
            return False
