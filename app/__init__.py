import os
from pathlib import Path

from flask import Flask, g, redirect, session, url_for

from .auth import auth_bp
from .db import close_db, get_db, init_db
from .journal import journal_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        DATABASE=os.environ.get(
            "DATABASE_URL",
            str(instance_path / "mood_journal.sqlite3"),
        ),
        OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY"),
        OPENAI_MODEL=os.environ.get("OPENAI_MODEL", "gpt-5.2"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config is not None:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(journal_bp)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = None

        if user_id is not None:
            g.user = get_db().execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

    @app.route("/")
    def home():
        if g.user:
            return redirect(url_for("journal.dashboard"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        init_db()

    return app
