# ==============================
# 📘 Homework Helper - LLM Helpers
# ==============================
# Centralized utilities for handling OpenAI API calls.
# Includes text simplification, question generation, vocabulary explanations,
# and grammar-related sentence/question generation.
from typing import Any
from jedi.api.classes import defined_names
from openai import OpenAI
import os, yaml, re, json
from dotenv import load_dotenv
import streamlit as st
from utils.concept_map_loader import load_concept_map, detect_category_for_topic, get_question_focus
from utils.db import get_prompt_template


# ---------- Setup ----------
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
yaml_path = os.path.join("data", "grammar_hints.yaml")
DEBUG = False  # Set to False to disable debug logs


# ---------- Core LLM Wrapper ----------
def call_llm(prompt, model='gpt-4o-mini', temperature=0.2): #TODO: add subject as parameter (e.g. Math, grammar, etc)
    """Generic LLM call handler."""
    try:
        if DEBUG: st.write(f"DEBUG: LLM call with prompt: ")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': 'You are a patient tutor for a 5th grader. Always explain clearly and simply. Do not give direct answers initially. Let the student work the questions out.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f'(LLM error: {e})'

# ---------- Reading Comprehension Functions ----------
def simplify_text(text):
    """Simplify a passage for a 5th grader."""
    prompt = f"Rewrite this passage in clear, kid-friendly language for a 5th grader:\n\n{text}"
    return call_llm(prompt)

def generate_questions(text, n=3):
    """Generate comprehension questions for the given passage."""
    prompt = f"Create {n} short comprehension questions (no answers) for a 5th grader based on this passage:\n\n{text}"
    return call_llm(prompt)

def explain_word(word, context):
    """Explain the meaning of a word in context."""
    prompt = f"Explain the word '{word}' to a 5th grader using this context:\n\n{context}"
    return call_llm(prompt)

# ---------- Grammar Functions ----------
def generate_sentences(n=5):
    """Generate a clean list of N simple sentences for grammar practice.
    Tries to parse a JSON array from the model; falls back to line-splitting.
    """
    import json, re

    prompt = (
        "You are generating short practice sentences for a 5th grader. "
        f"Write exactly {n} simple, self-contained sentences (8–20 words each). "
        "Use everyday vocabulary. No dialogue, no quoted speech, no numbers or bullets. "
        "Return ONLY valid JSON: an array of strings, like [\"The cat sat on the warm windowsill.\", ...]. "
        "Do not include any preface or explanation."
    )

    text = call_llm(prompt, temperature=0.1)

    # Try to extract and parse a JSON array
    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            text = match.group(0)
        items = json.loads(text)
        if not isinstance(items, list):
            raise ValueError("Not a list")
        candidates = [str(s).strip() for s in items]
    except Exception:
        # Fallback: split lines and clean
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        candidates = []
        for ln in lines:
            # Drop meta/intros like "Sure" or "Here are" etc.
            if re.match(r"^(sure|here|let\'s|let us|okay|ok)\b", ln.lower()):
                continue
            # Remove leading numbering
            ln = re.sub(r"^\s*\d+\s*[\).:-]?\s*", "", ln)
            candidates.append(ln)

    # Final filtering: keep only plausible sentences
    def good(s: str) -> bool:
        s = s.strip()
        if len(s.split()) < 4:
            return False
        if not re.search(r"[.!?]$", s):
            return False
        # Avoid sentences that describe the prompt itself
        if re.search(r"(sentence|example|prompt|simple sentence)", s.lower()):
            return False
        return True

    sentences = [s for s in candidates if good(s)]

    # If we still don't have enough, truncate/extend gracefully
    if len(sentences) > n:
        sentences = sentences[:n]
    elif len(sentences) < n:
        # Duplicate last items to meet the requested count (better than failing UI)
        while sentences and len(sentences) < n:
            sentences.append(sentences[-1])
        # If completely empty, give safe placeholders
        if not sentences:
            sentences = [
                "The cat slept on the sunny porch.",
                "A blue bird landed on the fence.",
                "We packed snacks for the short hike.",
            ][:n]
    return sentences


