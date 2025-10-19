# ==============================
# 📘 Homework Helper - LLM Helpers
# ==============================
# Centralized utilities for handling OpenAI API calls.
# Includes text simplification, question generation, vocabulary explanations,
# and grammar-related sentence/question generation.
from jedi.api.classes import defined_names
from openai import OpenAI
import os, yaml, re, json
from dotenv import load_dotenv
import streamlit as st

# ---------- Setup ----------
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
yaml_path = os.path.join("data", "grammar_hints.yaml")

# ---------- Core LLM Wrapper ----------
def call_llm(prompt, model='gpt-4o-mini', temperature=0.2): #TODO: add subject as parameter (e.g. Math, grammar, etc)
    """Generic LLM call handler."""
    try:
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
        f"Write exactly {n} simple, self-contained sentences (8–14 words each). "
        "Use everyday vocabulary. No dialogue, no quoted speech, no numbers or bullets. "
        "Return ONLY valid JSON: an array of strings, like [\"The cat sat on the warm windowsill.\", ...]. "
        "Do not include any preface or explanation."
    )

    text = call_llm(prompt, temperature=0.4)

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


def generate_grammar_question(sentence, include_answer=False):
    """
    Generates a multiple-choice grammar question for the provided sentence.
    Returns a dict: {"prompt": str, "options": [str, ...]} by default,
    or includes "answer" if include_answer=True.
    The 'answer' is stored internally but not shown by default to avoid leaking the correct answer.
    """
    import json, re
    import random

    prompt = f"""
        You are a 5th-grade ELA tutor. Create ONE multiple-choice grammar question
        about this exact sentence (do not invent a different sentence):
        "{sentence}"
        Choose one of these types at random: (a) part of speech of a specific word,
        (b) simile vs. metaphor if applicable, or (c) subject–verb agreement or punctuation.
        
        Return ONLY valid JSON with keys exactly: "prompt", "options", "answer".
        *** It is absolutely forbidden to reveal, include, or imply the correct answer in the question prompt or in the options (for example, do not say "the answer is", "correct answer", or highlight or hint at the answer in any way). The question and options must be completely neutral and not contain the correct answer or any hint of it. ***
        Example JSON:
        {{
          "prompt": "What part of speech is the word 'jumped' in the sentence?",
          "options": ["noun", "verb", "adjective", "adverb"],
          "answer": "verb"
        }}
        No preface, no explanation, no markdown, no code fences.
        """

    def _sanitize_text(text, answer):
        """Remove explicit answer reveals or hints from prompt/options."""
        import re
        if not answer:
            return text
        # Remove 'answer' if it appears at end, or in 'is correct', 'the answer is', etc.
        # Remove patterns like: ' ... answer', ' ... is correct', ' ... the answer is ...'
        patterns = [
            rf"\b{re.escape(answer)}\b\s*(is\s+correct|is\s+the\s+answer|the\s+answer|correct\s+answer)?\.?$",
            rf"the\s+answer\s+is\s+'?{re.escape(answer)}'?",
            rf"correct\s+answer\s*:?(\s*'?{re.escape(answer)}'?)",
        ]
        # Remove from end of string or after punctuation
        out = text
        for pat in patterns:
            out = re.sub(pat, "", out, flags=re.IGNORECASE)
        return out.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        text = response.choices[0].message.content.strip()
        # Extract strict JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
        obj = json.loads(text)
        # Minimal validation
        if not all(k in obj for k in ("prompt", "options", "answer")):
            raise ValueError("Missing keys")
        if not isinstance(obj.get("options"), list) or not obj.get("options"):
            raise ValueError("Options malformed")
        # Keep the correct answer for internal logic but do not expose it unless requested
        answer = obj.get("answer")
        if not include_answer and "answer" in obj:
            obj.pop("answer")

        # --- Sanitize ONLY the prompt to prevent leaks; leave options intact so the correct choice remains selectable ---
        def scrub_leaks(text, answer):
            if not answer:
                return text
            import re
            patterns = [
                r"\bis correct\b",
                r"\bthe answer is\b",
                r"\bcorrect answer\b",
            ]
            pattern_re = re.compile(rf"\b({'|'.join(patterns)})\b", re.IGNORECASE)
            return re.sub(pattern_re, "[redacted]", text)

        if answer:
            obj["prompt"] = scrub_leaks(obj.get("prompt", ""), answer)

        # --- Normalize and ensure the correct answer is present among options ---
        options = [str(o).strip() for o in obj.get("options", []) if str(o).strip()]

        # Fixed set of distractors we can draw from
        POS_CHOICES = [
            "noun", "verb", "adjective", "adverb", "pronoun",
            "preposition", "conjunction", "interjection", "article", "determiner"
        ]

        # Ensure answer is present (case-insensitive)
        def ci_in(seq, item):
            return any(s.lower() == item.lower() for s in seq)

        if answer and not ci_in(options, answer):
            options.append(answer)

        # Deduplicate while preserving order (case-insensitive)
        seen = set()
        deduped = []
        for o in options:
            key = o.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(o)
        options = deduped

        # Top up with distractors to at least 4 choices
        need = 4 - len(options)
        if need > 0:
            distractors = [p for p in POS_CHOICES if not ci_in(options, p) and (not answer or p.lower() != answer.lower())]
            options.extend(distractors[:max(0, need)])

        # If we somehow still have fewer than 2 options, fall back to a safe default set
        if len(options) < 2:
            options = ["noun", "verb", "adjective", "adverb"]

        # Shuffle options to randomize order
        import random
        random.shuffle(options)
        obj["options"] = options

        return obj
    except Exception as e:
        # Safe fallback
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


def generate_sentences_from_topics(conn=None, n=3):
    """
    Pulls active topics from DB, asks OpenAI for sentences for each.
    """
    from utils.db import get_connection
    if conn is None or not hasattr(conn, "cursor"):
        conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM topics WHERE active = 1;")
    active_topics = [row[0] for row in cursor.fetchall()]

    sentences = []

    for topic in active_topics:
        prompt = f"""
            "You are generating short practice sentences for a 5th grader. "
            f"Write exactly {n} simple, self-contained sentences (8–14 words each) in the context of the {topic}. "
            "Use everyday vocabulary. No dialogue, no quoted speech, no numbers or bullets. "
            "Return ONLY valid JSON: an array of strings, like [\"The cat sat on the warm windowsill.\", ...]. "
            "Do not include any preface or explanation."
        """

        text = call_llm(prompt, temperature=0.4)

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
