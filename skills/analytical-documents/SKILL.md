---
name: analytical-documents
description: Create, review, or update an analytical document in Word, such as an opinion, memo, technical note, analysis report, due diligence report, legal or corporate analysis, or an internal position paper on a topic. Trigger whenever the deliverable is a .docx or .doc file, and also when the request says "in Word", "document", "written report", "opinion", "memo", "technical note", "written analysis", or "put this in a document" or "write this up", even without naming the format. Trigger also when the same work will also become a presentation, because document and deck coexist in the same task and the usual order is document first, deck second. Works for any client and is the conventions layer on top of the built-in `docx` skill, which remains responsible for the tooling and the file QA. When the deliverable is slides, the skill is `create-professional-presentations`; when it is a spreadsheet, `professional-spreadsheets`.
---

# Analytical documents

This skill defines the editorial standard for the written document. The tooling and the file QA live in the built-in `docx` skill. Load both: this one for what to say and how to organize it, `docx` for how to build the `.docx`.

The target standard is the **analysis document**: someone needs to understand a situation in depth, make a decision about it, and be able to come back later to check where each statement came from. That is different from a deck, which supports a conversation, and different from a summary, which does without the proof.

## Precedence

The user's explicit request prevails over this skill: the length, order, sections, density, and format they define are to be respected. Treat what follows as a repertoire, not a mold. The general rules of evidence also apply here without being repeated: no factual claim without a source you actually consulted, state the authority of a source when it changes the reading, and declare gaps instead of filling them by inference (your CLAUDE.md may define these rules in more detail).

## When it is a document and not a deck

Choose the document when the reasoning needs chaining and literal quotation: the conclusion depends on exactly what a contract says, on a sequence of dated facts, on a chain of "if this, then that". Slides cut that kind of reasoning into pieces that do not stand on their own.

Choose the deck when the message can be defended in independent blocks, when there is a meeting, or when the audience will read it in minutes.

Both together is a common combination and not redundancy: the document carries the proof, the deck carries the decision. When the request mentions both, do the document first. That is where the analysis comes together, and a deck comes out much better from a finished document than the other way around.

## Prepare

- Identify who will read it, what decision is at stake, and whether the material will circulate or is for internal reading. An internal working document accepts more density and more supporting apparatus; a document that circulates needs more care with what is confidential.
- Gather the sources before writing and know what each one is: signed document, draft, public record, working spreadsheet, material received from a third party. Finding this out in the middle of drafting means rewriting.
- If there is a base file, preserve it and save the result as a new version instead of overwriting it, following the versioning convention in your CLAUDE.md, if it defines one.

## Anatomy

Adjust to the case; these are not mandatory sections.

1. **Executive summary**, with the conclusions and what follows from them. Someone who reads only this must come away knowing the answer.
2. **Scope and method**: what was asked, what was examined, and what was left out. Stating what was not examined protects the reader from assuming coverage that did not happen.
3. **Established facts**, in an order that helps understanding, usually chronological.
4. **Analysis**, section by section, each with the quotation that supports it.
5. **Risks or points of attention**, with severity and what to do about them.
6. **Gaps**, at the end: what was missing and what it would have been used for. See below.
7. **Source appendix**, stating what each document is and its date.

Number the sections. An analytical document is made to be referenced in conversation and in email, and "section 4.2" settles what "that part in the middle" does not.

## Quote and explain

Whenever a conclusion depends on the text of a document, quote the literal excerpt and, right below it, explain in plain language what that excerpt means. Two lines are enough.

This is not redundancy. Whoever reads the report usually has not opened the contracts and has no obligation to decipher legal, accounting, or technical wording. Without the translation, the quotation becomes decoration: the reader skips it and starts trusting your conclusion with no way to check it, which is exactly what the document should prevent.

Always identify which document the excerpt came from, and say what that document is when that changes the weight of the quotation. An unsigned draft binds no one, and an analysis that treats it as a signed contract reaches the wrong conclusion with the appearance of rigor.

## Gaps

End with the list of what was missing. For each item, say what was missing, what it would allow you to conclude, and where it probably is.

A declared gap is a deliverable, not an excuse: it is what turns "I don't know" into a list of next steps. The opposite, filling the void with a plausible inference, produces an error that nobody finds later, because the inference looks like the rest of the text.

## Write

- Simple, direct sentences. Complex analysis does not call for complex writing; it calls for organization.
- One subject per paragraph, with the main statement in the first sentence.
- Numbers always with explicit unit, scale, and reference date.
- Bold only for decisive numbers and for terms that guide the reading.
- A table when the data are comparable to one another; running text when the relationship between them is the argument.
- When there is a wide diagram, use a landscape page and return to portrait afterward.

## Calibrate the length

A two-page technical note and a twenty-five-page opinion are the same craft at different scales. What changes is the depth of the proof, not the standard.

In a short document, merge sections: the summary and the facts become a single block, and the gaps become a paragraph. What cannot disappear, at any length, is the identification of the source and the statement of what was missing. If it would fit in an email and the user did not ask for a document, say so instead of producing a file just to add bulk.

## Build

The `python-docx` mechanics are in `references/docx-construction.md`. Read it when you generate the file, not before: it covers plumbing details (footer, page break, landscape section, usable width) that only matter at that point.

The ready-made primitives are in `scripts/doc.py`: headings, quotation with source and authority, "what this means", table with a repeated header, landscape section, footer with page numbering. They are primitives, not a closed template, because the anatomy is a decision for each piece of work. Use them so you do not rewrite the plumbing or repeat bugs that are already solved.

```bash
python "<this skill's folder>/scripts/doc.py" --verify "path/to/document.docx"
```

## Validate

- Open the file in Word and confirm that it does not ask for repair and that the page count is the expected one.
- Run the verifier above: it measures every table and every image against the usable width of the section they are in. An object that overflows the page is the defect that reading the extracted text never shows.
- Check the footer: correct text, no repetition between sections, page numbering as a field and not as a typed number.
- Check that there is no blank page between sections.
- Go through the conclusions and confirm that each one has a quotation or an identified source behind it. In a non-trivial analysis, invoke the `fact-checker` agent, which does this with fresh context.
- When PDF export is available, look at the pages. When it is not, and that does happen, say that the visual inspection was not done and what replaced it, instead of leaving it implied that it was done.
