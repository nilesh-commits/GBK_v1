# 09 — Local Development

> Planned developer workflow. Commands are the intended interface; they are finalized
> alongside implementation.

## Prerequisites

- Docker and Docker Compose (the supported path for reproducible local development).
- Optional for non-container work: Python 3.11+ and Node.js 20+.

## Configuration

Copy the template and fill values locally:

```bash
cp .env.example .env
```

Key variables (full list in [08 — Deployment](08-deployment.md)):

| Variable | Default (dev) | Purpose |
|---|---|---|
| `ELEXON_BASE_URL` | Elexon BMRS base | Source API; overridable for tests |
| `PURCHASE_CUTOFF_*` | documented assumption | Configurable purchasing cutoff |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL for the SPA |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allow the dev frontend |

Secrets are never committed. `.env` is git-ignored; `.env.example` holds keys only.

## Run everything with Docker Compose

```bash
docker compose up --build
# frontend: http://localhost:5173
# backend:  http://localhost:8000  (OpenAPI docs at /docs)
```

## Data ingestion

The backend serves from a **parquet cache**, not live Elexon calls on the request path. Populate/refresh the cache with the ingestion script:

```bash
docker compose run --rm backend python scripts/ingest.py
```

This fetches the January-2026 window (FUELHH `WIND` actuals + all WINDFOR vintages), normalizes to UTC/MW/30-min intervals, and writes parquet. See [03 — Data Sources](03-data-sources.md).

### Why parquet and not a database

The dataset is small (~1,500 actual intervals plus a bounded set of forecast vintages), read-only, and immutable (January 2026 is historical). A database would add a service to run, deploy, and configure for no analytical benefit. Parquet + pandas gives a fast, reproducible, offline-capable demo and nothing extra to deploy. (If server-side SQL filtering were ever wanted, SQLite — a single file, zero-config — is the fallback; it is not needed for the current scope.)

## Running tests

```bash
docker compose run --rm backend pytest
docker compose run --rm frontend npm test
```

See [07 — Testing](07-testing.md) for coverage.

## Build/run without Docker (optional)

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```
