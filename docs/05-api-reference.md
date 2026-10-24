# 05 — API Reference

> Planned contract. Paths and schemas may be refined during implementation; the
> live/authoritative schema will be the FastAPI-generated OpenAPI spec at `/docs`.

## Conventions

- Base path: `/api`. Versioning via path (e.g. `/api/v1/...`) may be introduced; documented here unversioned for brevity.
- All times are **ISO 8601 UTC** (`2026-01-15T12:00:00Z`).
- Generation values are **MW** (float).
- **Scope is decision-anchored.** The primary parameter is `decision_date`, which must fall within **1–31 January 2026**; out-of-scope dates return `422`. The delivery day is derived as **`decision_date + 1`** (day-ahead) and echoed in responses.

## Error response shape

All non-2xx responses share one shape:

```json
{
  "error": {
    "code": "OUT_OF_SCOPE_DATE",
    "message": "decision_date must fall within January 2026.",
    "details": { "parameter": "decision_date", "value": "2026-02-01" }
  }
}
```

| HTTP | `code` examples | When |
|---|---|---|
| 400 | `INVALID_PARAMETER` | Malformed/missing parameter |
| 422 | `OUT_OF_SCOPE_DATE` | Syntactically valid but outside 1–31 January 2026 |
| 404 | `NO_DATA` | No data for a valid in-scope request |
| 502 | `UPSTREAM_UNAVAILABLE` | Elexon failure encountered during (re)ingestion |
| 504 | `UPSTREAM_TIMEOUT` | Elexon timeout during (re)ingestion |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

## Endpoints

### `GET /api/health`
Liveness/readiness check.

**200**
```json
{ "status": "ok", "data_loaded": true, "intervals_cached": 1488 }
```

---

### `GET /api/forecasts`
Eligible (point-in-time-correct) forecast series for a decision date, covering the derived delivery day (`decision_date + 1`).

**Query parameters**

| Name | Type | Required | Notes |
|---|---|---|---|
| `decision_date` | date (`YYYY-MM-DD`) | yes | Must be in 1–31 January 2026 |
| `cutoff` | datetime (ISO UTC) | no | Overrides the configured default cutoff (default: 12:00 Europe/London on the decision day) |

**200**
```json
{
  "decision_date": "2026-01-15",
  "delivery_date": "2026-01-16",
  "cutoff": "2026-01-15T12:00:00Z",
  "unit": "MW",
  "intervals": [
    { "start_time": "2026-01-16T00:00:00Z", "forecast_mw": 1200.0, "publish_time": "2026-01-15T10:30:00Z" }
  ],
  "intervals_count": 48,
  "intervals_missing_forecast": 0
}
```

Each interval reports the `publish_time` of the vintage actually used, so eligibility is auditable.

---

### `GET /api/forecasts/history`
All available forecast vintages for a delivery interval (or the whole derived delivery day), for inspecting earlier forecasts and their eligibility at the cutoff.

**Query parameters**

| Name | Type | Required | Notes |
|---|---|---|---|
| `decision_date` | date | yes | 1–31 January 2026 (delivery day derived) |
| `start_time` | datetime (ISO UTC) | no | Narrow to one interval |

**200**
```json
{
  "start_time": "2026-01-16T00:00:00Z",
  "cutoff": "2026-01-15T12:00:00Z",
  "unit": "MW",
  "vintages": [
    { "publish_time": "2026-01-14T22:00:00Z", "forecast_mw": 1150.0, "eligible": true },
    { "publish_time": "2026-01-15T10:30:00Z", "forecast_mw": 1200.0, "eligible": true },
    { "publish_time": "2026-01-15T16:00:00Z", "forecast_mw": 1180.0, "eligible": false }
  ]
}
```

`eligible` marks whether each vintage was published on or before the cutoff for the selected decision date.

---

### `GET /api/accuracy`
Forecast-vs-actual series plus accuracy metrics for one decision date (or a range of decision dates) within scope.

**Query parameters**

| Name | Type | Required | Notes |
|---|---|---|---|
| `decision_date` | date | yes* | *Either `decision_date` or `start`+`end` |
| `start` / `end` | date | yes* | Inclusive range of **decision dates** within 1–31 January 2026 |
| `cutoff` | datetime (ISO UTC) | no | Overrides default cutoff |

**200**
```json
{
  "decision_range": { "start": "2026-01-15", "end": "2026-01-15" },
  "delivery_range": { "start": "2026-01-16", "end": "2026-01-16" },
  "cutoff": "2026-01-15T12:00:00Z",
  "unit": "MW",
  "metrics": { "mae": 166.7, "rmse": 173.2, "bias": 33.3, "matched_intervals": 48 },
  "series": [
    {
      "start_time": "2026-01-16T00:00:00Z",
      "forecast_mw": 1200.0,
      "actual_mw": 1000.0,
      "error_mw": 200.0,
      "abs_error_mw": 200.0
    }
  ],
  "excluded": { "missing_forecast": 0, "missing_actual": 0 }
}
```

`metrics.matched_intervals` is always present. Excluded intervals are counted, never zero-filled (see [04 — Methodology](04-methodology.md)).

## Documentation & secrets

- Interactive OpenAPI docs are served at `/docs` (Swagger) and the schema at `/openapi.json`.
- No secrets or credentials appear in source control; configuration is via environment variables (see [09 — Local Development](09-local-development.md)).
