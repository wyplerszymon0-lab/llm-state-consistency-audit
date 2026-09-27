"""Thin clients that send one prompt to a model and return its text reply.

SDKs are imported lazily, so you only need the package for the providers you use.
Credentials come from each SDK's usual environment variables:
ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY. Ollama runs locally.
"""

import json
import os
import urllib.request


class GenerationError(RuntimeError):
    """The provider answered, but not with usable text (e.g. a refusal)."""


def generate_anthropic(model: str, prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    # No server-side model fallback on purpose: an answer from a different model
    # would be scored under this model's name. A refusal counts as a failed run.
    with client.messages.stream(
        model=model,
        max_tokens=64000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        message = stream.get_final_message()
    if message.stop_reason == "refusal":
        raise GenerationError("model refused the request")
    return "".join(block.text for block in message.content if block.type == "text")


def generate_openai(model: str, prompt: str) -> str:
    from openai import OpenAI

    response = OpenAI().responses.create(model=model, input=prompt)
    return response.output_text


def generate_google(model: str, prompt: str) -> str:
    from google import genai

    response = genai.Client().models.generate_content(model=model, contents=prompt)
    return response.text or ""


def generate_ollama(model: str, prompt: str) -> str:
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    # Ollama's default context (2–4k tokens) silently truncates a long prompt plus
    # a full program in reply; 8k fits every scenario with room to spare.
    body = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "options": {"num_ctx": 8192}}
    ).encode()
    request = urllib.request.Request(
        f"{host}/api/generate", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.loads(response.read())["response"]


PROVIDERS = {
    "anthropic": generate_anthropic,
    "openai": generate_openai,
    "google": generate_google,
    "ollama": generate_ollama,
}


def generate(spec: str, prompt: str) -> str:
    """`spec` is "provider:model", e.g. "anthropic:claude-opus-5"."""
    provider, _, model = spec.partition(":")
    if provider not in PROVIDERS or not model:
        raise ValueError(f"expected provider:model with provider in {sorted(PROVIDERS)}, got {spec!r}")
    return PROVIDERS[provider](model, prompt)
