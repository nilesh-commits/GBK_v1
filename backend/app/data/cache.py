"""In-memory parquet-backed data cache.

The dataset is small, read-only and immutable, so we hold it in memory (no DB).
Loaded once at startup from parquet written by scripts/ingest.py. No Elexon call
happens on the request path.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_ACTUALS_COLS = ["start_time", "generation_mw"]
_FORECASTS_COLS = ["start_time", "publish_time", "generation_mw"]


def _empty(cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=cols)


class DataCache:
    def __init__(self) -> None:
        self.actuals: pd.DataFrame = _empty(_ACTUALS_COLS)
        self.forecasts: pd.DataFrame = _empty(_FORECASTS_COLS)
        self.loaded: bool = False

    def load(self, data_dir: str | Path) -> None:
        data_dir = Path(data_dir)
        actuals_path = data_dir / "actuals.parquet"
        forecasts_path = data_dir / "forecasts.parquet"
        if not (actuals_path.exists() and forecasts_path.exists()):
            self.loaded = False
            logger.warning(
                "Parquet cache not found in %s; run scripts/ingest.py to populate it.",
                data_dir,
            )
            return
        actuals = pd.read_parquet(actuals_path)
        forecasts = pd.read_parquet(forecasts_path)
        actuals["start_time"] = pd.to_datetime(actuals["start_time"], utc=True)
        forecasts["start_time"] = pd.to_datetime(forecasts["start_time"], utc=True)
        forecasts["publish_time"] = pd.to_datetime(forecasts["publish_time"], utc=True)
        self.seed(actuals, forecasts)
        logger.info(
            "Loaded cache: %d actual intervals, %d forecast rows.",
            len(actuals),
            len(forecasts),
        )

    def seed(self, actuals: pd.DataFrame, forecasts: pd.DataFrame) -> None:
        """Replace cache contents directly (used by tests and by load())."""
        self.actuals = actuals.reset_index(drop=True)
        self.forecasts = forecasts.reset_index(drop=True)
        self.loaded = True

    @property
    def intervals_cached(self) -> int:
        return int(len(self.actuals))


_cache = DataCache()


def get_cache() -> DataCache:
    return _cache
