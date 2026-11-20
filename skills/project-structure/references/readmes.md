# Text of the folder READMEs

Use it when creating the folders. Adapt only what belongs to the project (for example, pointing to the client's base). Each README starts with `# Using <folder>`.

## 00.Claude_Context

Context of **this** project: request, scope, what was agreed with whoever asked for it, fact sheet, design, plan. The project's rules live in the `AGENTS.md` at the root; the current state, in `STATUS.md`.

- Read a context only when it matches the task. Do not read the whole folder by default.
- A dated snapshot (with the month in its name) is validated against current material before it becomes fact.
- Client context that applies to several projects does not live here: it lives in the client's base. Point to it in this README instead of copying.
- Do not create, change or delete contexts without the user's authorization.

## 01.Prompts_and_Routines

Prompts and routines that only this project uses and that no skill covers. A routine is a short pointer: goal, skills to load, inputs and sequence. Never a copy of a skill.

- Run a routine from here when the user mentions it. If one clearly applies and was not mentioned, say so and ask for direction.
- It can stay with only this README.

## 02.Official_Templates

A template exclusive to this project. A client's brand template, used in several projects, lives in the client's base; a generic template lives in `~/Projects/_Templates`.

- **Authority:** normative on form (color, font, logo, layout). The template beats the references in 03 and loses to the material being edited and to the user's instruction.
- **Never a factual source:** filler text, numbers and sample names exist only to show the form.
- Generate the deliverable in a copy, in 06; preserve the original.
- It can stay with only this README.

## 03.Style_References

Finished materials that show how the work is written and structured: earlier editions, approved versions of recurring material, external examples of form.

- **Authority:** descriptive. It shows the practiced standard (style, density, anatomy, source and footer conventions); it does not impose a layout.
- **Never a factual source:** data, numbers, dates and conclusions from an old edition are not reused.
- In recurring work, this folder is a single one for every cycle.
- Select only what is comparable to the deliverable; do not read the whole folder.

## 04.Materials_and_Sources

Sources and evidence for the task: reports, spreadsheets, trial balances, documents received, transcripts, minutes, exported e-mails, downloaded external sources.

- It is the main source. Assess date, origin and consistency before treating old or contradictory material as definitive.
- A lookup made on the spot in a public database is also a source: record the date and what it proves and does not prove; save the result here, with the date in the name, when it is material.
- In recurring work, one subfolder per cycle.
- Do not change the files here; copy them to the applicable folder when you need to derive something.

## 05.Working_Files

The base file from which the new version comes: the current version of an agenda, report, presentation or spreadsheet; a direct model for the new version.

- Do not change it directly; the derived version goes to 06.
- Confirm that the base file is compatible with the period and the scope of the task.
- It is not a factual source when there is newer material in 04.

## 06.Outputs

Deliverables created or updated. Versions follow the skill `versions-and-folders`: `name_vX.Y.ext`, without overwriting what was delivered; a superseded version goes to the `old/` of the same folder.

- Not a source for a new task without confirming that the deliverable is still current.
- In recurring work, one subfolder per cycle.

## 99.Archive

What has gone out of circulation entirely within the project: an abandoned deliverable, a replaced context, a superseded base file. A superseded version of material still in use goes to the `old/` of its own folder, not here.

- Nothing here is a current source. Consult it only for history or comparison.
- Do not edit and do not use it for drafts.
