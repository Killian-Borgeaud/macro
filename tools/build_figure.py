#!/usr/bin/env python3
"""Build an interactive plotly figure from a JSON spec.

Two modes:
  python build_figure.py <spec.json> <output.html>           # standalone page
  python build_figure.py --snippet <spec.json> <output.html> # embeddable snippet

The standalone page is self-contained (plotly.js from CDN, full styles).
The snippet is a <div> + <script> for embedding inside a larger HTML document
that already loads plotly.js. The lecture template loads plotly.js once and
embeds many figure snippets per lecture.

Spec format documented in tools/figures/README.md.
Spec examples in tools/figures/library/.
"""
import json
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# JavaScript runtime (embedded in every figure snippet / standalone page)
# ─────────────────────────────────────────────────────────────────────────────
# This JS is the renderer that interprets the spec at runtime. It is the same
# code for every figure — we only inline it once per HTML document (the build
# script dedupes), and each figure instance calls renderFigure(spec, hostId).

RUNTIME_JS = r"""
window.MacroFigures = window.MacroFigures || (function() {

  function linspace(a, b, n) {
    const out = [];
    for (let i = 0; i < n; i++) out.push(a + (b - a) * i / (n - 1));
    return out;
  }

  function compileExpr(expr, paramNames) {
    return new Function('k', 'p',
      'const {' + paramNames.join(',') + '} = p; return ' + expr + ';');
  }

  function compileScalarExpr(expr, paramNames) {
    if (typeof expr === 'number') return () => expr;
    if (typeof expr === 'string') {
      return new Function('p',
        'const {' + paramNames.join(',') + '} = p; return ' + expr + ';');
    }
    return () => null;
  }

  function findIntersection(xs, y1s, y2s) {
    for (let i = 1; i < xs.length; i++) {
      const d0 = y1s[i-1] - y2s[i-1];
      const d1 = y1s[i] - y2s[i];
      if (d0 === 0) return { x: xs[i-1], y: y1s[i-1] };
      if (d0 * d1 < 0) {
        const t = d0 / (d0 - d1);
        return {
          x: xs[i-1] + t * (xs[i] - xs[i-1]),
          y: y1s[i-1] + t * (y1s[i] - y1s[i-1])
        };
      }
    }
    return null;
  }

  function findExtremum(xs, ys, kind) {
    let idx = 0;
    for (let i = 1; i < ys.length; i++) {
      if (kind === 'max' ? ys[i] > ys[idx] : ys[i] < ys[idx]) idx = i;
    }
    return { x: xs[idx], y: ys[idx] };
  }

  function buildCurveData(curve, xs, params, paramNames) {
    if (curve.type === 'time_series') {
      // Discrete recursion: k_{t+1} = recursion(k_t, p), starting from initial.
      const T = (curve.t_range && curve.t_range[1]) || 50;
      const t0 = (curve.t_range && curve.t_range[0]) || 0;
      const initFn = compileScalarExpr(curve.initial, paramNames);
      const recFn = new Function('k', 'p',
        'const {' + paramNames.join(',') + '} = p; return ' + curve.recursion + ';');
      const ts = [t0], ks = [initFn(params)];
      for (let t = t0 + 1; t <= T; t++) {
        ks.push(recFn(ks[ks.length - 1], params));
        ts.push(t);
      }
      return { x: ts, y: ks };
    }
    if (curve.type === 'piecewise') {
      // [{when: "k < 10", expr: "..."}], else expr at end
      const fns = curve.pieces.map(p => ({
        when: p.when ? new Function('k', 'p',
          'const {' + paramNames.join(',') + '} = p; return ' + p.when + ';') : null,
        fn: compileExpr(p.expr, paramNames)
      }));
      return {
        x: xs,
        y: xs.map(k => {
          for (const piece of fns) {
            if (!piece.when || piece.when(k, params)) return piece.fn(k, params);
          }
          return null;
        })
      };
    }
    // default: type === 'expr'
    const fn = compileExpr(curve.expr, paramNames);
    return { x: xs, y: xs.map(k => fn(k, params)) };
  }

  function buildPanel(panel, params, paramNames, panelHostId) {
    let xs;
    // For panels containing only time_series curves, x_range may be omitted.
    if (panel.x_range) {
      xs = linspace(panel.x_range[0], panel.x_range[1], panel.n_points || 200);
    } else {
      xs = [];
    }

    const curveData = panel.curves.map(c => buildCurveData(c, xs, params, paramNames));

    const traces = panel.curves.map((c, i) => ({
      x: curveData[i].x, y: curveData[i].y,
      name: c.name, mode: c.mode || 'lines',
      line: { color: c.color, width: c.width || 1.6, dash: c.dash || 'solid' },
      marker: { size: c.marker_size || 5, color: c.color, line: { color: 'white', width: 1 } }
    }));

    const shapes = [];
    const annotations = [];
    const readoutParts = [];

    for (const m of (panel.markers || [])) {
      let pt = null;
      let line = null;

      if (m.type === 'intersection') {
        pt = findIntersection(curveData[m.curves[0]].x, curveData[m.curves[0]].y, curveData[m.curves[1]].y);
      } else if (m.type === 'maximum' || m.type === 'minimum') {
        const kind = m.type === 'maximum' ? 'max' : 'min';
        pt = findExtremum(curveData[m.curve].x, curveData[m.curve].y, kind);
      } else if (m.type === 'vertical_line') {
        const x = compileScalarExpr(m.at, paramNames)(params);
        line = { type: 'line', x0: x, x1: x, yref: 'paper', y0: 0, y1: 1,
                 line: { color: m.color || '#5a7378', dash: m.dash || 'dash', width: 1 } };
        if (m.label) annotations.push({
          x: x, y: 0, xref: 'x', yref: 'paper', text: m.label,
          showarrow: false, yshift: -18, font: { size: 11, color: '#111' }
        });
      } else if (m.type === 'horizontal_line') {
        const y = compileScalarExpr(m.at, paramNames)(params);
        line = { type: 'line', y0: y, y1: y, xref: 'paper', x0: 0, x1: 1,
                 line: { color: m.color || '#5a7378', dash: m.dash || 'dash', width: 1 } };
        if (m.label) annotations.push({
          x: 1, y: y, xref: 'paper', yref: 'y', text: m.label,
          showarrow: false, xshift: -8, yshift: -8, font: { size: 11, color: '#111' }
        });
      } else if (m.type === 'tangent_line') {
        const x0 = compileScalarExpr(m.at, paramNames)(params);
        const fn = compileExpr(panel.curves[m.curve].expr, paramNames);
        const h = Math.max(0.001, Math.abs(x0) * 0.001);
        const slope = (fn(x0 + h, params) - fn(x0 - h, params)) / (2 * h);
        const y0v = fn(x0, params);
        const xMin = panel.x_range[0], xMax = panel.x_range[1];
        traces.push({
          x: [xMin, xMax],
          y: [y0v + slope * (xMin - x0), y0v + slope * (xMax - x0)],
          mode: 'lines', name: m.label || 'tangent',
          line: { color: m.color || '#16a34a', dash: 'dot', width: 2 }, showlegend: !!m.label
        });
        pt = { x: x0, y: y0v };
      } else if (m.type === 'asymptote') {
        const fn = compileExpr(panel.curves[m.curve].expr, paramNames);
        const yInf = fn(1e9, params);
        line = { type: 'line', y0: yInf, y1: yInf, xref: 'paper', x0: 0, x1: 1,
                 line: { color: m.color || '#94a3b8', dash: 'dot', width: 1 } };
        if (m.label) annotations.push({
          x: 0.98, y: yInf, xref: 'paper', yref: 'y', text: m.label,
          showarrow: false, xanchor: 'right', yshift: -8, font: { size: 11, color: '#666' }
        });
      } else if (m.type === 'area') {
        // Shaded region between curves[0] and curves[1]
        const ys1 = curveData[m.curves[0]].y;
        const ys2 = curveData[m.curves[1]].y;
        traces.push({
          x: [...curveData[m.curves[0]].x, ...curveData[m.curves[0]].x.slice().reverse()],
          y: [...ys1, ...ys2.slice().reverse()],
          fill: 'toself', fillcolor: m.color || 'rgba(37,99,235,0.15)',
          line: { width: 0 }, name: m.label || 'area', hoverinfo: 'skip',
          showlegend: !!m.label
        });
      } else if (m.type === 'label_point') {
        const x = compileScalarExpr(m.x, paramNames)(params);
        const y = compileScalarExpr(m.y, paramNames)(params);
        pt = { x, y };
      }

      if (pt) {
        const pointTrace = {
          x: [pt.x], y: [pt.y], mode: 'markers',
          marker: { size: 8, color: m.color || '#003135', line: { color: 'white', width: 1.5 } },
          name: m.label, showlegend: false,
          hovertemplate: (m.label ? m.label + ' = ' : '') + '(%{x:.3f}, %{y:.3f})<extra></extra>'
        };
        // label_point markers render the label TEXT next to the dot; other marker
        // types (intersection, max/min) write their label via annotations / guides.
        if (m.type === 'label_point' && m.label) {
          pointTrace.mode = 'markers+text';
          pointTrace.text = [m.label];
          pointTrace.textposition = m.textposition || 'top right';
          pointTrace.textfont = {
            size: 13, color: m.color || '#003135',
            family: 'JetBrains Mono, ui-monospace, monospace', weight: 700
          };
        }
        traces.push(pointTrace);
        if (m.guide === 'vertical') {
          shapes.push({ type: 'line', x0: pt.x, x1: pt.x, y0: 0, y1: pt.y,
                        line: { color: '#5a7378', dash: 'dash', width: 1 } });
        } else if (m.guide === 'horizontal') {
          shapes.push({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: pt.y, y1: pt.y,
                        line: { color: '#5a7378', dash: 'dash', width: 1 } });
        } else if (m.guide === 'both') {
          shapes.push({ type: 'line', x0: pt.x, x1: pt.x, y0: 0, y1: pt.y,
                        line: { color: '#5a7378', dash: 'dash', width: 1 } });
          shapes.push({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: pt.y, y1: pt.y,
                        line: { color: '#5a7378', dash: 'dash', width: 1 } });
        }
        if (m.label && m.guide === 'vertical') annotations.push({
          x: pt.x, y: 0, xref: 'x', yref: 'y', text: m.label + ' = ' + pt.x.toFixed(2),
          showarrow: false, yshift: -18, font: { size: 11, color: '#111' }
        });
        readoutParts.push(panel.id + ': ' + (m.label || '?') +
                          ' = ' + pt.x.toFixed(3) + ', y = ' + pt.y.toFixed(3));
      }
      if (line) shapes.push(line);
    }

    const layout = {
      font: { family: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
              color: '#003135', size: 12 },
      xaxis: { title: { text: panel.x_label, font: { size: 12, color: '#5a7378' } },
               gridcolor: '#e6eef0', zerolinecolor: '#d4e1e4', linecolor: '#d4e1e4',
               tickfont: { color: '#5a7378', size: 11 } },
      yaxis: { title: { text: panel.y_label, font: { size: 12, color: '#5a7378' } },
               gridcolor: '#e6eef0', zerolinecolor: '#d4e1e4', linecolor: '#d4e1e4',
               tickfont: { color: '#5a7378', size: 11 } },
      shapes: shapes, annotations: annotations,
      margin: { t: 28, r: 20, b: 50, l: 60 },
      title: panel.title ? { text: panel.title, font: { size: 13, color: '#024950' } } : undefined,
      legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.9)',
                bordercolor: '#d4e1e4', borderwidth: 1, font: { size: 11, color: '#003135' } },
      plot_bgcolor: '#ffffff', paper_bgcolor: '#ffffff'
    };

    Plotly.react(panelHostId, traces, layout, { responsive: true, displayModeBar: false });
    return readoutParts;
  }

  function renderFigure(spec, hostId) {
    const root = document.getElementById(hostId);
    if (!root) { console.warn('Figure host not found:', hostId); return; }
    const paramNames = Object.keys(spec.params);
    const defaults = JSON.parse(JSON.stringify(spec.params));
    const params = JSON.parse(JSON.stringify(spec.params));

    const panels = spec.panels || [{
      id: 'main', x_range: spec.x_range, n_points: spec.n_points,
      x_label: spec.x_label, y_label: spec.y_label,
      curves: spec.curves, markers: spec.markers
    }];

    function renderAll() {
      const readoutLines = [];
      panels.forEach((p, i) => {
        const lines = buildPanel(p, params, paramNames, hostId + '-panel-' + i);
        readoutLines.push(...lines);
      });
      const readoutEl = root.querySelector('.mf-readout');
      if (readoutEl) readoutEl.textContent = readoutLines.join('   |   ');
    }

    // Wire sliders
    (spec.sliders || []).forEach(s => {
      const sl = root.querySelector('[data-slider="' + s.param + '"]');
      const vsp = root.querySelector('[data-value="' + s.param + '"]');
      if (sl) sl.addEventListener('input', e => {
        params[s.param] = parseFloat(e.target.value);
        if (vsp) vsp.textContent = params[s.param].toFixed(s.decimals || 2);
        renderAll();
      });
    });

    // Reset button
    const resetBtn = root.querySelector('.mf-reset');
    if (resetBtn) resetBtn.addEventListener('click', () => {
      Object.assign(params, JSON.parse(JSON.stringify(defaults)));
      (spec.sliders || []).forEach(s => {
        const sl = root.querySelector('[data-slider="' + s.param + '"]');
        const vsp = root.querySelector('[data-value="' + s.param + '"]');
        if (sl) sl.value = defaults[s.param];
        if (vsp) vsp.textContent = defaults[s.param].toFixed(s.decimals || 2);
      });
      renderAll();
    });

    renderAll();
  }

  return { renderFigure };
})();
"""


