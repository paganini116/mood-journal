from tests.conftest import create_user


class StubAnalyzer:
    def analyze(self, _entry_text):
        return {
            "tone": "Hopeful",
            "current_state": "A little tired but optimistic.",
            "summary": "The user had a demanding day but still found signs of progress.",
            "feel_better_recommendation": "Take a short walk and write down one win from today.",
            "safety_note": "",
        }


class SafetyAnalyzer:
    def analyze(self, _entry_text):
        return {
            "tone": "Overwhelmed",
            "current_state": "This reads like a moment of acute distress.",
            "summary": "The entry suggests an urgent need for support.",
            "feel_better_recommendation": "Reach out to a trusted person right now and avoid being alone.",
            "safety_note": "You deserve immediate support from a real person right now.",
        }


def login(client):
    create_user(client)
    client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_journal_entry_is_saved_for_authenticated_user(client, db, monkeypatch):
    login(client)
    monkeypatch.setattr("app.journal.JournalAnalyzer", lambda: StubAnalyzer())

    response = client.post(
        "/journal/new",
        data={"raw_text": "Today was stressful, but I handled it."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Hopeful" in response.data

    entry = db.execute(
        "SELECT * FROM journal_entries"
    ).fetchone()

    assert entry is not None
    assert entry["analysis_status"] == "complete"
    assert entry["summary"] == "The user had a demanding day but still found signs of progress."


def test_history_page_lists_saved_entries(client, monkeypatch):
    login(client)
    monkeypatch.setattr("app.journal.JournalAnalyzer", lambda: StubAnalyzer())

    client.post(
        "/journal/new",
        data={"raw_text": "I am feeling okay today."},
        follow_redirects=True,
    )

    response = client.get("/journal/")

    assert response.status_code == 200
    assert b"The user had a demanding day but still found signs of progress." in response.data


def test_safety_note_marks_entry_for_attention(client, db, monkeypatch):
    login(client)
    monkeypatch.setattr("app.journal.JournalAnalyzer", lambda: SafetyAnalyzer())

    response = client.post(
        "/journal/new",
        data={"raw_text": "I do not feel safe with myself right now."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Support note" in response.data

    entry = db.execute(
        "SELECT * FROM journal_entries"
    ).fetchone()

    assert entry["analysis_status"] == "needs_attention"
