# Output Conventions

Layout and hard requirements for everything skills produce. Each skill's `SKILL.md` covers its own payload schema, build script invocation details, and content rules.

<pipeline>
Mandatory four-step flow:

1. Skill produces a JSON payload (schema in the skill's own `SKILL.md`).
2. Skill writes payload to a temp path (`$env:TEMP\<slug>.json` on Windows; `/tmp/<slug>.json` on POSIX).
3. Skill invokes `python tools/build_<type>.py <temp.json> <output.html>` via Bash.
4. The build script merges the payload with `tools/templates/<type>.html` and writes the final HTML.

**Skills MUST NOT write `.html` files directly.** *Why: the template + JSON pattern keeps tokens low (no boilerplate regeneration), keeps output consistent, and lets templates evolve without touching past outputs.* A Step 6 PreToolUse hook (matching `outputs/**/*.html`) will enforce this mechanically.
</pipeline>

<folder_layout>
| Type | Output path |
|---|---|
| Lecture | `outputs/lectures/<slug>_YYYY-MM-DD.html` |
| Quiz | `outputs/quizzes/<slug>_YYYY-MM-DD.html` |
| Exercise | `outputs/exercises/<slug>_YYYY-MM-DD.html` |
| Exam | `outputs/exams/<slug>_YYYY-MM-DD.html` |
| Essay (round-trip) | `outputs/essays/<slug>_YYYY-MM-DD/` folder containing `prompt.md`, `answer.md` (user writes), `grading.html` (skill produces after user fills `answer.md`) |
</folder_layout>

<naming_rules>
- `<slug>`: lowercase, hyphen-separated, no underscores within the slug. Short but identifiable.
  - ✅ `basic-solow-model`, `efficiency-wages-derivation`, `endogenous-growth-rd`
  - ❌ `Module_3_Quiz_v1`, `solow_growth`, `quiz1`
- Date: ISO `YYYY-MM-DD`, the day generated.
- Collisions: append `_v2`, `_v3` before the extension.
- **Never write outside the type-specific subfolder.** No HTML at root, none in `Material/`, none in `tools/`.
</naming_rules>

<learning_state>
All skills update `docs/LEARNING_STATE.json` after producing output. Canonical progression:

```
not_covered → seen → tested → practiced → mastered
```

| Level | Set by |
|---|---|
| `not_covered` | initial state |
| `seen` | `/lecture` |
| `tested` | `/quiz` |
| `practiced` | `/exercise`, `/quiz` (≥70%) |
| `mastered` | `/quiz` (≥80% twice), `/exercise` (clean) |

Never downgrade unless the user explicitly resets. Use a Python helper (planned `tools/state.py`) for surgical edits — don't read-modify-write the full file into context.
</learning_state>
