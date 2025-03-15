"""
Base vector store interface.

This module defines the base interface for vector stores used in the RAG component.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ...utils.logging import logger


class BaseVectorStore(ABC):
    """Base interface for vector stores."""
    
    @abstractmethod
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of IDs for the texts
            embeddings: Optional pre-computed embeddings
            
        Returns:
            List[str]: List of IDs for the added texts
        """
        pass
    
    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Query string or embedding
            k: Number of results to return
            filter: Optional filter to apply
            
        Returns:
            List[Dict[str, Any]]: List of results with text and metadata
        """
        pass
    
    @abstractmethod
    def delete(self, ids: Optional[List[str]] = None, filter: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete documents from the vector store.
        
        Args:
            ids: Optional list of IDs to delete
            filter: Optional filter to apply
            
        Returns:
            bool: Success status
        """
        pass
    
    @abstractmethod
    def persist(self) -> bool:
        """
        Persist the vector store to disk.
        
        Returns:
            bool: Success status
        """
        pass
    
    @property
    @abstractmethod
    def count(self) -> int:
        """
        Get the number of documents in the vector store.
        
        Returns:
            int: Document count
        """
        pass
