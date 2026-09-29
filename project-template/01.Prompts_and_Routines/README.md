# Using prompts and routines

This folder holds prompts and routines for recurring processes that Agent Skills do not cover. The triggering rules are in `CLAUDE.md`, section "Using prompts and routines".

For now it is empty. Presentations, executive summaries and spreadsheets are handled by the global skills in `~/.claude/skills`, with no separate routine, so that neither content nor reading is duplicated.

## When to create a routine

Create a routine only when the process is not covered by a skill and is worth formalizing. A routine should be a short pointer (objective, skills to load, minimum inputs and sequence), never a copy of the skill.

Use `.md` files, sequential numbering and short names.
