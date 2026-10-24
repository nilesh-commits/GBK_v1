# 11 — Assumptions, Limitations & Future Work

## Open questions needing client confirmation

| # | Question | Current handling |
|---|---|---|
| 1 | **What is the exact purchasing cutoff** (gate-closure time) for the day-ahead decision? | Not supplied. Implemented as a **configurable** value defaulting to **12:00 Europe/London on the decision day**; **not** silently assumed to be midnight, and labelled a provisional assumption rather than an official market deadline. See [04 — Methodology](04-methodology.md). |
| 2 | Is the day-ahead decision made for a whole delivery day at one cutoff, or per block? | Modelled per decision day *d* (one cutoff on day *d*, for delivery day *d*+1), configurable. To confirm. |
| 3 | Preferred UK display timezone handling across any edge days? | Compute in UTC; apply cutoff and display in **Europe/London** (GMT in January) via the zone, not a fixed offset. January 2026 has no DST change, so all in-scope days have 48 intervals. |

## Documented assumptions

- **Units** are MW as provided by Elexon; no conversion applied. Inconsistencies are flagged, not converted ([03 — Data Sources](03-data-sources.md)).
- **Resolution:** WINDFOR is hourly and FUELHH half-hourly (verified from the January 2026 data, contrary to the brief's "30-min" description of both). Accuracy is computed on the forecast's hourly grid, with actuals aggregated to each hour by mean — a documented alignment, not interpolation. If the client expects half-hourly forecast scoring, a half-hourly WINDFOR source would be required.
- **Default cutoff** is 12:00 Europe/London on the decision day — an explicit assumption carried in configuration and labelled provisional pending answer to open question #1. It is visible in API responses (`cutoff` field) so any score can be re-derived under a different cutoff.
- **Scope is decision-anchored:** decisions 1–31 January 2026 → delivery days 2 January – 1 February 2026. Ingestion covers FUELHH actuals through 2026-02-01 and WINDFOR vintages published across January 2026. (No late-December vintages — a 1 January delivery was decided in December, out of scope.)

## Scope limitations (hard)

The datasets provide **national wind actuals and forecasts only**. They do **not** include consumer demand or other generation availability. Therefore:

- The product quantifies **wind forecast uncertainty** only.
- It **must not** claim to compute the actual electricity shortfall or a recommended purchase quantity.
- Any illustrative procurement figure, if ever added, must be explicitly labelled **illustrative** and must enumerate the additional validated inputs required. The baseline product includes no such figure.

## Known limitations

- Accuracy is evaluated only over the matched intervals present in both datasets; intervals missing from either side are excluded and counted, not estimated.
- No performance targets or monitoring/alerting capabilities are claimed unless implemented and verified.
- Deployment targets are chosen (backend → Render, frontend → Vercel) but nothing is deployed yet; no live URL is claimed until deployment is verified in incognito ([08 — Deployment](08-deployment.md)).

## Future work (not implemented)

- Configurable per-block cutoffs if the client confirms block-level decisions.
- Additional error metrics (e.g. MAPE / skill score vs. a persistence baseline) if requested.
- Wider date ranges beyond January 2026 once scope expands.
- Incorporating demand and non-wind generation to move from *forecast uncertainty* toward an *illustrative residual-procurement* view — only with validated inputs and clear labelling.

## AI tool disclosure (for the README)

The README must explicitly name any AI tools used and how they assisted (or state accurately that none were used), per `require.md` §14. This documentation set was drafted with AI assistance (Claude); record the specifics in the README at submission time.
