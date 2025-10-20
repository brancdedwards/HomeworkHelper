import os, yaml, sqlite3
from functools import lru_cache

DB_PATH = "data/homework_helper.db"  # adjust if different

# Add this import to ensure DB mode works
try:
    from utils.concept_map_db import get_concept, DB_PATH
except ImportError:
    get_concept = None
    DB_PATH = None

DATA_DIR = os.path.join(os.path.dirname(__file__),"../" "data")

def _load_concept_map_uncached(subject: str = "grammar"):
    """
    Loads the concept map from DB if available; falls back to YAML.
    """
    import streamlit as st
    from utils.concept_map_db import DB_PATH

    # Prefer DB if present
    if DB_PATH and os.path.exists(DB_PATH):
        st.write(f"DEBUG: Using DB mode for subject '{subject}'")
        return {"db_mode": True}

    yaml_path = os.path.join(DATA_DIR, f"{subject}_concept_map.yaml")
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"No concept map found for subject: {subject} ({yaml_path})")

    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)

@lru_cache(maxsize=None)
def load_concept_map(subject: str = "grammar"):
    return _load_concept_map_uncached(subject)




def diagnostic_concept_map():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all grammar topics
    cursor.execute("SELECT name FROM topics WHERE subject = 'grammar' AND active = 1")
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"🧩 Checking {len(topics)} grammar topics...\n")

    working, missing, errors = [], [], []

    for topic in topics:
        try:
            qf = get_question_focus(topic, "grammar")
            if qf:
                print(f"✅ {topic:25} → {qf}")
                working.append(topic)
            else:
                print(f"⚠️  {topic:25} → None returned")
                missing.append(topic)
        except Exception as e:
            print(f"❌ {topic:25} → Exception: {e}")
            errors.append((topic, str(e)))

    print("\nSummary:")
    print(f"✅ Working: {len(working)}")
    print(f"⚠️  Missing: {len(missing)}")
    print(f"❌ Errors:  {len(errors)}")

    if missing:
        print("\n⚠️  Missing Topics:")
        for m in missing:
            print("   -", m)
    if errors:
        print("\n❌ Error Topics:")
        for e in errors:
            print("   -", e)


if __name__ == "__main__":
    diagnostic_concept_map()

def get_question_focus(topic: str, subject: str = "grammar") -> str:
    """
    Retrieves the 'question_focus' prompt for a given topic from the concept map YAML.
    Returns None if not found.
    """
    import streamlit as st

    def _find_question_focus(node, topic, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                current_path = f"{path}/{key}" if path else key
                # st.write(f"DEBUG: Traversing path: {current_path}")
                if key == topic and isinstance(value, dict) and "question_focus" in value:
                    qf = value["question_focus"]
                    st.write(f"DEBUG: Found question_focus at path: {current_path}: {qf}")
                    return qf
                elif topic.lower() in key.lower() or key.lower() in topic.lower():
                    st.write(f"DEBUG: Fuzzy match found for '{topic}' in key '{key}' at path: {current_path}")
                    if isinstance(value, dict) and "question_focus" in value:
                        return value["question_focus"]
                else:
                    found = _find_question_focus(value, topic, current_path)
                    if found is not None:
                        return found
        return None

    try:
        concept_map = load_concept_map(subject)
        if not concept_map:
            st.write("DEBUG: Concept map is None or empty.")
            return None
        if subject in concept_map:
            concept_map = concept_map[subject]
            st.write(f"DEBUG: Using concept_map['{subject}'] as subject_data")
        # Replacement block for DB mode or YAML fallback
        if "db_mode" in concept_map and concept_map["db_mode"] is True:
            st.write(f"DEBUG: DB mode active. Using get_concept() for '{topic}'")
            if get_concept:
                st.write("DEBUG: trying get_concept() method")
                try:
                    st.write(f"DEBUG: Retrieving from get_concept: Topic: {topic} Subject: {subject}")
                    concept = get_concept(topic, subject)
                    # Code fails at get_concept(), returns none
                    # st.write(f"DEBUG: Retrieved from get_concept: {concept}")
                    st.write(f"DEBUG: Retrieved from get_concept: {concept}")
                    if concept:
                        st.write(f"DEBUG: Retrieved from DB -> Category: {concept['category']}, Question Focus: {concept['question_focus']}")
                        return concept.get("question_focus")
                    else:
                        st.write(f"DEBUG: No DB entry found for topic '{topic}'")
                except Exception as e:
                    st.write(f"DEBUG: Exception in get_question_focus (DB mode): {e}")
            else:
                st.write("DEBUG: get_concept() not defined. Falling back to YAML logic.")
        else:
            st.write("DEBUG: Using top-level concept_map as subject_data")
            return _find_question_focus(concept_map, topic)
    except Exception as e:
        st.write(f"DEBUG: Exception in get_question_focus: {e}")
        pass
    return None

def detect_category_for_topic(topic: str, subject: str = "grammar") -> str:
    """
    Detects which category a topic belongs to within a subject's concept map.
    Returns 'general' if not found.
    """
    import streamlit as st

    def _find_category(node, topic, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                st.write(f"DEBUG: Key: {key}, Value: {value}")
                current_path = f"{path}/{key}" if path else key
                # st.write(f"DEBUG: Traversing path: {current_path}")
                if key.lower() == topic.lower():
                    st.write(f"DEBUG: Found topic '{topic}' at path: {current_path}")
                    # Return the category part of the path (parent key)
                    # Since key is topic, return the last category in path before topic
                    # path may be like "category/subcategory/topic"
                    parts = current_path.split('/')
                    if len(parts) >= 2:
                        category = parts[-2]
                    else:
                        category = parts[0]
                    return category
                elif topic.lower() in key.lower() or key.lower() in topic.lower():
                    # st.write(f"DEBUG: Fuzzy match found for '{topic}' in key '{key}' at path: {current_path}")
                    parts = current_path.split('/')
                    if len(parts) >= 2:
                        category = parts[-2]
                    else:
                        category = parts[0]
                    return category
                elif isinstance(value, dict):
                    found = _find_category(value, topic, current_path)
                    if found is not None:
                        return found
                elif isinstance(value, list):
                    # If value is a list, check if topic is in list (case insensitive)
                    if any(t.lower() == topic.lower() for t in value):
                        st.write(f"DEBUG: Found topic '{topic}' in list at path: {current_path}")
                        return key
        return None

    try:
        concept_map = load_concept_map(subject)
        subject_data = concept_map.get(subject, concept_map)
        st.write(f"DEBUG: Loaded concept map keys: {list(subject_data.keys())}")

        category = _find_category(subject_data, topic)
        if category:
            return category

    except Exception as e:
        st.write(f"DEBUG: Exception in detect_category_for_topic: {e}")

    return "general"