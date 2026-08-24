import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

import { Pie } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

function Analytics({ alerts, incidents }) {
  const alertData = {
    labels: ["Critical", "Other"],
    datasets: [
      {
        data: [
          alerts.filter(
            (a) => a.severity === "critical"
          ).length,
          alerts.filter(
            (a) => a.severity !== "critical"
          ).length,
        ],
      },
    ],
  };

  const incidentData = {
    labels: ["Resolved", "Open"],
    datasets: [
      {
        data: [
          incidents.filter(
            (i) => i.status === "resolved"
          ).length,
          incidents.filter(
            (i) => i.status !== "resolved"
          ).length,
        ],
      },
    ],
  };

  return (
    <div className="analytics-grid">

      <div className="chart-card">
        <h2>Alert Severity Distribution</h2>
        <Pie data={alertData} />
      </div>

      <div className="chart-card">
        <h2>Incident Status</h2>
        <Pie data={incidentData} />x4
      </div>

    </div>
  );
}

export default Analytics;
