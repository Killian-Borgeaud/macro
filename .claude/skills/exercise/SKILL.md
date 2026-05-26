---
name: exercise
description: "Generate numerical/computational exercise sets with worked solutions. Use this skill whenever the user says '/exercise', asks for practice problems, wants to drill computations, mentions wanting to practice applying formulas, or requests worked examples. Also triggers on 'give me problems on [topic]', 'I need to practice computing [topic]', or any request for hands-on problem sets. Exercises are 'I can do it' — distinct from quizzes which are 'I understand it'."
---

# /exercise — Exercise Generation Skill

Generate HTML exercise sets with worked solutions. Save to `.claude/output/exercises/`.

Exercises test **computation and application** — the user must derive, calculate, or prove something by hand. This is distinct from `/quiz` (conceptual understanding via MCQ).

## Invocation

User says `/exercise [topic]` optionally with a count (default: 5).

## Workflow

### Step 1 — Read context

Read these files (in this order):
- `.claude/CONVENTIONS.md` — naming, folder structure, output rules, **canonical level definitions**
- `LEARNING_STATE.json` — current understanding per topic
- `subject-config.md` — subject context, exam scope, `[exercise_style]` calibration section
- All course material files relevant to the requested topic

### Step 2 — Calibration (first use only)

If no `[exercise_style]` in subject-config.md:
1. Generate 5 sample exercises with different styles (see calibration archive below)
2. User grades. Write calibrated style to subject-config.md under `## Calibration` → `[exercise_style]`.

### Step 3 — Plan exercises

For a default 5-exercise set, use this distribution:

| Category              | Count | Description                                                                |
|-----------------------|-------|----------------------------------------------------------------------------|
| **connection-forcing**| 2–3   | Compute-style. Requires linking two concepts not usually taught together.  |
| **standard drill**    | 1–2   | Compute-style. Direct application of one concept with realistic numbers.   |
| **derive / prove**    | 1–2   | Show/prove a result algebraically. Step-labeled proof.                     |

The **connection-forcing** exercises are the backbone — they should feel non-trivial and reveal something insightful, not just be hard. Standard drill rounds out the set but never dominates.

**Every exercise gets progressive hints:**
- **Compute exercises:** 1–3 hints. First hint reframes the problem, second gives the key setup.
- **Derive exercises:** 3–4 hints (mandatory minimum 3). Each hint scaffolds one conceptual or algebraic move. A derivation with only 2 hints is too sparse — the student needs a path through the proof, not just the start and end.

### Step 4 — Generate exercises

For each exercise, produce:
- A problem statement (may include data tables, given values, specific numbers)
- 1–3 progressive hints
- Step-by-step solution with labeled steps (every algebraic step explicit)
- Final answer clearly boxed

### Exercise Design Rules

1. **No sub-part scaffolding.** Each exercise is ONE problem, ONE answer. Never break into (a), (b), (c) unless the user explicitly asks.

2. **No plug-and-chug.** If the exercise can be solved by substituting numbers into a formula with no thought, it's too easy. The problem should require choosing the right approach, connecting two concepts, or recognizing a non-obvious setup.

3. **Force new links (highest-value rule).** The best exercises require the student to connect concepts that aren't usually presented together, or apply a familiar formula in an unfamiliar context. The goal is *insight* — the student should finish and think "I didn't realize these two things were related." This matters more than raw difficulty.

4. **Concrete, not abstract.** Give specific numbers, datasets, or scenarios. Avoid "consider a general model with k regressors" — instead, give `k = 4`, `n = 120`, actual coefficient values.

5. **Clean-but-not-round numbers.** Avoid trivially round numbers (100, 0.5, 1.0) but also avoid gratuitously long decimals that add nothing (0.7287, 0.5065). When the conceptual point doesn't depend on messy arithmetic, prefer numbers that simplify cleanly — e.g., priors of (0.4, 0.6) instead of (0.45, 0.55), or signal probabilities that produce integer-ratio posteriors. Reserve ugly decimals for exercises where realistic messiness is the point (e.g., calibration from real data).

6. **Derivation depth: test understanding, not identity recall.** A derivation exercise that amounts to "apply integration by parts and sign the result" is too mechanical — it tests whether the student knows the identity, not whether they understand the concept. The best derivation exercises require the student to *construct* an argument: set up the right objects, choose the proof strategy, and connect intermediate results to reach a non-obvious conclusion. If the proof can be summarised as "apply identity X, simplify, sign" it is too shallow. Prefer exercises where the student must decide *what to prove as an intermediate step*, or where the algebraic structure reveals a conceptual surprise.

