# Contributing to llm2slm

Thank you for your interest in contributing to **llm2slm**, a Python project for converting Large Language Models (LLMs) to Small Language Models (SLMs). This document provides guidelines for contributors to ensure high-quality, maintainable code that aligns with production deployment standards.

## Table of Contents

- [Contributing to llm2slm](#contributing-to-llm2slm)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
    - [Project Structure](#project-structure)
  - [Development Guidelines](#development-guidelines)
    - [Key Components](#key-components)
  - [Testing](#testing)
  - [Deployment](#deployment)
    - [Local Deployment](#local-deployment)
    - [Production Deployment](#production-deployment)
    - [Deployment Checklist](#deployment-checklist)
  - [Contributing Process](#contributing-process)
  - [Contact \& Support](#contact--support)
  - [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (for containerized development and deployment)
- A code editor (e.g., VS Code with recommended extensions)

### Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:
    ```bash
    git clone https://github.com/Kolerr-Lab/llm2slm-oss.git
    cd llm2slm
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt  # For development tools
    ```
5. Install pre-commit hooks for code quality:
    ```bash
    pre-commit install
    ```

### Project Structure

- `src/llm2slm/`: Main package code
- `tests/`: Test files
- `docker/`: Docker configurations
- `.github/workflows/`: CI/CD pipelines
- `.vscode/`: VS Code settings

## Development Guidelines

- **Python Version**: Use Python 3.8+ with modern async/await patterns.
- **Style**: Follow PEP 8. Use tools like `black` for formatting and `flake8` for linting.
- **Type Hints**: Include type hints for all function signatures.
- **Docstrings**: Write comprehensive docstrings for all modules, classes, and functions using Google-style formatting.
- **Error Handling**: Implement robust error handling and logging using the `logging` module.
- **Versioning**: Follow semantic versioning (e.g., MAJOR.MINOR.PATCH).
- **Commits**: Use clear, descriptive commit messages. Follow conventional commits (e.g., `feat: add new provider integration`).

### Key Components

- **CLI**: Command-line interface for model operations.
- **Core**: Configuration and pipeline management.
- **Providers**: Integrations with LLM providers (e.g., OpenAI, Anthropic, Google, LiquidAI).
- **Server**: FastAPI-based REST API.
- **SLM**: Small Language Model export and runtime.

Prioritize code quality, documentation, and maintainability. Run `pre-commit run --all-files` before committing to ensure compliance.

### Adding New Providers

To add support for a new LLM provider:

1. **Create Provider Implementation**: Add a new file in `src/llm2slm/providers/` (e.g., `newprovider.py`)
2. **Implement Required Methods**: Subclass `BaseProvider` and implement `generate_response()` and `convert_to_slm()`
3. **Add Simple Methods**: Include `generate(prompt: str) -> str` and `embed(text: str) -> list[float]` methods
4. **API Key Handling**: Load API keys from environment variables (e.g., `NEWPROVIDER_API_KEY`)
5. **Update Exports**: Add to `src/llm2slm/providers/__init__.py` and `get_available_providers()`
6. **Configuration**: Add API key to `core/config.py` and `.env.example`
7. **CLI Integration**: Update CLI help and validation for the new provider
8. **Tests**: Add comprehensive unit tests with mocking in `tests/test_providers.py`
9. **Documentation**: Update README.md, demo.ipynb, and this file

Example providers: OpenAI, Anthropic, Google Gemini, LiquidAI.

## Testing

- Use `pytest` for unit and integration tests.
- Aim for high test coverage (target: 90%+). Run `pytest --cov=src/llm2slm` to check coverage.
- Write tests for new features and bug fixes.
- Include edge cases and error scenarios.
- Run tests locally before submitting a PR:
  ```bash
  pytest
  ```

## Deployment

### Local Deployment

1. Build the Docker image:
    ```bash
    docker build -t llm2slm .
    ```
2. Run the container:
    ```bash
    docker run -p 8000:8000 llm2slm
    ```
3. Access the API at `http://localhost:8000`.

### Production Deployment

For production, use the provided Docker Compose setup or deploy to a cloud platform (e.g., AWS, GCP, Azure).

1. Ensure environment variables are set (e.g., API keys for providers).
2. Use the CI/CD pipeline in `.github/workflows/` for automated builds and deployments.
3. Monitor logs and performance using integrated logging.
4. Follow security best practices: no hardcoded secrets, use environment variables, and enable HTTPS.

### Deployment Checklist

- [ ] All tests pass with 90%+ coverage.
- [ ] Code is linted and formatted.
- [ ] Documentation is updated.
- [ ] No security vulnerabilities (run `safety check`).
- [ ] Environment variables are configured.
- [ ] Docker image builds successfully.
- [ ] API endpoints are tested in staging.

## Contributing Process

1. Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
2. Make changes, ensuring they follow the guidelines above.
3. Run tests and pre-commit checks.
4. Submit a pull request (PR) with a clear description.
5. Address review feedback and ensure CI passes.
6. Once approved, your PR will be merged.

For bugs, create an issue first and reference it in your PR.

## Contact & Support

- **Primary Author**: Ricky Kolerr <ricky@kolerr.com>
- **Community Support**: Kolerr Lab <lab.kolerr@kolerr.com>
- **Repository**: [https://github.com/Kolerr-Lab/llm2slm-oss](https://github.com/Kolerr-Lab/llm2slm-oss)
- **Issues**: [GitHub Issues](https://github.com/Kolerr-Lab/llm2slm-oss/issues)

## Code of Conduct

We follow a code of conduct to ensure a welcoming environment. Be respectful, inclusive, and collaborative. Harassment or discriminatory behavior will not be tolerated.

For questions, reach out via GitHub issues or discussions.

Thank you for contributing to llm2slm!
