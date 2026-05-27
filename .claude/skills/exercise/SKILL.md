---
name: exercise
description: "Generate deep-understanding exercise sets with progressive hints and fully-detailed worked solutions. Use this skill whenever the user says '/exercise', asks for practice problems, wants to drill proofs/derivations, mentions wanting to prove things on paper, or requests worked examples. Also triggers on 'give me problems on [topic]', 'I need to practice deriving [topic]', 'proof exercises for [topic]', or any request for hands-on problem sets that go beyond MCQ. Exercises are 'I can derive it on paper, with depth' — distinct from /quiz (MCQ recognition) and /exam (essay-time simulation)."
---

# /exercise — Compound Exercise Generation

Generate **5 exercises per set** that are jointly **cumulatively exhaustive** of the requested topic and **mutually exclusive** between exercises, then save to `outputs/exercises/`.

Each exercise is a **compound problem** built from labeled sub-moves (anchor, main proof, method variation, methodology reflection, counterfactual, numeric, falsification, …). The compound structure is the entire point: it forces interleaving, self-explanation, and counterfactual reasoning — the three highest-yield strategies in the learning research for deep understanding and transfer.

The user does these **after** `/lecture` (study) and `/quiz` (recognition check). By the time they hit `/exercise` they've seen the material and probed their understanding; this is where they *reproduce* derivations on paper, *connect* across topics, and *break* assumptions to see what holds the result together.

@docs/COGNITIVE_PREFS.md
@docs/OUTPUT_CONVENTIONS.md
@docs/EXAM_PROFILE.md

## Invocation

User says `/exercise [topic]` optionally with a single-topic or multi-module hint. Set size is fixed at 5.

---

## Workflow

### Step 1 — Read context

The three `@import`s above are already in context. Also read:
- `docs/LEARNING_STATE.json` — current level per topic (calibrates difficulty)
- `Material/modules/<N>/CLAUDE.md` for the topic, then the lecture files in scope
- If any referenced equation has `<!-- formula-not-decoded -->` or scrambled OCR in the `.md`, read the corresponding `.pages/p<NNN>.png`

### Step 2 — Confirm scope (mandatory)

State which module(s) and which lecture files you will draw from, AND list the 5 sub-topic slots you intend to cover. Wait for "go". Example:

> "Generating 5 exercises on **module 1 (basic Solow)** from `Lecture 1a.md`, `Lecture 1b.md`, `Lecture 1c.md`. Slots:
> - Ex 1: convergence speed (two methods, counterfactual on country-specific α)
> - Ex 2: factor shares + Cobb-Douglas vs CES falsification
> - Ex 3: Golden Rule derivation + envelope-theorem variation
> - Ex 4: numeric inversion on observed (s, r) → recover α
> - Ex 5: transition simulation (sketch the algorithm + counterfactual on δ shock)
>
> Together: exhaustive of M1 mechanics + properties; out of set: empirical-evidence prose (handled by `/exam`).
> Ready?"

The exhaustive-mutually-exclusive constraint goes here, not at audit. If you can't divide the module cleanly into 5 slots, ask the user how to scope it (drop a sub-topic, narrow the module, etc.) before generating.

### Step 3 — Generate JSON

Author the JSON per the schema below. Apply all Design Rules.

### Step 4 — Audit (mandatory, before building)

Print this checklist VERBATIM in chat. Every box must check or you patch and re-print.

