# Material/modules — Course Overview and Module Index

**Course:** Macroeconomics III — HSG, Spring 2026
**Instructor:** Prof. Guido Cozzi (lectures); Maria Bolboaca (exercise sessions)
**Exam:** approximately June 2026
**Textbook:** Peter Birch Sørensen and Hans Jørgen Whitta-Jacobsen, *Introducing Advanced Macroeconomics: Growth and Business Cycles*, 2nd Edition, McGraw-Hill (2010). Relevant chapters (1-11) are sliced into the corresponding module folders as `textbook_chN.pdf` + `.md` + `.pages/`. Chapters 12-25 (trade unions, business cycles, short-run models) are out of scope. The original full textbook PDF is no longer in the workspace.

The course is structured as 6 lectures (each split into sub-sessions a/b/c) plus weekly exercise sessions. Modules 1-5 are growth theory; Module 6 pivots to structural unemployment. Short-run / business-cycle macro is out of scope.

## The 6 modules

| # | Folder | Topic | Textbook chapters |
|---|---|---|---|
| 1 | `module 1/` | Stylized Facts and the Basic Solow Model | 1, 2, 3 |
| 2 | `module 2/` | Open-Economy Solow and Technological Progress | 4, 5 |
| 3 | `module 3/` | Human Capital and Scarce Resources | 6, 7 |
| 4 | `module 4/` | Endogenous Growth: Externalities and R&D | 8, 9 |
| 5 | `module 5/` | Endogenous Growth without Scale Effects | *(lecture notes only)* |
| 6 | `module 6/` | Structural Unemployment | 10, 11 |

## Module summaries

1. **Module 1 — Stylized Facts and the Basic Solow Model.** Empirical regularities of long-run growth (stylized facts 1-7), then the closed-economy Solow model. The foundation everything else extends.
2. **Module 2 — Open-Economy Solow and Technological Progress.** Extends the basic Solow model to a small open economy with capital mobility, then introduces exogenous technological progress (B_t growing at constant rate).
3. **Module 3 — Human Capital and Scarce Resources.** Two extensions of the general Solow model: human capital (MRW 1992) addresses convergence and investment-rate puzzles; scarce natural resources revisits classical pessimism.
4. **Module 4 — Endogenous Growth: Externalities and R&D.** Endogenizes technological progress. Two flavours: productive-externality-based (Ch 8) and R&D-based (Ch 9, Romer-style).
5. **Module 5 — Endogenous Growth without Scale Effects.** Refines Ch 9's R&D model to remove the empirically-failing scale effect. Semi-endogenous (Jones/Kortum/Segerstrom) vs truly-endogenous-without-scale (Howitt, Peretto, Young) vs hybrid (Cozzi 2017). No textbook chapter — lecture notes only.
6. **Module 6 — Structural Unemployment.** Topic switch. Why involuntary unemployment exists in long-run equilibrium; the efficiency wage model and "Solow conditions" of the labour market.

## Cross-module flow

The growth-theory arc builds monotonically: Module 1 establishes the basic Solow model → Module 2 extends to open economy and exogenous technological progress → Module 3 plugs empirical gaps (human capital, scarce resources) while keeping technology exogenous → Module 4 endogenizes technological progress (externalities, R&D) → Module 5 refines the R&D model to remove its empirically-failing scale effect. Module 6 is conceptually independent (relaxes the full-employment assumption that all growth models took for granted).

## What's in a module folder

Each module folder follows the same pattern:

- `Lecture Na.pdf` / `Lecture Nb.pdf` (and `Lecture 1c.pdf` for module 1) — Prof. Cozzi's content lectures.
- `Slides_SessionN.pdf` — Maria Bolboaca's exercise sessions (independent studies, exercise discussions). Note: module 2's slide file is named `Slides_Macro3_Session2.pdf`; module 6's second lecture is `Lecture6b.pdf` (no space).
- `textbook_chN.pdf` — sliced from the original textbook per the lecture plan's chapter mapping. Module 5 has none.
- For each `*.pdf`, sibling `*.md` (Docling-extracted text with `## Page N` headers) and `*.pages/p{NNN}.png` (per-page ~200dpi renders).
- `CLAUDE.md` — per-module index with file summaries, textbook references, and cross-module connections.

## Mock exam

`../mock exam/Mock_Exam-1.pdf` — four equally-weighted (25% each) essay questions covering: (1) empirical evidence on basic Solow (Module 1), (2) Solow with land and natural resources plus numerical simulation (Module 3, Ch 7), (3) Cozzi (2017) hybrid model and its policy implications (Module 5), (4) Solow conditions of the efficiency wages model (Module 6, Ch 11). Detailed style/format analysis will live in `EXAM_PROFILE.md` at workspace root (Step 4 deliverable, not yet written).

## Broken math

The PNG-fallback rule is defined in the root `CLAUDE.md` (always loaded). Most-affected files in this folder tree are all `textbook_chN.md` (modules 1-4 and 6) and most `Slides_SessionN.md`. Cleanest are module 1's lectures and `Lecture 2a.md` (formula model was on for those).
