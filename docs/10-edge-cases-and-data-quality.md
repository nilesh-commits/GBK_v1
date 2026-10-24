# 10 — Edge Cases & Data Quality

Handling is explicit and documented. The governing rule: **never silently treat missing values as zero**, and **exclude unmatched intervals from accuracy metrics** unless a documented method says otherwise.

## Data-quality cases

| Case | Handling |
|---|---|
| **Multiple forecasts for one interval** | Expected (vintages). Selection picks latest `publishTime` ≤ cutoff; full history available via `/api/forecasts/history`. |
| **No eligible forecast before cutoff** | Interval has no forecast; excluded from metrics, counted in `excluded.missing_forecast`, surfaced in UI. Not back-filled. |
| **Actual not yet available** | Interval excluded from metrics, counted in `excluded.missing_actual`. Forecast can still be shown on the dashboard. |
| **Duplicate 30-min intervals** | De-duplicated deterministically (e.g. keep one record per `(start_time, publish_time)`); duplicates logged. |
| **Missing 30-min intervals** | Not synthesized. Absent from matched set; reflected in counts. |
| **Forecast/actual timestamps don't align** | Only exact interval-key matches are joined; non-aligned intervals are unmatched, not approximated. |
| **Missing or invalid generation value** | Row treated as missing (not `0`); excluded; logged. |
| **Unexpected units / timestamp convention** | Flagged during ingestion and logged; not silently converted. Assumptions documented in [03 — Data Sources](03-data-sources.md). |
| **Forecast/actual resolution mismatch** | Verified real case: WINDFOR is hourly, FUELHH half-hourly. Actuals are aggregated to the hourly forecast grid by mean before joining — a documented alignment, not interpolation (see [04 — Methodology](04-methodology.md)). |
| **Purchase date outside January 2026** | Rejected at the API with `422 OUT_OF_SCOPE_DATE`. |

## Upstream (Elexon) failure handling

Elexon is contacted during **ingestion**, not on the request path, which isolates request-time behaviour from upstream instability.

| Condition | Handling |
|---|---|
| **Timeout** | Bounded timeout; limited retries with backoff; surfaced as `504 UPSTREAM_TIMEOUT` if ingestion is triggered via API. |
| **HTTP/transport failure** | Limited retries; then `502 UPSTREAM_UNAVAILABLE`; last good parquet cache remains servable. |
| **Malformed / unexpected schema** | Validated on parse; offending records rejected and logged; a schema-shape change fails loudly rather than corrupting the cache. |

## Logging & observability

- Ingestion logs: records fetched, filtered, de-duplicated, rejected, and written.
- Request logs: parameters, matched/excluded counts, errors.
- Only capabilities actually implemented are claimed as present (see [11 — Assumptions](11-assumptions-and-limitations.md)); no monitoring or alerting is asserted unless built and verified.
