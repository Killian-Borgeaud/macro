# Hook design (sketch — implemented in Step 6)

Design only. No `.ps1` scripts yet. The hooks live in `.claude/hooks/` and are registered in `.claude/settings.json`. User is on Windows PowerShell, so hook scripts use `shell: powershell`.

## Goal

Enforce the "all outputs go through build scripts" rule mechanically rather than relying on each skill to remember.

## Hook 1 — Block direct writes to `outputs/`

| Field | Value |
|---|---|
| Event | `PreToolUse` |
| Matcher | `Write` (and `Edit` if file exists) |
| Conditional matcher | `file_path` matches `outputs/**/*.html` |
| Action | Exit 2 with stderr: "Direct writes to outputs/ are forbidden. Use tools/build_<type>.py instead." |
| Why | Forces the JSON-payload + Python-build pattern. Stops skills from writing raw HTML even if the SKILL.md instructions are forgotten. |
| Allows | Writes by `python tools/build_<type>.py` (Bash invocations, not Write tool calls — naturally bypass the matcher). |

## Hook 2 — Block writes outside the type-specific folder

| Field | Value |
|---|---|
| Event | `PreToolUse` |
| Matcher | `Write\|Edit` |
| Conditional matcher | `file_path` matches `*.html` AND NOT matches `outputs/**/*.html` |
| Action | Exit 2 with stderr: "HTML output must live in outputs/<type>/. Got <path>." |
| Why | Stops accidental HTML files at root or inside `Material/`. |

## Hook 3 (maybe) — Validate filename slug format

Deferred. The build scripts can validate the slug format themselves on input parsing. Hook-based validation is overkill.

## Rejected ideas (kept here so we don't re-litigate)

- **Hook to enforce LEARNING_STATE updates.** Too brittle — when exactly is an update due? After every build? After user feedback? Leave to skill discipline.
- **Hook to enforce CLAUDE.md / docs/ reading at session start.** Claude does this automatically via the walk; no hook needed.
- **PostToolUse hook to validate HTML well-formedness.** Build script already does its own validation. Extra hook = duplicate work.

## Cross-platform note

Hooks are `.ps1` PowerShell scripts. The matcher's `file_path` glob is normalized by Claude Code, so forward-slash globs (`outputs/**/*.html`) work on Windows. The hook script reads JSON from stdin, parses `tool_input.file_path`, and exits with code 0 (allow) or 2 (block + show stderr to Claude).

Concrete `.claude/settings.json` shape (to write in Step 6):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "command": ".claude/hooks/enforce_outputs.ps1"
          }
        ]
      }
    ]
  }
}
```
