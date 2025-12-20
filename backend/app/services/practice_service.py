"""
practice_service.py

Business logic layer for logging student practice attempts.
Coordinates validation, repository calls, and future analytics hooks.
"""

from backend.app.schemas.attempts import AttemptIn
from backend.app.repositories.attempts_repository import create_attempt
from backend.app.core.logging_config import log_prompt_and_response


def log_attempt(payload: AttemptIn):
    """
    Orchestrates logging a student's practice attempt.

    - Validates payload through Pydantic (AttemptIn)
    - Passes validated data to the repository layer
    - Logs the event for debugging/analytics
    """

    try:
        log_prompt_and_response("attempt_log_request", str(payload.model_dump()))

        # Insert into DB
        attempt_id = create_attempt(payload)

        if attempt_id is None:
            raise Exception("DB insertion failed")

        log_prompt_and_response("attempt_log_success", f"Logged attempt for topic={payload.topic}")

        return {"status": "success", "attempt_id": attempt_id}

    except Exception as e:
        log_prompt_and_response("attempt_log_error", str(e))
        raise