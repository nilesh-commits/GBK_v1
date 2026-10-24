"""Shared helpers for API routes (validation, cutoff resolution, serialization)."""
from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from app.config import Settings
from app.errors import ApiError
from app.models.schemas import AccuracySeriesItem
from app.time_utils import resolve_cutoff, to_utc


def validate_decision_date(d: date, settings: Settings) -> None:
    if not (settings.decision_date_min <= d <= settings.decision_date_max):
        raise ApiError(
            422,
            "OUT_OF_SCOPE_DATE",
            f"decision_date must fall within {settings.decision_date_min.isoformat()} "
            f".. {settings.decision_date_max.isoformat()}.",
            {"parameter": "decision_date", "value": d.isoformat()},
        )


def resolve_request_cutoff(
    decision: date, cutoff_override: datetime | None, settings: Settings
) -> datetime:
    if cutoff_override is not None:
        return to_utc(cutoff_override)
    return resolve_cutoff(decision, settings.cutoff_local_time, settings.cutoff_timezone)


def _f(value: object) -> float | None:
    return None if pd.isna(value) else float(value)  # type: ignore[arg-type]


def build_series(merged: pd.DataFrame) -> list[AccuracySeriesItem]:
    return [
        AccuracySeriesItem(
            start_time=row.start_time,
            forecast_mw=_f(row.forecast_mw),
            actual_mw=_f(row.actual_mw),
            error_mw=_f(row.error_mw),
            abs_error_mw=_f(row.abs_error_mw),
        )
        for row in merged.itertuples()
    ]
