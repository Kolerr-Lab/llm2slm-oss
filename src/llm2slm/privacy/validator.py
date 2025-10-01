"""
Privacy Validator for LLM2SLM.

Provides privacy compliance validation and audit logging.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PrivacyLevel(str, Enum):
    """Privacy compliance levels."""

    NONE = "none"  # No privacy checks
    LOW = "low"  # Basic PII detection
    MEDIUM = "medium"  # PII + content filtering
    HIGH = "high"  # Comprehensive privacy + audit logging
    STRICT = "strict"  # Maximum privacy enforcement


class AuditAction(str, Enum):
    """Types of audit actions."""

    PII_DETECTED = "pii_detected"
    PII_ANONYMIZED = "pii_anonymized"
    CONTENT_FILTERED = "content_filtered"
    CONTENT_FLAGGED = "content_flagged"
    CONTENT_REJECTED = "content_rejected"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"


@dataclass
class AuditEntry:
    """Single audit log entry."""

    timestamp: datetime
    action: AuditAction
    details: Dict[str, Any]
    user: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class AuditLog:
    """Audit log for privacy operations."""

    entries: List[AuditEntry] = field(default_factory=list)
    log_file: Optional[Path] = None

    def add(
        self,
        action: AuditAction,
        details: Dict[str, Any],
        user: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Add entry to audit log."""
        entry = AuditEntry(
            timestamp=datetime.now(),
            action=action,
            details=details,
            user=user,
            session_id=session_id,
        )
        self.entries.append(entry)

        # Write to log file if configured
        if self.log_file:
            self._write_to_file(entry)

    def _write_to_file(self, entry: AuditEntry) -> None:
        """Write audit entry to file."""
        if not self.log_file:
            return
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                log_data = {
                    "timestamp": entry.timestamp.isoformat(),
                    "action": entry.action.value,
                    "details": entry.details,
                    "user": entry.user,
                    "session_id": entry.session_id,
                }
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            logging.error(f"Failed to write audit log: {e}")

    def get_entries(
        self,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AuditEntry]:
        """
        Get filtered audit entries.

        Args:
            action: Filter by action type
            start_time: Filter entries after this time
            end_time: Filter entries before this time

        Returns:
            Filtered list of audit entries
        """
        filtered = self.entries

        if action:
            filtered = [e for e in filtered if e.action == action]

        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        return filtered

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of audit log."""
        action_counts = {}
        for entry in self.entries:
            action_counts[entry.action.value] = action_counts.get(entry.action.value, 0) + 1

        return {
            "total_entries": len(self.entries),
            "action_counts": action_counts,
            "first_entry": self.entries[0].timestamp.isoformat() if self.entries else None,
            "last_entry": self.entries[-1].timestamp.isoformat() if self.entries else None,
        }


@dataclass
class ValidationResult:
    """Result of privacy validation."""

    passed: bool
    level: PrivacyLevel
    pii_detected: bool = False
    pii_count: int = 0
    content_violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class PrivacyValidator:
    """Privacy compliance validator."""

    def __init__(
        self,
        level: PrivacyLevel = PrivacyLevel.MEDIUM,
        audit_log: Optional[AuditLog] = None,
    ):
        """
        Initialize privacy validator.

        Args:
            level: Privacy compliance level
            audit_log: Audit log instance (creates new if None)
        """
        self.level = level
        self.audit_log = audit_log or AuditLog()

    def validate(
        self,
        text: str,
        anonymizer: Optional[Any] = None,
        content_filter: Optional[Any] = None,
    ) -> ValidationResult:
        """
        Validate text for privacy compliance.

        Args:
            text: Text to validate
            anonymizer: PIIAnonymizer instance (optional)
            content_filter: ContentFilter instance (optional)

        Returns:
            ValidationResult with validation details
        """
        pii_detected = False
        pii_count = 0
        content_violations = []
        recommendations = []

        # Check PII (if anonymizer provided and level requires it)
        if self.level in [
            PrivacyLevel.LOW,
            PrivacyLevel.MEDIUM,
            PrivacyLevel.HIGH,
            PrivacyLevel.STRICT,
        ]:
            if anonymizer:
                try:
                    pii_entities = anonymizer.detect_pii(text)
                    pii_detected = len(pii_entities) > 0
                    pii_count = len(pii_entities)

                    if pii_detected:
                        self.audit_log.add(
                            action=AuditAction.PII_DETECTED,
                            details={
                                "count": pii_count,
                                "entities": [e["entity_type"] for e in pii_entities],
                            },
                        )
                        recommendations.append(
                            f"Detected {pii_count} PII entities. Consider anonymizing before processing."
                        )
                except Exception as e:
                    logging.warning(f"PII detection failed: {e}")

        # Check content filtering (if filter provided and level requires it)
        if self.level in [PrivacyLevel.MEDIUM, PrivacyLevel.HIGH, PrivacyLevel.STRICT]:
            if content_filter:
                try:
                    filter_result = content_filter.filter(text)
                    if not filter_result.passed:
                        content_violations = filter_result.violations
                        self.audit_log.add(
                            action=AuditAction.CONTENT_FLAGGED,
                            details={
                                "violations": content_violations,
                                "scores": filter_result.scores,
                            },
                        )
                        recommendations.append(
                            f"Content policy violations detected: {', '.join(v['category'] for v in content_violations)}"
                        )
                except Exception as e:
                    logging.warning(f"Content filtering failed: {e}")

        # Determine if validation passed
        passed = True
        if self.level == PrivacyLevel.STRICT:
            passed = not pii_detected and len(content_violations) == 0
        elif self.level == PrivacyLevel.HIGH:
            passed = len(content_violations) == 0
        elif self.level == PrivacyLevel.MEDIUM:
            passed = len([v for v in content_violations if v.get("score", 0) > 0.8]) == 0

        # Log validation result
        self.audit_log.add(
            action=AuditAction.VALIDATION_PASSED if passed else AuditAction.VALIDATION_FAILED,
            details={
                "level": self.level.value,
                "pii_detected": pii_detected,
                "pii_count": pii_count,
                "content_violations": len(content_violations),
            },
        )

        return ValidationResult(
            passed=passed,
            level=self.level,
            pii_detected=pii_detected,
            pii_count=pii_count,
            content_violations=content_violations,
            recommendations=recommendations,
        )

    def validate_batch(
        self,
        texts: List[str],
        anonymizer: Optional[Any] = None,
        content_filter: Optional[Any] = None,
    ) -> List[ValidationResult]:
        """
        Validate multiple texts.

        Args:
            texts: List of texts to validate
            anonymizer: PIIAnonymizer instance (optional)
            content_filter: ContentFilter instance (optional)

        Returns:
            List of ValidationResults
        """
        return [self.validate(text, anonymizer, content_filter) for text in texts]

    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit log summary."""
        return self.audit_log.get_summary()
