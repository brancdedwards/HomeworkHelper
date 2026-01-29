from pydantic import BaseModel

class TopicIn(BaseModel):
    name: str
    category: str | None = None
    question_focus: str | None = None
    active: bool = True

class TopicOut(TopicIn):
    id: int