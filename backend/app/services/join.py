"""Join eligible forecasts to actuals by delivery interval (see docs/04, docs/10).

Resolution note (verified from the data): WINDFOR forecasts are published at
**hourly** resolution, while FUELHH actuals are **half-hourly**. We therefore
aggregate actuals onto the forecast's hourly grid by mean (each hourly bin
[HH:00, HH+1:00) averages its two half-hour values) and compare like-for-like.
This is a documented alignment, not interpolation or zero-filling.

Only intervals present on both sides after alignment are "matched" and enter
metrics. Unmatched intervals are counted (missing_forecast / missing_actual),
never zero-filled.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from app.time_utils import delivery_window_utc


def _actuals_on_forecast_grid(actuals_window: pd.DataFrame) -> pd.DataFrame:
    """Aggregate half-hourly actuals to the hourly forecast grid by mean."""
    if actuals_window.empty:
        return pd.DataFrame(columns=["start_time", "actual_mw"])
    tmp = actuals_window[["start_time", "generation_mw"]].copy()
    tmp["start_time"] = tmp["start_time"].dt.floor("h")
    return (
        tmp.groupby("start_time", as_index=False)["generation_mw"]
        .mean()
        .rename(columns={"generation_mw": "actual_mw"})
    )


def join_forecast_actual(
    selected: pd.DataFrame,
    actuals: pd.DataFrame,
    delivery_day_: date,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """Return (merged_outer, matched_only, counts).

    - merged_outer: every hourly interval seen on either side, sorted by
      start_time, NaN where a side is missing, with error columns where both exist.
    - matched_only: rows where both forecast and (hour-aggregated) actual exist.
    - counts: {"missing_forecast": int, "missing_actual": int}.
    """
    start, end = delivery_window_utc(delivery_day_)
    act_window = actuals.loc[(actuals["start_time"] >= start) & (actuals["start_time"] < end)]
    act = _actuals_on_forecast_grid(act_window)

    fc = (
        selected[["start_time", "forecast_mw"]]
        if not selected.empty
        else pd.DataFrame(columns=["start_time", "forecast_mw"])
    )

    merged = pd.merge(fc, act, on="start_time", how="outer").sort_values("start_time").reset_index(drop=True)

    has_fc = merged["forecast_mw"].notna()
    has_act = merged["actual_mw"].notna()
    counts = {
        "missing_forecast": int((~has_fc & has_act).sum()),
        "missing_actual": int((has_fc & ~has_act).sum()),
    }

    merged["error_mw"] = merged["forecast_mw"] - merged["actual_mw"]
    merged["abs_error_mw"] = merged["error_mw"].abs()

    matched = merged.loc[has_fc & has_act].copy().reset_index(drop=True)
    return merged, matched, counts
