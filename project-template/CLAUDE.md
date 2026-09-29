# Project instructions

The general working rules live in your global `CLAUDE.md` (`~/.claude/CLAUDE.md`), if you have one, and apply here without needing to be repeated: writing, evidence, use of skills, versioning, wrap-up and machine environment. The two files load together; neither replaces the other.

This file covers only what is specific to this folder structure.

## Form precedence

For decisions on layout, brand, typography and structure, the order is: user instruction, then the base file or current material, then `02.Official_Templates`, then `03.Style_References`.

This is the single definition of the form chain in the project; the folder READMEs refer back to it. For facts and figures, neither of the last two is a source.

## Project structure

Use the folders as needed:

- `00.Claude_Context`: applicable instructions, criteria and contexts.
- `01.Prompts_and_Routines`: reusable prompts, playbooks and routines.
- `02.Official_Templates`: institutional templates and brand manual. Normative on brand and form. Templates for a specific client go in a subfolder named after that client and apply only to that client.
- `03.Style_References`: examples and references of form, structure and design. Descriptive.
- `04.Materials_and_Sources`: data, documents and evidence for the current task.
- `05.Working_Files`: preserved base files.
- `06.Outputs`: deliverables created or updated.
- `99.Archive`: backups and historical materials. Not a current factual source, and must not be edited.

Not every folder needs to be used in every task.

Skills and subagents do not live here: they are in `~/.claude/skills` and `~/.claude/agents`, where they apply to every project.

The READMEs in folders `02` to `05` describe what goes into each one and what its authority is. Read a folder's README the first time you use that folder in the project, or when in doubt about a file's authority. There is no need to reread it for every task.

## Using contexts

In non-trivial analysis or deliverable tasks:

1. read client-, project- or topic-specific contexts only when they match the current request;
2. consult complementary contexts only when they apply to the format or objective;
3. validate dated snapshots against current materials before treating any item as current fact.

Do not apply a specific context just because the file is present. Do not read the whole folder by default.

## Using prompts and routines

The `01.Prompts_and_Routines` folder holds recurring procedures that Agent Skills do not cover. Run a routine when the user mentions it. When a routine clearly applies but was not mentioned, say that it exists and ask for direction before running it; this does not prevent a skill from triggering automatically. Do not change, move, rename or delete routines without explicit authorization.

## References, materials and base files

- Use references as a standard of form, never as an automatic factual source.
- Use `04.Materials_and_Sources` as the main source for the task and preserve its files.
- Preserve the files in `05.Working_Files`; generate updated versions in `06.Outputs`, unless instructed otherwise.
- Do not treat base files or historical files as a current factual source when more recent materials exist.
- Create backups only when there is a material risk of loss, overwriting or structural change.

## Preserving the structure

Do not reorganize the project structure without explicit authorization.
