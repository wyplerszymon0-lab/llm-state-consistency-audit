"""Render reports/leaderboard.md as a standalone HTML page for GitHub Pages.

Usage:
    python -m bench.site                          # reports/leaderboard.md -> site/index.html
    python -m bench.site IN.md OUT.html
"""

import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/wyplerszymon0-lab/llm-state-consistency-audit"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM State-Consistency Leaderboard</title>
<meta name="description" content="Pass rates of LLM-generated programs on stateful simulations, with confidence intervals and failure details.">
<style>
  :root {{ color-scheme: light; --bg: #fcfcfb; --fg: #0b0b0b; --muted: #52514e; --line: #e1e0d9; --head: #f3f2ee; --link: #2a78d6; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ color-scheme: dark; --bg: #1a1a19; --fg: #ffffff; --muted: #c3c2b7; --line: #2c2c2a; --head: #222220; --link: #3987e5; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }}
  h1 {{ font-size: 26px; margin: 0 0 8px; }}
  h2 {{ font-size: 18px; margin: 32px 0 8px; }}
  p, li {{ color: var(--muted); }}
  a {{ color: var(--link); }}
  code {{ font-size: 0.9em; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }}
  th, td {{ padding: 6px 10px; border-bottom: 1px solid var(--line); text-align: left; white-space: nowrap; }}
  th {{ background: var(--head); font-weight: 600; }}
  footer {{ margin-top: 40px; font-size: 13px; color: var(--muted); }}
</style>
</head>
<body>
<main>
{body}
<footer>Source, scenarios and methodology: <a href="{repo}">{repo}</a></footer>
</main>
</body>
</html>
"""


def render(markdown_text: str) -> str:
    body = markdown.markdown(markdown_text, extensions=["tables"], output_format="html")
    # Wide tables scroll inside their own box instead of widening the page on phones.
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return PAGE.format(body=body, repo=REPO_URL)


def main(argv: list[str]) -> None:
    source = Path(argv[0]) if argv else ROOT / "reports" / "leaderboard.md"
    target = Path(argv[1]) if len(argv) > 1 else ROOT / "site" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(source.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main(sys.argv[1:])
