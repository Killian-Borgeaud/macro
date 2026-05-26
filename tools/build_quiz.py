#!/usr/bin/env python3
"""Build quiz HTML from JSON payload.

Usage: python build_quiz.py <input.json> <output.html>

Top-level payload:
  {
    "title": "...",
    "meta": "...",
    "questions": [ <question> | <chain>, ... ]
  }

A <question> is:
  {
    "id": 1,
    "style": "boundary" | "flaw" | "deep-short" | "measure" | "bridge"
           | "multi-select" | "numeric" | "graph"
           | "derivation-justify" | "derivation-source" | "derivation-why",
    "topic": "short label",
    "stem": "html",
    "choices": [
      {"letter": "A", "text": "...", "defense": "why a partial-understander picks this"},
      ...
    ],
    "correct": "B"                    # single-MCQ types and numeric and graph and derivation-*
            | ["A", "C"],             # multi-select
    "explanation": "html",
    "connection": "optional html",    # rendered as a footnote inside the explanation block
    "figure": { ... }                 # required for style == "graph"; spec format from build_figure
    "derivation": ["step1", "step2", ...]   # required for derivation-* styles (LaTeX strings)
    "highlight": 3                    # 1-indexed step the question targets (derivation-* styles)
  }

A <chain> is:
  { "type": "chain", "setup": "html", "questions": [ <question>, <question>, ... ] }
"""
import json
import os
import sys
from pathlib import Path

# Local import: figure builder lives next to this script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_figure import build_snippet, RUNTIME_CSS, RUNTIME_JS  # noqa: E402

PLOTLY_CDN = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'

STYLE_LABELS = {
    "boundary": "Boundary",
    "flaw": "Spot the flaw",
    "deep-short": "Deep-short",
    "measure": "What it measures",
    "bridge": "Cross-topic",
    "multi-select": "Multi-select",
    "numeric": "Numeric",
    "graph": "Graph",
    "derivation-justify": "Derivation · justify step",
    "derivation-source": "Derivation · source",
    "derivation-why": "Derivation · why",
}


def _topic_attr(q):
    return q.get("topic", "").replace('"', '&quot;')


def _build_choice_html(c, multi=False):
    """Render one choice row. Multi-select uses toggle() instead of pick()."""
    letter = c["letter"]
    text = c["text"]
    defense = c.get("defense", "")
    defense_html = f'<div class="choice-defense">{defense}</div>' if defense else ""
    # The chip's visible letter is wrapped in a span so multi-select can hide it
    # behind a checkmark without losing it from the DOM (keeps spacing stable).
    chip = f'<span class="choice-letter"><span>{letter}</span></span>'
    body = f'<div class="choice-body">{text}{defense_html}</div>'
    return (
        f'<div class="choice" data-letter="{letter}">'
        f'{chip}{body}'
        f'</div>'
    )


def _build_derivation_html(steps, highlight, style):
    """Render the numbered derivation step list inside the stem.

    For derivation-justify: the highlighted step is shown but boxed.
    For derivation-source: no highlight (the final identity is in the stem, choices are derivations).
    For derivation-why: no highlight (the identity is in the stem, choices are mechanisms).
    """
    rows = []
    for i, step in enumerate(steps, start=1):
        classes = ["derivation-step"]
        if highlight and i == highlight:
            classes.append("highlight")
        cls = " ".join(classes)
        rows.append(
            f'<div class="{cls}"><span class="step-num">({i})</span>'
            f'<span class="step-body">{step}</span></div>'
        )
    return f'<div class="derivation-block">{"".join(rows)}</div>'


