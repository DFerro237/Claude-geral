---
name: review-presentations
description: Review the consistency and standardization of a finished PowerPoint presentation, checking term usage, fonts, italics, title, subtitle and footer positions, typos, grammar and link integrity, and delivering an error log as a spreadsheet. Trigger whenever the request is to check, review or audit an existing deck for standards, formatting, consistency, typos, off-standard fonts, misalignment between slides or broken links, including when it only says "review this deck's formatting", "check the formatting", "go over it with a fine-tooth comb", "proofread the deck" or "see if everything is consistent". Confirms every finding with the user before changing anything. Not for creating or restructuring content: reviewing the argument, narrative and choice of exhibits is `create-professional-presentations`.
---

# Presentation review

Checking a finished deck, when the content has already been decided and what is at stake is the finish: the same thing written two ways, a font that slipped through, a title 2 pt out of place, a link that leads nowhere.

This matters because finishing errors have a disproportionate cost. Nobody questions the thesis because of an `Estimated tiem`, but everybody notices, and attention leaves the argument.

Also load the built-in `pptx` skill for the file tooling, and the client's brand skill when there is one, because the official palette and typography come from it.

## The principle behind everything

**You do not decide what is right. You find divergences and bring them to the user.**

A deck may diverge from the template on purpose, and a slide may be frozen by an earlier decision. That is why this skill never fixes anything directly: it identifies, presents a table, and waits for confirmation. The cost of asking is one message. The cost of "fixing" what was intentional is redoing approved work.

## 1. Confirm the scope before opening the file

Ask which dimensions to review. Do not start without that, because sweeping everything in a large deck produces a long, expensive list, and much of it may not matter.

Available dimensions, with the ID prefix of each:

| ID | Dimension | What it checks |
|---|---|---|
| `G` | Spelling and typing | Typos, diacritics, agreement, multiple spaces (including after punctuation and non-breaking spaces), line-break hyphen stuck to the word |
| `N` | Naming and terms | One spelling per term, a single date format, standardized appendix references |
| `F` | Fonts | A single typeface, including inside tables |
| `I` | Italics | Foreign-language terms in italics (for example, English terms in a Portuguese deck), acronyms and proper nouns in roman |
| `A` | Alignment and grid | Title, subtitle and footer at the same coordinate within a block |
| `R` | Footers and references | Source line and numbered notes aligned |
| `L` | Links | Link resolves, label matches the target, appendix has a way back |
| `U` | Numbers and units | Currency spacing, plurals, the same number matching across slides |
| `C` | Colors | One shade per function, no near-variant of a color already in use |
| `E` | Exhibits | Title, source and axis labels present and consistent |
| `H` | File hygiene | Empty slide, orphan shape, editing leftovers |

Also ask whether any slide is frozen, that is, whether some part must not be touched. If so, respect it absolutely: no alignment, no size, no position.

## 2. Fix the reference for judgment

Before calling anything an error, define what you are comparing against.

**Look for a previous review spreadsheet in the project**, usually in the sources folder (`04.Materials_and_Sources` in the project template). Its "Standards" sheet records the canonical form already agreed. Treat it as an established norm and do not reopen the discussion: if it says `tranche` stays in roman, do not propose italics.

**Without a previous spreadsheet, derive it from the deck itself.** Establish the dominant pattern, not the template's, because the current file prevails over the template. Establish it **per block**: content slides and appendices often have a different grid, and that is structure, not error. The cover and section dividers almost always leave the grid by design.

When the deck's dominant pattern differs from a previously recorded standard, report the divergence instead of choosing on your own which one applies.

## 3. Inspect

The scripts live in this skill's folder, not in the project's. Call them by full path:

```bash
python "<skill folder>/scripts/inspect_deck.py" "path/to/deck.pptx"
```

It returns the full inventory: text by paragraph, font per run, italics, position, size and autofit mode of each shape, hyperlinks with resolved targets, and the automatic checks for currency, dates and spelling variants. The output comes in sections marked with the dimension prefix, so read only the ones in the confirmed scope. Use `--text` when you need the full text for the spelling and grammar review.

The italics term list and the currency and plural checks in `inspect_deck.py` are tuned for Portuguese-language decks. For a deck in another language, adjust the lists at the top of the script before trusting that section.

Read the result with suspicion. Before recording any finding, read `references/pitfalls.md`, which lists false positives that have already cost rework, such as Arial that is the bullet font and not the text font, and superscript that exists as an attribute and not as a character.

## 4. Present in the chat and stop

Build one table per category, in the chat, with these columns:

```
ID | Slide | Current | Should be | Recommendation
```

`Recommendation` is **fix**, **question** or **do not fix**, and it is your reading, not the decision. Use question when both forms are defensible and the choice is one of style, not of correctness.

Quote the literal text in "Current". The user needs to recognize their own text to judge quickly.

**Do not change anything until confirmation.** If the user asks to fix only part, or reclassifies an item, that is what applies.

When the explanation of a finding does not fit in the table row, offer to detail it instead of stuffing the cell. A structural divergence, such as two subtitle formats between blocks, almost always needs its own paragraph.

