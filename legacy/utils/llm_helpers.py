# ==============================
# 📘 Homework Helper - LLM Helpers
# ==============================
# Centralized utilities for handling OpenAI API calls.
# Includes text simplification, question generation, vocabulary explanations,
# and grammar-related sentence/question generation.

from typing import Any
from config.logger import log
from openai import OpenAI
import os, yaml, re, json
from dotenv import load_dotenv
import streamlit as st
from legacy.utils.concept_map_loader import load_concept_map, get_question_focus

# ---------- Setup ----------
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
yaml_path = os.path.join("data", "grammar_combined.yaml")
DEBUG = False  # Enable debug logs for detailed tracing


# ---------- Unified Prompt Builder and Tutor Personas ----------
from functools import lru_cache

PROMPT_PERSONAS = {
    "grammar_mechanics": "You are a 5th-grade grammar tutor who helps students master sentence correction and structure.",
    "writing_quality": "You are a 5th-grade writing tutor who teaches organization, transitions, and clarity.",
    "vocabulary": "You are a 5th-grade vocabulary tutor who focuses on word meaning and usage.",
    "literary_devices": "You are a 5th-grade literature tutor who helps students recognize figurative language.",
    "punctuation": "You are a 5th-grade punctuation tutor helping students choose correct marks in sentences.",
    "sentence_structure": "You are a 5th-grade language tutor who explains how clauses form sentences.",
}

@lru_cache(maxsize=64)
def build_prompt(persona, topic, category, question_focus, example, num_per_topic):
    return f"""
{persona}

You are generating {num_per_topic} *multiple-choice* grammar questions about the topic **{topic}**, 
which belongs to the category **{category}**.

If you see curly braces like {{word}} or {{sentence}}, 
treat them as variable placeholders — they represent example content. 
Replace them naturally with simple, age-appropriate examples (e.g., "happy", "run", or "The dog barked."). 
Do NOT display the braces or variable names in the question or options. 
Do NOT explain that you replaced them.

Each question must follow this JSON structure:

{{
  "topic": "{topic}",
  "category": "{category}",
  "question": "A single clear question that tests understanding of {topic}. Do NOT mention topic or category names.",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "The correct option text."
}}

Rules:
1. Only generate multiple-choice questions — no fill-in-the-blank, true/false, or open-ended items.
2. Never show curly braces, metadata, or variable names in the output.
3. Stay strictly within {category} concepts. Use age-appropriate vocabulary (grades 4–7).
4. Keep questions short, natural, and engaging.
5. Include one guiding example: **{example}**
6. Return ONLY valid JSON as an array of objects. No commentary, markdown, or explanations.
"""

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

    category_label = category.replace("_", " ").strip().title() if category else "English"

    prompt = f"""
        You are a {n}th-grade {category_label} tutor.
        
        Your task:
        - Write one multiple-choice question that teaches a 5th grader a concept related to the following text.
        - Keep it simple, natural, and age-appropriate.
        - Do not ask about the text directly (avoid “In the sentence above…”).
        - Stay within {category_label.lower()} concepts.
        - Each question must have exactly 4 options and 1 correct answer.
        
        Return ONLY valid JSON with keys "prompt", "options", and "answer".
        
        Example text:
        "{sentence}"
        """
    # Use unified prompt builder
    persona = PROMPT_PERSONAS.get(
        category,
        f"You are a 5th-grade {category.replace('_', ' ')} tutor."
    )

    prompt = build_prompt(
        persona=persona,
        topic=cleaned_sentence,
        category=category,
        question_focus=f"Grammar question generation from a sample sentence.",
        example=None,
        num_per_topic=1
    )
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
            return re.sub(
                r"(?i)\b(the answer is|answer:?|correct answer:?)(.*?)($|\.)",
                "",
                txt
            ).strip()
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
    """Retrieve grammar hint dynamically from grammar_combined.yaml."""
    # topic = topic.lower().strip()
    st.write(f"DEBUG: (from llm helpers) topic: {topic}")
    # yaml_path = os.path.join("data", "grammar_combined.yaml")
    if not os.path.exists(yaml_path):
        st.write("DEBUG: yaml_path not detected")
        return "Remember, (yaml_path not detected) think about how the word is used in the sentence."

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            grammar_data = yaml.safe_load(f)
            # st.write(f"DEBUG: grammar_data: {grammar_data}")
            if not isinstance(grammar_data, dict):
                st.write("DEBUG: Invalid grammar_combined.yaml structure.", grammar_data)
                return "Remember,(found yaml) think about how the word is used in the sentence."
    except Exception as e:
        st.write("DEBUG: Failed to read or parse YAML", str(e))
        return "Remember, (exception) think about how the word is used in the sentence."

    if topic in grammar_data:
        data = grammar_data[topic]
        st.write(f"DEBUG: data: {data}")
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
        # on 11/3 this is being returned... why?
        return f"Remember, think about how the word is used in the sentence for {topic}."

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
    Returns a list of distinct categories from topics that have ACTIVE topics.
    Used by the UI to populate the category dropdown.
    """
    from legacy.utils.db import get_connection

    if conn is None or not hasattr(conn, "cursor"):
        conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        select distinct
            t.category
            
            from topics t
            where t.active = 1
                and t.category is not null
                and TRIM(t.category) != ''
            order by lower(t.category)

    """)
    rows = cur.fetchall()
    return [r[0] for r in rows] if rows else []

