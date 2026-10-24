# 03 — Data Sources

All core data comes from the **Elexon BMRS API**. No other data source is used for forecast or accuracy analysis.

## Actual wind generation — FUELHH

- **Endpoint:** `https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream`
- **Filter:** use only records where `fuelType = WIND`.

| Field | Meaning | Use |
|---|---|---|
| `startTime` | Target delivery interval start, 30-minute resolution | Join key to forecasts |
| `generation` | Actual wind generation (MW) | "Actual" series |

## Forecast wind generation — WINDFOR

- **Endpoint:** `https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream`

| Field | Meaning | Use |
|---|---|---|
| `startTime` | Target delivery interval | Join key to actuals |
| `publishTime` | Time the forecast was published | Forecast **vintage**; drives eligibility by cutoff |
| `generation` | Forecast wind generation (MW) | "Forecast" series |

A single delivery `startTime` typically has **multiple forecast rows** with different `publishTime` values (successive vintages). Selecting the correct one is the core of the methodology — see [04 — Methodology](04-methodology.md).

## Units and conventions

- **Units:** generation values are treated as **MW**. All reported metrics are in MW. If ingestion observes values inconsistent with MW, that is flagged (see [10 — Edge Cases](10-edge-cases-and-data-quality.md)), not silently converted.
- **Interval resolution (verified from the data):** FUELHH **actuals are half-hourly** (48 intervals/day; `startTime` minutes 00 and 30). WINDFOR **forecasts are hourly** (`startTime` minute 00 only; ~24 target intervals/day). The brief describes both at 30-min resolution, but the in-scope WINDFOR data is hourly — confirmed by inspecting the January 2026 payload (all 17,688 forecast rows have minute 00). Forecasts and actuals are therefore compared on the forecast's **hourly grid**: actuals are aggregated to each hour by mean (see [04 — Methodology](04-methodology.md)). January 2026 has no DST change, so all in-scope days are full days.
- **Time zone:** Elexon timestamps are handled explicitly in **UTC** internally. UK local time (GMT in January) is used only for display labels. Conversions are explicit; see [04 — Methodology](04-methodology.md) and [11 — Assumptions](11-assumptions-and-limitations.md).

## Scope filter

Scope is **decision-anchored**: the in-scope events are purchase **decisions made 1–31 January 2026**. Because the market is day-ahead, a decision made on day *d* is for **delivery on day *d*+1**, so the relevant **delivery days span 2 January – 1 February 2026**.

- **Actuals:** delivery intervals for **2026-01-02 … 2026-02-01**.
- **Forecasts:** WINDFOR vintages **published across January 2026** that target those delivery days. (No late-December vintages: a 1 January delivery was decided in December, which is out of scope.) Ingestion retains all vintages so the configured cutoff always has eligible forecasts to choose from; the exact window is documented in the ingestion script.

## Ingestion notes

- The Elexon adapter requests the in-scope window (actuals for delivery days 2026-01-02 … 2026-02-01; WINDFOR vintages published across January 2026), filters `fuelType=WIND` for actuals, and retains **all** forecast vintages (never pre-collapsed to one per interval — vintage history is a product feature).
- Normalized output schema written to parquet:
  - `actuals(start_time: datetime[utc], generation_mw: float)`
  - `forecasts(start_time: datetime[utc], publish_time: datetime[utc], generation_mw: float)`
- Timeouts, retries, and malformed-response handling are covered in [10 — Edge Cases](10-edge-cases-and-data-quality.md).
