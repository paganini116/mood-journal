from werkzeug.security import generate_password_hash

from tests.conftest import create_user


def login_as_admin(client, db):
    db.execute(
        """
        INSERT INTO users (email, password_hash, role)
        VALUES (?, ?, 'admin')
        """,
        ("admin@example.com", generate_password_hash("password123")),
    )
    db.commit()

    client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_non_admin_cannot_access_admin_dashboard(client):
    create_user(client)
    client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )

    response = client.get("/admin/", follow_redirects=True)

    assert response.status_code == 200
    assert b"You do not have permission to access that page." in response.data


def test_admin_can_view_metadata_dashboard_without_raw_text(client, db):
    create_user(client, email="member@example.com")
    db.execute(
        """
        INSERT INTO journal_entries (
            user_id,
            raw_text,
            tone,
            current_state,
            summary,
            feel_better_recommendation,
            safety_note,
            analysis_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            "This should stay private.",
            "Reflective",
            "Processing a difficult day.",
            "Sensitive summary that must not appear in admin.",
            "Sensitive recommendation that must not appear in admin.",
            "",
            "complete",
        ),
    )
    db.commit()

    login_as_admin(client, db)
    response = client.get("/admin/")

    assert response.status_code == 200
    assert b"Operational visibility without exposing private journal content." in response.data
    assert b"This should stay private." not in response.data
    assert b"Sensitive summary that must not appear in admin." not in response.data
    assert b"Sensitive recommendation that must not appear in admin." not in response.data


def test_admin_dashboard_logs_audit_event(client, db):
    login_as_admin(client, db)

    response = client.get("/admin/")

    assert response.status_code == 200

    audit_row = db.execute(
        """
        SELECT action, target_type
        FROM admin_audit_log
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    assert audit_row["action"] == "view_dashboard"
    assert audit_row["target_type"] == "dashboard"


def test_admin_sees_flagged_metadata_only(client, db):
    create_user(client, email="flagged@example.com")
    db.execute(
        """
        INSERT INTO journal_entries (
            user_id,
            raw_text,
            tone,
            current_state,
            summary,
            feel_better_recommendation,
            safety_note,
            analysis_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            "Highly sensitive private text.",
            "Overwhelmed",
            "Acute distress.",
            "Do not show this summary.",
            "Do not show this recommendation.",
            "Needs support.",
            "needs_attention",
        ),
    )
    db.commit()

    login_as_admin(client, db)
    response = client.get("/admin/")

    assert response.status_code == 200
    assert b"flagged@example.com" in response.data
    assert b"needs attention" in response.data
    assert b"Highly sensitive private text." not in response.data
