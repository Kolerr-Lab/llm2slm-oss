# Privacy & Security Guide

This guide covers the privacy and security features in LLM2SLM, including PII detection, anonymization, content filtering, and compliance validation.

## Overview

LLM2SLM includes comprehensive privacy features to help you:

- **Detect and anonymize** Personally Identifiable Information (PII)
- **Filter harmful content** (toxicity, profanity, hate speech)
- **Validate privacy compliance** with configurable levels
- **Audit privacy operations** for regulatory compliance

## Installation

Install privacy dependencies:

```bash
pip install llm2slm[privacy]
```

This installs:

- **presidio-analyzer** & **presidio-anonymizer**: Microsoft's PII detection framework
- **detoxify**: Content toxicity detection
- **spacy**: Natural language processing

## PII Anonymization

### Supported PII Entities

- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers (US_SSN)
- Person names
- Locations
- Dates and times
- IP addresses
- Passport numbers
- Driver's license numbers
- Medical licenses
- IBAN codes
- Cryptocurrency addresses

### Anonymization Methods

| Method    | Description                                      | Example                                    |
| --------- | ------------------------------------------------ | ------------------------------------------ |
| `mask`    | Replace with masking character                   | `john@email.com` → `****@*****.***`        |
| `redact`  | Remove completely                                | `john@email.com` → `[REDACTED]`            |
| `replace` | Replace with placeholder                         | `john@email.com` → `<EMAIL_ADDRESS>`       |
| `hash`    | Replace with hash                                | `john@email.com` → `hash_abc123`           |
| `encrypt` | Encrypt (reversible)                             | `john@email.com` → `[ENCRYPTED_DATA]`      |

### PII Anonymization Python API

```python
from llm2slm.privacy import PIIAnonymizer, AnonymizationConfig, AnonymizationMethod

# Configure anonymizer
config = AnonymizationConfig(
    enabled=True,
    method=AnonymizationMethod.MASK,
    entities={"EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON"},
    score_threshold=0.6,  # Confidence threshold
)

# Initialize anonymizer
anonymizer = PIIAnonymizer(config)

# Detect PII
text = "Contact John Smith at john@example.com or 555-123-4567"
pii_entities = anonymizer.detect_pii(text)
print(f"Found {len(pii_entities)} PII entities")

# Anonymize text
anonymized = anonymizer.anonymize(text)
print(anonymized)
# Output: "Contact **** ***** at ****************** or ************"

# Batch anonymization
texts = ["Email: john@example.com", "Phone: 555-123-4567"]
results = anonymizer.anonymize_batch(texts)
```

### PII Anonymization CLI

```bash
# Anonymize text
llm2slm anonymize "Contact john@example.com" --method mask

# Specify entities
llm2slm anonymize "Call me at 555-1234" --method redact --entities PHONE_NUMBER

# Save to file
llm2slm anonymize "PII text here" --method replace -o anonymized.txt
```

## Content Filtering

### Supported Categories

- **Toxicity**: General toxic content
- **Severe Toxicity**: Extremely toxic content
- **Obscene**: Obscene language
- **Threat**: Threatening language
- **Insult**: Insulting language
- **Identity Attack**: Attacks on identity/demographics
- **Sexual Explicit**: Sexually explicit content
- **Profanity**: Profane language
- **Hate Speech**: Hate speech

### Filter Actions

| Action   | Description                             |
| -------- | --------------------------------------- |
| `allow`  | Allow content to pass                   |
| `flag`   | Flag but allow (log violation)          |
| `redact` | Remove violating content                |
| `reject` | Reject entire text                      |

### Content Filtering Python API