# ─────────────────────────────────────────────────────────────────────────────
# CSS for figures (also dedupe-able — emit once per document)
# ─────────────────────────────────────────────────────────────────────────────
RUNTIME_CSS = """
.mf-figure { margin: 1.75rem 0; padding: 1.25rem; background: #ffffff;
             border: 1px solid #b8dcd9; border-radius: 0; }
.mf-figure h4 { margin: 0 0 0.8rem 0; font-size: 1rem; font-weight: 600;
                color: #024950; letter-spacing: -0.01em; }
.mf-panels { display: grid; gap: 1rem; }
.mf-panels.cols-2 { grid-template-columns: 1fr 1fr; }
@media (max-width: 720px) { .mf-panels.cols-2 { grid-template-columns: 1fr; } }
.mf-panel { min-height: 380px; }
.mf-sliders { display: grid; gap: 0.35rem; margin-top: 1.25rem; padding: 0;
              background: transparent; border: none; }
.mf-slider-row { display: grid; grid-template-columns: 160px 1fr 70px;
                 align-items: center; gap: 0.9rem; }
.mf-slider-row label { font-size: 0.76rem; color: #5a7378; font-weight: 400;
                       letter-spacing: 0.01em; }
.mf-slider-row input[type=range] {
  -webkit-appearance: none; appearance: none;
  width: 100%; height: 16px; background: transparent; margin: 0; padding: 0;
  cursor: pointer;
}
.mf-slider-row input[type=range]::-webkit-slider-runnable-track {
  height: 1px; background: #b8dcd9; border: none;
}
.mf-slider-row input[type=range]::-moz-range-track {
  height: 1px; background: #b8dcd9; border: none;
}
.mf-slider-row input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  height: 9px; width: 9px; border-radius: 50%;
  background: #0FA4AF; border: none; margin-top: -4px;
  cursor: pointer; transition: transform .12s, background .12s;
}
.mf-slider-row input[type=range]::-moz-range-thumb {
  height: 9px; width: 9px; border-radius: 50%;
  background: #0FA4AF; border: none;
  cursor: pointer; transition: transform .12s, background .12s;
}
.mf-slider-row input[type=range]:hover::-webkit-slider-thumb {
  background: #024950; transform: scale(1.25);
}
.mf-slider-row input[type=range]:hover::-moz-range-thumb {
  background: #024950; transform: scale(1.25);
}
.mf-slider-row .mf-value { font-family: 'JetBrains Mono', ui-monospace, monospace;
                           text-align: right; color: #024950; font-weight: 400;
                           font-size: 0.76rem; }
.mf-slider-row .mf-value::before { content: ''; }
.mf-reset { background: transparent; border: none;
            padding: 0.35rem 0; margin-top: 0.4rem; cursor: pointer; font-size: 0.72rem;
            color: #5a7378; justify-self: start; letter-spacing: 0.05em;
            text-transform: uppercase; font-family: inherit;
            border-bottom: 1px solid transparent; transition: color .15s, border-color .15s; }
.mf-reset:hover { color: #024950; border-bottom-color: #0FA4AF; }
.mf-readout { font-family: 'JetBrains Mono', ui-monospace, monospace;
              font-size: 0.74rem; color: #964734; font-weight: 400;
              margin-top: 0.6rem; padding: 0.4rem 0;
              border-top: 1px dashed #b8dcd9; min-height: 1rem;
              letter-spacing: 0.01em; }
.mf-caption { font-size: 0.84rem; color: #5a7378; line-height: 1.6;
              margin-top: 1rem; padding: 0.75rem 0 0;
              border-top: 1px solid #b8dcd9; }
.mf-caption strong { color: #024950; font-weight: 600; letter-spacing: 0.01em; }
"""


