# Wind Forecast & Accuracy Portal

A web application for a UK energy utility's **day-ahead electricity purchasing team**. It helps them:

1. See the **latest eligible national wind generation forecast** available at the point a purchasing decision is made.
2. **Quantify wind forecast accuracy** by comparing forecasts against actual generation.

Scope is deliberately limited to **Elexon national wind** — FUELHH actuals and WINDFOR forecasts — for purchase **decisions made in January 2026** (day-ahead, so delivery days span 2 Jan – 1 Feb 2026).

> **Status:** runs end-to-end locally (backend + frontend, Dockerized). Not yet deployed — no live URL is claimed until a deployment is verified. See [Deployment](#deployment).

---

## Repository layout

```
.
├── backend/              FastAPI service (Python)
│   ├── app/
│   │   ├── main.py            app wiring, CORS, error handlers, startup cache load
│   │   ├── config.py          settings (Elexon URL, cutoff default, CORS, scope)
│   │   ├── time_utils.py      UTC/Europe-London cutoff + delivery-day mapping
│   │   ├── adapters/          Elexon BMRS client (FUELHH, WINDFOR)
│   │   ├── services/          forecast_selection, join, metrics  (pure logic)
│   │   ├── data/cache.py      in-memory parquet-backed cache
│   │   ├── api/               routers: health, forecasts, accuracy
│   │   └── models/schemas.py  pydantic response models
│   ├── scripts/ingest.py      one-shot Elexon -> parquet ingestion
│   ├── tests/                 pytest unit + integration (16 tests)
│   └── Dockerfile
├── frontend/             React + Vite + TypeScript SPA
│   ├── src/
│   │   ├── api/               typed client + response types
│   │   ├── components/        Sidebar, Header, charts, table, controls, StateBoundary
│   │   ├── views/             Overview, ForecastDashboard, AccuracyAnalysis, DataMethodology
│   │   ├── hooks/useApiData   fetch with cancellation + stale-response guard
│   │   └── lib/format.ts      MW / time formatting (Europe/London)
│   └── Dockerfile
├── docker-compose.yml    backend (:8000) + frontend (:5173)
├── docs/                 full design documentation (01–11)
├── require.md            requirements notes
├── task.md               phased tasklist / progress tracker
└── .env.example          environment variables
```

Deep documentation lives in [`docs/`](docs/README.md): [architecture](docs/02-architecture.md), [data sources](docs/03-data-sources.md), [methodology](docs/04-methodology.md), [API reference](docs/05-api-reference.md), [frontend](docs/06-frontend.md), [testing](docs/07-testing.md), [edge cases](docs/10-edge-cases-and-data-quality.md), [assumptions & limitations](docs/11-assumptions-and-limitations.md).

---

## How to run

### Option A — Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
# backend:  http://localhost:8000  (API docs at /docs)
# frontend: http://localhost:5173
```

Populate the data cache once (the backend serves from parquet, not live Elexon):

```bash
docker compose run --rm backend python scripts/ingest.py
```

Then reload the frontend.

### Option B — Local (no Docker)

**Backend** (Python 3.11):
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/ingest.py                               # fetch Jan-2026 data -> data/*.parquet
uvicorn app.main:app --reload                          # http://localhost:8000
```

**Frontend** (Node 20+):
```bash
cd frontend
npm install
npm run dev                                            # http://localhost:5173
```

The frontend reads the backend URL from `VITE_API_URL` (defaults to `http://localhost:8000`).

---

## Running tests

```bash
# Backend (16 unit + integration tests)
cd backend && pytest
# or: docker compose run --rm backend pytest

# Frontend (component + API-client tests)
cd frontend && npm test
```

---

## API

Base path `/api`; interactive OpenAPI docs at `/docs`. Primary parameter is `decision_date` (1–31 Jan 2026); the delivery day (`decision_date + 1`) is derived.

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Readiness + cache status |
| `GET /api/forecasts?decision_date=YYYY-MM-DD` | Latest eligible forecast for the delivery day |
| `GET /api/forecasts/history?decision_date=…` | All forecast vintages, flagged eligible-at-cutoff |
| `GET /api/accuracy?decision_date=…` | Forecast vs actual series + MAE/RMSE/Bias |

Full request/response schemas and error codes: [docs/05-api-reference.md](docs/05-api-reference.md).

---

## Methodology (summary)

- **Point-in-time correctness.** For each decision we use only the latest WINDFOR vintage published **on or before the purchasing cutoff**; later vintages are never used to score an earlier decision (no look-ahead bias).
- **Cutoff.** Defaults to **12:00 Europe/London on the decision day** — a *provisional assumption*, not an official market deadline — and is configurable per request/env.
- **Resolution alignment (data finding).** WINDFOR is published **hourly**; FUELHH actuals are **half-hourly**. Actuals are aggregated to the hourly forecast grid by mean before comparison — a documented alignment, not interpolation. Missing intervals are excluded and counted, never treated as zero.
- **Metrics (MW).** `error = forecast − actual` (positive = over-forecast); MAE, RMSE, Bias, each reported with the number of matched intervals.

Detail: [docs/04-methodology.md](docs/04-methodology.md).

### Scope limitation

The datasets cover national wind only. The portal quantifies **wind forecast uncertainty**; it does **not** compute an electricity shortfall or a recommended purchase quantity (that would need demand and other generation availability).

---

## Deployment

Planned: **frontend → Vercel** (static build; set `VITE_API_URL` to the backend URL), **backend → Render** (Docker web service; set `CORS_ALLOWED_ORIGINS` to the Vercel origin). Render's free tier cold-starts after idle — warm it before a demo. Nothing is deployed yet; the live URL will be added here once verified in a fresh incognito session. Steps: [docs/08-deployment.md](docs/08-deployment.md).

---

## AI tool disclosure

This project was built with the assistance of **Claude Code (Claude Opus)**. AI assistance was used to: draft the design documentation set (`docs/`), scaffold and implement the FastAPI backend and React frontend, write the test suites, and investigate the Elexon data (including discovering the WINDFOR hourly vs FUELHH half-hourly resolution difference). All code was run and verified: the backend was tested against live Elexon January-2026 data, and both test suites pass.
