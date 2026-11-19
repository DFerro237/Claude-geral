# Claude-geral

Reusable [Claude Code](https://claude.com/claude-code) skills, a subagent, a global `CLAUDE.md` and a project folder template for professional work: finance spreadsheets and models in Excel, presentations, analytical documents in Word, quality review of finished decks, and the housekeeping around them (project status, versions, session retrospectives).

The common thread is deliverables that state their sources, declare their gaps and read on their own.

## What is inside

| Item | Type | What it is for |
|---|---|---|
| [`CLAUDE.md`](CLAUDE.md) | global instructions | A standard `~/.claude/CLAUDE.md`: precedence, response style, questions, files and git, writing, evidence, use of skills, output versioning, sanitizing delivered files, model and effort per task, and session retrospectives. |
| [`professional-spreadsheets`](skills/professional-spreadsheets/) | skill | Finance spreadsheets and models in Excel (valuation, DCF, projections, cash flow, budget, cap table) that keep structure, formulas, traceability and checks. |
| [`create-professional-presentations`](skills/create-professional-presentations/) | skill | Consulting-style decks: action titles, structured text, sourced exhibits, plus a geometric checker for overlaps and margins. |
| [`create-executive-summary`](skills/create-executive-summary/) | skill | Executive summary slides that condense context, conclusions, recommendation and decision so they stand on their own. |
| [`review-presentations`](skills/review-presentations/) | skill | Fine-tooth-comb review of a finished deck (typos, terms, fonts, italics, positions, links), with every finding confirmed before any change and an error log in Excel. |
| [`analytical-documents`](skills/analytical-documents/) | skill | Memos, opinions, technical notes and due diligence reports in Word, with sourced claims, declared gaps and a checker for the `.docx`. |
| [`project-status`](skills/project-status/) | skill | Builds and updates a `STATUS.md` at the project root, so another session or another AI can pick up the work without rereading everything. |
| [`versions-and-folders`](skills/versions-and-folders/) | skill | The `vX.Y` version pattern (small change, large change, new purpose, previous version to `old/`) and careful reorganization of existing folders, with a helper script. |
| [`session-retrospective`](skills/session-retrospective/) | skill | Closes a session with a "Challenges" block: the friction that cost time, where each lesson should live, applied only after approval and logged. |
| [`fact-checker`](agents/fact-checker.md) | subagent | Checks a finished deliverable against its sources for unsupported claims, conclusions stronger than the evidence and numbers that do not match. Changes nothing, returns findings. |
| [`project-template`](project-template/) | folder template | A numbered folder structure for a project (context, routines, official templates, style references, sources, working files, outputs, archive), with an `AGENTS.md` shared by any AI, a `CLAUDE.md` that imports it, and a README per folder explaining what goes in and how much authority it has. |

## Installation

1. Copy each folder under `skills/` into `~/.claude/skills/`, for example `~/.claude/skills/professional-spreadsheets/`.
2. Copy `agents/fact-checker.md` into `~/.claude/agents/`.
3. Put `CLAUDE.md` at `~/.claude/CLAUDE.md`. If you already have one, merge the sections you want instead of replacing it, and add your personal style rules where the file shows an example.
4. For a new project, copy the contents of `project-template/` into the project folder and adapt `AGENTS.md` to the project's goal.

Claude Code discovers skills and agents on the next session. Install only the items you need; each skill names the others it works with, and the cross-references assume the names used here.

## Requirements

- The document skills are a conventions layer over Anthropic's native `docx`, `xlsx`, `pptx` and `pdf` skills, which remain responsible for the file tooling. Keep those enabled.
- The bundled Python scripts need Python 3 with `python-docx` (`analytical-documents`), `python-pptx` (`create-professional-presentations`), and `python-pptx`, `openpyxl`, `pdfplumber`, `pypdfium2` and `Pillow` plus LibreOffice (`review-presentations`). `versions-and-folders` uses only the standard library.
- The scripts were written for Portuguese-speaking users: code identifiers and command-line flags are in Portuguese, while docstrings, help texts and messages are in English. Each `SKILL.md` documents the flags as they are.
- Where a skill mentions your `CLAUDE.md`, it refers to the rules in the `CLAUDE.md` of this repository, or to the ones you define. The skills also work without it.

## Author

Maintained by DFerro237.
