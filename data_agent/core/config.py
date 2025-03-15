"""
Configuration module for the Data Agent.

This module handles loading configuration from environment variables and
provides access to configuration throughout the application.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file if it exists
load_dotenv()


class LLMConfig(BaseModel):
    """Configuration for the Language Model."""

    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, etc.)")
    model_name: str = Field(default="gpt-4", description="Model name to use")
    api_key: Optional[str] = Field(default=None, description="API key for the LLM provider")
    max_tokens: int = Field(default=4096, description="Maximum number of tokens to generate")
    temperature: float = Field(default=0.7, description="Temperature for generation")


class VectorStoreConfig(BaseModel):
    """Configuration for the Vector Store."""

    provider: str = Field(default="chroma", description="Vector store provider")
    persist_directory: str = Field(
        default="./data/chroma", description="Directory to persist vector store"
    )
    collection_name: str = Field(
        default="data_agent", description="Collection name in the vector store"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = Field(default="INFO", description="Logging level")
    file: Optional[str] = Field(default=None, description="Log file path")


class AgentConfig(BaseModel):
    """Main configuration for the Data Agent."""

    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    vector_store: VectorStoreConfig = Field(
        default_factory=VectorStoreConfig, description="Vector store configuration"
    )
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    data_dir: str = Field(default="./data", description="Data directory")


def load_config() -> AgentConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        AgentConfig: Agent configuration
    """
    # Load LLM config
    llm_config = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model_name=os.getenv("LLM_MODEL_NAME", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
    )

    # Load Vector Store config
    vector_store_config = VectorStoreConfig(
        provider=os.getenv("VECTOR_STORE_PROVIDER", "chroma"),
        persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma"),
        collection_name=os.getenv("VECTOR_STORE_COLLECTION", "data_agent"),
    )

    # Load Logging config
    logging_config = LoggingConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        file=os.getenv("LOG_FILE"),
    )

    # Create directories if they don't exist
    data_dir = os.getenv("DATA_DIR", "./data")
    Path(data_dir).mkdir(exist_ok=True, parents=True)
    
    if vector_store_config.persist_directory:
        Path(vector_store_config.persist_directory).mkdir(exist_ok=True, parents=True)
    
    if logging_config.file:
        log_path = Path(logging_config.file)
        log_path.parent.mkdir(exist_ok=True, parents=True)

    return AgentConfig(
        llm=llm_config,
        vector_store=vector_store_config,
        logging=logging_config,
        data_dir=data_dir,
    )


# Create a global config instance
config = load_config()
