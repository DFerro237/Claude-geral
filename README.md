# Claude-geral

Reusable [Claude Code](https://claude.com/claude-code) skills, one subagent and a project folder template, focused on analytical and finance-oriented deliverables: documents, decks and spreadsheets that state their sources, declare their gaps and read on their own.

## What is inside

| Item | Type | What it does |
|---|---|---|
| [`analytical-documents`](skills/analytical-documents/) | skill | Opinions, memos, technical notes, analysis and due diligence reports in Word, with sourced claims, declared gaps and a width checker for the `.docx`. |
| [`create-professional-presentations`](skills/create-professional-presentations/) | skill | Consulting-style decks in PowerPoint or Google Slides: action titles, structured text, sourced exhibits, plus a geometric checker for overlaps and margins. |
| [`create-executive-summary`](skills/create-executive-summary/) | skill | Executive summary slides that condense context, conclusions, alternatives and recommendation so they stand on their own. |
| [`professional-spreadsheets`](skills/professional-spreadsheets/) | skill | Spreadsheets and financial models (valuation, DCF, projections, cap table, budget) that keep structure, formulas, traceability and checks. |
| [`fact-checker`](agents/fact-checker.md) | subagent | Checks a finished deliverable against its sources for unsupported claims, conclusions stronger than the evidence and numbers that do not match. Changes nothing, returns findings. |
| [`project-template`](project-template/) | folder template | A numbered folder structure for a Claude project (context, routines, official templates, style references, sources, working files, outputs, archive), with a `CLAUDE.md` and a README per folder explaining what goes in and how much authority it has. |

## Installation

1. Copy each folder under `skills/` into `~/.claude/skills/`, for example `~/.claude/skills/analytical-documents/`.
2. Copy `agents/fact-checker.md` into `~/.claude/agents/`.
3. For a new project, copy the contents of `project-template/` into the project folder and adjust the `CLAUDE.md`.

Claude Code discovers skills and agents on the next session. Install only the items you need; each skill names the others it works with.

## Requirements

- The document skills are a conventions layer over Anthropic's built-in `docx`, `pptx` and `xlsx` skills, which remain responsible for the file tooling.
- The bundled Python scripts need Python 3 with `python-docx` (`analytical-documents`) and `python-pptx` (`create-professional-presentations`).
- Where a skill mentions your `CLAUDE.md`, it refers to rules you may define there. The skills work without one.
