import { Metrics } from "../api/types";
import { formatMW, formatSigned } from "../lib/format";

interface Props {
  metrics: Metrics;
}

export function MetricCards({ metrics }: Props) {
  const biasLabel =
    metrics.bias === null
      ? ""
      : metrics.bias > 0
        ? "on average, over-forecast"
        : metrics.bias < 0
          ? "on average, under-forecast"
          : "no systematic bias";

  return (
    <div className="cards">
      <div className="card">
        <span className="card__label">MAE</span>
        <span className="card__value">{formatMW(metrics.mae)}</span>
        <span className="card__hint">mean absolute error</span>
      </div>
      <div className="card">
        <span className="card__label">RMSE</span>
        <span className="card__value">{formatMW(metrics.rmse)}</span>
        <span className="card__hint">penalises large misses</span>
      </div>
      <div className="card">
        <span className="card__label">Bias</span>
        <span className="card__value">{formatSigned(metrics.bias)}</span>
        <span className="card__hint">{biasLabel}</span>
      </div>
      <div className="card card--muted">
        <span className="card__label">Matched intervals</span>
        <span className="card__value">{metrics.matched_intervals}</span>
        <span className="card__hint">hours used in metrics</span>
      </div>
    </div>
  );
}
