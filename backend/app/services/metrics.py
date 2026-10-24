"""Accuracy metrics (see docs/04-methodology.md). All values in MW.

error = forecast - actual  (positive => overforecast)
MAE  = mean(|error|)
RMSE = sqrt(mean(error^2))
Bias = mean(error)
"""
from __future__ import annotations

import math

import pandas as pd


def compute_metrics(matched: pd.DataFrame) -> dict:
    """Compute MAE/RMSE/Bias over matched intervals. Empty -> None metrics, N=0."""
    n = int(len(matched))
    if n == 0:
        return {"mae": None, "rmse": None, "bias": None, "matched_intervals": 0}
    err = matched["error_mw"].astype(float)
    return {
        "mae": round(float(err.abs().mean()), 1),
        "rmse": round(math.sqrt(float((err**2).mean())), 1),
        "bias": round(float(err.mean()), 1),
        "matched_intervals": n,
    }
