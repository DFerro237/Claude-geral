---
name: review-presentations
description: >-
  Does the fine-tooth-comb standardization pass on a finished PowerPoint deck (terms, font, italics, title and footer position, typos, grammar and links), with an error log in a spreadsheet and confirmation of every finding before changing anything. Trigger when the request says "go over it with a fine-tooth comb", "review this deck's standards", "check the formatting" or "see if everything is consistent". Not for reviewing the argument or narrative (create-professional-presentations).
---

# Presentation review

Checking a finished deck, when the content has already been decided and what is at stake is the finish: the same thing written two ways, a font that slipped through, a title 2 pt out of place, a link that leads nowhere.

This matters because finishing errors have a disproportionate cost. Nobody questions the thesis because of an `Estimated tiem`, but everybody notices, and attention leaves the argument.

Also load the native `pptx` skill for the file tooling, and the client's brand skill when there is one, because the official palette and typography come from it.

## The principle behind everything

**You do not decide what is right. You find divergences and bring them to the user.**

A deck may diverge from the template on purpose, and a slide may be frozen by an earlier decision. That is why this skill never fixes anything directly: it identifies, presents a table, and waits for confirmation. The cost of asking is one message. The cost of "fixing" what was intentional is redoing approved work.

## 1. Confirm the scope before looking at the file

Ask which dimensions to review. Do not start without that, because sweeping everything in a large deck produces a long, expensive list, and much of it may not matter.

Available dimensions, with the ID prefix of each:

| ID | Dimension | What it checks |
|---|---|---|
| `G` | Spelling and typing | Typos, diacritics, agreement, multiple spaces (including after punctuation and with non-breaking spaces), line-break hyphen stuck to the word |
| `N` | Naming and terms | One spelling per term, a single date format, standardized appendix references |
| `F` | Font | A single typeface, including inside tables |
| `I` | Italics | Foreign-language terms in italics, acronyms and proper names in roman |
| `A` | Alignment and grid | Title, subtitle and footer at the same coordinate within each block |
| `R` | Footers and references | Source line and numbered notes aligned |
| `L` | Links | The link resolves, the label matches the target, appendices have a way back |
| `U` | Numbers and units | Currency spacing, plurals, the same number matching across slides |
| `C` | Colors | One shade per function, no near variant of a color already in use |
| `E` | Exhibits | Title, source and axis labels present and consistent |
| `H` | File hygiene | Empty slides, orphan shapes, editing leftovers |

Also ask whether any slide is frozen, that is, whether some part must not be touched. If so, respect it absolutely: no alignment, no size, no position.

## 2. Pin down the reference for judgment

Before calling anything an error, define what you are comparing against.

**Look for an earlier review spreadsheet in the project**, usually under materials and sources. Its "Standards" tab records the canonical forms already agreed. Treat it as established norm and do not reopen the discussion: if it says `tranche` stays in roman, do not propose italics.

**Without an earlier spreadsheet, derive the standard from the deck itself.** Establish the dominant pattern, not the template's, because the current file beats the template in the project's precedence chain. Establish it **per block**: content slides and appendices often have a different grid, and that is structure, not error. The cover and section dividers almost always leave the grid by design.

When the deck's dominant pattern diverges from a standard recorded earlier, report the divergence instead of choosing on your own which one wins.

## 3. Inspect

The scripts live in this skill's folder, not in the project's. Call them by full path:

```bash
python "<skill folder>/scripts/inspect_deck.py" "path/to/deck.pptx"
```

It returns the full inventory: text per paragraph, font per run, italics, position, size and autofit mode of each shape, hyperlinks with the resolved target, and the automatic checks for currency, dates and spelling variants. The output comes in sections tagged with the dimension prefix, so read only those in the confirmed scope. Use `--texto` when you need the full text for the typing and grammar review, and `--slides` to limit the sweep.

Read the output with suspicion. Before logging any finding, check `references/pitfalls.md`, which lists the false positives that have already cost rework, such as Arial that is a bullet font and not a text font, and superscript that exists as an attribute and not as a character.

Some automatic checks in the script look for patterns of the language the deck was written in (appendix labels, currency symbols, plural of magnitude words). Adapt or ignore them when the deck is in another language, and do the same check by reading.

## 4. Present in the chat and stop

Build one table per category, in the chat, with these columns:

```
ID | Slide | Current | Should be | Recommendation
```

`Recommendation` takes **fix**, **doubt** or **do not fix**, and it is your reading, not the decision. Use doubt when both forms are defensible and the choice is one of style, not correctness.

