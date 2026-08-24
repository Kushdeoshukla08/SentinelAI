from tests.conftest import auth_headers


def test_analyst_cannot_access_audit_log(client, analyst_token):
    response = client.get("/audit/", headers=auth_headers(analyst_token))

    assert response.status_code == 403


def test_analyst_cannot_list_users(client, analyst_token):
    response = client.get("/users/", headers=auth_headers(analyst_token))

    assert response.status_code == 403


def test_admin_can_access_audit_log(client, admin_token):
    response = client.get("/audit/", headers=auth_headers(admin_token))

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_list_users(client, admin_token):
    response = client.get("/users/", headers=auth_headers(admin_token))

    assert response.status_code == 200


def test_admin_can_change_user_role(client, admin_token, analyst_token):
    users = client.get("/users/", headers=auth_headers(admin_token)).json()
    analyst = next(u for u in users if u["email"] == "analyst@example.com")

    response = client.patch(
        f"/users/{analyst['id']}/role",
        json={"role": "viewer"},
        headers=auth_headers(admin_token)
    )

    assert response.status_code == 200
    assert response.json()["role"] == "viewer"


def test_invalid_role_rejected(client, admin_token, analyst_token):
    users = client.get("/users/", headers=auth_headers(admin_token)).json()
    analyst = next(u for u in users if u["email"] == "analyst@example.com")

    response = client.patch(
        f"/users/{analyst['id']}/role",
        json={"role": "superuser"},
        headers=auth_headers(admin_token)
    )

    assert response.status_code == 400


def test_role_change_on_unknown_user_404(client, admin_token):
    response = client.patch(
        "/users/does-not-exist/role",
        json={"role": "viewer"},
        headers=auth_headers(admin_token)
    )

    assert response.status_code == 404


def test_viewer_cannot_create_incident(client, viewer_token):
    response = client.post(
        "/incidents/",
        json={"title": "Should not be created", "severity": "low"},
        headers=auth_headers(viewer_token)
    )

    assert response.status_code == 403


def test_viewer_can_read_incidents(client, viewer_token):
    response = client.get("/incidents/", headers=auth_headers(viewer_token))

    assert response.status_code == 200
