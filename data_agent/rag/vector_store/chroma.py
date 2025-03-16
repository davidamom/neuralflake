"""
Chroma vector store implementation.

This module provides integration with the Chroma vector database.
"""

import uuid
from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ...core.config import config
from ...llm.provider import get_default_provider
from ...utils.logging import logger
from ...utils.helpers import ensure_directory
from .base import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    """Chroma vector store implementation."""
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Any] = None,
    ):
        """
        Initialize the Chroma vector store.
        
        Args:
            collection_name: Collection name
            persist_directory: Directory to persist the database
            embedding_function: Function to generate embeddings
        """
        self.collection_name = collection_name or config.vector_store.collection_name
        self.persist_directory = persist_directory or config.vector_store.persist_directory
        
        # Ensure the persist directory exists
        if self.persist_directory:
            ensure_directory(self.persist_directory)
        
        # Initialize the client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Create or get the collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function or self._get_default_embedding_function(),
            )
            logger.info(f"Connected to Chroma collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error connecting to Chroma: {str(e)}")
            raise
    
    def _get_default_embedding_function(self) -> Any:
        """
        Get the default embedding function.
        
        Returns:
            Any: Default embedding function
        """
        try:
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=config.llm.api_key,
                model_name="text-embedding-ada-002"
            )
        except Exception as e:
            logger.warning(f"Could not create OpenAI embedding function: {str(e)}")
            logger.warning("Falling back to default embedding function")
            return None  # Chroma will use its default embedding function
    
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
        if not texts:
            logger.warning("No texts provided to add_texts")
            return []
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Ensure metadatas is provided for each text
        if metadatas is None:
            metadatas = [{} for _ in range(len(texts))]
        
        try:
            # Add documents to the collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info(f"Added {len(texts)} documents to Chroma collection")
            return ids
        except Exception as e:
            logger.error(f"Error adding texts to Chroma: {str(e)}")
            return []
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Query string
            k: Number of results to return
            filter: Optional filter to apply
            
        Returns:
            List[Dict[str, Any]]: List of results with text and metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filter
            )
            
            # Format results to match the expected interface
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                    formatted_results.append({
                        "text": doc,
                        "metadata": metadata,
                        "id": results["ids"][0][i] if results["ids"] and results["ids"][0] else None,
                        "score": results["distances"][0][i] if results["distances"] and results["distances"][0] else None,
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def delete(self, ids: Optional[List[str]] = None, filter: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete documents from the vector store.
        
        Args:
            ids: Optional list of IDs to delete
            filter: Optional filter to apply
            
        Returns:
            bool: Success status
        """
        try:
            if ids:
                self.collection.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} documents from Chroma collection")
            elif filter:
                # Get IDs matching the filter
                results = self.collection.get(where=filter)
                if results and results["ids"]:
                    self.collection.delete(ids=results["ids"])
                    logger.info(f"Deleted {len(results['ids'])} documents from Chroma collection using filter")
            return True
        except Exception as e:
            logger.error(f"Error deleting from Chroma: {str(e)}")
            return False
    
    def persist(self) -> bool:
        """
        Persist the vector store to disk.
        
        Returns:
            bool: Success status
        """
        try:
            # For newer versions of Chroma, data is automatically persisted
            # when using a PersistentClient, so no explicit persist is needed
            logger.info("Chroma collection data is automatically persisted to disk")
            return True
        except Exception as e:
            logger.error(f"Error persisting Chroma collection: {str(e)}")
            return False
    
    @property
    def count(self) -> int:
        """
        Get the number of documents in the vector store.
        
        Returns:
            int: Document count
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting Chroma collection count: {str(e)}")
            return 0
