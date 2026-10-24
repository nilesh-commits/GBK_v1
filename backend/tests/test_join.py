from datetime import date

import pandas as pd

from app.services.join import join_forecast_actual

DDAY = date(2026, 1, 16)


def test_join_aligns_halfhourly_actuals_to_hourly_forecast():
    # Hourly forecasts (WINDFOR native resolution).
    selected = pd.DataFrame(
        {
            "start_time": pd.to_datetime(
                ["2026-01-16T00:00:00Z", "2026-01-16T01:00:00Z"], utc=True
            ),
            "forecast_mw": [1250.0, 900.0],
        }
    )
    # Half-hourly actuals (FUELHH native resolution).
    actuals = pd.DataFrame(
        {
            "start_time": pd.to_datetime(
                [
                    "2026-01-16T00:00:00Z",
                    "2026-01-16T00:30:00Z",  # -> hour 00:00 bin, mean(1000,850)=925
                    "2026-01-16T02:00:00Z",  # hour 02:00 has no forecast
                ],
                utc=True,
            ),
            "generation_mw": [1000.0, 850.0, 800.0],
        }
    )
    merged, matched, counts = join_forecast_actual(selected, actuals, DDAY)

    assert len(matched) == 1  # only hour 00:00 has both forecast and actual
    row0 = matched.iloc[0]
    assert row0.actual_mw == 925.0  # mean of the two half-hours
    assert row0.error_mw == 325.0  # 1250 - 925
    assert counts["missing_actual"] == 1  # 01:00 forecast, no actual
    assert counts["missing_forecast"] == 1  # 02:00 actual, no forecast


def test_missing_actual_not_zero_filled():
    selected = pd.DataFrame(
        {
            "start_time": pd.to_datetime(["2026-01-16T00:00:00Z"], utc=True),
            "forecast_mw": [1250.0],
        }
    )
    actuals = pd.DataFrame({"start_time": pd.to_datetime([], utc=True), "generation_mw": []})
    merged, matched, counts = join_forecast_actual(selected, actuals, DDAY)
    assert len(matched) == 0
    assert counts["missing_actual"] == 1
    assert pd.isna(merged.iloc[0].actual_mw)  # never 0
