from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd

from app.services.forecast_selection import (
    intervals_with_any_vintage,
    select_eligible,
    vintage_history,
)

UTC = ZoneInfo("UTC")
DDAY = date(2026, 1, 16)
CUTOFF = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)


def _forecasts() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "start_time": pd.to_datetime(
                [
                    "2026-01-16T00:00:00Z",
                    "2026-01-16T00:00:00Z",
                    "2026-01-16T00:00:00Z",
                    "2026-01-16T00:30:00Z",
                ],
                utc=True,
            ),
            "publish_time": pd.to_datetime(
                [
                    "2026-01-15T06:00:00Z",
                    "2026-01-15T11:00:00Z",
                    "2026-01-15T16:00:00Z",  # after cutoff -> ineligible
                    "2026-01-15T11:00:00Z",
                ],
                utc=True,
            ),
            "generation_mw": [1200.0, 1250.0, 1180.0, 900.0],
        }
    )


def test_selects_latest_eligible():
    sel = select_eligible(_forecasts(), DDAY, CUTOFF)
    row = sel[sel.start_time == pd.Timestamp("2026-01-16T00:00:00Z")].iloc[0]
    assert row.forecast_mw == 1250.0
    assert row.publish_time == pd.Timestamp("2026-01-15T11:00:00Z")


def test_excludes_post_cutoff_vintage():
    sel = select_eligible(_forecasts(), DDAY, CUTOFF)
    assert 1180.0 not in set(sel.forecast_mw)


def test_no_eligible_interval_is_dropped():
    early_cutoff = datetime(2026, 1, 15, 5, 0, tzinfo=UTC)  # before every publish
    sel = select_eligible(_forecasts(), DDAY, early_cutoff)
    assert sel.empty


def test_vintage_history_flags_eligibility():
    hist = vintage_history(
        _forecasts(), DDAY, CUTOFF, start_time=datetime(2026, 1, 16, 0, 0, tzinfo=UTC)
    )
    elig = dict(zip(hist.publish_time, hist.eligible))
    assert elig[pd.Timestamp("2026-01-15T11:00:00Z")] is True or elig[pd.Timestamp("2026-01-15T11:00:00Z")]
    assert not elig[pd.Timestamp("2026-01-15T16:00:00Z")]


def test_intervals_with_any_vintage():
    assert intervals_with_any_vintage(_forecasts(), DDAY) == 2
