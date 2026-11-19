# Using contexts

This folder gathers the contexts that apply to the project. The general working rules are in `AGENTS.md` and in the global instructions file, not here.

## File types

- **Specific context:** information about a client, project, company or topic.
- **Snapshot:** time-bound information that must be validated before use.

## Current files

List each context here, with one line on what it covers. Example:

- `01.work_context_<client>.md`  
  Stable, client-specific context.
- `02.snapshot_<client>_YYYY-MM.md`  
  Client information subject to updates. The suffix indicates the reference month.

Use `.md` files, sequential numbering and short names.

## How to consult

1. Read a specific context only when it matches the current client, project or topic.
2. Use snapshots only when relevant, and validate the reference date against current materials.

Do not read the whole folder by default. The presence of a specific context does not authorize applying it to another client.

## Preparing new projects

- **Projects for the same client:** use the project template unchanged.
- **Projects for other clients:** remove the previous client's material:
  - their contexts in this folder;
  - their subfolder in `02.Official_Templates`, whose templates are normative on brand and do not apply to another client.

A client brand skill can stay installed when its trigger prevents it from being applied to other clients.

## Contexts and skills

Agent Skills, in `~/.claude/skills` and valid in every project, are the canonical source of specialized procedures (spreadsheets, presentations, summaries) and are discovered automatically. That is why there are no bridge documents in this folder: contexts bring knowledge and criteria, without repeating the content of the skills.

Contexts guide execution, but specific and current facts must be confirmed in the task's sources.

Do not create, change, move or delete contexts without explicit authorization.
