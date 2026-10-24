import { useState } from "react";
import { api } from "./api/client";
import { Header } from "./components/Header";
import { Sidebar, ViewKey } from "./components/Sidebar";
import { useApiData } from "./hooks/useApiData";
import { formatDate } from "./lib/format";
import { AccuracyAnalysis } from "./views/AccuracyAnalysis";
import { DataMethodology } from "./views/DataMethodology";
import { ForecastDashboard } from "./views/ForecastDashboard";
import { Overview } from "./views/Overview";

const TITLES: Record<ViewKey, string> = {
  overview: "Overview",
  forecast: "Forecast Analysis",
  accuracy: "Accuracy Analysis",
  methodology: "Data & Methodology",
};

export function App() {
  const [view, setView] = useState<ViewKey>("overview");
  const [decisionDate, setDecisionDate] = useState("2026-01-15");
  const health = useApiData((s) => api.getHealth(s), []);

  const subtitle =
    view === "methodology"
      ? "How the forecast and accuracy analysis are produced"
      : `Decision date ${formatDate(decisionDate)} · next-day delivery`;

  return (
    <div className="layout">
      <Sidebar active={view} onSelect={setView} />
      <main className="main">
        <Header title={TITLES[view]} subtitle={subtitle} health={health} />
        <div className="content">
          {view === "overview" && <Overview decisionDate={decisionDate} onNavigate={setView} />}
          {view === "forecast" && (
            <ForecastDashboard decisionDate={decisionDate} onDecisionChange={setDecisionDate} />
          )}
          {view === "accuracy" && (
            <AccuracyAnalysis decisionDate={decisionDate} onDecisionChange={setDecisionDate} />
          )}
          {view === "methodology" && <DataMethodology />}
        </div>
      </main>
    </div>
  );
}
