"""
hint_service.py

Provides hint generation for grammar questions.
A hint explains why the *wrong answer* is incorrect, or reinforces
the definition/example of the topic if the wrong answer cannot be analyzed.
"""

from backend.app.services.topic_service import get_topic_data
from backend.app.core.logging_config import log_prompt_and_response
from backend.app.utils.normalization import normalize_answer

def get_hint_for_topic(topic: str, wrong_answer: str) -> str:
    """
    Produce a simple, consistent hint for Grammar MCQs.

    Priority:
    1. If topic metadata exists (definition or examples), base hint on that.
    2. Otherwise fallback to a generic structured hint.
    """

    topic = normalize_answer(topic)
    wrong_answer = normalize_answer(wrong_answer)

    topic_data = get_topic_data(topic)
    if topic_data:
        definition = topic_data.get("definition")
        examples = topic_data.get("examples")

        # Normalize examples if needed
        if isinstance(examples, list):
            examples = "; ".join(examples)

        if definition:
            log_prompt_and_response("hint_service_hit", f"Topic={topic}, wrong={wrong_answer}")
            return (
                f"Not quite. Remember: {definition}. "
                f"Your choice ('{wrong_answer}') doesn’t match this rule."
            )

        if examples:
            log_prompt_and_response("hint_service_example", f"Topic={topic}, wrong={wrong_answer}")
            return (
                f"Not quite. Here are examples that follow the topic: {examples}. "
                f"Compare them to your choice ('{wrong_answer}')."
            )

    # Fallback — no topic metadata found
    log_prompt_and_response("hint_service_fallback", f"Topic={topic}, wrong={wrong_answer}")
    return (
        f"That’s not quite right. Think about what the topic “{topic}” describes "
        f"and compare it with your choice ('{wrong_answer}')."
        " Try reviewing the definition and comparing each option carefully."
    )
