"""
Privacy module for LLM2SLM.

Provides PII detection, anonymization, content filtering, and privacy validation
for secure model conversion and deployment.
"""

from typing import TYPE_CHECKING

from llm2slm.privacy.validator import AuditLog, PrivacyLevel, PrivacyValidator

# Check for optional privacy dependencies
_presidio_available = False
_detoxify_available = False

try:
    import presidio_analyzer  # noqa: F401
    import presidio_anonymizer  # noqa: F401

    _presidio_available = True
except ImportError:
    pass

try:
    import detoxify  # noqa: F401

    _detoxify_available = True
except ImportError:
    pass

# Conditional imports
if TYPE_CHECKING or _presidio_available:
    from llm2slm.privacy.anonymizer import (
        AnonymizationConfig,
        AnonymizationMethod,
        PIIAnonymizer,
    )
else:
    PIIAnonymizer = None  # type: ignore
    AnonymizationConfig = None  # type: ignore
    AnonymizationMethod = None  # type: ignore

if TYPE_CHECKING or _detoxify_available:
    from llm2slm.privacy.filter import (
        ContentCategory,
        ContentFilter,
        FilterAction,
        FilterConfig,
    )
else:
    ContentFilter = None  # type: ignore
    FilterConfig = None  # type: ignore
    ContentCategory = None  # type: ignore
    FilterAction = None  # type: ignore


__all__ = [
    "PIIAnonymizer",
    "AnonymizationConfig",
    "AnonymizationMethod",
    "ContentFilter",
    "FilterConfig",
    "ContentCategory",
    "FilterAction",
    "PrivacyValidator",
    "PrivacyLevel",
    "AuditLog",
    "presidio_available",
    "detoxify_available",
]


def presidio_available() -> bool:
    """Check if Presidio (PII detection) is available."""
    return _presidio_available


def detoxify_available() -> bool:
    """Check if Detoxify (content filtering) is available."""
    return _detoxify_available
