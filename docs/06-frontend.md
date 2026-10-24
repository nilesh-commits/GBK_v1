# 06 — Frontend

> Planned design. No components are implemented yet.

## Stack

- **React** with **Vite** (fast dev server, simple static build for Vercel).
- Charting via a React charting library (e.g. Recharts) for the time-series and error views.
- A thin API client wraps `fetch`, reads the backend base URL from `VITE_API_URL`, and normalizes the error-response shape from [05 — API Reference](05-api-reference.md).

## Views

### View 1 — Forecast Dashboard (the "pitch" screen)
- Forecast wind generation (MW) per 30-minute interval for the selected delivery date.
- Shows both **delivery time** (`start_time`) and the **publication time** (`publish_time`) of the vintage used.
- Uses the latest forecast eligible by the purchasing **cutoff**; the cutoff is visible and adjustable.
- Lets the user **inspect earlier vintages** for an interval (drawing on `/api/forecasts/history`).
- Date/interval filters restricted to January 2026.

### View 2 — Accuracy Analysis
- Forecast and actual plotted on the **same chart** for comparison.
- Metric summary cards: **MAE**, **RMSE**, **Bias** (all MW), plus **matched-interval count**.
- Detailed **error table**: delivery time, forecast, actual, signed error, absolute error.
- Date / range selection across January 2026.

## Reusable components (planned)

| Component | Role |
|---|---|
| `DateIntervalSelector` | Scope-restricted date + interval picking |
| `CutoffControl` | Displays/edits the purchasing cutoff |
| `GenerationChart` | Time-series (forecast, and forecast-vs-actual) |
| `MetricCards` | MAE / RMSE / Bias / N |
| `ErrorTable` | Per-interval error detail |
| `StateBoundary` | Loading / empty / stale / error rendering |

## UI states (all explicit, none silent)

| State | Trigger | Shown as |
|---|---|---|
| **Loading** | Request in flight | Skeleton/spinner in the affected panel |
| **Empty** | Valid request, no data | Clear "no data for this selection" message |
| **Stale** | Served data older than a freshness marker | Visible "last updated"/stale badge |
| **Error** | Non-2xx from API | Message derived from `error.code`/`message`, with retry |

## State management & performance

- Keep client state minimal: selected date/range, cutoff, fetched payloads. Prefer local/component state and a small data-fetching hook over a heavy global store.
- Memoize derived chart/table data and avoid unnecessary re-renders (stable keys, `useMemo` for transforms). No performance *targets* are claimed unless measured (see [11 — Assumptions](11-assumptions-and-limitations.md)).

## Responsiveness

Designed for common desktop sizes first; layout remains usable on smaller screens (stacked panels, horizontally scrollable table).
Visual Design & Layout

Use a professional energy analytics dashboard design with a clean light theme, dark navy typography, restrained green accents, and consistent spacing.

Include a responsive sidebar with Overview, Forecast Analysis, Accuracy Analysis, and Data & Methodology navigation.

Add a page header showing the selected period, backend/API status, and last successful data update.

Prioritize the forecast chart and key metrics. Avoid excessive decoration, oversized headers, and unnecessary animations.

Use reusable cards, consistent typography, accessible contrast, and clear visual hierarchy.

Forecast Dashboard Enhancements

Display the selected delivery date and the purchasing cutoff prominently above the main chart.

Show forecast generation in MW for each 30-minute interval, with interactive tooltips and a clearly labelled time axis.

Distinguish delivery time (start_time) from forecast publication time (publish_time) throughout the interface.

Provide a forecast-vintage history panel for inspecting earlier publications for a selected delivery interval.

Indicate whether each vintage was eligible at the selected cutoff.

Display missing intervals explicitly rather than interpolating or treating missing values as zero.

Cutoff & Timezone Handling

Use a configurable provisional default of 12:00 Europe/London on D-1, pending client confirmation.

Clearly label the default as an assumption, not an official market deadline.

Display the cutoff timezone and convert timestamps consistently.

Handle GMT/BST transitions using the Europe/London timezone.

Ensure the selected forecast vintage was published at or before the cutoff.

Refresh the displayed forecast when the selected date, interval, or cutoff changes.

Accuracy Visualization Enhancements

Show forecast and actual generation on the same chart using distinguishable series and a shared MW axis.

Include an error-over-time chart with a zero reference line.

Define signed error as Forecast − Actual; positive bias indicates over-forecasting on average.

Calculate MAE, RMSE, and Bias using only valid matched forecast/actual intervals.

Display the matched-interval count and clearly identify missing observations.

Provide sorting and readable number formatting in the error table.

API Integration & Data Integrity

Centralize API requests in a reusable client and follow the contracts in 05-api-reference.md.

Support request cancellation when users change filters rapidly.

Prevent outdated responses from overwriting results for newer selections.

Handle network failures, malformed payloads, and non-2xx responses with actionable messages.

Use backend-provided freshness metadata or a documented freshness rule to determine whether data is stale.

Never fabricate production data, timestamps, or accuracy metrics.

Keep mock data isolated and visibly labelled if used during development.

Accessibility & Interaction

Ensure keyboard navigation, visible focus states, semantic labels, and accessible color contrast.

Provide meaningful labels and legends for charts; do not rely on color alone to communicate meaning.

Make all visible controls functional, or clearly disable them with an explanation.

Ensure tables remain readable on mobile through horizontal scrolling and appropriate column sizing.

Provide clear retry actions for failed requests.

Testing & Acceptance Criteria

Test cutoff eligibility, forecast-vintage selection, and timezone boundaries.

Test metric calculations, missing intervals, and invalid data.

Test loading, empty, stale, partial-data, and error states.

Verify that all date and interval selections remain within January 2026.

Verify that forecast and actual values align by delivery interval.

Verify the frontend works with the configured backend URL and does not silently fall back to mock data.

Document assumptions and known limitations in 11-assumptions-and-limitations.md.