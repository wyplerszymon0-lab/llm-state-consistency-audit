"""Thin clients that send one prompt to a model and return its reply and token usage.

SDKs are imported lazily, so you only need the package for the providers you use.
Credentials come from each SDK's usual environment variables:
ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY. Ollama runs locally.
"""

import json
import os
import urllib.request
from dataclasses import dataclass


class GenerationError(RuntimeError):
    """The provider answered, but not with usable text (e.g. a refusal)."""


@dataclass(frozen=True)
class Reply:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None  # includes reasoning/thinking tokens where the API counts them


def generate_anthropic(model: str, prompt: str) -> Reply:
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
    text = "".join(block.text for block in message.content if block.type == "text")
    return Reply(text, message.usage.input_tokens, message.usage.output_tokens)


def generate_openai(model: str, prompt: str) -> Reply:
    from openai import OpenAI

    response = OpenAI().responses.create(model=model, input=prompt)
    usage = getattr(response, "usage", None)
    return Reply(response.output_text, getattr(usage, "input_tokens", None), getattr(usage, "output_tokens", None))


def generate_google(model: str, prompt: str) -> Reply:
    from google import genai

    response = genai.Client().models.generate_content(model=model, contents=prompt)
    usage = getattr(response, "usage_metadata", None)
    output = None
    if usage is not None and usage.candidates_token_count is not None:
        output = usage.candidates_token_count + (getattr(usage, "thoughts_token_count", None) or 0)
    return Reply(response.text or "", getattr(usage, "prompt_token_count", None), output)


def generate_ollama(model: str, prompt: str) -> Reply:
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    # Ollama's default context (2–4k tokens) silently truncates a long prompt plus
    # the reply; 16k leaves room for reasoning models that think before they code.
    body = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "options": {"num_ctx": 16384}}
    ).encode()
    request = urllib.request.Request(
        f"{host}/api/generate", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=1800) as response:
        data = json.loads(response.read())
    return Reply(data["response"], data.get("prompt_eval_count"), data.get("eval_count"))


PROVIDERS = {
    "anthropic": generate_anthropic,
    "openai": generate_openai,
    "google": generate_google,
    "ollama": generate_ollama,
}


def generate(spec: str, prompt: str) -> Reply:
    """`spec` is "provider:model", e.g. "anthropic:claude-opus-5"."""
    provider, _, model = spec.partition(":")
    if provider not in PROVIDERS or not model:
        raise ValueError(f"expected provider:model with provider in {sorted(PROVIDERS)}, got {spec!r}")
    return PROVIDERS[provider](model, prompt)
