# 🧠 HomeworkHelper

An educational assistant to help kids practice reading comprehension and grammar. The project includes:
- A Streamlit UI for interactive practice and review
- A FastAPI backend for topic management, LLM-powered question generation, synchronization from YAML → DB, and optional OCR helpers

Powered by the OpenAI API. This README documents both the UI and API components, setup, and how to run them locally.

---

## 🚀 Features

- Reading Mode
  - Upload or paste a passage (e.g., from school assignments or PDFs)
  - Generate simplified versions for elementary readability
  - Generate comprehension questions and vocabulary explanations
  - Export session as a formatted PDF

- Grammar Practice
  - Generate practice sentences and multiple-choice questions
    - Topics include parts of speech, figurative language (e.g., simile vs. metaphor), etc.
  - Randomized, adaptive question generation using GPT

- Admin & Topics
  - Manage “What We’re Learning” concepts and vocabulary
  - Sync curated YAML topics into the local database via API

- History & Review
  - View past sessions with passages, questions, and answers
  - Export summaries or full lesson sessions to PDF

---

## 🧩 Tech Stack

- UI: Streamlit
- API: FastAPI
- Database: SQLite (local)
- AI/LLM: OpenAI (model configurable; default is `gpt-4o-mini` per settings)
- PDF/Docs: ReportLab, FPDF2, and PyMuPDF (`fitz`)
- OCR: Tesseract via `pytesseract` (optional)
- Config: Pydantic BaseSettings with `.env`

Note: Previous README stated a specific Python version. The repository does not pin Python in code or config.
- TODO: Confirm and document the minimum supported Python version (e.g., 3.10+).

---

## ⚙️ Requirements

- Python (3.x). A virtual environment is recommended.
- Pip packages: see `requirements.txt`.
- System dependencies (as needed by features):
  - Tesseract OCR (for OCR-related endpoints)
    - macOS: `brew install tesseract`
    - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
    - Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki
  - OpenAI API key
  - Optional: spaCy model(s) if later required by features
    - TODO: Identify and document the exact spaCy model to install (e.g., `en_core_web_sm`).

---

## 🛠️ Setup

1) Clone the repository
```
git clone https://github.com/brandonedwards/HomeworkHelper.git
cd HomeworkHelper
```

2) Create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

3) Install dependencies
```
pip install -r requirements.txt
```

4) Configure environment variables
- Create a `.env` file in the project root. The backend loads settings from `.env` via Pydantic BaseSettings.
- Minimal example:
```
OPENAI_API_KEY=your_api_key_here
```
- Extended example (with defaults from `backend/app/core/settings.py`). Only override what you need:
```
# Environment & behavior
ENV=development
DEBUG=true

# Paths (relative to project root by default)
# NOTE: There are references to both data/ and db/ paths in the repo.
# TODO: Unify DB path usage across UI and backend.
DATA_DIR=data
DB_PATH=db/homeworkhelper.db
GRAMMAR_YAML_PATH=data/grammar_topics.yaml

# LLM Settings
OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini
MAX_OUTPUT_TOKENS=800
TEMPERATURE=0.3

# Feature flags
ENABLE_HINTS=true
ENABLE_OCR=false
ENABLE_ADMIN_TOOLS=true

# App behavior
MAX_SENTENCES_PER_REQUEST=25
RANDOM_TOPIC_FILL=true
NORMALIZE_ANSWERS=true
```

---

## ▶️ How to Run

You can run the UI and API separately. In two terminals:

1) Start the FastAPI backend
```
# If uvicorn is not installed:
pip install "uvicorn[standard]"

# Start API (hot-reload)
uvicorn backend.main:app --reload --port 8000
```
Notes:
- The project depends on FastAPI but does not currently pin `uvicorn` in `requirements.txt`.
  - TODO: Add `uvicorn` to `requirements.txt` or document an alternative ASGI server for production.
- Interactive docs: http://localhost:8000/docs

2) Start the Streamlit UI
```
streamlit run app.py
```

Optional initialization helper:
```
python setup_project.py
```
This script creates missing folders/files and a starter database under `data/`.

---

## 📡 API Overview (summary)

FastAPI app lives at `backend/main.py`.

- Health/root
  - `GET /` → `{ "status": "ok" }`

