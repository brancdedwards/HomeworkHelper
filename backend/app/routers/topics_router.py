from fastapi import APIRouter
from backend.app.schemas.topic import TopicIn, TopicOut
from backend.app.services.topic_service import (
    get_all_topics,
    create_topic,
    update_topic,
    deactivate_topic
)

router = APIRouter(prefix="/topics", tags=["topics"])

@router.get("/", response_model=list[TopicOut])
def list_topics():
    return get_all_topics()

@router.post("/", response_model=TopicOut)
def add_topic(payload: TopicIn):
    return create_topic(payload)

@router.put("/{topic_id}", response_model=TopicOut)
def edit_topic(topic_id: int, payload: TopicIn):
    return update_topic(topic_id, payload)

@router.delete("/{topic_id}")
def disable_topic(topic_id: int):
    deactivate_topic(topic_id)
    return {"deleted": True}