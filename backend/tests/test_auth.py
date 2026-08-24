from tests.conftest import auth_headers
from tests.conftest import login
from tests.conftest import register


def test_register_creates_user(client):
    response = register(client, "user1@example.com")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "user1@example.com"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_rejected(client):
    register(client, "dupe@example.com")
    response = register(client, "dupe@example.com")

    assert response.status_code == 400


def test_first_user_becomes_admin(client):
    response = register(client, "first@example.com")

    assert response.json()["role"] == "admin"


def test_second_user_defaults_to_analyst(client):
    register(client, "first@example.com")
    response = register(client, "second@example.com")

    assert response.json()["role"] == "analyst"


def test_login_success_returns_token(client):
    register(client, "user2@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "user2@example.com", "password": "TestPass123!"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    register(client, "user3@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "user3@example.com", "password": "WrongPassword!"}
    )

    assert response.status_code == 401


def test_login_unknown_email_rejected(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"}
    )

    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/users/me")

    assert response.status_code in (401, 403)


def test_protected_route_rejects_invalid_token(client):
    response = client.get(
        "/users/me",
        headers=auth_headers("not-a-real-token")
    )

    assert response.status_code == 401


def test_protected_route_accepts_valid_token(client):
    register(client, "user4@example.com")
    token = login(client, "user4@example.com")

    response = client.get("/users/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["user"]["sub"] == "user4@example.com"
