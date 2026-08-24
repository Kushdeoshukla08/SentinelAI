from tests.conftest import auth_headers


def upload_log(client, token, source_ip="198.51.100.1", event_type="login_success", username="admin"):
    return client.post(
        "/logs/upload",
        json={"source_ip": source_ip, "event_type": event_type, "username": username},
        headers=auth_headers(token)
    )


def test_log_upload_calculates_risk(client, analyst_token):
    response = upload_log(client, analyst_token, event_type="failed_login")

    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] == 85
    assert body["severity"] == "high"
    assert body["mitre_technique"] == "T1110"


def test_log_upload_requires_auth(client):
    response = client.post(
        "/logs/upload",
        json={"source_ip": "1.2.3.4", "event_type": "login_success", "username": "admin"}
    )

    assert response.status_code in (401, 403)


def test_no_alert_below_brute_force_threshold(client, analyst_token):
    for _ in range(4):
        response = upload_log(client, analyst_token, source_ip="192.0.2.9", event_type="failed_login")

    assert response.json()["alert_generated"] is False

    alerts = client.get("/alerts/", headers=auth_headers(analyst_token)).json()
    assert alerts == []


def test_brute_force_threshold_creates_alert_and_incident(client, analyst_token):
    for _ in range(5):
        response = upload_log(client, analyst_token, source_ip="192.0.2.10", event_type="failed_login")

    assert response.json()["alert_generated"] is True

    alerts = client.get("/alerts/", headers=auth_headers(analyst_token)).json()
    assert len(alerts) == 1
    assert alerts[0]["source_ip"] == "192.0.2.10"
    assert alerts[0]["alert_type"] == "Brute Force Attack"

    incidents = client.get("/incidents/", headers=auth_headers(analyst_token)).json()
    assert len(incidents) == 1
    assert incidents[0]["title"] == "Brute Force Attack Detected"


def test_repeated_brute_force_does_not_duplicate_alert(client, analyst_token):
    for _ in range(7):
        upload_log(client, analyst_token, source_ip="192.0.2.20", event_type="failed_login")

    alerts = client.get("/alerts/", headers=auth_headers(analyst_token)).json()
    matching = [a for a in alerts if a["source_ip"] == "192.0.2.20"]
    assert len(matching) == 1


def test_get_logs_lists_uploaded_logs(client, analyst_token):
    upload_log(client, analyst_token)
    upload_log(client, analyst_token)

    response = client.get("/logs/", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    assert len(response.json()) == 2
