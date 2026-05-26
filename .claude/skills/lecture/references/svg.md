# SVG Templates — Lecture Figures

Reusable inline SVG patterns beyond the basic axis-curve in `SKILL.md`. Copy a template and adapt coordinates/labels.

All templates assume:
- `viewBox='0 0 400 260'` for 2D plots; `'0 0 400 320'` for taller comparisons
- Single-quoted attributes (JSON-safe)
- Palette: `#2563eb` blue, `#dc2626` red, `#16a34a` green, `#333` axes, `#666` dashed guides, `#111` points
- Wrap in `<div class='figure' id='fig-...'>` + `<figcaption><strong>Figure N.</strong> ...`

---

## Template 1: Phase / transition diagram (k_{t+1} vs k_t with 45° line)

Useful for: convergence to steady state, cobweb dynamics, fixed-point arguments.

```html
<svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'>
  <line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='280' y2='40' stroke='#666' stroke-dasharray='4,4'/>
  <path d='M 40 200 Q 150 60 380 50' fill='none' stroke='#2563eb' stroke-width='2'/>
  <circle cx='205' cy='86' r='4' fill='#111'/>
  <text x='205' y='80'>k*</text>
  <text x='285' y='38'>45°</text>
  <text x='320' y='65' fill='#2563eb'>k_{t+1}(k_t)</text>
  <text x='180' y='252'>k_t</text>
  <text x='10' y='40' transform='rotate(-90 15 40)'>k_{t+1}</text>
</svg>
```

---

## Template 2: Shifted-curve comparative statics

Useful for: ↑savings rate, ↑population growth, ↑technology — anything that shifts one curve and produces a new equilibrium.

```html
<svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'>
  <line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/>
  <path d='M 40 220 Q 150 110 380 80' fill='none' stroke='#2563eb' stroke-width='2' opacity='0.4'/>
  <path d='M 40 220 Q 150 60 380 40' fill='none' stroke='#2563eb' stroke-width='2'/>
  <line x1='40' y1='220' x2='380' y2='60' stroke='#dc2626' stroke-width='2'/>
  <circle cx='180' cy='148' r='4' fill='#111' opacity='0.4'/>
  <circle cx='250' cy='126' r='4' fill='#111'/>
  <line x1='180' y1='148' x2='180' y2='220' stroke='#666' stroke-dasharray='3,3' opacity='0.4'/>
  <line x1='250' y1='126' x2='250' y2='220' stroke='#666' stroke-dasharray='3,3'/>
  <text x='173' y='235' opacity='0.5'>k*</text>
  <text x='246' y='235'>k**</text>
  <text x='285' y='95' fill='#2563eb' opacity='0.5'>s f(k) old</text>
  <text x='285' y='55' fill='#2563eb'>s' f(k)</text>
  <text x='325' y='95' fill='#dc2626'>(n+δ)k</text>
</svg>
```

Pattern: faded old curve + bold new curve + faded old equilibrium point + bold new equilibrium point. Use `opacity='0.4'` for the "before" state.

---

## Template 3: Hill-shaped curve (e.g. Golden Rule c*(s))

```html
<svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'>
  <line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/>
  <path d='M 40 220 Q 160 30 380 220' fill='none' stroke='#16a34a' stroke-width='2'/>
  <circle cx='200' cy='66' r='4' fill='#111'/>
  <line x1='200' y1='66' x2='200' y2='220' stroke='#666' stroke-dasharray='3,3'/>
  <text x='190' y='235'>s** = α</text>
  <text x='180' y='252'>savings rate, s</text>
  <text x='10' y='40' transform='rotate(-90 15 40)'>consumption c*</text>
</svg>
```

---

## Template 4: Multiple paths to same steady state (convergence)

Useful for: two economies starting at different $k_0$, both → $k^*$.

```html
<svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'>
  <line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='100' x2='380' y2='100' stroke='#666' stroke-dasharray='4,4'/>
  <text x='10' y='105'>k*</text>
  <path d='M 60 200 Q 200 130 380 102' fill='none' stroke='#2563eb' stroke-width='2'/>
  <path d='M 60 30 Q 200 80 380 98' fill='none' stroke='#dc2626' stroke-width='2'/>
  <text x='65' y='195' fill='#2563eb'>poor country (low k_0)</text>
  <text x='65' y='25' fill='#dc2626'>rich country (high k_0)</text>
  <text x='180' y='252'>time</text>
  <text x='10' y='40' transform='rotate(-90 15 40)'>capital per worker k</text>
</svg>
```

---

## Template 5: Comparison bars (cross-country, factor shares, etc.)

Useful for: stylized fact 6 (labour share across countries), Lorenz-style approximations.

```html
<svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'>
  <line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/>
  <rect x='70' y='80' width='40' height='140' fill='#2563eb'/>
  <rect x='130' y='100' width='40' height='120' fill='#2563eb'/>
  <rect x='190' y='70' width='40' height='150' fill='#2563eb'/>
  <rect x='250' y='90' width='40' height='130' fill='#2563eb'/>
  <rect x='310' y='110' width='40' height='110' fill='#2563eb'/>
  <text x='75' y='235'>US</text>
  <text x='135' y='235'>UK</text>
  <text x='195' y='235'>DE</text>
  <text x='258' y='235'>FR</text>
  <text x='318' y='235'>JP</text>
  <text x='10' y='40' transform='rotate(-90 15 40)'>labour share, wL/Y</text>
</svg>
```

---

## Template 6: Lorenz curve

Useful for: inequality discussions, distributional facts.

```html
<svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'>
  <line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/>
  <line x1='40' y1='220' x2='380' y2='20' stroke='#666' stroke-dasharray='4,4'/>
  <path d='M 40 220 Q 250 215 380 20' fill='none' stroke='#2563eb' stroke-width='2'/>
  <text x='280' y='40'>perfect equality</text>
  <text x='200' y='180' fill='#2563eb'>actual</text>
  <text x='180' y='252'>cumulative population %</text>
  <text x='10' y='40' transform='rotate(-90 15 40)'>cumulative income %</text>
</svg>
```

---

## Tips

- **Coordinates:** with `viewBox='0 0 400 260'`, the drawable area is x ∈ [40, 380], y ∈ [20, 220] (leaving margins for axes and labels). Origin in browser space is top-left; lower y = higher up on screen.
- **Concave curve:** quadratic Bezier `Q ctrl_x ctrl_y end_x end_y`. Pull `ctrl_y` toward the top of the viewBox for steeper concavity.
- **Multiple curves on one diagram:** draw them in order back-to-front. Use `opacity` on older/faded elements.
- **Labels:** keep them inside the viewBox; estimate width as ~6px per character at font-size 12.
- **No JavaScript:** SVGs are static. No animation, no interaction, no tooltips.
