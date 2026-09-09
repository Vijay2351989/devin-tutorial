# Organization Blueprint Guide

## What is an Organization Blueprint?

An **Organization Blueprint** in Devin Cloud is a reusable environment configuration template that can be shared across multiple repositories within an organization. It's a higher-level abstraction that allows you to define standard setup procedures, tool configurations, and secret management patterns that can be consistently applied across different projects.

## Key Concepts

### 1. Repository-Level vs Organization-Level

**Repository-Level Blueprint:**
- Specific to a single repository
- Defined in the repository's `environment.yaml`
- Customized for that particular project's needs
- Created via: `devin cloud drs blueprint-create --repo <repo>`

**Organization-Level Blueprint:**
- Shared across multiple repositories in an organization
- Defined at the organization level
- Provides standard configurations that can be inherited
- Can include common secrets, tools, and setup procedures
- Created via organization admin settings

### 2. Blueprint Inheritance

Repositories can inherit from organization blueprints:
```
Organization Blueprint (base)
    ↓
Repository Blueprint (overrides and extensions)
    ↓
Final Environment Configuration
```

### 3. Secret Management

Organization blueprints provide secure secret management:

**Why Organization-Level Secrets?**
- **Security**: Secrets are stored centrally and never exposed in repository code
- **Consistency**: Same secrets available across multiple repositories
- **Rotation**: Easy to rotate secrets in one place
- **Access Control**: Fine-grained permissions for who can access secrets

**How It Works:**
1. Admin uploads secrets to organization: `devin cloud drs secret-create --key API_KEY --from-env MY_VAR`
2. Secrets are referenced in blueprints: `$API_KEY`
3. Devin Cloud automatically injects secrets during environment setup
4. Secret values never appear in logs, chat, or repository files

## Practical Example

### Scenario: Multi-Repository Python Organization

You have an organization with multiple Python services that need:
- Common Python version (3.11)
- Standard testing framework (pytest)
- Shared linting configuration (ruff)
- Common database credentials
- Shared API keys for external services

### Organization Blueprint Configuration

```yaml
# Organization-level blueprint (defined by org admin)
organization:
  name: "python-standard"
  python_version: "3.11"
  
initialize:
  - run: |
      # Install common Python tools
      pip install pytest pytest-cov ruff mypy
      
      # Set up common linting config
      echo "[lint]" > .ruff.toml
      echo "line-length = 88" >> .ruff.toml
      
maintenance:
  - run: |
      # Ensure common tools are available
      pip install -q pytest pytest-cov ruff mypy

knowledge:
  - name: org-test
    contents: |
      # Standard testing command for all repos
      pytest --cov=. --cov-report=html
      
  - name: org-lint
    contents: |
      # Standard linting for all repos
      ruff check .
      ruff format --check .
      mypy .

# Organization-level secrets
secrets:
  - name: DATABASE_URL
    description: "Shared database connection string"
  - name: SHARED_API_KEY
    description: "API key for external service"
```

### Repository Blueprint Using Organization Base

```yaml
# Repository-level blueprint (in environment.yaml)
extends: "python-standard"  # Inherits from org blueprint

initialize:
  - run: |
      # Repository-specific setup
      pip install -r requirements.txt
      
      # Use org secrets
      export DATABASE_URL=$DATABASE_URL
      export SHARED_API_KEY=$SHARED_API_KEY

maintenance:
  - run: |
      # Keep dependencies installed
      pip install -q -r requirements.txt

knowledge:
  - name: startup
    contents: |
      # Repository-specific startup
      uvicorn app.main:app --reload --port 8000
      
  # Inherits org-test and org-lint from organization blueprint
```

## Benefits of Organization Blueprints

### 1. Consistency
- All repositories use the same tools and configurations
- Reduced onboarding time for new projects
- Standardized development practices

### 2. Efficiency
- Don't repeat setup across repositories
- Centralized updates propagate to all repos
- Faster environment setup times

### 3. Security
- Centralized secret management
- No secrets in repository code
- Fine-grained access control

### 4. Maintainability
- Update configuration in one place
- Version control for blueprints
- Rollback capabilities

### 5. Compliance
- Enforce organizational standards
- Audit trail for environment configurations
- Consistent security practices

## Setting Up Organization Blueprints

### For Organization Administrators

1. **Create organization blueprint:**
   ```bash
   # Via Devin Cloud dashboard or CLI
   devin cloud org blueprint-create --name "python-standard"
   ```

2. **Upload secrets:**
   ```bash
   # Never pass secret values directly
   devin cloud drs secret-create --key DATABASE_URL --from-env MY_DB_VAR
   devin cloud drs secret-create --key API_KEY --from-file path/to/secret.txt
   ```

3. **Configure blueprint settings:**
   - Define base configurations
   - Set up shared knowledge sections
   - Configure secret access policies

### For Repository Owners

1. **Create repository blueprint:**
   ```bash
   devin cloud drs blueprint-create --repo myorg/myrepo --from-file environment.yaml
   ```

2. **Optionally extend organization blueprint:**
   ```yaml
   extends: "python-standard"
   ```

3. **Test the build:**
   ```bash
   devin cloud drs build
   ```

## Secret Management Best Practices

### DO:
- Use organization-level secrets for shared credentials
- Reference secrets via `$VARNAME` in blueprints
- Rotate secrets regularly
- Use descriptive secret names
- Document secret purposes in metadata

### DON'T:
- Never hardcode secrets in repository files
- Never pass secret values via command line arguments
- Never commit `.env` files with real values
- Never share secrets in chat or documentation
- Never use the same secret across different environments

## Example: Secret Upload Workflow

### Local Development
```bash
# 1. Set secret in local environment
export MY_API_KEY="sk-1234567890abcdef"

# 2. Upload to organization (value never enters chat)
devin cloud drs secret-create --key API_KEY --from-env MY_API_KEY

# 3. Reference in environment.yaml
initialize:
  - run: |
      export API_KEY=$API_KEY
```

### From File
```bash
# 1. Create file with secret (not in git)
echo "sk-1234567890abcdef" > /tmp/api_key.txt

# 2. Upload from file
devin cloud drs secret-create --key API_KEY --from-file /tmp/api_key.txt

# 3. Clean up
rm /tmp/api_key.txt
```

### Interactive
```bash
# 1. Upload via stdin (secure prompt)
devin cloud drs secret-create --key API_KEY --from-stdin
# Enter secret value when prompted (value not echoed)
```

## Troubleshooting

### Common Issues

**Issue:** Blueprint build fails with "secret not found"
- **Solution:** Ensure secret is uploaded to organization and referenced correctly

**Issue:** Repository can't access organization secret
- **Solution:** Check organization permissions and secret access policies

**Issue:** Environment changes not propagating
- **Solution:** Trigger a new build after updating organization blueprint

**Issue:** Secret appears in logs
- **Solution:** This should never happen - report as security issue immediately

## Conclusion

Organization blueprints provide a powerful way to standardize development environments across repositories while maintaining security through centralized secret management. They represent a DevOps best practice for managing complex, multi-repository organizations in Devin Cloud.

For this example project, you would:
1. Create an organization blueprint for Python FastAPI projects
2. Upload shared secrets (database URLs, API keys) at organization level
3. Create repository-specific blueprints that extend the organization base
4. Reference organization secrets in your repository blueprint

This approach ensures consistency, security, and efficiency across all your Python services.
