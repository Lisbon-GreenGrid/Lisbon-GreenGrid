# NCDC Tree Inventory - CI/CD Setup Guide

## Overview

This project uses GitHub Actions for automated testing, code quality checks, and deployment.

## GitHub Actions Workflows

### 1. Testing & Code Quality (`tests.yml`)

Runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
1. **Python Tests** - API & ETL code quality
   - Flake8 linting
   - Bandit security analysis
   - PostgreSQL service for integration tests

2. **Docker Build** - Container image build
   - Builds Docker image
   - Uses GitHub Actions cache

3. **Frontend Checks** - Web application validation
   - Node.js dependencies check
   - npm audit for security

### 2. Environment Secrets

Configure in **Settings → Secrets and variables → Actions**:

#### For Staging:
```
STAGING_HOST        # Staging server hostname
STAGING_USER        # SSH user
STAGING_DEPLOY_KEY  # SSH private key
```

#### For Production:
```
PROD_HOST           # Production server hostname
PROD_USER           # SSH user
PROD_DEPLOY_KEY     # SSH private key
```

## Setup Instructions

### Step 1: Generate SSH Keys

```bash
ssh-keygen -t ed25519 -f deploy_key -N ""
cat deploy_key.pub >> ~/.ssh/authorized_keys
# Add deploy_key to GitHub secrets
```

### Step 2: Create GitHub Environments

1. Go to **Settings → Environments**
2. Create `staging` and `production` environments
3. Set required reviewers for production

### Step 3: Enable Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Deployment Pipeline

1. **Development** → Feature branch with tests
2. **Staging** → Auto-deploy on main push
3. **Production** → Auto-deploy on version tags

## Common Issues

### Deployment Fails
- Check SSH key access: `ssh -i key user@host`
- Verify Docker daemon on target
- Check Actions logs for details

### Tests Failing Locally
- Match Python version (3.11)
- Run tests in Docker: `docker-compose run api pytest`

### Pre-commit Hooks Failing
```bash
# Auto-fix issues
black api/ greengrid_etl/
isort api/ greengrid_etl/
```

---

**Last Updated**: 2026-06-20
