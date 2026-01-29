from pydantic import BaseModel
from typing import List
from typing import Union
from pydantic import field_validator, model_validator


class MultipleChoiceOption(BaseModel):
    text: str
    is_correct: bool
    role: str | None = None


class MultipleChoiceQuestion(BaseModel):
    prompt: str
    options: List[MultipleChoiceOption]
    explanation: str | None = None
    topic: str
    subject: str

    # Reading comprehension fields (optional)
    passage_text: str | None = None
    passage_title: str | None = None
    passage_source: str | None = None
    passage_grade_level: str | None = None

    @model_validator(mode="after")
    def validate_options(self):
        correct = [o for o in self.options if o.is_correct]
        if len(correct) != 1:
            raise ValueError("Exactly one option must be correct.")
        if len(self.options) < 3:
            raise ValueError("At least three options required.")
        return self

    model_config = {
        "str_strip_whitespace": True,
        "validate_default": True
    }

QuestionType = Union[MultipleChoiceQuestion]

class QuestionResponse(BaseModel):
    question: MultipleChoiceQuestion
    source_topic: str
    source_prompt: str | None = None
    llm_model: str

    model_config = {
        "str_strip_whitespace": True,
        "validate_default": True
    }

MULTIPLE_CHOICE_JSON_SCHEMA = {
    "name": "multiple_choice_question",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "The question text"},
            "options": {
                "type": "array",
                "description": "Array of exactly 4 answer choices",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The answer choice text"},
                        "is_correct": {"type": "boolean", "description": "True if this is the correct answer"}
                    },
                    "required": ["text", "is_correct"],
                    "additionalProperties": False
                },
                "minItems": 4,
                "maxItems": 4
            },
            "explanation": {"type": "string", "description": "Brief explanation of the correct answer"},
            "topic": {"type": "string", "description": "The topic name"},
            "subject": {"type": "string", "description": "The subject (e.g., grammar)"}
        },
        "required": ["prompt", "options", "topic", "subject"],
        "additionalProperties": False
    }
}

def question_from_llm_json(raw: dict) -> MultipleChoiceQuestion:
    """
    Safely converts raw LLM JSON into a validated MultipleChoiceQuestion.
    Performs cleanup, normalization, and type correction.
    """
    # normalize booleans
    for opt in raw.get("options", []):
        if isinstance(opt.get("is_correct"), str):
            opt["is_correct"] = opt["is_correct"].lower() in ("true", "yes", "1")

    # normalize topic/subject casing
    raw["topic"] = raw.get("topic", "").lower().strip()
    raw["subject"] = raw.get("subject", "").lower().strip()

    try:
        return MultipleChoiceQuestion(**raw)
    except Exception as e:
        raise ValueError(f"Invalid LLM response: {raw!r}") from e

def mcq_to_attempt_record(mcq: MultipleChoiceQuestion) -> dict:
    return {
        "topic": mcq.topic,
        "subject": mcq.subject,
        "question_text": mcq.prompt,
        "correct_answer": next(o.text for o in mcq.options if o.is_correct)
    }
