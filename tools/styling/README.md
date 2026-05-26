# Styling workspace

Use this to iterate on the lecture HTML look without rebuilding real material.

## Workflow

1. Edit one of:
   - `tools/templates/lecture.html` (palette, fonts, layout, callout boxes)
   - `tools/build_figure.py` → `RUNTIME_CSS` (figure cards, sliders, captions, readout)
   - `tools/build_figure.py` → Plotly `layout` block (axis colors, fonts, line widths)
2. Rebuild the preview:
   ```
   python tools/build_lecture.py tools/styling/fixture.json tools/styling/preview.html
   ```
3. Refresh `preview.html` in a browser.

## What the fixture covers

`fixture.json` is a single hand-written payload that exercises every renderable
element exactly once: typography, inline + display math, key-concept and example
callouts, table, code block, interactive Plotly figure with slider, schematic
SVG figure. If you add a new element type to the lecture pipeline, add an
instance here so it stays in the visual test.

## Color changes

All colors live in the `:root` CSS vars in `lecture.html` (`--bg`, `--accent`,
`--accent-2`, `--key`, `--box-fill`, `--box-text`, `--box-line`). The HUD
tracer SVGs use `mask-image` + `background-color: var(--box-line)`, so changing
the var updates the tracer color automatically — no SVG edits needed.

The paper-grain noise in the body bg has its warm-brown tint baked into the
`feColorMatrix` values (R=0.45, G=0.35, B=0.20); change those if you swap to
a cool-toned bg.
