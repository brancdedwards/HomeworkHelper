from fastapi import FastAPI
from backend.app.routers import sync, llm, ocr, topics_router, grammar_router

app = FastAPI(
    title="Homework Helper API",
    description="Backend API for grammar topics, OCR importing, LLM question generation, and YAML → DB sync.",
    version="1.0.0"
)

app.include_router(topics_router.router)
app.include_router(grammar_router.router)
app.include_router(ocr.router)
app.include_router(llm.router)
app.include_router(sync.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Homework Helper Backend Running"}