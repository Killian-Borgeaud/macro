#!/usr/bin/env python3
"""Build exam HTML from JSON payload.

Usage: python build_exam.py <input.json> <output.html>

Top-level payload:
  {
    "title": "Mock Exam Simulation",
    "meta": "Macroeconomics III — full 4-question essay simulation — YYYY-MM-DD",
    "exam_info": {
      "total_minutes": 90,
      "num_questions": 4,
      "weight_per_question": "25%",
      "format_note": "4 essay questions, equal weight. No MCQ, no T/F, no sub-parts."
    },
    "questions": [ <question>, ... ]
  }

A <question> is:
  {
    "id": 1,
    "module": 1,
    "verb_pair": "describe + critique",      # one of the mock-exam verb pairs
    "weight": "25%",
    "target_minutes": 20,
    "prompt": "<html — short, declarative, Cozzi-style 2-4 lines>",
    "skeleton": [                             # the points a good answer must hit
      "Point 1: ...",
      "Point 2: ...",
      ...
    ],
    "model_answer": "<html ~600-800 word essay, with <h3> sub-sections, "
                    "key-result HUD blocks, KaTeX math, etc.>"
  }

The exam format reflects Prof. Cozzi's mock: 4 essay questions, 25% each,
two-component (technical + interpretive) prompts. No hints during the exam —
this skill simulates the real test.
"""
import json
import os
import sys


def _build_exam_info(info):
    if not info:
        return ""
    n = info.get("num_questions", 4)
    total = info.get("total_minutes", 90)
    weight = info.get("weight_per_question", "25%")
    note = info.get("format_note", "")
    cells = (
        f'<div class="exam-info-cell"><span class="val">{n}</span>'
        f'<span class="lbl">questions</span></div>'
        f'<div class="exam-info-cell"><span class="val">{weight}</span>'
        f'<span class="lbl">each</span></div>'
        f'<div class="exam-info-cell"><span class="val">{total} min</span>'
        f'<span class="lbl">total</span></div>'
        f'<div class="exam-info-cell"><span class="val">{total // n} min</span>'
        f'<span class="lbl">per Q (target)</span></div>'
    )
    note_html = (
        f'<div class="exam-info-note">{note}</div>' if note else ''
    )
    return (
        '<div class="exam-info">'
        '<span class="exam-info-label">Exam format</span>'
        f'{cells}{note_html}'
        '</div>'
    )


def _build_question(q):
    qid = q["id"]
    module = q.get("module", "")
    verb_pair = q.get("verb_pair", "")
    weight = q.get("weight", "25%")
    target_min = q.get("target_minutes", 20)
    prompt = q["prompt"]
    skeleton = q.get("skeleton", []) or []
    model_answer = q.get("model_answer", "")

    # Tags row
    tag_bits = [f'<span class="q-tag weight">{weight}</span>']
    if module:
        tag_bits.append(f'<span class="q-tag module">Module {module}</span>')
    if verb_pair:
        tag_bits.append(f'<span class="q-tag">{verb_pair}</span>')
    tag_bits.append(f'<span class="q-tag time">~{target_min} min</span>')
    tags_html = "".join(tag_bits)

    # Skeleton
    skel_html = ""
    skel_btn = ""
    if skeleton:
        skel_items = "".join(f'<li>{s}</li>' for s in skeleton)
        skel_html = (
            '<div class="skeleton">'
            '<div class="skeleton-title">Answer skeleton — what to cover</div>'
            f'<ul>{skel_items}</ul>'
            '</div>'
        )
        skel_btn = (
            f'<button class="reveal-btn" type="button" '
            f'data-label="Reveal skeleton" '
            f'onclick="toggleSection(this,\'skeleton\')">Reveal skeleton</button>'
        )

    # Model answer
    model_btn = (
        f'<button class="reveal-btn primary" type="button" '
        f'data-label="Reveal model answer" '
        f'onclick="toggleSection(this,\'model-answer\')">Reveal model answer</button>'
    )
    model_html = (
        '<div class="model-answer">'
        '<div class="model-answer-title">Model answer (exam-quality, ~600-800 words)</div>'
        f'{model_answer}'
        '</div>'
    )

    return (
        f'<div class="question" id="q-{qid}">'
        f'<div class="question-header">'
        f'<span class="q-num">Question {qid}</span>'
        f'<div class="q-tags">{tags_html}</div>'
        f'</div>'
        f'<div class="q-prompt">{prompt}</div>'
        f'<div class="reveal-row">'
        f'{skel_btn}{model_btn}'
        f'<span class="reveal-hint-text">Outline your answer before revealing.</span>'
        f'</div>'
        f'{skel_html}'
        f'{model_html}'
        f'</div>'
    )


def build(input_path, output_path):
    tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(tpl_dir, "exam.html"), "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    exam_info_html = _build_exam_info(data.get("exam_info", {}))
    questions_html = "\n".join(_build_question(q) for q in questions)

    html = (tpl
            .replace("{{TITLE}}", data.get("title", "Exam Simulation"))
            .replace("{{META}}", data.get("meta", ""))
            .replace("{{EXAM_INFO}}", exam_info_html)
            .replace("{{QUESTIONS}}", questions_html))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Smoke checks ────────────────────────────────────────────────────
    warnings = []
    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids):
        dupes = [i for i in ids if ids.count(i) > 1]
        warnings.append(f"duplicate question ids: {sorted(set(dupes))}")
    if len(questions) != 4:
        warnings.append(
            f"exam has {len(questions)} questions (Cozzi's real exam is 4 — "
            "check this is intentional)"
        )
    for q in questions:
        if not q.get("prompt"):
            warnings.append(f"Q{q['id']}: empty prompt")
        if not q.get("model_answer"):
            warnings.append(f"Q{q['id']}: empty model_answer")
        if not q.get("verb_pair"):
            warnings.append(f"Q{q['id']}: no verb_pair tag")
    total_target = sum(q.get("target_minutes", 0) for q in questions)
    info_total = data.get("exam_info", {}).get("total_minutes", 90)
    if total_target and abs(total_target - info_total) > 15:
        warnings.append(
            f"sum of target_minutes is {total_target} but exam_info.total_minutes is {info_total}"
        )
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
