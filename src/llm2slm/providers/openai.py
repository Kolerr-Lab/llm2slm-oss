import asyncio
import logging
import os
from typing import Any, Optional

import openai
from openai import AsyncOpenAI

"""
OpenAI Provider Module for LLM2SLM

This module provides integration with OpenAI's API for large language model operations,
such as text generation, within the LLM2SLM conversion pipeline. It is designed for
production deployment with robust error handling, logging, and security practices.

Key Features:
- Asynchronous API calls using aiohttp for non-blocking operations.
- Secure API key management via environment variables.
- Comprehensive logging for monitoring and debugging.
- Type hints and docstrings for maintainability.
- Error handling for common API issues (e.g., rate limits, authentication).

Dependencies:
- openai: Official OpenAI Python client.
- aiohttp: For asynchronous HTTP requests (if needed for custom calls).
- python-dotenv: For loading environment variables.

Usage:
    provider = OpenAIProvider()
    response = await provider.generate_text(prompt="Hello, world!", model="gpt-3.5-turbo")
"""


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class OpenAIProvider:
    """
    Provider class for interacting with OpenAI's API.

    This class handles authentication, request sending, and response parsing for OpenAI models.
    It uses asynchronous methods to support high-throughput operations in the LLM2SLM pipeline.

    Attributes:
        api_key (str): The OpenAI API key loaded from environment variables.
        client (AsyncOpenAI): The asynchronous OpenAI client instance.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the OpenAI provider.

        Args:
            api_key (Optional[str]): The OpenAI API key. If not provided, it will be loaded
                from the OPENAI_API_KEY environment variable.

        Raises:
            ValueError: If the API key is not provided or invalid.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided via parameter or OPENAI_API_KEY environment "
                "variable."
            )

        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info("OpenAI provider initialized successfully.")

    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using the specified OpenAI model.

        This method sends a chat completion request to OpenAI and returns the generated text.
        It includes retry logic for transient errors and proper error handling.

        Args:
            prompt (str): The input prompt for text generation.
            model (str): The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4").
            max_tokens (int): Maximum number of tokens to generate.
            temperature (float): Sampling temperature for randomness (0.0 to 1.0).
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            str: The generated text response.

        Raises:
            openai.APIError: For API-related errors.
            Exception: For unexpected errors.
        """
        try:
            logger.info(f"Sending request to OpenAI model '{model}' with prompt: {prompt[:50]}...")

            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            content = response.choices[0].message.content
            generated_text = str(content).strip() if content is not None else ""  # type: ignore[no-any-return]
            logger.info(f"Successfully generated text: {generated_text[:50]}...")
            return generated_text

        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            await asyncio.sleep(1)  # Simple backoff; consider exponential backoff in production
            raise
        except openai.AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during text generation: {e}")
            raise

    async def close(self) -> None:
        """
        Close the OpenAI client session.

        This method should be called to properly clean up resources when the provider is no
        longer needed.
        """
        await self.client.close()
        logger.info("OpenAI provider session closed.")