def _build_slider_row(s, default_val):
    decimals = s.get("decimals", 2)
    return (
        '<div class="mf-slider-row">'
        f'<label>{s["label"]}</label>'
        f'<input type="range" data-slider="{s["param"]}" '
        f'min="{s["min"]}" max="{s["max"]}" step="{s["step"]}" value="{default_val}">'
        f'<span class="mf-value">= <span data-value="{s["param"]}">'
        f'{default_val:.{decimals}f}</span></span>'
        '</div>'
    )


def _safe_id(s: str) -> str:
    return "".join(c if c.isalnum() or c == "-" else "-" for c in s)


def build_snippet(spec: dict) -> str:
    """Return an HTML snippet (div + script) ready to embed.

    The caller must ensure plotly.js, RUNTIME_CSS, and RUNTIME_JS are loaded
    elsewhere on the page (e.g. in the lecture template head).
    """
    fig_id = _safe_id(spec["id"])
    panels = spec.get("panels") or [{}]  # default to 1 panel for backward compat
    n_panels = len(panels)
    cols_class = "cols-2" if n_panels == 2 else ""

    panel_divs = "".join(
        f'<div id="{fig_id}-panel-{i}" class="mf-panel"></div>'
        for i in range(n_panels)
    )
    sliders_html = "".join(
        _build_slider_row(s, spec["params"][s["param"]])
        for s in spec.get("sliders", [])
    )
    sliders_block = (
        f'<div class="mf-sliders">{sliders_html}'
        '<button type="button" class="mf-reset">Reset to defaults</button></div>'
        if sliders_html else ''
    )
    caption_block = (
        f'<p class="mf-caption"><strong>{spec.get("title", "")}.</strong> '
        f'{spec["caption"]}</p>' if spec.get("caption") else ''
    )

    spec_json = json.dumps(spec)
    # Defensive: wait for DOMContentLoaded so the runtime + Plotly are guaranteed
    # to be parsed. Also surface a visible error in the figure container if either
    # is missing — silent failure was the original bug.
    init_js = (
        '(function(){'
        f'var spec={spec_json};var hostId="{fig_id}";'
        'function go(){'
        'if(!window.MacroFigures){'
        f'document.getElementById(hostId).insertAdjacentHTML("afterbegin",'
        '"<div style=\\"color:#dc2626;padding:1rem;border:2px dashed #dc2626\\">'
        'Runtime missing: window.MacroFigures not defined. Did FIGURE_JS load before this snippet?</div>");return;}'
        'if(!window.Plotly){'
        f'document.getElementById(hostId).insertAdjacentHTML("afterbegin",'
        '"<div style=\\"color:#dc2626;padding:1rem;border:2px dashed #dc2626\\">'
        'Runtime missing: window.Plotly not loaded.</div>");return;}'
        'try{window.MacroFigures.renderFigure(spec,hostId);}'
        'catch(e){'
        f'document.getElementById(hostId).insertAdjacentHTML("afterbegin",'
        '"<div style=\\"color:#dc2626;padding:1rem;border:2px dashed #dc2626\\">'
        'Render error: "+e.message+"</div>");}'
        '}'
        'if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",go);}'
        'else{go();}'
        '})();'
    )
    return (
        f'<div class="mf-figure" id="{fig_id}">'
        f'<div class="mf-panels {cols_class}">{panel_divs}</div>'
        f'<div class="mf-readout"></div>'
        f'{sliders_block}'
        f'{caption_block}'
        f'<script>{init_js}</script>'
        '</div>'
    )


def build_standalone(spec: dict) -> str:
    """Return a full standalone HTML page (plotly + CSS + runtime inlined)."""
    snippet = build_snippet(spec)
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        f'<title>{spec.get("title", "Figure")}</title>'
        '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
        f'<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;'
        'background:#fafafa;color:#1a1a1a;max-width:1100px;margin:2rem auto;padding:1rem;}'
        'h1{font-size:1.3rem;color:#2563eb;margin-bottom:0.5rem;}'
        f'{RUNTIME_CSS}</style></head><body>'
        f'<h1>{spec.get("title", "Figure")}</h1>'
        f'<script>{RUNTIME_JS}</script>'
        f'{snippet}'
        '</body></html>'
    )


def main():
    args = sys.argv[1:]
    snippet_mode = False
    if args and args[0] == "--snippet":
        snippet_mode = True
        args = args[1:]
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)
    spec_path, out_path = args
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    html = build_snippet(spec) if snippet_mode else build_standalone(spec)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Built: {out}")


if __name__ == "__main__":
    main()
