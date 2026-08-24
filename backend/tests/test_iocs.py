from tests.conftest import auth_headers


def create_ioc(client, token, value="198.51.100.99", ioc_type="ip", severity="high"):
    return client.post(
        "/iocs/",
        json={
            "ioc_type": ioc_type,
            "value": value,
            "source": "manual",
            "confidence": 80,
            "severity": severity,
            "tags": "test,malicious"
        },
        headers=auth_headers(token)
    )


def test_create_ioc(client, analyst_token):
    response = create_ioc(client, analyst_token)

    assert response.status_code == 200
    body = response.json()
    assert body["ioc_type"] == "ip"
    assert body["value"] == "198.51.100.99"
    assert body["is_active"] is True


def test_invalid_ioc_type_rejected(client, analyst_token):
    response = client.post(
        "/iocs/",
        json={"ioc_type": "carrier-pigeon", "value": "x"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 400


def test_invalid_confidence_rejected(client, analyst_token):
    response = client.post(
        "/iocs/",
        json={"ioc_type": "ip", "value": "1.2.3.4", "confidence": 500},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 400


def test_duplicate_ioc_rejected(client, analyst_token):
    create_ioc(client, analyst_token)
    response = create_ioc(client, analyst_token)

    assert response.status_code == 400


def test_list_iocs(client, analyst_token):
    create_ioc(client, analyst_token, value="1.1.1.1")
    create_ioc(client, analyst_token, value="2.2.2.2")

    response = client.get("/iocs/", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_nonexistent_ioc_404(client, analyst_token):
    response = client.get("/iocs/99999", headers=auth_headers(analyst_token))

    assert response.status_code == 404


def test_update_ioc(client, analyst_token):
    ioc = create_ioc(client, analyst_token).json()

    response = client.patch(
        f"/iocs/{ioc['id']}",
        json={"is_active": False, "severity": "low"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert response.json()["severity"] == "low"


def test_viewer_cannot_create_ioc(client, viewer_token):
    response = client.post(
        "/iocs/",
        json={"ioc_type": "ip", "value": "9.9.9.9"},
        headers=auth_headers(viewer_token)
    )

    assert response.status_code == 403


def test_only_admin_can_delete_ioc(client, analyst_token):
    ioc = create_ioc(client, analyst_token).json()

    response = client.delete(f"/iocs/{ioc['id']}", headers=auth_headers(analyst_token))

    assert response.status_code == 403


def test_log_upload_matches_active_ip_ioc(client, analyst_token):
    create_ioc(client, analyst_token, value="203.0.113.66", severity="critical")

    response = client.post(
        "/logs/upload",
        json={
            "source_ip": "203.0.113.66",
            "event_type": "login_success",
            "username": "someuser"
        },
        headers=auth_headers(analyst_token)
    )

    body = response.json()
    assert body["risk_score"] == 100
    assert body["severity"] == "critical"
    assert body["ioc_matched"] is True
    assert body["alert_generated"] is True

    alerts = client.get("/alerts/", headers=auth_headers(analyst_token)).json()
    ioc_alert = next(a for a in alerts if a["alert_type"] == "Known Malicious IP")
    assert ioc_alert["source_ip"] == "203.0.113.66"
    assert ioc_alert["severity"] == "critical"

    incidents = client.get("/incidents/", headers=auth_headers(analyst_token)).json()
    assert any(i["title"] == "Known Malicious IP Detected" for i in incidents)


def test_log_upload_does_not_match_inactive_ioc(client, analyst_token):
    ioc = create_ioc(client, analyst_token, value="203.0.113.77").json()

    client.patch(
        f"/iocs/{ioc['id']}",
        json={"is_active": False},
        headers=auth_headers(analyst_token)
    )

    response = client.post(
        "/logs/upload",
        json={
            "source_ip": "203.0.113.77",
            "event_type": "login_success",
            "username": "someuser"
        },
        headers=auth_headers(analyst_token)
    )

    assert response.json()["ioc_matched"] is False


def test_repeated_ioc_matches_do_not_duplicate_alert(client, analyst_token):
    create_ioc(client, analyst_token, value="203.0.113.88")

    for _ in range(3):
        client.post(
            "/logs/upload",
            json={
                "source_ip": "203.0.113.88",
                "event_type": "login_success",
                "username": "someuser"
            },
            headers=auth_headers(analyst_token)
        )

    alerts = client.get("/alerts/", headers=auth_headers(analyst_token)).json()
    matching = [a for a in alerts if a["alert_type"] == "Known Malicious IP" and a["source_ip"] == "203.0.113.88"]
    assert len(matching) == 1


def test_ioc_last_seen_updates_on_match(client, analyst_token):
    ioc = create_ioc(client, analyst_token, value="203.0.113.99").json()
    original_last_seen = ioc["last_seen"]

    client.post(
        "/logs/upload",
        json={
            "source_ip": "203.0.113.99",
            "event_type": "login_success",
            "username": "someuser"
        },
        headers=auth_headers(analyst_token)
    )

    updated = client.get(f"/iocs/{ioc['id']}", headers=auth_headers(analyst_token)).json()
    assert updated["last_seen"] >= original_last_seen
