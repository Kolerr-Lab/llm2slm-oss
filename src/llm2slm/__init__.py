"""LLM2SLM - Large Language Model to Small Language Model Converter.

A Python package for converting Large Language Models (LLMs) to optimized
Small Language Models (SLMs) with CLI interface, server components, and
provider integrations.
"""

__version__ = "0.1.0"
__author__ = "Kolerr Lab"
__email__ = "ricky@kolerr.com"

from .cli import cli
from .core.config import Config
from .core.pipeline import Pipeline

__all__ = ["cli", "Config", "Pipeline"]
