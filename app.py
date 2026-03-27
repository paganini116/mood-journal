from app import create_app

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - keeps local boot resilient before install
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

# Expose the Flask application instance for the development server.
app = create_app()
