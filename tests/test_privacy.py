"""
Tests for privacy module (PII anonymization, content filtering, and validation).
"""

import pytest

# Check if privacy module is available
try:
    from llm2slm.privacy import (
        detoxify_available,
        presidio_available,
    )

    PRIVACY_MODULE_AVAILABLE = True
except ImportError:
    PRIVACY_MODULE_AVAILABLE = False

    def presidio_available():
        return False

    def detoxify_available():
        return False


# ────────────────────────────────────────────────────────────────────────────────
# Anonymizer Tests
# ────────────────────────────────────────────────────────────────────────────────


@pytest.mark.skipif(not presidio_available(), reason="Presidio not available")
class TestPIIAnonymizer:
    """Test PII anonymization with Presidio."""

    def test_anonymizer_init(self):
        """Test anonymizer initialization."""
        from llm2slm.privacy import AnonymizationConfig, PIIAnonymizer

        config = AnonymizationConfig(enabled=True)
        anonymizer = PIIAnonymizer(config)

        assert anonymizer.config.enabled is True
        assert anonymizer.analyzer is not None
        assert anonymizer.anonymizer is not None

    def test_detect_pii_email(self):
        """Test PII detection for email addresses."""
        from llm2slm.privacy import AnonymizationConfig, PIIAnonymizer

        config = AnonymizationConfig(enabled=True, entities={"EMAIL_ADDRESS"})
        anonymizer = PIIAnonymizer(config)

        text = "Contact me at john@example.com for more info."
        results = anonymizer.detect_pii(text)

        assert len(results) > 0
        assert any(r["entity_type"] == "EMAIL_ADDRESS" for r in results)

    def test_anonymize_email_mask(self):
        """Test email anonymization with masking."""
        from llm2slm.privacy import AnonymizationConfig, AnonymizationMethod, PIIAnonymizer

        config = AnonymizationConfig(
            enabled=True, method=AnonymizationMethod.MASK, entities={"EMAIL_ADDRESS"}
        )
        anonymizer = PIIAnonymizer(config)

        text = "Contact john@example.com"
        result = anonymizer.anonymize(text)

        assert "john@example.com" not in result
        assert "*" in result or "EMAIL" in result

    def test_anonymize_disabled(self):
        """Test that anonymization is skipped when disabled."""
        from llm2slm.privacy import AnonymizationConfig, PIIAnonymizer

        config = AnonymizationConfig(enabled=False)
        anonymizer = PIIAnonymizer(config)

        text = "Contact john@example.com"
        result = anonymizer.anonymize(text)

        assert result == text  # Should return unchanged

    def test_anonymize_batch(self):
        """Test batch anonymization."""
        from llm2slm.privacy import AnonymizationConfig, PIIAnonymizer

        config = AnonymizationConfig(enabled=True, entities={"EMAIL_ADDRESS"})
        anonymizer = PIIAnonymizer(config)

        texts = [
            "Email: john@example.com",
            "Contact: jane@example.com",
        ]
        results = anonymizer.anonymize_batch(texts)

        assert len(results) == 2
        assert all("@example.com" not in r for r in results)

    def test_validate_text_with_pii(self):
        """Test validation detects PII."""
        from llm2slm.privacy import AnonymizationConfig, PIIAnonymizer

        config = AnonymizationConfig(enabled=True, entities={"EMAIL_ADDRESS"})
        anonymizer = PIIAnonymizer(config)

        text = "Email: john@example.com"
        has_pii = anonymizer.validate_text(text)

        assert has_pii is True

    def test_validate_text_without_pii(self):
        """Test validation with clean text."""
        from llm2slm.privacy import AnonymizationConfig, PIIAnonymizer

        config = AnonymizationConfig(enabled=True, entities={"EMAIL_ADDRESS"})
        anonymizer = PIIAnonymizer(config)

        text = "This is a clean text without any PII."
        has_pii = anonymizer.validate_text(text)

        assert has_pii is False


