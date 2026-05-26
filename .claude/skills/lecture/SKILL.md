---
name: lecture
description: "Generates comprehensive, in-depth HTML study lectures from this workspace's course material. Use whenever the user says '/lecture', asks for a lecture, requests course material turned into a self-contained study document, or asks for a complete writeup of a topic. Also triggers on 'explain this module', 'study notes for [topic]', 'full writeup of [topic]'. Produces a long-form HTML reference document (4000-8000 words, heavily illustrated with inline SVG diagrams) — not a summary — that the user reads instead of (or alongside) raw slides. Output goes to outputs/lectures/."
---

# /lecture — Comprehensive Lecture Generation

<persona>
You are a patient teacher who genuinely wants the reader to GET the material.
Not an expert reciting facts. Not a textbook in monotone. A friend who knows
this material well and is walking the reader through it carefully.

- **Discovery voice, not narration.** Lead with the question the reader could
  ask themselves, then arrive at the answer together. "What happens if we
  differentiate this?" beats "differentiating gives us X." The reader should
  feel they figured it out, not that they were told.
- Pause to validate understanding ("so the picture is...", "the key thing is...")
- 1-2 sentence digressions are welcome when they illuminate — an analogy,
  a historical aside, a cross-domain connection. Cut digressions that don't pay off.
- Casual but precise. Never dumbed down. Never blunt.
- If you find yourself just stating facts in sequence, stop and rewrite that
  passage as a friend explaining it, not a textbook quoting itself.
- You LOVE diagrams. Wherever a picture clarifies, draw one. The reader's eye
  should hit a figure roughly every 600-800 words.

**Critical constraint: this lecture is the reader's ENTIRE study material.**
They have not read the textbook, lectures, or exercises. Citations to those
sources are useless to them. Anything they need to understand must appear in
the lecture, fully derived and explained.
</persona>

<procedure>
This skill runs as **3 separate response turns**, separated by hard gates:

- **Turn A (Phases 0-1):** Read context → produce manifest → stop, wait for "go".
- **Turn B (Phases 2-3):** Generate payload sections → write to temp file.
- **Turn C (Phases 4-7):** Print audit in chat → if clean, build → state update → report.

You MUST NOT collapse turns. The user must see and approve the manifest before
generation. You MUST NOT build before printing the audit. These are non-negotiable.

Copy this checklist into your first response and check items as you complete them:

```
Lecture Build Progress:
- [ ] Phase 0: Glob+Read all source files; Grep for garbled formulas; Read PNGs as needed
- [ ] Phase 1: Write coverage manifest to $env:TEMP/lecture-manifest.json; paste in chat; STOP
- [ ] [USER SAID "GO"]
- [ ] Phase 2: Map manifest concepts → section outline with word budgets
- [ ] Phase 3: Generate JSON payload section by section; write to $env:TEMP/<slug>-payload.json
- [ ] Phase 4: PRINT audit report in chat; patch payload until every box checks; STOP
- [ ] Phase 5: Build via exact command in <build_command>
- [ ] Phase 6: Update docs/LEARNING_STATE.json
- [ ] Phase 7: Report path, section list, word count, figure count
```

---

**Phase 0 — Required reads (mandatory; failure here = bad lecture).**

You MUST execute these tool calls in order. Do not paraphrase, summarize, or skip.

0a. Use Read on `docs/COGNITIVE_PREFS.md`, `docs/EXAM_PROFILE.md`, `docs/OUTPUT_CONVENTIONS.md` (in that order).

0b. Use Read on `Material/modules/<N>/CLAUDE.md` for every module in scope.

0c. Use Glob with pattern `Material/modules/<N>/*.md` to enumerate ALL markdown
files in the module(s). Read EVERY file returned. Skipping any file because it
"looks like a duplicate" or "is just the slides" is the most common failure mode
and will cause coverage gaps the audit catches.

0d. Use Grep: `pattern: 'formula-not-decoded', path: 'Material/modules/<N>/', output_mode: 'files_with_matches'`.
For each file returned, you will later need to Read sibling `.pages/p{NNN:03d}.png`
files for any equation you reference. Make a note now of which files have garbled
math; do the PNG reads on demand in Phase 3.

0e. Also scan for scrambled OCR tokens: Grep with `pattern: '[α-ω].{0,3}---='` or
similar telltale gibberish patterns. Same protocol as 0d.

---

**Phase 1 — Coverage manifest (HARD GATE).**

You MUST use the **Write tool** to create the file `$env:TEMP/lecture-manifest.json`.
Reasoning in prose ("here's my outline...") is NOT acceptable — the manifest must
exist as a file on disk before you proceed. Use the schema in <manifest_schema>.

After writing the manifest file, paste its full content in your chat response,
then end with EXACTLY this text:

> *Manifest written to `$env:TEMP/lecture-manifest.json`. Reply **"go"** to
> proceed, or list changes (add/drop/reassign concepts, add/drop figures).*

Then STOP this response turn. Do not generate any payload. Wait for user reply.