def _build_question_html(q):
    qid = q["id"]
    style = q.get("style", "")
    style_display = STYLE_LABELS.get(style, style)
    topic = _topic_attr(q)

    # Build stem with optional derivation block or figure embedded after the prose.
    stem_html = q["stem"]
    if style in ("derivation-justify", "derivation-source", "derivation-why"):
        steps = q.get("derivation", [])
        if steps:
            highlight = q.get("highlight") if style == "derivation-justify" else None
            stem_html += _build_derivation_html(steps, highlight, style)
    figure_snippet = ""
    if style == "graph":
        spec = q.get("figure")
        if not spec:
            raise ValueError(f"Q{qid} is style=graph but has no 'figure' field")
        # Force-strip sliders: graph quizzes are static.
        spec = dict(spec)
        spec.pop("sliders", None)
        spec.setdefault("id", f"fig-q{qid}")
        figure_snippet = build_snippet(spec)
        stem_html += figure_snippet

    # Card-level classes for multi-select and mono numeric.
    card_classes = ["question-card"]
    is_multi = style == "multi-select"
    if is_multi:
        card_classes.append("multi")
    if style == "numeric":
        card_classes.append("mono-choices")

    # Build choices and click bindings.
    choices_html = ""
    for c in q["choices"]:
        choice = _build_choice_html(c, multi=is_multi)
        if is_multi:
            choice = choice.replace(
                'class="choice"',
                f'class="choice" onclick="toggle({qid},\'{c["letter"]}\')"',
            )
        else:
            choice = choice.replace(
                'class="choice"',
                f'class="choice" onclick="pick({qid},\'{c["letter"]}\')"',
            )
        choices_html += choice

    # data-correct: single string or JSON array
    correct = q["correct"]
    if isinstance(correct, list):
        correct_attr = json.dumps(sorted(correct))
    else:
        correct_attr = str(correct)
    # HTML attribute quoting: data-correct goes inside double quotes, so any inner
    # double quotes (from JSON) must be escaped.
    correct_attr_html = correct_attr.replace('"', '&quot;')

    # Multi-select submit row
    submit_row = ""
    if is_multi:
        submit_row = (
            f'<div class="submit-row">'
            f'<button type="button" class="submit-btn" disabled '
            f'onclick="submitMulti({qid})">Submit</button>'
            f'<span>Pick all that apply, then submit.</span>'
            f'</div>'
        )

    # Explanation block
    explanation = q.get("explanation", "")
    connection = q.get("connection", "")
    conn_html = (
        f'<div class="connection"><strong>Connection:</strong> {connection}</div>'
        if connection else ""
    )

    return (
        f'<div class="{" ".join(card_classes)}" id="q-{qid}" '
        f'data-correct="{correct_attr_html}" data-topic="{topic}" data-done="0">'
        f'<div class="question-header">'
        f'<span class="question-number">Q{qid}</span>'
        f'<span class="question-style">{style_display}</span>'
        f'</div>'
        f'<div class="question-stem">{stem_html}</div>'
        f'<div class="choices">{choices_html}</div>'
        f'{submit_row}'
        f'<div class="explanation">{explanation}{conn_html}</div>'
        f'</div>'
    )


def _build_chain_html(chain):
    setup = chain.get("setup", "")
    inner = "".join(_build_question_html(q) for q in chain["questions"])
    return (
        f'<div class="chain-block">'
        f'<span class="chain-label">Scenario</span>'
        f'<div class="chain-setup">{setup}</div>'
        f'{inner}'
        f'</div>'
    )


def _flatten_questions(items):
    """Yield each leaf question (chain-aware) in order."""
    for item in items:
        if item.get("type") == "chain":
            yield from item["questions"]
        else:
            yield item


def _has_any_graph(items):
    return any(q.get("style") == "graph" for q in _flatten_questions(items))


def build(input_path, output_path):
    tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(tpl_dir, "quiz.html"), "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["questions"]
    flat = list(_flatten_questions(items))
    count = len(flat)

    # Render each top-level item: either a chain block or a question card.
    blocks = []
    for item in items:
        if item.get("type") == "chain":
            blocks.append(_build_chain_html(item))
        else:
            blocks.append(_build_question_html(item))
    questions_html = "\n".join(blocks)

    has_fig = _has_any_graph(items)
    plotly_script = PLOTLY_CDN if has_fig else ""
    figure_css = RUNTIME_CSS if has_fig else ""
    figure_js = f"<script>{RUNTIME_JS}</script>" if has_fig else ""

    quiz_file = os.path.splitext(os.path.basename(output_path))[0]

    html = (tpl
            .replace("{{TITLE}}", data.get("title", "Quiz"))
            .replace("{{META}}", data.get("meta", ""))
            .replace("{{QUESTION_COUNT}}", str(count))
            .replace("{{QUIZ_FILE}}", quiz_file)
            .replace("{{QUESTIONS}}", questions_html)
            .replace("{{PLOTLY_SCRIPT}}", plotly_script)
            .replace("{{FIGURE_CSS}}", figure_css)
            .replace("{{FIGURE_JS}}", figure_js))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Smoke checks (post-build) ───────────────────────────────────────
    warnings = []
    ids = [q["id"] for q in flat]
    if len(set(ids)) != len(ids):
        dupes = [i for i in ids if ids.count(i) > 1]
        warnings.append(f"duplicate question ids: {sorted(set(dupes))}")
    for q in flat:
        if q.get("style") == "multi-select":
            if not isinstance(q.get("correct"), list):
                warnings.append(f"Q{q['id']} is multi-select but 'correct' is not a list")
        elif isinstance(q.get("correct"), list):
            warnings.append(f"Q{q['id']} (style={q.get('style')}) has list 'correct' but is not multi-select")
    if has_fig:
        runtime_pos = html.find("window.MacroFigures = window.MacroFigures")
        first_call_pos = html.find("window.MacroFigures.renderFigure")
        if runtime_pos == -1:
            warnings.append("graph questions present but FIGURE_JS runtime missing")
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
