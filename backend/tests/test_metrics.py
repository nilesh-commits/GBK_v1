import pandas as pd

from app.services.metrics import compute_metrics


def test_metrics_fixture():
    # Errors +200, -200, +100 (see docs/04-methodology.md).
    matched = pd.DataFrame({"error_mw": [200.0, -200.0, 100.0]})
    m = compute_metrics(matched)
    assert m["matched_intervals"] == 3
    assert m["mae"] == 166.7
    assert m["rmse"] == 173.2
    assert m["bias"] == 33.3


def test_metrics_empty():
    m = compute_metrics(pd.DataFrame({"error_mw": []}))
    assert m == {"mae": None, "rmse": None, "bias": None, "matched_intervals": 0}
