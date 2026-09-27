"""
JARVIS AI layer.

Priority:
1. Ollama local AI - private and does not need an API key.
2. OpenAI API - used only when OPENAI_API_KEY is configured.
3. Helpful offline fallback when neither is available.

Environment variables:
    JARVIS_AI=auto | ollama | openai | offline
    OLLAMA_MODEL=llama3.2:3b
    OLLAMA_URL=http://127.0.0.1:11434
    OPENAI_API_KEY=your_key
    OPENAI_MODEL=gpt-5.6
"""

import json
import os
import urllib.error
import urllib.request


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")
AI_MODE = os.getenv("JARVIS_AI", "auto").lower()

SYSTEM_PROMPT = (
    "You are JARVIS, a helpful personal desktop assistant. "
    "Answer clearly and briefly because your answer will be spoken aloud. "
    "Do not claim to have performed a computer action unless the program "
    "actually performed it."
)

_history = []


def _remember(user_text: str, assistant_text: str) -> None:
    _history.append({"role": "user", "content": user_text})
    _history.append({"role": "assistant", "content": assistant_text})
    # Keep memory small so local models remain fast.
    del _history[:-10]


def _ollama_available() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def _ask_ollama(prompt: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_history)
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    answer = data.get("message", {}).get("content", "").strip()
    if not answer:
        raise RuntimeError("Ollama returned an empty answer.")
    return answer


def _ask_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The openai package is not installed. Run: pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(_history)
    messages.append({"role": "user", "content": prompt})

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=messages,
    )
    answer = response.output_text.strip()
    if not answer:
        raise RuntimeError("OpenAI returned an empty answer.")
    return answer


def ai_status() -> str:
    """Return a spoken-friendly description of the configured AI."""
    if AI_MODE == "offline":
        return "AI is set to offline mode."

    if AI_MODE in {"auto", "ollama"} and _ollama_available():
        return f"Local Ollama AI is ready with model {OLLAMA_MODEL}."

    if AI_MODE in {"auto", "openai"} and os.getenv("OPENAI_API_KEY"):
        return f"OpenAI AI is configured with model {OPENAI_MODEL}."

    return (
        "No AI model is currently available. Install Ollama and pull a model, "
        "or configure an OpenAI API key. Basic JARVIS commands still work."
    )


def _offline_answer(prompt: str) -> str:
    text = prompt.lower().strip()

    if "hello" in text or "hi jarvis" in text:
        return "Hello. I am ready."

    if "your name" in text:
        return "My name is JARVIS."

    if "what can you do" in text:
        return (
            "I can control supported Windows actions, calculate maths, "
            "search the web, and use a local or cloud AI model."
        )

    return (
        "I can handle that when an AI model is connected. "
        "For private AI, install Ollama and set the model in the README."
    )


def ask_ai(prompt: str) -> str:
    """Answer with the selected AI backend and remember the conversation."""
    prompt = prompt.strip()
    if not prompt:
        return "Please give me something to work with."

    answer = None

    if AI_MODE in {"auto", "ollama"}:
        try:
            if _ollama_available():
                answer = _ask_ollama(prompt)
        except (urllib.error.URLError, TimeoutError, RuntimeError, OSError, ValueError):
            answer = None

    if answer is None and AI_MODE in {"auto", "openai"}:
        if os.getenv("OPENAI_API_KEY"):
            try:
                answer = _ask_openai(prompt)
            except Exception:
                answer = None

    if answer is None:
        answer = _offline_answer(prompt)

    _remember(prompt, answer)
    return answer
