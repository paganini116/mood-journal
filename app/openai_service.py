import json

from flask import current_app


class JournalAnalyzer:
    def __init__(self, client=None):
        self._client = client

    def analyze(self, entry_text):
        entry_text = (entry_text or "").strip()
        if not entry_text:
            raise ValueError("Entry text is required for analysis.")

        flagged_for_safety = self._detect_crisis_language(entry_text)
        prompt = self._build_prompt(entry_text)

        try:
            raw_response = self.client.responses.create(
                model=current_app.config["OPENAI_MODEL"],
                input=prompt,
            )
            payload = json.loads(raw_response.output_text)
            return self._normalize_result(payload)
        except Exception:
            if flagged_for_safety:
                return self._safety_fallback_result()
            return self._fallback_result()

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "The openai package is required to analyze journal entries."
                ) from exc

            api_key = current_app.config.get("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured.")

            self._client = OpenAI(api_key=api_key)

        return self._client

    def _build_prompt(self, entry_text):
        return f"""
You are a supportive wellness coach for a mood journal application.
Return JSON only with exactly these keys:
- tone
- current_state
- summary
- feel_better_recommendation
- safety_note

Rules:
- Do not claim to be a therapist.
- Keep recommendations gentle, low-risk, and practical.
- If the entry suggests risk of self-harm or immediate danger, set safety_note to a short supportive crisis-oriented message and keep feel_better_recommendation focused on seeking immediate human support.
- If there is no elevated risk, set safety_note to an empty string.
- Keep each field under 80 words.

Journal entry:
\"\"\"{entry_text}\"\"\"
""".strip()

    def _normalize_result(self, payload):
        normalized = {
            "tone": str(payload.get("tone", "")).strip(),
            "current_state": str(payload.get("current_state", "")).strip(),
            "summary": str(payload.get("summary", "")).strip(),
            "feel_better_recommendation": str(
                payload.get("feel_better_recommendation", "")
            ).strip(),
            "safety_note": str(payload.get("safety_note", "")).strip(),
        }

        if not all(
            normalized[key]
            for key in (
                "tone",
                "current_state",
                "summary",
                "feel_better_recommendation",
            )
        ):
            return self._fallback_result()

        return normalized

    def _fallback_result(self):
        return {
            "tone": "Reflective",
            "current_state": "You may be carrying a lot right now.",
            "summary": (
                "This entry captures a meaningful emotional moment and deserves"
                " a little care and patience."
            ),
            "feel_better_recommendation": (
                "Try one small grounding step next: drink some water, take five"
                " slow breaths, and message someone you trust if you want"
                " support."
            ),
            "safety_note": "",
        }

    def _safety_fallback_result(self):
        return {
            "tone": "Concerned",
            "current_state": "This entry may reflect a moment of acute distress.",
            "summary": (
                "Your words suggest you may need immediate support from a real"
                " person right now."
            ),
            "feel_better_recommendation": (
                "Please contact someone you trust right away and reach out to"
                " emergency or crisis support if you may be in danger."
            ),
            "safety_note": (
                "If you feel like you may be in immediate danger or might harm"
                " yourself, contact emergency services or a crisis hotline right"
                " away."
            ),
        }

    def _detect_crisis_language(self, entry_text):
        lowered = entry_text.lower()
        markers = (
            "kill myself",
            "end my life",
            "hurt myself",
            "harm myself",
            "suicide",
            "suicidal",
            "don't want to live",
            "do not feel safe",
            "immediate danger",
        )
        return any(marker in lowered for marker in markers)
