from pydantic import BaseModel

class QuestionRequest(BaseModel):
    topic: str
    category: str | None = None
    count: int = 3