from tests.conftest import auth_headers


def trigger_brute_force(client, token, source_ip="203.0.113.5"):
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
    alert = next(a for a in alerts if a["source_ip"] == source_ip)

    incidents = client.get("/incidents/", headers=auth_headers(token)).json()
    incident = next(i for i in incidents if i["title"] == "Brute Force Attack Detected")

    return alert, incident


def trigger_ioc_match(client, token, ip="185.220.101.50"):
    client.post(
        "/iocs/",
        json={
            "ioc_type": "ip",
            "value": ip,
            "source": "test-feed",
            "confidence": 95,
            "severity": "critical",
            "tags": "botnet"
        },
        headers=auth_headers(token)
    )

    client.post(
        "/logs/upload",
        json={"source_ip": ip, "event_type": "login_success", "username": "admin"},
        headers=auth_headers(token)
    )

    alerts = client.get("/alerts/", headers=auth_headers(token)).json()
    alert = next(a for a in alerts if a["alert_type"] == "Known Malicious IP")

    incidents = client.get("/incidents/", headers=auth_headers(token)).json()
    incident = next(i for i in incidents if i["title"] == "Known Malicious IP Detected")

    return alert, incident


def test_explain_brute_force_alert_uses_local_provider_with_real_evidence(client, analyst_token):
    alert, _ = trigger_brute_force(client, analyst_token)

    response = client.get(f"/ai/alerts/{alert['id']}/explain", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "local"
    assert "203.0.113.5" in body["summary"]
    assert len(body["evidence"]) == 5
    assert all("failed_login" in e for e in body["evidence"])
    assert body["confidence"] == 90
    assert body["severity"] == "critical"
    assert "MFA" in body["recommended_action"] or "multi-factor" in body["recommended_action"]


def test_explain_known_malicious_ip_alert_references_the_ioc(client, analyst_token):
    alert, _ = trigger_ioc_match(client, analyst_token)

    response = client.get(f"/ai/alerts/{alert['id']}/explain", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    body = response.json()
    assert body["confidence"] == 95
    assert any("test-feed" in e for e in body["evidence"])
    assert any("botnet" in e for e in body["evidence"])


def test_explain_nonexistent_alert_404(client, analyst_token):
    response = client.get("/ai/alerts/99999/explain", headers=auth_headers(analyst_token))

    assert response.status_code == 404


def test_explain_alert_requires_auth(client):
    response = client.get("/ai/alerts/1/explain")

    assert response.status_code in (401, 403)


def test_explain_incident_correlates_related_alerts(client, analyst_token):
    _, incident = trigger_brute_force(client, analyst_token)

    response = client.get(f"/ai/incidents/{incident['id']}/explain", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "local"
    assert "1 related alert" in body["summary"]
    assert len(body["evidence"]) == 1
    assert "Brute Force Attack" in body["evidence"][0]
    assert body["confidence"] == 85


def test_explain_incident_with_no_correlated_alerts(client, admin_token):
    incident = client.post(
        "/incidents/",
        json={"title": "Manually created incident", "severity": "low"},
        headers=auth_headers(admin_token)
    ).json()

    response = client.get(f"/ai/incidents/{incident['id']}/explain", headers=auth_headers(admin_token))

    body = response.json()
    assert body["evidence"] == []
    assert body["confidence"] == 40


def test_explain_resolved_incident_uses_resolution_notes_as_recommended_action(client, analyst_token):
    incident = client.post(
        "/incidents/",
        json={"title": "Manually created incident", "severity": "low"},
        headers=auth_headers(analyst_token)
    ).json()

    client.patch(
        f"/incidents/{incident['id']}/resolve",
        json={"resolution_notes": "Rotated the exposed credential"},
        headers=auth_headers(analyst_token)
    )

    response = client.get(f"/ai/incidents/{incident['id']}/explain", headers=auth_headers(analyst_token))

    assert response.json()["recommended_action"] == "Rotated the exposed credential"


def test_explain_nonexistent_incident_404(client, analyst_token):
    response = client.get("/ai/incidents/99999/explain", headers=auth_headers(analyst_token))

    assert response.status_code == 404


def test_viewer_can_read_ai_explanations(client, analyst_token, viewer_token):
    alert, _ = trigger_brute_force(client, analyst_token)

    response = client.get(f"/ai/alerts/{alert['id']}/explain", headers=auth_headers(viewer_token))

    assert response.status_code == 200