```
## Exercise Set Audit

### Scope and coverage
- [ ] Set has exactly 5 exercises
- [ ] coverage.topics_covered lists all 5 exercise_ids with explicit topic tags
- [ ] coverage.exhaustive_mutually_exclusive is true AND argued:
      - Union of topics across exercises covers the module's mechanics + properties + key examples
      - No two exercises target the same sub-topic
      - Any deliberate exclusions are listed in coverage.topics_excluded with reason
- [ ] Every exercise's `scope` field cites the specific lecture sections it draws from
- [ ] No exercise drifts out of scope — confirm by reading the prompt and checking
      every named concept appears in the cited lecture files (R-scope below)

### Compound depth
- [ ] Every exercise has a `Main proof` (or equivalent: Main derivation, Main computation) sub-move
- [ ] Every exercise has AT LEAST ONE of:
      methodology-reflection, counterfactual, falsification, cross-module-bridge
- [ ] At least 1 exercise in the set uses two-method derivation (interleaving)
- [ ] At least 1 exercise has a counterfactual sub-move
- [ ] At most 1 exercise is `numeric-inversion` style
- [ ] No exercise is pure plug-and-chug (R-plug-and-chug below)
- [ ] No exercise has "sub-parts" in the bad sense — list each sub-move and confirm
      it deepens (anchor / variation / reflection / counterfactual) rather than
      procedurally chunks (compute X, compute Y, compute Z)

### Hints
- [ ] Every sub-move with substantive algebra has ≥ 2 hints (≥ 3 for Main proof)
- [ ] Hints are progressive: hint 1 orients, mid-hints unblock specific moves,
      final hint gives the load-bearing step
- [ ] No hint gives away the result; the last hint should still leave the
      reader with a step to do

### Solution
- [ ] Every exercise has a solution
- [ ] Solution is organized with `<h3>` (or `<h4>`) sub-section per sub-move
- [ ] Solution shows EVERY algebraic step ("we get" / "rearranging" = audit fail)
- [ ] Solution is ~1500 words total (range: 1200-1800). Currently: <N>
- [ ] Solution uses notation consistent with the lecture (same symbols)
- [ ] Solution flags any assumption it leans on explicitly

### Notation
- [ ] Symbols match `docs/COGNITIVE_PREFS.md` + the source lecture's notation
- [ ] No symbol means two different things in the set
- [ ] Greek letters consistently used (α for capital share, etc.)

### Technical
- [ ] JSON parses
- [ ] LaTeX backslashes doubled in JSON source
- [ ] All exercise ids unique
- [ ] Figure specs (if any) use palette colors and have no `sliders`
```

### Step 5 — Build

```powershell
$tmp = Join-Path $env:TEMP "exercise_payload.json"
# (write JSON to $tmp via Write tool)
python tools/build_exercise.py $tmp outputs/exercises/<slug>_<YYYY-MM-DD>.html
```

The builder prints `WARNINGS:` to stderr for: duplicate IDs, wrong set size (≠5), missing Main proof, missing solution, coverage/id mismatch, figure runtime issues. Treat any warning as audit fail.

### Step 6 — Update LEARNING_STATE.json

For each covered topic: set level to at least `practiced` (never downgrade). When the user reports completing the set with self-assessed mastery, advance to `mastered`.

---

## Design Rules

### R-compound: every exercise is a compound problem

A compound has a **Main proof** (the substantive task) plus at least one **depth-probe** sub-move from this menu:

| Sub-move | Purpose | Length |
|---|---|---|
| **Anchor** | Recall context — "sketch where identity X comes from and under what assumptions" | 1-3 sentences |
| **Main proof** | The substantive derivation / proof / computation | The meat |
| **Method variation** | Same result, second derivation route | Comparable to main |
| **Methodology reflection** | "What does each method rely on? Which assumption is load-bearing?" | 2-4 sentences per method |
| **Counterfactual** | "What happens if assumption Z is dropped / made country-specific / weakened?" | Brief — paragraph or two |
| **Falsification probe** | Prove the result; then construct a case where it fails | Comparable to main |
| **Numeric inversion** | Recover a parameter from observed outcomes; never plug-and-chug | One short calculation |
| **Cross-module bridge** | Use a technique from another module to derive the same result | Comparable to main |

Floor: every exercise has Main + at least one depth-probe. Ceiling: ~5 sub-moves per exercise (more becomes a slog).

### R-variation: vary the compound shape across exercises

Exercises in a set should NOT all look like (Anchor + Main + Variation + Reflection + Counterfactual). Vary the mix:
- Ex with 3 sub-moves (Main + Falsification + Counterfactual) sits next to
- Ex with 5 sub-moves (full compound) sits next to
- Ex with 2 sub-moves (Numeric + Counterfactual)

The user has explicitly said sub-moves can be vastly different across exercises. Treat the catalogue as a menu, not a template.

### R-scope: anchored, not drifting

Every exercise prompt must stay inside the cited module's content. Cross-module references are ALLOWED when they deepen understanding (the user has explicitly invited this), but ONLY as method variation or as a bridge sub-move — the Main proof's primary result must be the module's own content. A Module-1 exercise cannot have its main proof be a Module-5 result.

**Audit step**: for every named concept in an exercise prompt, confirm the concept appears in the cited lecture files. If a concept is from another module, it must be either (a) re-introduced inline (briefly, like the V5 anchor pattern in `/lecture`), or (b) explicitly tagged "from Module X, restated:". No silent borrowings.

### R-exhaustive-exclusive: 5 exercises tile the module

