# 01 — Project Overview

## Business objective

A UK energy utility must buy electricity on the **day-ahead market** to serve consumer demand. Wind generation is weather-dependent and must be *forecast* a day ahead, because purchasing decisions are made before the delivery day. The residual demand that the utility must procure from other sources (e.g. thermal plants) depends directly on how much wind is expected — and on how wrong that expectation might be.

This application supports the purchasing team by making the **latest eligible wind forecast** visible at decision time and by **quantifying how accurate those forecasts have historically been**, so decisions can account for forecast error.

## Target users

Members of the day-ahead power-purchasing team. Assume domain-literate but not developers: the UI uses plain language, explicit units (MW), and clearly labelled timestamps.

## What the product does

1. **Forecast dashboard** — shows forecast wind generation per 30-minute delivery interval, with delivery time and forecast publication time, selecting the latest forecast eligible by the purchasing cutoff and allowing inspection of earlier forecast vintages.
2. **Accuracy analysis** — compares the eligible forecast against actual generation, plots both, tabulates per-interval error, and reports MAE, RMSE and bias (all in MW) with the count of matched intervals.

## What the product explicitly does NOT do

Per the scope limitation in the requirements (and reflected in the UI copy):

- It does **not** calculate the actual electricity shortfall or a recommended purchase quantity. The available data (national wind only) lacks consumer demand and other generation availability needed for that.
- Any illustrative procurement figure, if ever added, must be labelled **illustrative** and must list the additional validated inputs it would require. The baseline product contains no such figure.

## Success criteria (functional)

- A purchasing-team user can select a January 2026 decision/delivery date and immediately see the forecast that would have been available at the configured cutoff.
- The same user can see quantified forecast error for that period, computed with point-in-time-correct forecasts, excluding unmatched intervals, with the matched-interval count shown.
- All loading, empty, stale, and error conditions are visible rather than silent.
