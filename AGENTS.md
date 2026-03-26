# AGENTS.md

## Project
- This is a Python Flask app.
- Use SQLite for the database.
- Keep the architecture lightweight and MVP-friendly unless explicitly asked to scale it up.

## Run And Test
- Run the app with: `flask --debug run`
- Run tests with: `pytest tests/`
- Load local config from `.env`
- Keep `.env.example` updated when adding new required settings.

## Code And Structure
- Follow PEP 8 style.
- Prefer simple server-rendered Flask patterns unless there is a stronger reason to change.
- Keep OpenAI integration server-side; do not expose API keys in frontend code.
- Preserve owner-scoped journal access and metadata-only admin access unless requirements explicitly change.

## UI And UX
- Preserve the current visual direction and clean premium feel.
- Do not expose debugging or internal AI/provider metadata in visible product UI.
- Keep mobile behavior usable and intentional.

## Safety And Sensitive Data
- Treat journal content as sensitive.
- Do not broaden admin access to raw journal entries unless explicitly requested.
- Prefer observability through logs, response metadata, and devtools-friendly app endpoints rather than user-facing debug UI.

## Docs
- Keep developer setup in `README.md`.
- Put future product, help, and architecture docs in a `docs/` folder rather than overloading the README.