The 5 exercises together must cover the module's content jointly without overlap:
- **Cumulatively exhaustive**: the union of topics across the 5 exercises spans the module's core mechanics, properties, and examples. State this in `coverage.topics_covered`.
- **Mutually exclusive**: no two exercises drill the same sub-topic. If Ex 2 derives the steady-state factor share, Ex 3 cannot also derive the steady-state factor share (even via a different method — that would just be redundant).

Cross-references are NOT overlap: Ex 1 deriving convergence may anchor on Ex 2's factor-share result, and that's fine — the *Main proof* targets are still distinct.

If the module is too big for 5-exhaustive (e.g. a 3-module sprawl), ask the user to scope tighter before generating.

### R-no-plug-and-chug

Numeric questions test *inversion or interpretation*, never arithmetic. Banned:
- "Given α, s, n, δ, compute k\*" → calculator test
- "Compute the F-statistic from this table" → arithmetic

Allowed:
- "Given observed r* = 0.06 and (n+δ) = 0.05, what does basic Solow predict for $\alpha/s$? Discuss whether the value is reasonable."
- "Recover $\alpha$ from observed factor income shares; if the recovered value contradicts the Cobb-Douglas assumption, what would CES predict instead?"

### R-hints-progressive

Hints unfold per sub-move, in this order:
- **Hint 1**: orient the strategy ("Linearize around k\*"; "Use Euler's theorem")
- **Hint 2 (if needed)**: unblock the key algebraic move
- **Hint 3 (if needed)**: provide the load-bearing substitution or assumption
- **Final hint (proofs only)**: name the last non-obvious step — but stop short of the result

Main proof: ≥3 hints. Other substantive sub-moves: ≥2 hints. Reflection / counterfactual / numeric-interpretation: 0-1 hints (these are about thinking, not computing).

### R-solution-depth

Every solution:
1. Is organized by sub-move (use `<h3>` or `<h4>` headers matching the sub-move labels)
2. Shows EVERY algebraic step. No "we get"; no "rearranging gives"; no "by similar reasoning". If a substitution happens, show the equation before and after.
3. Names assumptions in-line, exactly when they're used (not "as before" or "assuming the usual conditions").
4. Targets **~1500 words** total. Compress only if the topic genuinely fits in less; never compress the algebra.
5. Highlights the final result of each sub-move in a `.key-result` block (renders as a HUD callout — same style as lecture `.example` blocks).

### R-difficulty-by-level

| LEARNING_STATE level | Exercise character |
|---|---|
| `seen` | Simpler compounds (3 sub-moves). Heavy hints. Main proof is a well-trodden derivation. |
| `tested` | Standard compounds (4 sub-moves). At least 1 counterfactual per set. |
| `practiced` | Full compounds (5 sub-moves). Two-method derivations dominate. Cross-module bridges allowed. |
| `mastered` | Compounds with falsification probes and unusual starting points. Sparse hints. Counterfactuals push to 3-module spans. |

---

## JSON Schema

