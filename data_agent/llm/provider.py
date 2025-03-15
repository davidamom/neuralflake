"""
LLM provider factory.

This module provides a factory for creating LLM provider instances.
"""

from typing import Any, Dict, List, Optional, Union

from ..core.config import config
from ..utils.logging import logger
from .openai import OpenAIProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    @staticmethod
    def create(
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Any:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Provider name (openai, anthropic, etc.)
            api_key: API key for the provider
            model_name: Model name to use
            
        Returns:
            Any: LLM provider instance
        """
        provider_name = provider_name or config.llm.provider
        
        if provider_name.lower() == "openai":
            return OpenAIProvider(api_key=api_key, model_name=model_name)
        # Add support for more providers here
        # elif provider_name.lower() == "anthropic":
        #     return AnthropicProvider(api_key=api_key, model_name=model_name)
        else:
            logger.warning(f"Unsupported LLM provider: {provider_name}. Falling back to OpenAI.")
            return OpenAIProvider(api_key=api_key, model_name=model_name)


def get_default_provider() -> Any:
    """
    Get the default LLM provider instance.
    
    Returns:
        Any: Default LLM provider instance
    """
    return LLMProviderFactory.create()
