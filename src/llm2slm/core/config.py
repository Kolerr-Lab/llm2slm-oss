import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

"""
Configuration module for the llm2slm project.

This module provides a centralized configuration management system for the LLM to SLM
conversion tool. It supports loading configurations from environment variables, YAML
files, and provides default values with validation.

The configuration includes settings for:
- Model conversion parameters
- Provider integrations (e.g., OpenAI API keys)
- Server settings (e.g., host, port for FastAPI)
- Logging levels and output
- Pipeline options

Example usage:

    config = Config.load_from_env()
    print(config.openai_api_key)
"""


@dataclass
class Config:
    """
    Main configuration class for the llm2slm application.

    Attributes:
        openai_api_key (str): API key for OpenAI provider.
        anthropic_api_key (str): API key for Anthropic provider.
        google_api_key (str): API key for Google provider.
        liquid_api_key (str): API key for LiquidAI provider.
        model_name (str): Name of the LLM to convert (default: 'gpt-3.5-turbo').
        output_dir (Path): Directory to save converted SLM models.
        server_host (str): Host for the FastAPI server (default: 'localhost').
        server_port (int): Port for the FastAPI server (default: 8000).
        log_level (str): Logging level (default: 'INFO').
        pipeline_steps (list[str]): List of pipeline steps for conversion.
        custom_settings (Dict[str, Any]): Additional custom settings.
    """

    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    liquid_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    server_host: str = "localhost"
    server_port: int = 8000
    log_level: str = "INFO"
    pipeline_steps: list[str] = field(default_factory=lambda: ["load", "compress", "export"])
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load_from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

        Raises:
            ValueError: If required environment variables are missing.

        Returns:
            Config: An instance of Config populated from environment variables.
        """
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required.")

        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        liquid_api_key = os.getenv("LIQUID_API_KEY")

        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        server_host = os.getenv("SERVER_HOST", "localhost")
        server_port_str = os.getenv("SERVER_PORT", "8000")
        try:
            server_port = int(server_port_str)
        except ValueError as err:
            raise ValueError(
                f"Invalid SERVER_PORT value: {server_port_str}. Must be an integer."
            ) from err

        log_level = os.getenv("LOG_LEVEL", "INFO")
        pipeline_steps_str = os.getenv("PIPELINE_STEPS", "load,compress,export")
        pipeline_steps = [step.strip() for step in pipeline_steps_str.split(",")]

        return cls(
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            google_api_key=google_api_key,
            liquid_api_key=liquid_api_key,
            model_name=model_name,
            output_dir=output_dir,
            server_host=server_host,
            server_port=server_port,
            log_level=log_level,
            pipeline_steps=pipeline_steps,
        )

    @classmethod
    def load_from_yaml(cls, file_path: Union[str, Path]) -> "Config":
        """
        Load configuration from a YAML file.

        Args:
            file_path (Union[str, Path]): Path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If the YAML file is malformed.
            ValueError: If required fields are missing or invalid.

        Returns:
            Config: An instance of Config populated from the YAML file.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("YAML configuration must be a dictionary.")

        openai_api_key = data.get("openai_api_key")
        if not openai_api_key:
            raise ValueError("openai_api_key is required in the YAML configuration.")

        model_name = data.get("model_name", "gpt-3.5-turbo")
        output_dir = Path(data.get("output_dir", "./output"))
        server_host = data.get("server_host", "localhost")
        server_port = data.get("server_port", 8000)
        if not isinstance(server_port, int):
            raise ValueError("server_port must be an integer.")

        log_level = data.get("log_level", "INFO")
        pipeline_steps = data.get("pipeline_steps", ["load", "compress", "export"])
        if not isinstance(pipeline_steps, list):
            raise ValueError("pipeline_steps must be a list of strings.")

        custom_settings = data.get("custom_settings", {})

        return cls(
            openai_api_key=openai_api_key,
            model_name=model_name,
            output_dir=output_dir,
            server_host=server_host,
            server_port=server_port,
            log_level=log_level,
            pipeline_steps=pipeline_steps,
            custom_settings=custom_settings,
        )

    def setup_logging(self) -> None:
        """
        Configure logging based on the log_level setting.

        This method sets up the root logger with the specified level and a standard
        formatter. It should be called after loading the configuration.
        """
        level = getattr(logging, self.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def validate(self) -> None:
        """
        Validate the configuration settings.

        Raises:
            ValueError: If any setting is invalid (e.g., invalid log level).
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log_level: {self.log_level}. Must be one of {valid_levels}.")

        if not self.pipeline_steps:
            raise ValueError("pipeline_steps cannot be empty.")

        if not isinstance(self.custom_settings, dict):
            raise ValueError("custom_settings must be a dictionary.")
