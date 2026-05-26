#!/usr/bin/env python3
"""Build lecture HTML from JSON payload.
Usage: python build_lecture.py <input.json> <output.html>

Payload format:
  {
    "title": "...",
    "meta": "...",
    "sections": [{"id": "sec-1", "title": "...", "html": "<p>...</p>"}],
    "interactive_figures": [   # optional
      {"id": "fig-x", "spec": {...}}              # inline spec
      OR
      {"id": "fig-x", "library": "solow-pair"}   # reference tools/figures/library/*.json
    ]
  }

Each `<div data-figure='fig-x'></div>` placeholder in any section html is
replaced with the rendered interactive figure snippet.
"""
import json
import re
import sys
import os
from pathlib import Path

# Local import: figure builder lives next to this script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_figure import build_snippet, RUNTIME_CSS, RUNTIME_JS  # noqa: E402

PLOTLY_CDN = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
LIBRARY_DIR = Path(__file__).parent / "figures" / "library"
PLACEHOLDER_RE = re.compile(r"<div\s+data-figure=['\"]([^'\"]+)['\"]\s*></div>")


def _resolve_figure(entry: dict) -> dict:
    """Return a spec dict for an interactive_figures entry."""
    if "spec" in entry:
        spec = entry["spec"]
    elif "library" in entry:
        lib_path = LIBRARY_DIR / f"{entry['library']}.json"
        spec = json.loads(lib_path.read_text(encoding="utf-8"))
        if "overrides" in entry and isinstance(entry["overrides"], dict):
            # shallow merge of params/sliders (most common override case)
            for k, v in entry["overrides"].items():
                if k == "params" and isinstance(v, dict):
                    spec.setdefault("params", {}).update(v)
                else:
                    spec[k] = v
    else:
        raise ValueError(f"interactive_figure entry needs 'spec' or 'library': {entry}")
    # Allow the payload to override the figure id (lets one library spec be used
    # multiple times in one lecture under different placeholder ids).
    if "id" in entry:
        spec = dict(spec)
        spec["id"] = entry["id"]
    return spec


def build(input_path: str, output_path: str) -> str:
    tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(tpl_dir, "lecture.html"), "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build figure snippets indexed by id
    snippets = {}
    for entry in data.get("interactive_figures", []):
        spec = _resolve_figure(entry)
        snippets[spec["id"]] = build_snippet(spec)

    # Substitute placeholders in each section's html
    def substitute(html: str) -> str:
        def repl(m):
            fig_id = m.group(1)
            return snippets.get(
                fig_id,
                f'<div style="border:2px dashed #dc2626;padding:1rem;color:#dc2626">'
                f'Missing interactive figure: <code>{fig_id}</code></div>',
            )
        return PLACEHOLDER_RE.sub(repl, html)

    nav = "".join(f'<a href="#{s["id"]}">{s["title"]}</a>' for s in data["sections"])
    sections = "".join(
        f'<div class="section" id="{s["id"]}"><h2>{s["title"]}</h2>{substitute(s["html"])}</div>'
        for s in data["sections"]
    )

    has_figures = bool(snippets)
    plotly_script = PLOTLY_CDN if has_figures else ""
    figure_css = RUNTIME_CSS if has_figures else ""
    figure_js = f"<script>{RUNTIME_JS}</script>" if has_figures else ""

    html = (tpl
            .replace("{{TITLE}}", data.get("title", "Lecture"))
            .replace("{{META}}", data.get("meta", ""))
            .replace("{{NAV_LINKS}}", nav)
            .replace("{{SECTIONS}}", sections)
            .replace("{{PLOTLY_SCRIPT}}", plotly_script)
            .replace("{{FIGURE_CSS}}", figure_css)
            .replace("{{FIGURE_JS}}", figure_js))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Post-build smoke check ───────────────────────────────────────────────
    # Catch silent failures that the agent's audit can't see:
    #   (a) declared interactive_figures that no placeholder ever references
    #   (b) placeholders that still survive in the output (substitution failed)
    #   (c) script-ordering check: runtime IIFE must appear BEFORE renderFigure
    declared_ids = {e.get("id") for e in data.get("interactive_figures", [])}
    referenced_ids = set()
    for s in data["sections"]:
        referenced_ids.update(PLACEHOLDER_RE.findall(s["html"]))
    warnings = []
    orphan_declared = declared_ids - referenced_ids
    if orphan_declared:
        warnings.append(f"declared but never referenced: {sorted(orphan_declared)}")
    leftover = PLACEHOLDER_RE.findall(html)
    if leftover:
        warnings.append(f"placeholders not substituted: {sorted(set(leftover))}")
    if has_figures:
        runtime_pos = html.find("window.MacroFigures = window.MacroFigures")
        first_call_pos = html.find("window.MacroFigures.renderFigure")
        if runtime_pos == -1:
            warnings.append("FIGURE_JS runtime missing from output")
        elif first_call_pos != -1 and runtime_pos > first_call_pos:
            warnings.append(
                f"script ordering bug: runtime at pos {runtime_pos} but first "
                f"renderFigure call at pos {first_call_pos} — figures will fail silently"
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
