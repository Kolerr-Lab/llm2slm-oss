"""
PII Anonymizer for LLM2SLM.

Detects and anonymizes Personally Identifiable Information (PII) in text data
using Microsoft Presidio framework.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig

    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    AnalyzerEngine = Any  # type: ignore
    AnonymizerEngine = Any  # type: ignore
    OperatorConfig = Any  # type: ignore


class AnonymizationMethod(str, Enum):
    """Anonymization methods."""

    MASK = "mask"  # Replace with asterisks: john@email.com -> ****@*****.***
    REDACT = "redact"  # Remove completely: john@email.com -> [REDACTED]
    REPLACE = "replace"  # Replace with placeholder: john@email.com -> <EMAIL>
    HASH = "hash"  # Replace with hash: john@email.com -> hash_abc123
    ENCRYPT = "encrypt"  # Encrypt (reversible): john@email.com -> [ENCRYPTED]


@dataclass
class AnonymizationConfig:
    """Configuration for PII anonymization."""

    enabled: bool = True
    method: AnonymizationMethod = AnonymizationMethod.MASK
    entities: Set[str] = field(
        default_factory=lambda: {
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "CREDIT_CARD",
            "US_SSN",
            "PERSON",
            "LOCATION",
            "DATE_TIME",
            "US_PASSPORT",
            "US_DRIVER_LICENSE",
            "IP_ADDRESS",
            "IBAN_CODE",
            "MEDICAL_LICENSE",
            "CRYPTO",
        }
    )
    language: str = "en"
    score_threshold: float = 0.6  # Confidence threshold for PII detection
    mask_char: str = "*"
    custom_patterns: Dict[str, str] = field(default_factory=dict)


class PIIAnonymizer:
    """PII detection and anonymization using Microsoft Presidio."""

    def __init__(self, config: Optional[AnonymizationConfig] = None):
        """
        Initialize PII anonymizer.

        Args:
            config: Anonymization configuration

        Raises:
            ImportError: If presidio packages are not installed
        """
        if not PRESIDIO_AVAILABLE:
            raise ImportError(
                "Presidio is not installed. Install with: "
                "pip install llm2slm[privacy] or "
                "pip install presidio-analyzer presidio-anonymizer"
            )

        self.config = config or AnonymizationConfig()
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII entities in text.

        Args:
            text: Input text to analyze

        Returns:
            List of detected PII entities with type, location, and confidence score
        """
        results = self.analyzer.analyze(
            text=text,
            language=self.config.language,
            entities=list(self.config.entities) if self.config.entities else None,
            score_threshold=self.config.score_threshold,
        )

        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start : result.end],
            }
            for result in results
        ]

    def anonymize(self, text: str) -> str:
        """
        Anonymize PII in text.

        Args:
            text: Input text to anonymize

        Returns:
            Anonymized text
        """
        if not self.config.enabled:
            return text

        # Analyze text for PII
        analyzer_results = self.analyzer.analyze(
            text=text,
            language=self.config.language,
            entities=list(self.config.entities) if self.config.entities else None,
            score_threshold=self.config.score_threshold,
        )

        # Configure anonymization operators
        operators = self._get_operators()

        # Anonymize
        anonymized_result = self.anonymizer.anonymize(
            text=text, analyzer_results=analyzer_results, operators=operators
        )

        return anonymized_result.text

    def anonymize_batch(self, texts: List[str]) -> List[str]:
        """
        Anonymize multiple texts.

        Args:
            texts: List of texts to anonymize

        Returns:
            List of anonymized texts
        """
        return [self.anonymize(text) for text in texts]

    def _get_operators(self) -> Dict[str, OperatorConfig]:
        """Get anonymization operators based on method."""
        if self.config.method == AnonymizationMethod.MASK:
            return {
                "DEFAULT": OperatorConfig(
                    "mask",
                    {
                        "masking_char": self.config.mask_char,
                        "chars_to_mask": 100,
                        "from_end": False,
                    },
                )
            }
        elif self.config.method == AnonymizationMethod.REDACT:
            return {"DEFAULT": OperatorConfig("redact", {})}
        elif self.config.method == AnonymizationMethod.REPLACE:
            return {"DEFAULT": OperatorConfig("replace", {})}
        elif self.config.method == AnonymizationMethod.HASH:
            return {"DEFAULT": OperatorConfig("hash", {"hash_type": "sha256"})}
        elif self.config.method == AnonymizationMethod.ENCRYPT:
            return {"DEFAULT": OperatorConfig("encrypt", {"key": "WmZq4t7w!z%C*F-J"})}
        else:
            return {}

    def validate_text(self, text: str) -> bool:
        """
        Check if text contains PII.

        Args:
            text: Text to validate

        Returns:
            True if text contains PII, False otherwise
        """
        results = self.analyzer.analyze(
            text=text,
            language=self.config.language,
            entities=list(self.config.entities) if self.config.entities else None,
            score_threshold=self.config.score_threshold,
        )
        return len(results) > 0


# Fallback regex-based anonymizer (when Presidio is not available)
class RegexPIIAnonymizer:
    """Simple regex-based PII anonymizer (fallback when Presidio unavailable)."""

    def __init__(self, config: Optional[AnonymizationConfig] = None):
        """Initialize regex-based anonymizer."""
        self.config = config or AnonymizationConfig()

        # Common PII patterns
        self.patterns = {
            "EMAIL_ADDRESS": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE_NUMBER": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "CREDIT_CARD": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
            "US_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        }

    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using regex patterns."""
        results = []
        for entity_type, pattern in self.patterns.items():
            if entity_type not in self.config.entities:
                continue

            for match in re.finditer(pattern, text):
                results.append(
                    {
                        "entity_type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "score": 0.9,  # Fixed confidence for regex
                        "text": match.group(),
                    }
                )
        return results

    def anonymize(self, text: str) -> str:
        """Anonymize PII using regex replacement."""
        if not self.config.enabled:
            return text

        result = text
        for entity_type, pattern in self.patterns.items():
            if entity_type not in self.config.entities:
                continue

            if self.config.method == AnonymizationMethod.MASK:
                result = re.sub(pattern, lambda m: self.config.mask_char * len(m.group()), result)
            elif self.config.method == AnonymizationMethod.REDACT:
                result = re.sub(pattern, "[REDACTED]", result)
            elif self.config.method == AnonymizationMethod.REPLACE:
                result = re.sub(pattern, f"<{entity_type}>", result)

        return result

    def anonymize_batch(self, texts: List[str]) -> List[str]:
        """Anonymize multiple texts."""
        return [self.anonymize(text) for text in texts]

    def validate_text(self, text: str) -> bool:
        """Check if text contains PII."""
        for entity_type, pattern in self.patterns.items():
            if entity_type not in self.config.entities:
                continue
            if re.search(pattern, text):
                return True
        return False
