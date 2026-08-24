from tests.conftest import auth_headers


def create_incident(client, token, title="Test Incident", severity="high"):
    return client.post(
        "/incidents/",
        json={"title": title, "severity": severity},
        headers=auth_headers(token)
    )


def test_create_incident(client, analyst_token):
    response = create_incident(client, analyst_token)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Test Incident"
    assert body["severity"] == "high"
    assert body["status"] == "open"


def test_list_incidents(client, analyst_token):
    create_incident(client, analyst_token)
    create_incident(client, analyst_token, title="Second")

    response = client.get("/incidents/", headers=auth_headers(analyst_token))

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_incident_status(client, analyst_token):
    incident = create_incident(client, analyst_token).json()

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "investigating"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "investigating"


def test_assign_incident(client, analyst_token):
    incident = create_incident(client, analyst_token).json()

    response = client.patch(
        f"/incidents/{incident['id']}/assign",
        json={"assigned_to": "analyst@example.com"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["assigned_to"] == "analyst@example.com"


def test_resolve_incident(client, analyst_token):
    incident = create_incident(client, analyst_token).json()

    response = client.patch(
        f"/incidents/{incident['id']}/resolve",
        json={"resolution_notes": "Root cause fixed"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    assert response.json()["resolution_notes"] == "Root cause fixed"


def test_update_nonexistent_incident_404(client, analyst_token):
    response = client.patch(
        "/incidents/99999",
        json={"status": "investigating"},
        headers=auth_headers(analyst_token)
    )

    assert response.status_code == 404


def test_unauthenticated_incident_access_rejected(client):
    response = client.get("/incidents/")

    assert response.status_code in (401, 403)
