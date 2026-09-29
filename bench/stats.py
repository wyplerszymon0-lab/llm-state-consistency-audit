"""Small-sample statistics for pass rates.

With 5 runs per scenario, 1/5 and 2/5 are often the same model on a different
day, so the leaderboard reports uncertainty instead of bare percentages.
"""

from math import comb, sqrt


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimate of the chance that at least one of k samples passes,
    given c passes in n samples (Chen et al., 2021, "Evaluating Large Language
    Models Trained on Code"). Requires k <= n."""
    if not 0 < k <= n:
        raise ValueError(f"need 0 < k <= n, got k={k}, n={n}")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion.

    Unlike the normal approximation it stays inside [0, 1] and is not
    degenerate at 0 or n successes, which is exactly where small benchmarks live.
    """
    if total == 0:
        return (0.0, 1.0)
    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))
