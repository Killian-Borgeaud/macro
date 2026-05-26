---
name: quiz
description: "Generate conceptual multiple-choice quizzes from course material. Use this skill whenever the user says '/quiz', asks for a quiz, wants to test their understanding, mentions wanting practice questions, or requests MCQ/multiple-choice questions on any topic. Also triggers on requests like 'test me on [topic]', 'quiz me', 'make practice questions', 'I want to check if I understand [topic]', or any request to create assessment questions from course material. Even if the user just says something like 'can you test me' or 'I need to practice', use this skill."
---

# /quiz — Quiz Generation Skill

Generate conceptual multiple-choice quizzes and save them to `.claude/output/quizzes/`.

## Invocation

User says `/quiz [topic or module]` optionally with a question count (default: 10). A quiz may span multiple topics or focus on one.

## Workflow

### Step 1 — Read context

Read these files (in this order):
- `.claude/CONVENTIONS.md` — naming, folder structure, output rules
- `PREFERENCES.md` — cognitive preferences
- `LEARNING_STATE.json` — current understanding per topic
- `subject-config.md` — subject context, exam scope, calibrated style (if exists)
- All course material files relevant to the requested topic

### Step 2 — Calibration (first use only)

If `subject-config.md` has no `[quiz_style]` section:
1. Generate 3 sample questions on the same concept, each in a different style (see Question Styles below)
2. Ask the user to grade them
3. Write calibrated preferences to `subject-config.md` under `## Calibration` → `[quiz_style]`

If calibration already exists, skip to Step 3.

### Step 3 — Plan the quiz

Determine:
- **Scope**: which topics to cover (from user request + material scan)
- **Count**: how many questions (user-specified or default 10)
- **Distribution**: spread questions across sub-topics so the quiz is comprehensive, not clustered

Present a brief plan:
> "I'll generate [N] questions covering: [topic list]. Conceptual focus unless you ask for computation. Ready?"

If the user says "go" or doesn't object, proceed.

### Step 4 — Generate questions

Generate a JSON payload following the format below. Apply ALL quality rules from the Question Design Rules section.

**JSON format:**
```json
{
  "title": "Quiz: [Topic]",
  "meta": "[Subject] — [Module/Week range] — [Date]",
  "question_count": 10,
  "questions": [
    {
      "id": 1,
      "style": "boundary",
      "topic": "Gauss-Markov Theorem",
      "stem": "The question text...",
      "choices": [
        {"letter": "A", "text": "First choice"},
        {"letter": "B", "text": "Second choice"},
        {"letter": "C", "text": "Third choice"},
        {"letter": "D", "text": "Fourth choice"}
      ],
      "correct": "B",
      "explanation": "Why B is correct and why each distractor fails...",
      "connection": "Optional: a cross-topic insight this question reveals"
    }
  ]
}
```

### Step 4b — Length-bias verification (mandatory)

After generating the JSON, verify choice-length parity for EVERY question before building:
- For each question, count the words in each choice's `text` field
- If the correct answer's word count exceeds the shortest distractor by more than 30%, REWRITE the distractors to match (make them equally precise but wrong) or shorten the correct answer
- This is the single most common failure mode. Check it explicitly, do not skip.

### Step 5 — Build the HTML

1. Write JSON to `/tmp/quiz_payload.json`
2. Run: `python .claude/scripts/build_quiz.py /tmp/quiz_payload.json .claude/output/quizzes/[filename].html`
3. Copy the output file to the workspace root for user access
4. Present the file link using a `computer://` link

### Step 6 — Update LEARNING_STATE.json

After generating the quiz:
- Topics covered → set level to at least `tested` if previously `seen`
- Never downgrade existing levels

### Step 7 — Process results (next conversation)

When the user pastes quiz results JSON into chat, parse it and update LEARNING_STATE.json:
- **Score ≥ 75%** on a topic → advance to `practiced` (or `mastered` if already `practiced`)
- **Score 50–74%** → advance to `practiced` if currently `seen` or `tested`; stay at current level otherwise
- **Score < 50%** → stay at current level (do not downgrade)
- Per-question misses: note which specific subtopics were missed for targeted follow-up

