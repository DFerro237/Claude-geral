---
name: versions-and-folders
description: >-
  Applies the vX.Y version pattern (small change, large change or new purpose, previous version to old), carefully reorganizes folders that already exist, including on a shared drive, and picks the period folder for a received file by its reference date. Use whenever saving a new version of a deliverable, even without an explicit request, and when the user says "save a new version", "make a version for so-and-so", "organize this folder", "this folder is a mess" or "where do I save this attachment". Not for files whose naming convention the project declares separately nor for creating or importing a project's numbered structure (project-structure).
---

# Versions and folders

The naming rule and what happens to the previous version (small goes to `old/`, large asks, new purpose coexists, same number across formats, delivery line) are in the global `CLAUDE.md`, section "Versioning of outputs", and are not repeated here.
This skill covers what the rule does not: how to classify the change, how to apply the rule day to
day and how to reorganize a folder that already exists without breaking anything.

The script `scripts/versions.py` only reads. It computes the next name and inventories folders, but never moves,
renames or deletes. You do the moving, after the rule or the user's approval.

The subcommands and flags are in Portuguese, as in the code: `proxima` (next) takes `pequena` (small) or
`grande` (large); `inventario` (inventory) takes `--recursivo` (recursive), `--sem-hash` (no hash) and `--json`.

```bash
python "<skill folder>/scripts/versions.py" proxima "<current file>" pequena|grande
python "<skill folder>/scripts/versions.py" inventario "<folder>" [--recursivo] [--sem-hash] [--json]
```

## Which mode

| | Mode A: version | Mode B: reorganize | Mode C: file what arrives |
|---|---|---|---|
| When | You have just generated a new version of one of your outputs | The user asked to organize a folder that already exists, in the project or on the shared drive | You are going to save a file received from outside (email attachment, material from a company) into a folder that receives files often |
| Autonomy | Apply the rule. A small version goes to `old/` on its own; for a large one you ask | Nothing changes without a triage approved by the user | Apply the rule to the new file, including creating the year or quarter folder. Files already there do not move without triage |
| Names | Only the new file, which is born right | By default, none. Renaming is a separate proposal | Keep the name the file arrived with, unless the user asks otherwise |

The difference in caution has a reason. In mode A you touch what you have just created, inside the project, and
you know what each file is. In mode B you touch what other people created and use. A moved file
breaks a path cited in a CRM card or in a meeting agenda, a changed name breaks the team's reference, and
the file that looks superseded may be exactly the one someone is using.

## Classify the change

| Type | Signal | Example |
|---|---|---|
| Small | Same structure, same content, same line of reasoning: corrected text, adjusted number, changed label, better supported recommendation | Report going from v1.3 to v1.4, with the same structure, corrected text and better supported recommendations |
| Large | New structure, new scope, broad rewrite, changed method, but it replaces the previous one | Report that gained a new section and had all cases reassessed with a new criterion |
| New purpose | Another use or another audience, and the previous material **is still in use** | Short version for a meeting alongside the full one; version for an external reviewer alongside the user's own |

If the request changes the purpose but does not say whether the previous material is still in use, ask:
"does it replace X or live alongside it?". Erring one way retires a file in use, and erring the
other way leaves two current files.

When it is a new purpose, the purpose goes into the base name, before the version. For example,
`analysis_external_review_v1.1.xlsx`, and not `analysis_v08_reviewer.xlsx`. A suffix
after the version is exactly what the rule forbids, and it breaks automatic reading of the name.

## Mode A: version

1. Classify the change with the table above.
2. Compute the name with `proxima`. A file in the old pattern (`v04`) or with no version yields `v1.1`, and the
   script warns. This is expected, because the user decided not to rename legacy files.
3. Save the new version in the same folder as the current file.
4. Handle the previous one according to `CLAUDE.md`. What it does not say:
   - **Folder for old files with another name** (`Old`, `Archive`, `Previous`): use that one and do not create a second one.
   - **Open file:** if there is a `~$` file with its name or the system denies access, do not force it.
     Say that the previous version stayed outside `old/` because it was open.
   - **Several formats:** all formats of the previous version go to `old/` together.
