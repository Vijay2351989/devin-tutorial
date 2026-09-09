# Verification Checklist for Organization Blueprint Setup

This checklist helps verify that the organization blueprint and secret management setup is correctly configured.

## ✅ Pre-Deployment Verification

### 1. Repository Configuration

- [ ] **environment.yaml** correctly references organization secrets
  ```yaml
  initialize:
    - run: |
        export API_KEY=$API_KEY
        export DATABASE_URL=$DATABASE_URL
  ```

- [ ] **.env** file does not contain actual secret values
  ```bash
  cat .env
  # Should only show comments and ENVIRONMENT
  ```

- [ ] **.gitignore** includes `.env` to prevent accidental commits
  ```bash
  cat .gitignore | grep ".env"
  ```

- [ ] **Application code** reads secrets from environment variables
  ```python
  api_key = os.getenv("API_KEY")
  ```

### 2. Security Verification

- [ ] No secret values in repository files
  ```bash
  # Search for potential secret patterns
  grep -r "sk-" . --exclude-dir=.git
  grep -r "api_key" . --exclude-dir=.git
  grep -r "password" . --exclude-dir=.git
  ```

- [ ] No secrets in git history
  ```bash
  git log --all --full-history --source -- "*.env"
  git log --all --full-history --source -- "environment.yaml"
  ```

- [ ] .env.example is properly documented
  ```bash
  cat .env.example
  # Should explain that secrets come from organization blueprint
  ```

### 3. Application Logic Verification

- [ ] **Root endpoint** (`/`) shows API key status
  - Returns masked status: `"api_key_status": "configured (length: 32)"`
  - Never exposes actual API key value
  - Shows "not configured" when secret is missing

- [ ] **Secrets status endpoint** (`/secrets-status`) shows detailed status
  - Shows configuration status for each secret
  - Shows length of secret values (for verification)
  - Shows source as "organization blueprint"
  - Never exposes actual secret values

- [ ] **Tests** cover secret functionality
  ```bash
  # Check test file includes secret tests
  grep -A 5 "test_secrets_status" tests/test_main.py
  ```

## 🚀 Deployment Verification

### 4. Organization Secrets Setup

- [ ] **Secrets uploaded to organization**
  ```bash
  "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-list
  # Should show: API_KEY, DATABASE_URL, ENVIRONMENT
  ```

- [ ] **Secret names match exactly** (case-sensitive)
  - `$API_KEY` in environment.yaml matches `API_KEY` secret
  - `$DATABASE_URL` in environment.yaml matches `DATABASE_URL` secret

- [ ] **Secret values are valid** (test in sandbox first)
  - API key format is correct for your service
  - Database URL is properly formatted
  - Environment value is valid (development/staging/production)

### 5. Blueprint Configuration

- [ ] **Blueprint created for repository**
  ```bash
  "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-list
  # Should show your repository blueprint
  ```

- [ ] **Blueprint uses correct environment.yaml**
  - File path is correct
  - YAML syntax is valid
  - Secret references use `$VARNAME` format

- [ ] **Blueprint build succeeds**
  ```bash
  "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build
  # Should complete with "success" status
  ```

### 6. Runtime Verification

- [ ] **Application starts successfully**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  # Server should start without errors
  ```

- [ ] **Root endpoint returns expected response**
  ```bash
  curl http://localhost:8000/
  # Should include api_key_status field
  ```

- [ ] **Secrets status endpoint shows configured secrets**
  ```bash
  curl http://localhost:8000/secrets-status
  # Should show both secrets as "configured"
  ```

- [ ] **Environment variables are accessible to application**
  - Application can read `os.getenv("API_KEY")`
  - Application can read `os.getenv("DATABASE_URL")`
  - Values match organization secrets

## 🔒 Security Verification

### 7. Secret Exposure Prevention

- [ ] **Secrets never appear in logs**
  - Check build logs for secret values
  - Check application logs for secret values
  - Secrets should only appear as masked or referenced

- [ ] **Secrets never appear in API responses**
  - Root endpoint only shows status, not value
  - Secrets status endpoint only shows length, not value
  - No endpoint returns actual secret values

- [ ] **Secrets never appear in error messages**
  - Test error scenarios
  - Ensure secrets aren't exposed in stack traces
  - Ensure secrets aren't exposed in debug output

### 8. Access Control

- [ ] **Organization secret permissions are correct**
  - Only authorized users can access secrets
  - Repository has permission to access required secrets
  - Secret access is logged and auditable

- [ ] **Repository permissions are appropriate**
  - Only authorized users can modify blueprints
  - Only authorized users can trigger builds
  - Changes are reviewed before deployment

## 📋 Final Verification Steps

### 9. End-to-End Test

- [ ] **Complete deployment test**
  1. Upload test secrets to organization
  2. Create/update blueprint
  3. Trigger build
  4. Deploy to test environment
  5. Verify application starts
  6. Test all endpoints
  7. Verify secret functionality
  8. Clean up test secrets

- [ ] **Secret rotation test**
  1. Update secret value in organization
  2. Rebuild environment
  3. Verify application uses new secret
  4. Verify old secret is no longer accessible

- [ ] **Failover test**
  1. Remove secret from organization
  2. Rebuild environment
  3. Verify application handles missing secret gracefully
  4. Restore secret and verify recovery

### 10. Documentation Verification

- [ ] **Setup guide is complete**
  - All CLI commands are documented
  - All configuration options are explained
  - Troubleshooting section covers common issues

- [ ] **README is updated**
  - Organization blueprint usage is documented
  - Secret management is explained
  - Deployment steps are clear

- [ ] **Code comments are accurate**
  - Secret usage is documented in code
  - Environment variable references are clear
  - Security considerations are noted

## 🐛 Common Issues and Solutions

### Issue: "Secret not found" during build

**Verification steps:**
1. Check secret exists: `"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-list`
2. Check name matches exactly (case-sensitive)
3. Check blueprint references correct variable name
4. Verify repository has access to the secret

### Issue: API key shows as "not configured"

**Verification steps:**
1. Check environment.yaml exports the secret
2. Check secret is uploaded to organization
3. Check maintenance section also exports the secret
4. Test in sandbox to isolate the issue

### Issue: Build fails with permission errors

**Verification steps:**
1. Verify you have organization admin access
2. Check repository permissions
3. Verify blueprint creation permissions
4. Contact organization admin if needed

### Issue: Secrets appear in logs

**Verification steps:**
1. This is a security issue - report immediately
2. Check environment.yaml for accidental logging
3. Check application code for debug prints
4. Review build logs for sensitive data
5. Rotate exposed secrets immediately

## ✅ Success Criteria

The setup is successful when:

- ✅ No secret values are stored in the repository
- ✅ Organization secrets are accessible to the application
- ✅ Application correctly reads and uses secrets
- ✅ Endpoints show secret status without exposing values
- ✅ Blueprint builds successfully
- ✅ Application runs without errors
- ✅ Secret rotation works correctly
- ✅ Security best practices are followed
- ✅ Documentation is complete and accurate

## 📞 Support Resources

If you encounter issues:

1. **Check documentation**: Review `ORGANIZATION_SETUP_GUIDE.md`
2. **Check logs**: Use `"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build-logs`
3. **Test in sandbox**: Use `"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs sandbox-create`
4. **Verify permissions**: Check organization and repository access
5. **Contact support**: Use Devin Cloud support channels

---

**Last Updated**: 2026-09-09
**Status**: Ready for organization blueprint deployment
