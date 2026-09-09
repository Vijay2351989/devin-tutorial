# FastAPI Example Project with Organization Blueprint

A comprehensive FastAPI example project demonstrating best practices for Python web development with tests, linting, and **organization-level secret management** for Devin Cloud. This project shows how to securely manage secrets using organization blueprints instead of storing them in the repository.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application with organization secret support
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Test cases including secret functionality
├── scripts/
│   ├── lint.py              # Cross-platform linting
│   ├── lint.bat             # Windows linting
│   └── format.bat           # Windows formatting
├── .env.example             # Environment variables template (no actual secrets)
├── .env                     # Local reference only (no actual secrets)
├── .gitignore
├── environment.yaml         # Devin environment setup with organization secret references
├── pyproject.toml           # Project configuration
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── ORGANIZATION_SETUP_GUIDE.md  # Step-by-step CLI commands for organization setup
├── ORGANIZATION_BLUEPRINT_GUIDE.md  # Detailed explanation of organization blueprints
├── VERIFICATION_CHECKLIST.md     # Pre and post-deployment verification
├── test_logic.py            # Logic verification without running server
└── README.md
```

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py
```

### Linting and Formatting

```bash
# Run linting checks
python scripts/lint.py

# Or on Windows:
scripts\lint.bat

# Format code
ruff format .

# Or on Windows:
scripts\format.bat
```

### Type Checking

```bash
mypy app/
```

## Devin Cloud Setup

This project is configured for Devin Cloud using the `environment.yaml` file with **organization-level secret management**. When you run this project in Devin Cloud:

1. **Initial setup** (`initialize` section):
   - Installs all dependencies
   - Imports organization secrets (`$API_KEY`, `$DATABASE_URL`)
   - Creates minimal .env file for reference

2. **Session maintenance** (`maintenance` section):
   - Ensures dependencies are installed
   - Ensures organization secrets are available in environment

3. **Knowledge commands** (available to Devin):
   - `lint`: Run linting checks
   - `test`: Run tests
   - `startup`: Start the FastAPI server
   - `project_structure`: View project structure
   - `dependencies`: View dependency information
   - `secrets`: View organization secret management information

**Key Feature**: This project uses organization-level secrets exclusively. No secret values are stored in the repository.

## Secret Management

### 🎯 Organization Blueprint Approach (Recommended)

This project demonstrates **organization-level secret management** - the most secure approach for production deployments.

**Quick Start:**
1. See `ORGANIZATION_SETUP_GUIDE.md` for step-by-step CLI commands
2. Upload secrets to your organization using secure methods
3. Create repository blueprint referencing organization secrets
4. Deploy - secrets are automatically injected

**Example CLI Commands:**
```bash
# Upload API key securely (value never enters chat)
export MY_API_KEY="sk-your-actual-key"
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key API_KEY --from-env MY_API_KEY

# Create blueprint for repository
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-create --repo your-org/your-repo --from-file environment.yaml

# Build and deploy
"C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build
```

### Local Development (For Testing Only)

For local development without organization access:

1. Copy `.env.example` to `.env`
2. The `.env` file contains only comments and ENVIRONMENT
3. **Do not add actual secret values** - they come from organization blueprint
4. For local testing, you can temporarily add test values (never commit)

**Important**: This project is designed to use organization secrets. Local development should ideally use a sandbox environment with organization access.

## API Endpoints

- `GET /` - Returns hello world message with **API key configuration status**
  ```json
  {
    "message": "Hello World from FastAPI!",
    "environment": "development",
    "api_key_status": "configured (length: 32)"
  }
  ```

- `GET /health` - Health check endpoint
  ```json
  {
    "status": "healthy",
    "service": "fastapi-example"
  }
  ```

- `GET /secrets-status` - **Organization secrets status** (shows configuration without exposing values)
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

- `GET /items/{item_id}` - Example with path and query parameters

## Configuration

- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn
- **Testing**: Pytest with httpx
- **Linting**: Ruff (modern replacement for flake8/black)
- **Type Checking**: MyPy
- **Environment**: python-dotenv

## Best Practices Demonstrated

1. **Security**: Organization-level secret management (no secrets in repository)
2. **Separation of concerns**: Clear project structure
3. **Environment configuration**: Using organization blueprints
4. **Testing**: Comprehensive test coverage including secret functionality
5. **Code quality**: Linting and type checking
6. **Documentation**: Comprehensive guides for organization setup
7. **DevOps ready**: Complete environment configuration for cloud deployment
8. **Secret rotation**: Easy secret rotation without code changes
9. **Auditability**: Clear secret usage tracking and status endpoints
10. **Zero-trust**: Application only receives secrets at runtime from organization

## 📚 Documentation

- **[ORGANIZATION_SETUP_GUIDE.md](ORGANIZATION_SETUP_GUIDE.md)** - Step-by-step CLI commands for setting up organization blueprints and secrets
- **[ORGANIZATION_BLUEPRINT_GUIDE.md](ORGANIZATION_BLUEPRINT_GUIDE.md)** - Detailed explanation of organization blueprint concepts and benefits
- **[VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)** - Pre and post-deployment verification checklist

## 🔍 Quick Verification

To verify the setup is working correctly:

1. **Check repository has no secrets:**
   ```bash
   grep -r "sk-" . --exclude-dir=.git
   # Should return no results
   ```

2. **Verify environment.yaml references organization secrets:**
   ```bash
   grep "export API_KEY" environment.yaml
   # Should show: export API_KEY=$API_KEY
   ```

3. **Test application logic locally:**
   ```bash
   python test_logic.py
   # Should pass all logic tests
   ```

## 🚀 Deployment Workflow

1. **Push code to git and index in Devin Cloud** (one-time):
   ```bash
   git add .
   git commit -m "Add organization blueprint setup"
   git push origin main
   # Then index repository in Devin Cloud dashboard
   ```

2. **Setup organization secrets** (one-time):
   ```bash
   export MY_API_KEY="your-actual-key"
   "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs secret-create --key API_KEY --from-env MY_API_KEY
   ```

3. **Create repository blueprint** (one-time, after indexing):
   ```bash
   # Check if auto-detected
   "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-list
   
   # If not auto-detected, create manually
   "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs blueprint-create --repo your-org/your-repo --from-file environment.yaml
   ```

4. **Build and deploy** (every update):
   ```bash
   "C:\Users\Vijay.Bhatt\AppData\Local\devin\cli\bin\devin.exe" cloud drs build
   ```

5. **Verify deployment**:
   - Check `/secrets-status` endpoint
   - Verify API key shows as "configured"
   - Test application functionality

**Important**: Even with environment.yaml in your git repository, you typically need to explicitly create the blueprint to register it in Devin Cloud's system and set up proper permissions.

## 🎯 Key Achievement

This project demonstrates a **complete, production-ready setup** where:
- ✅ No secret values are ever stored in the repository
- ✅ Secrets are managed securely at the organization level
- ✅ Application receives secrets automatically at runtime
- ✅ Secret rotation is simple (no code changes needed)
- ✅ Security best practices are followed throughout
- ✅ Complete documentation for setup and verification

This represents the ideal organization blueprint setup for Python FastAPI projects in Devin Cloud.
