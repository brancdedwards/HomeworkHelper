from fastapi import FastAPI
from backend.app.routers import sync, topics_router, grammar_router
# from backend.app.routers import llm  # TODO: Fix llm router imports
# from backend.app.routers import ocr  # TODO: Implement OCR router

app = FastAPI(
    title="Homework Helper API",
    description="Backend API for grammar practice with Anthropic Claude",
    version="1.0.0"
)

app.include_router(topics_router.router)
app.include_router(grammar_router.router)
# app.include_router(ocr.router)  # TODO: Implement OCR router
# app.include_router(llm.router)  # TODO: Fix llm router imports
app.include_router(sync.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Homework Helper Backend Running"}