```json
{
  "title": "Exercises: <Topic>",
  "meta": "Macroeconomics III — Module N — YYYY-MM-DD — 5 exercises",
  "coverage": {
    "module_scope": "module 1 (basic Solow)",
    "exhaustive_mutually_exclusive": true,
    "topics_covered": [
      {"exercise_id": 1, "topics": ["convergence speed", "stability"]},
      {"exercise_id": 2, "topics": ["factor shares", "Cobb-Douglas vs CES"]},
      {"exercise_id": 3, "topics": ["Golden Rule", "envelope theorem"]},
      {"exercise_id": 4, "topics": ["numeric calibration α from observed (s,r)"]},
      {"exercise_id": 5, "topics": ["transition simulation algorithm", "shock response"]}
    ],
    "topics_excluded": [
      "empirical evidence prose — handled by /exam"
    ]
  },
  "exercises": [
    {
      "id": 1,
      "title": "Convergence speed two ways",
      "scope": "Module 1 §3 (Solow law of motion), §4 (stability)",
      "sub_moves": [
        {
          "label": "Anchor",
          "prompt": "<p>Recall: in Solow with $f(k) = Bk^\\alpha$, capital per worker evolves as $\\Delta k_t = sBk_t^\\alpha - (n+\\delta)k_t$. State the two conditions on $f$ that guarantee a unique stable steady state $k^*$. (One sentence each; no derivation.)</p>",
          "hints": [
            "One condition is on the slope of $f$ as $k \\to 0$; another is on the slope as $k \\to \\infty$.",
            "These are the Inada conditions."
          ]
        },
        {
          "label": "Main proof",
          "prompt": "<p>Derive the local convergence speed $\\lambda$ — defined as the per-period rate at which $\\ln k_t - \\ln k^*$ contracts. Use the linearization-around-$k^*$ method. Show every step.</p>",
          "hints": [
            "Take logs of the Solow equation and Taylor-expand around $\\ln k^*$.",
            "The coefficient on $\\ln k_t - \\ln k^*$ is $-(1-\\alpha)(n+\\delta)$ (or $-(1-\\alpha)(n+\\delta+g)$ with technology).",
            "$\\lambda$ is the absolute value of that coefficient — but justify the sign first."
          ]
        },
        {
          "label": "Method variation",
          "prompt": "<p>Now derive $\\lambda$ a second way: treat the Solow equation as the nonlinear difference equation $k_{t+1} = \\phi(k_t)$, compute $\\phi'(k^*)$ explicitly, and connect $\\phi'(k^*)$ to your answer for $\\lambda$. Show the algebra of the connection.</p>",
          "hints": [
            "$k_{t+1} = k_t + sBk_t^\\alpha - (n+\\delta)k_t$. Differentiate at $k^*$.",
            "At a steady state, $sB(k^*)^{\\alpha-1} = n+\\delta$ — use this to simplify $\\phi'(k^*)$."
          ]
        },
        {
          "label": "Methodology reflection",
          "prompt": "<p>Each method buys you something the other doesn't. The linearization is <em>local</em>; the difference-equation method gives a <em>global</em> monotonicity statement. State the condition on $\\phi'$ for global monotone convergence and identify which method uses which assumption.</p>",
          "hints": []
        },
        {
          "label": "Counterfactual",
          "prompt": "<p>Suppose $\\alpha$ is country-specific: each country $i$ has its own $\\alpha_i \\in (0,1)$ but shares $s, n, \\delta$ with the others. Does country $i$'s convergence speed depend only on $\\alpha_i$, or does it depend on other countries' parameters too? Argue from the derivation step that's contaminated (or not) by cross-country interaction. Rapid prose, no full re-derivation.</p>",
          "hints": []
        }
      ],
      "solution": "<h3>Anchor</h3><p>The Inada conditions are ...</p><h3>Main proof</h3>...<h3>Method variation</h3>...<h3>Methodology reflection</h3>...<h3>Counterfactual</h3>..."
    }
  ]
}
```

### Notes on the schema

- **`label`** is the visible sub-move heading. Conventional values are `Anchor`, `Main proof`, `Method variation`, `Methodology reflection`, `Counterfactual`, `Falsification probe`, `Numeric inversion`, `Cross-module bridge`. The builder does not branch on label — pick what's clearest for each sub-move.
- **`prompt`** is HTML, with LaTeX in `$…$` or `$$…$$` (double-backslash in JSON).
- **`hints`** is a list of progressive hint strings. The HTML renders all hints hidden; a single button reveals them one at a time.
- **`solution`** is one HTML block. Organize it with `<h3>` per sub-move heading and use `<div class="step"><span class="step-label">Step N</span> …</div>` for each algebraic step. Use `<div class="key-result">…</div>` to highlight the final equation of each sub-move (renders as a dark HUD callout).
- **`figure`** (optional, per exercise): same spec as lecture/quiz figures. Sliders stripped automatically. `figure_anchor` selects which sub-move hosts the figure (default: the sub-move whose label starts with "Main").

---

## Pre-Build Checklist

- [ ] Confirmed scope with user (Step 2 mandatory): module + lecture files + 5-slot plan
- [ ] Read LEARNING_STATE.json and calibrated difficulty
- [ ] Read all relevant lecture files; for any garbled formula, read the sibling `.pages/p<NNN>.png`
- [ ] Exactly 5 exercises
- [ ] coverage.exhaustive_mutually_exclusive = true and defended in the audit
- [ ] No exercise drifts out of scope (R-scope audit passes)
- [ ] Every exercise has a Main proof + at least one depth-probe
- [ ] Compound shapes vary across the set (R-variation: not all 5 are identical)
- [ ] At least 1 two-method derivation; at least 1 counterfactual; at most 1 numeric
- [ ] No plug-and-chug (R-no-plug-and-chug)
- [ ] Progressive hints, ≥3 on every Main proof
- [ ] Solutions ~1500 words, sectioned by sub-move, every algebraic step shown
- [ ] Notation matches the lecture's
- [ ] JSON parses; LaTeX backslashes doubled; all IDs unique
- [ ] Audit printed verbatim in chat; every box checked
