"""Health / readiness endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.data.cache import DataCache, get_cache
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(cache: DataCache = Depends(get_cache)) -> HealthResponse:
    return HealthResponse(
        status="ok" if cache.loaded else "degraded",
        data_loaded=cache.loaded,
        intervals_cached=cache.intervals_cached,
    )
