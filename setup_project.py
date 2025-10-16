import os
import sqlite3
from textwrap import dedent

def create_file(path, content):
    """Create a file with given content only if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(dedent(content).strip() + "\n")
        print(f"🆕 Created file: {path}")
    else:
        print(f"✅ Skipped (already exists): {path}")

def main():
    base_dir = os.getcwd()
    print(f"📁 Setting up Homework Helper project in: {base_dir}")

    # Directories to ensure exist
    dirs = [
        "data",
        "models",
        "utils",
        "modules"
    ]
    for d in dirs:
        path = os.path.join(base_dir, d)
        os.makedirs(path, exist_ok=True)
        print(f"📂 Ensured directory: {path}")

    # SQLite database
    db_path = os.path.join(base_dir, "data", "homework_helper.db")
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.commit()
        conn.close()
        print(f"🆕 Created database: {db_path}")
    else:
        print(f"✅ Database already exists: {db_path}")

    # app.py placeholder
    app_py = '''
    import streamlit as st

    st.title("📚 Homework Helper — Reading & Grammar (Setup Test)")
    st.write("Setup completed successfully! You can now build the full app here.")
    '''
    create_file(os.path.join(base_dir, "app.py"), app_py)

    # requirements.txt
    reqs = """
    streamlit>=1.37.0
    openai>=1.40.0
    spacy>=3.7.0
    python-dotenv>=1.0.1
    sqlalchemy>=2.0.0
    fpdf2>=2.7.0
    """
    create_file(os.path.join(base_dir, "requirements.txt"), reqs)

    # .env.example
    env_example = """
    # Copy to .env and fill in your key
    OPENAI_API_KEY=sk-yourkeyhere
    """
    create_file(os.path.join(base_dir, ".env.example"), env_example)

    # README.md
    readme = """
    # Homework Helper

    This script bootstraps the project structure for a cross‑platform (Mac + Windows) setup.

    ## Folders
    - **data/** — Stores local SQLite database
    - **models/** — SQLAlchemy ORM models
    - **utils/** — Helper modules (AI, PDF, grammar)
    - **modules/** — Individual Streamlit modules for modular app design

    ## Quick Start
    1. Create a virtual environment:
       ```bash
       python -m venv .venv
       source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
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
    """
    create_file(os.path.join(base_dir, "README.md"), readme)

    # Placeholder files for modular structure
    placeholders = {
        "modules/learning_mode.py": "import streamlit as st\n\ndef show():\n    st.title('📖 Learning Mode')\n    st.write('Coming soon...')",
        "modules/grammar_practice.py": "import streamlit as st\n\ndef show():\n    st.title('📘 Grammar Practice')\n    st.write('Coming soon...')",
        "utils/llm_helpers.py": "from openai import OpenAI\nimport os\nfrom dotenv import load_dotenv\n\nload_dotenv()\nclient = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))\n\ndef call_llm(prompt, model='gpt-4o-mini'):\n    try:\n        resp = client.chat.completions.create(\n            model=model,\n            messages=[\n                {'role': 'system', 'content': 'You are a patient tutor for a 5th grader.'},\n                {'role': 'user', 'content': prompt}\n            ],\n            temperature=0.2\n        )\n        return resp.choices[0].message.content.strip()\n    except Exception as e:\n        return f'(LLM error: {e})'",
        "utils/db.py": "from sqlalchemy import create_engine\nfrom sqlalchemy.orm import sessionmaker, declarative_base\nimport os\n\nDB_PATH = 'data/homework_helper.db'\nengine = create_engine(f'sqlite:///{DB_PATH}', echo=False)\nSessionLocal = sessionmaker(bind=engine)\nBase = declarative_base()\n"
    }

    for path, content in placeholders.items():
        create_file(os.path.join(base_dir, path), content)

    print(f"\n✅ Project setup complete at {base_dir}")
    print("You can safely re-run this script; it will only add missing components.")
    print("Next steps:")
    print("  1. Activate your virtual environment.")
    print("  2. Run: pip install -r requirements.txt")
    print("  3. Launch Streamlit: streamlit run app.py")
    print("  4. Start adding logic to your modules inside /modules/")
    print("\nAll paths are cross‑platform and safe for Mac or Windows use.")

if __name__ == "__main__":
    main()