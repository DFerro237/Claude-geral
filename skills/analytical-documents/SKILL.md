---
name: analytical-documents
description: >-
  Creates, reviews or updates an analytical document in Word (opinion, memo, technical note, due diligence, legal or corporate analysis), with source citations and a list of gaps. Use when the request says "write an opinion on", "write a memo", "technical note in Word", "due diligence report" or "put this in a document". Not for documents that have a format skill of their own (meeting agenda, committee minutes) nor for slides (create-professional-presentations).
---

# Analytical documents

This skill sets the editorial standard for the written document and provides the primitives to build it, in `scripts/doc.py`. From the native `docx` skill, use only the QA and the rendering to images: it builds with docx-js, and here the build is in python-docx, through the primitives.

The target standard is the **analysis document**: someone needs to understand a situation in depth, decide on it, and be able to come back later to check where each statement came from.

## Precedence

The user's explicit request prevails over this skill: length, order, sections, density and format set by the user are to be respected. Treat what follows as a repertoire, not a mold. Evidence, gaps and versioning follow the `CLAUDE.md` ("Direction and evidence" and "Versioning of outputs"); this skill holds only what is specific to the document.

## Document or deck

A document when the reasoning depends on chaining and on literal quotation: exactly what a contract says, a sequence of dated facts, a chain of "if this, then that". A deck when the message stands in independent blocks and there is a meeting. When the request mentions both, do the document first, because that is where the analysis closes, and a deck comes out better from a finished document.

## Prepare

- Identify who will read it, what decision is at stake, and whether the material will circulate or is for internal reading. A document that circulates needs more care with what is confidential.
- Gather the sources before writing and know what each one is: signed document, draft, public record, working spreadsheet, material received from a third party. Finding this out halfway through the writing forces a rewrite.

## Anatomy

Adjust to the case; these are not mandatory sections.

1. **Executive summary**, with the conclusions and what follows from them. Whoever reads only this must come away knowing the answer.
2. **Scope and method**: what was asked, what was examined and what was left out. Stating what was not examined protects the reader from assuming coverage that did not happen.
3. **Facts established**, in an order that helps understanding, usually chronological.
4. **Analysis**, section by section, each with the quotation that supports it.
5. **Risks or points of attention**, with severity and what to do about them.
6. **Gaps**, at the end: what was missing, what would allow a conclusion and where it probably is.
7. **Source appendix**, stating what each document is and its date.

Number the sections. An analytical document is made to be referenced in conversation and in e-mail, and "section 4.2" solves what "that part in the middle" does not.

## Quote and explain

Whenever a conclusion depends on the text of a document, quote the literal passage, say which document it came from and, right below, explain in plain language what it means. Two lines are enough. The reader of the report usually has not opened the contracts and has no obligation to decipher legal, accounting or technical drafting; without the translation, the quotation becomes decoration and the reader starts trusting the conclusion with no way to check it. The `citacao` and `explica` primitives make this pair.

## Write and calibrate

- Simple, direct sentences. Complex analysis does not call for complex writing; it calls for organization.
- One subject per paragraph, with the main statement in the first sentence.
- Numbers always with explicit unit, scale and reference date.
- Bold only for decisive numbers and for terms that guide the reading.
- A table when the data are comparable with each other; running text when the relationship between them is the argument.
- A wide diagram goes in a landscape section, and the document returns to portrait afterwards.
- A two-page technical note and a twenty-five-page opinion are the same craft. In a short document, merge sections, but identifying the source and declaring what was missing do not disappear at any size. If it would fit in an e-mail and the user did not ask for a document, say so instead of producing a file.

## Build

Use the primitives in `scripts/doc.py`: numbered headings, quotation with source and authority, "what this means", table with repeated header, landscape and portrait sections, footer with page number as a field. The script header shows the usage. They already solve the defects that cost time before (blank page, repeated footer, table wider than the page, font swapped in non-Latin text). They are primitives, not a closed template: the anatomy is a decision for each piece of work.

Read `references/docx-construction.md` only if you need to step outside the primitives or open the file in Word through COM.

## Validate

- Run the checker, which measures every table and every image against the usable width of the section they are in. An object that overflows the page is the defect that reading the extracted text never shows.

  ```bash
  python "<this skill's folder>/scripts/doc.py" --verificar "path/to/document.docx"
  ```

- Run the native `docx` validator (`python scripts/office/validate.py document.docx`). It flags much of what makes Word ask for repair on opening, a defect that rendering through LibreOffice does not show.
- Render through the native `docx` path (PDF and `pdftoppm`) and look at the pages: expected count, no blank page between sections, footer without repetition. When export is not available, say that the visual inspection was not done and what replaced it.
- Go through the conclusions and confirm that each one has a quotation or an identified source behind it. In non-trivial analysis, call the `fact-checker` agent, which does this with fresh context.
