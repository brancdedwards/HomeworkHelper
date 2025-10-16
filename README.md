# Homework Helper

This script bootstraps the project structure for a cross‑platform (Mac + Windows) setup.

## Folders
- **data/** — Stores local SQLite database
- **models/** — SQLAlchemy ORM models
- **utils/** — Helper modules (AI, PDF, grammar)

## Quick Start
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` from `.env.example` and add your API key.
4. Run the app:
   ```bash
   streamlit run app.py
   ```
