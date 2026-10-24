export type ViewKey = "overview" | "forecast" | "accuracy" | "methodology";

const NAV: { key: ViewKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "forecast", label: "Forecast Analysis" },
  { key: "accuracy", label: "Accuracy Analysis" },
  { key: "methodology", label: "Data & Methodology" },
];

interface Props {
  active: ViewKey;
  onSelect: (key: ViewKey) => void;
}

export function Sidebar({ active, onSelect }: Props) {
  return (
    <nav className="sidebar" aria-label="Primary">
      <div className="sidebar__brand">
        <span className="sidebar__mark" aria-hidden>
          ◐
        </span>
        <span>Wind Portal</span>
      </div>
      <ul className="sidebar__nav">
        {NAV.map((item) => (
          <li key={item.key}>
            <button
              className={`sidebar__link${active === item.key ? " is-active" : ""}`}
              aria-current={active === item.key ? "page" : undefined}
              onClick={() => onSelect(item.key)}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
      <p className="sidebar__foot">UK day-ahead wind · Jan 2026</p>
    </nav>
  );
}
