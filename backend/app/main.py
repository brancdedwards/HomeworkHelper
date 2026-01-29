from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import sync, topics_router, grammar_router
# from backend.app.routers import llm  # TODO: Fix llm router imports
# from backend.app.routers import ocr  # TODO: Implement OCR router

app = FastAPI(
    title="Homework Helper API",
    description="Backend API for grammar practice with Anthropic Claude",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics_router.router)
app.include_router(grammar_router.router)
# app.include_router(ocr.router)  # TODO: Implement OCR router
# app.include_router(llm.router)  # TODO: Fix llm router imports
app.include_router(sync.router)

@app.get("/debug/settings")
def debug_settings():
    from backend.app.core.settings import settings
    return {
        "claude_api_key_set": bool(settings.CLAUDE_API_KEY),
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "db_path": str(settings.DB_PATH),
        "max_questions": settings.MAX_QUESTIONS_PER_SESSION
    }

@app.get("/")
def root():
    return {"status": "ok", "message": "Homework Helper Backend Running"}
