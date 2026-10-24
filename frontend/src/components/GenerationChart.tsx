import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatTime } from "../lib/format";

export interface ChartPoint {
  time: string; // formatted HH:mm
  forecast: number | null;
  actual?: number | null;
}

interface Props {
  data: ChartPoint[];
  showActual?: boolean;
}

export function GenerationChart({ data, showActual = false }: Props) {
  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
          <XAxis dataKey="time" tick={{ fontSize: 12 }} minTickGap={24} />
          <YAxis
            tick={{ fontSize: 12 }}
            width={64}
            label={{ value: "MW", angle: -90, position: "insideLeft", fontSize: 12 }}
          />
          <Tooltip formatter={(v: number) => `${Math.round(v).toLocaleString("en-GB")} MW`} />
          <Legend />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
          />
          {showActual && (
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual"
              stroke="var(--ink)"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Helper to turn ISO-stamped series into chart points.
export function toChartPoints(
  rows: { start_time: string; forecast_mw: number | null; actual_mw?: number | null }[],
): ChartPoint[] {
  return rows.map((r) => ({
    time: formatTime(r.start_time),
    forecast: r.forecast_mw,
    actual: r.actual_mw ?? null,
  }));
}
