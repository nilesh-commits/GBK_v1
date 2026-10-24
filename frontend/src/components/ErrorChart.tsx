import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AccuracySeriesItem } from "../api/types";
import { formatTime } from "../lib/format";

interface Props {
  series: AccuracySeriesItem[];
}

// Forecast error (forecast - actual) over time, with a zero reference line.
export function ErrorChart({ series }: Props) {
  const data = series
    .filter((r) => r.error_mw !== null)
    .map((r) => ({ time: formatTime(r.start_time), error: r.error_mw as number }));

  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
          <XAxis dataKey="time" tick={{ fontSize: 12 }} minTickGap={24} />
          <YAxis
            tick={{ fontSize: 12 }}
            width={64}
            label={{ value: "Error (MW)", angle: -90, position: "insideLeft", fontSize: 12 }}
          />
          <Tooltip formatter={(v: number) => `${v > 0 ? "+" : ""}${Math.round(v).toLocaleString("en-GB")} MW`} />
          <ReferenceLine y={0} stroke="var(--ink)" />
          <Bar dataKey="error" name="Error" fill="var(--accent)" />
        </BarChart>
      </ResponsiveContainer>
      <p className="chart__note">Positive = over-forecast (forecast above actual); negative = under-forecast.</p>
    </div>
  );
}
