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

2. Create your local environment file:

```bash
cp .env.example .env
```

Then edit `.env` and set at least:

```bash
FLASK_APP=app.py
SECRET_KEY=change-me
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-5.4
```

3. Start the app:

```bash
flask --debug run
```

## Tests

```bash
pytest tests/
```