7. **Derivation exercises need 3–4 hints.** A derivation without sufficient hints is a wall. Provide at least 3 hints: the first orients the overall approach, the middle hints each scaffold one algebraic or conceptual move, the last hint gives the final key step before the result. Two hints for a proof is never enough.

8. **Solutions show every step.** Never "it follows that" or "by simplification." Write out every algebraic manipulation. Label each step.

### Difficulty scaling by LEARNING_STATE level

| Level          | Exercise character                                                     | Target solve rate |
|----------------|------------------------------------------------------------------------|-------------------|
| `not_covered`  | Do not generate — user hasn't seen the topic                           | —                 |
| `seen`         | Direct application of one concept, but with non-obvious numbers        | 80–90%            |
| `tested`       | Requires connecting two related concepts                               | 65–80%            |
| `practiced`    | Multi-step, may cross topics, derivations at this level                | 50–65%            |
| `mastered`     | Edge cases, subtle proofs, exam-level composites                       | 40–55%            |

### Step 5 — Build the HTML

1. Generate JSON payload:
```json
{
  "title": "Exercises: [Topic]",
  "meta": "[Subject] — [Date] — [N] exercises",
  "exercises": [
    {
      "id": 1,
      "style": "compute",
      "title": "Exercise 1: [short description]",
      "problem": "<p>Given \\(n = 526\\) observations...</p>",
      "hints": [
        "Think about what happens to the F-statistic denominator as you add regressors.",
        "Compare the change in SSR to the change in degrees of freedom."
      ],
      "solution_steps": [
        {"label": "Step 1", "html": "<p>First, compute the unrestricted SSR...</p>"},
        {"label": "Step 2", "html": "<p>The F-statistic is...</p>"}
      ],
      "answer": "\\(F = 5.02\\), reject at 5%"
    }
  ]
}
```

2. Write JSON to `/tmp/exercise_payload.json`
3. Run: `python .claude/scripts/build_exercise.py /tmp/exercise_payload.json .claude/output/exercises/[filename].html`
4. Copy output to workspace root for `computer://` link
5. Present file link to user

### Step 6 — Update LEARNING_STATE

For each topic covered, set level to at least `practiced` (never downgrade).

### File naming

Follow `.claude/CONVENTIONS.md`: `[topic-slug]_[YYYY-MM-DD].html`

---

## Anti-patterns (never do these)

| Anti-pattern                        | Why it's bad                                              |
|-------------------------------------|-----------------------------------------------------------|
| Sub-parts (a), (b), (c), (d)       | Breaks the problem into trivial plug-and-chug steps       |
| "Figure out what to compute"        | Too abstract, user wants a concrete target                |
| Derivation with only 2 hints       | Too sparse — proofs need 3-4 granular hints minimum       |
| Round numbers everywhere            | Feels fake, doesn't prepare for real exam data            |
| Scaffolded walkthroughs             | Exercise should test if user can set up, not hold hand    |
| Set dominated by standard drill     | Boring — standard exercises are filler (max 1-2 per set)  |
| Hard but uninsightful               | Difficulty without insight is just tedious                |

## Calibration archive

### Round 1 (2026-04-14) — 5 style archetypes:
- A (scaffolded sub-parts): 3/10 — "too many computations for something easy"
- B (single block, direct): 7/10 — "non-standard, forces new links"
- C (progressive hints): 5/10 — "trivial question, but hints are great"
- D (scenario-driven extraction): 4/10 — "too abstract"
- E (derivation/prove): 8/10 — "very good for 1-2 per set, needs hints"

### Round 2 (2026-04-14) — 10 cross-subject exercises:
- Ex1 (law + compound interest): 6/10 — "seems fine"
- Ex2 (log-level elasticity): 6/10 — "a bit easy but interesting"
- Ex3 (OLS inconsistency proof): 8/10 — "very interesting and non-trivial relation. Hints are a bit weak (could use more hints for proofs)"
- Ex5 (adjusted R² decrease): 6/10 — "a bit standard but useful to have a few of those in each set"
- Ex6 (Cournot Nash equilibrium): 6/10 — "good for heavy drill but very standard"
- Ex10 (eigenvalue PD condition): 7/10 — no comment

### Derived rules:
- **Insight > difficulty.** Non-trivial relations score 8/10; hard-but-standard scores 6/10.
- **Derivation hints must be 3-4 minimum**, each scaffolding one conceptual move.
- **Standard drill is acceptable filler** (1-2 per set) but must never dominate.
- **Connection-forcing exercises are the backbone** (2-3 per set of 5).
- Default distribution: 2-3 connection-forcing compute + 1-2 standard drill + 1-2 derive with 3-4 hints.