5. On delivery, the line from `CLAUDE.md` plus what went to `old/`. For example: "v1.4 replaces v1.3,
   small change, with better supported recommendations. v1.3 went to old/."
6. If the folder became messy, with 3 or more live materials at the root or more than 6 files outside
   `old/`, suggest in one sentence reorganizing it with mode B. Do not reorganize on your own, because the
   projects' `AGENTS.md` forbids touching the structure without authorization.

**Where mode A does not act.** Shared drive, folders outside the project and files whose naming exception
is declared in the global `CLAUDE.md` or in the project's `AGENTS.md`. In those places the existing name
prevails. The copy of an output that
goes to the shared drive gets the name the drive uses, such as a final meeting agenda with no version number.

## Mode B: reorganize

### 1. Define the scope

Confirm the exact folder and whether subfolders are included. Do not widen the scope on your own. "Organize
folder A" does not authorize touching folder B.

### 2. Inventory, read only

Run `inventario --recursivo`. On a synced cloud drive, use `--sem-hash` when there are many files, because reading the
content forces the drive client to download each file. The script lists, per material:

- the current version and the candidates for `old/`;
- the legacy files;
- and the doubts, among them:
  - a download copy `(1)`;
  - `final` or `ok` in the name;
  - a suffix after the version;
  - two files competing for the place of current file;
  - the same material with different years in the name;
  - an old candidate modified in the last 7 days;
  - an open file.

The inventory groups by name. It does not know what the file is. Look at the dates and, when the name is not
enough and the file is small, at the content.

The name patterns are at the top of the script. Status words are `final` and `ok` plus a few Portuguese
ones (`revisado`, `definitivo`, `aprovado`); copy markers are ` (1)` and ` - Copy`; the only English name it
treats as a folder of old files is `old`. If your team uses other words (`revised`, `Archive`), add them
to the `STATUS` and `PASTAS_OLD` patterns.

### 3. Triage with the user

Present one table per folder:

| # | File | Material | Proposal | Certainty | Why |
|---|---|---|---|---|---|
| 1 | `agenda_v03.docx` | agenda | old/ | certain | superseded by v04, same material |
| 2 | `agenda final.docx` | agenda | ask | doubt | no version, may be the delivered copy |

The **proposal** is one of five: stays, `old/`, material folder, `99.Archive` or ask.

The **certainty** is "certain" only when name, date and material leave no margin. Everything the inventory
flagged as a doubt, and everything you cannot assert, becomes "doubt", and the proposal becomes
ask. Do not settle a doubt by deduction. The user knows which file they use, and you do not.

Ask only what changes the action. A file that stays in place either way does not need to become a
question, even if the inventory noted something about it: record it as a remark in the row and
move on. A long list of questions with no consequence hides the few that matter.

In a large folder, with more than about 40 files, offer to build a triage HTML page.
It has one row per file, the choice between stays, old,
folder and rename, and a button that saves the decision as JSON. Then you execute from the saved
JSON. In a small folder, the table in the chat is enough.

### 4. Names, in a separate list

Renaming is another decision, with another list: "rename X to Y". On a shared drive, the default is **not to propose
mass renaming**, because the names are shared with the team. Propose only where the current name
gets in the way, such as `final`, `(1)` or two files with the same name. A legacy `vNN` file is only renamed if the
user approves the list.

### 5. Paths cited elsewhere

Before moving a **folder**, and not just a loose file, look for where its path appears:

- in external systems that store paths (CRM, cards). The list of a client's known places lives in
  the client's base, in `~/Projects/<Client> Base/05.Working_Files/Paths/cited-paths.md`.
  Read that file before moving a folder of a client that has a base. If the base exists and the file does not,
  say that the list of external places is missing and ask the user where the path may be cited
  before moving; do not conclude that there is no citation just because the list does not exist;
- in the project's meeting agendas and READMEs;
- in `CLAUDE.md` and in skills, when it is one of Claude's own folders.

