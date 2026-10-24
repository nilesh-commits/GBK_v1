# 07 — Testing

> Planned test strategy. Tests are not yet written.

## Strategy

- **Unit tests** for isolated logic: forecast selection, metric math, join behaviour, parameter validation. These require no network and no running server.
- **Integration tests** for API/data workflows: route → service → cached data, including error contracts and upstream-failure handling (Elexon calls mocked/stubbed).
- **Frontend tests** for key component states (loading/empty/stale/error) and the API client's error normalization.

Backend: `pytest`. Frontend: the Vite-native test runner (e.g. Vitest) + React Testing Library.

## Required test cases (from `require.md` §9)

### Forecast selection
- Selects the **latest** eligible forecast by `publishTime` ≤ cutoff.
- **Excludes** any forecast published after the cutoff (look-ahead guard).
- Interval with no eligible forecast → excluded, counted, not back-filled.

### Metrics
- MAE, RMSE, and bias computed correctly against a known fixture.
  - Fixture (from [04 — Methodology](04-methodology.md)): errors `+200, −200, +100` → **MAE 166.7**, **RMSE ≈ 173.2**, **Bias +33.3** MW.
- `matched_intervals` count correct and present.

### Join & data quality
- Join forecasts↔actuals by delivery interval.
- Missing, duplicate, or mismatched timestamps handled (see [10 — Edge Cases](10-edge-cases-and-data-quality.md)).
- Missing forecast / unavailable actual → interval excluded, **never** zero-filled.

### API / validation
- Invalid query parameters → `400`.
- Out-of-scope dates (outside January 2026) → `422`.
- Elexon timeout / failure / malformed data during ingestion → mapped to `504`/`502`/handled error, not a crash.
- Response contracts match [05 — API Reference](05-api-reference.md).

### Frontend
- Loading, empty, stale, and error states render for each view.
- API client maps the standard error shape to user-facing messages.

## Running tests

Exact commands are finalized with implementation; intended entry points:

```bash
# Backend (from repo root)
docker compose run --rm backend pytest        # or: cd backend && pytest

# Frontend
docker compose run --rm frontend npm test      # or: cd frontend && npm test
```

See [09 — Local Development](09-local-development.md) for environment setup.