```python
from llm2slm.privacy import ContentFilter, FilterConfig, ContentCategory, FilterAction

# Configure filter
config = FilterConfig(
    enabled=True,
    categories={
        ContentCategory.TOXICITY,
        ContentCategory.HATE_SPEECH,
        ContentCategory.THREAT,
    },
    thresholds={
        ContentCategory.TOXICITY: 0.7,
        ContentCategory.HATE_SPEECH: 0.6,
        ContentCategory.THREAT: 0.5,
    },
    action=FilterAction.FLAG,
)

# Initialize filter
content_filter = ContentFilter(config)

# Analyze content
text = "This is a friendly message."
scores = content_filter.analyze(text)
print(f"Toxicity score: {scores.get('toxicity', 0)}")

# Filter content
result = content_filter.filter(text)
if result.passed:
    print("Content passed filtering")
else:
    print(f"Violations: {result.violations}")
    print(f"Filtered text: {result.text}")

# Batch filtering
texts = ["Hello world", "Nice day", "Great work"]
results = content_filter.filter_batch(texts)
```

### CLI Usage

```bash
# Filter text
llm2slm filter "Your text here" --action flag

# Specify categories and threshold
llm2slm filter "Check this" --categories toxicity hate_speech --threshold 0.6

# Redact violating content
llm2slm filter "Text to check" --action redact -o filtered.txt
```

## Privacy Validation

### Privacy Levels

| Level    | Description                                                        |
| -------- | ------------------------------------------------------------------ |
| `none`   | No privacy checks                                                  |
| `low`    | Basic PII detection only                                           |
| `medium` | PII detection + content filtering                                  |
| `high`   | Comprehensive privacy + audit logging                              |
| `strict` | Maximum privacy enforcement (fails if any PII or violations found) |

### Python API

```python
from llm2slm.privacy import (
    PrivacyValidator,
    PrivacyLevel,
    PIIAnonymizer,
    ContentFilter,
    AnonymizationConfig,
    FilterConfig,
)

# Initialize components
anonymizer = PIIAnonymizer(AnonymizationConfig(enabled=True))
content_filter = ContentFilter(FilterConfig(enabled=True))

# Create validator
validator = PrivacyValidator(level=PrivacyLevel.HIGH)

# Validate text
text = "Contact john@example.com for details"
result = validator.validate(text, anonymizer, content_filter)

print(f"Validation passed: {result.passed}")
print(f"PII detected: {result.pii_detected} ({result.pii_count} entities)")
print(f"Content violations: {len(result.content_violations)}")
print(f"Recommendations: {result.recommendations}")

# Get audit summary
summary = validator.get_audit_summary()
print(f"Total audit entries: {summary['total_entries']}")
```

## Pipeline Integration

Integrate privacy checks into your conversion pipeline:

```python
from llm2slm.core import Pipeline

# Configure pipeline with privacy
config = {
    "model": "gpt-4",
    "output": "./my-slm",
    "privacy": {
        "enabled": True,
        "anonymize_pii": True,
        "filter_content": True,
        "validate_privacy": True,
        "privacy_level": "high",
        "anonymization_method": "mask",
        "filter_action": "flag",
        "pii_entities": [
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "PERSON",
            "LOCATION",
        ],
        "content_categories": [
            "toxicity",
            "hate_speech",
            "threat",
        ],
    },
}

# Run pipeline with privacy steps
pipeline = Pipeline(
    config,
    steps=[
        "load_model",
        "anonymize_data",      # Anonymize PII
        "filter_content",      # Filter harmful content
        "validate_privacy",    # Validate compliance
        "process_model",
        "export_slm",
    ],
)

result = await pipeline.run()
```

## Configuration File

Create a `privacy_config.yaml`:

```yaml
privacy:
  enabled: true

  # PII Anonymization
  anonymize_pii: true
  anonymization_method: mask  # mask, redact, replace, hash, encrypt
  pii_entities:
    - EMAIL_ADDRESS
    - PHONE_NUMBER
    - CREDIT_CARD
    - US_SSN
    - PERSON
    - LOCATION
    - IP_ADDRESS

  # Content Filtering
  filter_content: true
  filter_action: flag  # allow, flag, redact, reject
  content_categories:
    - toxicity
    - severe_toxicity
    - hate_speech
    - threat
    - insult
  content_thresholds:
    toxicity: 0.7
    severe_toxicity: 0.5
    hate_speech: 0.6

  # Privacy Validation
  validate_privacy: true
  privacy_level: high  # none, low, medium, high, strict

  # Audit Logging
  audit_logging: true
  audit_log_file: ./logs/privacy_audit.log
```