# Regex fallback tests (always available)
class TestRegexPIIAnonymizer:
    """Test regex-based PII anonymizer (fallback)."""

    def test_regex_anonymizer_init(self):
        """Test regex anonymizer initialization."""
        from llm2slm.privacy.anonymizer import AnonymizationConfig, RegexPIIAnonymizer

        config = AnonymizationConfig(enabled=True)
        anonymizer = RegexPIIAnonymizer(config)

        assert anonymizer.config.enabled is True
        assert len(anonymizer.patterns) > 0

    def test_regex_detect_email(self):
        """Test regex email detection."""
        from llm2slm.privacy.anonymizer import AnonymizationConfig, RegexPIIAnonymizer

        config = AnonymizationConfig(enabled=True, entities={"EMAIL_ADDRESS"})
        anonymizer = RegexPIIAnonymizer(config)

        text = "Contact john@example.com"
        results = anonymizer.detect_pii(text)

        assert len(results) > 0
        assert results[0]["entity_type"] == "EMAIL_ADDRESS"

    def test_regex_anonymize_mask(self):
        """Test regex masking."""
        from llm2slm.privacy.anonymizer import (
            AnonymizationConfig,
            AnonymizationMethod,
            RegexPIIAnonymizer,
        )

        config = AnonymizationConfig(
            enabled=True, method=AnonymizationMethod.MASK, entities={"EMAIL_ADDRESS"}
        )
        anonymizer = RegexPIIAnonymizer(config)

        text = "Email: test@example.com"
        result = anonymizer.anonymize(text)

        assert "test@example.com" not in result
        assert "*" in result


# ────────────────────────────────────────────────────────────────────────────────
# Content Filter Tests
# ────────────────────────────────────────────────────────────────────────────────


@pytest.mark.skipif(not detoxify_available(), reason="Detoxify not available")
class TestContentFilter:
    """Test content filtering with Detoxify."""

    def test_filter_init(self):
        """Test content filter initialization."""
        from llm2slm.privacy import ContentFilter, FilterConfig

        config = FilterConfig(enabled=True)
        content_filter = ContentFilter(config)

        assert content_filter.config.enabled is True
        assert content_filter.model is not None

    def test_analyze_clean_text(self):
        """Test analysis of clean text."""
        from llm2slm.privacy import ContentFilter, FilterConfig

        config = FilterConfig(enabled=True)
        content_filter = ContentFilter(config)

        text = "This is a normal, friendly message."
        scores = content_filter.analyze(text)

        assert isinstance(scores, dict)
        # Clean text should have low toxicity scores
        if "toxicity" in scores:
            assert scores["toxicity"] < 0.5

    def test_filter_clean_text_passes(self):
        """Test that clean text passes filtering."""
        from llm2slm.privacy import ContentFilter, FilterConfig

        config = FilterConfig(enabled=True)
        content_filter = ContentFilter(config)

        text = "Hello, how are you doing today?"
        result = content_filter.filter(text)

        assert result.passed is True
        assert len(result.violations) == 0

    def test_filter_disabled(self):
        """Test that filtering is skipped when disabled."""
        from llm2slm.privacy import ContentFilter, FilterConfig

        config = FilterConfig(enabled=False)
        content_filter = ContentFilter(config)

        text = "Any text here"
        result = content_filter.filter(text)

        assert result.passed is True
        assert result.text == text

    def test_filter_batch(self):
        """Test batch filtering."""
        from llm2slm.privacy import ContentFilter, FilterConfig

        config = FilterConfig(enabled=True)
        content_filter = ContentFilter(config)

        texts = [
            "Hello world",
            "Nice to meet you",
        ]
        results = content_filter.filter_batch(texts)

        assert len(results) == 2
        assert all(isinstance(r.passed, bool) for r in results)