def generate_grammar_question(sentence: object, category: object = None, include_answer: object = False) -> dict[str, str | list[str]] | Any:
    """
    Generates a multiple-choice grammar question for the provided sentence,
    guided by the provided category (e.g., vocabulary, punctuation, writing_quality).
    Returns a dict: {"prompt": str, "options": [str, ...]} by default,
    or includes "answer" if include_answer=True.
    """

    # Detect and sanitize placeholder-style inputs (e.g., "Practice question about nouns", "Question on prefix", etc.)
    if isinstance(sentence, dict):
        sentence = sentence.get("question", str(sentence))

    cleaned_sentence = sentence.strip()

    # Only treat as placeholder if it's short and not already a full question/prompt
    if len(cleaned_sentence.split()) <= 8 and re.fullmatch(
        r"(?i)\s*(?:practice\s*question|question\s*(?:on|about)?)\s*[:\-\s]*([a-zA-Z_ ]+)\s*\.?$",
        cleaned_sentence,
    ):
        placeholder_match = re.fullmatch(
            r"(?i)\s*(?:practice\s*question|question\s*(?:on|about)?)\s*[:\-\s]*([a-zA-Z_ ]+)\s*\.?$",
            cleaned_sentence,
        )
        if placeholder_match:
            topic_clean = placeholder_match.group(1).strip().replace("_", " ").title()
            sentence = f"Write a grammar practice question about {topic_clean} suitable for a 5th grader."
            if DEBUG:
                st.write(f"DEBUG: Placeholder sanitized → topic='{topic_clean}' → replaced with: {sentence}")
    else:
        if DEBUG:
            st.write(f"DEBUG: Skipped placeholder sanitization for valid sentence: {sentence}")

    # Safeguard: default category to "general" if None
    if not category:
        category = "general"

    CATEGORY_EXAMPLES = {
        "vocabulary": "Ask about what a word means, its prefix/suffix, or how it changes meaning.",
        "writing_quality": "Ask how to improve clarity, coherence, or sentence strength.",
        "punctuation": "Ask where punctuation should be placed or which punctuation mark is correct.",
        "sentence_structure": "Ask about subjects, verbs, clauses, or sentence order.",
        "literary_devices": "Ask which phrase shows a metaphor, simile, idiom, or personification.",
        "mechanics": "Ask about capitalization, spelling, or general grammar correctness.",
        "general": "Ask a basic grammar comprehension question suitable for a 5th grader."
    }

    category_instruction = CATEGORY_EXAMPLES.get(category.lower(), CATEGORY_EXAMPLES["general"])

    prompt = f"""
    You are a 5th-grade ELA tutor. Create ONE multiple-choice grammar question
    about this exact sentence:
    "{sentence}"

    The question should reflect the topic category: "{category}".
    {category_instruction}

    Write a thoughtful, age-appropriate question that tests understanding of this concept.
    Return ONLY valid JSON with keys exactly: "prompt", "options", and "answer".
    Example JSON:
    {{
      "prompt": "[Question here]",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }}
    No preface, no markdown, no explanations, no reasoning.
    """

    try:
        # category = detect_category_for_topic(topic, subject="grammar")
        # if DEBUG: st.write(f"DEBUG: Sending prompt to LLM with category '{category}' and topic {topic}...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        text = response.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
        obj = json.loads(text)

        # Minimal validation
        if not all(k in obj for k in ("prompt", "options", "answer")):
            raise ValueError("Missing keys")
        if not isinstance(obj.get("options"), list) or not obj.get("options"):
            raise ValueError("Options malformed")

        # Sanitize: remove answer leaks from prompt
        answer = obj.get("answer")
        def scrub_leaks(txt):
            return re.sub(r"(is correct|the answer is|correct answer)", "", txt, flags=re.I).strip()
        obj["prompt"] = scrub_leaks(obj.get("prompt", ""))

        if not include_answer:
            obj.pop("answer", None)

        return obj

    except Exception as e:
        fallback = {
            "prompt": f"Which word is a noun in the sentence: '{sentence}'?",
            "options": ["noun", "verb", "adjective", "adverb"],
            "answer": "noun",
        }
        if not include_answer:
            fallback.pop("answer", None)
        return fallback

