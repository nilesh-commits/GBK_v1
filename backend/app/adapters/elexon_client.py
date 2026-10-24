"""Elexon BMRS adapter: fetch + normalize FUELHH actuals and WINDFOR forecasts.

Used only by scripts/ingest.py (offline), never on the request path. Normalizes
to a small, explicit internal schema and skips (does not zero-fill) rows with
missing generation values.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime

import httpx

logger = logging.getLogger(__name__)


class ElexonError(Exception):
    """Base error for Elexon ingestion failures."""


class ElexonTimeout(ElexonError):
    """Upstream timed out after retries."""


class ElexonUnavailable(ElexonError):
    """Upstream returned an error / was unreachable after retries."""


def _as_records(payload: object) -> list[dict]:
    """Elexon /stream returns a JSON array; some datasets wrap it in {'data': [...]}"""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    raise ElexonError("Unexpected Elexon response shape (expected a list of records).")


def _to_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


class ElexonClient:
    def __init__(self, base_url: str, timeout_seconds: float, max_retries: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._max_retries = max(1, max_retries)

    async def _get(self, path: str, params: dict) -> list[dict]:
        url = f"{self._base_url}{path}"
        last_exc: Exception | None = None
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(1, self._max_retries + 1):
                try:
                    resp = await client.get(url, params=params)
                    resp.raise_for_status()
                    return _as_records(resp.json())
                except httpx.TimeoutException as exc:
                    last_exc = exc
                    logger.warning("Elexon timeout (attempt %d/%d) %s", attempt, self._max_retries, url)
                except httpx.HTTPError as exc:
                    last_exc = exc
                    logger.warning("Elexon HTTP error (attempt %d/%d) %s: %s", attempt, self._max_retries, url, exc)
                if attempt < self._max_retries:
                    await asyncio.sleep(min(2 ** (attempt - 1), 8))
        if isinstance(last_exc, httpx.TimeoutException):
            raise ElexonTimeout(str(last_exc)) from last_exc
        raise ElexonUnavailable(str(last_exc)) from last_exc

    async def fetch_actuals(self, settlement_date_from: date, settlement_date_to: date) -> list[dict]:
        """FUELHH actuals, filtered to fuelType == WIND, normalized."""
        records = await self._get(
            "/datasets/FUELHH/stream",
            {
                "settlementDateFrom": settlement_date_from.isoformat(),
                "settlementDateTo": settlement_date_to.isoformat(),
            },
        )
        out: list[dict] = []
        skipped = 0
        for rec in records:
            if str(rec.get("fuelType", "")).upper() != "WIND":
                continue
            start = rec.get("startTime")
            gen = _to_float(rec.get("generation"))
            if start is None or gen is None:
                skipped += 1
                continue
            out.append({"start_time": start, "generation_mw": gen})
        if skipped:
            logger.info("FUELHH: skipped %d WIND rows with missing start/generation.", skipped)
        return out

    async def fetch_forecasts(self, publish_from: datetime, publish_to: datetime) -> list[dict]:
        """WINDFOR forecasts (all vintages in the publish window), normalized."""
        records = await self._get(
            "/datasets/WINDFOR/stream",
            {
                "publishDateTimeFrom": publish_from.isoformat(),
                "publishDateTimeTo": publish_to.isoformat(),
            },
        )
        out: list[dict] = []
        skipped = 0
        for rec in records:
            start = rec.get("startTime")
            publish = rec.get("publishTime")
            gen = _to_float(rec.get("generation"))
            if start is None or publish is None or gen is None:
                skipped += 1
                continue
            out.append({"start_time": start, "publish_time": publish, "generation_mw": gen})
        if skipped:
            logger.info("WINDFOR: skipped %d rows with missing start/publish/generation.", skipped)
        return out
