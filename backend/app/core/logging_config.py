import logging
import os

# -------------------------------
# Logging Setup
# -------------------------------

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "homework_helper.log")

logger = logging.getLogger("homework_helper")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)


# -------------------------------
# Public Logging Helper
# -------------------------------

def log_prompt_and_response(tag: str, text: str):
    """
    Unified logger for all LLM prompt/response debugging.

    Usage:
        log_prompt_and_response("grammar_question", prompt_text)
    """
    logger.info(f"[{tag}] {text}")