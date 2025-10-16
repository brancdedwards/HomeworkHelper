

import os
import random
import requests
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

# ---------- CONFIG ----------
DB_PATH = "data/homework_helper.db"
LOCAL_PASSAGE_DIR = "data/passages"
os.makedirs(LOCAL_PASSAGE_DIR, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)

# ---------- UTILITIES ----------
def load_local_passages():
    """Load all .txt files in data/passages as passages."""
    passages = []
    for fname in os.listdir(LOCAL_PASSAGE_DIR):
        if fname.endswith(".txt"):
            with open(os.path.join(LOCAL_PASSAGE_DIR, fname), "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    passages.append(text)
    return passages

def fetch_from_gutendex():
    """Fetch a random children's book from the Gutendex API and return cleaned text."""
    try:
        page = random.randint(1, 5)
        url = f"https://gutendex.com/books/?topic=children&languages=en&page={page}"
        r = requests.get(url, timeout=10)
        data = r.json()
        book = random.choice(data["results"])
        title = book["title"]
        text_url = None
        for fmt in book["formats"]:
            if fmt.startswith("text/plain"):
                text_url = book["formats"][fmt]
                break
        if not text_url:
            print(f"No text/plain found for {title}")
            return None
        txt = requests.get(text_url, timeout=15).text
        print(f"Fetched '{title}' from Gutendex.")
        return clean_text(txt)
    except Exception as e:
        print(f"Error fetching from Gutendex: {e}")
        return None

def clean_text(text):
    """Remove headers, footers, and artifacts from Project Gutenberg text."""
    start = text.find("*** START")
    end = text.find("*** END")
    if start != -1 and end != -1:
        text = text[start:end]
    text = text.replace("\r", "").strip()
    return text

def split_into_passages(text, min_len=300, max_len=800):
    """Split long text into smaller passages based on paragraphs."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 0]
    passages = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < max_len:
            current += "\n\n" + p
        else:
            if len(current) > min_len:
                passages.append(current.strip())
            current = p
    if len(current) > min_len:
        passages.append(current.strip())
    random.shuffle(passages)
    return passages

def load_random_passage(save_to_db=True):
    """Load a random passage from local files or Gutendex. Save to DB if requested."""
    local_passages = load_local_passages()
    text = None
    source = "local"

    if local_passages:
        text = random.choice(local_passages)
        print("Loaded passage from local library.")
    else:
        text = fetch_from_gutendex()
        if text:
            chunks = split_into_passages(text)
            if chunks:
                text = random.choice(chunks)
                source = "gutendex"
                print("Loaded passage from Gutendex.")
            else:
                print("No valid chunks extracted from Gutendex.")
                return None
        else:
            print("Failed to fetch passage from Gutendex.")
            return None

    if save_to_db:
        try:
            db = SessionLocal()
            db.execute(
                "INSERT INTO passages (session_id, original_text, simplified_text) VALUES (NULL, ?, NULL)",
                (text,)
            )
            db.commit()
            db.close()
            print("Saved passage to database.")
        except Exception as e:
            print(f"Could not save passage to DB: {e}")

    return text

if __name__ == "__main__":
    passage = load_random_passage(save_to_db=False)
    print("\n--- SAMPLE PASSAGE ---\n")
    print(passage[:800] + "..." if passage else "No passage found.")