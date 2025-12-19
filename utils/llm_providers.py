"""LLM Provider utilities for Groq."""

import os
import re
import json
import time
import requests

# Reuse a single HTTP session for all outbound requests
SESSION = requests.Session()


def groq_chat(api_key: str, messages: list, model: str = None, temperature: float = 0.2, max_tokens: int = 600) -> str:
    """Minimal Groq chat-completions helper returning assistant content as text.

    Token-optimized: enforce a single model (llama-3.1-8b-instant) with no fallbacks.
    """
    if not api_key:
        raise RuntimeError("Groq API key missing")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    model = (model or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant")
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    # Simple retry/backoff for rate limits and transient errors
    attempts = 0
    last_err = None
    while attempts < 2:
        resp = SESSION.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 429:
            # Parse suggested wait from message, else sleep a small backoff
            wait_s = 2.5
            try:
                msg = resp.text or ""
                m = re.search(r"try again in\s([\d\.]+)s", msg)
                if m:
                    wait_s = min(max(float(m.group(1)) * 1.2, 2.0), 8.0)
            except Exception:
                pass
            time.sleep(wait_s)
            attempts += 1
            last_err = resp
            continue
        if 500 <= resp.status_code < 600:
            # transient server error
            time.sleep(1.5 * (attempts + 1))
            attempts += 1
            last_err = resp
            continue
        if resp.status_code >= 400:
            raise requests.HTTPError(f"{resp.status_code} {resp.reason}: {resp.text}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            return json.dumps(data)
    # if we exhausted retries
    if last_err is not None:
        raise requests.HTTPError(f"{last_err.status_code} {last_err.reason}: {last_err.text}")
    raise RuntimeError("Groq request failed after retries")


# Ollama support removed per project configuration.
