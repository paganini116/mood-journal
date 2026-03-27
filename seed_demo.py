from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_db


DEMO_USERS = [
    {
        "email": "demo@moodjournal.local",
        "password": "password123",
        "role": "user",
        "entries": [
            {
                "raw_text": (
                    "I woke up feeling behind before the day even started. Work"
                    " was packed, but I still finished the hardest task on my"
                    " list and that helped a little."
                ),
                "tone": "Tense but capable",
                "current_state": "Stretched thin and mentally busy, with a small sense of momentum.",
                "summary": (
                    "The day felt demanding, but there were signs of progress"
                    " that gave the user some stability."
                ),
                "feel_better_recommendation": (
                    "Step away from screens for ten minutes, drink water, and"
                    " write down the one thing that went better than expected."
                ),
                "safety_note": "",
                "analysis_status": "complete",
                "created_at": "2026-03-21 08:30:00",
            },
            {
                "raw_text": (
                    "I had lunch outside and it helped me slow down. I still"
                    " feel uncertain about a few things, but today wasn't as"
                    " heavy as the rest of the week."
                ),
                "tone": "Cautiously hopeful",
                "current_state": "A bit unsettled, though noticeably calmer than earlier in the week.",
                "summary": (
                    "A slower moment created room for relief and perspective,"
                    " even if uncertainty is still lingering."
                ),
                "feel_better_recommendation": (
                    "Keep the evening light, take a walk, and avoid overloading"
                    " yourself with extra decisions."
                ),
                "safety_note": "",
                "analysis_status": "complete",
                "created_at": "2026-03-22 12:45:00",
            },
            {
                "raw_text": (
                    "I snapped at someone I care about and I feel guilty about"
                    " it. I think I'm more exhausted than I realized."
                ),
                "tone": "Regretful",
                "current_state": "Emotionally drained and self-critical after a tense interaction.",
                "summary": (
                    "The user is carrying guilt and fatigue, and the conflict"
                    " seems connected to deeper exhaustion."
                ),
                "feel_better_recommendation": (
                    "Rest first, then send a short, honest check-in message"
                    " instead of replaying the conversation all night."
                ),
                "safety_note": "",
                "analysis_status": "complete",
                "created_at": "2026-03-23 20:15:00",
            },
            {
                "raw_text": (
                    "Everything feels loud in my head tonight and I don't feel"
                    " safe being alone with these thoughts."
                ),
                "tone": "Overwhelmed",
                "current_state": "This reads like a moment of acute emotional distress.",
                "summary": (
                    "The entry suggests the user may need immediate support and"
                    " should not carry this alone."
                ),
                "feel_better_recommendation": (
                    "Reach out to a trusted person right now and move toward"
                    " immediate real-world support."
                ),
                "safety_note": (
                    "You deserve immediate support from a real person right now."
                ),
                "analysis_status": "needs_attention",
                "created_at": "2026-03-24 23:10:00",
            },
            {
                "raw_text": (
                    "Today was simple in a good way. I cleaned up my place,"
                    " cooked dinner, and felt more like myself again."
                ),
                "tone": "Steady",
                "current_state": "Grounded and gently reconnected with a sense of routine.",
                "summary": (
                    "Ordinary routines helped the user feel calmer and more"
                    " settled in their own space."
                ),
                "feel_better_recommendation": (
                    "Protect the calm by keeping tomorrow morning slow and"
                    " starting with one familiar habit."
                ),
                "safety_note": "",
                "analysis_status": "complete",
                "created_at": "2026-03-25 18:05:00",
            },
        ],
    },
    {
        "email": "alex@moodjournal.local",
        "password": "password123",
        "role": "user",
        "entries": [
            {
                "raw_text": (
                    "I felt disconnected most of the day, but I finally talked"
                    " to a friend tonight and that helped."
                ),
                "tone": "Low but open",
                "current_state": "A little isolated, though connection is starting to soften that feeling.",
                "summary": (
                    "The day carried loneliness, but the user ended it with a"
                    " meaningful moment of support."
                ),
                "feel_better_recommendation": (
                    "Follow up with that friend tomorrow and do one small thing"
                    " that gets you out of your head."
                ),
                "safety_note": "",
                "analysis_status": "complete",
                "created_at": "2026-03-22 21:00:00",
            },
            {
                "raw_text": (
                    "I keep second-guessing myself at work. Nothing catastrophic"
                    " happened, but I can't seem to relax."
                ),
                "tone": "Anxious",
                "current_state": "Mentally activated and stuck in a loop of self-doubt.",
                "summary": (
                    "Even without a specific crisis, the user seems worn down by"
                    " persistent worry and overthinking."
                ),
                "feel_better_recommendation": (
                    "Close the workday with a short shutdown ritual and remind"
                    " yourself what is done for now."
                ),
                "safety_note": "",
                "analysis_status": "complete",
                "created_at": "2026-03-25 17:20:00",
            },
        ],
    },
    {
        "email": "admin@moodjournal.local",
        "password": "password123",
        "role": "admin",
        "entries": [],
    },
]


# Populate the local database with demo users and sample journal history.
def seed():
    app = create_app()

    with app.app_context():
        db = get_db()

        for user in DEMO_USERS:
            existing = db.execute(
                "SELECT id FROM users WHERE email = ?",
                (user["email"],),
            ).fetchone()

            if existing is None:
                cursor = db.execute(
                    """
                    INSERT INTO users (email, password_hash, role)
                    VALUES (?, ?, ?)
                    """,
                    (
                        user["email"],
                        generate_password_hash(user["password"]),
                        user["role"],
                    ),
                )
                user_id = cursor.lastrowid
            else:
                user_id = existing["id"]
                db.execute(
                    "UPDATE users SET role = ? WHERE id = ?",
                    (user["role"], user_id),
                )
                db.execute(
                    "DELETE FROM journal_entries WHERE user_id = ?",
                    (user_id,),
                )

            for entry in user["entries"]:
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
                        analysis_status,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        entry["raw_text"],
                        entry["tone"],
                        entry["current_state"],
                        entry["summary"],
                        entry["feel_better_recommendation"],
                        entry["safety_note"],
                        entry["analysis_status"],
                        entry["created_at"],
                        entry["created_at"],
                    ),
                )

        db.commit()

        total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_entries = db.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0]

        print("Seed complete.")
        print(f"Users: {total_users}")
        print(f"Journal entries: {total_entries}")
        print("Demo login: demo@moodjournal.local / password123")
        print("Admin login: admin@moodjournal.local / password123")


if __name__ == "__main__":
    seed()
