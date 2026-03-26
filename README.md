# Mood Journal

A Flask + SQLite mood journal MVP with email/password authentication, AI-generated wellness reflections, and a polished server-rendered UI.

## Features

- Account signup, login, and logout
- Private journal entries stored in SQLite
- Structured AI reflection with tone, current state, summary, and a gentle recommendation
- Safety-oriented fallback messaging for concerning entries
- Apple-inspired visual design with responsive templates

## Run locally

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
export FLASK_APP=app.py
export SECRET_KEY="change-me"
export OPENAI_API_KEY="your-api-key"
```

Optional:

```bash
export OPENAI_MODEL="gpt-5.2"
```

3. Start the app:

```bash
flask --debug run
```

## Tests

```bash
pytest tests/
```
