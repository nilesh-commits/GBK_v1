import asyncio
from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx
import respx

from app.adapters.elexon_client import ElexonClient, ElexonTimeout

UTC = ZoneInfo("UTC")
BASE = "https://example.test/bmrs/api/v1"


@respx.mock
def test_fetch_actuals_filters_wind_and_skips_missing():
    respx.get(f"{BASE}/datasets/FUELHH/stream").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"fuelType": "WIND", "startTime": "2026-01-16T00:00:00Z", "generation": 1000},
                {"fuelType": "CCGT", "startTime": "2026-01-16T00:00:00Z", "generation": 5000},
                {"fuelType": "WIND", "startTime": "2026-01-16T00:30:00Z", "generation": None},
            ],
        )
    )
    client = ElexonClient(BASE, timeout_seconds=5, max_retries=1)
    rows = asyncio.run(client.fetch_actuals(date(2026, 1, 2), date(2026, 2, 1)))
    assert len(rows) == 1  # only the WIND row with a generation value
    assert rows[0]["generation_mw"] == 1000.0


@respx.mock
def test_timeout_raises_elexon_timeout():
    respx.get(f"{BASE}/datasets/WINDFOR/stream").mock(side_effect=httpx.TimeoutException("boom"))
    client = ElexonClient(BASE, timeout_seconds=1, max_retries=2)
    try:
        asyncio.run(
            client.fetch_forecasts(
                datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 2, 1, tzinfo=UTC)
            )
        )
        raise AssertionError("expected ElexonTimeout")
    except ElexonTimeout:
        pass
