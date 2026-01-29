# Anthropic Migration & Grammar Practice MVP

## ✅ What We Built

This branch (`anthropic-migration`) successfully migrates the HomeworkHelper API from OpenAI to Anthropic Claude and implements the Grammar Practice MVP.

### 🚀 Working Features

1. **Anthropic Claude 3.5 Haiku Integration**
   - Cost-effective AI model for question generation
   - Fast response times
   - High-quality educational content

2. **Grammar Practice Session API**
   - Generate 1-10 questions per session
   - Category-specific or random question selection
   - 79 grammar topics across 11 categories

3. **Working Endpoints**
   - `GET /` - Health check
   - `GET /grammar/categories` - List available categories
   - `POST /grammar/practice/session` - Generate practice questions
   - `GET /docs` - Interactive API documentation

## 📋 How to Test

### 1. Start the Server

From the worktree directory:
```bash
./start_server.sh
```

Or manually:
```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m uvicorn backend.main:app --reload --port 8000
```

### 2. Test Endpoints

**Get Categories:**
```bash
curl http://localhost:8000/grammar/categories
```

**Generate Practice Session (Category-Specific):**
```bash
curl -X POST http://localhost:8000/grammar/practice/session \
  -H 'Content-Type: application/json' \
  -d '{"num_questions":3,"category":"parts_of_speech"}'
```

**Generate Practice Session (Random):**
```bash
curl -X POST http://localhost:8000/grammar/practice/session \
  -H 'Content-Type: application/json' \
  -d '{"num_questions":5,"category":null}'
```

### 3. View Interactive Docs
Open in browser: http://localhost:8000/docs

## 🔧 Environment Setup

The `.env` file is configured for Anthropic:
```env
LLM_PROVIDER=anthropic
CLAUDE_API_KEY=sk-ant-api03-...
LLM_MODEL=claude-3-5-haiku-20241022
MAX_QUESTIONS_PER_SESSION=10
MIN_QUESTIONS_PER_SESSION=1
```

## 📊 Database

The app uses the database at:
```
backend/db/homeworkhelper.db
```

With 79 active grammar topics across categories:
- parts_of_speech (8 topics)
- punctuation (12 topics)
- vocabulary (10 topics)
- sentence_structure (12 topics)
- literary_devices (9 topics)
- grammar_mechanics (10 topics)
- writing_quality (14 topics)

## 🎯 Next Steps

### To Merge into `fastapi-backend`:
1. Test thoroughly on this branch
2. Go to your main repo directory
3. Checkout `fastapi-backend`
4. Merge `anthropic-migration`:
   ```bash
   git merge anthropic-migration
   ```

### Future Work (TODO):
- [ ] Implement hints system (requires normalization utils)
- [ ] Add attempts tracking API for analytics
- [ ] Build React frontend
- [ ] Re-enable OCR router
- [ ] Fix legacy llm router for backward compatibility

## 📁 Key Files Modified

- `backend/app/clients/llm_client.py` - Anthropic integration
- `backend/app/services/grammar_services.py` - Practice session logic
- `backend/app/routers/grammar_router.py` - New endpoints
- `backend/app/core/settings.py` - Configuration
- `requirements.txt` - Dependencies
- `.env` - API keys and settings

## 🧪 Example Response

```json
{
  "num_questions": 2,
  "category": "parts_of_speech",
  "questions": [
    {
      "topic": "noun",
      "category": "parts_of_speech",
      "question": "Which word is a noun?",
      "options": ["run", "quickly", "dog", "happy"],
      "correct_answer": "dog",
      "explanation": "A noun names a person, place, thing, or idea."
    },
    {
      "topic": "verb",
      "category": "parts_of_speech",
      "question": "Which word shows action?",
      "options": ["Sarah", "plays", "soccer", "after"],
      "correct_answer": "plays",
      "explanation": "A verb shows action or state of being."
    }
  ]
}
```

## 💡 Notes

- Server must be run from the project root directory
- Python 3.12 is being used
- All LLM calls now go through Anthropic Claude API
- The worktree is at: `/Users/brandonedwards/.claude-worktrees/HomeworkHelper/pedantic-moore/`
- Main repo is at: `/Users/brandonedwards/Library/CloudStorage/OneDrive-Personal/Python Projects/GitHub/PythonProject/HomeworkHelper/`
