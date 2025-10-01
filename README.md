# llm2slm

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.txt)
[![CI/CD](https://github.com/Kolerr-Lab/llm2slm-oss/actions/workflows/ci.yml/badge.svg)](https://github.com/Kolerr-Lab/llm2slm-oss/actions)
[![PyPI version](https://badge.fury.io/py/llm2slm.svg)](https://pypi.org/project/llm2slm/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Quality Gate](https://img.shields.io/badge/quality-A+-brightgreen.svg)](https://github.com/Kolerr-Lab/llm2slm-oss)

A robust Python library and CLI tool for converting Large Language Models (LLMs) to optimized Small Language Models (SLMs). Streamline model deployment with provider integrations, containerization, and API access.

## Features

- **CLI Interface**: Command-line tools for seamless model conversion and management.
- **Provider Integrations**: Support for OpenAI, Anthropic, Google Gemini, and LiquidAI providers.
- **Privacy & Security**: PII detection, anonymization, content filtering, and compliance validation.
- **Server API**: FastAPI-based REST API for remote model operations.
- **Docker Support**: Containerized deployment for easy scaling.
- **CI/CD Pipelines**: Automated testing and deployment via GitHub Actions.
- **Comprehensive Testing**: High-coverage pytest suite with type hints and docstrings.
- **Error Handling & Logging**: Robust logging and exception management.
- **Semantic Versioning**: Predictable release cycles.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install from PyPI

```bash
pip install llm2slm
```

### Install from Source

```bash
git clone https://github.com/Kolerr-Lab/llm2slm-oss.git
cd llm2slm
pip install -e .
```

### Install with Privacy Features

```bash
pip install llm2slm[privacy]
```

Includes PII detection (Presidio), content filtering (Detoxify), and compliance tools.

### Docker Installation

```bash
docker build -t llm2slm .
docker run -p 8000:8000 llm2slm
```

## Usage

### CLI

Show version:

```bash
llm2slm version
```

List available providers:

```bash
llm2slm providers
```

Validate setup:

```bash
llm2slm validate
```

Convert an LLM to SLM:

```bash
# Using OpenAI (default)
llm2slm convert openai/gpt-4 ./my-slm --provider openai --compression-factor 0.5

# Using Anthropic Claude
llm2slm convert claude-3-opus-20240229 ./my-slm --provider anthropic --compression-factor 0.5

# Using Google Gemini
llm2slm convert gemini-pro ./my-slm --provider google --compression-factor 0.5

# Using LiquidAI
llm2slm convert liquid-1.0 ./my-slm --provider liquid --compression-factor 0.5
```

### API Server

Start the server:

```bash
llm2slm serve --host 0.0.0.0 --port 8000
```

Example API request:

```bash
curl -X POST "http://localhost:8000/convert" \
    -H "Content-Type: application/json" \
    -d '{"model": "openai/gpt-4", "output": "my-slm"}'
```

### Python Library

```python
from llm2slm import convert_model

# Convert a model using OpenAI
result = await convert_model(
    input_model="openai/gpt-4",
    output_path="./my-slm",
    provider="openai",
    compression_factor=0.5
)

# Convert using Anthropic
result = await convert_model(
    input_model="claude-3-opus-20240229",
    output_path="./my-slm",
    provider="anthropic",
    compression_factor=0.5
)

# Convert using Google Gemini
result = await convert_model(
    input_model="gemini-pro",
    output_path="./my-slm",
    provider="google",
    compression_factor=0.5
)
```

## Configuration

Configure providers via environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_API_KEY`: Your Google API key
- `LIQUID_API_KEY`: Your LiquidAI API key

Or use the CLI config commands:

```bash
llm2slm config --set OPENAI_API_KEY your-openai-key-here
llm2slm config --set ANTHROPIC_API_KEY your-anthropic-key-here
llm2slm config --set GOOGLE_API_KEY your-google-key-here
llm2slm config --set LIQUID_API_KEY your-liquid-key-here
```

## Privacy & Security

LLM2SLM includes comprehensive privacy features for enterprise and regulated environments:

### PII Anonymization

```bash
# Detect and anonymize PII
llm2slm anonymize "Contact john@example.com" --method mask

# Supported: EMAIL, PHONE, SSN, CREDIT_CARD, PERSON, LOCATION, IP_ADDRESS
```

### Content Filtering

```bash
# Filter harmful content
llm2slm filter "Your text here" --action flag --categories toxicity hate_speech
```

### Privacy Validation

```python
from llm2slm.privacy import PrivacyValidator, PrivacyLevel, PIIAnonymizer, ContentFilter

# Validate text for compliance
validator = PrivacyValidator(level=PrivacyLevel.HIGH)
result = validator.validate(text, anonymizer, content_filter)

print(f"Passed: {result.passed}")
print(f"PII detected: {result.pii_detected}")
print(f"Violations: {result.content_violations}")
```

For comprehensive privacy documentation, see [PRIVACY.md](PRIVACY.md).

## Development

### Setup

```bash
pip install -r requirements-dev.txt
pre-commit install
```

### Testing

```bash
pytest --cov=llm2slm
```

### Building

```bash
python -m build
```

## Project Structure

```plaintext
src/llm2slm/
├── __init__.py          # Package initialization and version info
├── cli.py               # Command-line interface
├── core/                # Core functionality
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   └── pipeline.py      # Conversion pipeline
├── providers/           # LLM provider integrations
│   ├── __init__.py
│   ├── base.py          # Base provider interface
│   └── openai.py        # OpenAI provider implementation
├── server/              # FastAPI server
│   ├── __init__.py
│   └── app.py           # FastAPI application
└── slm/                 # Small Language Model components
    ├── __init__.py
    ├── benchmark.py     # Performance benchmarking
    ├── export.py        # Model export functionality
    ├── loaders.py       # Model loading with factory pattern
    ├── metadata.py      # Metadata creation
    ├── model.py         # SLM model representation
    └── runtime.py       # SLM runtime management
```

## Contact & Support

- **Primary Author**: Ricky Kolerr <ricky@kolerr.com>
- **Community Support**: Kolerr Lab <lab.kolerr@kolerr.com>
- **Repository**: [https://github.com/Kolerr-Lab/llm2slm-oss](https://github.com/Kolerr-Lab/llm2slm-oss)
- **Issues**: [GitHub Issues](https://github.com/Kolerr-Lab/llm2slm-oss/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Kolerr-Lab/llm2slm-oss/discussions)

## GitHub Repository Setup

If you're forking or deploying this repository, you'll need to configure GitHub secrets and environments for the CI/CD pipeline. See [GITHUB_SETUP.md](GITHUB_SETUP.md) for detailed instructions.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository.
2. Create a feature branch.
3. Add tests and ensure coverage.
4. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