## API Endpoints

The FastAPI server provides REST endpoints for all privacy operations.

### Start the Server

```bash
llm2slm serve --host 0.0.0.0 --port 8000
```

### Check Privacy Status

```bash
curl http://localhost:8000/privacy/status
```

Response:

```json
{
  "privacy_module_available": true,
  "presidio_available": true,
  "detoxify_available": true,
  "features": {
    "anonymization": true,
    "content_filtering": true,
    "privacy_validation": true,
    "fallback_available": true
  },
  "installation_command": "pip install llm2slm[privacy]"
}
```

### Anonymize PII Endpoint

**POST** `/anonymize`

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact John Smith at john@example.com or call 555-123-4567",
    "method": "mask",
    "entities": ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON"],
    "score_threshold": 0.6
  }'
```

Response:

```json
{
  "original_text": "Contact John Smith at john@example.com or call 555-123-4567",
  "anonymized_text": "Contact **** ***** at ****************** or call ************",
  "pii_detected": 3,
  "entities_found": ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON"],
  "method_used": "mask"
}
```

**Parameters:**

- `text` (required): Text to anonymize
- `method` (optional): Anonymization method - `mask`, `redact`, `replace`, `hash`, `encrypt` (default: `mask`)
- `entities` (optional): List of PII entities to detect (default: `["EMAIL_ADDRESS", "PHONE_NUMBER"]`)
- `score_threshold` (optional): Detection confidence threshold 0.0-1.0 (default: `0.6`)

### Filter Content Endpoint

**POST** `/filter`

```bash
curl -X POST http://localhost:8000/filter \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text to check here",
    "action": "flag",
    "categories": ["toxicity", "hate_speech", "threat"],
    "threshold": 0.7
  }'
```

Response:

```json
{
  "original_text": "Your text to check here",
  "filtered_text": "Your text to check here",
  "passed": true,
  "violations": [],
  "scores": {
    "toxicity": 0.12,
    "hate_speech": 0.05,
    "threat": 0.03
  },
  "action_taken": "allow"
}
```

**Parameters:**

- `text` (required): Text to filter
- `action` (optional): Filter action - `allow`, `flag`, `redact`, `reject` (default: `flag`)
- `categories` (optional): Content categories to check (default: `["toxicity", "severe_toxicity"]`)
- `threshold` (optional): Detection threshold 0.0-1.0 (default: `0.7`)

**Available Categories:**

- `toxicity` - General toxic content
- `severe_toxicity` - Extremely toxic content
- `obscene` - Obscene language
- `threat` - Threatening language
- `insult` - Insulting language
- `identity_attack` - Attacks on identity/demographics

### Validate Privacy Endpoint

**POST** `/validate`

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact me at john@example.com for sensitive information",
    "level": "high",
    "check_pii": true,
    "check_content": true
  }'
```

Response:

```json
{
  "passed": false,
  "level": "high",
  "pii_detected": true,
  "pii_count": 1,
  "content_violations": [],
  "recommendations": [
    "Detected 1 PII entities. Consider anonymizing before processing."
  ]
}
```

**Parameters:**

- `text` (required): Text to validate
- `level` (optional): Privacy level - `none`, `low`, `medium`, `high`, `strict` (default: `medium`)
- `check_pii` (optional): Check for PII (default: `true`)
- `check_content` (optional): Check content policy (default: `true`)

**Privacy Levels:**

- `none` - No privacy checks
- `low` - Basic PII detection only
- `medium` - PII detection + content filtering
- `high` - Comprehensive privacy + audit logging
- `strict` - Maximum privacy enforcement (fails if any violations)

## Compliance & Regulations

### GDPR Compliance

- **Article 17 (Right to Erasure)**: Anonymize PII before processing
- **Article 25 (Data Protection by Design)**: Enable privacy-by-default in pipeline
- **Article 32 (Security)**: Use encryption method for sensitive data

### HIPAA Compliance

