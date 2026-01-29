from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import sync, topics_router, grammar_router, subjects_router
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
app.include_router(subjects_router.router)  # Generic multi-subject endpoints
# app.include_router(ocr.router)  # TODO: Implement OCR router
# app.include_router(llm.router)  # TODO: Fix llm router imports
app.include_router(sync.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Homework Helper Backend Running"}
