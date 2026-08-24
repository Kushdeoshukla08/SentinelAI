from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.core.database import get_db
from app.main import app

from app import models  # noqa: F401 - populates Base.metadata for create_all/drop_all
from app.models import User


def _with_db_name(url: str, db_name: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, f"/{db_name}", parts.query, parts.fragment))


TEST_DB_NAME = urlsplit(settings.DATABASE_URL).path.lstrip("/") + "_test"
TEST_DATABASE_URL = _with_db_name(settings.DATABASE_URL, TEST_DB_NAME)


def _ensure_test_database_exists():
    admin_url = _with_db_name(settings.DATABASE_URL, "postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME}
        ).first()

        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))

    admin_engine.dispose()


_ensure_test_database_exists()

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _reset_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture()
def client():

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


DEFAULT_PASSWORD = "TestPass123!"


def register(client, email, password=DEFAULT_PASSWORD, name="Test User"):
    return client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password}
    )


def login(client, email, password=DEFAULT_PASSWORD):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_token(client):
    register(client, "admin@example.com")
    return login(client, "admin@example.com")


@pytest.fixture()
def analyst_token(client, admin_token):
    register(client, "analyst@example.com")
    return login(client, "analyst@example.com")


@pytest.fixture()
def viewer_token(client, db_session, admin_token):
    register(client, "viewer@example.com")

    user = db_session.query(User).filter(User.email == "viewer@example.com").first()
    user.role = "viewer"
    db_session.commit()

    return login(client, "viewer@example.com")
