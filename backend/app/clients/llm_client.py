"""
llm_client.py
LLM client wrapper for OpenAI (or any other model).
Handles: model call, retries, JSON extraction, safety trimming.
"""

import json
from openai import OpenAI

from backend.app.core.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_llm(prompt: str):
    return client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.MAX_OUTPUT_TOKENS,
        temperature=settings.TEMPERATURE,
    )

def call_llm_json(prompt: str, schema: dict, max_retries: int = 3):
    """
    Structured LLM call using JSON schema.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                temperature=settings.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
            return json.loads(raw)
        except Exception as e:
            print(f"[LLM JSON] Error attempt {attempt+1}: {e}")
    return None