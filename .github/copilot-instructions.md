<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project: llm2slm - Large Language Model to Small Language Model Converter

This is a Python project for converting Large Language Models (LLMs) to Small Language Models (SLMs). The project includes:

- CLI interface for model conversion
- Server components for API access
- Provider integrations (OpenAI, etc.)
- Docker containerization support
- GitHub CI/CD workflows
- Comprehensive testing setup

### Development Guidelines

- Use Python 3.8+ with modern async/await patterns
- Follow PEP 8 style guidelines
- Include type hints for all function signatures
- Write comprehensive docstrings for all modules, classes, and functions
- Use pytest for testing with high coverage requirements
- Implement proper error handling and logging
- Follow semantic versioning for releases

### Project Structure

The project follows a standard Python package structure with:
- `src/llm2slm/` - Main package code
- `tests/` - Test files
- `docker/` - Docker configuration
- `.github/workflows/` - CI/CD pipeline
- `.vscode/` - VS Code configuration

### Key Components

- **CLI**: Command-line interface for model operations
- **Core**: Configuration and pipeline management
- **Providers**: Integration with different LLM providers
- **Server**: FastAPI-based REST API
- **SLM**: Small Language Model export and runtime

When working on this project, prioritize code quality, documentation, and maintainability.