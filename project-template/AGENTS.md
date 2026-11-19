# Project instructions: <project name>

Rules for this project, valid for any AI (Claude, Codex, Gemini and others). The general rules (writing, evidence, versioning, execution) live in each AI's global instructions file and are not repeated here.

## Template

This folder is the template for new projects. Keep a pristine copy of it. A new project starts from a copy, without `99.Archive` contents, without large client templates it does not need, without caches, without history and without this folder's `STATUS.md`; the new project creates its own `STATUS.md` (skill `project-status`). Adapt this file to the new project's goal.

## Form precedence

For layout, brand, typography and structure: user instruction, then the base file or current material, then `02.Official_Templates`, then `03.Style_References`. This is the single definition of the form chain in the project; the folder READMEs refer back to it. For facts and figures, neither of the last two is a source.

## Folders

- `00.Claude_Context`: project instructions, criteria and contexts. The name is historical; it applies to any AI.
- `01.Prompts_and_Routines`: reusable prompts, playbooks and routines.
- `02.Official_Templates`: institutional templates and brand manual. Normative on brand and form. A client's templates go in a subfolder named after that client and apply only to that client.
- `03.Style_References`: examples of form, structure and design. Descriptive.
- `04.Materials_and_Sources`: data, documents and evidence for the current task. Main source; preserve the files.
- `05.Working_Files`: preserved base files. The updated version goes to `06.Outputs`.
- `06.Outputs`: deliverables created or updated.
- `99.Archive`: backups and historical materials. Not a current factual source, and must not be edited.

Not every folder is used in every task. The READMEs in folders `02` to `05` say what goes into each one and how much authority it has: read a folder's README the first time you use it or when in doubt.

## Contexts and routines

- Read a client, project or topic context only when it matches the current request. Do not apply a context just because the file exists, and do not read the whole folder by default. Validate a dated snapshot against current material before treating it as current fact.
- Run a routine from `01.Prompts_and_Routines` when the user mentions it. If a routine clearly applies and was not mentioned, say so and ask for direction before using it.
- Do not create, change, move or delete contexts and routines without explicit authorization.

## Sources and base files

- References are a standard of form, never an automatic factual source.
- Do not treat a base file or historical file as a current factual source when more recent material exists.
- Create a backup only when there is a material risk of loss, overwriting or structural change.
- Do not reorganize the project structure without explicit authorization.
