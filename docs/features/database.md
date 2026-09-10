# Database and Products API

SQLite persistence via SQLAlchemy 2.x, plus the `POST /api/products` endpoint.
See [../../AGENT.md](../../AGENT.md) for project context and
[api-endpoints.md](api-endpoints.md) for the other endpoints.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./products.db` | SQLAlchemy connection string |

`DATABASE_URL` is read with `os.getenv` in `app/database.py`. In Devin Cloud it
is exported by `environment.yaml` from the organization secret, falling back to
the SQLite default when the secret is unset. SQLite files are git-ignored
(`*.db`, `*.sqlite`, `*.sqlite3`).

## Modules

- `app/models.py` — `Base` (declarative base) and the `Product` ORM model.
- `app/database.py` — `engine`, `SessionLocal`, `get_db` (FastAPI dependency),
  `init_db`, `check_connection`, `get_schema_version`, `configure_engine`.
- `app/schemas.py` — `ProductCreate`, `ProductResponse`, `ErrorResponse`.

### `Product` model (`products` table)

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | Integer | primary key, auto-increment |
| `name` | String(255) | not null, indexed |
| `description` | Text | nullable |
| `price` | Float | not null, `CHECK (price >= 0)` |
| `created_at` | DateTime | not null, `server_default=now()` |
| `updated_at` | DateTime | nullable, set `onupdate` |

### Initialisation and schema versioning

`init_db()` runs in the FastAPI `lifespan` handler on startup. It calls
`Base.metadata.create_all` and maintains a `schema_version` table containing
`SCHEMA_VERSION` (currently `1`). Bump `SCHEMA_VERSION` and add a migration
step in `init_db` when the schema changes. Both operations are idempotent.

For SQLite, the engine is created with `check_same_thread=False`; in-memory
URLs additionally use `StaticPool` so all sessions share one connection.
Non-SQLite URLs use `pool_pre_ping=True`.

## `POST /api/products`

Creates a product. Duplicate names are allowed. Responds `201 Created`.

Request body (`ProductCreate`):

| Field | Type | Rules |
| --- | --- | --- |
| `name` | string | required, 1–255 characters |
| `description` | string | optional |
| `price` | number | required, `>= 0` |

Response (`ProductResponse`):

```json
{
  "id": 1,
  "name": "Widget",
  "description": "A useful widget",
  "price": 9.99,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null
}
```

Errors:

| Status | When | Body |
| --- | --- | --- |
| `422` | validation error (missing `name`, `price < 0`, wrong type, name too long) | FastAPI `{"detail": [...]}` |
| `500` | database failure while saving | `{"detail": "Failed to save product to the database."}` |

Database errors are logged by exception type only; internals are never returned
to the client.

## Testing

`tests/conftest.py` gives every test a fresh in-memory SQLite engine and
overrides the `get_db` dependency on the app, so `products.db` is never touched.

```bash
pytest tests/ -v --cov=app
```
