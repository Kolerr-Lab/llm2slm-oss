import abc
import logging
from typing import Any, Dict

"""
Base provider module for LLM2SLM project.

This module defines the base class for all LLM providers, ensuring consistent
interfaces and production-ready error handling, logging, and async operations.
"""


logger = logging.getLogger(__name__)


class BaseProvider(abc.ABC):
    """
    Abstract base class for LLM providers.

    This class provides a common interface for interacting with different
    Large Language Model providers, such as OpenAI. Subclasses must implement
    the abstract methods to handle provider-specific logic.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary for the provider.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the provider with configuration.

        Args:
            config (Dict[str, Any]): Provider-specific configuration options,
                such as API keys, endpoints, and timeouts.

        Raises:
            ValueError: If required configuration keys are missing.
        """
        self.config = config
        self._validate_config()
        logger.info(f"Initialized {self.__class__.__name__} provider.")

    def _validate_config(self) -> None:
        """
        Validate the provider configuration.

        This method should be overridden by subclasses to perform
        provider-specific validation.

        Raises:
            ValueError: If configuration is invalid.
        """
        pass  # Default implementation does nothing; subclasses can override.

    @abc.abstractmethod
    async def generate_response(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a response from the LLM provider.

        Args:
            prompt (str): The input prompt for the model.
            **kwargs: Additional provider-specific parameters.

        Returns:
            str: The generated response.

        Raises:
            RuntimeError: If the provider fails to generate a response.
        """
        pass

    @abc.abstractmethod
    async def convert_to_slm(self, model_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Convert an LLM to an SLM using the provider.

        Args:
            model_id (str): Identifier of the model to convert.
            **kwargs: Additional conversion parameters.

        Returns:
            Dict[str, Any]: Metadata or results of the conversion process.

        Raises:
            RuntimeError: If the conversion fails.
        """
        pass

    async def close(self) -> None:
        """
        Clean up resources used by the provider.

        This method should be called to release any connections or resources.
        Subclasses can override to implement specific cleanup logic.
        """
        logger.info(f"Closing {self.__class__.__name__} provider.")
        # Default implementation does nothing; subclasses can override.
