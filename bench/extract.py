"""Pulls the Python module out of a model's free-text reply."""

import re

FENCE = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(reply: str) -> str | None:
    """Return the code block that defines run(), else the longest block, else None."""
    blocks = [b.strip() for b in FENCE.findall(reply) if b.strip()]
    if not blocks:
        return None
    with_run = [b for b in blocks if re.search(r"^def run\s*\(", b, re.MULTILINE)]
    return max(with_run or blocks, key=len) + "\n"
