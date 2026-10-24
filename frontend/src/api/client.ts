// Centralized API client. Reads the backend base URL from VITE_API_URL,
// normalizes the backend error shape, and supports request cancellation.
import {
  AccuracyResponse,
  ApiError,
  ForecastHistoryResponse,
  ForecastsResponse,
  HealthResponse,
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, params: Record<string, string>, signal?: AbortSignal): Promise<T> {
  const qs = new URLSearchParams(params).toString();
  const url = `${BASE_URL}${path}${qs ? `?${qs}` : ""}`;
  let resp: Response;
  try {
    resp = await fetch(url, { signal, headers: { Accept: "application/json" } });
  } catch (err) {
    if (signal?.aborted) throw err; // bubbled and ignored by the caller
    throw new ApiError("NETWORK_ERROR", "Could not reach the API. Is the backend running?");
  }

  let body: unknown = null;
  try {
    body = await resp.json();
  } catch {
    // leave body null
  }

  if (!resp.ok) {
    const e = (body as { error?: { code?: string; message?: string; details?: unknown } } | null)?.error;
    throw new ApiError(
      e?.code ?? "HTTP_ERROR",
      e?.message ?? `Request failed (${resp.status}).`,
      e?.details,
    );
  }
  return body as T;
}

export const api = {
  baseUrl: BASE_URL,

  getHealth: (signal?: AbortSignal) => request<HealthResponse>("/api/health", {}, signal),

  getForecasts: (decisionDate: string, cutoff?: string, signal?: AbortSignal) =>
    request<ForecastsResponse>(
      "/api/forecasts",
      cutoff ? { decision_date: decisionDate, cutoff } : { decision_date: decisionDate },
      signal,
    ),

  getForecastHistory: (decisionDate: string, startTime?: string, signal?: AbortSignal) =>
    request<ForecastHistoryResponse>(
      "/api/forecasts/history",
      startTime ? { decision_date: decisionDate, start_time: startTime } : { decision_date: decisionDate },
      signal,
    ),

  getAccuracy: (decisionDate: string, cutoff?: string, signal?: AbortSignal) =>
    request<AccuracyResponse>(
      "/api/accuracy",
      cutoff ? { decision_date: decisionDate, cutoff } : { decision_date: decisionDate },
      signal,
    ),
};
