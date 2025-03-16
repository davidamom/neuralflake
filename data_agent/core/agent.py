"""
Core agent implementation.

This module contains the main NeuralFlake agent class that orchestrates
interactions between different components.
"""

import json
import time
from typing import Any, Dict, List, Optional, Union

from ..llm.provider import LLMProviderFactory, get_default_provider
from ..rag.retriever import DocumentRetriever
from ..utils.logging import logger, setup_logging
from ..utils.helpers import generate_hash, save_json, load_json
from .config import config


class DataAgent:
    """
    Core NeuralFlake implementation.
    
    This class orchestrates interactions between the LLM, RAG system,
    and various data connectors.
    """
    
    def __init__(
        self,
        llm_provider: Optional[Any] = None,
        document_retriever: Optional[DocumentRetriever] = None,
    ):
        """
        Initialize the Data Agent.
        
        Args:
            llm_provider: LLM provider instance
            document_retriever: Document retriever instance
        """
        self.logger = setup_logging(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("Initializing Data Agent")
        
        # Initialize LLM provider
        self.llm = llm_provider or get_default_provider()
        
        # Initialize document retriever
        self.retriever = document_retriever or DocumentRetriever()
        
        # Initialize conversation history
        self.conversation_history = []
        
        self.logger.info("Data Agent initialized successfully")
    
    def query(self, query: str, use_rag: bool = True) -> str:
        """
        Process a user query and generate a response.
        
        Args:
            query: User query
            use_rag: Whether to use RAG for context augmentation
            
        Returns:
            str: Response to the query
        """
        self.logger.info(f"Processing query: {query}")
        start_time = time.time()
        
        # Add user query to conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Retrieve relevant context if RAG is enabled
        context = ""
        if use_rag and self.retriever:
            self.logger.info("Retrieving relevant documents")
            documents = self.retriever.retrieve(query)
            if documents:
                context = "\n\n".join([doc["text"] for doc in documents])
                self.logger.info(f"Retrieved {len(documents)} relevant documents")
        
        # Generate a prompt with the context
        if context:
            prompt = self._generate_prompt_with_context(query, context)
        else:
            prompt = query
        
        # Generate response using the LLM
        response = self.llm.generate(prompt)
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"Query processed in {elapsed_time:.2f} seconds")
        
        return response
    
    def _generate_prompt_with_context(self, query: str, context: str) -> str:
        """
        Generate a prompt with the retrieved context.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            str: Prompt with context
        """
        return f"""You are NeuralFlake, a Data Engineering assistant that helps with analysis and suggestions.
Please use the following context to answer the query.

CONTEXT:
{context}

QUERY:
{query}

Provide a helpful, accurate, and concise response based on the context provided."""
    
    def chat(self, message: str, use_rag: bool = True) -> str:
        """
        Continue a conversation with the agent.
        
        Args:
            message: User message
            use_rag: Whether to use RAG for context augmentation
            
        Returns:
            str: Response to the message
        """
        self.logger.info(f"Received chat message: {message}")
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Retrieve relevant context if RAG is enabled
        context = ""
        if use_rag and self.retriever:
            documents = self.retriever.retrieve(message)
            if documents:
                context = "\n\n".join([doc["text"] for doc in documents])
        
        # Convert conversation history to format expected by the LLM
        messages = self._prepare_chat_messages(message, context)
        
        # Generate response using the LLM with conversation history
        response = self.llm.generate_with_history(messages)
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _prepare_chat_messages(self, message: str, context: str) -> List[Dict[str, str]]:
        """
        Prepare messages for the chat model.
        
        Args:
            message: Current user message
            context: Retrieved context
            
        Returns:
            List[Dict[str, str]]: Formatted messages
        """
        # Start with a system message
        messages = [
            {
                "role": "system",
                "content": f"""You are NeuralFlake, a Data Engineering assistant that helps with analysis and suggestions.
You provide helpful, accurate, and concise responses.
"""
            }
        ]
        
        # Add context if available
        if context:
            messages[0]["content"] += f"\nPlease use the following context for your responses:\n{context}"
        
        # Add conversation history (excluding the current message)
        history = self.conversation_history[:-1] if self.conversation_history else []
        messages.extend(history)
        
        # Add the current message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def save_conversation(self, file_path: str) -> bool:
        """
        Save the conversation history to a file.
        
        Args:
            file_path: Path to save the conversation
            
        Returns:
            bool: Success status
        """
        conversation_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "conversation_id": generate_hash(str(time.time())),
            "messages": self.conversation_history
        }
        
        return save_json(conversation_data, file_path)
    
    def load_conversation(self, file_path: str) -> bool:
        """
        Load a conversation history from a file.
        
        Args:
            file_path: Path to the conversation file
            
        Returns:
            bool: Success status
        """
        conversation_data = load_json(file_path)
        if conversation_data and "messages" in conversation_data:
            self.conversation_history = conversation_data["messages"]
            return True
        return False
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
