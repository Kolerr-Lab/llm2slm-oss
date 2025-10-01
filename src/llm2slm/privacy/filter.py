"""
Content Filter for LLM2SLM.

Semantic content filtering for toxicity, profanity, hate speech, and harmful content
using Detoxify and custom filters.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

try:
    from detoxify import Detoxify

    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False


class ContentCategory(str, Enum):
    """Content filtering categories."""

    TOXICITY = "toxicity"
    SEVERE_TOXICITY = "severe_toxicity"
    OBSCENE = "obscene"
    THREAT = "threat"
    INSULT = "insult"
    IDENTITY_ATTACK = "identity_attack"
    SEXUAL_EXPLICIT = "sexual_explicit"
    PROFANITY = "profanity"
    HATE_SPEECH = "hate_speech"


class FilterAction(str, Enum):
    """Actions to take when content violates filters."""

    ALLOW = "allow"  # Allow content to pass
    FLAG = "flag"  # Flag but allow
    REDACT = "redact"  # Remove violating content
    REJECT = "reject"  # Reject entire text


@dataclass
class FilterConfig:
    """Configuration for content filtering."""

    enabled: bool = True
    categories: Set[ContentCategory] = field(
        default_factory=lambda: {
            ContentCategory.TOXICITY,
            ContentCategory.SEVERE_TOXICITY,
            ContentCategory.OBSCENE,
            ContentCategory.THREAT,
            ContentCategory.INSULT,
            ContentCategory.IDENTITY_ATTACK,
        }
    )
    thresholds: Dict[ContentCategory, float] = field(
        default_factory=lambda: {
            ContentCategory.TOXICITY: 0.7,
            ContentCategory.SEVERE_TOXICITY: 0.5,
            ContentCategory.OBSCENE: 0.7,
            ContentCategory.THREAT: 0.5,
            ContentCategory.INSULT: 0.7,
            ContentCategory.IDENTITY_ATTACK: 0.7,
            ContentCategory.SEXUAL_EXPLICIT: 0.8,
            ContentCategory.PROFANITY: 0.7,
            ContentCategory.HATE_SPEECH: 0.6,
        }
    )
    action: FilterAction = FilterAction.FLAG
    custom_blocklist: Set[str] = field(default_factory=set)
    model_name: str = "original"  # Detoxify model: original, unbiased, multilingual


@dataclass
class FilterResult:
    """Result of content filtering."""

    text: str
    passed: bool
    violations: List[Dict[str, Any]] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    action_taken: FilterAction = FilterAction.ALLOW


class ContentFilter:
    """Semantic content filter using Detoxify."""

    def __init__(self, config: Optional[FilterConfig] = None):
        """
        Initialize content filter.

        Args:
            config: Filter configuration

        Raises:
            ImportError: If detoxify is not installed
        """
        if not DETOXIFY_AVAILABLE:
            raise ImportError(
                "Detoxify is not installed. Install with: "
                "pip install llm2slm[privacy] or pip install detoxify"
            )

        self.config = config or FilterConfig()
        self.model = Detoxify(self.config.model_name)

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze text for harmful content.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of scores for each category
        """
        if not text or not text.strip():
            return {}

        # Get predictions from Detoxify
        results = self.model.predict(text)

        # Normalize keys to match our ContentCategory enum
        normalized = {}
        for key, value in results.items():
            try:
                category = ContentCategory(key.lower())
                normalized[category.value] = float(value)
            except (ValueError, KeyError):
                # Skip categories not in our enum
                pass

        return normalized

    def filter(self, text: str) -> FilterResult:
        """
        Filter text based on content policy.

        Args:
            text: Text to filter

        Returns:
            FilterResult with filtering decision and details
        """
        if not self.config.enabled:
            return FilterResult(text=text, passed=True, action_taken=FilterAction.ALLOW)

        # Check custom blocklist first
        if self._check_blocklist(text):
            return FilterResult(
                text=(
                    "[BLOCKED - Custom Blocklist]"
                    if self.config.action == FilterAction.REDACT
                    else text
                ),
                passed=False,
                violations=[{"category": "custom_blocklist", "score": 1.0}],
                action_taken=self.config.action,
            )

        # Analyze with Detoxify
        scores = self.analyze(text)

        # Check violations
        violations = []
        for category in self.config.categories:
            category_value = category.value
            if category_value in scores:
                score = scores[category_value]
                threshold = self.config.thresholds.get(category, 0.7)

                if score >= threshold:
                    violations.append(
                        {
                            "category": category_value,
                            "score": score,
                            "threshold": threshold,
                        }
                    )

        # Determine action
        passed = len(violations) == 0

        if not passed:
            if self.config.action == FilterAction.REDACT:
                filtered_text = (
                    f"[CONTENT FILTERED - {', '.join(v['category'] for v in violations)}]"
                )
            elif self.config.action == FilterAction.REJECT:
                filtered_text = "[REJECTED]"
            else:
                filtered_text = text
        else:
            filtered_text = text

        return FilterResult(
            text=filtered_text,
            passed=passed,
            violations=violations,
            scores=scores,
            action_taken=self.config.action if not passed else FilterAction.ALLOW,
        )

    def filter_batch(self, texts: List[str]) -> List[FilterResult]:
        """
        Filter multiple texts.

        Args:
            texts: List of texts to filter

        Returns:
            List of FilterResults
        """
        return [self.filter(text) for text in texts]

    def _check_blocklist(self, text: str) -> bool:
        """Check if text contains blocklisted terms."""
        if not self.config.custom_blocklist:
            return False

        text_lower = text.lower()
        for term in self.config.custom_blocklist:
            if term.lower() in text_lower:
                return True
        return False


