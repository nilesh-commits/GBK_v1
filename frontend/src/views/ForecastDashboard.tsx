import { useEffect, useState } from "react";
import { api } from "../api/client";
import { ForecastHistoryResponse } from "../api/types";
import { DecisionControls } from "../components/DecisionControls";
import { GenerationChart, toChartPoints } from "../components/GenerationChart";
import { StateBoundary } from "../components/StateBoundary";
import { useApiData } from "../hooks/useApiData";
import { formatDateTime, formatMW, formatTime } from "../lib/format";

interface Props {
  decisionDate: string;
  onDecisionChange: (d: string) => void;
}

export function ForecastDashboard({ decisionDate, onDecisionChange }: Props) {
  const state = useApiData((s) => api.getForecasts(decisionDate, undefined, s), [decisionDate]);
  const data = state.data;

  const [selected, setSelected] = useState<string | undefined>(undefined);
  useEffect(() => setSelected(undefined), [decisionDate]);
  const effective = selected ?? data?.intervals[0]?.start_time;

  const hist = useApiData<ForecastHistoryResponse | null>(
    (s) => (effective ? api.getForecastHistory(decisionDate, effective, s) : Promise.resolve(null)),
    [decisionDate, effective],
  );

  return (
    <section>
      <DecisionControls
        decisionDate={decisionDate}
        onChange={onDecisionChange}
        deliveryDate={data?.delivery_date}
        cutoff={data?.cutoff}
      />

      <div className="panel">
        <div className="panel__head">
          <h2>Forecast wind generation</h2>
          {data && (
            <span className="panel__meta">
              {data.intervals_count} hourly intervals
              {data.intervals_missing_forecast > 0 && ` · ${data.intervals_missing_forecast} with no eligible forecast`}
            </span>
          )}
        </div>
        <StateBoundary
          loading={state.loading}
          error={state.error}
          empty={!!data && data.intervals.length === 0}
          emptyMessage="No eligible forecast for this decision date at the cutoff."
          onRetry={() => onDecisionChange(decisionDate)}
        >
          {data && <GenerationChart data={toChartPoints(data.intervals)} />}
        </StateBoundary>
      </div>

      <div className="panel">
        <div className="panel__head">
          <h2>Forecast vintage history</h2>
          <label className="inline-select">
            Interval:
            <select value={effective ?? ""} onChange={(e) => setSelected(e.target.value)}>
              {data?.intervals.map((i) => (
                <option key={i.start_time} value={i.start_time}>
                  {formatTime(i.start_time)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="panel__note">
          Each publication is a forecast <em>vintage</em>. Only vintages published on or before the cutoff were
          eligible for this decision.
        </p>
        <StateBoundary
          loading={hist.loading}
          error={hist.error}
          empty={!!hist.data && hist.data.vintages.length === 0}
          emptyMessage="No vintages found for this interval."
        >
          {hist.data && (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Published</th>
                    <th>Forecast</th>
                    <th>Eligible at cutoff</th>
                  </tr>
                </thead>
                <tbody>
                  {hist.data.vintages.map((v) => (
                    <tr key={v.publish_time} className={v.eligible ? "" : "row--muted"}>
                      <td>{formatDateTime(v.publish_time)}</td>
                      <td className="num">{formatMW(v.forecast_mw)}</td>
                      <td>
                        <span className={`pill pill--${v.eligible ? "ok" : "off"}`}>
                          {v.eligible ? "eligible" : "after cutoff"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </StateBoundary>
      </div>
    </section>
  );
}
