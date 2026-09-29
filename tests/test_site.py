from bench.site import REPO_URL, render

SAMPLE = """# Title

Intro with **bold**.

| Rank | Model | Pass rate |
| ---: | :--- | ---: |
| 1 | m | 7% [1%–30%] |
"""


def test_render_produces_a_standalone_page_with_tables():
    html = render(SAMPLE)
    assert html.startswith("<!doctype html>")
    assert "<h1>Title</h1>" in html
    assert '<div class="table-wrap"><table>' in html and "</table></div>" in html
    assert '<td style="text-align: right;">7% [1%–30%]</td>' in html
    assert REPO_URL in html
    assert "prefers-color-scheme: dark" in html


def test_render_keeps_braces_from_the_report():
    # The page template uses str.format; braces in the report must survive.
    assert "{x}" in render("Value `{x}`")