# Fallback regex-based content filter (when Detoxify is not available)
class RegexContentFilter:
    """Simple regex-based content filter (fallback when Detoxify unavailable)."""

    def __init__(self, config: Optional[FilterConfig] = None):
        """Initialize regex-based filter."""
        self.config = config or FilterConfig()

        # Common profanity patterns (basic example - expand as needed)
        self.profanity_patterns = [
            r"\b(fuck|shit|damn|ass|bitch|bastard|crap)\b",
            r"\b(hell|piss|dick|pussy|cock|whore|slut)\b",
        ]

    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze text using regex patterns."""
        if not text:
            return {}

        scores = {category.value: 0.0 for category in ContentCategory}

        # Simple profanity detection
        text_lower = text.lower()
        for pattern in self.profanity_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                scores[ContentCategory.PROFANITY.value] = min(1.0, len(matches) * 0.3)
                scores[ContentCategory.TOXICITY.value] = min(0.8, len(matches) * 0.2)

        return scores

    def filter(self, text: str) -> FilterResult:
        """Filter text using regex patterns."""
        if not self.config.enabled:
            return FilterResult(text=text, passed=True, action_taken=FilterAction.ALLOW)

        scores = self.analyze(text)

        # Check violations
        violations = []
        for category in self.config.categories:
            if category.value in scores:
                score = scores[category.value]
                threshold = self.config.thresholds.get(category, 0.7)

                if score >= threshold:
                    violations.append(
                        {
                            "category": category.value,
                            "score": score,
                            "threshold": threshold,
                        }
                    )

        passed = len(violations) == 0

        if not passed and self.config.action == FilterAction.REDACT:
            # Remove profanity with regex
            filtered_text = text
            for pattern in self.profanity_patterns:
                filtered_text = re.sub(pattern, "[FILTERED]", filtered_text, flags=re.IGNORECASE)
        else:
            filtered_text = text

        return FilterResult(
            text=filtered_text,
            passed=passed,
            violations=violations,
            scores=scores,
            action_taken=self.config.action if not passed else FilterAction.ALLOW,
        )

    def filter_batch(self, texts: List[str]) -> List[FilterResult]:
        """Filter multiple texts."""
        return [self.filter(text) for text in texts]
