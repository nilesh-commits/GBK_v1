// Response contracts (mirror backend docs/05-api-reference.md).

export interface HealthResponse {
  status: string;
  data_loaded: boolean;
  intervals_cached: number;
}

export interface ForecastInterval {
  start_time: string;
  forecast_mw: number | null;
  publish_time: string | null;
}

export interface ForecastsResponse {
  decision_date: string;
  delivery_date: string;
  cutoff: string;
  unit: string;
  intervals: ForecastInterval[];
  intervals_count: number;
  intervals_missing_forecast: number;
}

export interface VintageItem {
  start_time: string;
  publish_time: string;
  forecast_mw: number;
  eligible: boolean;
}

export interface ForecastHistoryResponse {
  decision_date: string;
  delivery_date: string;
  cutoff: string;
  start_time: string | null;
  unit: string;
  vintages: VintageItem[];
}

export interface AccuracySeriesItem {
  start_time: string;
  forecast_mw: number | null;
  actual_mw: number | null;
  error_mw: number | null;
  abs_error_mw: number | null;
}

export interface Metrics {
  mae: number | null;
  rmse: number | null;
  bias: number | null;
  matched_intervals: number;
}

export interface DateRange {
  start: string;
  end: string;
}

export interface AccuracyResponse {
  decision_range: DateRange;
  delivery_range: DateRange;
  cutoff: string | null;
  unit: string;
  metrics: Metrics;
  series: AccuracySeriesItem[];
  excluded: { missing_forecast: number; missing_actual: number };
}

export class ApiError extends Error {
  code: string;
  details: unknown;
  constructor(code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
  }
}
