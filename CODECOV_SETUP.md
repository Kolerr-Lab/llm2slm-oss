# Codecov Integration Guide

This document explains how to set up and use Codecov for comprehensive code coverage tracking in the LLM2SLM project.

## Overview

Codecov is integrated into our CI/CD pipeline to track code coverage across all tests, generate detailed reports, and enforce coverage standards.

## Setup Instructions

### 1. Get Codecov Token

1. Go to [Codecov.io](https://codecov.io/)
2. Sign in with your GitHub account
3. Add the `Kolerr-Lab/llm2slm-oss` repository
4. Copy the repository upload token

### 2. Configure GitHub Secrets

Add the Codecov token to your GitHub repository secrets:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CODECOV_TOKEN`
5. Value: Paste your Codecov upload token
6. Click **Add secret**

### 3. Verify Codecov Configuration

The project includes a `codecov.yml` file with the following settings:

- **Coverage Target**: 80% for new code (patch coverage)
- **Project Coverage**: Auto-calculated with 1% threshold
- **Ignore Paths**: Tests, docs, build artifacts
- **PR Comments**: Enabled with detailed coverage diff
- **Flags**: Separate tracking for unit tests, integration tests, and privacy module

## Features

### Coverage Reporting

The CI/CD pipeline generates multiple coverage report formats:

- **XML**: For Codecov upload
- **HTML**: Interactive browsable coverage report
- **JSON**: Machine-readable coverage data
- **Terminal**: In-line coverage summary

### Coverage Badges

Add coverage badges to your README:

```markdown
[![codecov](https://codecov.io/gh/Kolerr-Lab/llm2slm-oss/branch/master/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/Kolerr-Lab/llm2slm-oss)
```

Replace `YOUR_TOKEN` with your actual Codecov badge token.

### PR Comments

Codecov automatically comments on pull requests with:

- Coverage change summary
- List of files with changed coverage
- Detailed diff of coverage changes
- Links to full coverage reports

### Coverage Flags

The project uses flags to track coverage by test type:

- **unit-tests**: Core unit test coverage
- **integration**: Integration test coverage
- **privacy**: Privacy module specific coverage

## Local Testing

### Run Tests with Coverage

```bash
# Basic coverage
pytest tests/ --cov=src/llm2slm --cov-report=term-missing

# Comprehensive coverage with all formats
pytest tests/ \
  --cov=src/llm2slm \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-branch \
  -v

# Open HTML coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Generate Coverage Badge Locally

```bash
pip install coverage-badge
coverage-badge -o coverage.svg -f
```

### Check Coverage Threshold

```bash
# Fail if coverage is below 60%
pytest tests/ --cov=src/llm2slm --cov-fail-under=60
```

## Coverage Configuration

### pyproject.toml Settings

```toml
[tool.coverage.run]
source = ["src/llm2slm"]
branch = true
parallel = true

[tool.coverage.report]
fail_under = 60
show_missing = true
precision = 2
skip_empty = true
```

### Excluding Code from Coverage

Use `# pragma: no cover` to exclude specific code:

```python
if __name__ == "__main__":  # pragma: no cover
    main()

def debug_only():  # pragma: no cover
    """This function is only for debugging."""
    pass
```

## CI/CD Integration

### Workflow Jobs

1. **quality**: Code quality checks (linting, formatting, type checking)
2. **test**: Matrix testing across Python versions and OS platforms
3. **coverage**: Dedicated comprehensive coverage analysis
4. **integration**: Integration tests with services
5. **docker**: Docker build and security scanning

### Coverage Job

The dedicated coverage job:

- Runs after all tests complete
- Generates comprehensive coverage reports
- Uploads to Codecov with verbose logging
- Creates coverage artifacts
- Posts coverage summary to PR

### Matrix Testing

Coverage is collected from:

- Python 3.8, 3.9, 3.10, 3.11, 3.12
- Ubuntu, Windows, macOS
- Main coverage upload from Python 3.11 on Ubuntu

## Codecov Dashboard

### Accessing Reports

1. Visit [codecov.io/gh/Kolerr-Lab/llm2slm-oss](https://codecov.io/gh/Kolerr-Lab/llm2slm-oss)
2. View overall project coverage
3. Browse file-by-file coverage
4. Analyze coverage trends over time
5. Compare coverage between branches

### Key Metrics

- **Line Coverage**: Percentage of executed lines
- **Branch Coverage**: Percentage of executed code branches
- **Complexity**: Code complexity metrics
- **Diff Coverage**: Coverage of changed code in PRs

### Coverage Trends

The Codecov dashboard shows:

- Coverage over time (graph)
- Per-commit coverage changes
- Per-PR coverage impact
- Coverage by component/module

## Best Practices

### Writing Testable Code

1. **Keep functions small** - Easier to test and cover
2. **Separate concerns** - Pure logic vs I/O operations
3. **Use dependency injection** - Makes mocking easier
4. **Avoid side effects** - Makes tests more reliable

### Improving Coverage

1. **Identify gaps**: Use coverage reports to find untested code
2. **Write focused tests**: Target specific branches and conditions
3. **Test edge cases**: Boundary conditions, errors, exceptions
4. **Use parametrize**: Test multiple inputs efficiently

Example:

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### Coverage Goals

- **Minimum**: 60% (enforced by CI/CD)
- **Target**: 80% (recommended for production)
- **Stretch**: 90%+ (excellent coverage)
- **New code**: 80% minimum (enforced by Codecov)

## Troubleshooting

### Coverage Not Uploading

1. Check `CODECOV_TOKEN` is set in GitHub secrets
2. Verify network access in CI/CD runner
3. Check Codecov action logs for errors
4. Ensure `coverage.xml` file is generated

### Low Coverage Warnings

1. Run coverage locally to identify gaps
2. Check excluded files in `codecov.yml`
3. Verify test discovery is working
4. Review coverage report for missing files

### PR Comments Not Appearing

1. Ensure Codecov GitHub App is installed
2. Check repository permissions
3. Verify PR comments are enabled in `codecov.yml`
4. Check Codecov dashboard for processing errors

## Advanced Features

### Coverage Comparison

Compare coverage between branches:

```bash
# Generate coverage for current branch
pytest --cov=src/llm2slm --cov-report=json

# Compare with main branch
git checkout main
pytest --cov=src/llm2slm --cov-report=json:coverage-main.json
# Use coverage diff tools to compare
```

### Parallel Coverage

For faster testing with parallel execution:

```bash
pytest tests/ -n auto --cov=src/llm2slm --cov-report=xml
```

### Coverage by Test Type

Use markers to track coverage by test type:

```bash
# Only unit tests
pytest tests/ -m unit --cov=src/llm2slm

# Only integration tests
pytest tests/ -m integration --cov=src/llm2slm

# Only privacy tests
pytest tests/test_privacy.py --cov=src/llm2slm/privacy
```

## Resources

- **Codecov Documentation**: https://docs.codecov.com/
- **pytest-cov Documentation**: https://pytest-cov.readthedocs.io/
- **Coverage.py Documentation**: https://coverage.readthedocs.io/
- **GitHub Actions Codecov Action**: https://github.com/codecov/codecov-action

## Support

For issues with Codecov integration:

1. Check this guide
2. Review CI/CD logs
3. Consult Codecov documentation
4. Open an issue in the repository
5. Contact the maintainers

---

**Last Updated**: October 1, 2025
**Maintained By**: LLM2SLM Team
