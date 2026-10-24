# 04 — Forecast Selection & Accuracy Methodology

This is the analytical core of the product. Two things must be correct: **which forecast we score** (point-in-time correctness) and **how we score it** (error metrics).

## 1. Forecast selection — point-in-time correctness

For each delivery interval there are multiple forecast vintages (distinct `publishTime`s). To reflect what the purchasing team *actually knew* when deciding, we select, per delivery interval:

> the forecast with the **latest `publishTime` that is less than or equal to the configured purchasing cutoff**.

- A forecast published **after** the cutoff is **never** used to score that decision. Using one would introduce **look-ahead bias** and overstate achievable forecast quality.
- If **no** forecast exists on or before the cutoff for an interval, that interval has **no eligible forecast** and is excluded from accuracy metrics (and surfaced in the UI as such). It is **not** back-filled.

### The cutoff is configurable — not assumed

The exact operational cutoff (gate-closure deadline for the day-ahead decision) **was not supplied** by the client. Therefore:

- The cutoff is a **configuration value**, resolved per decision day.
- The system does **not** silently assume midnight.
- The default is **12:00 Europe/London on the decision day**, provided *as an explicit, documented assumption* (see [11 — Assumptions](11-assumptions-and-limitations.md)), labelled as provisional and not an official market deadline, and overridable via configuration / request parameter.

Modelled as: a **decision date *d*** (the in-scope selector, *d* ∈ 1–31 Jan 2026); the cutoff is a timestamp on day *d*; the decision is for **delivery day *d*+1** (day-ahead). The API takes `decision_date`, derives the delivery day, and exposes the resolved cutoff so a reviewer can see and change it rather than trust a hidden constant.

## 2. Joining forecasts to actuals

**Resolution alignment (verified from the data).** WINDFOR forecasts are published
at **hourly** resolution; FUELHH actuals are **half-hourly** (see [03 — Data Sources](03-data-sources.md)).
To compare like-for-like without inventing data, actuals are aggregated to the
forecast's hourly grid: each hourly bin `[HH:00, HH+1:00)` takes the **mean** of its
two half-hourly actual values. This is a documented alignment — not interpolation and
not zero-filling.

- After alignment, join the selected (eligible) forecast to the hour-aggregated actuals **by `start_time`**.
- Only intervals present in **both** the eligible-forecast set and the actuals set are "matched" and enter metric calculations.
- Unmatched intervals (missing forecast, or actual not yet available) are excluded and counted separately; they are **never** treated as `0`.

## 3. Error definition

For each matched interval:

```
error = forecast_generation - actual_generation      (MW)
```

- **Positive error** → wind was **overforecast** (forecast higher than actual).
- **Negative error** → wind was **underforecast**.

## 4. Metrics (all in MW)

Over the set of **N** matched intervals:

| Metric | Formula | Interpretation |
|---|---|---|
| **MAE** | `mean(|error|)` | Typical magnitude of error, robust to sign |
| **RMSE** | `sqrt(mean(error²))` | Penalizes large errors more; ≥ MAE |
| **Bias** | `mean(error)` | Systematic over- (positive) or under- (negative) forecasting |

Every metric response includes **N**, the number of matched intervals used — a metric without its sample size is not reported.

## 5. Worked micro-example

Three matched intervals (forecast, actual in MW):

| start_time | forecast | actual | error |
|---|---|---|---|
| 00:00 | 1200 | 1000 | +200 |
| 00:30 | 900 | 1100 | −200 |
| 01:00 | 1500 | 1400 | +100 |

- MAE = (200 + 200 + 100) / 3 = **166.7 MW**
- RMSE = √((200² + 200² + 100²)/3) = √(90000/3) = √30000 ≈ **173.2 MW**
- Bias = (+200 − 200 + 100)/3 = **+33.3 MW** (slight overforecast)

These exact numbers are used as a unit-test fixture (see [07 — Testing](07-testing.md)).

## 6. Explicitly out of scope

This methodology quantifies **wind forecast uncertainty only**. It does not estimate the electricity shortfall or a purchase quantity — that would require consumer demand and other generation availability, which these datasets do not contain. See [01 — Overview](01-overview.md) and [11 — Assumptions](11-assumptions-and-limitations.md).
