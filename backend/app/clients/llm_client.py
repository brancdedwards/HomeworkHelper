"""
llm_client.py
LLM client wrapper supporting both OpenAI and Anthropic.
Handles: model call, retries, JSON extraction, provider switching.
"""

import json
from openai import OpenAI
from anthropic import Anthropic

from backend.app.core.settings import settings

# Initialize clients based on provider
openai_client = None
anthropic_client = None

if settings.LLM_PROVIDER == "openai":
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
elif settings.LLM_PROVIDER == "anthropic":
    anthropic_client = Anthropic(api_key=settings.CLAUDE_API_KEY)


def call_llm(prompt: str):
    """
    Simple LLM call - returns the response text.
    """
    if settings.LLM_PROVIDER == "openai":
        response = openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.MAX_OUTPUT_TOKENS,
            temperature=settings.TEMPERATURE,
        )
        return response.choices[0].message.content

    elif settings.LLM_PROVIDER == "anthropic":
        response = anthropic_client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=settings.MAX_OUTPUT_TOKENS,
            temperature=settings.TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


def call_llm_json(prompt: str, schema: dict, max_retries: int = 3):
    """
    Structured LLM call using JSON schema.
    For Anthropic: We'll request JSON in the prompt and parse it.
    For OpenAI: Use native JSON schema support.
    """
    for attempt in range(max_retries):
        try:
            if settings.LLM_PROVIDER == "openai":
                # OpenAI has native JSON schema support
                response = openai_client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=settings.MAX_OUTPUT_TOKENS,
                    temperature=settings.TEMPERATURE,
                    response_format={
                        "type": "json_schema",
                        "json_schema": schema,
                    }
                )
                raw = response.choices[0].message.content
                return json.loads(raw)

            elif settings.LLM_PROVIDER == "anthropic":
                # Anthropic: Request JSON output in prompt
                json_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON matching the schema. No additional text."

                response = anthropic_client.messages.create(
                    model=settings.LLM_MODEL,
                    max_tokens=settings.MAX_OUTPUT_TOKENS,
                    temperature=settings.TEMPERATURE,
                    messages=[{"role": "user", "content": json_prompt}],
                )

                raw = response.content[0].text
                # Try to extract JSON if wrapped in markdown
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()

                return json.loads(raw)

            else:
                raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")

        except Exception as e:
            print(f"[LLM JSON] Error attempt {attempt+1}: {e}")

    return None