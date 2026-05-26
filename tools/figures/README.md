# Interactive Figure Spec Format

Specs are JSON files in `tools/figures/library/` (reusable) or inline in a lecture payload's `interactive_figures` array. `tools/build_figure.py` renders them to plotly HTML snippets. `tools/build_lecture.py` embeds those snippets where a `<div data-figure='ID'></div>` placeholder appears.

## Contents
- Top-level spec fields
- Panels (single or linked side-by-side)
- Curve types (expr, time_series, piecewise)
- Marker types (9 kinds)
- Sliders
- Style conventions
- Common patterns / mistakes

---

## Top-level fields

```jsonc
{
  "id": "fig-solow",                        // kebab-case, "fig-" prefix
  "title": "Figure. Title",                 // shown above plot
  "caption": "What to NOTICE.",             // shown below plot, in callout
  "params": {"a": 1, "b": 0.5},             // initial parameter values
  "sliders": [...],                          // parameters made interactive
  "panels": [...]                            // 1 or 2 panels
}
```

Either `panels` (preferred) or the legacy single-panel fields (`curves`, `markers`, `x_range`, `x_label`, `y_label`, `n_points`) at the top level. Always prefer `panels`.

---

## Panels

```jsonc
"panels": [
  {
    "id": "panel-1",                        // optional, kebab-case
    "title": "Optional small title above panel",
    "x_range": [0.1, 80],                   // required for `expr` and `piecewise` curves
    "n_points": 200,                        // default 200
    "x_label": "capital per worker, k",
    "y_label": "per worker",
    "curves": [...],
    "markers": [...]
  }
]
```

**Linked panels** (side-by-side): put two panel objects in `panels`. They share sliders and re-render together on any slider change. Use only when the two views genuinely complement each other (Solow + transition; level + growth rate; before + after). Don't pad with a second panel for symmetry.

---

## Curve types

The x-axis variable is always called `k` inside expressions (regardless of what it conceptually represents — `s` in the golden-rule example, `t` in time series).

### `expr` — continuous function

```jsonc
{
  "type": "expr",
  "name": "s·f(k)",                          // legend label
  "expr": "s * B * Math.pow(k, alpha)",      // JS expression in `k` and params
  "color": "#2563eb",
  "width": 3,                                // optional, default 2
  "dash": "solid"                            // "solid" | "dash" | "dot"
}
```

The expression has access to `k` (the x-axis value) and all params by name. Uses JavaScript syntax (`Math.pow`, `Math.exp`, `Math.log`, `Math.sqrt`, etc.).

### `time_series` — discrete iteration

```jsonc
{
  "type": "time_series",
  "name": "k_t",
  "initial": "k0",                           // scalar expr in params (no `k`)
  "recursion": "(s * B * Math.pow(k, alpha) + (1 - delta) * k) / (1 + n)",
  "t_range": [0, 100],                       // [t_start, t_end], step 1
  "color": "#2563eb",
  "width": 3
}
```

The recursion expression: given current `k`, returns next `k`. Initial value is computed once from params (`k` is not available in `initial`).

`x_range` on the panel is ignored for time_series — t_range governs the x-axis.

### `piecewise` — different expr per x-range

```jsonc
{
  "type": "piecewise",
  "name": "f(k)",
  "pieces": [
    {"when": "k < 10", "expr": "0"},
    {"when": "k < 50", "expr": "0.5 * k"},
    {"expr": "25 + 0.1 * k"}                 // final piece, no `when`, is the fallthrough
  ],
  "color": "#dc2626"
}
```

---

## Marker types

All markers can have `label` (string shown in legend/annotation) and `color` (hex).

### `intersection` — where two curves cross

```jsonc
{"type": "intersection", "label": "k*", "curves": [0, 1], "guide": "vertical"}
```
- `curves`: indices into the panel's `curves` array.
- `guide`: `"vertical"`, `"horizontal"`, `"both"`, or omit for no guide line.
- Numerically finds the first sign-change of `curves[0] - curves[1]`.

