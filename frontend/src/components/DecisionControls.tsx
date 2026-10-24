import { formatDate, formatDateTime } from "../lib/format";

interface Props {
  decisionDate: string; // YYYY-MM-DD
  onChange: (date: string) => void;
  deliveryDate?: string;
  cutoff?: string | null;
  min?: string;
  max?: string;
}

// Decision-date selector + derived delivery date + the purchasing cutoff.
export function DecisionControls({
  decisionDate,
  onChange,
  deliveryDate,
  cutoff,
  min = "2026-01-01",
  max = "2026-01-31",
}: Props) {
  return (
    <div className="controls">
      <label className="control">
        <span className="control__label">Decision date</span>
        <input
          type="date"
          value={decisionDate}
          min={min}
          max={max}
          onChange={(e) => onChange(e.target.value)}
        />
      </label>
      <div className="control">
        <span className="control__label">Delivery day</span>
        <span className="control__value">{deliveryDate ? formatDate(deliveryDate) : "—"}</span>
      </div>
      <div className="control">
        <span className="control__label">Purchasing cutoff</span>
        <span className="control__value">
          {formatDateTime(cutoff)}
          <span className="control__tag" title="Provisional assumption, not an official market deadline.">
            provisional
          </span>
        </span>
      </div>
    </div>
  );
}
