---
name: exam
description: "Generate exam-style practice tests with mixed question types (MCQ, T/F, numeric, checkbox, dropdown) organized in scenario chains that mirror the professor's testing style. Use this skill whenever the user says '/exam', asks for an exam simulation, wants exam-style practice, mock exam, or exam training. Also triggers on 'simulate the exam', 'exam practice on [topic]', 'mock test', 'exam-style questions', or any request for mixed-format exam questions with scenarios. Distinct from /quiz (MCQ only) and /exercise (single-block compute/derive)."
---

# /exam — Exam Simulator Skill

Generate exam-style practice tests with mixed question types and scenario chains. Output goes to `.claude/output/exams/`.

## Invocation

User says `/exam [topics or module range]` with optional flags:
- `--difficulty 1|2|3` (default: 1)
- `--questions N` (default: ~15–20)

Example: `/exam M01-M06 --difficulty 2 --questions 20`

## How This Differs from /quiz and /exercise

| Feature | /quiz | /exercise | /exam |
|---|---|---|---|
| Question types | MCQ only | Single-block compute/derive | MCQ, T/F, numeric, checkbox, dropdown |
| Structure | Flat list, independent | Flat list, independent | Parts with scenario chains |
| Sub-parts | No | No (explicitly banned) | Yes — answers feed forward within a scenario |
| Difficulty | Fixed (60-75% target) | Fixed | Adaptive (3 levels) |
| Scenarios | No | Sometimes a setup | Always — named agents, concrete decisions |
| Goal | Test conceptual understanding | Test computational ability | Simulate the actual exam format |

## Workflow

### Step 1 — Read context

Read these files (in this order):
1. `.claude/CONVENTIONS.md` — naming, folder structure, output rules
2. `PREFERENCES.md` — cognitive preferences
3. `LEARNING_STATE.json` — current understanding per topic
4. `subject-config.md` — subject context, exam scope, calibrated style (if exists)
5. All course material files relevant to the requested topics — slides, homeworks, tutorials, old exams
6. Old exams in `material/old_exams/` — to calibrate question style, difficulty, and format

**IMPORTANT:** Read ALL material comprehensively. Scan slides for definitions, theorems, and worked examples. Scan homeworks and tutorials for the kinds of problems the professor assigns. Study old exams for the professor's testing psychology (see Professor Psychology section below).

### Step 2 — Calibration (first use only)

If `subject-config.md` has no `[exam_style]` section:
1. Generate 3 sample scenario-chain questions (2 questions each) in different styles:
   - **Style A**: Clean conceptual setup → T/F + MCQ
   - **Style B**: Numeric scenario → compute + dropdown comparative statics
   - **Style C**: Edge-case scenario → checkbox + numeric
2. Ask the user to grade them
3. Write calibrated style to `subject-config.md` under `## Calibration` → `[exam_style]`

If calibration already exists, skip to Step 3.

### Step 3 — Plan the exam

Design the exam structure. Present the plan:

> "I'll generate a Level [X] exam covering [topics]. Structure:
> - Part I: [N] standalone conceptual questions (MCQ, T/F, checkbox)
> - Part II: [Scenario name] — [N] questions (types: ...)
> - Part III: [Scenario name] — [N] questions (types: ...)
> Total: [N] questions. Ready?"

**Structural rules:**
- Part I is ALWAYS standalone conceptual questions (no scenario). Mix of MCQ, T/F, and checkbox. These test definition edge cases, boundary conditions, and tricky conceptual distinctions.
- Parts II–IV are ALWAYS scenario chains with a named agent facing a concrete decision problem. Questions within a scenario build on each other — later questions may use results from earlier ones.
- Total: 15–20 questions by default (user can override).
- Each scenario has 4–8 questions with at least 2 different question types.

### Step 4 — Generate the JSON payload

Generate a JSON payload following the format below. Apply ALL rules from the Question Design Rules and Professor Psychology sections.

