"""List prices used to put a dollar figure on each run.

USD per million tokens (input, output), Anthropic first-party API list prices as
of 2026-06. Models not listed get no cost rather than a guessed one; local
Ollama models cost nothing to call. Add entries here with their date and source.
"""

PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "anthropic:claude-fable-5-1": (10.00, 50.00),
    "anthropic:claude-opus-5-5": (4.00, 20.00),
    "anthropic:claude-opus-5": (5.00, 25.00),
    "anthropic:claude-sonnet-5": (2.00, 10.00),
    "anthropic:claude-haiku-4-5": (1.00, 5.00),
}


def cost_usd(spec: str, input_tokens: int | None, output_tokens: int | None) -> float | None:
    """Dollar cost of one call, 0 for local models, None when unknown."""
    if spec.startswith("ollama:"):
        return 0.0
    price = PRICES_PER_MTOK.get(spec)
    if price is None or input_tokens is None or output_tokens is None:
        return None
    return (input_tokens * price[0] + output_tokens * price[1]) / 1_000_000
