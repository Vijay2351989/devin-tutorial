# Secret Management

How organization-level secrets flow from Devin Cloud into this application. See
[../../AGENT.md](../../AGENT.md) for project context and
[../../security.rules](../../security.rules) for the rules that govern secret
handling.

## The flow

```
Devin Cloud organization blueprint (secret store)
        │  injects API_KEY, DATABASE_URL into the environment
        ▼
environment.yaml  →  initialize / maintenance export the variables
        ▼
app/main.py  →  os.getenv("API_KEY"), os.getenv("DATABASE_URL")
        ▼
/  and  /secrets-status  →  masked status only (never the value)
```

## 1. Organization blueprint

`API_KEY` and `DATABASE_URL` are defined once at the organization level in Devin
Cloud and injected into every session's environment. Creating the secrets and
the blueprint is covered in
[../../ORGANIZATION_SETUP_GUIDE.md](../../ORGANIZATION_SETUP_GUIDE.md); the
difference between organization-level and repository-level blueprints is
explained in
[../../ORGANIZATION_BLUEPRINT_GUIDE.md](../../ORGANIZATION_BLUEPRINT_GUIDE.md).

## 2. `environment.yaml`

The file has three sections: `initialize`, `maintenance`, and `knowledge`.

`initialize` runs once when the environment is first created. It installs
dependencies, re-exports the injected secrets, and writes a minimal `.env` for
local reference:

```yaml
initialize:
  - run: |
      pip install -r requirements.txt
      pip install -r requirements-dev.txt

      export API_KEY=$API_KEY
      export DATABASE_URL=$DATABASE_URL
      export ENVIRONMENT=${ENVIRONMENT:-development}

      cat > .env << EOF
      ENVIRONMENT=${ENVIRONMENT:-development}
      # API_KEY and DATABASE_URL are provided by organization blueprint
      EOF
```

`maintenance` re-verifies dependencies and re-exports the same variables so the
environment stays ready.

The generated `.env` contains only `ENVIRONMENT` — no secret values — and `.env`
is git-ignored. Organization-injected values take precedence over anything in
`.env`.

`knowledge` holds guidance sections (`lint`, `test`, `startup`,
`project_structure`, `dependencies`, `secrets`) that describe how to work with
the project.

## 3. Runtime consumption

`app/main.py` calls `load_dotenv()` at import time and then reads the variables
with `os.getenv`:

- `API_KEY` — reported as masked status by `/` and `/secrets-status`
- `DATABASE_URL` — reported as masked status by `/secrets-status`
- `ENVIRONMENT` — defaults to `development`

Values are never returned or logged; only presence, length, and source are
exposed.

## `/secrets-status` response contract

`GET /secrets-status` → `200`

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

Per secret:

| Field | Type | Value when set | Value when unset |
| --- | --- | --- | --- |
| `status` | string | `"configured"` | `"not configured"` |
| `length` | int | character length of the value | `0` |
| `source` | string | `"organization blueprint"` | `"missing"` |

`service` is always `"fastapi-example"`; `environment` is `ENVIRONMENT` or
`"development"`.

The root endpoint `/` exposes the same idea for `API_KEY` alone via
`api_key_status`: `"configured (length: N)"` or `"not configured"`.

## Verifying

Start the server and check the endpoint:

```bash
uvicorn app.main:app --reload
curl http://localhost:8000/secrets-status
```

A `source` of `"missing"` means the organization blueprint did not inject the
secret. Work through
[../../VERIFICATION_CHECKLIST.md](../../VERIFICATION_CHECKLIST.md) to diagnose
the setup.

See also [api-endpoints.md](api-endpoints.md).
