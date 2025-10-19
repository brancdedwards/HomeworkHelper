# parser_newsletter.py
import re
from datetime import datetime

def extract_topic(line: str) -> str:
    """
    Extracts topic keywords from a newsletter line.
    Example: "Grammar: Adverbs" → "adverbs"
    """
    parts = re.split(r'[:\-]', line)
    return parts[1].strip().lower().replace(" ", "_") if len(parts) > 1 else line.strip().lower()

def get_date(text: str) -> str:
    """
    Finds a date in the newsletter text, defaults to today's date if missing.
    """
    match = re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text)
    if match:
        try:
            date_obj = datetime.strptime(match.group(), "%m/%d/%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return datetime.today().strftime("%Y-%m-%d")

def parse_newsletter(text: str):
    """
    Parse raw newsletter text into structured subject-topic-date records.
    """
    subjects = ["grammar", "reading", "math", "writing", "science"]
    results = []

    for line in text.splitlines():
        for subject in subjects:
            if subject in line.lower():
                topic = extract_topic(line)
                date = get_date(text)
                results.append({"subject": subject, "topic": topic, "date": date})
    return results

if __name__ == "__main__":
    # Example test
    sample_text = """
    Week of 10/14/2025
    Grammar: Adverbs
    Reading: Point of View
    Math: Fractions
    """
    parsed = parse_newsletter(sample_text)
    for item in parsed:
        print(item)


# topic_manager.py
import os
import yaml

def update_topics(parsed_topics, yaml_dir="data/"):
    """
    Synchronizes parsed newsletter topics with their respective YAML files.
    Creates or updates entries automatically.
    """
    os.makedirs(yaml_dir, exist_ok=True)

    for topic in parsed_topics:
        subject = topic["subject"]
        topic_name = topic["topic"].lower().replace(" ", "_")
        yaml_path = os.path.join(yaml_dir, f"{subject}_hints.yaml")

        if not os.path.exists(yaml_path):
            with open(yaml_path, "w") as f:
                yaml.safe_dump({}, f)

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f) or {}

        if topic_name in data:
            data[topic_name]["active"] = True
            data[topic_name]["last_seen_date"] = topic["date"]
        else:
            data[topic_name] = {
                "definition": "Pending definition.",
                "examples": [],
                "subject": subject,
                "active": True,
                "grade_level": 5,
                "last_seen_date": topic["date"],
                "link": ""
            }

        with open(yaml_path, "w") as f:
            yaml.safe_dump(data, f)

if __name__ == "__main__":
    # Example test
    from parser_newsletter import parse_newsletter

    text = """
    Week of 10/14/2025
    Grammar: Adverbs
    Reading: Point of View
    Math: Fractions
    """
    topics = parse_newsletter(text)
    update_topics(topics)
    print("YAML files updated successfully.")