# ---------- Grammar Hint Helper ----------
def get_grammar_hint(topic: str) -> str:
    """Retrieve grammar hint dynamically from grammar_hints.yaml."""
    import logging
    topic = topic.lower().strip()
    yaml_path = os.path.join("data", "grammar_combined.yaml")
    if not os.path.exists(yaml_path):
        return "Remember, think about how the word is used in the sentence."

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            grammar_data = yaml.safe_load(f)
            if not isinstance(grammar_data, dict):
                st.write("DEBUG: Invalid grammar_hints.yaml structure.", grammar_data)
                return "Remember, think about how the word is used in the sentence."
    except Exception as e:
        st.write("DEBUG: Failed to read or parse YAML", str(e))
        return "Remember, think about how the word is used in the sentence."

    if topic in grammar_data:
        data = grammar_data[topic]
        definition = str(data.get("definition", "")).strip()
        examples_list = data.get("examples", [])
        examples_md = ""
        if isinstance(examples_list, list) and examples_list:
            examples_md = "\n\n**Examples:**\n" + "\n".join(f"- {ex}" for ex in examples_list)
        link = data.get("link", "")
        link_md = f"\n\n[Click here to learn more about {topic}s]({link})" if link else ""
        # Compose hint: no topic repetition, clean markdown, natural capitalization
        hint_md = f"Remember, {definition.lower()}{examples_md}{link_md}"
        return hint_md
    else:
        return "Remember, think about how the word is used in the sentence."

# ---------- Active Topics Integration ----------
def get_active_topics(subject="grammar"):
    """
    Returns a list of currently active topics from the YAML file.
    """
    # yaml_path = os.path.join("data", f"{subject}_hints.yaml")
    if not os.path.exists(yaml_path):
        return []

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f) or {}
    return [key for key, val in data.items() if val.get("active", False)]

