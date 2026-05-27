#!/usr/bin/env python3
"""Build exercise HTML from JSON payload.

Usage: python build_exercise.py <input.json> <output.html>

Top-level payload:
  {
    "title": "...",
    "meta": "...",
    "coverage": {
      "module_scope": "module 1 (basic Solow)",
      "exhaustive_mutually_exclusive": true,
      "topics_covered": [
        {"exercise_id": 1, "topics": ["topic A", "topic B"]},
        ...
      ],
      "topics_excluded": ["topic intentionally not covered + why"]
    },
    "exercises": [ <exercise>, ... ]
  }

An <exercise> is:
  {
    "id": 1,
    "title": "<short descriptive title>",
    "scope": "Module 1 §3-§4 (Solow law of motion, stability)",
    "sub_moves": [
      {"label": "Anchor", "prompt": "<html>", "hints": ["...", "..."]},
      {"label": "Main proof", "prompt": "<html>", "hints": ["...", "...", "..."]},
      {"label": "Method variation", "prompt": "<html>", "hints": []},
      {"label": "Methodology reflection", "prompt": "<html>", "hints": []},
      {"label": "Counterfactual", "prompt": "<html>", "hints": []}
    ],
    "figure": {...},          # optional, build_figure spec embedded after the main-proof sub-move
    "figure_anchor": "Main proof",  # which sub-move to attach figure to (default: last sub-move with no figure)
    "solution": "<html>"      # full ~1500-word solution; agent organizes with <h3>/<h4> per sub-move
  }

The builder is shape-agnostic about which sub-move labels appear — the agent
chooses labels per exercise (Anchor/Main/Variation/Reflection/Counterfactual,
or whatever fits). Hints are progressive per sub-move; the solution is one
block per exercise, hidden by default.
"""
import json
import os
import sys

# Reuse figure runtime from build_figure (graphs in exercises are static —
# we strip sliders just like quiz graphs).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_figure import build_snippet, RUNTIME_CSS, RUNTIME_JS  # noqa: E402

PLOTLY_CDN = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'


def _build_hints_block(hints, qid_prefix):
    """Render the hint area for one sub-move: hidden hint divs + a single
    progressive button. Button hides itself once all hints are shown."""
    if not hints:
        return ""
    total = len(hints)
    hint_divs = []
    for i, h in enumerate(hints, start=1):
        hint_divs.append(
            f'<div class="hint" data-idx="{i}"><strong>Hint {i}.</strong> {h}</div>'
        )
    return (
        '<div class="hints-area">'
        + "".join(hint_divs)
        + f'<button type="button" class="hint-btn" onclick="nextHint(this)">'
        f'Hint 1 / {total}</button>'
        + '</div>'
    )


def _build_sub_move(move, eid, idx, figure_html):
    label = move.get("label", f"Part {idx}")
    prompt = move.get("prompt", "")
    hints = move.get("hints", []) or []
    total = len(hints)
    hints_block = _build_hints_block(hints, f"ex{eid}-m{idx}")
    # Figure (if attached to this sub-move) goes after the prompt, before hints.
    fig_block = figure_html or ""
    return (
        f'<div class="sub-move" data-hints-total="{total}" data-hints-shown="0">'
        f'<div class="sub-move-label">{label}</div>'
        f'<div class="sub-move-prompt">{prompt}</div>'
        f'{fig_block}'
        f'{hints_block}'
        f'</div>'
    )


def _build_exercise(ex):
    eid = ex["id"]
    title = ex.get("title", f"Exercise {eid}")
    scope = ex.get("scope", "")
    sub_moves = ex.get("sub_moves", [])
    solution = ex.get("solution", "")
    fig_spec = ex.get("figure")
    fig_anchor = ex.get("figure_anchor")  # which sub-move label hosts the figure

    # Build the figure snippet once (if any), then attach to the right sub-move.
    figure_snippet = ""
    if fig_spec:
        spec = dict(fig_spec)
        spec.pop("sliders", None)
        spec.setdefault("id", f"fig-ex{eid}")
        figure_snippet = build_snippet(spec)

    # Resolve which sub-move index to attach the figure to.
    target_idx = -1
    if figure_snippet:
        if fig_anchor:
            for i, m in enumerate(sub_moves):
                if m.get("label") == fig_anchor:
                    target_idx = i
                    break
        if target_idx == -1:
            # Default: attach to the first sub-move whose label starts with "Main"
            for i, m in enumerate(sub_moves):
                if m.get("label", "").lower().startswith("main"):
                    target_idx = i
                    break
        if target_idx == -1 and sub_moves:
            target_idx = 0

    moves_html = []
    for i, move in enumerate(sub_moves):
        fh = figure_snippet if i == target_idx else ""
        moves_html.append(_build_sub_move(move, eid, i + 1, fh))
    moves_html = "".join(moves_html)

    scope_html = (
        f'<div class="exercise-scope"><strong>Scope:</strong> {scope}</div>'
        if scope else ''
    )

    return (
        f'<div class="exercise" id="ex-{eid}">'
        f'<div class="exercise-header">'
        f'<span class="exercise-number">Exercise {eid}</span>'
        f'<span class="exercise-title">{title}</span>'
        f'</div>'
        f'{scope_html}'
        f'{moves_html}'
        f'<div class="solution-toggle-row">'
        f'<button type="button" class="solution-btn" onclick="toggleSolution(this)">Show solution</button>'
        f'<span class="solution-hint-text">Solve on paper first.</span>'
        f'</div>'
        f'<div class="solution">{solution}</div>'
        f'</div>'
    )


