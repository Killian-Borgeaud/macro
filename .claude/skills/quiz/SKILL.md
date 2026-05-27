---
name: quiz
description: "Generate conceptual multiple-choice quizzes from course material. Use this skill whenever the user says '/quiz', asks for a quiz, wants to test their understanding, mentions wanting practice questions, or requests MCQ/multiple-choice questions on any topic. Also triggers on requests like 'test me on [topic]', 'quiz me', 'make practice questions', 'I want to check if I understand [topic]', or any request to create assessment questions from course material. Even if the user just says something like 'can you test me' or 'I need to practice', use this skill."
---

# /quiz — Quiz Generation Skill

Generate mixed-format retrieval-practice quizzes and save them to `outputs/quizzes/`.

The exam is essay-only (see `docs/EXAM_PROFILE.md`). Quizzes are therefore a *retrieval-practice* tool, not exam mimicry — push for variety and difficulty, not format realism. `/exam` handles essay-format simulation separately.

@docs/COGNITIVE_PREFS.md
@docs/OUTPUT_CONVENTIONS.md
@docs/EXAM_PROFILE.md

## Invocation

User says `/quiz [topic or module]` optionally with a question count (default: 20). A quiz may span multiple topics or focus on one.

---

## Workflow

### Step 1 — Read calibration + state

Before generating:
- The three `@import`s above are already in context.
- Read `docs/LEARNING_STATE.json` for the topic's current level (calibrates difficulty).
- Read the relevant `Material/modules/<N>/CLAUDE.md` to find which lecture files cover the topic, then read those.

### Step 2 — Module/topic confirmation (mandatory)

Before generating, **state which module(s) and which specific lecture files you will draw from**, and ask the user to confirm. Example:

> "Generating 20 questions on **module 1 (basic Solow)** from `Lecture 1a.md`, `Lecture 1b.md`, `Lecture 1c.md`. Topics covered: production function, capital accumulation, steady state, convergence. Ready?"

This catches the most damaging failure mode — silently drawing from the wrong module. If the user asked for "module 1" but the closest material is in module 2, surface that mismatch *before* generating, not after.

If the user says "go", proceed. No fixed type ratios — pick types that fit the material.

### Step 3 — Generate JSON

Author the JSON payload following the format in **JSON Schema** below. Apply every rule in **Question Design Rules** and **Soft Constraints**.

### Step 4 — Length-bias and stem-bias verification (mandatory)

Before building, verify every question:
- **Length parity**: correct answer's word count is within ±30% of the shortest distractor.
- **Boundary-stem check**: the stem does NOT name the concept being tested. Stems describe scenarios/symptoms; choices name concepts. If the stem says "What is the Solow steady state?" — rewrite as "An economy has $\dot k = 0$ and $\dot K / K = n$. Which property is implied?"
- **Distractor-defense field present** on every choice (correct included). If you cannot write a one-line "why a partial-understander picks this" for any choice, that choice is filler — rewrite it.
- **No type used more than 30% of the quiz** (e.g. in a 20-Q quiz, no type appears more than 6 times).

### Step 5 — Build

```powershell
# Write payload to temp, then build:
$tmp = Join-Path $env:TEMP "quiz_payload.json"
# (write JSON to $tmp)
python tools/build_quiz.py $tmp outputs/quizzes/<slug>_<YYYY-MM-DD>.html
```

The builder will print `WARNINGS:` to stderr if anything looks off (duplicate IDs, type/correct mismatch, missing figure runtime). Fix and rebuild before showing the user.

### Step 6 — Update LEARNING_STATE.json

Mark covered topics: if previously `seen`, advance to `tested`. Never downgrade.

### Step 7 — Process results (next conversation)

When the user pastes the quiz JSON export into chat, parse it and update `LEARNING_STATE.json` per `docs/OUTPUT_CONVENTIONS.md` thresholds (score ≥80% twice → `mastered`, ≥70% → `practiced`, ≥50% → at least `tested`, <50% → no downgrade). Note specific subtopics missed for targeted follow-up.

---

## Question Type Catalogue

11 types. Pick what fits the topic — do not force one of each.

