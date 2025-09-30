from .base import BaseProvider
from .openai import OpenAIProvider

# Optional imports for providers that may not be installed
try:
    from .anthropic import AnthropicProvider

    _anthropic_available = True
except ImportError:
    _anthropic_available = False
    AnthropicProvider = None  # type: ignore

try:
    # from .google import GoogleProvider
    GoogleProvider = None  # type: ignore
    _google_available = False
except ImportError:
    _google_available = False
    GoogleProvider = None  # type: ignore

try:
    from .liquid import LiquidProvider

    _liquid_available = True
except ImportError:
    _liquid_available = False
    LiquidProvider = None  # type: ignore

"""
Providers package for LLM2SLM.

This package contains integrations with various Large Language Model (LLM) providers,
such as OpenAI, Anthropic, Google, and LiquidAI, to facilitate model conversion and interaction.
It provides a unified interface for accessing different providers while ensuring high code quality,
maintainability, and adherence to project guidelines.

Modules:
    - base: Defines the base provider interface and common functionality.
    - openai: Implements the OpenAI provider integration.
    - anthropic: Implements the Anthropic Claude provider integration (optional).
    - google: Implements the Google Gemini provider integration (optional).
    - liquid: Implements the LiquidAI provider integration (optional).

Usage:
    Import specific providers as needed, e.g., from llm2slm.providers import AnthropicProvider.
"""


def get_available_providers() -> list[str]:
    """Get a list of available provider names."""
    providers = ["openai"]  # OpenAI is always available
    if _anthropic_available:
        providers.append("anthropic")
    if _google_available:
        providers.append("google")
    if _liquid_available:
        providers.append("liquid")
    return providers  # TODO: Make this dynamic based on installed/available providers


__all__ = ["BaseProvider", "OpenAIProvider"]
if _anthropic_available:
    __all__.append("AnthropicProvider")
if _google_available:
    __all__.append("GoogleProvider")
if _liquid_available:
    __all__.append("LiquidProvider")