- **Protected Health Information (PHI)**: Anonymize medical records, patient names, dates
- **Audit Controls**: Enable audit logging for all privacy operations
- **Access Controls**: Use strict privacy level for healthcare data

### CCPA/CPRA Compliance

- **Consumer Privacy Rights**: Implement data anonymization for California residents
- **Data Minimization**: Filter unnecessary PII before model training

## Best Practices

### 1. Choose Appropriate Privacy Level

```python
# Development/testing
privacy_level = PrivacyLevel.LOW

# Production (general)
privacy_level = PrivacyLevel.MEDIUM

# Regulated industries (healthcare, finance)
privacy_level = PrivacyLevel.HIGH

# Maximum security
privacy_level = PrivacyLevel.STRICT
```

### 2. Configure Entity-Specific Anonymization

```python
# Financial data
config = AnonymizationConfig(
    entities={"CREDIT_CARD", "US_SSN", "IBAN_CODE"},
    method=AnonymizationMethod.HASH,
)

# Healthcare data
config = AnonymizationConfig(
    entities={"PERSON", "MEDICAL_LICENSE", "DATE_TIME"},
    method=AnonymizationMethod.ENCRYPT,
)

# Communication data
config = AnonymizationConfig(
    entities={"EMAIL_ADDRESS", "PHONE_NUMBER", "IP_ADDRESS"},
    method=AnonymizationMethod.MASK,
)
```

### 3. Enable Audit Logging

```python
from pathlib import Path
from llm2slm.privacy import AuditLog, PrivacyValidator, PrivacyLevel

# Create audit log
audit_log = AuditLog(log_file=Path("./logs/privacy_audit.log"))

# Use with validator
validator = PrivacyValidator(level=PrivacyLevel.HIGH, audit_log=audit_log)

# Review audit summary
summary = validator.get_audit_summary()
print(f"Privacy operations logged: {summary['total_entries']}")
```

### 4. Handle Privacy Failures Gracefully

```python
try:
    result = validator.validate(text, anonymizer, content_filter)

    if not result.passed:
        # Log recommendations
        for rec in result.recommendations:
            logger.warning(f"Privacy recommendation: {rec}")

        # Take appropriate action
        if result.pii_detected:
            text = anonymizer.anonymize(text)

        if result.content_violations:
            text = content_filter.filter(text).text

except Exception as e:
    logger.error(f"Privacy validation failed: {e}")
    # Fallback to safe defaults
```

## Troubleshooting

### Import Errors

```python
# Check if privacy modules are available
from llm2slm.privacy import presidio_available, detoxify_available

if not presidio_available():
    print("Install Presidio: pip install presidio-analyzer presidio-anonymizer")

if not detoxify_available():
    print("Install Detoxify: pip install detoxify")
```

### Performance Optimization

```python
# For large batches, use batch operations
texts = ["text1", "text2", ..., "text1000"]

# More efficient than looping
results = anonymizer.anonymize_batch(texts)
results = content_filter.filter_batch(texts)
results = validator.validate_batch(texts, anonymizer, content_filter)
```

### Model Download Issues

Detoxify will download models on first use. Ensure internet connectivity or pre-download:

```bash
python -c "from detoxify import Detoxify; Detoxify('original')"
```

## Security Considerations

1. **Encryption Keys**: For `AnonymizationMethod.ENCRYPT`, use strong, unique keys
2. **Audit Logs**: Protect audit logs with appropriate file permissions
3. **Threshold Tuning**: Balance false positives/negatives based on your use case
4. **Regular Updates**: Keep privacy dependencies updated for security patches

## Additional Resources

- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/)
- [Detoxify GitHub](https://github.com/unitaryai/detoxify)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/)

## Support

For privacy-related issues or questions:

- GitHub Issues: [llm2slm-oss/issues](https://github.com/Kolerr-Lab/llm2slm-oss/issues)
- Email: <privacy@kolerr.com>
- Documentation: [Full Privacy Guide](https://github.com/Kolerr-Lab/llm2slm-oss/blob/main/PRIVACY.md)
