"""
schemas/attempts.py

Pydantic models for validating attempt logging requests
and responses in the practice/analytics system.
"""

from pydantic import BaseModel
from typing import Optional


class AttemptIn(BaseModel):
    subject: str
    topic: Optional[str] = None
    question_type: str
    question_text: str
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: bool
    hint_used: bool = False
    difficulty_level: str = "normal"


class AttemptOut(BaseModel):
    id: int
    subject: str
    topic: Optional[str]
    question_type: str
    question_text: str
    user_answer: Optional[str]
    correct_answer: Optional[str]
    is_correct: bool
    hint_used: bool
    difficulty_level: str
    attempt_date: str