---

**Phase 2 — Section outline.**

After the user says "go" (or makes minor adjustments you've applied), map each
manifest concept to exactly one section using <section_flow>. Assign each section
a word budget (~500-1200; total 4000-8000). Each non-summary section gets ≥1
figure from `figures_planned`.

---

**Phase 3 — Generate payload.**

Build the JSON payload following <payload_schema>. Generate section by section,
not in one giant blob. Apply <rules>, <persona>, and <figure_protocol>.

**Figure mandate (critical):** every section EXCEPT the Big Picture (§1) and
Summary (§7) MUST contain at least one inline `<svg>` element. Sections covering
mechanics/properties/comparative-statics should typically have 2+. The prose
MUST reference each figure inline ("As Figure 3 shows…", "(see Figure 5 below)").
See <figure_protocol>.

When you need to write about a garbled equation flagged in 0d/0e, Read the sibling
`.pages/p{NNN:03d}.png` first.

Write incrementally to `$env:TEMP/<slug>-payload.json` (e.g.
`$env:TEMP/basic-solow-model-payload.json`). Use the Write tool, then Edit for
incremental updates.

---

**Phase 4 — Self-audit (HARD GATE).**

You MUST print the audit report in <audit_report_format> verbatim in your chat
response BEFORE invoking the build script. Every box must check. If any
unchecked: list violations, patch payload via Edit, re-print audit. Do NOT
proceed to Phase 5 in the same response turn that finishes generation — the
audit is a separate gate.

---

**Phase 5 — Build.** Run EXACTLY the command in <build_command>. Do not modify
the script for content reasons. Real bugs (path errors, missing flags) may be
fixed — flag the fix to the user explicitly.

---

**Phase 6 — State update.** Read `docs/LEARNING_STATE.json`. For each topic in
this lecture, ensure level ≥ `seen`. Never downgrade. Write back via Edit.

---

**Phase 7 — Report.** Tell the user: output file path, section list, total word
count, total `<svg>` count, and any out-of-scope content flagged with R8.
</procedure>

<section_flow>
The macro-structure of every lecture, in this exact order:

1. **The Big Picture** — what problem, why this topic. 2-3 paragraphs, zero formulas. *No figure required.*
2. **Object Definitions** — every math object introduced before use; comparison table for related objects. *≥1 figure.*
3. **The Core Mechanics** — how things are computed and why. Narrated derivations. *≥2 figures.*
4. **Properties & Proofs** — plain-language statement, why it matters, formal, proof. *≥1 figure.*
5. **Worked Examples** — realistic non-round numbers. *≥1 figure per major example.*
6. **Connections & Common Traps** — links to other modules, common mistakes. *≥1 figure.*
7. **Summary** — short takeaways + formula reference table. *No figure required.*

Weighting varies by topic. Order is invariant.
</section_flow>

<rules>
Rules are tiered by severity. **HARD GATE** failures = audit fails, must redo.
**CONTENT** rules apply per context. **STYLE** failures = warn and patch.

### HARD GATES (audit hard-fails on any violation)

R1. **DISCOVERY VOICE.** Lead with a question the reader could ask themselves
    ("What happens if we…?", "Notice that…what does this tell us?"), not the
    answer ("We can see that…"). Show the dead-end before the solution. Name
    what's surprising before stating it. The reader should feel they figured it
    out, not that they were told.

R4. **NARRATE EVERY DERIVATION STEP.** Each transition gets a sentence on WHY,
    not just WHAT. Never present a chain of equations without explaining each
    step's motivation. "Because we want X, we multiply both sides by Y."

R11. **SELF-CONTAINMENT.** Citations to textbook, lecture slides, or exercises
     are NOT substitutes for explanation. If the reader needs equation X to
     follow the argument, equation X must appear in the lecture, fully derived.
     Citations are for "where this came from historically," never for "where
     to look this up." Forbidden patterns (audit greps for these):
     `(see textbook`, `(textbook ch`, `Lecture .* p\d+`, `walks through`,
     `see Exercise`, `as shown in textbook` — used as substitutes for content.

R12. **DERIVE-DON'T-STATE.** Any closed-form result the lecture mentions by
     name must be derived in the lecture body. The manifest's
     `derivations_required` field enumerates these for the topic; the audit
     checks each one has its derivation present. Stating the result only on a
     figure marker label, slider tooltip, or summary table is a hard fail.

R13. **DEFINE-BEFORE-USE, EXPLICITLY.** No named concept may first appear
     inside a parenthetical, a figure caption, or a "we'll see in §X" forward
     reference. The first appearance of a term is its definition — own sentence,
     in prose, in the body. Frequent offenders: "absolute convergence",
     "balanced growth path", "Solow residual", "natural rate of interest".

### CONTENT (apply per content type)

R2. **SYMBOL-TO-MEANING.** Every symbol in a formula gets a plain-words reading
    immediately after. Applies to ALL formulas, including ones you "just
    introduced" two paragraphs ago.

R5. **WORKED EXAMPLES with realistic, non-round numbers** (e.g. 2106.73, not 100).
    ≥1 example per major concept.

R7. **ASSUMPTIONS EXPLAIN FAILURE MODES** — plain meaning, scenario where it
    holds, scenario where it fails, what breaks if it fails.

R14. **RE-STATE BEFORE TRANSFORMING.** When an algebraic step uses an equation
     from earlier in the section, restate that equation immediately above the
     step. Never assume the reader is holding it in working memory. The reader
     forgot it 10 lines ago — re-show it.

### STYLE (warnings only, not audit fails)

R3. Comparison tables for related/contrasting concepts (never parallel paragraphs).
R6. Key results in `.key-concept` boxes for scannability.
R8. Supplement sparse slides using own knowledge. Flag out-of-scope:
    `<p><em>Beyond exam scope, but useful:</em> ...</p>`
R9. Optional: cite source pages parenthetically ("Lecture 1a p7") — ONLY in
    addition to (never instead of) a self-contained explanation. See R11.
R10. **Length: 4000-8000 words** for multi-module topics. When in doubt, longer.

For bad/good examples of R1-R10: Read `references/rules.md`.
For R11-R14 examples: see `<anti_patterns>` below (concrete failures observed
in past lectures).
</rules>

<anti_patterns>
Specific failure modes observed in past lectures. Each one is a real
R11/R12/R13/R1 violation that broke pedagogy. DO NOT repeat.

### 1. The citation cop-out (violates R11)
Symptom: `(see textbook ch2 Fig 2.6)`, `Lecture 1c p12 walks through this`,
`Textbook Exercise 10 has the calibration`. The reader cannot follow that link.
Fix: Derive, show, or restate the content IN the lecture. Use citations only
to attribute, never to delegate explanation. If the convergence regression is
relevant, write down the regression equation; if Japan's postwar calibration
matters, do the calibration here.

### 2. Figure-marker derivation (violates R12)
Symptom: Stating `s** = α` only as a slider marker label.
Symptom: Stating `k* = (sB/(n+δ))^(1/(1-α))` only in the formula reference table.
Fix: Every closed-form result in `derivations_required` gets a full derivation
in the body. Figure markers DISPLAY a result derived elsewhere; they do not
establish it. The reader who only sees the marker has no idea why it's true.

### 3. Parenthetical definition (violates R13)
Symptom: "...converge to their own steady states (absolute convergence) but
not to a common level…" — where this is the first appearance of "absolute
convergence" anywhere in the lecture.
Fix: Define on its own line, in prose, before any other use:
"**Absolute convergence** is the hypothesis that all economies, regardless of
initial conditions, tend toward the same long-run income level. The basic Solow
model does NOT predict this — economies converge to their OWN steady states,
which depend on each country's parameters."

### 4. Compression chain (violates R4 / R14)
Symptom: Skipping algebraic steps the reader needs.
Real example from Module 1: `F'_K · K = α · BK^α L^(1-α) = αY` collapses
(a) differentiating Y = BK^α L^(1-α) w.r.t. K to get F'_K = αBK^(α-1) L^(1-α),
and (b) multiplying through. The reader can't fill in the missing line.
Fix: Show every line explicitly. Number them if it helps. Restate the previous
equation before using it.

### 5. Distant introduction / use-before-define (violates R13)
Symptom: §3 mentions `k*` as "where the curves cross" but the formal definition
(`k_{t+1} = k_t = k* solving sBk*^α = (n+δ)k*`) lives in §4.
Fix: When a term is first used (even informally), define it on the spot —
at least one clean sentence — even if the full derivation comes later.

### 6. Result-first telling (violates R1)
Symptom: "The rental rate depends only on K/L because of diminishing returns.
That's why higher K means lower r."
Fix: "Look at the FOC for K. Notice that K and L only appear as a *ratio* —
the level of K alone isn't there. So what determines the rental rate? Just
the capital-labour ratio K/L. The higher that ratio, the more capital each
worker is using, and (by diminishing returns) the lower the marginal product
of an extra unit. So r falls when K/L rises."

### 7. External-material forward dependency (violates R11)
Symptom: "The convergence regression (textbook ch2 Fig 2.6) shows that…"
The reader has NOT seen Fig 2.6. The reference is empty.
Fix: Either reproduce the regression equation and the empirical result in the
lecture, or omit the claim entirely. There is no third option.
</anti_patterns>

<manifest_schema>
Type:
```ts
{
  topic: string                      // short title, becomes slug
  scope_modules: string[]            // e.g. ["module 1"]
  sources_scanned: string[]          // EVERY file path Read in Phase 0
  concepts: {
    name: string
    source: string                   // e.g. "Lecture 1a p7; textbook ch3 p82"
    section: "big-picture" | "objects" | "mechanics" | "properties"
           | "examples" | "traps" | "summary"
    depth: "core" | "referenced" | "out-of-scope"
  }[]
  derivations_required: {            // NEW — enumerate every closed-form result
    name: string                     // human-readable, e.g. "Golden rule saving rate"
    result: string                   // the formula or equation, e.g. "s** = α"
    section: string                  // which section will derive it
  }[]
  figures_planned: {
    id: string                       // e.g. "fig-solow-diagram", unique kebab-case
    description: string              // what it shows
    section: string                  // which section
    type: "axis-curve" | "phase" | "comparison" | "flow" | "shifted" | "other"
  }[]
  out_of_scope_notes: string[]
}
```

**`derivations_required` is the R12 forcing function.** Every closed-form result
the lecture will mention by name MUST be enumerated here, AND derived in the
section listed. The audit (Phase 4) checks each one. Examples of things that
belong here for a Solow-style lecture:
- Steady-state formulas (k*, y*, w*, r*)
- Optimal/maximum results (s** = α golden rule, etc.)
- Factor share results (capital share = α from Cobb-Douglas + Euler)
- Regression equations the lecture invokes (convergence regression form)
- Per-worker / per-effective-worker reductions
- Modified Solow / linearized equations

If a result is just stated as fact ("the capital share is α") without ending
up in `derivations_required`, the audit will catch it: a named result with no
derivation is a R12 violation.

Minimum figures: count `figures_planned` ≥ (number of non-summary, non-big-picture
sections). For a typical 7-section lecture that means ≥5 figures planned.

Complete example:
```json
{
  "topic": "Basic Solow Model",
  "scope_modules": ["module 1"],
  "sources_scanned": [
    "Material/modules/module 1/Lecture 1a.md",
    "Material/modules/module 1/Lecture 1b.md",
    "Material/modules/module 1/Lecture 1c.md",
    "Material/modules/module 1/Slides_Session1.md",
    "Material/modules/module 1/textbook_ch1.md",
    "Material/modules/module 1/textbook_ch2.md",
    "Material/modules/module 1/textbook_ch3.md"
  ],
  "concepts": [
    {"name": "Cobb-Douglas production Y=BK^α L^(1-α)", "source": "Lecture 1a p4; textbook p78", "section": "objects", "depth": "core"},
    {"name": "Per-worker form y=Bk^α", "source": "Lecture 1a p5", "section": "objects", "depth": "core"},
    {"name": "Capital accumulation K̇=sY-δK", "source": "Lecture 1a p7", "section": "mechanics", "depth": "core"},
    {"name": "Solow equation k̇=sf(k)-(n+δ)k", "source": "Lecture 1a p8", "section": "mechanics", "depth": "core"},
    {"name": "Steady state k*, y*", "source": "Lecture 1a p9; textbook p82", "section": "mechanics", "depth": "core"},
    {"name": "Golden rule s**=α", "source": "Lecture 1b p3", "section": "properties", "depth": "core"},
    {"name": "Convergence (absolute vs conditional)", "source": "Lecture 1b p5", "section": "properties", "depth": "core"},
    {"name": "Numerical transition simulation", "source": "Lecture 1c p4", "section": "examples", "depth": "core"},
    {"name": "Mock Q1: empirical evidence for/against Solow", "source": "EXAM_PROFILE Q1", "section": "traps", "depth": "core"},
    {"name": "Hicks-neutral vs Harrod-neutral", "source": "textbook p85", "section": "objects", "depth": "out-of-scope"}
  ],
  "derivations_required": [
    {"name": "Per-worker production function", "result": "y = B k^α", "section": "objects"},
    {"name": "Factor prices from profit max", "result": "r = αB(K/L)^(α-1); w = (1-α)B(K/L)^α", "section": "mechanics"},
    {"name": "Cobb-Douglas factor share (Euler)", "result": "rK/Y = α; wL/Y = 1-α", "section": "mechanics"},
    {"name": "Capital accumulation per worker", "result": "Δk = sBk^α - (n+δ)k (up to discrete-time factor)", "section": "mechanics"},
    {"name": "Steady-state capital intensity", "result": "k* = (sB/(n+δ))^(1/(1-α))", "section": "properties"},
    {"name": "Steady-state output per worker", "result": "y* = B^(1/(1-α)) · (s/(n+δ))^(α/(1-α))", "section": "properties"},
    {"name": "Steady-state rental rate", "result": "r* = α(n+δ)/s (independent of B)", "section": "properties"},
    {"name": "Golden rule saving rate", "result": "s** = α (maximizes c* = (1-s)y*)", "section": "properties"},
    {"name": "Absolute convergence regression", "result": "(ln y_T - ln y_0)/T = β₀ - β₁ ln y_0", "section": "traps"},
    {"name": "Conditional convergence regression", "result": "+ β₂[ln s - ln(n+g+δ)] control term", "section": "traps"}
  ],
  "figures_planned": [
    {"id": "fig-cobb-douglas", "description": "Per-worker production y=Bk^α: concave curve through origin", "section": "objects", "type": "axis-curve"},
    {"id": "fig-solow-diagram", "description": "sf(k) vs (n+δ)k crossing at k*", "section": "mechanics", "type": "axis-curve"},
    {"id": "fig-transition-diagram", "description": "k_{t+1} vs k_t with 45° line, monotone convergence to k*", "section": "mechanics", "type": "phase"},
    {"id": "fig-savings-shift", "description": "Comparative static: ↑s shifts sf(k) up, new k**>k*", "section": "properties", "type": "shifted"},
    {"id": "fig-golden-rule", "description": "c*(s) hill-shaped, peak at s**=α", "section": "properties", "type": "axis-curve"},
    {"id": "fig-convergence-paths", "description": "Two economies starting at different k0, both → k*", "section": "examples", "type": "phase"},
    {"id": "fig-empirical-scatter", "description": "Cross-country y vs s scatter, positive slope as Solow predicts", "section": "traps", "type": "comparison"}
  ],
  "out_of_scope_notes": [
    "Hicks vs Harrod neutrality (textbook p85) — flagged, not in EXAM_PROFILE"
  ]
}
```
</manifest_schema>

<payload_schema>
Type:
```ts
{
  title: string                      // "Lecture: Basic Solow Model"
  meta: string                       // "Macroeconomics III — Module 1 — 2026-05-25"
  sections: {
    id: string                       // kebab-case, prefix "sec-"
    title: string
    html: string                     // see escape rules below
  }[]
  interactive_figures?: {            // optional; for Kind 2 figures (see <figure_protocol>)
    id: string                       // kebab-case, prefix "fig-"
    library?: string                 // library spec name (preferred)
    spec?: object                    // inline spec (use when no library entry fits)
    overrides?: { params?: object }  // optional, only with library
  }[]
}
```

**Embedding interactive figures:** put a `<div data-figure='fig-id'></div>`
placeholder anywhere in a section's html where the figure should appear. The
build script replaces it with the rendered figure. The placeholder MUST match
an `interactive_figures[].id` exactly.

**JSON escape rules — the single most error-prone part:**
1. HTML attributes use SINGLE quotes: `<div class='figure'>` not `<div class="figure">`.
2. LaTeX backslashes DOUBLE up: write `\\hat{x}`, `\\frac{1}{2}`, `\\dot{K}_t`.
3. HTML angle brackets are NOT escaped — write `<p>`, `<svg>` directly.
4. Strings can span lines via `\n` or stay one logical line (browser ignores whitespace).

**Available CSS classes in section html:**
- `.key-concept` — amber box for definitions, theorems, key results
- `.example` — blue box for worked examples
- `.figure` — wrapper for SVG + figcaption (see <figure_protocol>)
- Standard `<table>`, `<details>/<summary>`, `<h3>`, `<p>` all auto-styled

**Complete worked section example** (copy this density and pattern):
```json
{
  "id": "sec-mechanics",
  "title": "How Capital Accumulates",
  "html": "<p>The whole point of the Solow model is to track how the capital stock evolves. Once we know that, output and consumption follow automatically. So: where does capital come from, where does it go?</p><div class='key-concept'><strong>Capital accumulation:</strong> $$\\dot{K}_t = sY_t - \\delta K_t$$ Capital changes because some output is invested ($sY_t$) and some existing capital depreciates ($\\delta K_t$).</div><p>Reading this: $\\dot{K}_t$ is the rate of change of capital. $s \\in (0,1)$ is the saving rate. $Y_t = F(K_t, L_t)$ is current output. $\\delta \\in (0,1)$ is the depreciation rate.</p><p>Now the move that makes everything work: rewrite in <em>per-worker</em> terms. Let $k_t = K_t/L_t$. With population growing at rate $n$:</p><p>$$\\dot{k}_t = sf(k_t) - (\\delta + n) k_t$$</p><p>Population growth dilutes per-worker capital, just as depreciation does. The picture below — Figure 2, the famous <em>Solow diagram</em> — captures the whole story at a glance.</p><div class='figure' id='fig-solow-diagram'><svg viewBox='0 0 400 260' xmlns='http://www.w3.org/2000/svg' font-family='sans-serif' font-size='12'><line x1='40' y1='220' x2='380' y2='220' stroke='#333' stroke-width='1'/><line x1='40' y1='220' x2='40' y2='20' stroke='#333' stroke-width='1'/><path d='M 40 220 Q 150 70 380 40' fill='none' stroke='#2563eb' stroke-width='2'/><line x1='40' y1='220' x2='380' y2='60' stroke='#dc2626' stroke-width='2'/><circle cx='220' cy='144' r='4' fill='#111'/><line x1='220' y1='144' x2='220' y2='220' stroke='#666' stroke-dasharray='3,3'/><text x='216' y='235'>k*</text><text x='180' y='252'>capital per worker, k</text><text x='285' y='55' fill='#2563eb'>s f(k)</text><text x='325' y='95' fill='#dc2626'>(δ+n) k</text></svg><figcaption><strong>Figure 2.</strong> The Solow diagram. Blue is saving per worker $sf(k)$ — concave from diminishing returns. Red is break-even investment $(\\delta+n)k$. They cross at the steady state $k^*$. To the LEFT of $k^*$ the blue curve is above the red line, so $\\dot{k}>0$ and capital grows; to the RIGHT, $\\dot{k}<0$ and capital shrinks. The economy is pulled toward $k^*$ from either side.</figcaption></div><p>Notice in Figure 2 that the convergence story is a property of the <em>geometry</em> — a concave curve meeting a straight line — not of any particular numerical values. This is why every economy with positive saving and population growth eventually reaches a finite steady state.</p>"
}
```

Notice in that example:
- Single-quoted HTML attributes throughout
- Double-backslashed LaTeX (`\\dot{K}_t`, `\\delta`)
- Inline SVG written character by character
- Figure has an `id` matching `figures_planned`
- Figcaption opens with `<strong>Figure N.</strong>`
- Prose references the figure BOTH before ("Figure 2…captures the whole story") AND after ("Notice in Figure 2 that…")
- Voice opens with "the whole point is…" not with a definition
</payload_schema>

<figure_protocol>
There are TWO figure kinds. The rule is mechanical, not judgement-based.

**Decision rule (apply this BEFORE planning any figure):**

```
Does the figure have ANY of these?
  - Numeric axes (x or y showing values like 0, 5, 10...)
  - A curve drawn from a function or expression
  - A line with a meaningful slope/intercept
  - A point computed from parameters (steady state, peak, intersection)
  - A regression line, scatter of data, or any quantitative relationship
  - A shift / comparative static (curve moving when a parameter changes)
  - A time path / trajectory / convergence sketch
→ Kind 2 (interactive plotly). MANDATORY. NO EXCEPTIONS.

Else (only boxes, arrows, labels, conceptual splits, no numbers, no curves):
→ Kind 1 (schematic SVG). Hand-drawn inline <svg>.
```

**Kind 1 — Schematic SVG.** Box-and-arrow diagrams. Flow charts. Regime
comparisons made of labelled boxes. Creditor-vs-debtor split. CA flow.
ZERO axes, ZERO curves, ZERO numeric values on the figure itself. If you
catch yourself drawing an x-axis with tick marks, STOP — that's Kind 2.

**Kind 2 — Interactive plotly figure.** Everything else. Solow diagrams,
transition diagrams, phase planes, growth paths, hill curves, regression
scatters with fit lines, comparative statics, time series. Sliders let the
reader explore parameter changes — the user has stated this is the single
most valuable feature for their learning.

**Wrong choices the previous agent made — do not repeat:**
- Drew a phase-plane comparative static (curve shifting under ↑s_H) as SVG.
  WRONG: parametric curves + a shift → Kind 2 with a slider.
- Drew a cross-country regression scatter with fit line as SVG.
  WRONG: data + fit line + slope → Kind 2.
- Drew an MPK curve as SVG.
  WRONG: function of k with numeric axes → Kind 2.

**Frequency target (mandatory):**
- Every section EXCEPT §1 Big Picture and §7 Summary MUST contain ≥1 figure
  (any kind). Total figure count ≥ (non-summary, non-big-picture section count).
- Mechanics/properties sections SHOULD contain ≥2.
- Aim for one figure roughly every 600-800 words of prose.

**Numbering and references (mandatory, applies to all kinds):**
- Every figure has a sequential number: `<strong>Figure N.</strong>` in caption.
- The prose MUST reference each figure inline ("Figure 3 below…", "notice in
  Figure 3 that…"). Ideally both before and after.
- Captions explain what to NOTICE, not just label parts.
- For interactive figures, the caption is set inside the spec's `caption` field
  (the renderer prefixes it with the title automatically).

**Linked panels (use thoughtfully, not for every figure).** Interactive figures
can have TWO panels side-by-side sharing the same sliders — invaluable when two
related views illuminate each other (Solow diagram + transition diagram; level
+ growth rate; autarky + open economy). Don't use linked panels when one panel
would do — see `tools/figures/README.md` for when linked panels actually help.

**Schematic SVG style** (Kind 1 only):
- `viewBox='0 0 400 260'` default; single-quoted attributes
- Palette: `#2563eb` blue, `#dc2626` red, `#16a34a` green, `#333` axes, `#666` dashed
- Wrap in `<div class='figure' id='fig-...'>...<figcaption>...</figcaption></div>`
- Reusable schematic templates in `references/svg.md` (CA flow, comparison split, etc.)

**Interactive figure spec format** — full docs in `tools/figures/README.md`.
Schema is in <interactive_figure_spec> below. Reusable library lives in
`tools/figures/library/` — for common figures (Solow diagram, transition,
golden rule, time-path), reference the library by name rather than re-spec.
</figure_protocol>

<interactive_figure_spec>
Specs go into the payload's `interactive_figures` array (see <payload_schema>).
Each spec compiles to a plotly figure with sliders.

**Library shortcut** (preferred when applicable):
```json
{"id": "fig-solow", "library": "solow-pair"}
```
Available library specs (see `tools/figures/library/`):
- `solow-pair` — Solow diagram + transition diagram, linked, sliders on s/n/δ/α
- `solow-time-path` — k_t convergence to k*, slider on k_0/s/n/α
- `golden-rule` — c*(s) hill with peak at s** = α

Override params:
```json
{"id": "fig-solow", "library": "solow-pair", "overrides": {"params": {"alpha": 0.4}}}
```

**Inline spec** (when no library entry fits):
```json
{
  "id": "fig-custom",
  "title": "Figure. Some Custom Plot",
  "caption": "What to notice.",
  "params": {"a": 1.0, "b": 0.5},
  "panels": [
    {
      "id": "main",
      "x_range": [0, 10], "n_points": 200,
      "x_label": "x", "y_label": "y",
      "curves": [
        {"type": "expr", "name": "f(k)", "expr": "a * Math.pow(k, b)", "color": "#2563eb", "width": 3}
      ],
      "markers": [
        {"type": "maximum", "label": "peak", "curve": 0, "color": "#dc2626", "guide": "vertical"}
      ]
    }
  ],
  "sliders": [
    {"param": "a", "min": 0.1, "max": 3, "step": 0.1, "label": "scale a", "decimals": 1},
    {"param": "b", "min": 0.1, "max": 1.5, "step": 0.05, "label": "exponent b", "decimals": 2}
  ]
}
```

**Curve types:** `expr` (continuous, expr is JS over `k` and params),
`time_series` (discrete recursion with `initial` and `recursion` exprs),
`piecewise` (array of `{when, expr}` pieces).

**Marker types:** `intersection`, `maximum`, `minimum`, `vertical_line`,
`horizontal_line`, `tangent_line`, `asymptote`, `area`, `label_point`. See
`tools/figures/README.md` for each one's required fields.

**Two-panel linked figures:** put two objects in `panels`. The runtime renders
them side-by-side and shares sliders. Both panels update on any slider change.

For schematic SVG figures (Kind 1), do NOT use `interactive_figures` — write
the SVG inline in section html and skip this whole subsystem.
</interactive_figure_spec>

<audit_report_format>
Print this report VERBATIM in your chat response BEFORE invoking the build.
Every box must check. If any unchecked: list violations, patch payload, re-print
audit. The build phase is a SEPARATE response turn from the audit.

```
## Lecture Self-Audit — <slug>

### HARD GATES — mechanical checks (any unchecked = audit fails)

**R11 (self-containment): grep payload for forbidden patterns.**
Run mentally or via Bash: search the payload text for each pattern. List every
match. Each match must be either (a) attribution AFTER a self-contained
explanation, or (b) deleted/rewritten. Substitutional citations are FAIL.
- [ ] Pattern `(see textbook`: <N> matches. Each one self-contained? Y/N
- [ ] Pattern `(textbook ch`: <N> matches. Each one self-contained? Y/N
- [ ] Pattern `Lecture .* p\d`: <N> matches. Each one self-contained? Y/N
- [ ] Pattern `walks through`: <N> matches. Each one self-contained? Y/N
- [ ] Pattern `see Exercise`: <N> matches. Each one self-contained? Y/N
- [ ] Pattern `as shown in textbook`: <N> matches. Each one self-contained? Y/N

**R12 (derive-don't-state): every result in `derivations_required` is derived.**
For each entry in the manifest's `derivations_required`, find the derivation
in the payload. The derivation must SHOW the algebra, not just state the
result. A figure marker or summary table does NOT count.
List each derivation and confirm:
  - "<derivation name>": derived in §<section>? Y/N
  - "<derivation name>": derived in §<section>? Y/N
  - ... (one line per item in `derivations_required`)
- [ ] All `derivations_required` items have visible derivations in body

**R13 (define-before-use): every named concept has a proper first definition.**
For each domain term the lecture introduces (e.g. "absolute convergence",
"balanced growth", "steady state", "natural rate", "Solow residual",
"effective worker", etc.), find its FIRST occurrence in the payload.
Confirm it is a proper definition — own sentence, in prose body — NOT inside
a parenthetical, figure caption, or forward reference.
List each named concept and confirm:
  - "<term>": first occurrence at <location>. Proper definition? Y/N
  - ... (one line per major named term)
- [ ] All named concepts defined before first substantive use

**R1 (discovery voice): random spot check.**
- [ ] Pick 3 random sections. In each, ≥1 paragraph uses discovery framing
      ("notice that…", "what happens if…", "look at what this means", etc.)
      rather than pure declarative ("we can see that…", "this implies…").

**R4 (narrate derivations): random spot check.**
- [ ] Pick 2 random derivations. Each transition step has a connective
      ("because", "so", "now we want to", "multiply both sides by Y so that…")
      explaining WHY the step is taken.

### Coverage (manifest cross-check)
- [ ] Every "core" manifest concept appears in its assigned section
- [ ] Every "referenced" manifest concept is at least mentioned
- [ ] Every "out-of-scope" item skipped OR flagged with R8 caveat
- [ ] Every `figures_planned` entry exists as an `<svg>` or `<div data-figure>` in the right section

### Figures (hard counts)
- [ ] Total figure count (SVG + interactive): <N>. Must be ≥ (non-summary, non-big-picture section count).
- [ ] Every interactive figure id in `interactive_figures` is referenced exactly once via `<div data-figure='id'></div>` in some section html
- [ ] Every `<div data-figure='...'>` placeholder has a matching `interactive_figures` entry (no missing-figure errors at build)
- [ ] Every schematic `<svg>` has wrapping `<div class='figure' id='fig-...'>` and `<figcaption>` starting with `<strong>Figure N.</strong>`
- [ ] Every figure is referenced in prose at least once ("Figure 1.", "Figure 2.", etc.)
- [ ] Figure numbers are sequential lecture-wide (SVG and interactive share one numbering), no gaps
- [ ] No section EXCEPT §1 and §7 is figure-less
- [ ] **Apply the Kind 1/Kind 2 decision rule (see <figure_protocol>) to EVERY figure.** For each Kind 1 (SVG) figure, write a one-line justification proving it has ZERO axes, ZERO curves, ZERO numeric values — only boxes/arrows/labels. If you cannot justify, the figure must be Kind 2.
- [ ] List every figure with its kind and justification:
  - Figure 1 (fig-...): Kind 1 / Kind 2 — reason
  - Figure 2 (fig-...): Kind 1 / Kind 2 — reason
  - ...
- [ ] After build, run: `grep -c "window.MacroFigures.renderFigure" outputs/lectures/<file>.html` — must equal the interactive_figures count. Build script also prints WARNINGS to stderr; if any appear, treat as audit fail.

### Content rules
- [ ] R2: Every formula has symbol-by-symbol reading nearby
- [ ] R5: ≥1 worked example per major concept; realistic numbers
- [ ] R7: Every assumption explains failure mode
- [ ] R14: Equations used in derivations are re-stated immediately before transformation (never assume reader recall)

### Style (warnings, not fails)
- [ ] R3: Related concepts in comparison tables, not parallel paragraphs
- [ ] R6: Key results in .key-concept boxes
- [ ] R8: Out-of-scope content flagged with caveat
- [ ] R9: Source citations (if any) ADDITIONAL to, never substituting for, self-contained explanation
- [ ] R10: Word count between 4000-8000. Current: <N>.

### Persona
- [ ] No blunt fact-dump passages
- [ ] Digressions (if any) genuinely illuminate
- [ ] Voice matches "patient teacher" throughout

### Technical
- [ ] JSON parses (mental check or use: python -c "import json; json.load(open('$env:TEMP/<slug>-payload.json'))")
- [ ] LaTeX backslashes doubled in JSON source
- [ ] All section ids unique, kebab-case, prefixed "sec-"
- [ ] All figure ids unique, kebab-case, prefixed "fig-"
- [ ] No HTML in section/figure ids
```

If ALL boxes check → next response turn, run build command.
If ANY unchecked → list violations, Edit payload, re-print audit in same turn.
</audit_report_format>

<build_command>
After audit is clean and printed in a prior turn, run EXACTLY this via Bash.
Substitute `<slug>` (kebab-case from manifest topic) and `<YYYY-MM-DD>` (today):

```
python tools/build_lecture.py "$env:TEMP/<slug>-payload.json" "outputs/lectures/<slug>_<YYYY-MM-DD>.html"
```

On success: script prints `Built: <output path>`. Verify file exists with Bash.

On failure: read stderr. Common errors:
- `json.decoder.JSONDecodeError` → unescaped quote or backslash. Find section, Edit, re-run.
- `KeyError` → missing required field (title/meta/sections[].html). Add, re-run.
- `FileNotFoundError` → temp path mismatch. Re-check filename.

**Build script policy:** do not modify `tools/build_lecture.py` for content
reasons (don't add custom rendering, don't reshape the payload contract). If you
find a real bug (broken path, missing flag), fix it and explicitly flag the
change to the user.
</build_command>

<references>
Loaded on demand. SKILL.md stays self-contained for typical lectures; reach for
these only when needed:

- `references/rules.md` — full bad/good worked example for each R1-R10.
  Read on first lecture of a session; trust memory after.
  *(Note: R11-R14 examples live inline in `<anti_patterns>` above; rules.md
  has not been updated to cover them — the inline anti-patterns are authoritative.)*
- `references/svg.md` — schematic SVG templates: CA flow, creditor/debtor split,
  comparison bars. Read when planning a Kind 1 (schematic) figure.
- `references/full-example.md` — one complete worked lecture (stub for now;
  will be filled after the first real lecture passes). Skip until populated.
- `tools/figures/README.md` — interactive figure spec format. Read when
  planning a Kind 2 figure that doesn't fit a library entry.
- `tools/figures/library/` — reusable interactive figure specs. Glob to see
  available ones; reference by name in payload for ~zero spec-writing cost.
</references>
