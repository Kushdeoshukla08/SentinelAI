from tests.conftest import auth_headers


def create_asset(client, token, name="Web Server 1", ip_address="203.0.113.10"):
    return client.post(
        "/assets/",
        json={
            "name": name,
            "asset_type": "server",
            "owner": "infra-team",
            "criticality": "high",
            "environment": "production",
            "ip_address": ip_address
        },
        headers=auth_headers(token)
    )


def test_create_asset(client, analyst_token):
    response = create_asset(client, analyst_token)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Web Server 1"
    assert body["criticality"] == "high"
    assert body["status"] == "active"
    assert body["risk_score"] == 0


def test_invalid_criticality_rejected(client, analyst_token):
    response = client.post(
        "/assets/",
        json={
            "name": "Bad Asset",
            "asset_type": "server",
            "criticality": "extreme"
        },
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 400


def test_list_assets(client, analyst_token):
    create_asset(client, analyst_token, name="Server A", ip_address="10.0.0.1")
    create_asset(client, analyst_token, name="Server B", ip_address="10.0.0.2")

    response = client.get("/assets/", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_single_asset(client, analyst_token):
    asset = create_asset(client, analyst_token).json()

    response = client.get(f"/assets/{asset['id']}", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    assert response.json()["id"] == asset["id"]


def test_get_nonexistent_asset_404(client, analyst_token):
    response = client.get("/assets/99999", headers=auth_headers(analyst_token))

    assert response.status_code == 404


def test_update_asset(client, analyst_token):
    asset = create_asset(client, analyst_token).json()

    response = client.patch(
        f"/assets/{asset['id']}",
        json={"criticality": "critical", "status": "inactive"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["criticality"] == "critical"
    assert response.json()["status"] == "inactive"


def test_invalid_status_update_rejected(client, analyst_token):
    asset = create_asset(client, analyst_token).json()

    response = client.patch(
        f"/assets/{asset['id']}",
        json={"status": "on-fire"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 400


def test_viewer_cannot_create_asset(client, viewer_token):
    response = client.post(
        "/assets/",
        json={"name": "Should fail", "asset_type": "server"},
        headers=auth_headers(viewer_token)
    )

    assert response.status_code == 403


def test_viewer_can_list_assets(client, viewer_token):
    response = client.get("/assets/", headers=auth_headers(viewer_token))

    assert response.status_code == 200


def test_only_admin_can_delete_asset(client, analyst_token):
    asset = create_asset(client, analyst_token).json()

    response = client.delete(f"/assets/{asset['id']}", headers=auth_headers(analyst_token))

    assert response.status_code == 403


def test_admin_can_delete_asset(client, admin_token):
    asset = create_asset(client, admin_token).json()

    response = client.delete(f"/assets/{asset['id']}", headers=auth_headers(admin_token))
    assert response.status_code == 200

    follow_up = client.get(f"/assets/{asset['id']}", headers=auth_headers(admin_token))
    assert follow_up.status_code == 404


def test_asset_risk_score_reflects_unresolved_alerts(client, analyst_token):
    asset = create_asset(client, analyst_token, ip_address="192.0.2.50").json()

    for _ in range(5):
        client.post(
            "/logs/upload",
            json={
                "source_ip": "192.0.2.50",
                "event_type": "failed_login",
                "username": "admin"
            },
            headers=auth_headers(analyst_token)
        )

    response = client.get(f"/assets/{asset['id']}", headers=auth_headers(analyst_token))

    assert response.json()["risk_score"] == 40


def test_asset_risk_score_drops_after_alert_resolved(client, analyst_token):
    asset = create_asset(client, analyst_token, ip_address="192.0.2.60").json()

    for _ in range(5):
        client.post(
            "/logs/upload",
            json={
                "source_ip": "192.0.2.60",
                "event_type": "failed_login",
                "username": "admin"
            },
            headers=auth_headers(analyst_token)
        )

    alerts = client.get("/alerts/", headers=auth_headers(analyst_token)).json()
    alert = next(a for a in alerts if a["source_ip"] == "192.0.2.60")

    client.patch(
        f"/alerts/{alert['id']}/resolve",
        json={"resolution_notes": "handled"},
        headers=auth_headers(analyst_token)
    )

    response = client.get(f"/assets/{asset['id']}", headers=auth_headers(analyst_token))
    assert response.json()["risk_score"] == 0
