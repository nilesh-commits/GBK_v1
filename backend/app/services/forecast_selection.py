"""Point-in-time-correct forecast selection (see docs/04-methodology.md).

For a decision day d (cutoff on d), over delivery day d+1's intervals, pick the
latest WINDFOR vintage with publish_time <= cutoff. Intervals with no eligible
vintage are simply absent (never back-filled). Pure pandas; no HTTP, no Elexon.
"""
from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from app.time_utils import delivery_window_utc

_SELECTED_COLS = ["start_time", "forecast_mw", "publish_time"]


def select_eligible(forecasts: pd.DataFrame, delivery_day_: date, cutoff_utc: datetime) -> pd.DataFrame:
    """Return one eligible forecast row per delivery interval (latest publish <= cutoff)."""
    start, end = delivery_window_utc(delivery_day_)
    cutoff = pd.Timestamp(cutoff_utc)
    mask = (
        (forecasts["start_time"] >= start)
        & (forecasts["start_time"] < end)
        & (forecasts["publish_time"] <= cutoff)
    )
    df = forecasts.loc[mask]
    if df.empty:
        return pd.DataFrame(columns=_SELECTED_COLS)
    idx = df.groupby("start_time")["publish_time"].idxmax()
    out = (
        df.loc[idx]
        .rename(columns={"generation_mw": "forecast_mw"})[_SELECTED_COLS]
        .sort_values("start_time")
        .reset_index(drop=True)
    )
    return out


def intervals_with_any_vintage(forecasts: pd.DataFrame, delivery_day_: date) -> int:
    """How many delivery-day intervals have at least one forecast vintage (any publish time)."""
    start, end = delivery_window_utc(delivery_day_)
    mask = (forecasts["start_time"] >= start) & (forecasts["start_time"] < end)
    return int(forecasts.loc[mask, "start_time"].nunique())


def vintage_history(
    forecasts: pd.DataFrame,
    delivery_day_: date,
    cutoff_utc: datetime,
    start_time: datetime | None = None,
) -> pd.DataFrame:
    """All vintages for the delivery day (or one interval), each flagged eligible."""
    start, end = delivery_window_utc(delivery_day_)
    mask = (forecasts["start_time"] >= start) & (forecasts["start_time"] < end)
    if start_time is not None:
        mask &= forecasts["start_time"] == pd.Timestamp(start_time)
    df = forecasts.loc[mask].copy()
    if df.empty:
        return pd.DataFrame(columns=["start_time", "publish_time", "forecast_mw", "eligible"])
    df = df.rename(columns={"generation_mw": "forecast_mw"})
    df["eligible"] = df["publish_time"] <= pd.Timestamp(cutoff_utc)
    return (
        df[["start_time", "publish_time", "forecast_mw", "eligible"]]
        .sort_values(["start_time", "publish_time"])
        .reset_index(drop=True)
    )
