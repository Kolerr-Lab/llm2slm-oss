import asyncioimport asyncioimport asyncio

import logging

import osimport loggingimport logging

from typing import Any, Dict, List, Optional

import osimport os

import google.generativeai as genai

from typing import Any, Dict, List, Optionalfrom         """

"""

Google Provider Module for LLM2SLM        Initialize the Google provider.



This module provides integration with Google's Generative AI API for large languageimport google.generativeai as genai

model operations, such as text generation, within the LLM2SLM conversion pipeline.

It is designed for production deployment with robust error handling, logging, and        Args:

security practices.

"""            api_key (Optional[str]): API key for Google Generative AI. If None, uses

Key Features:

- Asynchronous API calls for non-blocking operations.Google Provider Module for LLM2SLM                GOOGLE_API_KEY env var.

- Secure API key management via environment variables.

- Comprehensive logging for monitoring and debugging.            model_name (str): Name of the model to use. Defaults to 'gemini-1.5-flash'.

- Type hints and docstrings for maintainability.

- Error handling for common API issues (e.g., rate limits, authentication).This module provides integration with Google's Generative AI API for large language



Dependencies:model operations, such as text generation, within the LLM2SLM conversion pipeline.        Raises:

- google-generativeai: Official Google Generative AI Python client.

It is designed for production deployment with robust error handling, logging, and            ValueError: If no API key is provided or found.

Usage:

    provider = GoogleProvider()security practices.        """ort Any, Dict, List, Optional

    response = await provider.generate(prompt="Hello, world!", model="gemini-1.5-flash")

"""



Key Features:import google.generativeai as genai

# Configure logging

logger = logging.getLogger(__name__)- Asynchronous API calls for non-blocking operations.



- Secure API key management via environment variables."""

class GoogleProvider:

    """- Comprehensive logging for monitoring and debugging.Google Provider Module for LLM2SLM

    Provider class for interacting with Google's Generative AI API.

- Type hints and docstrings for maintainability.

    This class handles authentication, request sending, and response parsing for Google models.

    It uses asynchronous methods to support high-throughput operations in the LLM2SLM pipeline.- Error handling for common API issues (e.g., rate limits, authentication).This module provides integration with Google's Generative AI API for large language



    Attributes:model operations, such as text generation, within the LLM2SLM conversion pipeline.

        api_key (str): The Google API key loaded from environment variables.

        client (genai.GenerativeModel): The initialized Google Generative AI client.Dependencies:It is designed for production deployment with robust error handling, logging, and

    """