@st.cache_data(ttl=300)
def get_available_categories(conn=None):
    """
    Returns a list of distinct categories from concept_map that have ACTIVE topics.
    Used by the UI to populate the category dropdown.
    """
    from utils.db import get_connection

    if conn is None or not hasattr(conn, "cursor"):
        conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT cm.category
        FROM concept_map cm
        JOIN topics t ON cm.topic = t.name
        WHERE t.active = 1
          AND cm.category IS NOT NULL
          AND TRIM(cm.category) != ''
        ORDER BY LOWER(cm.category)
    """)
    rows = cur.fetchall()
    return [r[0] for r in rows] if rows else []

def generate_sentences_from_topics(conn=None, n=3, category=None):
    """
    Pulls active topics from DB, detects their categories using the concept map loader,
    and asks OpenAI for sentences for each, possibly customizing prompts per category.
    """
    # --- Integration point: load concept map for category detection ---
    from utils.db import get_connection
    import random
    if conn is None or not hasattr(conn, "cursor"):
        conn = get_connection()
    cursor = conn.cursor()
    # cursor.execute("SELECT cm.topic FROM concept_map cm join topics t on cm.topic = t.name WHERE t.active = 1;")
    if category:
        cursor.execute("""
                       SELECT cm.topic
                       FROM concept_map cm
                                JOIN topics t ON cm.topic = t.name
                       WHERE LOWER(cm.category) = LOWER(?)
                         AND t.active = 1;
                       """, (category,))
    else:
        cursor.execute("""
                       SELECT cm.topic
                       FROM concept_map cm
                                JOIN topics t ON cm.topic = t.name
                       WHERE t.active = 1;
                       """)
    active_topics = [row[0] for row in cursor.fetchall()]
    # if DEBUG: st.write(f"DEBUG: Active topics: {active_topics}")

    # Load concept map for category detection
    concept_map = load_concept_map()
    # if DEBUG: st.write(f"DEBUG: Loaded concept map: {concept_map}")

    # Randomly select up to n topics
    selected_topics = random.sample(active_topics, min(n, len(active_topics)))
    if DEBUG: st.write(f"DEBUG: Selected topics: {selected_topics}")
    sentences = []

    from utils.concept_map_db import get_concept
    topics_data = []
    for topic in selected_topics:
        if DEBUG: st.write(f"DEBUG from llm_helpers (b4 category/question_focus lookup): Topic: {topic}")
        # Try to get from DB first
        concept_record = get_concept(topic, subject="grammar")
        if concept_record:
            category = concept_record.get("category") if isinstance(concept_record, dict) else getattr(concept_record, "category", None)
            question_focus = concept_record.get("question_focus") if isinstance(concept_record, dict) else getattr(concept_record, "question_focus", None)
            if DEBUG: st.write(f"DEBUG Topic: {topic} - used DB record for category/question_focus. Category: {category}, Question Focus: {question_focus}")
        else:
            category = detect_category_for_topic(topic, subject="grammar")
            question_focus = get_question_focus(topic, subject="grammar")
            if DEBUG: st.write(f"DEBUG Topic: {topic} - used fallback detect_category/get_question_focus. Category: {category}, Question Focus: {question_focus}")
        if question_focus:
            # Instead of calling the LLM here, collect info for batching
            topics_data.append({
                "topic": topic,
                "category": category,
                "question_focus": question_focus,
            })
            # --- Debug: cache category in session state for visibility
            st.session_state["last_category"] = category
            if DEBUG: st.write(f"DEBUG: Cached last_category in session: {category}")
        # For now, skip the other branches (vocabulary/category-only) for batching
        # To keep the batching logic simple, only batch those with question_focus
        # Optionally, you could batch all, but per instructions, just batch the question_focus ones

    # --- Remove batching/groupby logic; do one LLM call per topic ---
# --- Per-topic LLM call with guardrails and sanitization ---
    if topics_data:
        for t in topics_data:
            if DEBUG: st.write(f"DEBUG: Generating single-question call for topic '{t['topic']}' in category '{t['category']}'")
            example = None  # ensure example is always initialized
            prompt = ""  # ensure prompt is defined before use

            if example:
                prompt += f"\nPlease see this example for guidance: {example}"

            # Enforce strict JSON output
            prompt += (
                "\n\nIMPORTANT: Return ONLY valid JSON in this exact structure, no explanations or extra text:\n"
                "{\n"
                f'  "topic": "{t["topic"]}",\n'
                '  "question": "[Your question here]",\n'
                '  "options": ["Option A", "Option B", "Option C", "Option D"],\n'
                '  "answer": "Correct Option"\n'
                "}"
            )

            text = call_llm(prompt)
            prompt_template = None
            try:
                cursor.execute("""
                               SELECT prompt_template, example
                               FROM prompts
                               WHERE LOWER(category) = LOWER(?)
                                 AND LOWER(topic) = LOWER(?)
                               LIMIT 1;
                               """, (t['category'], t['topic']))
                row = cursor.fetchone()
                if row:
                    prompt_template, db_example = row
                    if db_example:
                        example = db_example
                    if DEBUG:
                        st.write(f"DEBUG: Found DB prompt template for {t['topic']} ({t['category']})")
            except Exception as e:
                if DEBUG:
                    st.write(f"DEBUG: Failed to fetch prompt template for {t['topic']}: {e}")

            # Build prompt from template or fallback
            if prompt_template:
                prompt = prompt_template.format(
                    topic=t['topic'],
                    category=t['category'],
                    question_focus=t['question_focus']
                )
            else:
                prompt = f"""
            You are a 5th-grade English tutor. Generate ONE multiple-choice grammar question for the topic "{t['topic']}".
            This question should directly test the concept named in the topic.
            Category: {t['category']}
            Question Focus: {t['question_focus']}

            Rules:
            - The question must be self-contained and natural for a 5th grader.
            - Include 4 answer choices.
            - Clearly indicate the correct answer.

            Return ONLY valid JSON in this format:
            {{
              "topic": "{t['topic']}",
              "question": "[Your question here]",
              "options": ["A", "B", "C", "D"],
              "answer": "Correct Option"
            }}
            """
            # Append example if available
            if example:
                prompt += f"\nPlease see this example for guidance: {example}"

            # Enforce strict JSON output
            prompt += (
                "\n\nIMPORTANT: Return ONLY valid JSON in this exact structure, no explanations or extra text:\n"
                "{\n"
                f'  "topic": "{t["topic"]}",\n'
                '  "question": "[Your question here]",\n'
                '  "options": ["Option A", "Option B", "Option C", "Option D"],\n'
                '  "answer": "Correct Option"\n'
                "}"
            )

            text = call_llm(prompt)
            # ---- GUARDRAIL: enforce strict JSON output and clean up any meta prefixes ----
            import json, re
            text = text.strip()
            text = re.sub(r"(?i)(^sure|^okay|^here|^let.?s|^of course).*", "", text)
            text = re.sub(r"(?i)(question on|topic:|category:)\s*[A-Za-z_ ]+[:\-]*", "", text)
            text = re.sub(r"(?i)please see.*guidance.*", "", text)

            # Attempt to extract JSON
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                text = match.group(0)

            # Safety: don't attempt to parse if empty or truncated
            if not text or len(text.strip()) < 5:
                if DEBUG:
                    st.write(f"DEBUG: Empty or invalid JSON text for topic '{t['topic']}'. Text was: {repr(text[:100])}")
                continue

            try:
                item = json.loads(text)
            except json.JSONDecodeError:
                if DEBUG:
                    st.write(f"DEBUG: JSON parse failed once, retrying sanitize pass for topic '{t['topic']}'")
                text = re.sub(r"```(?:json)?|```", "", text)
                text = re.sub(r"(?i)example json.*?\{", "{", text)
                text = text.strip()

                # Skip if text still empty or too short
                if not text or len(text.strip()) < 5:
                    if DEBUG:
                        st.write(f"DEBUG: JSON text still invalid/empty after sanitize for topic '{t['topic']}' → skipping")
                    continue

                try:
                    item = json.loads(text)
                except json.JSONDecodeError as e:
                    if DEBUG:
                        st.write(f"DEBUG: JSON parsing failed again for topic '{t['topic']}' — raw text:\n{text}\nError: {e}")
                    continue  # Skip instead of crashing

            # Validate structure strictly
            if not isinstance(item, dict) or not all(k in item for k in ("question", "options", "answer")):
                if DEBUG: st.write(f"DEBUG: Invalid or incomplete JSON for topic '{t['topic']}' → skipping")
                continue

            # Clean any leftover phrasing from the question
            item["question"] = re.sub(
                r"(?i)(question on|topic:|category:)\s*[A-Za-z_ ]+[:\-]*", "", item["question"]
            ).strip()
            sentences.append(item)
            if DEBUG: st.write(f"DEBUG: Added question for topic '{t['topic']}'")

    # --- Final guardrail: drop malformed or duplicate entries ---
    sentences = [
        s for s in sentences
        if isinstance(s, dict)
        and s.get("question")
        and isinstance(s.get("options"), list)
        and len(s["options"]) >= 2
    ]

    # --- Post-processing: flatten and balance across categories ---
    # Avoid duplicate questions by using a set while preserving order (based on question string)
    seen = set()
    unique_questions = []
    for q in sentences:
        # Use question text as unique key if q is dict, else q itself
        key = q["question"] if isinstance(q, dict) and "question" in q else str(q)
        if key not in seen:
            unique_questions.append(q)
            seen.add(key)

    # Limit to requested count
    sentences = unique_questions[:n]

    # If still short, refill by sampling from other categories or re-query
    # UI fallback: generate a readable header+summary for user clarity, not sent to LLM
    if len(sentences) < n:
        import random
        filler_topics = [t["topic"] for t in topics_data if t["topic"] not in [q["topic"] for q in sentences if isinstance(q, dict) and "topic" in q]]
        if DEBUG: st.write(f"DEBUG: Replenishing from topics {filler_topics}")
        while len(sentences) < n:
            t = random.choice(topics_data)
            # Provide a clear header for user-facing UI only; not sent to LLM
            header = f"Question on {t['topic'].capitalize()} ({t['category']})"
            summary = f"{t['question_focus'].strip().rstrip('?')}?"
            sentences.append({
                "topic": t["topic"],
                "question": f"{header}: {summary}",
                "options": [],
                "answer": ""
            })

    return sentences

# ---------- PDF Export Function ----------
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def export_passage_to_pdf(session, passage, questions, words, file_path):
    """
    Export a session's passage, simplified text, questions, and vocabulary to a nicely formatted PDF.
    """
    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        content = [Paragraph(f"<b>Homework Helper - Session {session.id}</b>", styles["Title"]), Spacer(1, 12),
                   Paragraph(f"<b>Topic:</b> {session.topic or 'Untitled'}", styles["Normal"]),
                   Paragraph(f"<b>Date:</b> {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]),
                   Spacer(1, 12), Paragraph("<b>Original Passage:</b>", styles["Heading2"]),
                   Paragraph(passage.original_text or "—", styles["Normal"]), Spacer(1, 12)]

        # Header

        # Original Passage

        # Simplified Version
        if passage.simplified_text:
            content.append(Paragraph("<b>Simplified Version:</b>", styles["Heading2"]))
            content.append(Paragraph(passage.simplified_text, styles["Normal"]))
            content.append(Spacer(1, 12))

        # Questions
        if questions:
            content.append(Paragraph("<b>Comprehension Questions:</b>", styles["Heading2"]))
            for q in questions:
                content.append(Paragraph(f"• {q.question_text}", styles["Normal"]))
            content.append(Spacer(1, 12))

        # Vocabulary Words
        if words:
            content.append(Paragraph("<b>Vocabulary Words:</b>", styles["Heading2"]))
            for w in words:
                content.append(Paragraph(f"<b>{w.word}</b>: {w.explanation}", styles["Normal"]))
            content.append(Spacer(1, 12))

        doc.build(content)
        return f"✅ PDF exported successfully to {file_path}"

    except Exception as e:
        return f"(PDF export error: {e})"

# ---------- PDF Export: Weekly Concepts Summary ----------
def export_concepts_to_pdf(concepts, file_path, title="Weekly Concepts Summary"):
    """
    Export a list of concept records (from the concepts table) into a structured PDF.
    Each record should include subject, topic, type, and date range.
    """
    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        content = []

        # Header
        content.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
        content.append(Spacer(1, 12))
        content.append(Paragraph("This summary includes topics and vocabulary extracted from newsletters or database entries.", styles["Normal"]))
        content.append(Spacer(1, 12))

        # Concept list
        if not concepts:
            content.append(Paragraph("No concepts found for the selected time period.", styles["Normal"]))
        else:
            for c in concepts:
                content.append(Paragraph(f"<b>Subject:</b> {c.subject}", styles["Heading2"]))
                content.append(Paragraph(f"<b>Topic:</b> {c.topic}", styles["Normal"]))
                content.append(Paragraph(f"<b>Type:</b> {c.type or 'N/A'}", styles["Normal"]))
                content.append(Paragraph(f"<b>Date Range:</b> {c.date_start} to {c.date_end or 'N/A'}", styles["Normal"]))
                if getattr(c, 'notes', None):
                    content.append(Paragraph(f"<b>Notes:</b> {c.notes}", styles["Normal"]))
                content.append(Spacer(1, 10))
                content.append(Paragraph("<hr/>", styles["Normal"]))

        doc.build(content)
        return f"✅ Concepts summary PDF exported successfully to {file_path}"

    except Exception as e:
        return f"(Concepts PDF export error: {e})"
