# GitHub Repository Setup Guide

This document outlines the required GitHub repository configuration for the CI/CD pipeline to work properly.

## Required GitHub Secrets

Navigate to **Settings** → **Secrets and variables** → **Actions** in your GitHub repository and add the following secrets:

### 1. PyPI Publishing

- **`PYPI_API_TOKEN`**: Your PyPI API token for publishing packages
  - Get this from [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
  - Required for: Release workflow (publishing to PyPI)

### 2. Docker Hub Publishing

- **`DOCKER_USERNAME`**: Your Docker Hub username
  - Required for: Release workflow (pushing Docker images)

- **`DOCKER_PASSWORD`**: Your Docker Hub password or access token
  - Get an access token from [https://hub.docker.com/settings/security](https://hub.docker.com/settings/security)
  - Required for: Release workflow (pushing Docker images)

## Required GitHub Environments

Navigate to **Settings** → **Environments** in your GitHub repository and create the following environments:

### 1. Release Environment

- **Name**: `release`
- **Protection rules** (recommended):
  - Required reviewers: Add 1-2 reviewers for production releases
  - Deployment branches: Only `main` or tags matching `v*`
- **Purpose**: Controls access to PyPI and Docker Hub publishing

### 2. GitHub Pages Environment

- **Name**: `github-pages`
- **Note**: This environment is automatically created when you enable GitHub Pages
- **Setup Steps**:
  1. Go to **Settings** → **Pages**
  2. Under "Build and deployment":
     - Source: **GitHub Actions**
  3. The `github-pages` environment will be created automatically

## Verification

After configuring the secrets and environments:

1. The YAML validation warnings in `.github/workflows/ci.yml` will disappear
2. Push a tag to test the release workflow:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. Check the Actions tab to see the CI/CD pipeline run successfully

## Optional: Branch Protection

For production repositories, consider adding branch protection rules:

1. Navigate to **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required status checks: `quality`, `test`, `integration`, `security`

## Troubleshooting

### "Secret not found" errors

- Verify the secret name matches exactly (case-sensitive)
- Check that secrets are added at the repository level (not organization level)

### "Environment not found" errors

- Ensure environments are created in repository settings
- Check environment names match exactly: `release` and `github-pages`

### "Unauthorized" Docker push errors

- Verify `DOCKER_USERNAME` matches your Docker Hub username
- Ensure `DOCKER_PASSWORD` is a valid access token (not your account password)
- Access tokens are more secure and recommended over passwords

## Security Notes

- Never commit secrets to the repository
- Use GitHub's secret management - secrets are encrypted and masked in logs
- Rotate secrets regularly (every 90 days recommended)
- Use access tokens instead of passwords where possible
- Limit environment access to specific branches/tags

## References

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [PyPI API Tokens](https://pypi.org/help/#apitoken)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
