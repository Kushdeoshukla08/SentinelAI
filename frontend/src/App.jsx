import Sidebar from "./components/Sidebar";
import Login from "./components/Login";
import { useEffect, useState } from "react";
import { apiFetch, getToken, clearToken } from "./api";
import "./App.css";

function App() {
  const [authed, setAuthed] = useState(!!getToken());

  const [stats, setStats] = useState({
    total_logs: 0,
    total_alerts: 0,
    high_risk_events: 0,
    critical_alerts: 0,
  });

  const [logs, setLogs] = useState([]);
  const [mitreTechniques, setMitreTechniques] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [assets, setAssets] = useState([]);

  useEffect(() => {
    if (!authed) return;

    apiFetch("/dashboard/stats").then(setStats).catch(() => {});
    apiFetch("/mitre/").then(setMitreTechniques).catch(() => {});
    apiFetch("/logs/").then(setLogs).catch(() => {});
    apiFetch("/alerts/").then(setAlerts).catch(() => {});
    apiFetch("/incidents/").then(setIncidents).catch(() => {});
    apiFetch("/assets/").then(setAssets).catch(() => {});
  }, [authed]);

  function handleLogout() {
    clearToken();
    setAuthed(false);
  }

  if (!authed) {
    return <Login onLogin={() => setAuthed(true)} />;
  }

  return (
    <div className="layout">
      <Sidebar onLogout={handleLogout} />

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

        <div className="table-section">
          <h2>Security Alerts</h2>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Alert Type</th>
                <th>Source IP</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Assigned To</th>
              </tr>
            </thead>

            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id}>
                  <td>{alert.id}</td>
                  <td>{alert.alert_type}</td>
                  <td>{alert.source_ip}</td>
                  <td>
                    <span className="critical-badge">
                      {alert.severity}
                    </span>
                  </td>
                  <td>
                    <span className="status-badge">
                      {alert.status}
                    </span>
                  </td>
                  <td>
                    {alert.assigned_to || "Unassigned"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="table-section">
          <h2>Incident Management</h2>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Assigned To</th>
              </tr>
            </thead>

            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id}>
                  <td>{incident.id}</td>
                  <td>{incident.title}</td>
                  <td>
                    <span className="critical-badge">
                      {incident.severity}
                    </span>
                  </td>
                  <td>
                    <span className="status-badge">
                      {incident.status}
                    </span>
                  </td>
                  <td>
                    {incident.assigned_to || "Unassigned"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
                </div>

        <div className="table-section">
          <h2>Asset Inventory</h2>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Environment</th>
                <th>Criticality</th>
                <th>Status</th>
                <th>Risk Score</th>
              </tr>
            </thead>

            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.id}</td>
                  <td>{asset.name}</td>
                  <td>{asset.asset_type}</td>
                  <td>{asset.environment}</td>
                  <td>
                    <span className="critical-badge">
                      {asset.criticality}
                    </span>
                  </td>
                  <td>
                    <span className="status-badge">
                      {asset.status}
                    </span>
                  </td>
                  <td>{asset.risk_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="table-section">
          <h2>MITRE ATT&CK Techniques</h2>

          <table>
            <thead>
              <tr>
                <th>Technique ID</th>
                <th>Name</th>
                <th>Tactic</th>
              </tr>
            </thead>

            <tbody>
              {mitreTechniques.map((technique) => (
                <tr key={technique.technique_id}>
                  <td>{technique.technique_id}</td>
                  <td>{technique.name}</td>
                  <td>{technique.tactic}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}

export default App;