### `maximum` / `minimum` — extremum of a curve

```jsonc
{"type": "maximum", "label": "s**", "curve": 0, "guide": "vertical"}
```
- `curve`: single index. Searches the curve's sampled points.

### `vertical_line` / `horizontal_line` — at a value

```jsonc
{"type": "vertical_line", "label": "k_target", "at": "20", "dash": "dash"}
{"type": "horizontal_line", "label": "k*", "at": "Math.pow(s/(n+delta), 1/(1-alpha))"}
```
- `at`: scalar expression in params (no `k`). Number or string both OK.

### `tangent_line` — line tangent to a curve at a point

```jsonc
{"type": "tangent_line", "label": "MPK at k0", "curve": 0, "at": "k0", "color": "#16a34a"}
```
- Numerically slope at the point. Drawn across panel x_range.
- Useful for marginal-product diagrams.

### `asymptote` — horizontal line at the curve's limit value

```jsonc
{"type": "asymptote", "label": "→ 1", "curve": 0}
```
- Evaluates curve at `k = 1e9`.

### `area` — shaded region between two curves

```jsonc
{"type": "area", "label": "Total saving", "curves": [0, 1], "color": "rgba(37,99,235,0.15)"}
```
- Spans the panel's x_range.

### `label_point` — annotated dot at a specific (x, y)

```jsonc
{"type": "label_point", "label": "K=L=10", "x": "10", "y": "10"}
```
- `x`, `y`: scalar expressions in params.

---

## Sliders

```jsonc
"sliders": [
  {
    "param": "s",                            // must exist in `params`
    "min": 0.05, "max": 0.50, "step": 0.01,
    "label": "saving rate s",
    "decimals": 2                            // for value display
  }
]
```

Sliders mutate the params object and trigger a full re-render of all panels. A "Reset to defaults" button is always rendered when sliders are present.

---

## Style conventions

- **Palette:** `#2563eb` blue (primary curve), `#dc2626` red (counter / break-even), `#16a34a` green (third / 45°-style), `#666` (axes/guides), `#111` (points), `#94a3b8` (asymptotes).
- **Widths:** `3` for important curves, `2` for secondary, `1` for guides.
- **Dashes:** `solid` (default), `dash` (45° lines, asymptotes), `dot` (tangents).
- **Captions** explain what to NOTICE, not just label axes ("Drag s and watch k* migrate right" beats "Solow diagram").

---

## Common patterns

| Pattern | When | How |
|---|---|---|
| Single Solow-style intersection | One curve, one line, one fixed point | 1 panel, 2 `expr` curves, 1 `intersection` marker |
| Comparative statics (shift) | Show what changes when a param moves | 1 panel, 2 curves, slider on the shifting param — user sees the curve move and the intersection re-find itself |
| Linked geometric + dynamic | Solow diagram + transition diagram | 2 panels, shared sliders |
| Time path to steady state | Show convergence dynamics | 1 panel, 1 `time_series` curve, 1 `horizontal_line` marker for k* |
| Hill-shaped optimum | Golden rule, Laffer curve, etc. | 1 panel, 1 `expr` curve, 1 `maximum` marker with guide |
| Before/after comparison | Two regimes (autarky/open, low/high tax) | 2 panels — each panel renders one regime — sliders for shared parameters |

## Common mistakes

- Using `k` as x-axis but writing `s` in the expression — the runtime sees `s` as a param, not the axis variable. Always write `k` for the x-axis even if it conceptually represents `s`, `t`, or anything else.
- Putting JS bigger than a one-liner inside an `expr` — split into multiple curves or use a piecewise.
- Forgetting `Math.` prefix on `pow`, `log`, `exp`, `sqrt` — JS requires it.
- Slider `step` too small for a long range (e.g. 100 steps across [0, 1]) → laggy re-renders. Aim for ~50 discrete positions.
- Two panels that show essentially the same thing — defeats the purpose of linked panels.
