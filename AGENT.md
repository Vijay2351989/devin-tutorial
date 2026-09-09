# AGENT.md

Canonical entry point for working in this repository.

## Overview

`fastapi-example` is a small FastAPI application whose primary purpose is to
demonstrate **organization-level secret management in Devin Cloud**: secrets are
injected into the environment from organization blueprints and consumed at
runtime, never committed to the repository. The HTTP endpoints exist mainly to
show and verify that flow.

## Tech Stack

- **Runtime:** Python (`requires-python >= 3.8`), FastAPI, Pydantic v2, Uvicorn (`uvicorn[standard]`), python-dotenv
- **Testing:** pytest, pytest-asyncio, httpx
- **Quality:** ruff (lint + format), black, mypy
- **Environment:** `environment.yaml` (Devin Cloud blueprint: `initialize`, `maintenance`, `knowledge`)

## Repository Structure

```
.
├── app/
│   ├── __init__.py
│   └── main.py                     # FastAPI app: MessageResponse + 4 GET endpoints
├── tests/
│   ├── __init__.py
│   └── test_main.py                # httpx.AsyncClient tests for every endpoint
├── scripts/
│   ├── lint.py                     # Cross-platform lint entry point
│   ├── lint.sh                     # Shell linting
│   ├── lint.bat                    # Windows linting
│   └── format.bat                  # Windows formatting
├── docs/features/
│   ├── secret-management.md        # Organization secret flow deep dive
│   └── api-endpoints.md            # Endpoint reference
├── environment.yaml                # Devin environment setup + knowledge sections
├── pyproject.toml                  # ruff / black / mypy / pytest configuration
├── ruff.toml                       # Standalone ruff config (mirrors pyproject)
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── .env.example                    # Template — no secret values
└── test_logic.py                   # Logic checks without running the server
```

## Commands

Install:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run the server:

```bash
uvicorn app.main:app --reload
# interactive docs at http://localhost:8000/docs
```

Test:

```bash
pytest
pytest --cov=app
```

Lint and type check:

```bash
python scripts/lint.py     # ruff check, ruff format --check, mypy app/
```

`scripts/lint.sh`, `scripts/lint.bat`, and `scripts/format.bat` are
platform-specific equivalents.

## Secrets

`API_KEY` and `DATABASE_URL` come from **Devin Cloud organization blueprints**
and are exported by the `initialize` and `maintenance` steps in
`environment.yaml`. `ENVIRONMENT` defaults to `development`. No secret values
live in this repository, and `.env` is git-ignored — see
[security.rules](security.rules).

## Index

Rules:

- [security.rules](security.rules) — secret handling
- [testing.rules](testing.rules) — test requirements
- [coding-standards.rules](coding-standards.rules) — Python style and typing

Feature docs:

- [docs/features/secret-management.md](docs/features/secret-management.md)
- [docs/features/api-endpoints.md](docs/features/api-endpoints.md)

Guides:

- [README.md](README.md)
- [ORGANIZATION_SETUP_GUIDE.md](ORGANIZATION_SETUP_GUIDE.md)
- [ORGANIZATION_BLUEPRINT_GUIDE.md](ORGANIZATION_BLUEPRINT_GUIDE.md)
- [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)
