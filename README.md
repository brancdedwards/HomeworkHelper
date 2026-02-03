# 🧠 HomeworkHelper

An AI-powered educational platform helping elementary students practice **Reading Comprehension** and **Grammar** through adaptive, engaging multiple-choice questions.

**Powered by Claude 3.5 Sonnet** • **Built with FastAPI + React** • **Multi-Subject Architecture**

---

## 🚀 Features

### 📖 Reading Comprehension
- **AI-Generated Passages**: Age-appropriate passages on diverse topics
- **4 Question Types**:
  - Main Idea & Theme
  - Inference & Conclusions
  - Vocabulary in Context
  - Text Structure & Purpose
- **Passage-Based Practice**: Multiple questions per passage for deeper comprehension
- **Grade-Level Validation**: Flesch-Kincaid readability scoring

### 📝 Grammar Practice
- **8 Categories**: Grammar Mechanics, Literary Devices, Parts of Speech, Punctuation, Sentence Structure, Sentence Types, Vocabulary, Writing Quality
- **40+ Topics**: From "adjectives" to "active vs passive voice"
- **Difficulty Scaling**: Easy, Normal, and Hard modes with vocabulary/complexity adjustments
- **Style Variations**: Default, Challenge, Socratic, Friendly, Direct

### 🎯 Quality & Engagement
- **Multi-Layer Duplicate Prevention**:
  - In-session tracking (exact questions, example sentences, overused words)
  - Cross-session database tracking with 7-day cooldown
  - SHA256 question fingerprinting
- **Content Variety**: AI prompts designed to avoid clichéd examples
- **Dynamic Question Generation**: Never runs out of practice material
- **Accurate Validation**: AI-powered verification ensures exactly 1 correct answer

### 🏗️ Multi-Subject Architecture
- **Subject-Agnostic Design**: Easily add new subjects (math, science, history)
- **Category System**: Each subject has distinct categories and topics
- **Flexible Routing**: Generic practice endpoints work for any subject
- **Extensible Services**: Subject-specific logic isolated in dedicated services

---

## 🧩 Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite with migrations
- **AI/LLM**: Claude 3.5 Sonnet via Anthropic API
- **Services**: Subject-agnostic practice generation, question history tracking
- **Config**: Pydantic Settings with `.env`

### Frontend
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Axios for backend communication

### DevOps
- **Development**: Hot-reload for both frontend and backend
- **Version Control**: Git with descriptive commits
- **Documentation**: Comprehensive guides in `docs/` folder

---

## ⚙️ Requirements

- **Python**: 3.10+ (for FastAPI backend)
- **Node.js**: 18+ (for React frontend)
- **Anthropic API Key**: Get one at https://console.anthropic.com/
- **Virtual Environment**: Recommended for Python dependencies

---

## 🛠️ Setup

### 1. Clone the Repository
```bash
git clone https://github.com/brandonedwards/HomeworkHelper.git
cd HomeworkHelper/pedantic-moore
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
Create `.env` file in project root:
```env
# Anthropic API
CLAUDE_API_KEY=your_api_key_here

# LLM Settings
LLM_MODEL=claude-3-5-sonnet-20241022
MAX_OUTPUT_TOKENS=1000
TEMPERATURE=0.3

# Database
DB_PATH=homework_helper.db

# Feature Flags
ENABLE_HINTS=true
DEBUG=true
```

#### Run Database Migrations
```bash
python backend/db/run_migrations.py
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Configure API Endpoint (if needed)
Edit `frontend/src/services/api.js` if your backend runs on a different port:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

---

## ▶️ How to Run

### Start Backend (Terminal 1)
```bash
# Activate venv first
source .venv/bin/activate

# Start FastAPI server with hot-reload
uvicorn backend.main:app --reload --port 8000
```

**Backend running at**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**Frontend running at**: http://localhost:5173

---

## 📡 API Overview

### Subject Management
- `GET /subjects` → List all subjects (grammar, reading)
- `GET /subjects/{subject}/categories` → Get categories for a subject
- `POST /subjects/{subject}/session` → Generate practice session
- `POST /subjects/{subject}/generate` → Generate single question

### Legacy Endpoints (Grammar)
- `POST /grammar/generate` → Generate grammar question (deprecated, use `/subjects/grammar/generate`)
- `POST /grammar/session` → Generate practice session (deprecated)

### Health Check
- `GET /` → `{ "status": "ok" }`

**Interactive API Docs**: Visit http://localhost:8000/docs for full Swagger documentation

---

## 🧱 Project Structure

