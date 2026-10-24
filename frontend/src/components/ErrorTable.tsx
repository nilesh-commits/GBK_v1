import { useMemo, useState } from "react";
import { AccuracySeriesItem } from "../api/types";
import { formatMW, formatSigned, formatTime } from "../lib/format";

type SortKey = "start_time" | "forecast_mw" | "actual_mw" | "error_mw" | "abs_error_mw";

interface Props {
  series: AccuracySeriesItem[];
}

export function ErrorTable({ series }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("start_time");
  const [asc, setAsc] = useState(true);

  const rows = useMemo(() => {
    const sorted = [...series].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (av === null) return 1;
      if (bv === null) return -1;
      if (av < bv) return asc ? -1 : 1;
      if (av > bv) return asc ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [series, sortKey, asc]);

  const header = (key: SortKey, label: string) => (
    <th>
      <button
        className={`th-sort${sortKey === key ? " is-active" : ""}`}
        onClick={() => {
          if (sortKey === key) setAsc((v) => !v);
          else {
            setSortKey(key);
            setAsc(true);
          }
        }}
        aria-label={`Sort by ${label}`}
      >
        {label}
        {sortKey === key ? (asc ? " ▲" : " ▼") : ""}
      </button>
    </th>
  );

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {header("start_time", "Delivery time")}
            {header("forecast_mw", "Forecast")}
            {header("actual_mw", "Actual")}
            {header("error_mw", "Error")}
            {header("abs_error_mw", "Abs error")}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.start_time} className={r.error_mw === null ? "row--missing" : ""}>
              <td>{formatTime(r.start_time)}</td>
              <td className="num">{formatMW(r.forecast_mw)}</td>
              <td className="num">{formatMW(r.actual_mw)}</td>
              <td className="num">{formatSigned(r.error_mw)}</td>
              <td className="num">{formatMW(r.abs_error_mw)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
