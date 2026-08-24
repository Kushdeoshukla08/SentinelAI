from tests.conftest import auth_headers


def trigger_brute_force_alert(client, token, source_ip="203.0.113.5"):
    for _ in range(5):
        client.post(
            "/logs/upload",
            json={
                "source_ip": source_ip,
                "event_type": "failed_login",
                "username": "admin"
            },
            headers=auth_headers(token)
        )

    alerts = client.get("/alerts/", headers=auth_headers(token)).json()
    return next(a for a in alerts if a["source_ip"] == source_ip)


def test_list_alerts_empty(client, analyst_token):
    response = client.get("/alerts/", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    assert response.json() == []


def test_brute_force_pipeline_creates_alert_with_new_status(client, analyst_token):
    alert = trigger_brute_force_alert(client, analyst_token)

    assert alert["status"] == "new"
    assert alert["assigned_to"] is None
    assert alert["severity"] == "critical"


def test_update_alert_status(client, analyst_token):
    alert = trigger_brute_force_alert(client, analyst_token)

    response = client.patch(
        f"/alerts/{alert['id']}",
        json={"status": "acknowledged"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_invalid_alert_status_rejected(client, analyst_token):
    alert = trigger_brute_force_alert(client, analyst_token)

    response = client.patch(
        f"/alerts/{alert['id']}",
        json={"status": "not-a-real-status"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 400


def test_assign_alert(client, analyst_token):
    alert = trigger_brute_force_alert(client, analyst_token)

    response = client.patch(
        f"/alerts/{alert['id']}/assign",
        json={"assigned_to": "analyst@example.com"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["assigned_to"] == "analyst@example.com"


def test_resolve_alert(client, analyst_token):
    alert = trigger_brute_force_alert(client, analyst_token)

    response = client.patch(
        f"/alerts/{alert['id']}/resolve",
        json={"resolution_notes": "Blocked at firewall"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_update_nonexistent_alert_404(client, analyst_token):
    response = client.patch(
        "/alerts/99999",
        json={"status": "acknowledged"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 404


def test_viewer_cannot_modify_alert(client, analyst_token, viewer_token):
    alert = trigger_brute_force_alert(client, analyst_token)

    response = client.patch(
        f"/alerts/{alert['id']}",
        json={"status": "acknowledged"},
        headers=auth_headers(viewer_token)
    )

    assert response.status_code == 403
