# REint Full Stack SWE Challenge — Tasklist

> **Budget:** max 16 hours total. Estimates per phase are a cap, not a target.
> **Goal:** A React + Python web app for a UK utility's day-ahead power-purchasing team that
> (1) surfaces the latest eligible national wind forecast and (2) quantifies wind forecast accuracy
> vs. actuals. Elexon BMRS data only (FUELHH actuals + WINDFOR forecasts).
>
> **Scope is decision-anchored:** in-scope events are purchase **decisions made 1–31 Jan 2026**.
> Day-ahead ⇒ each decision is for **next-day delivery**, so delivery days span **2 Jan – 1 Feb 2026**.
> The UI's primary selector is the **decision date** (d); the app derives **delivery = d+1** and applies
> the cutoff on day d.
>
> **Build order:** backend → **backend-test gate** → frontend → integrate → deploy/README/video.
> **Authoritative specs live in `docs/` (01–11).** Build to them.

---

## Phase 0 — Reconcile & save  [~0.5h]
- [x] Reconcile this `task.md` with all confirmed decisions (this rewrite).
- [ ] Correct `docs/03`, `docs/04`, `docs/05`, `docs/11` to decision-anchored scope + `decision_date` param.
- [ ] `git init`; add `.gitignore` (`.env`, `data/*.parquet`, `node_modules/`, `__pycache__/`); commit
      `require.md`, `task.md`, `docs/`, and the original `.docx` before writing any code.

## Phase A — Backend  [~6h]
- [ ] Scaffold `backend/` (FastAPI, uvicorn, httpx, pandas, pyarrow, pytest); `backend/Dockerfile`
      (python:3.11-slim); root `docker-compose.yml` serving backend on `:8000`; `.env.example`.
- [ ] Config (`app/config.py`, pydantic-settings): `ELEXON_BASE_URL`, cutoff default
      (**12:00 Europe/London on decision day**, provisional/configurable), `CORS_ALLOWED_ORIGINS`,
      parquet path, HTTP timeout/retry.
- [ ] Elexon adapter + `scripts/ingest.py`: fetch FUELHH (`fuelType=WIND`) actuals for delivery days
      **2026-01-02 … 2026-02-01**, and WINDFOR (all vintages) published across **Jan 2026** for those
      deliveries. Normalize to UTC / MW / 30-min; write parquet (`actuals`, `forecasts`). Bounded
      timeout, retries w/ backoff, reject+log malformed rows.
- [ ] Cache loader (`app/data/cache.py`): load parquet into pandas on startup; serve from memory
      (**no DB**; no Elexon call on the request path); expose `intervals_cached`.
- [ ] Services (pure, HTTP-free):
  - `forecast_selection.py` — for decision date d, over delivery d+1's intervals pick latest
    `publish_time ≤ cutoff(d)`; no-eligible intervals excluded + counted (never back-filled); expose vintage history.
  - `join.py` — inner-join eligible forecast ↔ actuals on `start_time`; count `missing_forecast` /
    `missing_actual`; **never zero-fill**.
  - `metrics.py` — `error = forecast − actual`; **MAE, RMSE, Bias** (MW) + `matched_intervals`.
    Reproduce the fixture: errors +200,−200,+100 → MAE 166.7, RMSE ≈173.2, Bias +33.3. (MAPE = future/optional.)
- [ ] Schemas (`app/models/schemas.py`): validate **`decision_date ∈ 1–31 Jan 2026`**; responses echo
      `decision_date` + derived `delivery_date`; error shape per `docs/05`.
- [ ] API routes (primary param `decision_date`): `GET /api/health`, `GET /api/forecasts`,
      `GET /api/forecasts/history`, `GET /api/accuracy`. Routes validate → call services → shape JSON;
      **no selection/metric math in routes.**
- [ ] Error handling: one shape `{error:{code,message,details}}`; validation→400, out-of-scope→422,
      no-data→404, upstream timeout/fail→504/502.
