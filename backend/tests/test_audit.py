from tests.conftest import auth_headers
from tests.conftest import login
from tests.conftest import register


def get_audit_log(client, admin_token):
    return client.get("/audit/", headers=auth_headers(admin_token)).json()


def test_registration_creates_audit_entry(client, admin_token):
    entries = get_audit_log(client, admin_token)

    assert any(e["action"] == "USER_REGISTERED" for e in entries)


def test_login_creates_audit_entry(client, admin_token):
    register(client, "someone@example.com")
    login(client, "someone@example.com")

    entries = get_audit_log(client, admin_token)
    login_entries = [
        e for e in entries
        if e["action"] == "USER_LOGIN" and e["actor_email"] == "someone@example.com"
    ]

    assert len(login_entries) == 1


def test_incident_actions_create_audit_entries(client, admin_token):
    incident = client.post(
        "/incidents/",
        json={"title": "Audit test incident", "severity": "medium"},
        headers=auth_headers(admin_token)
    ).json()

    client.patch(
        f"/incidents/{incident['id']}/resolve",
        json={"resolution_notes": "done"},
        headers=auth_headers(admin_token)
    )

    entries = get_audit_log(client, admin_token)
    actions = {e["action"] for e in entries if e["resource_type"] == "incident"}

    assert "INCIDENT_CREATED" in actions
    assert "INCIDENT_RESOLVED" in actions


def test_role_change_creates_audit_entry(client, admin_token):
    register(client, "target@example.com")
    users = client.get("/users/", headers=auth_headers(admin_token)).json()
    target = next(u for u in users if u["email"] == "target@example.com")

    client.patch(
        f"/users/{target['id']}/role",
        json={"role": "viewer"},
        headers=auth_headers(admin_token)
    )

    entries = get_audit_log(client, admin_token)

    assert any(e["action"] == "USER_ROLE_CHANGED" for e in entries)


def test_audit_log_requires_admin(client, analyst_token):
    response = client.get("/audit/", headers=auth_headers(analyst_token))

    assert response.status_code == 403