If the path is cited, list where and ask. Moving the folder leaves the card pointing to a place
that does not exist, and nobody notices until they need the file.

### 6. Execution, only of what was approved

- Execute in batches, one subfolder at a time. What was not approved stays where it is.
- Before moving, save a manifest of every file that will change place. Use a hash in a local folder
  and size plus modification date on a cloud drive, where hashing would force the download.
- Move without overwriting (`mv -n`). If the destination already has a file with the same name, stop and ask.
  Exception: if they are two versions of the same material with the same number, the more recent one gets the
  next free number (e.g. the newer v2.3 becomes v2.4), and you do not need to ask.
- Never delete anything. A leftover file is a smaller problem than a lost file.
- Save the log of moves, with source and destination on each line, in the current project's `06.Outputs`,
  **never inside the reorganized folder nor on the shared drive**. This log is what undoes the
  operation: just move things back, line by line.
- When the reorganized folder is `06.Outputs` itself, save the log in the project's `99.Archive`,
  which is the place for historical records. If the project has no `99.Archive`, ask where to
  save it.

### 7. Check and report

Check that each destination exists, each source is gone, the count matches and the manifest checks out. Then
report what was moved, what stayed in place, what was renamed, where the log is and the doubts
that remain open.

## Mode C: file what arrives

User rule for a folder that receives files from outside on a recurring basis:
results from monitored companies, minutes and notices, board materials, monthly reports. The reason is to
find the file later by the period it refers to, without the folder turning into a running list.

**Inside a project with the numbered structure**, what is received goes to `04.Materials_and_Sources`, and in a
recurring project the period is the cycle subfolder, with the name the skill `project-structure`
defines. The reference date picks the cycle in the same way (items 3 and 4 below). Items 1, 2 and 5 apply to
folders of received files outside that structure, such as those on a shared drive and those of an area.

1. **At a minimum, one folder per year:** `2026/`.
2. **When the folder starts to fill up, year and quarter:** `2026/Q3-26/`. The signal is receiving one file
   per month or more. A notice or a shareholders' meeting minute, which arrive a few times a year, stay at year level only.
   A monthly result, which arrives every month, goes into year and quarter.
3. **The period is the one of the information's reference date, not the date the file was made or
   received.** The management spreadsheet with September results, prepared in October, goes to
   `Q3-26`, not to `Q4-26`. Find the reference date in the file name, in the email text or in the content
   ("August results", "period ended 06/30", `2026.05` in the name). For a notice or a call to a meeting,
   the reference date is the meeting date.
4. **With no identifiable reference date, use the file date**: the one in the name or in the document and,
   failing those, the date of the email that brought it. Say which date you used.
5. **Follow the structure the folder already has.** If it already uses year and quarter, or a month subfolder for
   a partial delivery, such as `Q1-26/Feb` in a split monthly delivery, save in the same pattern. In a folder that has no quarter
   yet, use the spelling the neighboring folders on the same drive use; with no reference, `Q1-26` to `Q4-26`.

What is allowed without asking and what is not:

- **Allowed:** creating the year or quarter folder the new file calls for and saving it there. The rule is the
  user's, and the file is the one you have just received.
- **Not allowed:** moving into those folders the files that were already loose in the folder. That is
  reorganization, and follows mode B. If the folder has loose files from other periods, suggest the
  reorganization in one sentence on delivery.
- **Switching from year to year and quarter** in a folder that already has files at year level is also mode B: the
  year's files would have to be redistributed. The new file goes into the pattern the folder has today,
  and the suggestion to switch to quarters goes in the delivery.

On delivery, say the final folder and the period, for example: "saved in `2026/Q3-26`, reference date September
2026, from the spreadsheet title".

## Subfolder per material

Only when the folder is messy. One folder per material, named after the material, such as
`Monthly report` or `Proposal client X`, each with its own `old/`. Creating these subfolders is
reorganization, so propose it first, with the before and after structure, and wait for the ok.

A duplicate the user asked for is not an error. The same version in a working folder and in a meeting
folder is intentional. The inventory shows identical files. Ask before treating one of them
as a leftover.
