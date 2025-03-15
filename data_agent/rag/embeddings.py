"""
Embeddings module for the RAG component.

This module provides functions for generating embeddings from text.
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np

from ..core.config import config
from ..llm.provider import get_default_provider
from ..utils.logging import logger


class EmbeddingProvider:
    """Provider for generating embeddings from text."""
    
    def __init__(self, llm_provider: Optional[Any] = None):
        """
        Initialize the embedding provider.
        
        Args:
            llm_provider: LLM provider instance
        """
        self.logger = logger
        self.llm_provider = llm_provider or get_default_provider()
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        
        try:
            for text in texts:
                embedding = self.llm_provider.get_embedding(text)
                embeddings.append(embedding)
            
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            # Return empty embeddings as fallback
            return [[] for _ in range(len(texts))]
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            return self.llm_provider.get_embedding(text)
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
            return []


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        float: Cosine similarity (-1 to 1)
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    try:
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # Avoid division by zero
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return dot_product / (norm_v1 * norm_v2)
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {str(e)}")
        return 0.0


def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate Euclidean distance between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        float: Euclidean distance
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return float('inf')
    
    try:
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Calculate Euclidean distance
        return np.linalg.norm(v1 - v2)
    except Exception as e:
        logger.error(f"Error calculating Euclidean distance: {str(e)}")
        return float('inf')
