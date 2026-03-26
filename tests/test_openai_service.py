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


class InvalidShapeResponseObject:
    output_text = """
    {
      "tone": "Calm",
      "summary": "Missing required fields on purpose."
    }
    """


class InvalidShapeClient:
    class responses:
        @staticmethod
        def create(**_kwargs):
            return InvalidShapeResponseObject()


class NonJsonResponseObject:
    output_text = "not-json-at-all"


class NonJsonClient:
    class responses:
        @staticmethod
        def create(**_kwargs):
            return NonJsonResponseObject()


def test_openai_service_parses_structured_response(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=GoodClient())
        result = analyzer.analyze("I feel pretty grounded today.")

    assert result["tone"] == "Calm"
    assert result["safety_note"] == ""
    assert result["analysis_source"] == "openai"
    assert result["analysis_model"] == "gpt-5.4"
    assert result["analysis_reason"] == "openai_response_valid"


def test_openai_service_falls_back_safely(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=BadClient())
        result = analyzer.analyze("I feel pretty grounded today.")

    assert result["tone"] == "Reflective"
    assert result["safety_note"] == ""
    assert result["analysis_source"] == "fallback_error"
    assert result["analysis_reason"] == "openai_request_failed"


def test_openai_service_uses_safety_fallback_for_concerning_language(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=BadClient())
        result = analyzer.analyze("I do not feel safe and I might hurt myself.")

    assert result["tone"] == "Concerned"
    assert "immediate danger" in result["safety_note"]
    assert result["analysis_source"] == "fallback_error"
    assert result["analysis_reason"] == "openai_request_failed"


def test_openai_service_marks_invalid_shape_as_fallback(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=InvalidShapeClient())
        result = analyzer.analyze("I had a strange day.")

    assert result["tone"] == "Reflective"
    assert result["analysis_source"] == "fallback_invalid_shape"
    assert result["analysis_reason"] == "openai_response_missing_required_fields"


def test_openai_service_marks_non_json_as_parse_error(app):
    with app.app_context():
        analyzer = JournalAnalyzer(client=NonJsonClient())
        result = analyzer.analyze("I had a strange day.")

    assert result["tone"] == "Reflective"
    assert result["analysis_source"] == "fallback_parse_error"
    assert result["analysis_reason"] == "openai_response_not_valid_json"