```
pedantic-moore/
├── backend/
│   ├── main.py                      # FastAPI entry point
│   ├── app/
│   │   ├── core/
│   │   │   ├── settings.py          # Environment config
│   │   │   ├── logging_config.py    # Logging setup
│   │   │   └── subject_config.py    # Subject registry
│   │   ├── routers/
│   │   │   ├── subjects_router.py   # Generic practice endpoints
│   │   │   └── grammar_router.py    # Legacy grammar endpoints
│   │   ├── services/
│   │   │   ├── grammar_services.py  # Grammar question generation
│   │   │   ├── reading_service.py   # Reading comprehension + passages
│   │   │   ├── llm_service.py       # Claude API client
│   │   │   ├── topic_service.py     # Topic management
│   │   │   └── question_history_service.py  # Deduplication tracking
│   │   └── schemas/
│   │       └── questions.py         # Pydantic models
│   └── db/
│       ├── session.py               # Database connection
│       ├── migrations/              # SQL migration files
│       │   └── 001_create_question_history.sql
│       └── homework_helper.db       # SQLite database
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Main React component
│   │   ├── components/
│   │   │   ├── PracticeSetup.jsx    # Subject/category selection
│   │   │   ├── QuestionDisplay.jsx  # Question + passage display
│   │   │   └── Results.jsx          # Session results
│   │   └── services/
│   │       └── api.js               # Axios API client
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── imports/                     # CSV import templates
├── tools/
│   ├── import_topics.py             # Topic metadata generation
│   ├── review_topics.py             # Review generated topics
│   └── import_to_db.py              # Import to database
├── docs/                            # Documentation
│   ├── TOPIC_IMPORT_GUIDE.md        # Quick topic import guide
│   ├── READING_COMPREHENSION.md     # Reading feature docs
│   └── API_DOCUMENTATION.md         # API reference
├── archive/                         # Legacy code (not in use)
│   ├── legacy-streamlit/            # Old Streamlit UI
│   └── legacy-utils/                # Deprecated utilities
├── .env                             # Environment variables (create this)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 📚 Documentation

Comprehensive guides available in the `docs/` folder:

- **[Topic Import Guide](docs/TOPIC_IMPORT_GUIDE.md)** - How to add new grammar topics from weekly newsletters
- **[Reading Comprehension](docs/READING_COMPREHENSION.md)** - Reading feature overview and architecture
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Full API reference with examples

---

## 🔧 Tools & Scripts

### Topic Import Pipeline
Import new grammar topics from CSV files:

```bash
# 1. Generate metadata from CSV
python tools/import_topics.py data/imports/starter_topics.csv

# 2. Review generated topics
python tools/review_topics.py

# 3. Import to database
python tools/import_to_db.py
```

**See**: [Topic Import Guide](docs/TOPIC_IMPORT_GUIDE.md) for detailed instructions

### Database Migrations
```bash
# Run all pending migrations
python backend/db/run_migrations.py
```

---

## 🎯 How It Works

### Question Generation Flow

1. **User selects subject and category** (e.g., Reading → Main Idea & Theme)
2. **Backend fetches active topics** from database for that category
3. **For Grammar**:
   - Generates question using topic metadata and prompt templates
   - AI validation ensures exactly 1 correct answer
4. **For Reading**:
   - Generates age-appropriate passage on topic
   - Validates reading level (Flesch-Kincaid)
   - Generates multiple questions about passage
5. **Duplicate prevention checks**:
   - In-session: Exact text, example sentences, overused words
   - Cross-session: SHA256 hash with 7-day cooldown
6. **Records question in history database** for analytics and deduplication

### Multi-Layer Deduplication

**In-Session Tracking** (memory):
- `seen_questions`: Exact question text matches
- `seen_example_sentences`: First 50 chars of quoted sentences (prevents "Marco raced through..." duplicates)
- `seen_overused_words`: Tracks clichéd examples (elephant, Sarah, dog, cat, pizza)

**Cross-Session Tracking** (database):
- SHA256 hash of normalized question text
- 7-day cooldown period before question can reappear
- Persistent tracking in `question_history` table
- Analytics-ready (times shown, last shown date)

---

## 🔐 Security & Best Practices

- **API Keys**: Keep `.env` out of version control (already in `.gitignore`)
- **Database**: SQLite database contains learning history; handle appropriately
- **CORS**: Backend configured for local development (update for production)
- **Environment**: Use separate `.env` files for dev/staging/production

---

## 🧭 Roadmap

### Completed ✅
- [x] Multi-subject architecture (Grammar + Reading)
- [x] Question history database with deduplication
- [x] Reading comprehension with 4 question types
- [x] AI-generated passages with readability validation
- [x] Difficulty scaling (Easy/Normal/Hard)
- [x] React frontend with Tailwind CSS
- [x] Multi-layer duplicate prevention
- [x] Topic import pipeline with AI metadata generation

### In Progress 🚧
- [ ] Session analytics dashboard
- [ ] Student progress tracking
- [ ] Retry stubborn questions feature

### Future Enhancements 🔮
- [ ] Additional subjects (Math, Science, History)
- [ ] Multiple questions per passage (reuse passages efficiently)
- [ ] Timed reading challenges
- [ ] Export sessions as PDF
- [ ] Parent/teacher dashboard
- [ ] Offline mode for privacy
- [ ] Adaptive difficulty (auto-adjust based on performance)

---

## 💡 Philosophy

HomeworkHelper was created to solve a real problem: **keeping AI-generated educational content fresh, engaging, and non-repetitive**.

Early versions using OpenAI struggled with repetition (the infamous "elephant questions"), requiring extensive guardrails. The current architecture with Claude 3.5 Sonnet, multi-layer deduplication, and variety-focused prompts delivers consistently high-quality, diverse practice material.

**Design Principles**:
- **Quality over quantity**: AI validation ensures accuracy
- **Variety is key**: Multiple deduplication layers prevent boredom
- **Subject-agnostic**: Easy to add new subjects and question types
- **Student-focused**: Age-appropriate content, clear explanations, engaging scenarios

---

## 🤝 Contributing

This is a personal project for educational use, but suggestions and improvements are welcome!

**To suggest improvements**:
1. Open an issue describing the enhancement
2. For code changes, include context and rationale
3. Test thoroughly before submitting

---

## 📜 License

MIT License — open for educational use and modification.

---

## 🙏 Acknowledgments

- **Claude 3.5 Sonnet** by Anthropic - Powers all question generation
- **FastAPI** - Modern, fast Python web framework
- **React + Vite** - Lightning-fast frontend development
- **Tailwind CSS** - Utility-first styling

Built with ❤️ to make learning interactive and supportive for kids who thrive on guided feedback and adaptive practice.
