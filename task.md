# REint Full Stack SWE Challenge — Tasklist

> **Status (at a glance):** Phases 0 / A / B / C ✅ · deployed ✅ · tests 23/23 ✅ (backend 16, frontend 7).
> **Live:** app https://gbk-v1.vercel.app · API https://windportal-backend.onrender.com
> **Left to do:** incognito visual check · demo video · (optional) anonymous repo name + confirm repo public · submission form.


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

## Phase 0 — Reconcile & save  [~0.5h]  ✅
- [x] Reconcile this `task.md` with all confirmed decisions (this rewrite).
- [x] Correct `docs/03`, `docs/04`, `docs/05`, `docs/11` to decision-anchored scope + `decision_date` param.
- [x] `git init`; add `.gitignore`; commit `require.md`, `task.md`, `docs/`, and the original `.docx`.

## Phase A — Backend  [~6h]  ✅ complete (16/16 tests pass; verified on real Jan-2026 data)
> Finding: WINDFOR is **hourly**, FUELHH **half-hourly** — actuals are aggregated to the hourly
> forecast grid by mean (documented alignment, not interpolation). Sample: decision 2026-01-15 →
> MAE 858.7, RMSE 1084.8, Bias +396.6 MW, 24/24 matched.
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

## ⛒ Gate — backend tests must pass before Phase B  ✅ PASSED
- [x] pytest all green (16/16, incl. metrics fixture).
- [x] `GET /api/accuracy?decision_date=2026-01-15` (→ delivery 2026-01-16) returns sensible metrics on real data.
- [x] Look-ahead guard verified; `decision_date` outside Jan 2026 → 422; invalid param → 400; `/docs` renders.

## Phase B — Frontend (React)  [~5h]  ✅ complete (build clean, 7/7 tests pass)  — per `docs/06-frontend.md`
- [x] Scaffold `frontend/` (Vite + React + TS; Recharts); `frontend/Dockerfile`; add `frontend` to compose.
      API client reads `VITE_API_URL`, normalizes error shape, cancels stale requests, no silent mock fallback.
- [x] Shell: light-theme analytics dashboard; sidebar (Overview, Forecast Analysis, Accuracy Analysis,
      Data & Methodology); header with selected period + API status. Components: DecisionControls,
      GenerationChart, ErrorChart, MetricCards, ErrorTable, StateBoundary, Sidebar, Header.
- [x] View 1 — Forecast Dashboard: pick **decision date**; derived delivery date + cutoff shown; hourly
      forecast chart w/ tooltips; `start_time` vs `publish_time` distinguished; vintage-history panel w/
      eligibility pills; missing intervals shown explicitly.
- [x] View 2 — Accuracy: forecast vs actual on shared MW axis; error-over-time chart w/ zero line;
      MAE/RMSE/Bias + matched-interval cards; sortable error table.
- [x] All states explicit (loading/empty/error); accessibility basics. Frontend tests (Vitest + RTL):
      component states + API-client error handling.

## Phase C — Integrate  [~1h]  ✅ verified (HTTP/integration level)
- [x] `docker compose.yml` runs backend + frontend; frontend → local backend; CORS allows dev origin.
- [x] Verified: frontend serves (200) + JS asset (200); backend CORS allows `localhost:5173`; `/api/*` returns
      real data; both test suites pass. (Browser screenshot not possible in this session — no browser tooling.)

## Finishing steps  [~3h]  ← *video is where evaluation starts; do not submit without it*
- [x] Deploy backend → **Render** (live: https://windportal-backend.onrender.com); frontend → **Vercel**
      (live: https://gbk-v1.vercel.app); `VITE_API_URL` set; backend CORS → Vercel origin. Verified: health
      ok, cross-origin data calls work. (Render free tier cold-starts ~50s after idle — warm before recording.)
- [x] README: dirs/files, how to run (local + Docker), **live URLs**, methodology + metric defs,
      assumptions/limitations, **AI-tool disclosure**.
- [x] Code pushed to GitHub: https://github.com/nilesh-commits/GBK_v1 (branch main).
- [ ] **Open the live app in incognito** and click through all 3 views (visual check — not automatable here).
- [ ] Video (unlisted YouTube, ≤10 min): Part 1 ≤5 min client pitch (impress); Part 2 ≤5 min tech review
      (architecture, design, codebase, dev practices).
- [ ] Repo name is **not anonymous** (`GBK_v1`) — brief wanted a random name; rename/re-push if it matters.
- [ ] Make the GitHub repo **public** (required for submission) if not already.
- [ ] Fill the submission form; open every submitted URL in incognito to verify access.
- [ ] (Optional) CI: run tests on push.

---

### Key decisions (locked)
1. **Scope:** decision-anchored — decisions Jan 1–31 2026 → delivery Jan 2 – Feb 1 2026. Selector = `decision_date`.
2. **Forecast selection:** latest WINDFOR vintage with `publish_time ≤ cutoff(d)`; no look-ahead; no back-fill.
3. **Cutoff:** 12:00 Europe/London on decision day — **provisional assumption**, configurable; never silently midnight.
4. **Timezone:** compute in UTC; apply cutoff + display in Europe/London (GMT/BST via the zone).
5. **Persistence:** no database — parquet cache + pandas in-memory.
6. **Deploy:** backend → Render, frontend → Vercel.
7. **Scope honesty:** quantify wind forecast uncertainty only; do **not** claim a shortfall/purchase quantity.
