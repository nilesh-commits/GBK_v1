import { api } from "../api/client";
import { DecisionControls } from "../components/DecisionControls";
import { ErrorChart } from "../components/ErrorChart";
import { ErrorTable } from "../components/ErrorTable";
import { GenerationChart, toChartPoints } from "../components/GenerationChart";
import { MetricCards } from "../components/MetricCards";
import { StateBoundary } from "../components/StateBoundary";
import { useApiData } from "../hooks/useApiData";

interface Props {
  decisionDate: string;
  onDecisionChange: (d: string) => void;
}

export function AccuracyAnalysis({ decisionDate, onDecisionChange }: Props) {
  const state = useApiData((s) => api.getAccuracy(decisionDate, undefined, s), [decisionDate]);
  const data = state.data;

  return (
    <section>
      <DecisionControls
        decisionDate={decisionDate}
        onChange={onDecisionChange}
        deliveryDate={data?.delivery_range.start}
        cutoff={data?.cutoff}
      />

      <StateBoundary
        loading={state.loading}
        error={state.error}
        empty={!!data && data.metrics.matched_intervals === 0}
        emptyMessage="No matched forecast/actual intervals for this decision date."
        onRetry={() => onDecisionChange(decisionDate)}
      >
        {data && (
          <>
            <MetricCards metrics={data.metrics} />
            {(data.excluded.missing_forecast > 0 || data.excluded.missing_actual > 0) && (
              <p className="notice">
                Excluded from metrics: {data.excluded.missing_forecast} interval(s) with no eligible forecast,{" "}
                {data.excluded.missing_actual} with no actual. Excluded intervals are never treated as zero.
              </p>
            )}

            <div className="panel">
              <div className="panel__head">
                <h2>Forecast vs actual</h2>
                <span className="panel__meta">hourly, MW</span>
              </div>
              <GenerationChart data={toChartPoints(data.series)} showActual />
            </div>

            <div className="panel">
              <div className="panel__head">
                <h2>Forecast error over time</h2>
              </div>
              <ErrorChart series={data.series} />
            </div>

            <div className="panel">
              <div className="panel__head">
                <h2>Interval detail</h2>
                <span className="panel__meta">sortable</span>
              </div>
              <ErrorTable series={data.series} />
            </div>
          </>
        )}
      </StateBoundary>
    </section>
  );
}
