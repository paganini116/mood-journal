from flask import Blueprint, g, render_template

from .auth import admin_required
from .db import get_db


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Record an admin action without storing any journal content.
def log_admin_action(action, target_type, target_id=None):
    db = get_db()
    db.execute(
        """
        INSERT INTO admin_audit_log (admin_user_id, action, target_type, target_id)
        VALUES (?, ?, ?, ?)
        """,
        (g.user["id"], action, target_type, target_id),
    )
    db.commit()


@admin_bp.route("/")
@admin_required
# Show a metadata-only admin dashboard for operational visibility.
def dashboard():
    db = get_db()

    totals = {
        "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "entries": db.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0],
        "flagged_entries": db.execute(
            """
            SELECT COUNT(*)
            FROM journal_entries
            WHERE analysis_status = 'needs_attention'
            """
        ).fetchone()[0],
    }

    entry_status_counts = db.execute(
        """
        SELECT analysis_status, COUNT(*) AS count
        FROM journal_entries
        GROUP BY analysis_status
        ORDER BY count DESC, analysis_status ASC
        """
    ).fetchall()

    user_activity = db.execute(
        """
        SELECT u.id,
               u.email,
               u.role,
               u.created_at,
               COUNT(j.id) AS entry_count,
               SUM(CASE WHEN j.analysis_status = 'needs_attention' THEN 1 ELSE 0 END)
                   AS flagged_count,
               MAX(j.created_at) AS last_entry_at
        FROM users u
        LEFT JOIN journal_entries j ON j.user_id = u.id
        GROUP BY u.id, u.email, u.role, u.created_at
        ORDER BY entry_count DESC, u.email ASC
        """
    ).fetchall()

    flagged_entries = db.execute(
        """
        SELECT j.id,
               j.user_id,
               u.email,
               j.analysis_status,
               j.created_at
        FROM journal_entries j
        JOIN users u ON u.id = j.user_id
        WHERE j.analysis_status = 'needs_attention'
        ORDER BY j.created_at DESC, j.id DESC
        LIMIT 10
        """
    ).fetchall()

    recent_admin_events = db.execute(
        """
        SELECT a.action, a.target_type, a.target_id, a.created_at, u.email
        FROM admin_audit_log a
        JOIN users u ON u.id = a.admin_user_id
        ORDER BY a.created_at DESC, a.id DESC
        LIMIT 10
        """
    ).fetchall()

    log_admin_action("view_dashboard", "dashboard")

    return render_template(
        "admin/dashboard.html",
        totals=totals,
        entry_status_counts=entry_status_counts,
        user_activity=user_activity,
        flagged_entries=flagged_entries,
        recent_admin_events=recent_admin_events,
    )
