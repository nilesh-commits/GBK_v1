"""Time handling: UTC compute, Europe/London cutoff resolution, delivery mapping.

We store and compute in UTC. The purchasing cutoff is expressed in a wall-clock
local time (default Europe/London) on the decision day and converted to UTC via
the zone (so GMT/BST is handled correctly, not a fixed offset). January 2026 is
GMT, but the code never assumes that.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

UTC = ZoneInfo("UTC")


def delivery_day(decision: date) -> date:
    """Day-ahead: a decision on day d is for delivery on day d+1."""
    return decision + timedelta(days=1)


def resolve_cutoff(decision: date, local_hhmm: str, tz_name: str) -> datetime:
    """Resolve the cutoff timestamp (UTC) for a decision day.

    `local_hhmm` is "HH:MM" wall-clock in `tz_name` on the decision day.
    """
    hh, mm = (int(part) for part in local_hhmm.split(":"))
    tz = ZoneInfo(tz_name)
    local_dt = datetime.combine(decision, time(hh, mm), tzinfo=tz)
    return local_dt.astimezone(UTC)


def to_utc(dt: datetime) -> datetime:
    """Coerce a datetime to UTC; a naive datetime is assumed to already be UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def delivery_window_utc(day: date) -> tuple[pd.Timestamp, pd.Timestamp]:
    """[start, end) UTC bounds of a delivery day's 30-min intervals.

    January 2026 is GMT, so UK delivery-day boundaries align with UTC midnight.
    Documented assumption (docs/11): in-scope days have 48 intervals.
    """
    start = pd.Timestamp(datetime.combine(day, time(0, 0)), tz="UTC")
    return start, start + pd.Timedelta(days=1)
