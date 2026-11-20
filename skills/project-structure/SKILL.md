---
name: project-structure
description: >-
  Teaches and applies the numbered folder structure (00 to 06 and 99) for a complex project in the user's projects folder (~/Projects): creates a new project, imports the structure into a project that has grown, organizes cycles of recurring work (quarter, month, meeting), decides where to keep a template, a reference or a shared base, and closes a project by moving it to ~/Projects/_Archive. Use when the user says "create a new project", "import the standard folder structure", "organize this project", "where do I keep this", "the quarterly report has started, how do I organize it", "this template serves several projects" or "this project is over, archive it", even without naming the skill. Not for bringing in a project from elsewhere, for file versions (versions-and-folders) nor for the STATUS.md (project-status).
---

# Project structure

Projects live in `~/Projects/<project>`, in the user's home folder, outside any synced folder. This skill says how to organize what goes inside them. It ships no template files: it creates the folders and the READMEs from this text and from `references/readmes.md`, and so it works on any machine.

## When to use the structure

The structure exists for a **complex** project: several sources, versions of a deliverable, several sessions or several AIs, or work that repeats. A simple project (one deliverable, few sources, one or two sessions) is a folder with the files, without numbered folders. Forcing the structure on a simple project creates eight empty folders for three files.

When in doubt, propose it to the user and wait for the acceptance. A project that grows gets the structure later (see "Import the structure").

## The folders

A project that adopts the structure has **all** the folders, always with the **same number and the same name**, even when empty. The user says "drop it in 4" or "the version is in 6", and that only works if 4 and 6 are the same in every project. The numbers also set the order in which the folders appear in the file explorer. Do not renumber, do not rename and do not omit a folder because it is empty.

| Folder | What goes in | Authority |
|---|---|---|
| `00.Claude_Context` | context of **this** project: request, scope, fact sheet, design, plan. The name is historical and applies to any AI | guides; a current fact is confirmed in the source |
| `01.Prompts_and_Routines` | prompts and routines that only this project uses and that no skill covers (e.g. the prompts for the stages of a scan) | project instruction, when cited |
| `02.Official_Templates` | a template exclusive to this project | normative on form |
| `03.Style_References` | finished materials that show the standard (earlier editions, examples) | descriptive, never a factual source |
| `04.Materials_and_Sources` | sources and evidence for the task | main source; preserve |
| `05.Working_Files` | the base file to be updated (the current version from which the new one comes) | preserve; the derived version goes to 06 |
| `06.Outputs` | deliverables, with versions (`versions-and-folders`) | not a source for a new task without confirming it is still current |
| `99.Archive` | what has gone out of circulation entirely | historical; do not edit |

At the root: `AGENTS.md` (the project's rules, for any AI), `CLAUDE.md` (starts with `@AGENTS.md` and only adds what is specific to Claude), `STATUS.md` (skill `project-status`), a `.gitignore` with `work/`, and `git init`. Temporary files and drafts go in `work/<ai>/<task>`, never in a numbered folder.

The text of each README is in `references/readmes.md`. Read it when creating the folders.

## Where each thing lives

The rule is to keep each thing in the narrowest place that serves whoever uses it, and never to copy between projects.

| Who uses it | Where it lives |
|---|---|
| only this project | in the project (folder 00, 01, 02 or 03) |
| several projects of the same client (context, investment thesis, records, brand template, shared reference) | in the client's base, a project of its own such as `~/Projects/<Client> Base`, with the same numbering |
| any work, for any client | `~/Projects/_Templates`, with a README that explains each item |

A client's material applies only to that client's work: one client's template, thesis and context do not go into another client's project.

When the project needs something shared, the folder's README points to where it is ("the client context is in `~/Projects/<Client> Base/00.Claude_Context`"). Do not copy: the copy ages silently, and each project ends up with a different version of the same fact. Something is born in the project and moves up to the client's base or to `_Templates` when a second project needs it.

## Area and project

Some folders in `~/Projects` are **areas**, not projects: they group many pieces of work on one theme (a portfolio of companies, a prospecting pipeline). An area has folders by theme (one per company, one per event) and its own `AGENTS.md` and `STATUS.md`. Each piece of work inside it that produces a deliverable is a project, and that is what gets the numbered structure, if it is complex.

## Recurring work

A project that repeats (quarterly report, monthly committee meeting, weekly agenda) has **one** structure, and the cycle becomes a subfolder inside the folders that change every cycle:

```
Quarterly report/
  03.Style_References/             <- a single one, valid for every cycle
  04.Materials_and_Sources/2026 Q3/
  05.Working_Files/2026 Q3/
  06.Outputs/2026 Q3/
```

Cycle name: `YYYY QN` for a quarter (`2026 Q3`), `YYYY.MM` for a month or a monthly meeting (`2026.11`), `YYYY.MM.DD` for a weekly one. Folders 00 to 03 stay outside the cycle: the standard and the earlier editions serve all of them. Do not create the whole structure again for each cycle; that repeats folders 00 to 03 and scatters copies of the standard.

## Uses

### New project

1. Confirm that it is complex (or that the user asked for the structure).
2. Create `~/Projects/<name>` with the folders in the table and a README in each one.
3. Write the `AGENTS.md` with the project's goal and what is specific to it (sources, destination on the shared drive, client); `CLAUDE.md` with `@AGENTS.md`; `STATUS.md` through the skill `project-status`; `.gitignore` with `work/`; `git init`.
4. If the project belongs to a client with a base of its own, point to the base in `AGENTS.md` and in the READMEs, without copying.

### Import the structure

For a project that exists and has grown: create only the folders and READMEs that are missing. Do not move, rename or overwrite what already exists without showing the list to the user and getting the OK. A loose file at the root or in a folder outside the pattern goes into a destination proposal ("`source.xlsx` to 04"), approved before moving.

### Where do I keep this

Answer with the folder (number and name) and the reason in one line, from the folders table and the "Where each thing lives" table. Material received from third parties goes to 04, in the cycle subfolder when there is one; the file's reference date picks the cycle (`versions-and-folders`).

### Close a project

A finished project nobody will come back to: close the `STATUS.md` (situation "closed", date, where the final deliverable is) and move the whole folder, with its git, to `~/Projects/_Archive`, with the user's OK. `_Archive` keeps whole projects and must stay in the backup; do not confuse it with the `99.Archive` inside a project, which keeps only what went out of circulation within it. Closed work inside an area stays in the area.
