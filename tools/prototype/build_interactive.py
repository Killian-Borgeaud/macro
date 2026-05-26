#!/usr/bin/env python3
"""Prototype: build a self-contained interactive plotly figure from a JSON spec.
Usage: python build_interactive.py <spec.json> <output.html>

The spec defines: parameters, curves (as JS expressions over k and params),
optional markers (e.g. intersection points), and sliders that mutate parameters
on the fly. Output is one HTML file with plotly.js from CDN — no build server.
"""
import json
import sys
from pathlib import Path

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>__TITLE__</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #fafafa; color: #1a1a1a; max-width: 900px; margin: 2rem auto; padding: 1rem; }
  h1 { font-size: 1.3rem; color: #2563eb; margin-bottom: 0.5rem; }
  .plot { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; }
  .sliders { display: grid; gap: 0.8rem; margin: 1.5rem 0; padding: 1rem;
             background: white; border: 1px solid #e0e0e0; border-radius: 8px; }
  .slider-row { display: grid; grid-template-columns: 220px 1fr 80px; align-items: center; gap: 1rem; }
  .slider-row label { font-size: 0.9rem; }
  .slider-row input[type=range] { width: 100%; }
  .slider-row .value { font-family: monospace; text-align: right; color: #2563eb; font-weight: 600; }
  .caption { font-size: 0.9rem; color: #555; line-height: 1.6; padding: 0.8rem 1rem;
             background: #eff6ff; border-left: 3px solid #2563eb; border-radius: 0 6px 6px 0; }
  .reset { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px;
           padding: 0.3rem 0.8rem; cursor: pointer; font-size: 0.85rem; justify-self: start; }
  .reset:hover { background: #e2e8f0; }
  .marker-readout { font-family: monospace; font-size: 0.85rem; color: #111;
                    margin-top: 0.5rem; padding: 0.5rem; background: #fffbeb;
                    border-left: 3px solid #f59e0b; border-radius: 0 4px 4px 0; min-height: 1rem; }
</style>
</head>
<body>

<h1>__TITLE__</h1>

<div id="plot" class="plot" style="height: 500px;"></div>

<div id="readout" class="marker-readout"></div>

<div class="sliders">
__SLIDERS_HTML__
  <button class="reset" id="reset-btn">Reset to defaults</button>
</div>

<p class="caption">__CAPTION__</p>

<script>
const spec = __SPEC_JSON__;
const defaults = JSON.parse(JSON.stringify(spec.params));
const params = JSON.parse(JSON.stringify(spec.params));

const paramNames = Object.keys(spec.params);

// Compile each curve expr to a JS function (k, params) → y
const curveFns = spec.curves.map(c =>
  new Function('k', 'p',
    'const {' + paramNames.join(',') + '} = p; return ' + c.expr + ';'
  )
);

function linspace(a, b, n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push(a + (b - a) * i / (n - 1));
  return out;
}

function findIntersection(xs, y1s, y2s) {
  for (let i = 1; i < xs.length; i++) {
    const d0 = y1s[i-1] - y2s[i-1];
    const d1 = y1s[i] - y2s[i];
    if (d0 === 0) return { x: xs[i-1], y: y1s[i-1] };
    if (d0 * d1 < 0) {
      const t = d0 / (d0 - d1);
      const x = xs[i-1] + t * (xs[i] - xs[i-1]);
      const y = y1s[i-1] + t * (y1s[i] - y1s[i-1]);
      return { x, y };
    }
  }
  return null;
}

function render() {
  const xs = linspace(spec.x_range[0], spec.x_range[1], spec.n_points);
  const curveData = spec.curves.map((c, i) => ({
    x: xs,
    y: xs.map(k => curveFns[i](k, params)),
    name: c.name,
    mode: 'lines',
    line: { color: c.color, width: c.width || 2 }
  }));

  const traces = [...curveData];
  const shapes = [];
  const annotations = [];
  const readoutParts = [];

  for (const m of (spec.markers || [])) {
    if (m.find === 'intersection') {
      const ys1 = curveData[m.curves[0]].y;
      const ys2 = curveData[m.curves[1]].y;
      const pt = findIntersection(xs, ys1, ys2);
      if (pt) {
        traces.push({
          x: [pt.x], y: [pt.y], mode: 'markers',
          marker: { size: 12, color: m.color, line: { color: 'white', width: 2 } },
          name: m.label, showlegend: false,
          hovertemplate: m.label + ' = %{x:.3f}<extra></extra>'
        });
        if (m.guide === 'vertical') {
          shapes.push({
            type: 'line', x0: pt.x, x1: pt.x, y0: 0, y1: pt.y,
            line: { color: '#666', dash: 'dash', width: 1 }
          });
        }
        annotations.push({
          x: pt.x, y: 0, xref: 'x', yref: 'y',
          text: m.label + ' = ' + pt.x.toFixed(2),
          showarrow: false, yshift: -18,
          font: { size: 11, color: '#111' }
        });
        readoutParts.push(m.label + ' = ' + pt.x.toFixed(3) +
                          ', value = ' + pt.y.toFixed(3));
      }
    }
  }

  const layout = {
    xaxis: { title: spec.x_label, gridcolor: '#eee' },
    yaxis: { title: spec.y_label, gridcolor: '#eee' },
    shapes: shapes,
    annotations: annotations,
    margin: { t: 20, r: 20, b: 60, l: 60 },
    legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.8)' },
    plot_bgcolor: 'white', paper_bgcolor: 'white'
  };

  Plotly.react('plot', traces, layout, { responsive: true, displayModeBar: false });
  document.getElementById('readout').textContent = readoutParts.join(' | ');
}

for (const s of spec.sliders) {
  const slider = document.getElementById('slider-' + s.param);
  const valSpan = document.getElementById('val-' + s.param);
  slider.addEventListener('input', e => {
    params[s.param] = parseFloat(e.target.value);
    valSpan.textContent = params[s.param].toFixed(s.decimals);
    render();
  });
}

document.getElementById('reset-btn').addEventListener('click', () => {
  Object.assign(params, JSON.parse(JSON.stringify(defaults)));
  for (const s of spec.sliders) {
    document.getElementById('slider-' + s.param).value = defaults[s.param];
    document.getElementById('val-' + s.param).textContent = defaults[s.param].toFixed(s.decimals);
  }
  render();
});

render();
</script>

</body>
</html>
"""


def build_slider_row(s, default_val):
    return (
        '  <div class="slider-row">\n'
        f'    <label for="slider-{s["param"]}">{s["label"]}</label>\n'
        f'    <input type="range" id="slider-{s["param"]}" '
        f'min="{s["min"]}" max="{s["max"]}" step="{s["step"]}" value="{default_val}">\n'
        f'    <span class="value">= <span id="val-{s["param"]}">'
        f'{default_val:.{s["decimals"]}f}</span></span>\n'
        '  </div>'
    )


def build(spec_path: str, out_path: str) -> str:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    sliders_html = "\n".join(
        build_slider_row(s, spec["params"][s["param"]]) for s in spec.get("sliders", [])
    )
    html = (HTML
            .replace("__TITLE__", spec["title"])
            .replace("__CAPTION__", spec["caption"])
            .replace("__SLIDERS_HTML__", sliders_html)
            .replace("__SPEC_JSON__", json.dumps(spec)))
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    print(f"Built: {build(sys.argv[1], sys.argv[2])}")
