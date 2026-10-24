import { ReactNode } from "react";
import { ApiError } from "../api/types";

interface Props {
  loading: boolean;
  error: ApiError | null;
  empty?: boolean;
  emptyMessage?: string;
  onRetry?: () => void;
  children: ReactNode;
}

// Renders loading / error / empty explicitly; otherwise the children.
export function StateBoundary({ loading, error, empty, emptyMessage, onRetry, children }: Props) {
  if (loading) {
    return (
      <div className="state state--loading" role="status" aria-live="polite">
        <div className="spinner" aria-hidden />
        <span>Loading…</span>
      </div>
    );
  }
  if (error) {
    return (
      <div className="state state--error" role="alert">
        <strong>Could not load data</strong>
        <p>{error.message}</p>
        <p className="state__code">{error.code}</p>
        {onRetry && (
          <button className="btn" onClick={onRetry}>
            Retry
          </button>
        )}
      </div>
    );
  }
  if (empty) {
    return <div className="state state--empty">{emptyMessage ?? "No data for this selection."}</div>;
  }
  return <>{children}</>;
}
