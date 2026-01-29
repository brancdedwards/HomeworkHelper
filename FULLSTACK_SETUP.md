# 🚀 Grammar Practice Full Stack App - Complete Setup Guide

Your complete Grammar Practice application with React frontend and FastAPI backend powered by Anthropic Claude!

## 📍 Project Structure

```
HomeworkHelper/
├── backend/
│   ├── app/
│   │   ├── clients/
│   │   │   └── llm_client.py          # Anthropic Claude integration
│   │   ├── routers/
│   │   │   └── grammar_router.py      # Practice session endpoints
│   │   ├── services/
│   │   │   └── grammar_services.py    # Question generation logic
│   │   └── main.py                    # FastAPI app with CORS
│   └── db/
│       └── homeworkhelper.db          # SQLite database (79 topics)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PracticeSetup.jsx      # Configuration screen
│   │   │   └── QuestionDisplay.jsx    # Question answering
│   │   ├── services/
│   │   │   └── api.js                 # Backend API calls
│   │   └── App.jsx                    # Main React app
│   └── package.json
├── .env                                # API keys & configuration
└── start_server.sh                     # Backend startup script
```

## 🏃 Quick Start (Both Servers)

### Terminal 1: Start Backend
```bash
cd /path/to/HomeworkHelper
./start_server.sh

# Or manually:
source .venv/bin/activate  # if using venv
uvicorn backend.main:app --reload --port 8000
```

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

### Access the App
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ✨ Features

### Frontend (React + Tailwind CSS)
- 🎲 **Random or Category-Specific Practice**
- 📊 **Progress Tracking** - Visual progress bar
- ✅ **Instant Feedback** - Correct/incorrect with explanations
- 🎯 **Score Display** - Track your performance
- 📱 **Responsive Design** - Works on all devices
- 🎨 **Modern UI** - Beautiful gradient background, smooth animations

### Backend (FastAPI + Anthropic Claude)
- 🤖 **AI-Powered Questions** - Claude 3.5 Haiku generates educational content
- 📚 **79 Grammar Topics** - Across 11 categories
- 🔄 **Flexible Sessions** - 1-10 questions per session
- 🎯 **Category Filtering** - Focus on specific grammar concepts
- ⚡ **Fast & Efficient** - Optimized for quick responses

## 🎮 How to Use

1. **Choose Practice Mode**
   - 🎲 Random Mix - Questions from all categories
   - 🎯 Choose Category - Focus on specific topics

2. **Select Number of Questions**
   - Use slider to choose 1-10 questions

3. **Generate Practice Session**
   - Click "Generate Practice Session"
   - Wait for Claude to create your questions

4. **Answer Questions**
   - Click your answer choice
   - Click "Check Answer" to submit
   - Get instant feedback with explanations

5. **Track Progress**
   - See your score update in real-time
   - Review correct/incorrect answers
   - View final summary when complete

## 📚 Available Grammar Categories

1. **Parts of Speech** (8 topics)
   - Noun, Verb, Adjective, Adverb, Pronoun, Preposition, Conjunction, Interjection

2. **Sentence Structure** (12 topics)
   - Subject, Predicate, Clause, Phrase, Compound sentences, etc.

3. **Punctuation** (12 topics)
   - Comma, Period, Quotation marks, Apostrophe, etc.

4. **Vocabulary** (10 topics)
   - Synonyms, Antonyms, Homonyms, Prefixes, Suffixes, etc.

5. **Literary Devices** (9 topics)
   - Simile, Metaphor, Imagery, etc.

6. **Grammar Mechanics** (10 topics)
   - Capitalization, Spelling, etc.

7. **Writing Quality** (14 topics)
   - Organization, Transitions, Clarity, etc.

## 🔧 Configuration

### Environment Variables (.env)
```bash
# LLM Configuration
LLM_PROVIDER=anthropic
CLAUDE_API_KEY=your_api_key_here
LLM_MODEL=claude-3-5-haiku-20241022

# Question Limits
MAX_QUESTIONS_PER_SESSION=10
MIN_QUESTIONS_PER_SESSION=1
```

### Frontend API Configuration
Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 🐛 Troubleshooting

### Backend Issues

**Can't connect to backend:**
```bash
# Check if server is running
curl http://localhost:8000/

# Check logs
tail -f /tmp/server.log  # if using start_server.sh
```

**Database not found:**
```bash
# Make sure database exists
ls -la backend/db/homeworkhelper.db

# Copy from worktree if needed
cp /path/to/worktree/backend/db/homeworkhelper.db backend/db/
```

**Anthropic API errors:**
```bash
# Verify API key is set
python -c "from backend.app.core.settings import settings; print('Key set:', bool(settings.CLAUDE_API_KEY))"
```

### Frontend Issues

**Can't connect to backend:**
- Check CORS is enabled in `backend/main.py`
- Verify backend is running on port 8000
- Check browser console for errors

**Tailwind styles not working:**
```bash
cd frontend
npm install
npm run dev
```

**Port 3000 already in use:**
```bash
# Change port in vite.config.js
server: {
  port: 3001,  // Change this
}
```

## 📊 API Endpoints

### GET /grammar/categories
Returns list of available grammar categories

**Response:**
```json
{
  "categories": ["parts_of_speech", "punctuation", ...],
  "count": 11
}
```

### POST /grammar/practice/session
Generate a practice session

**Request:**
```json
{
  "num_questions": 5,
  "category": "parts_of_speech",  // or null for random
  "difficulty": "normal",
  "style": "default"
}
```

**Response:**
```json
{
  "num_questions": 5,
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
    ...
  ]
}
```

## 🚀 Deployment (Future)

### Backend
- Deploy to Railway, Render, or AWS
- Set environment variables
- Update CORS origins

### Frontend
- Build: `npm run build`
- Deploy to Vercel, Netlify, or Cloudflare Pages
- Update API_BASE_URL to production backend

## 📝 Next Features

- [ ] User authentication
- [ ] Save practice history
- [ ] Analytics dashboard
- [ ] Hints system for wrong answers
- [ ] Print/export results
- [ ] Dark mode
- [ ] Mobile app (React Native)

## 🎯 Performance

- **Backend**: ~500-1000ms per question generation (Claude Haiku)
- **Frontend**: Instant page loads with Vite
- **Database**: 79 topics, <1MB
- **Cost**: ~$0.001 per practice session (Anthropic pricing)

## 🤝 Support

For issues or questions:
1. Check this README
2. Check `ANTHROPIC_MIGRATION.md` for API details
3. Check `frontend/README_FRONTEND.md` for frontend specifics

---

**Branch**: `anthropic-migration`
**Stack**: React + FastAPI + Anthropic Claude + Tailwind CSS
**Database**: SQLite (79 grammar topics)

Built with ❤️ for better learning!
