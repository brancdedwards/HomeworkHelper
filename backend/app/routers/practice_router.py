from fastapi import APIRouter, HTTPException
from backend.app.schemas.attempts import AttemptIn, AttemptOut
from backend.app.repositories.attempts_repository import create_attempt, list_attempts_filtered, get_stats, get_attempt_by_id
from backend.app.core.logging_config import log_prompt_and_response

router = APIRouter(prefix="/practice", tags=["practice"])

# -------------------------------------------
# POST /practice/attempts  -> create attempt
# -------------------------------------------
@router.post("/attempts", response_model=AttemptOut)
def create_attempt_route(payload: AttemptIn):
    """Create a new practice attempt and return the logged row."""
    try:
        log_prompt_and_response("attempt_log_request", str(payload.model_dump()))
        new_attempt_id = create_attempt(payload)
        logged = get_attempt_by_id(new_attempt_id)
        return logged
    except Exception as e:
        log_prompt_and_response("attempt_log_error", str(e))
        raise HTTPException(status_code=500, detail="Failed to log attempt")


# -------------------------------------------
# GET /practice/attempts/{id}  -> fetch attempt
# -------------------------------------------
@router.get("/attempts/{attempt_id}", response_model=AttemptOut)
def get_attempt(attempt_id: int):
    attempt = get_attempt_by_id(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


# -------------------------------------------
# GET /practice/attempts -> list attempts
# Optional filters: subject, topic, correctness
# -------------------------------------------
@router.get("/attempts", response_model=list[AttemptOut])
def list_attempts(subject: str | None = None,
                  topic: str | None = None,
                  correct: bool | None = None):
    attempts = list_attempts_filtered(
        subject=subject,
        topic=topic,
        correct=correct
    )
    return attempts


# ---------------------------------------------------------
# OPTIONAL (we add now): GET /practice/stats
# simple aggregated stats for UI (correct %, total attempts)
# ---------------------------------------------------------
@router.get("/stats")
def get_stats_route():
    stats = get_stats()
    return stats