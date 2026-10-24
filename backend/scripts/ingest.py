"""One-shot ingestion: Elexon BMRS -> normalized parquet cache.

Scope is decision-anchored: decisions 1-31 Jan 2026 -> delivery days 2 Jan - 1 Feb
2026. We fetch FUELHH (WIND) actuals for those delivery days and WINDFOR vintages
published across January 2026, then write parquet that the API serves from memory.

Run from the backend directory:  python scripts/ingest.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from datetime import date, datetime
from pathlib import Path

# Allow `python scripts/ingest.py` to import the app package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from app.adapters.elexon_client import ElexonClient  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.time_utils import UTC  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest")

# In-scope windows.
ACTUALS_FROM = date(2026, 1, 2)
ACTUALS_TO = date(2026, 2, 1)
PUBLISH_FROM = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
PUBLISH_TO = datetime(2026, 2, 1, 0, 0, tzinfo=UTC)
# Delivery window used to trim forecasts/actuals to scope [from, to).
DELIVERY_FROM = pd.Timestamp("2026-01-02T00:00:00Z")
DELIVERY_TO = pd.Timestamp("2026-02-02T00:00:00Z")


async def main() -> None:
    settings = get_settings()
    client = ElexonClient(
        settings.elexon_base_url, settings.http_timeout_seconds, settings.http_max_retries
    )

    logger.info("Fetching FUELHH (WIND) actuals %s .. %s", ACTUALS_FROM, ACTUALS_TO)
    actuals_rows = await client.fetch_actuals(ACTUALS_FROM, ACTUALS_TO)
    logger.info("Fetching WINDFOR forecasts published %s .. %s", PUBLISH_FROM, PUBLISH_TO)
    forecast_rows = await client.fetch_forecasts(PUBLISH_FROM, PUBLISH_TO)

    actuals = pd.DataFrame(actuals_rows, columns=["start_time", "generation_mw"])
    forecasts = pd.DataFrame(forecast_rows, columns=["start_time", "publish_time", "generation_mw"])

    actuals["start_time"] = pd.to_datetime(actuals["start_time"], utc=True)
    forecasts["start_time"] = pd.to_datetime(forecasts["start_time"], utc=True)
    forecasts["publish_time"] = pd.to_datetime(forecasts["publish_time"], utc=True)

    actuals = (
        actuals.drop_duplicates(subset=["start_time"])
        .sort_values("start_time")
        .reset_index(drop=True)
    )
    forecasts = (
        forecasts.drop_duplicates(subset=["start_time", "publish_time"])
        .sort_values(["start_time", "publish_time"])
        .reset_index(drop=True)
    )

    actuals = actuals[(actuals["start_time"] >= DELIVERY_FROM) & (actuals["start_time"] < DELIVERY_TO)]
    forecasts = forecasts[
        (forecasts["start_time"] >= DELIVERY_FROM) & (forecasts["start_time"] < DELIVERY_TO)
    ]

    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    actuals.to_parquet(data_dir / "actuals.parquet", index=False)
    forecasts.to_parquet(data_dir / "forecasts.parquet", index=False)
    logger.info(
        "Wrote %d actual intervals and %d forecast rows to %s",
        len(actuals),
        len(forecasts),
        data_dir.resolve(),
    )


if __name__ == "__main__":
    asyncio.run(main())
