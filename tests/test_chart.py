import re

import pytest

from bench.chart import accuracy_vs_time_svg, points, spread_labels
from bench.report import CHART_NAME, render, write_report
from bench.scoring import PASS, WRONG, ModelSummary, RunResult
from bench.site import inline_svgs


def summary(name, statuses, latency):
    s = ModelSummary(name, name)
    for i, status in enumerate(statuses):
        usage = {"latency_s": latency} if latency is not None else None
        s.runs["ledger"].append(RunResult("ledger", name, f"run_{i}", status, 1.0, 1.0, usage=usage))
    return s


def test_points_use_median_latency_and_wilson_interval_and_skip_models_without_timing():
    fast = summary("fast", [PASS, WRONG, WRONG, WRONG], 30.0)
    untimed = summary("legacy", [PASS], None)
    (p,) = points([fast, untimed])
    assert p["name"] == "fast" and p["seconds"] == 30.0 and p["rate"] == 0.25
    assert 0 < p["lo"] < 0.25 < p["hi"] < 1 and (p["passes"], p["runs"]) == (1, 4)


def test_labels_are_spread_apart_in_order_and_kept_inside():
    placed = spread_labels([100, 101, 300, 102], min_gap=15, top=50, bottom=400)
    assert placed == [100, 115, 300, 130]
    assert spread_labels([395, 396], 15, 50, 400) == [385, 400]  # pushed up from the bottom edge


def test_svg_has_a_point_tooltip_and_label_per_model_and_dark_mode():
    svg = accuracy_vs_time_svg([summary("fast", [PASS, WRONG], 30.0), summary("slow & sure", [PASS], 900.0)])
    assert svg.startswith("<svg") and svg.count('<circle class="dot"') == 2
    assert "slow &amp; sure: 1/1 run passed (100%" in svg  # escaped, singular for one run
    assert "fast: 1/2 runs passed (50%" in svg
    assert "prefers-color-scheme: dark" in svg and 'role="img"' in svg
    assert re.search(r">30 s<", svg) and re.search(r">15 min<|>10 min<", svg)


def test_no_chart_without_timed_runs():
    assert accuracy_vs_time_svg([summary("legacy", [PASS], None)]) is None
    assert "Accuracy vs. time" not in render([summary("legacy", [PASS], None)])


def test_report_links_the_chart_and_writes_it_next_to_the_markdown(tmp_path):
    path = write_report([summary("fast", [PASS, WRONG], 30.0)], tmp_path / "leaderboard.md")
    assert f"]({CHART_NAME})" in path.read_text(encoding="utf-8")
    assert (tmp_path / CHART_NAME).read_text(encoding="utf-8").startswith("<svg")


def test_site_inlines_local_svg_images(tmp_path):
    (tmp_path / "c.svg").write_text("<svg><title>t</title></svg>", encoding="utf-8")
    html = inline_svgs('<p><img alt="x" src="c.svg" /></p><img src="missing.svg">', tmp_path)
    assert '<figure class="chart"><svg><title>t</title></svg></figure>' in html
    assert '<img src="missing.svg">' in html  # left alone when the file is not there


@pytest.mark.parametrize("bad", ['<img src="../secret.svg">', '<img src="https://x.org/a.svg">'])
def test_site_only_inlines_files_beside_the_report(tmp_path, bad):
    assert inline_svgs(bad, tmp_path) == bad