The quiz HTML exports a JSON blob at the end with per-question results. The user copies this and pastes it into the next conversation. Parse it, update the state, and acknowledge what changed.

### Difficulty escalation by level

| LEARNING_STATE level | Question style emphasis | Difficulty target |
|---|---|---|
| `seen` | Boundary-testing (does the student know the limits?) | 60-70% expected score |
| `tested` | Harder boundary + flaw-detection questions | 55-65% expected score |
| `practiced` | Cross-topic bridges + edge cases | 50-60% expected score |
| `mastered` | Exception-hunting, adversarial distractors, cross-subject bridges | 45-55% expected score |

### File naming

Follow `.claude/CONVENTIONS.md`. Pattern: `[topic-slug]_[YYYY-MM-DD].html` in `.claude/output/quizzes/`.

---

## Question Design Rules

These rules encode the user's calibrated preferences. Every question MUST satisfy ALL of them. They are the difference between a useful quiz and a waste of time.

### Rule 1: Test the boundary, not the center

The best questions target where understanding breaks down — the edge of a concept, not its textbook definition. A student who "mostly gets it" should find the question hard. A student who deeply understands should find it clear.

**What this means in practice:** instead of "What is unbiasedness?", ask "Which of these estimators is unbiased but inconsistent?" Instead of "What does the CLT say?", ask "Which of these is NOT implied by the CLT?"

### Rule 2: Every distractor must be independently plausible

Each wrong answer should be something a student who partially understands would genuinely pick. Distractors are not filler — they are carefully constructed misconceptions.

**How to construct good distractors:**
- **Sign/direction errors**: confusing upward with downward bias, mixing up conditions
- **Scope errors**: thinking a theorem says more than it does (e.g., BLUE means best among ALL estimators)
- **Condition swap**: correct result but wrong assumption set (e.g., consistency requires MLR.1-4, not MLR.1-6)
- **Partial truth**: statements that are true in a special case but not generally
- **Plausible reasoning**: a logical chain that sounds right but has one wrong link

**Anti-patterns for distractors (NEVER do these):**
- Obviously absurd answers that no student would pick
- Joke answers or filler
- Answers that are technically correct but "less correct" — each question has exactly one unambiguously correct answer
- Using "all of the above" or "none of the above"

### Rule 3: No giveaway patterns

The correct answer must not be identifiable by surface features. This rule is critical — violating it renders the quiz useless for learning.

**Length parity:** all four choices must be roughly the same length (within ±30% word count). If the correct answer is naturally longer because it's more precise, REWRITE the distractors to be equally precise (but wrong). If the correct answer is naturally shorter, pad it with qualifying language or rewrite the others to be shorter.

**Tone parity:** all choices must use the same register and level of technicality. If the correct answer uses a formula, at least two distractors should also use formulas. If the correct answer is colloquial, all should be.

**Position distribution:** over a 10-question quiz, the correct answer should appear roughly equally across A/B/C/D (2-3 times each, never more than 3 in a row for the same letter).

**Hedging parity:** avoid making the correct answer the only one with hedging language ("may," "can," "under certain conditions") or the only one with absolute language ("always," "never"). Distribute these equally.

### Rule 4: Conceptual by default, computational only on request

The default mode is conceptual: questions test understanding of what objects are, why results hold, where theorems stop applying, and how concepts relate.

Computation-style questions (calculate a t-statistic, find a bias direction given numbers) are generated ONLY when the user explicitly requests them. Even then, computation questions should require conceptual understanding to solve — never pure arithmetic.

### Rule 5: Cross-topic connections

At least 2 out of every 10 questions should connect concepts that are typically taught separately. These are the highest-value questions because they force the student to see the architecture of the subject rather than isolated facts.

**Examples of good connections:**
- Linking omitted variable bias (finite-sample) to inconsistency (asymptotic) — same mechanism, different frameworks
- Linking the Gauss-Markov theorem (OLS is BLUE) to the variance formula (why multicollinearity matters even though OLS is "best")
- Linking the envelope theorem to the interpretation of Lagrange multipliers
- Linking martingale pricing to risk-neutral valuation

