from werkzeug.security import check_password_hash

from tests.conftest import create_user


def test_signup_creates_user_and_hashes_password(client, db):
    response = create_user(client)

    assert response.status_code == 200

    user = db.execute(
        "SELECT * FROM users WHERE email = ?",
        ("test@example.com",),
    ).fetchone()

    assert user is not None
    assert user["password_hash"] != "password123"
    assert check_password_hash(user["password_hash"], "password123")
    assert user["role"] == "user"


def test_login_logout_flow(client):
    create_user(client)

    login_response = client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=False,
    )

    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/journal/")

    logout_response = client.post(
        "/auth/logout",
        follow_redirects=False,
    )

    assert logout_response.status_code == 302
    assert logout_response.headers["Location"].endswith("/auth/login")


def test_protected_route_redirects_when_logged_out(client):
    response = client.get("/journal/", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")