# Regex fallback tests
class TestRegexContentFilter:
    """Test regex-based content filter (fallback)."""

    def test_regex_filter_init(self):
        """Test regex filter initialization."""
        from llm2slm.privacy.filter import FilterConfig, RegexContentFilter

        config = FilterConfig(enabled=True)
        content_filter = RegexContentFilter(config)

        assert content_filter.config.enabled is True
        assert len(content_filter.profanity_patterns) > 0

    def test_regex_analyze(self):
        """Test regex analysis."""
        from llm2slm.privacy.filter import FilterConfig, RegexContentFilter

        config = FilterConfig(enabled=True)
        content_filter = RegexContentFilter(config)

        text = "This is a clean text"
        scores = content_filter.analyze(text)

        assert isinstance(scores, dict)

    def test_regex_filter_clean_text(self):
        """Test regex filtering of clean text."""
        from llm2slm.privacy.filter import FilterConfig, RegexContentFilter

        config = FilterConfig(enabled=True)
        content_filter = RegexContentFilter(config)

        text = "Hello, nice day!"
        result = content_filter.filter(text)

        assert result.passed is True


# ────────────────────────────────────────────────────────────────────────────────
# Privacy Validator Tests
# ────────────────────────────────────────────────────────────────────────────────


class TestPrivacyValidator:
    """Test privacy validation."""

    def test_validator_init(self):
        """Test validator initialization."""
        from llm2slm.privacy import PrivacyLevel, PrivacyValidator

        validator = PrivacyValidator(level=PrivacyLevel.MEDIUM)

        assert validator.level == PrivacyLevel.MEDIUM
        assert validator.audit_log is not None

    def test_validate_without_tools(self):
        """Test validation without anonymizer or filter."""
        from llm2slm.privacy import PrivacyLevel, PrivacyValidator

        validator = PrivacyValidator(level=PrivacyLevel.LOW)

        text = "Some text here"
        result = validator.validate(text)

        assert isinstance(result.passed, bool)
        assert result.level == PrivacyLevel.LOW

    def test_validate_batch(self):
        """Test batch validation."""
        from llm2slm.privacy import PrivacyLevel, PrivacyValidator

        validator = PrivacyValidator(level=PrivacyLevel.LOW)

        texts = ["Text 1", "Text 2", "Text 3"]
        results = validator.validate_batch(texts)

        assert len(results) == 3
        assert all(hasattr(r, "passed") for r in results)

    def test_get_audit_summary(self):
        """Test audit log summary."""
        from llm2slm.privacy import PrivacyLevel, PrivacyValidator

        validator = PrivacyValidator(level=PrivacyLevel.MEDIUM)

        # Run some validations to generate audit entries
        validator.validate("Test 1")
        validator.validate("Test 2")

        summary = validator.get_audit_summary()

        assert "total_entries" in summary
        assert summary["total_entries"] >= 2


class TestAuditLog:
    """Test audit logging."""

    def test_audit_log_init(self):
        """Test audit log initialization."""
        from llm2slm.privacy import AuditLog

        audit_log = AuditLog()

        assert len(audit_log.entries) == 0

    def test_audit_log_add_entry(self):
        """Test adding audit entries."""
        from llm2slm.privacy import AuditLog
        from llm2slm.privacy.validator import AuditAction

        audit_log = AuditLog()

        audit_log.add(action=AuditAction.PII_DETECTED, details={"count": 5}, user="test_user")

        assert len(audit_log.entries) == 1
        assert audit_log.entries[0].action == AuditAction.PII_DETECTED

    def test_audit_log_get_entries_filtered(self):
        """Test filtered audit entry retrieval."""
        from llm2slm.privacy import AuditLog
        from llm2slm.privacy.validator import AuditAction

        audit_log = AuditLog()

        audit_log.add(action=AuditAction.PII_DETECTED, details={})
        audit_log.add(action=AuditAction.CONTENT_FILTERED, details={})
        audit_log.add(action=AuditAction.PII_DETECTED, details={})

        filtered = audit_log.get_entries(action=AuditAction.PII_DETECTED)

        assert len(filtered) == 2

    def test_audit_log_summary(self):
        """Test audit log summary generation."""
        from llm2slm.privacy import AuditLog
        from llm2slm.privacy.validator import AuditAction

        audit_log = AuditLog()

        audit_log.add(action=AuditAction.PII_DETECTED, details={})
        audit_log.add(action=AuditAction.VALIDATION_PASSED, details={})

        summary = audit_log.get_summary()

        assert summary["total_entries"] == 2
        assert "action_counts" in summary
