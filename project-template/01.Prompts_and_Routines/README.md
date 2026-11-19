# Using prompts and routines

This folder holds prompts and routines for recurring processes that Agent Skills do not cover. The rules for running them are in `AGENTS.md`, section "Contexts and routines".

It starts empty. Presentations, executive summaries and spreadsheets are handled by the global skills, in `~/.claude/skills`, with no separate routine, so that content and reading are not duplicated.

## When to create a routine

Create a routine only when the process is not covered by a skill and is worth pinning down. A routine should be a short pointer (goal, skills to load, minimum inputs and sequence), never a copy of a skill.

Use `.md` files, sequential numbering and short names.