- [ ] Tests (`backend/tests/`, per `docs/07`): selection (latest≤cutoff; excludes later; no-eligible),
      metrics fixture, join (missing/dup/misaligned, no zero-fill); integration route happy-path + error
      contracts (Elexon mocked); out-of-scope→422, invalid→400.

## ⛒ Gate — backend tests must pass before Phase B
- [ ] `docker compose run --rm backend pytest` all green (incl. metrics fixture).
- [ ] `GET /api/accuracy?decision_date=2026-01-15` (→ delivery 2026-01-16) returns sensible metrics on real data.
- [ ] Look-ahead guard verified; `decision_date` outside Jan 2026 → 422.

## Phase B — Frontend (React)  [~5h]  — build to `docs/06-frontend.md` (authoritative)
- [ ] Scaffold `frontend/` (Vite + React + TS; Recharts); `frontend/Dockerfile`; add `frontend` to compose.
      API client reads `VITE_API_URL`, normalizes error shape, cancels stale requests, no silent mock fallback.
- [ ] Shell: light-theme analytics dashboard; sidebar (Overview, Forecast Analysis, Accuracy Analysis,
      Data & Methodology); header with selected period + API status + last-update. Components:
      `DateIntervalSelector`, `CutoffControl`, `GenerationChart`, `MetricCards`, `ErrorTable`, `StateBoundary`.
- [ ] View 1 — Forecast Dashboard: pick **decision date**; show derived delivery date + cutoff prominently;
      forecast MW per 30-min interval w/ tooltips; distinguish `start_time` vs `publish_time`;
      vintage-history panel w/ eligibility flag; missing intervals shown explicitly.
- [ ] View 2 — Accuracy: forecast vs actual on shared MW axis; error-over-time chart w/ zero line;
      MAE/RMSE/Bias + matched-interval cards; sortable error table.
- [ ] All states explicit (loading/empty/stale/partial/error); accessibility (keyboard, focus, contrast,
      legends not color-only). Frontend tests (Vitest + RTL): component states + API-client error handling.

## Phase C — Integrate  [~1h]
- [ ] `docker compose up --build` runs backend + frontend; frontend → local backend; CORS allows dev origin.
- [ ] Walk both views end-to-end on real data; hand-spot-check one day's metrics. App "complete" when both work.

## Finishing steps  [~3h]  ← *video is where evaluation starts; do not submit without it*
- [ ] Deploy backend → **Render** (Docker web service); frontend → **Vercel** (`VITE_API_URL`); backend
      CORS → Vercel origin. Warm Render before recording; **verify live URL in incognito**.
- [ ] README: dirs/files, how to run (local + Docker), **live URL**, methodology + metric defs, assumptions/
      limitations, **AI-tool disclosure** (required). Optional CI (test on push).
- [ ] Video (unlisted YouTube, ≤10 min): Part 1 ≤5 min client pitch (impress); Part 2 ≤5 min tech review
      (architecture, design, codebase, dev practices).
- [ ] Public GitHub repo (anonymous random name). Fill submission form; open every URL in incognito to verify.

---

### Key decisions (locked)
1. **Scope:** decision-anchored — decisions Jan 1–31 2026 → delivery Jan 2 – Feb 1 2026. Selector = `decision_date`.
2. **Forecast selection:** latest WINDFOR vintage with `publish_time ≤ cutoff(d)`; no look-ahead; no back-fill.
3. **Cutoff:** 12:00 Europe/London on decision day — **provisional assumption**, configurable; never silently midnight.
4. **Timezone:** compute in UTC; apply cutoff + display in Europe/London (GMT/BST via the zone).
5. **Persistence:** no database — parquet cache + pandas in-memory.
6. **Deploy:** backend → Render, frontend → Vercel.
7. **Scope honesty:** quantify wind forecast uncertainty only; do **not** claim a shortfall/purchase quantity.