- google-generativeai: Official Google Generative AI Python client.security practices.

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> None:

        """

        Initialize the Google provider.

Usage:Key Features:

        Args:

            api_key (Optional[str]): API key for Google Generative AI. If None, uses    provider = GoogleProvider()- Asynchronous API calls for non-blocking operations.

                GOOGLE_API_KEY env var.

            model_name (str): Name of the model to use. Defaults to 'gemini-1.5-flash'.    response = await provider.generate(prompt="Hello, world!", model="gemini-1.5-flash")- Secure API key management via environment variables.



        Raises:"""- Comprehensive logging for monitoring and debugging.

            ValueError: If no API key is provided or found.

        """- Type hints and docstrings for maintainability.

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:- Error handling for common API issues (e.g., rate limits, authentication).

            raise ValueError(

                "Google API key must be provided via parameter or GOOGLE_API_KEY environment variable."# Configure logging

            )

logger = logging.getLogger(__name__)Dependencies:

        self.model_name = model_name

        genai.configure(api_key=self.api_key)- google-generativeai: Official Google Generative AI Python client.

        self.client = genai.GenerativeModel(model_name)

        logger.info(f"Initialized GoogleProvider with model: {model_name}")



    async def generate(self, prompt: str, **kwargs: Any) -> str:class GoogleProvider:Usage:

        """

        Generate text using Google's Generative AI.    """    provider = GoogleProvider()



        Args:    Provider class for interacting with Google's Generative AI API.    response = await provider.generate(prompt="Hello, world!", model="gemini-1.5-flash")

            prompt (str): The input prompt for text generation.

            **kwargs: Additional parameters for the API call."""



        Returns:    This class handles authentication, request sending, and response parsing for Google models.

            str: The generated text response.

    It uses asynchronous methods to support high-throughput operations in the LLM2SLM pipeline.

        Raises:

            RuntimeError: If the API call fails.# Configure logging

        """

        try:    Attributes:logger = logging.getLogger(__name__)

            # Merge kwargs with defaults

            generation_config = {        api_key (str): The Google API key loaded from environment variables.

                "temperature": kwargs.get("temperature", 0.7),

                "top_p": kwargs.get("top_p", 0.8),        client (genai.GenerativeModel): The initialized Google Generative AI client.

                "top_k": kwargs.get("top_k", 10),

                "max_output_tokens": kwargs.get("max_tokens", 2048),    """class GoogleProvider:

            }

    """

            response = await self.client.generate_content_async(

                prompt,    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> None:    Provider class for interacting with Google's Generative AI API.

                generation_config=genai.types.GenerationConfig(**generation_config)

            )        """



            return response.text        Initialize the Google provider.    This class handles authentication, request sending, and response parsing for Google models.



        except Exception as e:    It uses asynchronous methods to support high-throughput operations in the LLM2SLM pipeline.

            logger.error(f"Error generating text with Google API: {e}")

            raise RuntimeError(f"Failed to generate text: {e}") from e        Args:



    async def embed(self, texts: List[str], **kwargs: Any) -> List[List[float]]:            api_key (Optional[str]): API key for Google Generative AI. If None, uses    Attributes:

        """

        Generate embeddings for the given texts using Google's embedding model.                GOOGLE_API_KEY env var.        api_key (str): The Google API key loaded from environment variables.



        Args:            model_name (str): Name of the model to use. Defaults to 'gemini-1.5-flash'.        client (genai.GenerativeModel): The initialized Google Generative AI client.

            texts (List[str]): List of texts to embed.

            **kwargs: Additional parameters for the API call.    """



        Returns:        Raises:

            List[List[float]]: List of embedding vectors.

            ValueError: If no API key is provided or found.    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> None:

        Raises:

            RuntimeError: If the API call fails.        """        """

        """

        try:        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")        Initialize the Google provider.

            # Use a text embedding model

            embedding_model = "models/embedding-001"        if not self.api_key:



            result = genai.embed_content(            raise ValueError(        Args:

                model=embedding_model,

                content=texts,                "Google API key must be provided via parameter or GOOGLE_API_KEY environment variable."            api_key (Optional[str]): API key for Google Generative AI. If None, uses GOOGLE_API_KEY env var.

                task_type="retrieval_document"

            )            )            model_name (str): Name of the model to use. Defaults to 'gemini-1.5-flash'.



            # Handle single text vs multiple texts

            if isinstance(result['embedding'], list) and len(result['embedding']) > 1:

                return result['embedding']        self.model_name = model_name        Raises:

            else:

                return [result['embedding']]        genai.configure(api_key=self.api_key)            ValueError: If no API key is provided or found.



        except Exception as e:        self.client = genai.GenerativeModel(model_name)        """

            logger.error(f"Error generating embeddings with Google API: {e}")

            raise RuntimeError(f"Failed to generate embeddings: {e}") from e        logger.info(f"Initialized GoogleProvider with model: {model_name}")        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")



    async def close(self) -> None:        if not self.api_key:

        """

        Clean up resources used by the provider.    async def generate(self, prompt: str, **kwargs: Any) -> str:            raise ValueError(



        This method should be called to release any connections or resources.        """                "Google API key must be provided via parameter or GOOGLE_API_KEY environment variable."

        """

        logger.info("Closing GoogleProvider.")        Generate text using Google's Generative AI.            )

        # Google Generative AI client doesn't require explicit cleanup


        Args:        self.model_name = model_name

            prompt (str): The input prompt for text generation.        genai.configure(api_key=self.api_key)

            **kwargs: Additional parameters for the API call.        self.client = genai.GenerativeModel(model_name)

        logger.info(f"Initialized GoogleProvider with model: {model_name}")

        Returns:

            str: The generated text response.    async def generate(self, prompt: str, **kwargs: Any) -> str:

        """

        Raises:        Generate text using Google's Generative AI.

            RuntimeError: If the API call fails.

        """        Args:

        try:            prompt (str): The input prompt for text generation.

            # Merge kwargs with defaults            **kwargs: Additional parameters for the API call.

            generation_config = {

                "temperature": kwargs.get("temperature", 0.7),        Returns:

                "top_p": kwargs.get("top_p", 0.8),            str: The generated text response.

                "top_k": kwargs.get("top_k", 10),

                "max_output_tokens": kwargs.get("max_tokens", 2048),        Raises:

            }            RuntimeError: If the API call fails.

        """

            response = await self.client.generate_content_async(        try:

                prompt,            # Merge kwargs with defaults

                generation_config=genai.types.GenerationConfig(**generation_config)            generation_config = {

            )                "temperature": kwargs.get("temperature", 0.7),

                "top_p": kwargs.get("top_p", 0.8),

            return response.text                "top_k": kwargs.get("top_k", 10),

                "max_output_tokens": kwargs.get("max_tokens", 2048),

        except Exception as e:            }

            logger.error(f"Error generating text with Google API: {e}")

            raise RuntimeError(f"Failed to generate text: {e}") from e            response = await self.client.generate_content_async(

                prompt, generation_config=genai.types.GenerationConfig(**generation_config)

    async def embed(self, texts: List[str], **kwargs: Any) -> List[List[float]]:            )

        """

        Generate embeddings for the given texts using Google's embedding model.            return response.text



        Args:        except Exception as e:

            texts (List[str]): List of texts to embed.            logger.error(f"Error generating text with Google API: {e}")

            **kwargs: Additional parameters for the API call.            raise RuntimeError(f"Failed to generate text: {e}") from e



        Returns:    async def embed(self, texts: List[str], **kwargs: Any) -> List[List[float]]:

            List[List[float]]: List of embedding vectors.        """

        Generate embeddings for the given texts using Google's embedding model.

        Raises:

            RuntimeError: If the API call fails.        Args:

        """            texts (List[str]): List of texts to embed.

        try:            **kwargs: Additional parameters for the API call.

            # Use a text embedding model

            embedding_model = "models/embedding-001"        Returns:

            List[List[float]]: List of embedding vectors.

            result = genai.embed_content(

                model=embedding_model,        Raises:

                content=texts,            RuntimeError: If the API call fails.

                task_type="retrieval_document"        """

            )        try:

            # Use a text embedding model

            # Handle single text vs multiple texts            embedding_model = "models/embedding-001"

            if isinstance(result['embedding'], list) and len(result['embedding']) > 1:

                return result['embedding']            result = genai.embed_content(

            else:                model=embedding_model, content=texts, task_type="retrieval_document"

                return [result['embedding']]            )



        except Exception as e:            # Handle single text vs multiple texts

            logger.error(f"Error generating embeddings with Google API: {e}")            if isinstance(result["embedding"], list) and len(result["embedding"]) > 1:

            raise RuntimeError(f"Failed to generate embeddings: {e}") from e                return result["embedding"]

            else:

    async def close(self) -> None:                return [result["embedding"]]

        """

        Clean up resources used by the provider.        except Exception as e:

            logger.error(f"Error generating embeddings with Google API: {e}")

        This method should be called to release any connections or resources.            raise RuntimeError(f"Failed to generate embeddings: {e}") from e

        """

        logger.info("Closing GoogleProvider.")    async def close(self) -> None:

        # Google Generative AI client doesn't require explicit cleanup        """
        Clean up resources used by the provider.

        This method should be called to release any connections or resources.
        """
        logger.info("Closing GoogleProvider.")
        # Google Generative AI client doesn't require explicit cleanup
        genai.configure(api_key=self.api_key)  # type: ignore
        self.client = genai.GenerativeModel(model_name=self.model_name)  # type: ignore
        logger.info(f"Initialized GoogleProvider with model: {self.model_name}")

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text using the Google LLM.

        Args:
            prompt (str): The input prompt for text generation.
            **kwargs: Additional parameters for the generation (e.g., temperature, max_tokens).

        Returns:
            str: The generated text response.

        Raises:
            Exception: If the API call fails.
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.generate_content(prompt, **kwargs)
            )  # type: ignore[arg-type]
            generated_text = response.text if response else ""
            logger.debug(f"Generated text for prompt: {prompt[:50]}...")
            return generated_text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Retrieve information about the current model.

        Returns:
            Dict[str, Any]: A dictionary containing model metadata.
        """
        # Placeholder for model info; adjust based on actual API capabilities
        info = {
            "provider": "Google",
            "model_name": self.model_name,
            "supported_features": ["text_generation"],
        }
        return info

    async def list_available_models(self) -> List[str]:
        """
        List available models from Google.

        Returns:
            List[str]: A list of available model names.
        """
        try:
            models = genai.list_models()  # type: ignore
            model_names = [
                model.name
                for model in models
                if "generateContent" in model.supported_generation_methods
            ]
            return model_names
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