def generate_sentences_from_topics(conn=None, n=3, category=None):
    """
    Pulls active topics from DB, detects their categories using the concept map loader,
    and asks OpenAI for sentences for each, possibly customizing prompts per category.
    """
    # --- Integration point: load concept map for category detection ---
    from legacy.utils.db import get_connection
    if conn is None or not hasattr(conn, "cursor"):
        conn = get_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("""
                       SELECT t.name FROM topics t 
                       WHERE LOWER(t.category) = LOWER(?)
                         AND t.active = 1;
                       """, (category,))
    else:
        cursor.execute("""
                        SELECT t.name
                        FROM topics t
                           WHERE t.active = 1;
                       """)
    active_topics = [row[0] for row in cursor.fetchall()]
    # if DEBUG: st.write(f"DEBUG: Active topics: {active_topics}")

    # Immediately after fetching active_topics: apply new selection logic
    available_count = len(active_topics)

    if category:
        selected_topics = active_topics[:n]
        if available_count < n:
            st.info(f"Only {available_count} questions available for category '{category}'. Showing all available.")
    else:
        import random
        if available_count < n:
            filler = random.choices(active_topics, k=n - available_count)
            selected_topics = active_topics + filler
        else:
            selected_topics = random.sample(active_topics, n)

    # Load concept map for category detection
    concept_map = load_concept_map()
    if DEBUG:
        st.write(f"DEBUG: Loaded concept map: {concept_map}")
        log.debug(f"Loaded concept map: {concept_map}")

    # Compute how many questions per topic
    if len(selected_topics) == 0:
        return []
    num_per_topic = max(1, n // len(selected_topics))
    if DEBUG:
        st.write(f"DEBUG: Number of questions per topic: {num_per_topic}")
        log.debug(f"Number of questions per topic: {num_per_topic}")

    if DEBUG:
        st.write(f"DEBUG: Selected topics: {selected_topics}")
        log.debug(f"Selected topics: {selected_topics}")
    sentences = []
    seen_questions = set()

    from legacy.utils.concept_map_db import get_concept
    topics_data = []
    for topic in selected_topics:
        if DEBUG:
            st.write(f"DEBUG from llm_helpers (b4 category/question_focus lookup): Topic: {topic}")
            log.debug(f"From llm_helpers (b4 category/question_focus lookup): Topic: {topic}")
        # Try to get from DB first
        concept_record = get_concept(topic, subject="grammar")
        if concept_record:
            t_category = concept_record.get("category") if isinstance(concept_record, dict) else getattr(concept_record, "category", None)
            question_focus = concept_record.get("question_focus") if isinstance(concept_record, dict) else getattr(concept_record, "question_focus", None)
            if DEBUG:
                st.write(
                    f"DEBUG Topic: {topic} - used DB record for category/question_focus. Category: {t_category}, Question Focus: {question_focus}")
                log.debug(
                    f"Topic: {topic} - used DB record for category/question_focus. Category: {t_category}, Question Focus: {question_focus}")
        else:
            # t_category = detect_category_for_topic(topic, subject="grammar")
            question_focus = get_question_focus(topic, subject="grammar")
            if DEBUG:
                st.write(
                    f"DEBUG Topic: {topic} - used fallback detect_category/get_question_focus. Category: {t_category}, Question Focus: {question_focus}")
                log.debug(
                    f"Topic: {topic} - used fallback detect_category/get_question_focus. Category: {t_category}, Question Focus: {question_focus}")
        if question_focus:
            topics_data.append({
                "topic": topic,
                "category": t_category,
                "question_focus": question_focus,
            })
            st.session_state["last_category"] = t_category
            if DEBUG:
                st.write(f"DEBUG: Cached last_category (llm helpers) in session: {t_category}")
                log.debug(f"Cached last_category (llm helpers) in session: {t_category}")

    # json and re are already imported at the top of the file; redundant here.
    # Helper function for parsing and cleaning
    def parse_llm_json_list(text):
        text = text.strip()
        text = re.sub(r"(?i)(^sure|^okay|^here|^let.?s|^of course).*", "", text)
        text = re.sub(r"(?i)(question on|topic:|category:)\s*[A-Za-z_ ]+[:\-]*", "", text)
        text = re.sub(r"(?i)please see.*guidance.*", "", text)
        # Attempt to extract JSON
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            text = match.group(0)
        # Safety: don't attempt to parse if empty or truncated
        if not text or len(text.strip()) < 5:
            return []
        try:
            items = json.loads(text)
            if not isinstance(items, list):
                return []
            return items
        except Exception:
            # Retry sanitize pass
            text = re.sub(r"```(?:json)?|```", "", text)
            text = re.sub(r"(?i)example json.*?\[", "[", text)
            text = text.strip()
            if not text or len(text.strip()) < 5:
                return []
            try:
                items = json.loads(text)
                if not isinstance(items, list):
                    return []
                return items
            except Exception:
                return []

    # For each topic, request multiple distinct questions
    for t in topics_data:
        if DEBUG:
            st.write(
                f"DEBUG: Generating {num_per_topic} questions for topic '{t['topic']}' in category '{t['category']}'")
            log.debug(f"Generating {num_per_topic} questions for topic '{t['topic']}' in category '{t['category']}'")
        # Try to get prompt template and example
        prompt_template = None
        example = None
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

        # --- Normalize topic and clean up prompt_template if present ---
        topic_clean = re.sub(r'[_\-]+', ' ', t['topic']).strip().title()
        # Remove literal "in {topic}" from template if present
        if prompt_template:
            # Remove "in {topic}" or "in [topic]" (case-insensitive, with or without quotes)
            prompt_template = re.sub(
                r'in\s*\{?\s*topic\s*\}?\s*', 'in a sentence ', prompt_template, flags=re.IGNORECASE
            )
            # Remove doubled spaces
            prompt_template = re.sub(r'\s{2,}', ' ', prompt_template)
        # --- Build new composite prompt, category-aware and concise ---
        if prompt_template:
            prompt_inner = prompt_template.format(
                topic=topic_clean,
                category=t['category'],
                question_focus=t['question_focus']
            )
        else:
            prompt_inner = f"Generate grammar questions about {topic_clean}."

        category_value = t.get('category') or 'general'
        category_label = category_value.replace('_', ' ').strip().title()

        # --- LEGACY PROMPT (for rollback or debugging) ---
        # base_prompt = f"""
# You are a {category_label} tutor.
#
# Your task:
# - Generate {num_per_topic} multiple-choice questions for 5th graders.
# - Focus on the topic: {topic_clean} ({t['category']}).
# - Use the following instructional context: "{prompt_inner}".
# - Include one example for guidance: {example or 'None provided'}.
# - Keep each question age-appropriate and clear.
# - Each question must have exactly 4 options and one correct answer.
# - Return ONLY valid JSON as an array of question objects with keys "topic", "question", "options", and "answer".
# - No explanations or extra text.
# """
        persona = PROMPT_PERSONAS.get(t['category'], f"You are a 5th-grade {t['category'].replace('_', ' ')} tutor.")
        # This is where the
        prompt = build_prompt(
            persona=persona,
            topic=topic_clean,
            category=t['category'],
            question_focus=t['question_focus'],
            example=example,
            num_per_topic=num_per_topic
        )
        # prompt = base_prompt.strip()
        if DEBUG:
            st.write(f"🧠 DEBUG Topic: {t['topic']}")
            st.write(f"🧩 DEBUG Category: {t['category']}")
            st.write(f"🧾 DEBUG Question Focus: {t['question_focus']}")
            st.write(f"📤 DEBUG Prompt to LLM (first 500 chars):\n{prompt[:500]}")
        text = call_llm(prompt)
        items = parse_llm_json_list(text)
        # Fallback: try again if empty
        if not items:
            text2 = call_llm(prompt)
            items = parse_llm_json_list(text2)

        # Garbage filter function
        def is_garbage_question(q: str):
            q_clean = q.strip().lower()
            # Meta-patterns
            meta_patterns = [
                r"which of the following sentences is correct",
                r"choose the correct sentence",
                r"what part of speech is",
                r"which sentence is written correctly",
            ]
            for pat in meta_patterns:
                if re.search(pat, q_clean):
                    return True
            # Reject if too short (< 6 words)
            if len(q_clean.split()) < 6:
                return True
            # Reject if contains "following sentences"
            if "following sentences" in q_clean:
                return True
            return False

        # Post-process and deduplicate
        for item in items:
            # Validate structure
            if not isinstance(item, dict) or not all(k in item for k in ("question", "options", "answer")):
                continue
            # Clean any leftover phrasing from the question
            item["question"] = re.sub(
                r"(?i)(question on|topic:|category:)\s*[A-Za-z_ ]+[:\-]*", "", item["question"]
            ).strip()
            # Garbage filter
            if is_garbage_question(item["question"]):
                if DEBUG:
                    st.write(f"DEBUG: Garbage question filtered out: {item['question']}")
                continue
            # Deduplication by question string
            q_key = item["question"].strip()
            if q_key in seen_questions:
                if DEBUG:
                    st.write(f"DEBUG: Duplicate question skipped for topic '{t['topic']}': {item['question']}")
                continue
            seen_questions.add(q_key)
            sentences.append(item)
            if len(sentences) >= n:
                break
        if len(sentences) >= n:
            break

    # Debug summary printout after the for loop and before deduplication
    if DEBUG:
        st.write(f"DEBUG: Generated {num_per_topic} questions each for {len(selected_topics)} topics = {len(selected_topics) * num_per_topic} total (before filtering)")

    # --- Final guardrail: drop malformed or duplicate entries ---
    sentences = [
        s for s in sentences
        if isinstance(s, dict)
        and s.get("question")
        and isinstance(s.get("options"), list)
        and len(s["options"]) >= 2
    ]

    # Limit to requested count
    sentences = sentences[:n]

    # If still short, skip filler generation to preserve quality
    if len(sentences) < n and topics_data:
        if DEBUG:
            st.write(f"⚠️ DEBUG: Only {len(sentences)} valid questions generated out of {n} requested; skipping filler placeholders to maintain quality.")
    # If still short, warn user and show available questions
    if len(sentences) < n and topics_data:
        msg = f"Requested {n} questions, but only {len(sentences)} unique concepts were available. Showing all available questions."
        st.warning(msg)
        if DEBUG:
            st.write(f"⚠️ DEBUG: {msg}")
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
