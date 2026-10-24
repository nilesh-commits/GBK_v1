import pandas as pd
from fastapi.testclient import TestClient

from app.data.cache import get_cache
from app.main import app

client = TestClient(app)


def _seed() -> None:
    # Hourly forecasts (WINDFOR native resolution); two vintages for hour 00:00,
    # the 16:00 one published after the 12:00 cutoff (ineligible).
    forecasts = pd.DataFrame(
        {
            "start_time": pd.to_datetime(
                ["2026-01-16T00:00:00Z", "2026-01-16T00:00:00Z", "2026-01-16T01:00:00Z"],
                utc=True,
            ),
            "publish_time": pd.to_datetime(
                ["2026-01-15T11:00:00Z", "2026-01-15T16:00:00Z", "2026-01-15T11:00:00Z"],
                utc=True,
            ),
            "generation_mw": [1250.0, 1180.0, 900.0],
        }
    )
    # Half-hourly actuals (FUELHH native resolution).
    actuals = pd.DataFrame(
        {
            "start_time": pd.to_datetime(
                [
                    "2026-01-16T00:00:00Z",
                    "2026-01-16T00:30:00Z",
                    "2026-01-16T01:00:00Z",
                    "2026-01-16T01:30:00Z",
                ],
                utc=True,
            ),
            "generation_mw": [1000.0, 850.0, 1200.0, 1100.0],
        }
    )
    get_cache().seed(actuals, forecasts)


def test_health_reports_loaded():
    _seed()
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["data_loaded"] is True


def test_forecasts_uses_eligible_vintage():
    _seed()
    r = client.get("/api/forecasts", params={"decision_date": "2026-01-15"})
    assert r.status_code == 200
    body = r.json()
    assert body["delivery_date"] == "2026-01-16"
    first = next(i for i in body["intervals"] if i["start_time"].startswith("2026-01-16T00:00"))
    assert first["forecast_mw"] == 1250.0  # 11:00 vintage, not the post-cutoff 16:00 one


def test_accuracy_single_date_metrics():
    _seed()
    r = client.get("/api/accuracy", params={"decision_date": "2026-01-15"})
    assert r.status_code == 200
    body = r.json()
    assert body["metrics"]["matched_intervals"] == 2
    s0 = next(x for x in body["series"] if x["start_time"].startswith("2026-01-16T00:00"))
    assert s0["forecast_mw"] == 1250.0
    assert s0["actual_mw"] == 925.0  # mean(1000, 850)
    assert s0["error_mw"] == 325.0  # 1250 - 925


def test_out_of_scope_date_returns_422():
    r = client.get("/api/accuracy", params={"decision_date": "2026-02-05"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "OUT_OF_SCOPE_DATE"


def test_invalid_parameter_returns_400():
    r = client.get("/api/forecasts", params={"decision_date": "not-a-date"})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_PARAMETER"
