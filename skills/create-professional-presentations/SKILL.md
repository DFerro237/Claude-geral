---
name: create-professional-presentations
description: Create, review or edit professional presentations in consulting-report style (substantial, structured text, action titles, sourced exhibits) in PowerPoint or Google Slides, for any client, with an analytical and finance focus. Trigger for any deliverable whose output is slides: corporate, strategy, committee or board decks, sales decks, results decks, industry and market analyses, valuation or investment thesis presented as slides, investment materials, one-pagers, and reviews of this kind of material, including when the request only says "slides", "deck", "presentation", "committee" or "board". It is the universal conventions layer over the built-in `pptx` skill and still applies alongside the more specific executive summary and client brand skills. When the deliverable is a spreadsheet or an Excel model, the skill is `professional-spreadsheets`.
---

# Professional presentations (consulting style)

This skill defines the editorial and reasoning standard for presentations. Tools, file generation and technical QA live in the built-in `pptx` skill. Load both: this one for *what* to say and how to structure it, `pptx` for *how to build* the `.pptx` and validate it.

The target standard is the **consulting report**: slides that support a decision and stand on their own, with substantial, structured text, not a minimalist deck of loose words. Density is not a defect here; disorganization is. Each slide carries a complete argument, not just a topic.

## Precedence

The user's explicit request prevails over this skill: the number of slides, order, font, content, density and layout the user defines are to be respected. A plan drafted by the agent does not silently revoke an earlier instruction. Treat the guidance below as a repertoire of quality, not a mold.

## Prepare

- Identify the audience, purpose, expected decision or understanding, central message and distribution format (live committee, board, sent by email, working document for internal reading).
- Material for internal reading is a register of its own: nobody will present it, so density and completeness matter more than polish, and investing time in design is investing in the wrong place. What does **not** loosen is source discipline, because an internal document often becomes the basis for a decision later.
- Consult the project's applicable context files, sources and folder READMEs, if the project has them, before writing.
- When editing, inspect the whole deck and treat it as the main reference for language, hierarchy, typography, palette, grid and fixed elements. Use `markitdown` and the thumbnails described in the `pptx` skill to map what already exists.
- Consult templates only when applicable; use them as a reference for form, never as a factual source.
- Preserve the base file and generate a new version at the defined destination, unless instructed otherwise.

## Build the reasoning (pyramid)

What separates a consulting deck from a pile of slides is logic, not aesthetics.

- Formulate the **governing idea**: "By the end, [audience] should [decide/understand/do] because [central message]". The whole deck serves it.
- Give each slide **an action title**, a sentence that states the slide's conclusion, not its subject. Prefer "Margin falls 3 pp in 2025, driven by raw material costs" over "Margin analysis". The reader should understand the story by reading only the titles, in sequence (the "horizontal storyline").
- Within the slide, support the title with evidence grouped in a MECE way (no overlap, no gap): 2 to 4 blocks, each with a clear function (context, cause, implication, action).
- Choose the deck's sequence to fit the case: situation → complication → question → answer; context → alternatives → recommendation → decision; or conclusion → evidence → implications → next steps.
- Do not force a recommendation in informational material, and do not create artificial alternatives to fill space.

## Write to the consulting standard

- Substantial text is welcome, as long as it is structured. Prefer complete sentences and claims backed by a source or a rationale over telegraphic fragments, because the slide has to defend itself when it is sent without a presenter.
- Each bullet or block must say something and end with the "so what?": fact plus implication, not just the data point.
- Build a hierarchy: action title; if useful, a one-line kicker or subtitle; structured body; and always the source of the data in the footer of the slide or of the exhibit.
- Reduce redundancy between title, subtitle and body. Repeating the same sentence at three levels is noise, not emphasis.
- Bold only decisive numbers and terms that guide the reading; bold on everything highlights nothing.
- Before shrinking the font to make things fit, reorganize, group or split into another slide. Body text below about 12pt usually means the slide needs to be split.

## Exhibits and finance

- Every relevant quantitative data point becomes an exhibit (table, chart or callout), not running text. Each exhibit has its own title that states the reading ("Revenue grows 18% a year, driven by new customers") and its source.
- Choose the chart by the message: bars for comparison, line for trend, waterfall for bridges (revenue, margin, valuation), table for precision and sensitivity, stacked for composition. Keep charts native and clean, as described in the `pptx` skill.
- In financial content, make currency, unit and scale explicit (for example USD thousand, USD million, %, or the equivalent in the deliverable's currency); put negatives in parentheses; keep decimal places consistent; and use labels that make the period and the base clear. Follow the typographic conventions of the deliverable's language for foreign terms: when the deliverable is not in English (a Portuguese deck, for example), set English or Latin terms in italics (*runway*, *churn*, *breakeven*, *pro rata*), keep acronyms (EBITDA, CAPEX, LTM) and proper nouns in roman, and keep in roman words already naturalized in that language's financial vocabulary, such as tranche in Portuguese. When in doubt, choose one form and repeat it throughout the deck.
- A big-number callout (KPI) communicates more than a sentence for anchor metrics; use it with a short label below.
- Diagrams, corporate structure charts, process flows and timelines follow a rule that charts do not have: **a single reading direction**. Choose the direction (top to bottom, or left to right) and keep every connector in it. A connector that goes back forces the reader to retrace the path, and it is the defect that most destroys the legibility of this kind of exhibit. When a relationship seems to require going back, the hierarchy is usually built the wrong way round. One box per entity, and the value of the relationship (percentage, term, volume) written on the connector itself, not floating in space.

## Design

- Apply the design principles and the "avoid" list of the built-in `pptx` skill (palette with a dominant color, consistent visual motif, contrast, safe fonts, margins). They apply here. The difference is that a consulting slide accommodates more text per unit.
- Work with a grid, clear alignments, consistent margins and an unambiguous reading sequence (usually top→bottom, left→right).
- Standardize colors: one tone per function (text, title, rule line, card background), reused; do not introduce close variants of a color already in use. If the project has an official template, take the exact values from it.
- One dominant exhibit or focus per slide, unless the message is a balanced comparison.
- Cards, bands and frames only when they separate distinct dimensions, not as decoration. Avoid the AI "tells": lines under titles, accent bands or stripes, too many badges.
- Icons and images only when they carry information. Preserve the deck's logos, footers, numbering and valid placeholders.

## Preserve editability and scope

- Keep text, shapes, tables and charts editable; do not rasterize slides to fake visual consistency.
- Change only the slides and objects in scope. Do not copy facts, dates or assumptions from templates.

## Validate

- Confirm every explicit requirement (number of slides, order, composition).
- Run the geometric check first: `python "<this skill's folder>/scripts/check.py" "path/to/deck.pptx"`. It compares the boxes of every object and flags overlaps and elements outside the margin in seconds, with a precision the eye does not have. Running it first saves the visual inspection of slides that are still going to change.
- Run the `pptx` skill's QA: `markitdown` for content, the file validator, and conversion to images for visual inspection of every changed slide at full size (overflow, alignment, contrast, footers). Visual inspection is still necessary, because it sees what geometry does not: text overflowing inside its own box, poor contrast, confusing hierarchy.
- Title reading test: read in sequence, the action titles tell the story on their own.
- Standalone reading test: when sent without an oral presentation, the slide explains itself.
- Compare with the base file and confirm there are no changes outside the scope. Remove leftovers and iterate until narrative, data and execution are consistent.