Quote the literal excerpt in "Current". The user needs to recognize their own text to judge quickly.

**Do not change anything until confirmation.** If they say to fix only part, or reclassify an item, that is what holds.

When the explanation of a finding does not fit in the table row, offer to detail it instead of stuffing the cell. A structural divergence, such as two subtitle formats across blocks, almost always needs a paragraph of its own.

### Multiple spaces get their own treatment

A run of spaces may be deliberate layout (pseudo-column, manual line break, indent), and fixing it dismantles what someone built. `inspect_deck.py` returns dimension `G` in two lists:

| Script list | Recommendation in the table | What to do |
|---|---|---|
| Probable typo | fix | Same as any other error |
| Possibly deliberate formatting | doubt | Show in the chat the whole paragraph and the neighboring lines of the same shape, and **ask** |

Never fix an item from the second list without an answer, and do not show only a snippet: it is the alignment across whole lines that reveals the pseudo-column. If the user confirms it is deliberate, the item goes to "Not fixed" with the user-decision reason (`Decisão do usuário`, see `references/error-log.md`), and the pattern goes to "Standards".

## 5. Apply what was approved

Work on a copy in the outputs destination, preserving the base file, unless told to edit the file itself.

Use the helpers in `scripts/edit.py`. They exist because PowerPoint text lives fragmented in runs, and `foodservice` may be split into `food` and `service`. Direct replacement in the XML gets these cases wrong and destroys formatting.

Order from least to most invasive: text, italics, position, links. That way, if something breaks, the last step applied is the suspect.

## 6. Verify in three layers

```bash
python "<skill folder>/scripts/verify.py" "original.pptx" "corrected.pptx" \
  --proibido "wrong excerpt 1,wrong excerpt 2" \
  --esperado "corrected form 1,corrected form 2" \
  --congelado 5
python "<skill folder>/scripts/line_count.py" "original.pptx" "corrected.pptx"
```

Pass in `--proibido` (forbidden) the excerpts that must no longer exist and in `--esperado` (expected) the corrected forms, otherwise the structural layer has nothing to check against. `--congelado` (frozen) takes the slides the user said not to touch, and any movement in them becomes an error instead of a note.

- **Structural:** no leftover of the wrong forms, all links resolving, each label pointing to the target it announces.
- **Formatting:** run-by-run comparison. Any size, color, bold or italic changed beyond what you intended is collateral damage and must show up here.
- **Visual:** count of rendered lines per changed box, plus pixel difference per slide. This is what catches overflow, which no XML check detects.

Also confirm that the original file kept its size and date.

Reporting "fixed" without having run these three layers is false. The XML accepts changes the screen rejects.

## 7. If something broke, go back and ask

A text fix changes the length of the string, and that can wrap one more line and push content out of the box.

When verification flags a visual or structural change, go back to the chat, say exactly which item caused it, what changed and in which box, and ask whether to keep or revert.

**Do not compensate on your own.** Shrinking the font, enlarging the box or rewriting the sentence to fit are the user's decisions, not yours. Reverting and logging under "not fixed" is usually the right trade when the item is low priority.

## 8. Generate the spreadsheet

First build an `achados.json` (findings) file with the three blocks of rows. The full format, with an example of each field, is in the header of `scripts/error_log.py`; the tabs, columns and reason table are in `references/error-log.md`, to read when building the JSON. In `cor_cabecalho`, give the main color from the client's brand skill, when there is one; without a brand skill, the script uses a neutral gray. Then:

```bash
python "<skill folder>/scripts/error_log.py" --config achados.json \
  --saida "<project outputs folder>/YYYY.MM.DD_Errors found by Claude in v<N>_v1.1.xlsx"
```

The name follows the versioning standard in `CLAUDE.md`: a review redone on the same deck goes up to `_v1.2`, without overwriting the previous one.

Check the output folder numbering in the project's `CLAUDE.md` before running. It is not the same in every project: where there is no templates folder, the whole numbering shifts by one, and what is `06.Outputs` in one project is `05.Outputs` in another.

The script refuses repeated IDs and warns when a reason falls outside the taxonomy, so treat those warnings as your error, not as noise.

The `Fixed` column starts empty and is filled only after verification, never from the intention to fix. The `Standards` tab is the asset that outlives the review: update it with what was established and with the accepted exceptions, so the next review does not raise the same false positives.

## Limitation of the visual layer

The visual layer depends on LibreOffice. Without it the visual check does not run, and that must be stated in the report as a limitation, not left unsaid. Ask the user before installing it, as for any missing tool.
