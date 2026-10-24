# 02 — Architecture

> Planned architecture. No components are implemented yet.

## Overview

A two-tier application: a **React single-page app** talking over HTTP/JSON to a **Python REST backend**. The backend ingests Elexon data into a local **parquet cache** and computes forecast selection and accuracy metrics in-memory with pandas.

```
                    ┌─────────────────────────────────────────┐
  Browser  ──HTTP──▶│  React SPA (Vite)                        │
                    │  - Forecast dashboard                    │
                    │  - Accuracy analysis                     │
                    └───────────────┬─────────────────────────┘
                                    │  JSON over HTTPS
                    ┌───────────────▼─────────────────────────┐
                    │  Python backend (FastAPI)                │
                    │  ┌─────────────┐  ┌───────────────────┐  │
                    │  │ API routes  │─▶│ Services          │  │
                    │  │ (HTTP only) │  │ - forecast select │  │
                    │  └─────────────┘  │ - metrics         │  │
                    │                   └─────────┬─────────┘  │
                    │  ┌─────────────┐            │            │
                    │  │ Elexon      │   ┌────────▼─────────┐  │
                    │  │ adapter     │──▶│ Parquet cache    │  │
                    │  │ (ingestion) │   │ (actuals, fcsts) │  │
                    │  └──────┬──────┘   └──────────────────┘  │
                    └─────────┼───────────────────────────────┘
                              │ HTTPS (ingestion only)
                    ┌─────────▼───────────────────────────────┐
                    │  Elexon BMRS API (FUELHH, WINDFOR)       │
                    └─────────────────────────────────────────┘
```

## Backend framework choice: FastAPI

`require.md` allows Flask or FastAPI. **FastAPI** is chosen because:
- Pydantic request/response models give schema validation and consistent error responses with little code (satisfies the validation and error-contract requirements).
- Auto-generated OpenAPI/Swagger docs at `/docs` satisfy the "document endpoint paths, parameters, response schemas" requirement directly.
- Native async suits outbound Elexon calls during ingestion.

## Component responsibilities

| Layer | Responsibility | Must NOT do |
|---|---|---|
| **API routes** | Parse/validate HTTP params, call services, shape JSON responses, map errors to status codes | Contain forecast-selection or metric math |
| **Services** | Forecast selection (point-in-time), metric computation, join logic | Know about HTTP or Elexon wire format |
| **Elexon adapter** | Fetch FUELHH/WINDFOR, parse, normalize to internal schema, timeouts/retries | Compute metrics |
| **Cache** | Store normalized actuals & forecasts as parquet; load into pandas on startup | Make network calls at request time |

Keeping selection and metric logic **out of route handlers** is a hard requirement (`require.md` §7) and makes that logic directly unit-testable.

## Data flow

**Ingestion (offline / startup):** Elexon adapter pulls Jan-2026 FUELHH (WIND) actuals and WINDFOR forecasts → normalizes (UTC, MW, 30-min intervals) → writes parquet. Reproducible and decoupled from request latency.

**Request time:** Route → service reads from in-memory frames → forecast selection applies the configurable cutoff → join to actuals → metrics → JSON. No live Elexon call on the request path.

See [03 — Data Sources](03-data-sources.md) and [04 — Methodology](04-methodology.md).

## Proposed directory layout

```
/                      repo root
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, route registration
│   │   ├── api/               # routers (health, forecasts, accuracy)
│   │   ├── services/          # forecast_selection.py, metrics.py, join.py
│   │   ├── adapters/          # elexon_client.py
│   │   ├── data/              # cache loader, parquet IO
│   │   └── models/            # pydantic schemas
│   ├── scripts/ingest.py      # one-shot ingestion to parquet
│   ├── tests/                 # unit + integration
│   ├── Dockerfile
│   └── pyproject.toml / requirements.txt
├── frontend/
│   ├── src/                   # React components, hooks, api client
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── docs/                      # this documentation set
├── .env.example
└── README.md
```

## Persistence: no database

A relational database is intentionally **not** used. The dataset is small (~1,500 actual intervals for January + a bounded set of forecast vintages), read-only, and immutable (January 2026 is historical). Data is cached as **parquet** and served from memory. Rationale and trade-offs are in [09 — Local Development](09-local-development.md) and [11 — Assumptions & Limitations](11-assumptions-and-limitations.md).