**JSON format:**
```json
{
  "title": "Exam: [Topic Range]",
  "meta": "Microeconomics III (4,202) — [Module range] — [Date]",
  "difficulty": 1,
  "parts": [
    {
      "title": "Part I — Conceptual Questions",
      "scenario": null,
      "questions": [
        {
          "id": "q1",
          "type": "mcq",
          "label": "Question 1",
          "stem": "<p>Which of the following...</p>",
          "choices": [
            {"letter": "A", "text": "First choice"},
            {"letter": "B", "text": "Second choice"},
            {"letter": "C", "text": "Third choice"},
            {"letter": "D", "text": "Fourth choice"}
          ],
          "correct": "B",
          "explanation": "B is correct because..."
        },
        {
          "id": "q2",
          "type": "tf",
          "label": "Question 2",
          "stem": "<p>Statement: Every complete preference...</p>",
          "choices": [
            {"letter": "A", "text": "True"},
            {"letter": "B", "text": "False"}
          ],
          "correct": "B",
          "explanation": "False. Completeness requires..."
        },
        {
          "id": "q3",
          "type": "checkbox",
          "label": "Question 3",
          "stem": "<p>Select all normative statements. <em>(Select all that apply.)</em></p>",
          "choices": [
            {"letter": "A", "text": "Statement 1", "value": "A"},
            {"letter": "B", "text": "Statement 2", "value": "B"},
            {"letter": "C", "text": "Statement 3", "value": "C"},
            {"letter": "D", "text": "Statement 4", "value": "D"}
          ],
          "correct": "A,C",
          "explanation": "A and C are normative because..."
        }
      ]
    },
    {
      "title": "Part II — Elena's Insurance Decision",
      "scenario": {
        "title": "Scenario — Elena's Insurance Decision",
        "html": "<p>Elena has initial wealth \\(w = 200\\) and faces...</p>"
      },
      "questions": [
        {
          "id": "q6",
          "type": "numeric",
          "label": "Question 6",
          "stem": "<p>Compute Elena's expected utility without insurance.</p>",
          "correct": "12.5",
          "tolerance": 0.1,
          "explanation": "EU = 0.8 × u(200) + 0.2 × u(50) = ..."
        },
        {
          "id": "q7",
          "type": "dropdown",
          "label": "Question 7",
          "stem_html": "<p>If the insurance premium increases from 30 to 45, Elena's optimal coverage <select data-answer=\"decreases\"><option value=\"\">— select —</option><option value=\"increases\">increases</option><option value=\"decreases\">decreases</option><option value=\"stays the same\">stays the same</option></select> because the marginal cost of coverage now <select data-answer=\"exceeds\"><option value=\"\">— select —</option><option value=\"exceeds\">exceeds</option><option value=\"equals\">equals</option><option value=\"is below\">is below</option></select> the marginal benefit at the original optimum.</p>",
          "correct": "decreases",
          "explanation": "At a higher premium, the price of coverage rises..."
        }
      ]
    }
  ]
}
```

### Step 5 — Build the HTML

1. Write JSON to `/tmp/exam_payload.json`
2. Run: `python .claude/scripts/build_exam.py /tmp/exam_payload.json .claude/output/exams/[filename].html`
3. Copy the output file to the workspace root for user access
4. Present the file link using a `computer://` link

### Step 6 — Update LEARNING_STATE.json

After generating the exam:
- Topics covered → set level to at least `tested` if previously `seen`
- Never downgrade existing levels

### File naming

Follow `.claude/CONVENTIONS.md`. Pattern: `[topic-slug]_[YYYY-MM-DD].html` in `.claude/output/exams/`.

---

## Professor Psychology — How She Tests

These patterns were extracted from the 2024 and 2025 final exams. Use them to calibrate the style, NOT to copy questions.

### Part I: Definition edge cases and tricky T/F

The professor loves testing the *boundary* of definitions — not whether you know them, but whether you know exactly where they stop.

**Patterns observed:**
- **Transitivity trick (2024 Q1):** "Is the relation 'has the same birthday' transitive?" — tests whether students confuse transitivity with reflexivity. The answer is yes, because the edge case (A shares birthday with B who shares with C → A shares with C) holds trivially.
- **Completeness trick (2024 Q2):** "Is strict preference complete?" — No, because \\(x \\succ x\\) fails. Students who conflate weak and strict preference get this wrong.
- **Variance ≠ MPS (2024 Q9):** "Higher variance always means lower EU for risk-averse agents" — False, because higher variance alone does not imply MPS.
- **Normative vs. positive (2024 Q6):** Checkbox asking which statements are normative — tests whether students can distinguish value judgments from factual claims.

**How to replicate:** Create T/F or MCQ questions where the "obvious" answer is wrong because of an edge case in the definition. The question should look easy but require precise knowledge.

### Parts II–IV: Named-agent scenario chains

**Structure:**
- A named agent (Seraina, Fabio, Elena, Edna) faces a concrete decision problem with explicit numbers.
- Questions build sequentially: compute a value in Q1, use it in Q2, etc.
- Mix of question types within a single scenario: compute EU (numeric), identify optimal action (MCQ), comparative statics (dropdown), identify which properties hold (checkbox).

**Number style:**
- Clean numbers: probabilities like 0.75, 0.25, 1/3; wealth like 100, 200, 240; utilities like \\(\\sqrt{x}\\), \\(\\ln(x)\\), \\(x^2\\).
- Answers should come to 3 significant digits at most. If intermediate steps produce ugly decimals, the problem setup is wrong — redesign it.

**Scenario depth:**
- 2024 Part 2 (Seraina): 6 questions, one scenario about club preferences → calibrate EU → predict choices → identify strict preference conditions.
- 2024 Part 3 (Fabio): 10 questions, information cascade with sequential Bayesian updating → posteriors → WTP for signals.
- 2025 Part II: Monopolist with reliable/unreliable products → signaling with warranty → pooling vs separating equilibria.
- 2025 Part III: Information cascade with costly signals → posterior computation → cascade breaking conditions.

**Key insight:** The professor tests whether students can *apply* theory to a specific situation, not whether they can state the theory. The scenarios are always concrete enough that there's one right answer, never vague or open-ended.

### Comparative statics via dropdowns

