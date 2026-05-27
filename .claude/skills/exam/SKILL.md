---
name: exam
description: "Generate a full essay-style mock exam matching Prof. Cozzi's format (4 questions, 25% each, ~20 min per question). Use this skill whenever the user says '/exam', asks for an exam simulation, wants exam-style practice, mock exam, or exam training. Also triggers on 'simulate the exam', 'exam practice on [topic]', 'mock test', 'full exam', or any request for timed essay simulation. Distinct from /quiz (MCQ recognition) and /exercise (deep proof drilling)."
---

# /exam — Exam Simulator

Generate a 4-question essay-style mock exam matching Prof. Cozzi's format, then save to `outputs/exams/`.

The mock exam (`Material/mock exam/Mock_Exam-1.pdf`) shows the format precisely: **4 essay questions, 25% each, ~90 minutes total**. No MCQ. No T/F. No sub-parts. Each question has a **technical component + interpretive component** (Derive + discuss, Explain + sketch, Describe + critique, Derive + intuition).

This skill simulates *that* test. Use it late in the study cycle for fluency under time pressure — it is not a learning tool, it is a self-assessment tool. **No hints during the exam.** The user reads each prompt, drafts an answer (mentally or on paper, ~20 min per question), then reveals the skeleton to self-check coverage, then the full model answer for comparison.

@docs/COGNITIVE_PREFS.md
@docs/OUTPUT_CONVENTIONS.md
@docs/EXAM_PROFILE.md

## Invocation

