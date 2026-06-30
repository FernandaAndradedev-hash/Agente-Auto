import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _require(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        print(f"\nERRO: Variável '{key}' não encontrada no .env\n", file=sys.stderr)
        sys.exit(1)
    return value


# APIs ──────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
SERPER_API_KEY: str = _require("SERPER_API_KEY")

# Modelos ───────────────────────────────────────────────────────────────────
LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-haiku-4-5")

# Segurança ─────────────────────────────────────────────────────────────────
MAX_TASK_LENGTH: int = int(os.getenv("MAX_TASK_LENGTH", "2000"))
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "5"))