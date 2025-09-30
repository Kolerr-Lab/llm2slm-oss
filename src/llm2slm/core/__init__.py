import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .config import Config
from .pipeline import Pipeline

"""
Core package for LLM2SLM.

This package contains the core functionality for the LLM to SLM conversion process,
including configuration management and pipeline orchestration.

Modules:
    - config: Configuration management and validation
    - pipeline: Main conversion pipeline implementation

Usage:
    from llm2slm.core import Config, Pipeline, convert_model, load_config, save_config
"""


async def convert_model(
    input_model: str,
    output_path: str,
    provider: str = "openai",
    compression_factor: float = 0.5,
    config: Optional[Config] = None,
) -> dict:
    """
    Convert a Large Language Model to a Small Language Model.

    This is a convenience function that sets up and runs the conversion pipeline.

    Args:
        input_model: Path or identifier of the input LLM model
        output_path: Path to save the converted SLM
        provider: Model provider ("openai", "local", etc.)
        compression_factor: Factor to reduce model size (0.0 to 1.0)
        config: Optional configuration object

    Returns:
        Dictionary with conversion results
    """
    if config is None:
        try:
            config = Config.load_from_env()
        except ValueError:
            # Fallback to default config if env vars not set
            config = Config(openai_api_key="dummy_key")

    pipeline_config = {
        "input_model": input_model,
        "output_path": output_path,
        "provider": provider,
        "compression_factor": compression_factor,
        "openai_api_key": config.openai_api_key,
        "model_name": config.model_name,
        "output_dir": str(config.output_dir),
    }

    pipeline = Pipeline(pipeline_config)
    result = await pipeline.run()
    return result


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables or config file.

    Returns:
        Dictionary containing configuration values
    """
    try:
        config = Config.load_from_env()
        return {
            "openai_api_key": config.openai_api_key,
            "model_name": config.model_name,
            "output_dir": str(config.output_dir),
            "server_host": config.server_host,
            "server_port": config.server_port,
            "log_level": config.log_level,
            "pipeline_steps": config.pipeline_steps,
            "custom_settings": config.custom_settings,
        }
    except ValueError:
        # Return default config if env vars not set
        return {
            "openai_api_key": "",
            "model_name": "gpt-3.5-turbo",
            "output_dir": "./output",
            "server_host": "localhost",
            "server_port": 8000,
            "log_level": "INFO",
            "pipeline_steps": ["load", "compress", "export"],
            "custom_settings": {},
        }


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to a JSON file.

    Args:
        config: Configuration dictionary to save
    """
    config_dir = Path.home() / ".llm2slm"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.json"

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
