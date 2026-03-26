from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .auth import login_required
from .db import get_db
from .openai_service import JournalAnalyzer


journal_bp = Blueprint("journal", __name__, url_prefix="/journal")


@journal_bp.route("/")
@login_required
def dashboard():
    entries = get_db().execute(
        """
        SELECT id, raw_text, tone, current_state, summary, safety_note,
               analysis_status, created_at
        FROM journal_entries
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (g.user["id"],),
    ).fetchall()
    return render_template("journal/dashboard.html", entries=entries)


@journal_bp.route("/new", methods=("GET", "POST"))
@login_required
def new_entry():
    if request.method == "POST":
        raw_text = request.form.get("raw_text", "").strip()

        if not raw_text:
            flash("Write a few thoughts before saving your entry.", "error")
            return render_template("journal/new_entry.html")

        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO journal_entries (user_id, raw_text, analysis_status)
            VALUES (?, ?, 'processing')
            """,
            (g.user["id"], raw_text),
        )
        entry_id = cursor.lastrowid
        db.commit()

        analysis = JournalAnalyzer().analyze(raw_text)
        status = "complete"
        if analysis.get("safety_note"):
            status = "needs_attention"

        db.execute(
            """
            UPDATE journal_entries
            SET tone = ?,
                current_state = ?,
                summary = ?,
                feel_better_recommendation = ?,
                safety_note = ?,
                analysis_status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
            """,
            (
                analysis["tone"],
                analysis["current_state"],
                analysis["summary"],
                analysis["feel_better_recommendation"],
                analysis["safety_note"],
                status,
                entry_id,
                g.user["id"],
            ),
        )
        db.commit()

        flash("Entry saved and reflected back to you.", "success")
        return redirect(url_for("journal.entry_detail", entry_id=entry_id))

    return render_template("journal/new_entry.html")


@journal_bp.route("/<int:entry_id>")
@login_required
def entry_detail(entry_id):
    entry = get_db().execute(
        """
        SELECT *
        FROM journal_entries
        WHERE id = ? AND user_id = ?
        """,
        (entry_id, g.user["id"]),
    ).fetchone()

    if entry is None:
        flash("That entry could not be found.", "error")
        return redirect(url_for("journal.dashboard"))

    return render_template("journal/detail.html", entry=entry)
