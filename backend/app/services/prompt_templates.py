"""
prompt_templates.py

Provides style templates for grammar question generation.
These templates give the LLM consistent tone and structure expectations.
"""

def get_style_template(style: str) -> str:
    """
    Return a block of text describing stylistic constraints
    for the LLM when generating questions.
    """

    style = (style or "").lower().strip()

    if style == "default":
        return (
            "- Use clear, simple language.\n"
            "- Keep sentences short and direct.\n"
            "- Avoid unnecessary complexity.\n"
            "- Suitable for elementary students."
        )

    if style == "challenge":
        return (
            "- Increase complexity slightly.\n"
            "- Include mild distractors in answer choices.\n"
            "- Encourage deeper reasoning without being confusing.\n"
            "- Still appropriate for upper‑elementary level."
        )

    if style == "socratic":
        return (
            "- Phrase questions in a guiding, reflective tone.\n"
            "- Encourage students to think rather than memorize.\n"
            "- Avoid giving clues in the question wording.\n"
            "- Keep the structure engaging but simple."
        )

    if style == "direct":
        return (
            "- Be concise and to the point.\n"
            "- Use minimal extra wording.\n"
            "- Focus sharply on the target skill.\n"
            "- Avoid any narrative or contextual fluff."
        )

    if style == "friendly":
        return (
            "- Use warm, encouraging language.\n"
            "- Maintain simplicity and positivity.\n"
            "- Avoid sounding overly formal.\n"
            "- Keep instructions light and welcoming."
        )

    # Fallback default style
    return (
        "- Use clear, simple wording.\n"
        "- Keep sentences short.\n"
        "- Avoid complex grammar.\n"
        "- Appropriate for elementary students."
    )
