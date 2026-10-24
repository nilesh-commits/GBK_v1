"""Forecast endpoints: latest eligible forecast + vintage history."""
from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, Query

from app.api.common import resolve_request_cutoff, validate_decision_date
from app.config import Settings, get_settings
from app.data.cache import DataCache, get_cache
from app.models.schemas import (
    ForecastHistoryResponse,
    ForecastInterval,
    ForecastsResponse,
    VintageItem,
)
from app.services.forecast_selection import (
    intervals_with_any_vintage,
    select_eligible,
    vintage_history,
)
from app.time_utils import delivery_day

router = APIRouter(tags=["forecasts"])


@router.get("/forecasts", response_model=ForecastsResponse)
def get_forecasts(
    decision_date: date = Query(..., description="Decision day (1-31 Jan 2026)"),
    cutoff: datetime | None = Query(None, description="Override the default cutoff (ISO datetime)"),
    cache: DataCache = Depends(get_cache),
    settings: Settings = Depends(get_settings),
) -> ForecastsResponse:
    validate_decision_date(decision_date, settings)
    dday = delivery_day(decision_date)
    cutoff_utc = resolve_request_cutoff(decision_date, cutoff, settings)

    selected = select_eligible(cache.forecasts, dday, cutoff_utc)
    intervals = [
        ForecastInterval(
            start_time=row.start_time,
            forecast_mw=float(row.forecast_mw),
            publish_time=row.publish_time,
        )
        for row in selected.itertuples()
    ]
    total_intervals = intervals_with_any_vintage(cache.forecasts, dday)
    missing = max(0, total_intervals - len(intervals))

    return ForecastsResponse(
        decision_date=decision_date,
        delivery_date=dday,
        cutoff=cutoff_utc,
        intervals=intervals,
        intervals_count=len(intervals),
        intervals_missing_forecast=missing,
    )


@router.get("/forecasts/history", response_model=ForecastHistoryResponse)
def get_forecast_history(
    decision_date: date = Query(..., description="Decision day (1-31 Jan 2026)"),
    start_time: datetime | None = Query(None, description="Narrow to a single delivery interval"),
    cutoff: datetime | None = Query(None, description="Override the default cutoff (ISO datetime)"),
    cache: DataCache = Depends(get_cache),
    settings: Settings = Depends(get_settings),
) -> ForecastHistoryResponse:
    validate_decision_date(decision_date, settings)
    dday = delivery_day(decision_date)
    cutoff_utc = resolve_request_cutoff(decision_date, cutoff, settings)

    hist = vintage_history(cache.forecasts, dday, cutoff_utc, start_time)
    vintages = [
        VintageItem(
            start_time=row.start_time,
            publish_time=row.publish_time,
            forecast_mw=float(row.forecast_mw),
            eligible=bool(row.eligible),
        )
        for row in hist.itertuples()
    ]
    return ForecastHistoryResponse(
        decision_date=decision_date,
        delivery_date=dday,
        cutoff=cutoff_utc,
        start_time=start_time,
        vintages=vintages,
    )
