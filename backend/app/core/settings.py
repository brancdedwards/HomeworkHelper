"""
Global application configuration.

Everything that should be adjustable (model names, DB location,
debug flags, YAML paths, API keys, etc.) comes from Settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Environment
    # ---------------------------------------------------------
    ENV: str = "development"
    DEBUG: bool = True

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent  # Add one more .parent
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = DATA_DIR / "db" / "homework_helper.db"

    # ---------------------------------------------------------
    # LLM Settings
    # ---------------------------------------------------------
    LLM_PROVIDER: str = "anthropic"  # Options: "openai" or "anthropic"

    # API Keys
    OPENAI_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""

    # Model configuration
    LLM_MODEL: str = "claude-3-5-haiku-20241022"  # or "gpt-4o-mini" for OpenAI
    MAX_OUTPUT_TOKENS: int = 800
    TEMPERATURE: float = 0.3

    # Disable/Enable features globally
    ENABLE_HINTS: bool = True
    ENABLE_OCR: bool = False
    ENABLE_ADMIN_TOOLS: bool = True

    # ---------------------------------------------------------
    # App Behavior
    # ---------------------------------------------------------
    MAX_SENTENCES_PER_REQUEST: int = 25
    MAX_QUESTIONS_PER_SESSION: int = 10  # Maximum questions per practice session
    MIN_QUESTIONS_PER_SESSION: int = 1   # Minimum questions per practice session
    RANDOM_TOPIC_FILL: bool = True  # ensure "fill to N" works for random mode
    NORMALIZE_ANSWERS: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()