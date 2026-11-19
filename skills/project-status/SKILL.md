---
name: project-status
description: >-
  Builds or updates the STATUS.md at the root of a project in the projects folder (goal, situation, current files, decisions, open items, next step), so that another session or AI can pick up the work without rereading everything. Use when the user says "update the status", "where did we stop", "do the handoff" or "leave a note for next time", when closing a block of work that changes the current file, a decision or an open item, and in a project that has no STATUS yet. Not for recording what was learned in the session (session-retrospective).
---

# Project status

`STATUS.md` is the first thing a new session reads in a project. In less than a page it answers: what the project is for, where it stands, which file is the current one, what has already been decided and what is still missing. Whoever picks up the work, be it another Claude session, Codex, Gemini or the user, does not need to reread the chat or open the whole folder.

## Where it lives

At the project root: `<projects folder>/<project>/STATUS.md`. One per project. A project with subprojects (such as a prospecting project with several fronts) has a single one, with a short section per subproject.

## Template

```markdown
# Status: <project name>

Updated on YYYY-MM-DD by <Claude | Codex | Gemini | user>.

## Goal
<2 or 3 lines: what the project delivers and to whom.>

## Situation
<In progress | Waiting for <what, from whom> | Completed on YYYY-MM-DD.>
- **Current:** `<relative path of the file that is valid today>` (and where it is on the shared drive, if it was delivered).
- <what matters most to know right now, in a few items>

## Decisions
- YYYY-MM-DD: <decision by the user or by the committee, with the source when there is one>.

## Open items and next step
- <open item: what is missing, who it depends on>
- **Next step:** <the first thing the next session should do>.

## Where things are
- Sources: `<folder>`; working base: `<folder>`; scripts or plans: `<folder>`.
- Skills and routines used: `<skill>`.

## Linked projects
- `<project>`: <what one delivers to the other and which version the other uses today>.

## History
- YYYY-MM-DD: <milestone, one line>.
```

Sections with no content are removed instead of being left with "none". A completed project can keep only Goal, Situation (with the final files and where they were delivered), Decisions and History.

## How to write it

- **Current state, not a diary.** When updating, rewrite Situation and Open items for the present moment. What is no longer valid leaves those sections; if it was a milestone, it becomes one line in History. A STATUS that grows every session turns into a log, and nobody reads logs.
- **Short.** Up to about 80 lines. History keeps at most about 10 milestones, most recent first. Long detail (plan, reconciliation, list of checks) lives in its own project file, and the STATUS only points to it.
- **Detail stays in the report.** A cell, a spreadsheet row or a reconciliation account goes into the report of the round or the project plan; the Situation item says the essentials in one or two lines and points to it.
- **Cyclical project** (quarterly round, monthly close): Situation describes the open round. When it closes, the round becomes one line in History and the remaining open items move on to the next one.
- **Paths, not descriptions.** "Current: `06.Outputs/monthly_report_v3.16.pptx`" is worth more than "the latest version of the report". Use paths relative to the project root.
- **Facts with backing.** Write only what is in the files, in the project memory or was said by the user in this conversation. What you inferred gets "(inference)". What you could not find out goes to Open items as "confirm with the user: ...", instead of being filled in by a guess.
- **Absolute dates** (YYYY-MM-DD), because "yesterday" loses its meaning in the next session.
- **No secrets and no copying the chat.** No tokens, passwords or sensitive personal data. Summarize the decision, not the conversation.

## When to update

When to update, and the care of rereading before editing, are in the `AGENTS.md` at the root of the projects folder, when there is one (section on several AIs in the same project). In short: once per block of work that changes the current file, a decision or an open item, not on every file save; before handing the work over; and, with two sessions active, each one updates only its own part.

## How to build it the first time

1. Read the project's `AGENTS.md`, `00.Claude_Context/README.md` and, if they exist, `plan.md` and the project's Claude memory.
2. List `06.Outputs` (or the outputs folder an older project uses) and find the highest version of each material by the vX.Y pattern, or by the exception the project's `AGENTS.md` declares (a model that feeds a report may use `_vNN`, for example); it is the candidate for current file. A file inside `old/` is not current.
   - The name says which file is valid, not what it contains. To describe a current version, read its latest record: a `Sources` tab, a note in the file itself or the report of the round. A skill's reference sheet, an earlier STATUS and memory may be outdated, because old sheets and STATUS files repeat decisions that were already replaced.
   - If the project delivers to another one (a model that feeds a report, for example), record the link under "Linked projects".
3. Look at the file dates to tell whether the project is stalled or active, and whether something was delivered to the shared drive.
4. Folder too large to read in the session: send a subagent with an economical model to survey versions, dates and context files, and write the STATUS yourself from what it brings back.
5. Show the STATUS to the user when it has relevant gaps; otherwise, save it and say in one line that you saved it.
