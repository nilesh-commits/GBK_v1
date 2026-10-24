"""Accuracy endpoint: forecast-vs-actual series + MAE/RMSE/Bias.

Accepts a single `decision_date` or an inclusive `start`+`end` range of decision
dates. In the range case each decision day uses its own resolved cutoff, metrics
aggregate across all days, and the `cutoff` field is null (it varies per day).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
from fastapi import APIRouter, Depends, Query

from app.api.common import build_series, resolve_request_cutoff, validate_decision_date
from app.config import Settings, get_settings
from app.data.cache import DataCache, get_cache
from app.errors import ApiError
from app.models.schemas import AccuracyResponse, DateRange, Excluded, Metrics
from app.services.forecast_selection import select_eligible
from app.services.join import join_forecast_actual
from app.services.metrics import compute_metrics
from app.time_utils import delivery_day

router = APIRouter(tags=["accuracy"])


def _decision_dates(
    decision_date: date | None, start: date | None, end: date | None
) -> list[date]:
    if decision_date is not None:
        return [decision_date]
    if start is not None and end is not None:
        if start > end:
            raise ApiError(
                400, "INVALID_PARAMETER", "start must be on or before end.",
                {"start": start.isoformat(), "end": end.isoformat()},
            )
        return [start + timedelta(days=i) for i in range((end - start).days + 1)]
    raise ApiError(
        400, "INVALID_PARAMETER", "Provide either decision_date or both start and end.",
    )


@router.get("/accuracy", response_model=AccuracyResponse)
def get_accuracy(
    decision_date: date | None = Query(None, description="Single decision day"),
    start: date | None = Query(None, description="Range start (decision day)"),
    end: date | None = Query(None, description="Range end (decision day)"),
    cutoff: datetime | None = Query(None, description="Override cutoff (single decision_date only)"),
    cache: DataCache = Depends(get_cache),
    settings: Settings = Depends(get_settings),
) -> AccuracyResponse:
    dates = _decision_dates(decision_date, start, end)
    for d in dates:
        validate_decision_date(d, settings)

    is_single = len(dates) == 1
    merged_parts: list[pd.DataFrame] = []
    matched_parts: list[pd.DataFrame] = []
    missing_forecast = 0
    missing_actual = 0
    single_cutoff: datetime | None = None

    for d in dates:
        dday = delivery_day(d)
        cutoff_utc = resolve_request_cutoff(d, cutoff if is_single else None, settings)
        if is_single:
            single_cutoff = cutoff_utc
        selected = select_eligible(cache.forecasts, dday, cutoff_utc)
        merged, matched, counts = join_forecast_actual(selected, cache.actuals, dday)
        merged_parts.append(merged)
        matched_parts.append(matched)
        missing_forecast += counts["missing_forecast"]
        missing_actual += counts["missing_actual"]

    merged_all = (
        pd.concat(merged_parts, ignore_index=True).sort_values("start_time").reset_index(drop=True)
        if merged_parts
        else pd.DataFrame(columns=["start_time", "forecast_mw", "actual_mw", "error_mw", "abs_error_mw"])
    )
    matched_all = (
        pd.concat(matched_parts, ignore_index=True)
        if matched_parts
        else pd.DataFrame(columns=["error_mw"])
    )

    return AccuracyResponse(
        decision_range=DateRange(start=dates[0], end=dates[-1]),
        delivery_range=DateRange(start=delivery_day(dates[0]), end=delivery_day(dates[-1])),
        cutoff=single_cutoff,
        metrics=Metrics(**compute_metrics(matched_all)),
        series=build_series(merged_all),
        excluded=Excluded(missing_forecast=missing_forecast, missing_actual=missing_actual),
    )