User says `/exam` (full 4-question simulation across modules, mirroring the mock's module distribution: M1, M3, M5, M6 by default) or `/exam <module-list>` to focus.

---

## Workflow

### Step 1 — Read context

The three `@import`s above are already in context. Also read:
- `docs/LEARNING_STATE.json` — used only to pick the *trickiest* angle per module (the user's weak spots from recent quizzes)
- `Material/mock exam/Mock_Exam-1.pdf` (or its `.md` sibling if extracted) — the canonical reference for verb-pair phrasing and prompt length
- `Material/modules/<N>/CLAUDE.md` + relevant lecture files for the modules in scope

### Step 2 — Confirm scope

State which 4 modules you'll target and the verb-pair for each. Default mirrors the mock: M1 (describe+critique), M3 (explain+sketch), M5 (derive+discuss), M6 (derive+intuition). Wait for "go" or revisions.

Example:

> "Generating a full mock-style exam. 4 questions, 25% each, ~20 min target per question:
> - **Q1 — M1, describe + critique**: empirical evidence for/against basic Solow
> - **Q2 — M3, explain + sketch**: Solow with land + numerical simulation
> - **Q3 — M5, derive + discuss**: Cozzi (2017) hybrid + policy implications
> - **Q4 — M6, derive + intuition**: Solow conditions of efficiency wages
>
> Match the mock exactly. Ready?"

If the user asks for `/exam M1 M2` (different module set), substitute accordingly — but keep the verb-pair distribution diverse (don't generate 4 "derive + discuss" in a row).

### Step 3 — Generate JSON

Author the JSON per the schema below. Apply all Design Rules.

### Step 4 — Self-audit (mandatory before build)

Print the audit verbatim in chat. Every box must check.

```
## Exam Audit

### Format fidelity (mock-exam matching)
- [ ] Exactly 4 questions
- [ ] All weights 25%; total = 100%
- [ ] target_minutes per question ≈ 20 (acceptable 18-25); sum ≈ 80-90
- [ ] Each prompt is 2-4 lines, declarative, Cozzi-style — no scaffolded sub-parts
- [ ] Each question has a verb-pair tag (technical + interpretive)
- [ ] Verb pairs across the 4 questions are diverse — not all "derive"

### Prompts
- [ ] No "discuss in detail" / "explain comprehensively" filler. Cozzi's mock is terse.
- [ ] Specific named results / models cited where the mock does (e.g. "Cozzi (2017)
      hybrid model", "Solow conditions of efficiency wages")
- [ ] Topic stays inside the cited module(s)

### Skeleton (the self-check helper)
- [ ] Every question has a `skeleton` field with 4-6 bullet points
- [ ] Each bullet is a point a full-credit answer must cover (not a hint to a sub-step)
- [ ] Skeleton bullets are PROSE summaries, not algebra fragments — they tell the
      reader "did you cover X?", not "do this calculation"

### Model answer
- [ ] Every question has a `model_answer` field
- [ ] Length: 600-800 words (exam-realistic — not the 1500-word /exercise length)
- [ ] Organized with <h3> sub-section headers when the answer has natural sections
- [ ] Uses <div class="key-result">...</div> to highlight final equations / conclusions
- [ ] Algebra is woven into prose (not labor-by-labor like /exercise solutions);
      key derivation steps shown, micro-steps elided — this is what graded essays look like
- [ ] Empirical claims are concrete (numbers, country examples) where the question
      asks for "evidence"

### Notation and style
- [ ] Symbols match the lecture's notation conventions
- [ ] Each "Derive + …" answer hits its key result in the body, not just the skeleton
- [ ] "Discuss policy" / "Give intuition" sections are 100-200 words each — substantive
      paragraphs, not afterthoughts

### Technical
- [ ] JSON parses; LaTeX backslashes doubled
- [ ] All question IDs unique
- [ ] No HTML in skeleton bullet text (skeleton is plain prose)
```

### Step 5 — Build

```powershell
$tmp = Join-Path $env:TEMP "exam_payload.json"
# (write JSON to $tmp)
python tools/build_exam.py $tmp outputs/exams/<slug>_<YYYY-MM-DD>.html
```

Smoke checks: 4-question count, target-time consistency, no empty prompts or model answers, verb-pair present on every question.

### Step 6 — Update LEARNING_STATE.json

When the user reports having gone through an `/exam` simulation (self-grading by comparison to model answers), advance every covered topic by one level (capped at `mastered`). Never downgrade.

---

## Design Rules

### R-format: 4 questions, 25% each, terse Cozzi phrasing

The real mock has prompts like:
> "Describe the main empirical evidence supporting and contradicting the basic Solow model."
> "Derive the 'Solow conditions' of the efficiency wages model and give an intuitive explanation of them."

Each is 1-2 lines, declarative, no instructions about answer length. Match this style. **Do not** write prompts like "In a 600-word essay, carefully explain X with three examples." That's a different course's style.

### R-verb-pair: technical + interpretive, always

Every question has both halves. The five canonical verb-pairs (observed in the mock plus one plausible extension):

| Verb pair | Technical half | Interpretive half | Mock example |
|---|---|---|---|
| `describe + critique` | Describe a body of evidence | Discuss what supports / contradicts | Q1 |
| `explain + sketch` | Explain a model | Sketch how to simulate it numerically | Q2 |
| `derive + discuss` | Derive a result formally | Discuss policy / economic implications | Q3 |
| `derive + intuition` | Derive a result formally | Give an intuitive explanation | Q4 |
| `compare + judge` | Compare two models | Judge which better explains a phenomenon | (extension; not on mock but plausible) |

### R-skeleton: 4-6 bullets per question, prose summaries

The skeleton tells the user "did you remember to cover X?" — it is NOT a step-by-step hint chain. Each bullet is a coverage point: "Define what 'basic Solow' predicts (steady state in *levels*, not growth rates)" or "Resolution: conditional vs absolute convergence". The user reveals the skeleton AFTER drafting an answer to self-check coverage; they should not see it during the attempt.

### R-model-answer: 600-800 words, exam-quality

Model answers reflect what a graded exam essay looks like:
- **600-800 words** total (≈ what fits in 20 minutes on paper)
- Equations woven into prose, not labor-by-labor algebra (that's `/exercise`)
- Key derivation steps shown; micro-steps elided
- `<h3>` sub-headers when there's a natural sectioning (e.g. "Supporting evidence" / "Contradicting evidence")
- `<div class="key-result">…</div>` for the final identity / steady-state formula / Solow condition
- Empirical content uses concrete numbers (MRW slope 0.59-0.93, ~2% convergence, etc.) where the question asks for evidence

This is the polished exam essay — distinct from the `/exercise` model answer, which is the underlying algebra in full.

### R-no-hints: the exam has no hints

Unlike `/quiz` (productive-failure reveal of choices) and `/exercise` (progressive hints per sub-move), `/exam` has only two reveals per question: the skeleton (self-check) and the model answer (comparison). No progressive hint chain. This matches the real exam.

### R-no-sub-parts

The mock has no sub-parts. Cozzi's prompts are single declarative sentences (often two). **Do not** write `(a) … (b) … (c) …` exam questions. Every question is one cohesive prompt covering both technical and interpretive halves.

---

## JSON Schema

```json
{
  "title": "Mock Exam Simulation",
  "meta": "Macroeconomics III — full 4-question simulation — YYYY-MM-DD",
  "exam_info": {
    "total_minutes": 90,
    "num_questions": 4,
    "weight_per_question": "25%",
    "format_note": "4 essay questions, equal weight. No MCQ, no T/F, no sub-parts. Verb-pair format throughout."
  },
  "questions": [
    {
      "id": 1,
      "module": 1,
      "verb_pair": "describe + critique",
      "weight": "25%",
      "target_minutes": 20,
      "prompt": "Describe the main empirical evidence supporting and contradicting the basic Solow model.",
      "skeleton": [
        "Define what 'basic Solow' predicts: steady state in levels (not growth), conditional convergence",
        "Supporting: Kaldor facts (constant labor share, K/Y, r); cross-country positive correlation of y* with s, negative with n+δ",
        "Contradicting: speed of convergence ~2%/yr observed vs ~5-6% predicted; large unexplained y* dispersion across countries",
        "Resolution attempt: MRW's α+φ ≈ 0.66 partially closes both puzzles",
        "Verdict: Solow is right in direction, wrong in magnitudes — points to missing factors (human capital, scale of TFP differences)"
      ],
      "model_answer": "<p>Basic Solow predicts that economies converge to a country-specific steady state determined by parameters $s$, $n$, $\\delta$, and the Cobb-Douglas exponent $\\alpha$. ...</p><h3>Supporting evidence</h3><p>...</p><h3>Contradicting evidence</h3><p>...</p><div class=\"key-result\"><strong>Verdict.</strong> Solow gets the direction right (richer countries have higher $s$, lower $n$) but misses on magnitudes — the convergence rate puzzle and the cross-country dispersion of $y^*$ both point to the same fix: a broader notion of accumulable capital.</div>"
    }
  ]
}
```

### Notes

- **`module`** is just a tag (integer); used only to display "Module N" on the card.
- **`verb_pair`** is one of the five canonical pairs (or one you can defend as a mock-style extension).
- **`target_minutes`** is per-question; the builder warns if their sum drifts from `exam_info.total_minutes` by more than ±15 minutes.
- **`skeleton`** is a list of strings (no HTML).
- **`model_answer`** is HTML, with LaTeX in `$…$` or `$$…$$` (double-backslash in JSON), and may include `<h3>`, `<p>`, `<ul>`, `<div class="key-result">…</div>`.
- **No `hints` field** — `/exam` has none by design.

---

## Pre-Build Checklist

- [ ] Confirmed module distribution + verb pairs with user (Step 2 mandatory)
- [ ] Read mock exam reference (`Material/mock exam/Mock_Exam-1.pdf`)
- [ ] Read relevant lecture files for each module
- [ ] Exactly 4 questions
- [ ] All weights = 25%; target_minutes sum ≈ 80-90
- [ ] Prompts are 1-2 lines, declarative, Cozzi-style
- [ ] Each question has skeleton (4-6 bullets) + model answer (~600-800 words)
- [ ] Verb pairs diverse across the 4 questions
- [ ] Model answers exam-quality, not /exercise-quality (woven algebra, not micro-steps)
- [ ] Notation matches lecture conventions
- [ ] Audit printed verbatim; every box checked
- [ ] JSON parses; LaTeX backslashes doubled; all IDs unique