### Multiple spaces get their own treatment

A run of two or more spaces is not always a typo. It may be deliberate alignment: a pseudo-column inside a text box, a block of spaces in place of a line break, a manual indent. Fixing those dismantles a layout someone built on purpose.

That is why `inspect_deck.py` returns dimension `G` in two lists, and each goes into the table differently:

| Script list | Recommendation in the table | What to do |
|---|---|---|
| Likely typo | fix | Same as any other error |
| Possibly deliberate formatting | question | Show the whole paragraph and the neighboring lines of the same shape in the chat, and **ask** |

Never fix an item from the second list without an answer. An excerpt does not work here: the alignment between lines is what reveals the pseudo-column, and it only shows with whole paragraphs, one under the other.

If the user confirms it is deliberate, the item goes to the "Not fixed" sheet with reason `User decision`, and the pattern goes to the "Standards" sheet, so the next review does not raise it again.

## 5. Apply what was approved

Work on a copy in the outputs destination, preserving the base file, unless told to edit the file itself.

Use the helpers in `scripts/edit.py`. They exist because PowerPoint text lives fragmented in runs, and `foodservice` may be split into `food` and `service`. A direct replacement in the XML fails in these cases and destroys formatting.

Order from least to most invasive: text, italics, position, links. That way, if something breaks, the last step applied is the suspect.

## 6. Verify in three layers

```bash
python "<skill folder>/scripts/verify.py" "original.pptx" "corrected.pptx" \
  --forbidden "wrong text 1,wrong text 2" \
  --expected "corrected form 1,corrected form 2" \
  --frozen 5
python "<skill folder>/scripts/line_count.py" "original.pptx" "corrected.pptx"
```

Pass in `--forbidden` the pieces of text that must no longer exist and in `--expected` the corrected forms, otherwise the structural layer has nothing to check against. `--frozen` takes the slides the user said not to touch, and any movement on them becomes an error instead of an observation.

- **Structural:** no leftovers of the wrong forms, every link resolving, each label pointing to the target it announces.
- **Formatting:** run-by-run comparison. Any size, color, bold or italic changed beyond what you intended is collateral damage and has to show up here.
- **Visual:** count of rendered lines per changed box, plus pixel difference per slide. This is what catches overflow, which no XML check detects.

Also confirm that the original file kept its size and date.

Reporting "fixed" without having run these three layers is false. The XML accepts changes the screen rejects.

## 7. If something broke, go back and ask

A text correction changes the length of the string, and that may break one more line and push content out of the box. It has really happened: two extra characters were enough.

When the verification reports a visual or structural change, go back to the chat, say exactly which item caused it, what changed and in which box, and ask whether to keep or revert.

**Do not compensate on your own.** Shrinking the font, enlarging the box or rewriting the sentence to fit are the user's decisions, not yours. Reverting and recording it under "not fixed" is usually the right trade when the item is low priority.

## 8. Build the spreadsheet

First assemble a `findings.json` file with the three blocks of rows. The full format, with an example of each field, is in the header of `scripts/error_log.py`. In `header_color`, give the main color of the client's brand skill, when there is one, so the spreadsheet comes out in the client's identity; without a brand skill, the script uses a neutral gray. Then:

```bash
python "<skill folder>/scripts/error_log.py" --config findings.json \
  --output "<project outputs folder>/YYYY.MM.DD_Review findings V<N>.xlsx"
```

Check the outputs folder in the project's `CLAUDE.md`, if it defines one, before running. Folder numbering is not the same in every project: where there is no templates folder, the whole numbering shifts by one, and what is `06.Outputs` in one project is `05.Outputs` in another.

The script refuses repeated IDs and warns when a reason falls outside the taxonomy, so treat those warnings as your own error, not as noise.

Three sheets:

| Sheet | Columns |
|---|---|
| `Errors V<N>` | ID, Slide, Category, Item, Current, Should be, Priority, Fixed, Note |
| `Not fixed` | ID, Slide, Category, Item, Priority, Reason, Detail |
| `Standards` | Dimension, Element, Standard, Note |

`Fixed` records the version in which the fix went in, such as `Yes (V15_Claude review)`. It starts empty and is only filled after the verification, never on the intention to fix.

`Reason`, in the not fixed sheet, translates what happened to the item after the conversation in step 4:

| Situation | Reason |
|---|---|
| Marked as question and not resolved | Open question |
| User said not to fix | User decision |
| Fixed, but reverted for breaking the layout | Breaks layout/design |
| Investigated and was not an error | Not an error (reclassified) |
| Depends on information nobody has yet | Pending decision |
| Fix possible, but with disproportionate risk | High risk / low benefit |

The `Standards` sheet is the asset that outlives the review. Update it with what was established and with the accepted exceptions, including reclassifications, so the next review does not raise the same false positives.

## Dependencies

`python-pptx`, `openpyxl`, `pypdfium2`, `pdfplumber` and `Pillow`, plus LibreOffice for the visual layer. Check them before starting. If something is missing, ask the user for permission before installing it.

Without LibreOffice the visual check does not run, and that has to be stated in the report as a limitation, not left unsaid.