### Single-MCQ types (correct: "B")

| Type | When to use |
|---|---|
| `boundary` | Concept has a precise scope; test what it does NOT imply. *"Gauss-Markov guarantees BLUE. Which is NOT implied?"* |
| `flaw` | Student-style argument with a subtle error; identify the wrong step. *"A student says X — what's wrong?"* |
| `deep-short` | One-line setup (often a small numeric or symbolic clue) whose correct interpretation requires deep understanding. *"$E[\hat\theta_N] = \theta + 2/N$. The estimator is..."* |
| `measure` | Formula or symbol shown; ask what it actually represents (not just what it equals). *"In $\text{Var}(\hat\beta_j) = \sigma^2/[\text{SST}_j(1-R^2_j)]$, the quantity $R^2_j$ is..."* |
| `bridge` | Two concepts from different modules connect mechanically (not just analogously). Always include the `connection` field. |
| `numeric` | Compute a clean-number answer; choices are 4 numbers. Renders in JetBrains Mono. Solution must require *conceptual setup*, not just arithmetic. |
| `graph` | Static Plotly chart embedded in stem with labeled points or curves. Two flavors: identify ("which point is k*?") or predict ("if s rises, where does the intersection move?"). Requires a `figure` field. |
| `derivation-justify` | Show a 3-5 step derivation with one step highlighted; ask which rule/assumption justifies that step. Requires `derivation` + `highlight`. |
| `derivation-source` | Show a final identity in the stem; ask which derivation produces it. Choices are alternative derivation paths. Requires no `derivation` field on the stem (it's in the choices). |
| `derivation-why` | Show an identity; ask which mechanism makes it true (distinguishes accounting identities from behavioral conditions, etc.). |

### Multi-answer types

| Type | When to use |
|---|---|
| `multi-select` | At least 2 of 4 options are correct; user must pick all and only the correct ones. Scored all-or-nothing; partial feedback shown on reveal. Use for "select all that apply" style or to defeat process-of-elimination. |
| `mtf-cluster` | **The highest-value type.** A shared setup (1-3 sentences) followed by 4 short statements, each independently T/F. Tests a tight family of micro-misconceptions for the cost of one stem. Matches the user's preferred exam-style format. **Use heavily**: 25-40% of any quiz should be MTF clusters once the topic supports it. Each statement gets its own `defense` field. |

---

## Soft Constraints

The generator chooses freely, with **only these floors**:

1. **MTF clusters carry the quiz.** Aim for **25-40% of questions to be `mtf-cluster`** — the user's preferred format, and the highest signal-per-stem type. Don't drop below 25% unless the topic genuinely doesn't support T/F statement clusters.
2. **At least 1 `bridge` question** — cross-topic connections are non-negotiable.
3. **At least 1 `derivation-*` question** on any topic with formal results. The user is here to learn proofs, not definitions.
4. **No single type exceeds ~35% of questions** — keeps variety. MTF is the exception (allowed up to 40%).
5. **1 scenario chain when the topic supports it.** Skip if forced.
6. **Default total: 20 questions.** User can override.

Beyond these floors, let the topic drive the mix.

### Productive-failure mode (default ON)

All quizzes ship with choices hidden by default — the user sees the stem, thinks about the answer, then clicks "Reveal options" to see the choices. This is baked into the template; no JSON flag controls it. **Implication for stem writing**: stems must be self-sufficient enough to be answerable mentally. Never write stems whose meaning only becomes clear after seeing the options (e.g. "Which of the following best describes…" — bad; "An economy has $\dot k = 0$. What does this imply for $r$?" — good).

---

## Question Design Rules

Every question must satisfy all 8 rules.

### Rule 1 — Boundary, not center

Test where understanding breaks down. Instead of "What is unbiasedness?", ask "Which estimator is unbiased but inconsistent?"

### Rule 2 — Every distractor independently plausible

Each wrong answer is a misconception a partial-understander would pick. Mandatory `defense` field per choice documents this. Types of good distractors: sign errors, scope errors (theorem overreach), condition swap (correct result, wrong assumption set), partial truth (true in a special case), plausible-but-flawed reasoning chain.

**The "Gini" failure mode (don't repeat):** in a question about Solow-model stylized facts, one of the four choices was "Gini coefficient". This is **on a different topic entirely** — no student conflates it with growth-model facts. The question collapses to 3 real options and trivial process-of-elimination. **All four distractors must live inside the topic's conceptual neighborhood** — same module, related family of misconceptions. If a distractor is from a different module/chapter, it's filler and the question is solved before it's read.

**Never use**: obviously absurd options, joke answers, "all of the above", "none of the above", "less correct" alternatives, distractors from a different topic family.

### Rule 3 — No giveaway patterns

- **Length parity**: all choices within ±30% word count.
- **Tone parity**: same register/technicality across choices. If correct answer uses a formula, ≥2 distractors should too.
- **Position distribution**: A/B/C/D distributed roughly evenly across the quiz; never 3+ same letter in a row.
- **Hedging parity**: don't make the correct answer the only one with "may/can/under certain conditions" or the only one with "always/never".

### Rule 4 — Boundary-stem (NEW)

Stems describe symptoms/scenarios; concepts are named only in the choices. Bad: *"Define conditional convergence."* Good: *"Two countries with the same $s,n,\delta,\alpha$ have different $k_0$. They will..."* — forces recognition, not recall.

### Rule 5 — Distractor defense field (NEW)

Every choice (including the correct one) has a `defense` field. If you cannot write a one-line plausibility argument, the distractor is filler.

### Rule 6 — Conceptual default + inverted numerics

Default mode is conceptual. `numeric` questions are *allowed* without user request, but they must test **inversion**, not arithmetic.

**Banned numeric pattern (the Q11 failure mode):**
> *"With $\alpha=0.3$, $s=0.2$, $n=0.01$, $\delta=0.04$, $k^* = (s/(n+\delta))^{1/(1-\alpha)} = ?"*

This is a calculator test. Even if the formula is omitted, the question is one substitution away from arithmetic.

**Required numeric pattern (solve-backwards):**
> *"A Cobb-Douglas economy is at the Golden Rule with $k^*=4$ and $\delta = 0.05$, no population growth. What is $\alpha$?"*

The student must (a) recognize Golden Rule ⇒ $\text{MPK} = n + \delta$, (b) write $\alpha (k^*)^{\alpha-1} = \delta$, (c) solve for $\alpha$. Tests *understanding of which direction the formula pushes* — not arithmetic.

Other valid patterns: given an observed outcome (e.g. $r^* = 0.08$), recover a parameter; given two steady states, find the parameter difference between them; given a numerical claim, identify which assumption it depends on.

**Rule of thumb**: if you can solve the question by typing into a calculator without thinking, it fails.

### Rule 7 — Cross-topic connections

At least 1 of every quiz is a `bridge` (more for longer quizzes). Bridges require *mechanical* links — concrete algebraic or logical connection between two modules — not aesthetic analogies.

### Rule 8 — Difficulty targeting

Well-prepared student should get 60-75% on first attempt. 90%+ means too easy; <50% means tests unseen material. Use `LEARNING_STATE.json` to calibrate (see escalation table below).

### Difficulty escalation by LEARNING_STATE level

| Level | Style emphasis | Target score |
|---|---|---|
| `seen` | `boundary`, `measure`, easy `deep-short`, easy `numeric` | 65-75% |
| `tested` | Harder `boundary` + `flaw`, first `bridge`, first `multi-select` | 55-65% |
| `practiced` | Heavy `bridge`, scenario chains, `derivation-*`, prediction-style `graph` | 50-60% |
| `mastered` | Adversarial distractors, edge cases, `multi-select` with 3 correct answers, chains 3-deep | 45-55% |

---

## JSON Schema

```json
{
  "title": "Quiz: <Topic>",
  "meta": "Macro III — <module> — YYYY-MM-DD",
  "questions": [
    { /* single question */ },
    { "type": "chain", "setup": "<html>", "questions": [ /* questions */ ] }
  ]
}
```

### Single-MCQ question (boundary, flaw, deep-short, measure, bridge, numeric)

```json
{
  "id": 1,
  "style": "boundary",
  "topic": "Solow steady state",
  "stem": "<p>HTML with KaTeX: $f(k) = k^\\alpha$</p>",
  "choices": [
    {"letter": "A", "text": "...", "defense": "why a partial-understander picks this"},
    {"letter": "B", "text": "...", "defense": "..."},
    {"letter": "C", "text": "...", "defense": "..."},
    {"letter": "D", "text": "...", "defense": "..."}
  ],
  "correct": "B",
  "explanation": "<p>Why B is right. Why each distractor fails.</p>",
  "connection": "Optional — required for style=bridge"
}
```

### Multi-select question

```json
{
  "id": 6,
  "style": "multi-select",
  "topic": "Kaldor facts",
  "stem": "<p>Which of these are stylized facts of growth? <strong>Select all that apply.</strong></p>",
  "choices": [ ... 4 choices each with defense ... ],
  "correct": ["A", "B", "C"],
  "explanation": "<p>...</p>"
}
```

### Graph question

```json
{
  "id": 8,
  "style": "graph",
  "topic": "Solow diagram",
  "stem": "<p>Four points are marked below. Which is the steady state?</p>",
  "figure": {
    "id": "fig-q8",
    "params": {"s": 0.3, "alpha": 0.3, "n": 0.01, "delta": 0.04},
    "x_range": [0, 30], "n_points": 200,
    "x_label": "k", "y_label": "",
    "curves": [
      {"name": "s·f(k)",  "expr": "s * Math.pow(k, alpha)", "color": "#0FA4AF"},
      {"name": "(n+δ)·k", "expr": "(n + delta) * k",       "color": "#964734"}
    ],
    "markers": [
      {"type": "intersection", "curves": [0, 1], "label": "B", "color": "#003135"},
      {"type": "label_point", "x": "5", "y": "s * Math.pow(5, alpha)", "label": "A", "color": "#003135"}
    ]
  },
  "choices": [ ... ],
  "correct": "B",
  "explanation": "<p>...</p>"
}
```

Figure spec uses the same format as lecture figures (see `tools/build_figure.py`), but **the builder strips any `sliders` field** — quiz graphs are always static. Use the lecture palette: `#024950` (accent), `#0FA4AF` (cyan), `#964734` (key), `#003135` (text).

### Derivation question

```json
{
  "id": 9,
  "style": "derivation-justify",
  "topic": "Solow law of motion",
  "stem": "<p>The derivation below leads to the per-worker law of motion. Which step justifies line (3)?</p>",
  "derivation": [
    "K_{t+1} = (1-\\delta) K_t + s Y_t",
    "k_{t+1} = K_{t+1}/L_{t+1}",
    "k_{t+1}(1+n) = (1-\\delta) k_t + s f(k_t)",
    "\\Delta k_t \\approx s f(k_t) - (n+\\delta) k_t"
  ],
  "highlight": 3,
  "choices": [ ... ],
  "correct": "A",
  "explanation": "<p>...</p>"
}
```

- `derivation` strings are LaTeX (no `$`) — rendered in JetBrains Mono with KaTeX.
- `highlight` is 1-indexed; only used by `derivation-justify` (the other two derivation styles don't need it since the question is about the *result*, not an intermediate step).

### MTF cluster (multiple true-false)

```json
{
  "id": 4,
  "style": "mtf-cluster",
  "topic": "Solow steady state",
  "setup": "<p>A Cobb-Douglas Solow economy with $\\alpha = 0.3$ sits at its steady state with saving rate $s = 0.25$. Evaluate each statement.</p>",
  "statements": [
    {"letter": "A", "text": "Capital per worker $k$ is constant.", "true": true,
     "defense": "Definition of steady state: $\\dot k = 0$."},
    {"letter": "B", "text": "Output per worker $y$ grows at rate $g$.", "true": false,
     "defense": "Without technology in the model, $y$ is constant in steady state. Picked by students who conflate basic Solow with the Solow-with-technology variant."},
    {"letter": "C", "text": "The economy is at the Golden Rule.", "true": false,
     "defense": "Golden Rule requires $s = \\alpha = 0.3$, but here $s = 0.25$. Tempting because 'steady state' and 'Golden Rule' are introduced near each other."},
    {"letter": "D", "text": "$r = \\alpha(n+\\delta)/s$.", "true": true,
     "defense": "Substitute $k^* = (s/(n+\\delta))^{1/(1-\\alpha)}$ into $r = \\alpha k^{\\alpha-1}$. Holds at the steady state regardless of whether it's Golden Rule."}
  ],
  "explanation": "<p>The cluster targets the four most common Solow confusions: (i) what 'steady state' actually constrains, (ii) the role of technology in producing growth in $y$, (iii) the difference between any steady state and the Golden Rule, (iv) the steady-state rental-rate formula.</p>"
}
```

- **Always 4 statements.** Each independently true or false. Mix at least 1 true and 1 false (a cluster of all-true or all-false is too easy to spot).
- Statements share the setup, but each one must be **logically independent** of the others — solving statement A should not commit you to a particular answer on B.
- Each statement gets a `defense` (rendered under the statement on reveal). For false statements, the defense should explain *who picks this and why they're wrong*. For true statements, why a doubter rejects it.
- The cluster's `explanation` is the final wrap-up — the meta-takeaway across all four statements. Use it to surface the *family* of misconceptions the cluster targets.
- Scoring: all-or-nothing per cluster (matches existing multi-select convention).

### Chain (scenario) block

```json
{
  "type": "chain",
  "setup": "<p><strong>Setup.</strong> A closed economy with $\\alpha = 0.3$, $\\delta = 0.05$... The saving rate permanently rises from 0.2 to 0.3.</p>",
  "questions": [
    { /* question with id 12 */ },
    { /* question with id 13, builds on Q12 */ }
  ]
}
```

- Chains contain 2-3 questions. IDs are globally sequential (chain doesn't reset).
- Q2 should logically build on Q1 (e.g. Q1 establishes a fact, Q2 computes with it).
- Chains count toward total question count and toward type quotas.

---

## Explanation Quality

Every `explanation` field must:
1. State why the correct answer is right (1-2 sentences).
2. State why each distractor is wrong (1 sentence each, specific).
3. For `bridge` style: explain the cross-topic mechanism in `connection`.

Per-choice `defense` fields are also rendered under each choice on reveal — they teach why each option was tempting. Treat them as part of the explanation, not metadata.

---

## Pre-Build Checklist

- [ ] Confirmed module/topic with user before generating (Step 2 mandatory)
- [ ] Read `LEARNING_STATE.json` and calibrated difficulty
- [ ] Read relevant `Material/modules/<N>/CLAUDE.md` + lecture files **from the confirmed module**
- [ ] If lecture files have `<!-- formula-not-decoded -->` or scrambled tokens on a referenced equation, read the corresponding `.pages/p<NNN>.png`
- [ ] ≥25% of questions are `mtf-cluster` (unless topic genuinely doesn't support it)
- [ ] ≥1 `bridge` and ≥1 `derivation-*`
- [ ] Optional chain block if topic supports it
- [ ] Every choice/statement has `defense` field
- [ ] Every stem describes a scenario, not a concept name; stems are answerable without seeing choices (productive-failure compatible)
- [ ] All distractors live inside the topic's conceptual neighborhood — no "Gini in a Solow question"
- [ ] No numeric question is solvable by typing into a calculator (inverted-numerics rule)
- [ ] Length parity within ±30% across all choices
- [ ] Correct-letter positions distributed roughly evenly
- [ ] No "all of the above", no "none of the above"
- [ ] Multi-select: `correct` is an array, not a string
- [ ] MTF clusters: exactly 4 statements, mix of true and false, each with `defense`
- [ ] Graph questions: `figure.markers` use palette colors, no `sliders`; `label_point` markers actually render labels (verified in preview)
- [ ] Derivation questions: `derivation` is a list of LaTeX strings (no `$`)
- [ ] All IDs unique across the flattened question list (including inside chains)
