"""
OpenAI LLM provider implementation.

This module provides integration with OpenAI's language models.
"""

import time
from typing import Any, Dict, List, Optional, Union

import openai
from openai import OpenAI

from ..core.config import config
from ..utils.logging import logger


class OpenAIProvider:
    """Provider for OpenAI language models."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model_name: Model name to use (defaults to config)
        """
        self.api_key = api_key or config.llm.api_key
        self.model_name = model_name or config.llm.model_name
        
        if not self.api_key:
            logger.warning("OpenAI API key not provided. Using environment variable if available.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop_sequences: Sequences to stop generation at
            
        Returns:
            str: Generated text
        """
        max_tokens = max_tokens or config.llm.max_tokens
        temperature = temperature or config.llm.temperature
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop_sequences,
                )
                
                if not response.choices:
                    logger.warning("OpenAI API returned no choices")
                    return ""
                
                return response.choices[0].message.content or ""
                
            except Exception as e:
                logger.error(f"Error in OpenAI API call (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries exceeded. Returning empty response.")
                    return ""
    
    def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """
        Generate text with conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop_sequences: Sequences to stop generation at
            
        Returns:
            str: Generated text
        """
        max_tokens = max_tokens or config.llm.max_tokens
        temperature = temperature or config.llm.temperature
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop_sequences,
                )
                
                if not response.choices:
                    logger.warning("OpenAI API returned no choices")
                    return ""
                
                return response.choices[0].message.content or ""
                
            except Exception as e:
                logger.error(f"Error in OpenAI API call (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries exceeded. Returning empty response.")
                    return ""
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for text.
        
        Args:
            text: Text to get embeddings for
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",  # Using the recommended embedding model
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Return empty embedding in case of error
            return []
