from fastapi import APIRouter
from backend.app.schemas.llm import QuestionRequest
from backend.app.services.llm_service import generate_sentences_from_topics

router = APIRouter(prefix="/llm", tags=["llm"])

@router.post("/questions")
def generate_questions(payload: QuestionRequest):
    return generate_sentences_from_topics(payload)