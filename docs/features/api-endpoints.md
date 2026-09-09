# API Endpoints

All endpoints are defined in `app/main.py`. The app is titled
`FastAPI Example`, version `0.1.0`. Interactive documentation is served at
[`/docs`](http://localhost:8000/docs) (Swagger UI) when the server is running:

```bash
uvicorn app.main:app --reload
```

See [../../AGENT.md](../../AGENT.md) for project context and
[secret-management.md](secret-management.md) for the secret flow behind `/` and
`/secrets-status`.

## `GET /`

Welcome message plus masked `API_KEY` status. Response model:
`MessageResponse` (`message: str`, `environment: Optional[str]`,
`api_key_status: Optional[str]`).

Parameters: none.

```json
{
  "message": "Hello World from FastAPI!",
  "environment": "development",
  "api_key_status": "configured (length: 32)"
}
```

When `API_KEY` is unset, `api_key_status` is `"not configured"`.
`environment` is `ENVIRONMENT` or `"development"`.

## `GET /health`

Health check. Parameters: none.

```json
{
  "status": "healthy",
  "service": "fastapi-example"
}
```

## `GET /items/{item_id}`

Example endpoint with a path parameter and an optional query parameter.

| Parameter | In | Type | Required |
| --- | --- | --- | --- |
| `item_id` | path | `int` | yes |
| `q` | query | `str` | no (defaults to `null`) |

`GET /items/42`:

```json
{
  "item_id": 42,
  "q": null
}
```

`GET /items/42?q=test`:

```json
{
  "item_id": 42,
  "q": "test"
}
```

A non-integer `item_id` returns FastAPI's standard `422` validation error.

## `GET /secrets-status`

Masked status of the organization secrets `API_KEY` and `DATABASE_URL`.
Parameters: none.

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
      "status": "not configured",
      "length": 0,
      "source": "missing"
    }
  },
  "environment": "development"
}
```

Full field contract: [secret-management.md](secret-management.md). Secret values
are never returned.
