#!/usr/bin/env python3
"""Build quiz HTML from JSON payload.
Usage: python build_quiz.py <input.json> <output.html>
JSON format: {
  "title":"...", "meta":"...", "question_count":10,
  "questions":[{
    "id":1, "style":"boundary", "topic":"...",
    "stem":"...",
    "choices":[{"letter":"A","text":"..."},{"letter":"B","text":"..."},...],
    "correct":"B",
    "explanation":"...",
    "connection":"optional..."
  }]
}
"""
import json, sys, os
from html import escape

def build_question_html(q):
    qid = q["id"]
    style_label = q.get("style", "")
    style_map = {
        "boundary": "Boundary",
        "flaw": "Spot the flaw",
        "deep-short": "Deep-short",
        "measure": "What does it measure",
        "bridge": "Cross-topic"
    }
    style_display = style_map.get(style_label, style_label)

    choices_html = ""
    for c in q["choices"]:
        letter = c["letter"]
        text = c["text"]
        choices_html += (
            f'<div class="choice" data-letter="{letter}" '
            f'onclick="pick({qid},\'{letter}\')">'
            f'<span class="choice-letter">{letter}</span>'
            f'<span>{text}</span></div>'
        )

    explanation = q.get("explanation", "")
    connection = q.get("connection", "")
    conn_html = ""
    if connection:
        conn_html = f'<div class="connection"><strong>Connection:</strong> {connection}</div>'

    topic = q.get("topic", "").replace('"', '&quot;')

    return (
        f'<div class="question-card" id="q-{qid}" data-correct="{q["correct"]}" data-topic="{topic}" data-done="0">'
        f'<div class="question-header">'
        f'<span class="question-number">Q{qid}</span>'
        f'<span class="question-style">{style_display}</span>'
        f'</div>'
        f'<div class="question-stem">{q["stem"]}</div>'
        f'<div class="choices">{choices_html}</div>'
        f'<div class="explanation">{explanation}{conn_html}</div>'
        f'</div>'
    )

def build(input_path, output_path):
    tpl_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    with open(os.path.join(tpl_dir, "quiz.html"), "r") as f:
        tpl = f.read()
    with open(input_path, "r") as f:
        data = json.load(f)

    count = data.get("question_count", len(data["questions"]))
    questions_html = "\n".join(build_question_html(q) for q in data["questions"])

    # Extract filename without extension for the export JSON reference
    quiz_file = os.path.splitext(os.path.basename(output_path))[0]

    html = tpl.replace("{{TITLE}}", data.get("title", "Quiz"))
    html = html.replace("{{META}}", data.get("meta", ""))
    html = html.replace("{{QUESTION_COUNT}}", str(count))
    html = html.replace("{{QUIZ_FILE}}", quiz_file)
    html = html.replace("{{QUESTIONS}}", questions_html)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    print(f"Built: {build(sys.argv[1], sys.argv[2])}")
