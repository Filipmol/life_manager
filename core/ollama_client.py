"""
Ollama local-LLM client.

Talks to Ollama's HTTP API at localhost:11434.
Supports streaming for real-time token display and a simple
blocking helper for one-shot generation.

Falls back gracefully when Ollama is unreachable.
"""

import json
import urllib.request
import urllib.error
from typing import Generator, Optional

OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"  # works with any model the user has pulled


def is_ollama_running() -> bool:
    """Return True if Ollama responds on its default port."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def list_models() -> list[str]:
    """Return model names available in the local Ollama installation."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate_stream(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: str = "",
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """
    Yield tokens one-by-one as Ollama generates them (streaming).
    The caller can update the UI after every chunk.
    """
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": True,
        "options": {"temperature": temperature},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            buffer = b""
            while True:
                chunk = resp.read(1)
                if not chunk:
                    break
                buffer += chunk
                if chunk == b"\n":
                    try:
                        obj = json.loads(buffer.decode())
                        token = obj.get("response", "")
                        if token:
                            yield token
                        if obj.get("done", False):
                            return
                    except json.JSONDecodeError:
                        pass
                    buffer = b""
    except urllib.error.URLError:
        yield "[Error: Cannot reach Ollama at localhost:11434. Is it running?]"
    except Exception as exc:
        yield f"[Error: {exc}]"


def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: str = "",
    temperature: float = 0.7,
) -> str:
    """Blocking one-shot generation — collects the full response."""
    parts: list[str] = []
    for token in generate_stream(prompt, model, system, temperature):
        parts.append(token)
    return "".join(parts)


# ─── Domain prompts ─────────────────────────────────────────────────

RECIPE_SYSTEM = (
    "You are a professional chef and nutritionist. "
    "When given a list of ingredients, create a detailed, easy-to-follow recipe. "
    "Include: recipe name, serving size, preparation time, cooking time, "
    "step-by-step instructions, and basic nutritional notes. "
    "Be creative but practical. Use ONLY the ingredients provided "
    "(plus common pantry staples like salt, pepper, oil, water)."
)

FITNESS_SYSTEM = (
    "You are an expert personal trainer and running coach. "
    "When given a fitness goal, create a specific, actionable workout plan. "
    "Include: warm-up, main workout with sets/reps/distances/times, cool-down, "
    "and rest recommendations. If it's a running goal, include pace targets. "
    "If it's a gym goal, include specific exercises with sets and reps. "
    "Adapt to all fitness levels and always include safety tips."
)


def generate_recipe(ingredients: str, model: str = DEFAULT_MODEL) -> Generator[str, None, None]:
    prompt = (
        f"I have these ingredients available:\n{ingredients}\n\n"
        "Please create a delicious recipe I can make with them."
    )
    yield from generate_stream(prompt, model=model, system=RECIPE_SYSTEM)


def generate_workout(goal: str, model: str = DEFAULT_MODEL) -> Generator[str, None, None]:
    prompt = (
        f"My fitness goal for today:\n{goal}\n\n"
        "Please create a detailed workout plan for me."
    )
    yield from generate_stream(prompt, model=model, system=FITNESS_SYSTEM)