When a question makes a cross-topic connection, include a brief `connection` field in the JSON explaining the insight.

### Rule 6: Difficulty targeting

Questions should cluster around the difficulty level where the student has to *think* — not recall, not compute, but reason. The target: a well-prepared student gets 60-75% right on first attempt. If they get 90%+, the quiz is too easy. If they get below 50%, it's testing material they haven't seen.

Use LEARNING_STATE.json to calibrate: topics at level `seen` get harder boundary-testing questions; topics at `practiced` get cross-topic connection questions; topics at `mastered` get edge-case and exception questions.

---

## Question Styles

Each question should be tagged with one of these styles. Distribute across styles for variety — never use the same style more than 3 times in a 10-question quiz.

### "boundary" — What does NOT follow

Present a theorem, definition, or result. Ask what is NOT implied, NOT guaranteed, or NOT a consequence. Forces the student to know exactly where the concept stops.

> "The Gauss-Markov theorem guarantees OLS is BLUE. Which is NOT implied?"

This is the highest-rated style. Use it for 2-3 questions per quiz.

### "flaw" — Spot the reasoning error

Present a student's statement or argument that contains a subtle error. The student must identify what's wrong. Distractors are alternative diagnoses of the flaw.

> "A student says: 'None of my t-tests are significant, so the model has no explanatory power.' What is wrong?"

Use for 2-3 questions per quiz.

### "deep-short" — Compact question, deep answer

A brief setup (1-2 sentences, possibly with a small numeric element) that requires understanding a concept at depth to answer. The question looks easy but isn't.

> "An estimator satisfies E(W_N) = θ + 2/N. It is: biased and consistent / biased and inconsistent / ..."

Use for 2-3 questions per quiz.

### "measure" — What does this object represent

Present a formula or mathematical object and ask what it actually measures or represents. Tests whether the student can connect symbols to meaning.

> "In Var(β̂_j) = σ²/[SST_j(1-R²_j)], the quantity R²_j is..."

Use for 1-2 questions per quiz.

### "bridge" — Cross-topic connection

A question whose correct answer requires understanding how two concepts from different modules interact mechanically — not just that they "resemble" each other. The question should be solvable by applying a concrete logical or algebraic link, not by picking the most poetic analogy.

**Good bridge:** "An agent's posterior dominates the prior in the FOSD sense after a good-news signal. What does this imply about her EU from any action with increasing state-dependent payoffs?" (requires applying FOSD → EU result to the Bayesian posterior — concrete, verifiable)

**Bad bridge:** "Sequential Bayesian updating is path-independent. This property is structurally analogous to which EU result?" (subjective — multiple answers could be argued; tests pattern-matching, not understanding)

> Rule: every bridge question must have a single unambiguous correct answer derivable from the mechanics of both concepts, not from aesthetic similarity.

Use for 1-2 questions per quiz. Always include the `connection` field in JSON.

---

## Explanation Quality

Every question's `explanation` field must:
1. State why the correct answer is right (1-2 sentences)
2. State why EACH distractor is wrong (1 sentence each, specific — not just "this is incorrect")
3. If the question is a "bridge" style, explain the cross-topic connection

Explanations are shown after the user answers and are a critical learning moment. They should teach, not just confirm.

---

## Pre-Generation Checklist

Before writing the JSON:
- [ ] Read CONVENTIONS.md and confirmed output path
- [ ] Read PREFERENCES.md and confirmed cognitive preferences
- [ ] Read LEARNING_STATE.json and calibrated difficulty
- [ ] Read subject-config.md for calibrated quiz style (or ran calibration)
- [ ] Scanned relevant material
- [ ] Planned question distribution across topics and styles
- [ ] Every question satisfies ALL 6 design rules
- [ ] Every distractor is independently plausible and same length/tone as correct answer
- [ ] Correct answer positions distributed roughly evenly across A/B/C/D
- [ ] At least 2 cross-topic "bridge" questions included
- [ ] Explanations cover all 4 choices, not just the correct one
- [ ] No giveaway patterns in phrasing, length, or hedging
