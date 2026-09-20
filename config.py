
import os
from pathlib import Path

# --------------------------------------------------
# HireFlow project directory
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------
# Load .env safely
# --------------------------------------------------

try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "python-dotenv is not installed. "
        "Run: python -m pip install python-dotenv"
    )

ENV_FILE = BASE_DIR / ".env"

# Load THIS project's .env file.
# override=True prevents an old inherited environment
# variable from replacing the value in this project's .env.
load_dotenv(dotenv_path=ENV_FILE, override=True)

# --------------------------------------------------
# OpenAI configuration
# --------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna"
).strip()

# --------------------------------------------------
# Project limits
# --------------------------------------------------

MAX_TEXT_CHARS = 30000
MAX_RESUMES = 5
MAX_INTERVIEW_TURNS = 4


# --------------------------------------------------
# Safe configuration check
# --------------------------------------------------

def validate_config():
    """Check configuration without exposing the API key."""

    if not ENV_FILE.exists():
        raise RuntimeError(
            f".env file not found at: {ENV_FILE}"
        )

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from .env"
        )

    if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        raise RuntimeError(
            "OPENAI_API_KEY still contains the placeholder value."
        )

    return True

