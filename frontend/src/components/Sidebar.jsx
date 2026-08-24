function Sidebar({ onLogout }) {
  return (
    <div className="sidebar">
      <h2>🛡 SentinelAI</h2>

      <ul>
        <li>📊 Dashboard</li>
        <li>📜 Logs</li>
        <li>🚨 Alerts</li>
        <li>🛠 Incidents</li>
        <li>🖥 Assets</li>
        <li>🎯 MITRE ATT&CK</li>
      </ul>

      <button className="logout-btn" onClick={onLogout}>
        🚪 Logout
      </button>
    </div>
  );
}

export default Sidebar;