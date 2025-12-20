from fastapi import APIRouter, UploadFile, File
from backend.app.services.ocr_service import extract_text_from_image

router = APIRouter(prefix="/ocr", tags=["ocr"])

@router.post("/")
async def ocr_upload(file: UploadFile = File(...)):
    text = await extract_text_from_image(file)
    return {"text": text}