- Topics (`backend/app/routers/topics_router.py`)
  - `GET /topics/` → list topics
  - `POST /topics/` → create topic
  - `PUT /topics/{id}` → update topic
  - `DELETE /topics/{id}` → deactivate topic

- Grammar (`backend/app/routers/grammar_router.py`)
  - `POST /grammar/generate` → generate grammar question
  - `POST /grammar/hint` → get hint for a wrong answer
  - `POST /grammar/hint/test` → debug endpoint with topic data

- LLM (`backend/app/routers/llm.py`)
  - `POST /llm/questions` → generate questions from topics

- Sync (`backend/app/routers/sync.py`)
  - `POST /sync/yaml-to-db` → import/sync topics from YAML into DB

- OCR (`backend/app/routers/ocr.py`) – file currently present but empty
  - TODO: Implement OCR endpoints and document expected inputs/outputs.

Explore the full schema and try endpoints at `/docs` once the server is running.

---

## 🧱 Project Structure (high-level)

```
HomeworkHelper/
├── app.py                     # Streamlit UI entry point
├── backend/
│   ├── main.py                # FastAPI entry point: `backend.main:app`
│   └── app/
│       ├── core/              # settings, logging, exceptions
│       ├── clients/           # LLM, OCR, DB clients
│       ├── repositories/      # data access (SQLite)
│       ├── routers/           # FastAPI routers (grammar, topics, llm, sync, ...)
│       ├── schemas/           # Pydantic models
│       ├── services/          # app logic (LLM, grammar, sync, topic, ...)
│       └── ui/                # (internal UI utilities)
├── config/                    # (reserved for future config)
├── data/                      # data files (e.g., YAML, or db from setup script)
├── db/                        # SQLite database files (active DB in current dev)
├── frontend/                  # (placeholder; not wired in this README)
├── models/                    # ORM or data models (if used)
├── modules/                   # Streamlit page modules (learning, history, grammar, admin)
├── utils/                     # Shared helpers (DB, LLM, loading)
├── requirements.txt
├── setup_project.py           # Optional bootstrap script
├── TODO.yaml                  # Project TODOs and roadmap items
└── README.md
```

Notes on database location:
- There are multiple references to database paths in the repo (`data/homework_helper.db`, `db/homework_helper.db`, and `db/homeworkhelper.db`).
- TODO: Choose one canonical path and update code accordingly (and document here).

---

## 🔧 Scripts

- `setup_project.py`
  - Creates common directories, a starter DB under `data/`, and placeholder files if missing.
  - Safe to re-run; it only adds missing components.

- `scratch_02.py`
  - Experimental helper for local data import into SQLite.
  - TODO: Replace with documented, reproducible migration or seed scripts.

---

## 🔐 Environment Variables

Environment is read from `.env` via Pydantic BaseSettings (`backend/app/core/settings.py`). Key variables:

- `OPENAI_API_KEY` – required to call OpenAI
- `LLM_MODEL` – default `gpt-4o-mini`
- `MAX_OUTPUT_TOKENS`, `TEMPERATURE` – model call tuning
- `ENABLE_HINTS`, `ENABLE_OCR`, `ENABLE_ADMIN_TOOLS` – feature flags
- `DATA_DIR`, `DB_PATH`, `GRAMMAR_YAML_PATH` – key paths

See the extended example in Setup for defaults and comments.

---

## ✅ Tests

- No automated tests are included yet.
- TODO: Add tests (e.g., pytest) for services and routers; include instructions to run them here.

---

## 🔒 Security Notes

- Keep your `.env` out of version control.
- Do not commit API keys or personal data.
- SQLite DBs may contain learning history; handle and share appropriately.

---

## 🧭 Roadmap

- [ ] Add multi-grade reading difficulty adjustment
- [ ] Admin dashboard for managing vocabulary and concepts
- [ ] Quiz scoring and student progress tracking
- [ ] Optional local/offline mode for privacy
- [ ] Unify database path and add migrations/seeds
- [ ] Add `uvicorn` (or another ASGI server) to project dependencies
- [ ] Implement OCR endpoints and document usage

---

## 💡 Inspiration

Created to make schoolwork more interactive and supportive —
especially for kids who learn best through guided feedback and adaptive practice.

---

## 📜 License

MIT License — open for educational use and modification.

Note: If a `LICENSE` file is not present at the project root, please add one.