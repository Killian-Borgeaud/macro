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

### Step 2 — Plan and confirm

Present a one-line plan:
> "I'll generate 20 questions covering [topic list], mixed across types. Ready?"

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

### Multi-answer type (correct: ["A", "C"])

| Type | When to use |
|---|---|
| `multi-select` | At least 2 of 4 options are correct; user must pick all and only the correct ones. Scored all-or-nothing; partial feedback shown on reveal. Use for "select all that apply" style or to defeat process-of-elimination. |

---

## Soft Constraints

The generator chooses freely, with **only these floors**:

1. **At least 1 `bridge` question** — cross-topic connections are non-negotiable.
2. **At least 1 question from a new-format type** (`multi-select`, `numeric`, `graph`, or any `derivation-*`) — prevents silent regression to single-MCQ-only quizzes.
3. **No single type exceeds ~30% of questions** — keeps variety without forcing balance.
4. **1 scenario chain when the topic supports it** (a shared setup + 2 linked questions). Skip if forced.
5. **Default total: 20 questions.** User can override.

Beyond these floors, let the topic drive the mix. Solow-mechanics quizzes will naturally lean graph + derivation + numeric; empirical-evidence quizzes will lean boundary + flaw + multi-select.

---

## Question Design Rules

Every question must satisfy all 8 rules.

### Rule 1 — Boundary, not center

Test where understanding breaks down. Instead of "What is unbiasedness?", ask "Which estimator is unbiased but inconsistent?"

### Rule 2 — Every distractor independently plausible

Each wrong answer is a misconception a partial-understander would pick. Mandatory `defense` field per choice documents this. Types of good distractors: sign errors, scope errors (theorem overreach), condition swap (correct result, wrong assumption set), partial truth (true in a special case), plausible-but-flawed reasoning chain.

**Never use**: obviously absurd options, joke answers, "all of the above", "none of the above", "less correct" alternatives.

### Rule 3 — No giveaway patterns

- **Length parity**: all choices within ±30% word count.
- **Tone parity**: same register/technicality across choices. If correct answer uses a formula, ≥2 distractors should too.
- **Position distribution**: A/B/C/D distributed roughly evenly across the quiz; never 3+ same letter in a row.
- **Hedging parity**: don't make the correct answer the only one with "may/can/under certain conditions" or the only one with "always/never".

### Rule 4 — Boundary-stem (NEW)

Stems describe symptoms/scenarios; concepts are named only in the choices. Bad: *"Define conditional convergence."* Good: *"Two countries with the same $s,n,\delta,\alpha$ have different $k_0$. They will..."* — forces recognition, not recall.

### Rule 5 — Distractor defense field (NEW)

Every choice (including the correct one) has a `defense` field. If you cannot write a one-line plausibility argument, the distractor is filler.

### Rule 6 — Conceptual default

Default mode is conceptual. `numeric` questions are *allowed* without user request, but require conceptual setup (no pure arithmetic).

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

- [ ] Read `LEARNING_STATE.json` and calibrated difficulty
- [ ] Read relevant `Material/modules/<N>/CLAUDE.md` + lecture files
- [ ] If lecture files have `<!-- formula-not-decoded -->` or scrambled tokens on a referenced equation, read the corresponding `.pages/p<NNN>.png`
- [ ] Planned topic distribution
- [ ] ≥1 `bridge`, ≥1 new-format type, no type >30%
- [ ] Optional chain block if topic supports it
- [ ] Every choice has `defense` field
- [ ] Every stem describes a scenario, not a concept name
- [ ] Length parity within ±30% across all choices
- [ ] Correct-letter positions distributed roughly evenly
- [ ] No "all of the above", no "none of the above"
- [ ] Multi-select: `correct` is an array, not a string
- [ ] Graph questions: `figure.markers` use palette colors, no `sliders`
- [ ] Derivation questions: `derivation` is a list of LaTeX strings (no `$`)
- [ ] All IDs unique across the flattened question list (including inside chains)
