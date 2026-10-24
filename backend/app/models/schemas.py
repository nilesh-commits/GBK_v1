"""Pydantic response models (the API contract; see docs/05-api-reference.md)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    intervals_cached: int


class ForecastInterval(BaseModel):
    start_time: datetime
    forecast_mw: Optional[float]
    publish_time: Optional[datetime]


class ForecastsResponse(BaseModel):
    decision_date: date
    delivery_date: date
    cutoff: datetime
    unit: str = "MW"
    intervals: list[ForecastInterval]
    intervals_count: int
    intervals_missing_forecast: int


class VintageItem(BaseModel):
    start_time: datetime
    publish_time: datetime
    forecast_mw: float
    eligible: bool


class ForecastHistoryResponse(BaseModel):
    decision_date: date
    delivery_date: date
    cutoff: datetime
    start_time: Optional[datetime] = None
    unit: str = "MW"
    vintages: list[VintageItem]


class AccuracySeriesItem(BaseModel):
    start_time: datetime
    forecast_mw: Optional[float]
    actual_mw: Optional[float]
    error_mw: Optional[float]
    abs_error_mw: Optional[float]


class Metrics(BaseModel):
    mae: Optional[float]
    rmse: Optional[float]
    bias: Optional[float]
    matched_intervals: int


class DateRange(BaseModel):
    start: date
    end: date


class Excluded(BaseModel):
    missing_forecast: int
    missing_actual: int


class AccuracyResponse(BaseModel):
    decision_range: DateRange
    delivery_range: DateRange
    cutoff: Optional[datetime]  # single decision date -> that day's cutoff; range -> null
    unit: str = "MW"
    metrics: Metrics
    series: list[AccuracySeriesItem]
    excluded: Excluded
