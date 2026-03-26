from app.openai_service import JournalAnalyzer


class ResponseObject:
    output_text = """
    {
      "tone": "Calm",
      "current_state": "The user seems reflective and steady.",
      "summary": "The user is processing a quiet day with gratitude.",
      "feel_better_recommendation": "Keep the evening simple and take a short stretch break.",
      "safety_note": ""
    }
    """


class GoodClient:
    class responses:
        @staticmethod
        def create(**_kwargs):
            return ResponseObject()


class BadClient:
    class responses:
        @staticmethod
        def create(**_kwargs):
            raise RuntimeError("boom")


def test_openai_service_parses_structured_response(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=GoodClient())
        result = analyzer.analyze("I feel pretty grounded today.")

    assert result["tone"] == "Calm"
    assert result["safety_note"] == ""


def test_openai_service_falls_back_safely(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=BadClient())
        result = analyzer.analyze("I feel pretty grounded today.")

    assert result["tone"] == "Reflective"
    assert result["safety_note"] == ""


def test_openai_service_uses_safety_fallback_for_concerning_language(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=BadClient())
        result = analyzer.analyze("I do not feel safe and I might hurt myself.")

    assert result["tone"] == "Concerned"
    assert "immediate danger" in result["safety_note"]
