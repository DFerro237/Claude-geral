---
name: session-retrospective
description: >-
  Closes the session with the Challenges block: finds the friction that cost time and may happen again, proposes where each lesson should live, with the text ready, applies only what was approved and records it in ~/.claude/challenges.md. Use when ending a session that had rework, a non-obvious error or a correction from the user, even without being asked, and when the user says "what were the challenges", "run the retrospective", "record this lesson", "this cannot happen again" or "review the challenges log". Not for the project state (project-status) nor for building a skill from scratch (skill-creator).
---

# Session retrospective

The rule is in the global `CLAUDE.md`, under "Evolution and preservation". This skill is the procedure.

The goal is for each session to leave the environment a little smarter: today's friction becomes an instruction, and the next session does not pay the same cost again. The user decides what goes in. You find, propose and record.

## What counts as a challenge

What counts is friction that **cost real time** and **can plausibly come back**. Both together. Examples:

- several attempts until finding the path that works, such as an API that refuses and an alternative method that solves it;
- a non-obvious error, or an error message that points to the wrong place;
- a tool that seemed missing but was outside the PATH, or the opposite;
- configuration, permission or encoding that failed silently;
- a correction from the user about style, format or criteria, because a correction that repeats is the most expensive of all;
- a rule that already existed and was not followed. Here the lesson is why it was not followed, not a new duplicated rule.

What does not count:

- a one-off failure that does not depend on anything of yours, such as a network drop that went away on the second try;
- a typo or a mistake corrected on the spot, at no cost;
- a preference for a single task, which the user did not ask to apply always;
- what is already recorded in the right place and worked in this session.

A session with no challenge has no block. Writing "Challenges: none" in every session becomes a ritual, and ritual is wasted tokens that nobody reads.

## Before proposing

1. **Search the log.** Read `~/.claude/challenges.md` looking for the words of the friction. If it has shown up before, say how many times and what was decided. A challenge that comes back after being refused or postponed deserves higher priority, and you should say so.
2. **Search the destination.** Before proposing a new rule, check whether it already exists in `CLAUDE.md`, in the skill or in memory. If it exists and was not followed, propose making it clearer or more visible, not a second copy. Duplicating instructions across files is what `CLAUDE.md` asks you to avoid.

## Where the lesson should live

| The lesson is | Destination |
|---|---|
| about a tool, flow or routine that already has a skill | the skill itself |
| a broad rule, valid in any task | `~/.claude/CLAUDE.md` |
| a rule for a single project | that project's `CLAUDE.md` |
| a fact about the machine, a system, a data source or a user preference | memory, in the memory system's format |
| a long, rarely used procedure | a guide in `~/.claude/guides/`, with one line in `CLAUDE.md` saying when to open it |
| a new, recurring flow that has no skill | a new skill, built with skill-creator |
| low cost or unlikely repetition | nowhere; only the log |

The underlying criterion is the cost of loading. `CLAUDE.md` is loaded in every session, so it only receives what is always valid. Skills and guides load on demand and can be longer.

## How to write the proposed change

The user decides in seconds if the text comes ready. For each challenge, bring:

- **where it goes:** file and section, or "new line after such item";
- **the exact text**, short, in the style of the destination file;
- **the reason inside the text itself**, because an instruction with a reason is followed with judgment, and an instruction without one is followed blindly or ignored;
- **the general form**, not the case: instead of "the video C3Sv... did not load the transcript", something like "YouTube transcript in the built-in browser: the panel comes empty without login; the full caption is in the `timedtext` request the player already made".

Avoid CAPITALS and "ALWAYS/NEVER" without explanation. A change to a skill preserves the rest of the skill: it changes only the passage the lesson reaches.

## Block format

In the final message of the session, before the block with what you need from the user and before the app's next-step box:

```
Challenges:
1. <short title>. <what happened and how much it cost, in one or two sentences>.
   Destination: <file and section>. Proposed text: "<text>".
   <if it already appears in the log: "3rd occurrence; refused on 10/02">
2. ...
```

At most about five items, from most to least expensive. If there are more, the smaller ones go only to the log, and you say how many were left out.

The decision follows the question rules in `CLAUDE.md`. If the items fit in the selector, ask through it which ones to apply, with your recommendation first. If the decision needs context, ask in text.

## After the answer

- **Apply only what was approved**, item by item. Read the destination file before editing, because the user may have changed it.
- **A change to `CLAUDE.md`** follows the changelog rule in its "Evolution and preservation" section: a record in the changelog file it names and the previous version saved where it says. A changed general rule also goes to the other AIs' copies, as the same section asks.
- **A relevant change to a skill** goes through skill-creator. A small adjustment, such as a line or an example, can be made directly.
- **Memory** follows the rules of the memory system: one fact per file and the pointer in `MEMORY.md`.
- **Record every item presented**, approved or not, in `~/.claude/challenges.md`, with the decision. The log is what makes it possible to notice repetition next time.

## Log

Single file: `~/.claude/challenges.md`. It is a single file because a good part of the friction crosses projects, such as shared drives, Office, encoding and connectors. One line per challenge, in the file's table:

| Date | Project | Challenge | Proposed destination | Decision |
|---|---|---|---|---|
| 2026-10-17 | General | LibreOffice seemed missing: it was outside the PATH | `CLAUDE.md`, installed tools section | applied |

The decision is `applied`, `refused`, `postponed` or `log only`. To review the log when the user asks, group by theme and show what repeats and what was postponed.

## Unattended execution

In a scheduled task or routine without the user present, do not change skills, `CLAUDE.md` or memory. Write the challenges in the task's result file, in the same format, for the user to decide later. If your setup has a guide for scheduled tasks (for example `~/.claude/guides/scheduled-tasks.md`), it explains why.
