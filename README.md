# Issue Tracker API

A small REST API for creating and managing issues, filtering and searching them, and adding comments. It is built with FastAPI, SQLAlchemy, Pydantic, and PostgreSQL, and can run locally or with Docker Compose.

## Features

- Create, retrieve, update, list, and delete issues
- Filter issues by status and priority, search titles, and paginate results
- Add comments to issues; comments are deleted with their issue
- Request validation and interactive OpenAPI documentation

## Requirements

- Python 3.10 or later
- Docker Desktop with Docker Compose, for the containerized setup or local PostgreSQL

## Run with Docker Compose

From the repository root:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and change `POSTGRES_PASSWORD` and the password in `DATABASE_URL` to the same value. Then start the API and database:

```powershell
docker compose up --build
```

The API is available at <http://localhost:8000>. Interactive docs are at <http://localhost:8000/docs>; the alternative ReDoc view is at <http://localhost:8000/redoc>.

The PostgreSQL container is published on port `5433` on the host. Compose stores database files in the `pgdata` volume, so data persists when containers stop. To stop the services, press Ctrl+C and run `docker compose down`. To also remove the stored database, run `docker compose down --volumes`.

## Run the API locally

This option runs PostgreSQL in Docker and the Python API on your machine. First create `.env` as above, then start the database:

```powershell
docker compose up db -d
```

Create a virtual environment, install dependencies, and start the server:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The supplied `.env.example` configures the local API to connect to PostgreSQL at `localhost:5433`. The application creates its tables at startup. Stop the local database with `docker compose down` when finished.

## Configuration

The application loads environment variables from `.env` in the current working directory. `DATABASE_URL` is required. The Compose database service also uses these variables:

| Variable | Purpose | Example |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `change_me` |
| `POSTGRES_DB` | Database name | `issue_tracker` |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql+psycopg://postgres:change_me@localhost:5433/issue_tracker` |

Compose configures the API container to connect to host `db` on the internal PostgreSQL port `5432`. For the API running on your host, use `localhost:5433` as shown in `.env.example`.

## API reference

All endpoints are prefixed at the root; there is currently no authentication.

| Method | Path | Description |
|---|---|---|
| `POST` | `/issues` | Create an issue (`201`) |
| `GET` | `/issues` | List, filter, search, and paginate issues |
| `GET` | `/issues/{issue_id}` | Get one issue, including its comments (`404` if missing) |
| `PATCH` | `/issues/{issue_id}` | Update supplied issue fields (`404` if missing) |
| `DELETE` | `/issues/{issue_id}` | Delete an issue and its comments (`204`; `404` if missing) |
| `POST` | `/issues/{issue_id}/comments` | Add a comment (`201`; `404` if issue is missing) |

### Issue fields

When creating an issue, `title` is required and must be 1-200 characters. `description` defaults to an empty string, `priority` defaults to `medium`, and `status` starts as `open`. Valid statuses are `open`, `in_progress`, and `closed`; valid priorities are `low`, `medium`, and `high`.

`PATCH /issues/{issue_id}` accepts any subset of `title`, `description`, `status`, and `priority`. Omitted fields remain unchanged. Invalid request data returns `422`.

### List query parameters

| Parameter | Description |
|---|---|
| `status` | Filter by `open`, `in_progress`, or `closed` |
| `priority` | Filter by `low`, `medium`, or `high` |
| `q` | Case-insensitive substring search in the title |
| `limit` | Maximum results; defaults to `20`, maximum `100` |
| `offset` | Number of results to skip; defaults to `0` |

Results are ordered by descending issue ID. Filters can be combined.

## Examples

Create an issue:

```bash
curl -X POST http://localhost:8000/issues \
	-H "Content-Type: application/json" \
	-d '{"title":"Login fails after password reset","description":"Reproduced on the web app.","priority":"high"}'
```

Search and filter issues:

```bash
curl "http://localhost:8000/issues?status=open&priority=high&q=login&limit=10&offset=0"
```

Update an issue and add a comment (replace `1` with an issue ID):

```bash
curl -X PATCH http://localhost:8000/issues/1 \
	-H "Content-Type: application/json" \
	-d '{"status":"in_progress"}'

curl -X POST http://localhost:8000/issues/1/comments \
	-H "Content-Type: application/json" \
	-d '{"body":"I am investigating this."}'
```

## Tests

With a working `DATABASE_URL` and PostgreSQL database configured, run:

```powershell
python -m pytest
```

The API tests use the configured database and create records; use a disposable development database when running them.