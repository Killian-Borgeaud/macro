#!/usr/bin/env python3
"""Build cheat sheet HTML from JSON payload.

Usage: python build_cheatsheet.py <input.json> <output.html>

The cheat sheet is a single dense reference document organized as:
  - Module-spine sections (M1-M6) with slide PNGs + mock answers in Cozzi tone
  - Cross-cutting comparison sections (convergence speeds, Golden Rule, R&D variants, ...)
  - Reference tables (notation, empirical numbers, simulation algorithm, glossary)

Each section can mix several content blocks; the builder is flexible about which
blocks each section uses.

JSON shape:
  {
    "title": "...",
    "meta": "...",
    "sections": [
      {
        "id": "sec-...",        # kebab-case, used for nav anchors
        "title": "...",
        "nav_group": "...",     # optional; groups nav links (e.g. "Modules", "Cross-cutting")
        "tag": "module 1",      # optional small tag in section header
        "pitch": "<html>",      # elevator pitch paragraph
        "slides": [
          {"path": "../../Material/.../pXXX.png", "caption": "..."},
          ...
        ],
        "slides_layout": "single|cols-2|cols-3",  # optional
        "skeleton": {
          "title": "Steady state k*",
          "steps": [
            {"math": "sBk^\\alpha = (n+\\delta)k", "why": "set $\\dot k = 0$"},
            ...
          ]
        },
        "mock_answer_title": "Mock answer (Cozzi tone)",  # default
        "mock_answer": "<html>",
        "key_results": ["$k^* = \\ldots$", ...],   # optional list of HUD callouts
        "pitfalls": ["...", "..."],   # optional, kept light
        "html": "<html>"        # optional free-form HTML (for ref/compare sections)
      }
    ]
  }
"""
import json
import os
import sys


def _render_slides(slides, layout):
    if not slides:
        return ""
    if len(slides) == 1 or not layout or layout == "single":
        s = slides[0]
        return (
            f'<div class="slide-block">'
            f'<img src="{s["path"]}" alt="{s.get("caption", "")}">'
            f'<div class="slide-caption">{s.get("caption", "")}</div>'
            f'</div>'
        )
    cls = layout if layout in ("cols-2", "cols-3") else "cols-2"
    items = "".join(
        f'<div class="slide-block">'
        f'<img src="{s["path"]}" alt="{s.get("caption", "")}">'
        f'<div class="slide-caption">{s.get("caption", "")}</div>'
        f'</div>'
        for s in slides
    )
    return f'<div class="slide-group {cls}">{items}</div>'


def _render_skeleton(sk):
    if not sk:
        return ""
    title = sk.get("title", "Skeleton derivation")
    steps = sk.get("steps", [])
    rows = []
    for i, step in enumerate(steps, start=1):
        math = step.get("math", "")
        why = step.get("why", "")
        rows.append(
            f'<div class="skeleton-step">'
            f'<span class="step-num">({i})</span>'
            f'<span class="step-math">{math}</span>'
            f'<span class="step-why">{why}</span>'
            f'</div>'
        )
    return (
        f'<div class="skeleton">'
        f'<div class="skeleton-title">{title}</div>'
        f'{"".join(rows)}'
        f'</div>'
    )


def _render_mock_answer(sec):
    body = sec.get("mock_answer")
    if not body:
        return ""
    title = sec.get("mock_answer_title", "Mock answer (Cozzi tone)")
    return (
        f'<div class="mock-answer">'
        f'<div class="mock-answer-title">{title}</div>'
        f'{body}'
        f'</div>'
    )


def _render_key_results(items):
    if not items:
        return ""
    return "".join(
        f'<div class="key-result"><strong>Result.</strong> {item}</div>' for item in items
    )


def _render_pitfalls(items):
    if not items:
        return ""
    lis = "".join(f"<li>{p}</li>" for p in items)
    return (
        f'<div class="pitfalls">'
        f'<div class="pitfalls-title">Quick pitfalls</div>'
        f'<ul>{lis}</ul>'
        f'</div>'
    )


def _render_section(sec):
    sec_id = sec["id"]
    title = sec["title"]
    tag = sec.get("tag", "")
    num = sec.get("num", "")
    tag_html = f'<span class="section-tag">{tag}</span>' if tag else ""
    num_html = f'<span class="section-num">§ {num}</span>' if num else ""
    pitch = sec.get("pitch", "")
    pitch_html = f'<div class="pitch">{pitch}</div>' if pitch else ""
    slides_html = _render_slides(sec.get("slides", []), sec.get("slides_layout"))
    skel_html = _render_skeleton(sec.get("skeleton"))
    mock_html = _render_mock_answer(sec)
    keys_html = _render_key_results(sec.get("key_results", []))
    pit_html = _render_pitfalls(sec.get("pitfalls", []))
    free_html = sec.get("html", "")
    return (
        f'<div class="section" id="{sec_id}">'
        f'<div class="section-header">'
        f'{num_html}'
        f'<h2>{title}</h2>'
        f'{tag_html}'
        f'</div>'
        f'{pitch_html}'
        f'{slides_html}'
        f'{free_html}'
        f'{skel_html}'
        f'{keys_html}'
        f'{mock_html}'
        f'{pit_html}'
        f'</div>'
    )


def _render_nav(sections):
    # Group by nav_group; preserve order
    groups = []
    current_group = None
    for s in sections:
        g = s.get("nav_group", "")
        if g != current_group:
            groups.append((g, []))
            current_group = g
        groups[-1][1].append(s)
    parts = []
    for label, secs in groups:
        if label:
            parts.append(f'<div class="nav-section-label">{label}</div>')
        for s in secs:
            parts.append(f'<a href="#{s["id"]}">{s["title"]}</a>')
    return "".join(parts)


def build(input_path, output_path):
    tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(tpl_dir, "cheatsheet.html"), "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections", [])
    # Auto-number sections that don't have a num set
    for i, s in enumerate(sections):
        if "num" not in s:
            s["num"] = str(i)

    nav_html = _render_nav(sections)
    sections_html = "\n".join(_render_section(s) for s in sections)

    html = (tpl
            .replace("{{TITLE}}", data.get("title", "Cheat Sheet"))
            .replace("{{META}}", data.get("meta", ""))
            .replace("{{NAV_LINKS}}", nav_html)
            .replace("{{SECTIONS}}", sections_html))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Smoke checks ────────────────────────────────────────────────────
    warnings = []
    ids = [s["id"] for s in sections]
    if len(set(ids)) != len(ids):
        dupes = [i for i in ids if ids.count(i) > 1]
        warnings.append(f"duplicate section ids: {sorted(set(dupes))}")
    # Verify slide PNG paths exist (relative to output file location)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    for s in sections:
        for slide in s.get("slides", []):
            p = slide.get("path", "")
            if p:
                abs_path = os.path.normpath(os.path.join(out_dir, p))
                if not os.path.exists(abs_path):
                    warnings.append(f"missing slide PNG: {p} (resolved to {abs_path})")
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
