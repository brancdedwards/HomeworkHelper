"""
Generic Practice Router for Multi-Subject Support

Subject-agnostic practice endpoints that work for grammar, reading, and future subjects.
Routes requests to subject-specific services based on the subject parameter.
"""

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.app.core.subject_config import (
    get_all_subjects,
    get_subject_config,
    is_valid_subject,
    is_valid_category,
    get_category_display_name
)
from backend.app.core.logging_config import log_prompt_and_response

router = APIRouter(prefix="/subjects", tags=["Subjects"])


class PracticeSessionRequest(BaseModel):
    num_questions: int = Field(ge=1, le=10, description="Number of questions (1-10)")
    category: Optional[str] = Field(None, description="Specific category to focus on, or None for random")
    difficulty: str = Field("normal", description="Question difficulty level")
    style: str = Field("default", description="Question style")


@router.get("")
def list_subjects():
    """
    Get list of all available subjects.
    Returns subject metadata including categories, icons, and descriptions.
    """
    try:
        subjects = get_all_subjects()
        return {
            "subjects": [
                {
                    "key": subject.key,
                    "display_name": subject.display_name,
                    "icon": subject.icon,
                    "description": subject.description,
                    "category_count": len(subject.categories)
                }
                for subject in subjects
            ],
            "count": len(subjects)
        }
    except Exception as e:
        log_prompt_and_response("list_subjects_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{subject}/categories")
def get_subject_categories(
    subject: str = Path(..., description="Subject key (grammar, reading, etc.)")
):
    """
    Get list of available categories for a specific subject.
    Returns categories with display names.
    """
    try:
        # Validate subject
        if not is_valid_subject(subject):
            raise HTTPException(
                status_code=404,
                detail=f"Subject '{subject}' not found. Available subjects: {', '.join([s.key for s in get_all_subjects()])}"
            )

        config = get_subject_config(subject)

        # Get categories from database for this subject to ensure they have topics
        from backend.db.session import get_db

        with get_db() as db:
            rows = db.execute("""
                SELECT DISTINCT category
                FROM topics
                WHERE active = 1
                  AND subject = ?
                  AND category IS NOT NULL
                ORDER BY category
            """, (subject,)).fetchall()

            # Map database categories to display names
            db_categories = [row['category'] for row in rows]

            # Only return categories that exist in both config and database
            available_categories = [
                cat for cat in config.categories
                if cat in db_categories
            ]

            # Format for display
            categories = [
                {
                    "key": cat,
                    "display_name": get_category_display_name(cat)
                }
                for cat in sorted(available_categories)
            ]

            return {
                "subject": subject,
                "categories": categories,
                "count": len(categories)
            }

    except HTTPException:
        raise
    except Exception as e:
        log_prompt_and_response("get_subject_categories_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subject}/session")
def create_practice_session(
    subject: str = Path(..., description="Subject key (grammar, reading, etc.)"),
    payload: PracticeSessionRequest = None
):
    """
    Generate a practice session with N questions for a specific subject.
    Questions can be from a specific category or random mix.
    Returns a list of questions ready for practice.
    """
    try:
        # Validate subject
        if not is_valid_subject(subject):
            raise HTTPException(
                status_code=404,
                detail=f"Subject '{subject}' not found"
            )

        # Validate category if provided
        if payload.category and not is_valid_category(subject, payload.category):
            config = get_subject_config(subject)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category '{payload.category}' for subject '{subject}'. Valid categories: {', '.join(config.categories)}"
            )

        # Route to subject-specific service
        if subject == 'grammar':
            from backend.app.services.grammar_services import generate_practice_session
            questions = generate_practice_session(
                num_questions=payload.num_questions,
                category=payload.category,
                difficulty=payload.difficulty,
                style=payload.style
            )
        elif subject == 'reading':
            from backend.app.services.reading_service import generate_reading_session
            questions = generate_reading_session(
                num_questions=payload.num_questions,
                category=payload.category,
                difficulty=payload.difficulty,
                style=payload.style
            )
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Service not implemented for subject '{subject}'"
            )

        return {
            "subject": subject,
            "num_questions": len(questions),
            "category": payload.category or "random",
            "questions": questions
        }

    except HTTPException:
        raise
    except Exception as e:
        log_prompt_and_response("create_practice_session_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


class GenerateQuestionRequest(BaseModel):
    topic: str = Field(..., description="Specific topic name")
    difficulty: str = Field("normal", description="Question difficulty")
    style: str = Field("default", description="Question style")


@router.post("/{subject}/generate")
def generate_single_question(
    subject: str = Path(..., description="Subject key (grammar, reading, etc.)"),
    payload: GenerateQuestionRequest = None
):
    """
    Generate a single question for a specific topic and subject.
    Useful for testing or custom question generation.
    """
    try:
        # Validate subject
        if not is_valid_subject(subject):
            raise HTTPException(status_code=404, detail=f"Subject '{subject}' not found")

        # Route to subject-specific service
        if subject == 'grammar':
            from backend.app.services.grammar_services import generate_grammar_question
            result = generate_grammar_question(
                topic=payload.topic,
                subject=subject,
                difficulty=payload.difficulty,
                style=payload.style
            )

            # Extract correct answer from options
            correct_answer = next((opt.text for opt in result.question.options if opt.is_correct), None)

            return {
                "topic": result.source_topic,
                "subject": subject,
                "question": result.question.prompt,
                "options": [opt.text for opt in result.question.options],
                "correct_answer": correct_answer,
                "explanation": result.question.explanation
            }

        elif subject == 'reading':
            from backend.app.services.reading_service import generate_reading_question
            result = generate_reading_question(
                topic=payload.topic,
                difficulty=payload.difficulty,
                style=payload.style
            )
            return result

        else:
            raise HTTPException(
                status_code=501,
                detail=f"Service not implemented for subject '{subject}'"
            )

    except HTTPException:
        raise
    except Exception as e:
        log_prompt_and_response("generate_single_question_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ['router']
