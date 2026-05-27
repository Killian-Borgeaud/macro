# Macroeconomics III — Exam Prep Workspace

Second-brain workspace for HSG Macroeconomics III (Spring 2026, Prof. Cozzi). Generates HTML lectures, MCQ quizzes, deep-understanding exercise sets, and exam simulations from extracted course PDFs.

<workspace_identity>
- **Subject:** Macroeconomics III (HSG, Spring 2026)
- **User:** Technically literate non-developer. Values collaborative teaching over black-boxed execution. Values honest analysis over confident-sounding answers. Cross-disciplinary thinker — connect to concepts from other fields when natural.
- **Reuse model:** This whole folder is copied per subject. Subject-specific content lives in `Material/` plus `docs/EXAM_PROFILE.md` and `docs/LEARNING_STATE.json`. Everything else (skills, tools, COGNITIVE_PREFS, OUTPUT_CONVENTIONS) stays identical across subjects.
</workspace_identity>

<operating_principles>
Four non-negotiable principles. Violating them is a regression, not a tradeoff.

1. **Simple as possible but not simpler.** No speculative features. If a workflow is used <10% of the time, cut it. *Why: complexity compounds; every unused feature is dead weight that confuses future sessions.*
2. **Project-specific only.** Every skill, tool, and config lives in this workspace. Nothing depends on plugin skills. *Why: the user will eventually delete plugin skills; nothing here should break when that happens.*
3. **Minimize user manual work.** User runs scripts, spot-checks outputs, writes essay answers. Agent does the rest. *Why: the user explicitly opted out of per-page/per-module manual annotation.*
4. **Default to retrieval, not explanation.** Generate prompts and grade answers; explanations are a secondary mode. *Why: learning-science research on the fluency illusion — passively reading AI-generated explanations feels productive but isn't.*
</operating_principles>

<on_session_start>
At the start of any session in this workspace:

1. Note the cwd. If it's inside `Material/modules/<N>/`, that module's CLAUDE.md is already in context — use it.
2. Identify the task type:
   - **Exploration / Q&A:** answer from in-context CLAUDE.mds + on-demand Reads of `Material/`.
   - **Skill invocation** (`/lecture`, `/quiz`, `/exercise`, `/exam`): the skill's SKILL.md handles loading via `@import`s.
   - **Architectural / workspace changes:** read the relevant `docs/` files first.
3. If math content is involved at any point, follow the **PNG fallback rule** below.
</on_session_start>

<global_rules>

## 1. PNG fallback for broken math

Every `.md` page in `Material/` has a corresponding `.pages/p{NNN}.png` sibling at ~200dpi. The PDFs were extracted without Docling's formula model (formula model would have taken ~48h on the user's CPU), so equations are unreliable in the .md.

**Two patterns indicate broken math:**

<example_broken_math>
Pattern 1 — explicit placeholder:
`<!-- formula-not-decoded -->`

Pattern 2 — scrambled tokens (the actual equation is gone, replaced by garbled OCR):
`1 1 t t t t t Y K h A L α ϕ α ϕ α ---=`
or `α ϕ α ---=` mixed into prose

Both mean the same thing: the equation is unrecoverable from text. Read `<file_stem>.pages/p{NNN:03d}.png` for that page (e.g. `Lecture 3a.pages/p010.png`) before generating any content that references that equation.
</example_broken_math>

The cleaner exceptions are module 1 lectures and `Lecture 2a.md` (extracted with formula model on; LaTeX equations preserved). The textbook chapter slices and most exercise-session slides need PNG fallback often.

## 2. Never write directly to `outputs/`

All study material goes through the build scripts in `tools/`. Skills generate a JSON payload describing content; Python scripts merge it with `tools/templates/*.html` to produce the final HTML.

*Why: the template + JSON pattern keeps token use low (no HTML boilerplate regeneration), keeps output consistent across runs, and lets templates evolve without touching past outputs.* Skills enforce this via `docs/OUTPUT_CONVENTIONS.md` — no automated hooks; this is a discipline rule.

## 3. Read calibration before generating

Every skill that produces output `@import`s these from its SKILL.md body:
- `docs/COGNITIVE_PREFS.md` — how the user learns (subject-agnostic)
- `docs/OUTPUT_CONVENTIONS.md` — pipeline + filename/folder rules
- `docs/EXAM_PROFILE.md` — professor's exam style + course metadata

Each skill's own `SKILL.md` contains its style calibration (lecture format, quiz distribution, exercise hint depth, etc.) inline — no separate config file.

*Why: shared docs cover what applies across all skills; per-skill calibration lives with the skill it calibrates.*
</global_rules>

<folder_map>
```
Macro/
├── CLAUDE.md                    ← this file (always loaded)
├── Material/                    ← course content (PDFs + .md + .pages PNGs)
│   ├── CLAUDE.md                ← pointer to mock exam + modules
│   ├── mock exam/
│   └── modules/
│       ├── CLAUDE.md            ← course overview + module summaries
│       └── module 1..6/
│           └── CLAUDE.md        ← per-module file list + connections
├── docs/                        ← reference docs (loaded via @import from skills)
│   ├── COGNITIVE_PREFS.md       ← how the user learns (subject-agnostic)
│   ├── OUTPUT_CONVENTIONS.md    ← pipeline + filename/folder rules
│   ├── EXAM_PROFILE.md          ← Cozzi's exam style + course metadata
│   └── LEARNING_STATE.json      ← topic progression tracking (data)
├── tools/
│   ├── setup/                   ← one-time (extract_all.py, slice_textbook.py)
│   ├── build_<type>.py          ← build scripts: lecture, quiz, exercise, exam, figure
│   ├── templates/               ← HTML templates merged with JSON payloads
│   └── styling/                 ← visual-test fixtures (one per skill)
├── outputs/                     ← generated material (only via tools/build_*.py)
│   └── {lectures, quizzes, exercises, exams}/
└── .claude/
    ├── settings.json            ← permissions
    ├── settings.local.json
    └── skills/                  ← /lecture, /quiz, /exercise, /exam
```
</folder_map>

<skills>
Four skills live in `.claude/skills/`, each with template + builder + fixture pipeline:

- **`/lecture`** — long-form HTML study document for a topic or module (replaces textbook + slides)
- **`/quiz`** — MCQ + multi-select + MTF-cluster + graph + derivation questions, productive-failure UI
- **`/exercise`** — compound 5-exercise sets (anchor + main proof + variation + reflection + counterfactual)
- **`/exam`** — 4-question essay simulation matching Cozzi's mock format (25% each, ~20 min target per question)
</skills>

<navigation>
- **What the course covers:** `Material/modules/CLAUDE.md`
- **What's in a specific module:** `Material/modules/module N/CLAUDE.md`
- **How to write output:** `docs/OUTPUT_CONVENTIONS.md`
- **How the user learns:** `docs/COGNITIVE_PREFS.md`
- **How the exam tests (and course metadata):** `docs/EXAM_PROFILE.md`
- **Per-skill style calibration:** inline in each `.claude/skills/<name>/SKILL.md`
</navigation>
