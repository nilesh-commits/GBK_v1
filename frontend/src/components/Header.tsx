import { api } from "../api/client";
import { HealthResponse } from "../api/types";
import { ApiState } from "../hooks/useApiData";

interface Props {
  title: string;
  subtitle: string;
  health: ApiState<HealthResponse>;
}

export function Header({ title, subtitle, health }: Props) {
  const ok = !health.loading && !health.error && health.data?.data_loaded;
  const statusLabel = health.loading
    ? "checking…"
    : health.error
      ? "unreachable"
      : health.data?.data_loaded
        ? "connected"
        : "no data loaded";
  const statusClass = ok ? "ok" : health.loading ? "pending" : "bad";

  return (
    <header className="header">
      <div>
        <h1 className="header__title">{title}</h1>
        <p className="header__subtitle">{subtitle}</p>
      </div>
      <div className="header__status">
        <span className={`dot dot--${statusClass}`} aria-hidden />
        <div className="header__status-text">
          <span>API {statusLabel}</span>
          <small title={api.baseUrl}>
            {health.data ? `${health.data.intervals_cached.toLocaleString("en-GB")} intervals cached` : api.baseUrl}
          </small>
        </div>
      </div>
    </header>
  );
}
