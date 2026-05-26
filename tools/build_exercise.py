#!/usr/bin/env python3
"""Build exercise HTML from JSON payload.
Usage: python build_exercise.py <input.json> <output.html>
JSON format: {
  "title":"...", "meta":"...",
  "exercises":[{
    "id":1, "style":"compute|derive", "title":"Exercise 1: ...",
    "problem":"<p>HTML problem statement</p>",
    "hints":["hint 1","hint 2"],
    "solution_steps":[
      {"label":"Step 1","html":"<p>...</p>"},
      {"label":"Step 2","html":"<p>...</p>"}
    ],
    "answer":"$final answer$"
  }]
}
"""
import json, sys, os


def build_exercise_html(ex):
    eid = ex["id"]
    style = ex.get("style", "compute")
    style_display = "Derivation" if style == "derive" else "Compute"
    tag_class = "tag-derive" if style == "derive" else "tag-compute"
    card_class = "exercise derive" if style == "derive" else "exercise"

    # Hints
    hints_html = ""
    hint_btns = ""
    for i, hint in enumerate(ex.get("hints", []), 1):
        hid = f"hint-{eid}-{i}"
        hint_btns += f'<button class="hint-btn" onclick="toggleEl(\'{hid}\')">Hint {i}</button>'
        hints_html += f'<div class="hint-box" id="{hid}"><strong>Hint {i}:</strong> {hint}</div>'

    # Solution steps
    steps_html = ""
    for step in ex.get("solution_steps", []):
        steps_html += (
            f'<div class="step">'
            f'<span class="step-label">{step["label"]}</span> '
            f'{step["html"]}'
            f'</div>'
        )

    answer = ex.get("answer", "")
    answer_html = f'<div class="final-answer">{answer}</div>' if answer else ""

    sol_id = f"sol-{eid}"

    return (
        f'<div class="{card_class}" id="ex-{eid}">'
        f'<div class="exercise-header">'
        f'<h2>{ex.get("title", f"Exercise {eid}")}</h2>'
        f'<span class="style-tag {tag_class}">{style_display}</span>'
        f'</div>'
        f'<div class="problem">{ex["problem"]}</div>'
        f'<div class="controls">'
        f'{hint_btns}'
        f'<button class="sol-btn" onclick="toggleEl(\'{sol_id}\')">Show solution</button>'
        f'</div>'
        f'{hints_html}'
        f'<div class="solution" id="{sol_id}">'
        f'<h3>Solution</h3>'
        f'{steps_html}'
        f'{answer_html}'
        f'</div>'
        f'</div>'
    )


def build(input_path, output_path):
    tpl_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    with open(os.path.join(tpl_dir, "exercise.html"), "r") as f:
        tpl = f.read()
    with open(input_path, "r") as f:
        data = json.load(f)

    exercises_html = "\n".join(build_exercise_html(ex) for ex in data["exercises"])

    html = tpl.replace("{{TITLE}}", data.get("title", "Exercises"))
    html = html.replace("{{META}}", data.get("meta", ""))
    html = html.replace("{{EXERCISES}}", exercises_html)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    print(f"Built: {build(sys.argv[1], sys.argv[2])}")
