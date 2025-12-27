from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.grammar_services import generate_grammar_question
from backend.app.core.logging_config import log_prompt_and_response
import traceback  # Add this

router = APIRouter(prefix="/grammar", tags=["Grammar"])


class GrammarRequest(BaseModel):
    topic: str
    subject: str = "grammar"
    difficulty: str = "normal"
    style: str = "default"


@router.post("/generate")
def generate_question(payload: GrammarRequest):
    try:
        result = generate_grammar_question(
            topic=payload.topic,
            subject=payload.subject,
            difficulty=payload.difficulty,
            style=payload.style
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate question")

        correct_answer = next(
            (opt.text for opt in result.question.options if opt.is_correct),
            None
        )

        return {
            "topic": payload.topic,
            "question": result.question.prompt,
            "options": [opt.text for opt in result.question.options],
            "answer": correct_answer,
            "explanation": result.question.explanation
        }

    except Exception as e:
        # Print full traceback to console
        print("=" * 80)
        print("ERROR IN GRAMMAR GENERATE:")
        print(traceback.format_exc())
        print("=" * 80)

        log_prompt_and_response("grammar_router_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))