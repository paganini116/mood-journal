from pathlib import Path

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test.sqlite3"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(database_path),
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def db(app):
    with app.app_context():
        from app.db import get_db

        yield get_db()


def create_user(client, email="test@example.com", password="password123"):
    return client.post(
        "/auth/signup",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
