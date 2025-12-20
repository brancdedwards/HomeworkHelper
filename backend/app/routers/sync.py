from fastapi import APIRouter
from backend.app.services.sync_service import sync_yaml_to_db

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/yaml-to-db")
def sync_yaml():
    count = sync_yaml_to_db()
    return {"synced": count}