def _build_coverage(coverage):
    if not coverage:
        return ""
    module_scope = coverage.get("module_scope", "")
    em = coverage.get("exhaustive_mutually_exclusive")
    topics_covered = coverage.get("topics_covered", [])
    topics_excluded = coverage.get("topics_excluded", [])

    scope_line = ""
    if module_scope or em is not None:
        em_text = "exhaustive · mutually exclusive" if em else ""
        scope_line = (
            f'<div class="coverage-scope">'
            f'<strong>Scope:</strong> {module_scope}'
            f'{" — " + em_text if em_text else ""}'
            f'</div>'
        )

    items = []
    for entry in topics_covered:
        ex_id = entry.get("exercise_id", "")
        topics = entry.get("topics", [])
        topics_text = " · ".join(topics) if topics else ""
        items.append(
            f'<li><span class="cov-num">Ex {ex_id}</span>'
            f'<span>{topics_text}</span></li>'
        )
    covered_html = (
        f'<ul class="coverage-list">{"".join(items)}</ul>' if items else ""
    )

    excluded_html = ""
    if topics_excluded:
        excluded_text = "; ".join(topics_excluded)
        excluded_html = (
            f'<div class="coverage-excluded">'
            f'<strong>Out of set</strong> (handled elsewhere or out of scope): {excluded_text}'
            f'</div>'
        )

    return (
        f'<div class="coverage">'
        f'<span class="coverage-label">Coverage</span>'
        f'{scope_line}'
        f'{covered_html}'
        f'{excluded_html}'
        f'</div>'
    )


def _has_any_figure(exercises):
    return any(ex.get("figure") for ex in exercises)


def build(input_path, output_path):
    tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(tpl_dir, "exercise.html"), "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    exercises = data.get("exercises", [])
    coverage_html = _build_coverage(data.get("coverage", {}))
    exercises_html = "\n".join(_build_exercise(ex) for ex in exercises)

    has_fig = _has_any_figure(exercises)
    plotly_script = PLOTLY_CDN if has_fig else ""
    figure_css = RUNTIME_CSS if has_fig else ""
    figure_js = f"<script>{RUNTIME_JS}</script>" if has_fig else ""

    html = (tpl
            .replace("{{TITLE}}", data.get("title", "Exercises"))
            .replace("{{META}}", data.get("meta", ""))
            .replace("{{COVERAGE}}", coverage_html)
            .replace("{{EXERCISES}}", exercises_html)
            .replace("{{PLOTLY_SCRIPT}}", plotly_script)
            .replace("{{FIGURE_CSS}}", figure_css)
            .replace("{{FIGURE_JS}}", figure_js))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Smoke checks ────────────────────────────────────────────────────
    warnings = []
    ids = [ex["id"] for ex in exercises]
    if len(set(ids)) != len(ids):
        dupes = [i for i in ids if ids.count(i) > 1]
        warnings.append(f"duplicate exercise ids: {sorted(set(dupes))}")
    if len(exercises) != 5:
        warnings.append(
            f"exercise set has {len(exercises)} exercises (expected 5 per the skill spec)"
        )
    for ex in exercises:
        sm = ex.get("sub_moves", [])
        if not sm:
            warnings.append(f"Ex {ex['id']}: no sub_moves")
        if not ex.get("solution"):
            warnings.append(f"Ex {ex['id']}: empty solution")
        # Every exercise needs at least one substantive sub-move (not a pure
        # depth-probe). Depth-probes alone are anchor / reflection / counterfactual.
        DEPTH_PROBE_LABELS = {
            "anchor", "methodology reflection", "reflection",
            "counterfactual", "falsification probe",
        }
        substantive = [
            m for m in sm
            if m.get("label", "").strip().lower() not in DEPTH_PROBE_LABELS
        ]
        if not substantive:
            warnings.append(
                f"Ex {ex['id']}: no substantive sub-move "
                f"(every sub-move is a depth-probe like Anchor/Reflection/Counterfactual)"
            )
    cov = data.get("coverage", {})
    covered_ids = {entry.get("exercise_id") for entry in cov.get("topics_covered", [])}
    if cov and covered_ids != set(ids):
        warnings.append(
            f"coverage.topics_covered ids {sorted(covered_ids)} != exercise ids {sorted(ids)}"
        )
    if has_fig:
        runtime_pos = html.find("window.MacroFigures = window.MacroFigures")
        first_call_pos = html.find("window.MacroFigures.renderFigure")
        if runtime_pos == -1:
            warnings.append("figures present but FIGURE_JS runtime missing")
        elif first_call_pos != -1 and runtime_pos > first_call_pos:
            warnings.append("script ordering bug: runtime after first renderFigure call")
    if warnings:
        print("WARNINGS:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    print(f"Built: {build(sys.argv[1], sys.argv[2])}")
