"""
Document retriever for the RAG component.

This module provides the ability to retrieve relevant documents for a query.
"""

from typing import Any, Dict, List, Optional, Union

from ..core.config import config
from ..llm.provider import get_default_provider
from ..utils.logging import logger
from .vector_store.chroma import ChromaVectorStore


class DocumentRetriever:
    """Document retriever for the RAG component."""
    
    def __init__(
        self,
        vector_store: Optional[Any] = None,
        top_k: int = 4,
    ):
        """
        Initialize the document retriever.
        
        Args:
            vector_store: Vector store instance
            top_k: Number of documents to retrieve
        """
        self.logger = logger
        self.top_k = top_k
        
        # Initialize vector store
        self.vector_store = vector_store
        if self.vector_store is None:
            self.logger.info("No vector store provided, creating default Chroma vector store")
            try:
                self.vector_store = ChromaVectorStore()
            except Exception as e:
                self.logger.error(f"Error initializing default vector store: {str(e)}")
                self.vector_store = None
        
        # Initialize LLM provider for potential reranking
        self.llm = get_default_provider()
        
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve
            filter: Optional filter to apply
            
        Returns:
            List[Dict[str, Any]]: List of retrieved documents
        """
        if not self.vector_store:
            self.logger.warning("No vector store available for retrieval")
            return []
        
        top_k = top_k or self.top_k
        
        try:
            self.logger.info(f"Retrieving documents for query: {query}")
            
            # Retrieve documents from vector store
            results = self.vector_store.similarity_search(
                query=query,
                k=top_k,
                filter=filter,
            )
            
            self.logger.info(f"Retrieved {len(results)} documents")
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of IDs for the texts
            
        Returns:
            List[str]: List of IDs for the added documents
        """
        if not self.vector_store:
            self.logger.warning("No vector store available to add documents")
            return []
        
        try:
            self.logger.info(f"Adding {len(texts)} documents to vector store")
            
            # Add documents to vector store
            doc_ids = self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids,
            )
            
            # Persist vector store
            self.vector_store.persist()
            
            self.logger.info(f"Added {len(doc_ids)} documents to vector store")
            return doc_ids
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            return []
    
    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Delete documents from the vector store.
        
        Args:
            ids: Optional list of IDs to delete
            filter: Optional filter to apply
            
        Returns:
            bool: Success status
        """
        if not self.vector_store:
            self.logger.warning("No vector store available to delete documents")
            return False
        
        try:
            success = self.vector_store.delete(ids=ids, filter=filter)
            
            if success:
                # Persist vector store
                self.vector_store.persist()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting documents: {str(e)}")
            return False
