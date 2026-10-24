import { api } from "../api/client";
import { MetricCards } from "../components/MetricCards";
import { StateBoundary } from "../components/StateBoundary";
import { useApiData } from "../hooks/useApiData";
import { ViewKey } from "../components/Sidebar";
import { formatDate } from "../lib/format";

interface Props {
  decisionDate: string;
  onNavigate: (v: ViewKey) => void;
}

export function Overview({ decisionDate, onNavigate }: Props) {
  const state = useApiData((s) => api.getAccuracy(decisionDate, undefined, s), [decisionDate]);
  const data = state.data;

  return (
    <section>
      <div className="intro">
        <p>
          This portal helps the day-ahead purchasing team see the latest eligible <strong>national wind
          generation forecast</strong> at decision time and understand how accurate those forecasts have been.
          Scope: Elexon national wind, decisions made in <strong>January 2026</strong> (next-day delivery).
        </p>
        <div className="intro__actions">
          <button className="btn btn--primary" onClick={() => onNavigate("forecast")}>
            View forecast
          </button>
          <button className="btn" onClick={() => onNavigate("accuracy")}>
            View accuracy
          </button>
        </div>
      </div>

      <div className="panel">
        <div className="panel__head">
          <h2>Accuracy snapshot</h2>
          <span className="panel__meta">
            decision {formatDate(decisionDate)} → delivery {data ? formatDate(data.delivery_range.start) : "—"}
          </span>
        </div>
        <StateBoundary loading={state.loading} error={state.error}>
          {data && <MetricCards metrics={data.metrics} />}
        </StateBoundary>
      </div>

      <p className="scope-note">
        Scope limitation: these datasets cover national wind only. The portal quantifies wind forecast
        uncertainty; it does not compute an electricity shortfall or a recommended purchase quantity.
      </p>
    </section>
  );
}
