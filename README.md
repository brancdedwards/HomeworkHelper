# 🧠 HomeworkHelper

A Streamlit-based educational assistant for kids to **practice reading comprehension and grammar** — powered by the OpenAI API.

---

## 🚀 Features

- **Reading Mode**
  - Upload or paste a passage (from school assignments or PDFs)
  - Automatically generate simplified versions for 5th-grade readability
  - Generate comprehension questions
  - Explain vocabulary in plain English
  - Export session as a formatted PDF

- **Grammar Practice**
  - Automatically generates practice sentences
  - Creates grammar multiple-choice questions (e.g., part of speech, simile vs metaphor)
  - Randomized, adaptive question generation using GPT-4o-mini

- **Admin Standards Management**
  - Add weekly “What We’re Learning” concepts from school newsletters
  - Track subjects, dates, and vocabulary for reinforcement

- **History & Review**
  - View all past sessions with passages, questions, and answers
  - Export summaries or full lesson sessions to PDF

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| UI | [Streamlit](https://streamlit.io/) |
| Backend | Python 3.13 |
| Database | SQLite (simple local storage) |
| AI/LLM | OpenAI GPT-4o-mini |
| PDF Export | ReportLab |
| Environment | dotenv |
| Editor | PyCharm |

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/brandonedwards/HomeworkHelper.git
cd HomeworkHelper
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_api_key_here
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🧱 Project Structure

```
HomeworkHelper/
│
├── app.py                     # Main Streamlit app entry point
├── modules/                   # UI modules
│   ├── add_passage.py
│   ├── learning_mode.py
│   ├── grammar_practice.py
│   ├── view_history.py
│   └── admin_standards.py
│
├── utils/                     # Helper modules
│   ├── db.py
│   ├── llm_helpers.py
│   └── passage_loader.py
│
├── homework_helper.sqlite     # Local SQLite database
├── setup_project.py           # Initializes DB + folders
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔒 Security Notes

- `.env` and SQLite databases are excluded from version control.
- API keys and personal data are never committed.
- Safe to make the repository public.

---

## 🧭 Roadmap

- [ ] Add multi-grade reading difficulty adjustment  
- [ ] Build admin dashboard for managing vocabulary and concepts  
- [ ] Add quiz scoring and student progress tracking  
- [ ] Enable optional local/offline mode for privacy  

---

## 💡 Inspiration

Created to make schoolwork more interactive and supportive —  
especially for kids who learn best through guided feedback and adaptive practice.

---

## 📜 License

MIT License — open for educational use and modification.