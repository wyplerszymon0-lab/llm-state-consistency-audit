"""Accuracy against time per run, as a self-contained SVG (no plotting library).

One point per model that recorded its latency: x = median seconds per run (log
scale), y = pass rate with its 95 % Wilson interval as a vertical bar. Colours
follow the leaderboard page (light and dark via prefers-color-scheme), each point
carries a <title> tooltip, and the model name is written next to it.
"""

from __future__ import annotations

import math
from html import escape
from statistics import median

from bench.scoring import ModelSummary

WIDTH, HEIGHT = 760, 420
LEFT, RIGHT, TOP, BOTTOM = 64, 150, 28, 52  # room for the y labels, point labels and x axis
TICKS_S = (10, 30, 60, 180, 600, 1800)  # round times, labelled in s or min

STYLE = """
  .surface { fill: #fcfcfb; }
  .grid { stroke: #e1e0d9; stroke-width: 1; }
  .axis-text { fill: #52514e; font: 12px system-ui, -apple-system, "Segoe UI", sans-serif; }
  .label { fill: #0b0b0b; font: 12px system-ui, -apple-system, "Segoe UI", sans-serif; }
  .interval { stroke: #2a78d6; stroke-width: 2; stroke-linecap: round; opacity: 0.45; }
  .dot { fill: #2a78d6; stroke: #fcfcfb; stroke-width: 2; }
  @media (prefers-color-scheme: dark) {
    .surface { fill: #1a1a19; }
    .grid { stroke: #2c2c2a; }
    .axis-text { fill: #c3c2b7; }
    .label { fill: #f0efec; }
    .interval { stroke: #3987e5; }
    .dot { fill: #3987e5; stroke: #1a1a19; }
  }
"""


def points(summaries: list[ModelSummary]) -> list[dict]:
    """Models with recorded latency: name, median seconds, pass rate and its interval."""
    out = []
    for s in summaries:
        latencies = [r.usage["latency_s"] for rs in s.runs.values() for r in rs if r.usage]
        if not latencies:
            continue
        lo, hi = s.pass_rate_interval()
        out.append(
            {
                "name": s.display_name,
                "seconds": median(latencies),
                "rate": s.pass_rate(),
                "lo": lo,
                "hi": hi,
                "runs": s.total(),
                "passes": s.passes(),
            }
        )
    return out


def spread_labels(ys: list[float], min_gap: float, top: float, bottom: float) -> list[float]:
    """Move label baselines apart (keeping their order) so none are closer than min_gap."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    placed = [0.0] * len(ys)
    last = top - min_gap
    for i in order:
        placed[i] = max(ys[i], last + min_gap)
        last = placed[i]
    overflow = last - bottom
    if overflow > 0:  # pushed past the bottom: shift the whole stack up
        for i in order:
            placed[i] -= overflow
    return placed


def accuracy_vs_time_svg(summaries: list[ModelSummary]) -> str | None:
    pts = points(summaries)
    if not pts:
        return None
    plot_w, plot_h = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM
    lo_s = min(min(p["seconds"] for p in pts), TICKS_S[0])
    hi_s = max(max(p["seconds"] for p in pts), 100)
    xmin, xmax = math.log10(lo_s) - 0.1, math.log10(hi_s) + 0.1

    def x(seconds: float) -> float:
        return LEFT + (math.log10(seconds) - xmin) / (xmax - xmin) * plot_w

    def y(rate: float) -> float:
        return TOP + (1 - rate) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" '
        f'role="img" aria-labelledby="avt-title avt-desc">',
        '<title id="avt-title">Pass rate against median time per run</title>',
        '<desc id="avt-desc">One point per model: x is the median seconds per run on a log scale, '
        "y is the pass rate, the vertical bar its 95 % Wilson interval.</desc>",
        f"<style>{STYLE}</style>",
        f'<rect class="surface" width="{WIDTH}" height="{HEIGHT}" rx="6"/>',
    ]
    for rate in (0, 0.25, 0.5, 0.75, 1.0):
        yy = y(rate)
        parts.append(f'<line class="grid" x1="{LEFT}" x2="{LEFT + plot_w}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
        parts.append(f'<text class="axis-text" x="{LEFT - 8}" y="{yy + 4:.1f}" text-anchor="end">{rate:.0%}</text>')
    for t in TICKS_S:
        if lo_s / 1.3 <= t <= hi_s * 1.3:
            xx = x(t)
            parts.append(f'<line class="grid" x1="{xx:.1f}" x2="{xx:.1f}" y1="{TOP}" y2="{TOP + plot_h}"/>')
            label = f"{t // 60} min" if t >= 60 else f"{t} s"
            parts.append(
                f'<text class="axis-text" x="{xx:.1f}" y="{TOP + plot_h + 18}" text-anchor="middle">{label}</text>'
            )
    parts.append(
        f'<text class="axis-text" x="{LEFT + plot_w / 2:.1f}" y="{HEIGHT - 10}" text-anchor="middle">'
        "Median time per run (log scale) — faster to the left</text>"
    )
    parts.append(
        f'<text class="axis-text" transform="translate(16 {TOP + plot_h / 2:.1f}) rotate(-90)" '
        'text-anchor="middle">Pass rate, 95 % interval</text>'
    )

    label_ys = spread_labels([y(p["rate"]) + 4 for p in pts], 15, TOP + 10, TOP + plot_h)
    for p, ly in zip(pts, label_ys, strict=True):
        px, py = x(p["seconds"]), y(p["rate"])
        tip = (
            f"{p['name']}: {p['passes']}/{p['runs']} run{'s' if p['runs'] != 1 else ''} passed ({p['rate']:.0%}, 95 % interval "
            f"{p['lo']:.0%}–{p['hi']:.0%}), median {p['seconds']:.0f} s per run"
        )
        parts.append(f"<g><title>{escape(tip)}</title>")
        parts.append(f'<line class="interval" x1="{px:.1f}" x2="{px:.1f}" y1="{y(p["hi"]):.1f}" y2="{y(p["lo"]):.1f}"/>')
        parts.append(f'<circle class="dot" cx="{px:.1f}" cy="{py:.1f}" r="5"/>')
        parts.append(f'<text class="label" x="{px + 10:.1f}" y="{ly:.1f}">{escape(p["name"])}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
