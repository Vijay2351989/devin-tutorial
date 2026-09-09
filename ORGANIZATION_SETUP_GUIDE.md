# Organization Blueprint and Secret Setup Guide

This guide provides step-by-step instructions for setting up organization blueprints and secrets in Devin Cloud for this FastAPI example project.

## Overview

This project demonstrates how to:
1. Use organization-level secrets instead of storing them in the repository
2. Reference organization secrets in your application
3. Create organization blueprints for reusable environment configurations
4. Deploy applications that automatically receive secrets from the organization

## Prerequisites

- Devin CLI installed and authenticated
- Organization admin access (for creating blueprints and secrets)
- This repository cloned and pushed to your git remote

## Step 1: Create Organization Secrets

### Method 1: Upload from Environment Variable (Recommended)

```bash
# Set your secret in a local environment variable
export MY_API_KEY="sk-your-actual-api-key-here"

# Upload to organization (value never enters chat or command line)
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key API_KEY --from-env MY_API_KEY
```

### Method 2: Upload from File

```bash
# Create a temporary file with your secret (not in git)
echo "sk-your-actual-api-key-here" > /tmp/api_key.txt

# Upload from file
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key API_KEY --from-file /tmp/api_key.txt

# Clean up
rm /tmp/api_key.txt
```

### Method 3: Upload via Stdin (Interactive)

```bash
# Upload via interactive prompt (value not echoed)
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key API_KEY --from-stdin
# Enter your API key when prompted
```

### Upload Additional Secrets

```bash
# Upload DATABASE_URL
export MY_DB_URL="postgresql://user:password@host:5432/dbname"
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key DATABASE_URL --from-env MY_DB_URL

# Set ENVIRONMENT (optional, defaults to development)
export MY_ENV="production"
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key ENVIRONMENT --from-env MY_ENV
```

### Verify Secrets Created

```bash
# List organization secrets (shows names only, not values)
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-list
```

## Step 2: Create Organization Blueprint

### Create Organization Blueprint (Optional - For Reusable Base)

If you want to create a reusable organization blueprint for Python FastAPI projects:

```bash
# Create organization blueprint via CLI
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud org blueprint-create --name "python-fastapi-standard"
```

Or use the Devin Cloud dashboard to create the organization blueprint with the following configuration:

```yaml
# Organization Blueprint Configuration
name: python-fastapi-standard
description: Standard environment for Python FastAPI projects

initialize:
  - run: |
      pip install fastapi uvicorn pytest pytest-cov ruff mypy python-dotenv

maintenance:
  - run: |
      pip install -q fastapi uvicorn pytest pytest-cov ruff mypy python-dotenv

knowledge:
  - name: org-lint
    contents: |
      ruff check .
      ruff format --check .
      mypy .
      
  - name: org-test
    contents: |
      pytest --cov=. --cov-report=html
```

## Step 3: Create Repository Blueprint

### First: Push Code to Git and Index in Devin Cloud

```bash
# Commit and push your code
git add .
git commit -m "Add organization blueprint setup"
git push origin main

# Then index the repository in Devin Cloud (via dashboard or CLI)
```

### Create Repository Blueprint

For this specific repository, create a blueprint that references the organization secrets:

```bash
# Check if blueprint already exists for this repo (after indexing)
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-list

# If auto-detection didn't create a blueprint, create it manually:
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-create --repo YOUR_ORG/YOUR_REPO --from-file environment.yaml
```

**Note**: Even if environment.yaml is in your git repository, Devin Cloud typically requires explicit blueprint creation to:
- Register the blueprint in the system
- Associate it with your specific repository  
- Configure build settings
- Set up secret access permissions

Replace `YOUR_ORG/YOUR_REPO` with your actual repository (e.g., `myorg/fastapi-example`).

## Step 4: Build and Test the Blueprint

```bash
# Trigger the build process
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build

# If the build fails, check the logs
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build-logs --build-job-id <BUILD_JOB_ID>
```

The build process will:
1. Set up the environment using the blueprint
2. Inject organization secrets into the environment
3. Install dependencies
4. Verify the setup is working

## Step 5: Test the Application

Once the build succeeds, you can test the application:

### Option 1: Using Devin Cloud Sandbox

```bash
# Create a sandbox to test the environment
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs sandbox-create --repo YOUR_ORG/YOUR_REPO

# Start the application in the sandbox
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs run --devin-id <DEVIN_ID> --command "uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### Option 2: Test Endpoints

```bash
# Test the root endpoint (shows API key status)
curl http://localhost:8000/

# Expected response:
# {
#   "message": "Hello World from FastAPI!",
#   "environment": "development",
#   "api_key_status": "configured (length: 32)"
# }

# Test the secrets status endpoint
curl http://localhost:8000/secrets-status

