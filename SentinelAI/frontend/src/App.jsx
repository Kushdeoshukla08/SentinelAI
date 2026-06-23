import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [stats, setStats] = useState({
    total_logs: 0,
    total_alerts: 0,
    high_risk_events: 0,
    critical_alerts: 0,
  });

  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/dashboard/stats")
      .then((response) => response.json())
      .then((data) => {
        setStats(data);
      });

    fetch("http://127.0.0.1:8000/logs/")
      .then((response) => response.json())
      .then((data) => {
        setLogs(data);
      });
  }, []);

  return (
    <div className="dashboard">
      <h1>🛡️ SentinelAI SOC Dashboard</h1>

      <div className="stats-grid">
        <div className="card">
          <h2>Total Logs</h2>
          <p>{stats.total_logs}</p>
        </div>

        <div className="card">
          <h2>Total Alerts</h2>
          <p>{stats.total_alerts}</p>
        </div>

        <div className="card">
          <h2>Critical Alerts</h2>
          <p>{stats.critical_alerts}</p>
        </div>

        <div className="card">
          <h2>High Risk Events</h2>
          <p>{stats.high_risk_events}</p>
        </div>
      </div>

      <div className="table-section">
        <h2>Recent Security Logs</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>IP Address</th>
              <th>Event Type</th>
              <th>User</th>
              <th>Risk Score</th>
              <th>Severity</th>
            </tr>
          </thead>

          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>{log.source_ip}</td>
                <td>{log.event_type}</td>
                <td>{log.username}</td>
                <td>{log.risk_score}</td>
                <td>{log.severity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;