The professor frequently uses dropdown questions for comparative statics: "If parameter X increases, the optimal Y [increases/decreases/stays the same]." These test economic intuition — whether the student can reason about the direction of an effect without computing it.

### What she does NOT test

- Pure memorization of definitions without application
- Long algebraic derivations on the exam (these are in homeworks, not exams)
- Open-ended essay questions
- Questions requiring material beyond the slides

---

## Difficulty Levels

### Level 1 — Exam-level (default)

Matches the professor's actual exam difficulty. Same number complexity, same depth of reasoning, same question types.

- Numbers: clean (0.75, 100, \\(\\sqrt{x}\\))
- Part I: 1-2 tricky edge cases, rest are standard but require careful reading
- Scenario chains: 4-6 questions, straightforward sequential reasoning
- Target: a well-prepared student gets 70-85%

### Level 2 — Harder

Same clean numbers, but more conceptual twists and edge cases. Does NOT make numbers dirtier.

- Part I: more edge cases, more "almost true but not quite" statements
- Scenario chains: extra twist (e.g., a parameter changes mid-scenario, forcing re-computation)
- Questions that combine concepts from different modules in non-obvious ways
- Target: a well-prepared student gets 55-70%

### Level 3 — Easier

Same structure, but simpler setups and more guidance in stems.

- Part I: standard definitions, fewer edge cases
- Scenario chains: shorter (3-4 questions), more guidance in stems ("Recall that CE is defined as...")
- Numbers even cleaner (round numbers like 100, 0.5)
- Target: a student who has read the slides gets 75-90%

---

## Question Design Rules

### Rule 1: Exam authenticity over pedagogical novelty

Every question should feel like it could appear on the actual exam. Mimic the professor's phrasing style, scenario structure, and level of precision. This is NOT a quiz — it's exam simulation.

### Rule 2: Clean numbers, 3 significant digits max

Use numbers that simplify cleanly. If an intermediate step produces 0.728723..., the problem setup is wrong. Redesign with numbers that give cleaner results. Final numeric answers should have at most 3 significant digits.

**Good:** priors (1/3, 2/3), probabilities (0.75, 0.25), wealth (100, 200), \\(u(x) = \\sqrt{x}\\)
**Bad:** priors (0.37, 0.63), probabilities (0.82, 0.18), wealth (147)

### Rule 3: Scenarios with named agents

Every scenario chain must have a named agent (not "an agent" or "a consumer"). Use realistic names and concrete decision contexts. The agent's problem should be stated with all parameters explicit — no ambiguity about what to compute.

### Rule 4: Sequential answer chains

Within a scenario, later questions should build on earlier ones. The student who gets Q1 wrong can still attempt Q2 using the correct Q1 answer (which is revealed when they check). Design the chain so that each question adds one new concept or computation.

### Rule 5: Mixed question types within scenarios

Each scenario should use at least 2 different question types. Typical pattern:
- Start with a numeric computation (compute EU, CE, posterior)
- Follow with an MCQ or T/F about interpretation
- End with a dropdown comparative statics question

### Rule 6: No giveaway patterns

All rules from the quiz skill apply: length parity across MCQ choices, no hedging tells, position distribution across A/B/C/D, tone parity. For T/F questions, distribute True and False answers roughly evenly.

### Rule 7: Explanations must be complete

Every question's explanation must:
1. State why the correct answer is right (with computation if numeric)
2. For MCQ/checkbox: explain why each wrong choice fails
3. For dropdown: explain the economic intuition behind the direction
4. For numeric: show every intermediate step

### Rule 8: Bridge questions in Part I

At least 1-2 Part I questions should connect concepts from different modules (same rule as quiz skill's bridge style, with mechanically derivable answers — never subjective analogy-matching).

### Rule 9: Dropdown answer encoding

For dropdown questions, the `stem_html` field must contain the full HTML including `<select>` elements with `data-answer` attributes. Each `<select>` must have:
- A blank placeholder `<option value="">— select —</option>`
- All answer options as `<option value="...">display text</option>`
- The `data-answer` attribute set to the correct value

Multiple dropdowns in one question are supported — the JS checks all of them.

---

## Pre-Generation Checklist

Before writing the JSON:
- [ ] Read CONVENTIONS.md and confirmed output path + LaTeX delimiter rules
- [ ] Read PREFERENCES.md for cognitive preferences
- [ ] Read LEARNING_STATE.json and calibrated difficulty
- [ ] Read subject-config.md for calibrated exam style (or ran calibration)
- [ ] Scanned ALL relevant material: slides, homeworks, tutorials, old exams
- [ ] Designed Part I with at least 1-2 definition edge cases
- [ ] Designed scenario chains with named agents and explicit parameters
- [ ] Verified all numeric answers come to ≤3 significant digits
- [ ] Every question satisfies rules 1-9
- [ ] Mixed question types within each scenario
- [ ] No giveaway patterns in phrasing, length, or hedging
- [ ] Explanations cover all choices and show all computation steps
- [ ] LaTeX uses only `\\(\\)` and `\\[\\]` — never `$`