# Expected response:
# {
#   "service": "fastapi-example",
#   "organization_secrets": {
#     "API_KEY": {
#       "status": "configured",
#       "length": 32,
#       "source": "organization blueprint"
#     },
#     "DATABASE_URL": {
#       "status": "configured",
#       "length": 45,
#       "source": "organization blueprint"
#     }
#   },
#   "environment": "development"
# }
```

## Step 6: Verify Security

### Verify Secrets Are Not in Repository

```bash
# Ensure .env file doesn't contain actual secrets
cat .env

# Should show:
# ENVIRONMENT=development
# # API_KEY and DATABASE_URL are provided by organization blueprint
# # Do not set these values locally - they are injected by Devin Cloud

# Ensure .gitignore is properly configured
cat .gitignore | grep ".env"
```

### Verify Secrets Are Not in Git History

```bash
# Check git history for accidental secret commits
git log --all --full-history --source -- "*.env"
git log --all --full-history --source -- "environment.yaml"
```

## Step 7: Update Existing Blueprint (If Needed)

If you need to update the blueprint after making changes:

```bash
# Get the existing blueprint ID
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-list

# Update the blueprint
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-write --blueprint-id <BLUEPRINT_ID> --from-file environment.yaml

# Rebuild
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build
```

## Step 8: Rotate Secrets (Security Best Practice)

定期轮换机密：

```bash
# Upload new secret value
export NEW_API_KEY="sk-new-api-key-here"
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key API_KEY --from-env NEW_API_KEY

# Rebuild the environment to pick up new secret
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build
```

## Common Issues and Solutions

### Issue: "Secret not found" during build

**Solution:** Ensure the secret is uploaded to the organization and the key name matches exactly (case-sensitive).

```bash
# List secrets to verify
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-list
```

### Issue: API key shows as "not configured" in application

**Solution:** Check that the environment.yaml correctly exports the secret:

```yaml
initialize:
  - run: |
      export API_KEY=$API_KEY  # Must match secret name exactly
```

### Issue: Build fails with permission errors

**Solution:** Ensure you have organization admin permissions to create blueprints and secrets.

### Issue: Local development without organization secrets

**Solution:** For local testing, you can temporarily set secrets in your local .env file (but never commit this):

```bash
# For local testing only (DO NOT COMMIT)
echo "API_KEY=test_key_for_local_dev" >> .env
```

## Security Best Practices

### ✅ DO:
- Use organization-level secrets for all sensitive data
- Reference secrets via `$VARNAME` in blueprints
- Rotate secrets regularly
- Use descriptive secret names
- Document secret purposes in metadata
- Test secret access in sandbox environments first

### ❌ DON'T:
- Never hardcode secrets in repository files
- Never pass secret values via command line arguments
- Never commit `.env` files with real values
- Never share secrets in chat or documentation
- Never use the same secret across different environments
- Never log or print secret values

## CLI Commands Reference

### Secret Management
```bash
# Create secret from environment variable
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key KEY_NAME --from-env ENV_VAR

# Create secret from file
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key KEY_NAME --from-file /path/to/file

# Create secret from stdin
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key KEY_NAME --from-stdin

# List secrets
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-list
```

### Blueprint Management
```bash
# List blueprints
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-list

# Create blueprint from file
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-create --repo ORG/REPO --from-file environment.yaml

# Update existing blueprint
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-write --blueprint-id ID --from-file environment.yaml
```

### Build and Testing
```bash
# Trigger build
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build

# Get build logs
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build-logs --build-job-id JOB_ID

# Create sandbox
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs sandbox-create --repo ORG/REPO

# Run command in sandbox
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs run --devin-id ID --command "COMMAND"
```

## Application Endpoints

### Root Endpoint (`GET /`)
Shows basic information including API key configuration status:
```json
{
  "message": "Hello World from FastAPI!",
  "environment": "development",
  "api_key_status": "configured (length: 32)"
}
```

### Secrets Status Endpoint (`GET /secrets-status`)
Detailed view of organization secrets:
```json
{
  "service": "fastapi-example",
  "organization_secrets": {
    "API_KEY": {
      "status": "configured",
      "length": 32,
      "source": "organization blueprint"
    },
    "DATABASE_URL": {
      "status": "configured",
      "length": 45,
      "source": "organization blueprint"
    }
  },
  "environment": "development"
}
```

### Health Check (`GET /health`)
Basic health check:
```json
{
  "status": "healthy",
  "service": "fastapi-example"
}
```

## Summary

This setup demonstrates:
1. **Security**: Secrets are never stored in the repository
2. **Flexibility**: Easy to rotate secrets without code changes
3. **Consistency**: Organization blueprints ensure standard configurations
4. **Automation**: Devin Cloud automatically injects secrets during environment setup
5. **Visibility**: Application endpoints show secret status without exposing values

The application now relies entirely on organization-level secrets for sensitive data, making it secure and maintainable for production deployments.
