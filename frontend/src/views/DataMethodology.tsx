import { api } from "../api/client";

export function DataMethodology() {
  return (
    <section className="prose">
      <h2>Data &amp; methodology</h2>

      <h3>Data sources (Elexon BMRS)</h3>
      <ul>
        <li>
          <strong>Actuals — FUELHH</strong> (fuelType = WIND): half-hourly national wind generation (MW).
        </li>
        <li>
          <strong>Forecasts — WINDFOR</strong>: wind generation forecasts (MW), each with a publication time.
          Multiple vintages exist per delivery interval.
        </li>
      </ul>

      <h3>Scope (decision-anchored)</h3>
      <p>
        In scope are purchase decisions made 1–31 January 2026. The market is day-ahead, so each decision is
        for next-day delivery — delivery days span 2 January – 1 February 2026.
      </p>

      <h3>Point-in-time correctness</h3>
      <p>
        For each decision we use only forecasts available at the time: the latest WINDFOR vintage published on
        or before the purchasing cutoff. Later vintages are never used to score an earlier decision
        (look-ahead bias). The cutoff defaults to <strong>12:00 Europe/London on the decision day</strong> — a
        provisional assumption, not an official market deadline — and is configurable.
      </p>

      <h3>Resolution alignment</h3>
      <p>
        WINDFOR is published hourly while FUELHH actuals are half-hourly. Actuals are aggregated to the hourly
        forecast grid by mean before comparison — a documented alignment, not interpolation. Missing intervals
        are excluded and counted, never treated as zero.
      </p>

      <h3>Metrics (MW)</h3>
      <ul>
        <li>
          <strong>Error</strong> = forecast − actual (positive = over-forecast).
        </li>
        <li>
          <strong>MAE</strong> = mean absolute error; <strong>RMSE</strong> = root mean squared error;{" "}
          <strong>Bias</strong> = mean signed error.
        </li>
        <li>Every metric is reported with the number of matched intervals used.</li>
      </ul>

      <p className="prose__foot">
        API base: <code>{api.baseUrl}</code> · interactive API docs at <code>{api.baseUrl}/docs</code>.
      </p>
    </section>
  );
}
