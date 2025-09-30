# ────────────────────────────────────────────────────────────────────────────────
# LLM2SLM Makefile - Development and Deployment Commands
# ────────────────────────────────────────────────────────────────────────────────

.PHONY: help install install-dev test test-cov lint format clean build docker run serve docs pre-commit release

# Default target
help: ## Show this help message
	@echo "LLM2SLM - Large Language Model to Small Language Model Converter"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ────────────────────────────────────────────────────────────────────────────────
# Installation and Setup
# ────────────────────────────────────────────────────────────────────────────────

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev,server,all]"
	pre-commit install

setup: install-dev ## Complete development setup
	mkdir -p output cache data logs
	cp .env.example .env
	@echo "✓ Development environment setup complete!"
	@echo "  - Edit .env file with your API keys"
	@echo "  - Run 'make test' to verify installation"

# ────────────────────────────────────────────────────────────────────────────────
# Testing and Quality Assurance
# ────────────────────────────────────────────────────────────────────────────────

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=src/llm2slm --cov-report=html --cov-report=term-missing -v

test-integration: ## Run integration tests
	pytest tests/ -m integration -v

test-all: ## Run all tests including slow ones
	pytest tests/ -v --runslow

# ────────────────────────────────────────────────────────────────────────────────
# Code Quality and Formatting
# ────────────────────────────────────────────────────────────────────────────────

lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/
	bandit -r src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/
	isort --check-only src/ tests/

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

quality: format lint test ## Run all quality checks

# ────────────────────────────────────────────────────────────────────────────────
# Development and Running
# ────────────────────────────────────────────────────────────────────────────────

run: ## Run the CLI (requires arguments)
	python -m llm2slm $(ARGS)

serve: ## Start the development server
	uvicorn llm2slm.server.app:create_app --reload --host 0.0.0.0 --port 8000

serve-prod: ## Start the production server
	gunicorn llm2slm.server.app:create_app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# ────────────────────────────────────────────────────────────────────────────────
# Docker Commands
# ────────────────────────────────────────────────────────────────────────────────

docker-build: ## Build Docker image
	docker build -t llm2slm:latest .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env llm2slm:latest

docker-dev: ## Run development Docker setup
	docker-compose --profile dev up --build

docker-prod: ## Run production Docker setup
	docker-compose up -d --build

docker-stop: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

# ────────────────────────────────────────────────────────────────────────────────
# Building and Distribution
# ────────────────────────────────────────────────────────────────────────────────

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	python -m build

upload-test: build ## Upload to test PyPI
	python -m twine upload --repository testpypi dist/*

upload: build ## Upload to PyPI
	python -m twine upload dist/*

# ────────────────────────────────────────────────────────────────────────────────
# Documentation
# ────────────────────────────────────────────────────────────────────────────────

docs: ## Generate documentation
	@echo "Documentation generation not yet implemented"
	@echo "Will use Sphinx or similar tool"

docs-serve: ## Serve documentation locally
	@echo "Documentation serving not yet implemented"

# ────────────────────────────────────────────────────────────────────────────────
# Database and Migrations (if needed in future)
# ────────────────────────────────────────────────────────────────────────────────

db-init: ## Initialize database
	@echo "Database initialization not yet implemented"

db-migrate: ## Run database migrations
	@echo "Database migrations not yet implemented"

# ────────────────────────────────────────────────────────────────────────────────
# Utility Commands
# ────────────────────────────────────────────────────────────────────────────────

check-deps: ## Check for dependency vulnerabilities
	pip-audit

update-deps: ## Update dependencies
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

security: ## Run security checks
	bandit -r src/
	safety check

benchmark: ## Run performance benchmarks
	python -m pytest benchmarks/ -v

profile: ## Profile the application
	python -m cProfile -o profile.stats -m llm2slm $(ARGS)

# ────────────────────────────────────────────────────────────────────────────────
# Release Management
# ────────────────────────────────────────────────────────────────────────────────

version: ## Show current version
	python -c "import llm2slm; print(llm2slm.__version__)"

tag: ## Create git tag for current version
	git tag v$(shell python -c "import llm2slm; print(llm2slm.__version__)")
	git push origin v$(shell python -c "import llm2slm; print(llm2slm.__version__)")

release: quality build ## Create a release
	@echo "Creating release..."
	@echo "1. Run tests and quality checks"
	@echo "2. Build distribution packages"
	@echo "3. Ready for upload to PyPI"
	@echo ""
	@echo "Next steps:"
	@echo "  - Review the built packages in dist/"
	@echo "  - Run 'make upload-test' to test on test PyPI"
	@echo "  - Run 'make upload' to upload to PyPI"
	@echo "  - Run 'make tag' to create git tag"

# ────────────────────────────────────────────────────────────────────────────────
# Examples and Demos
# ────────────────────────────────────────────────────────────────────────────────

demo-convert: ## Demo: Convert a model
	python -m llm2slm convert gpt-3.5-turbo --provider openai --compression 0.6

demo-server: ## Demo: Start server and show endpoints
	@echo "Starting server..."
	@echo "Available endpoints:"
	@echo "  - http://localhost:8000/docs (API documentation)"
	@echo "  - http://localhost:8000/health (health check)"
	@echo "  - http://localhost:8000/providers (list providers)"
	@$(MAKE) serve

demo-list: ## Demo: List available models
	python -m llm2slm list --provider openai

# ────────────────────────────────────────────────────────────────────────────────
# CI/CD Support
# ────────────────────────────────────────────────────────────────────────────────

ci-install: ## Install dependencies for CI
	pip install -e ".[dev,all]"

ci-test: ## Run CI tests
	pytest tests/ --cov=src/llm2slm --cov-report=xml -v

ci-quality: ## Run CI quality checks
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/
	bandit -r src/

ci-build: ## Build for CI
	python -m build --wheel

# ────────────────────────────────────────────────────────────────────────────────
# Environment Information
# ────────────────────────────────────────────────────────────────────────────────

info: ## Show environment information
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "LLM2SLM version: $(shell python -c 'import llm2slm; print(llm2slm.__version__)' 2>/dev/null || echo 'Not installed')"
	@echo "Current directory: $(shell pwd)"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Git commit: $(shell git rev-parse --short HEAD 2>/dev/null || echo 'Not a git repo')"