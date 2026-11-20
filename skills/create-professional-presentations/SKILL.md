---
name: create-professional-presentations
description: >-
  Creates, reviews or edits a deck in the consulting-report style (action titles, structured text, exhibits with sources), with a finance bias, for any client. Use when the request says "build a deck", "make the slides", "board presentation", "one-pager", "review the argument of this deck" or "turn this analysis into a presentation", even without the word PowerPoint. Works together with the native pptx skill, which builds and validates the file. A process deck that has a skill of its own (committee, report) uses both. Not for minutes nor for the fine-tooth pass on standards and typos (review-presentations).
---

# Professional presentations (consulting style)

This skill sets the editorial and reasoning standard for presentations. The tools, file generation and technical QA live in the native `pptx` skill. Load both: this one for *what* to say and how to structure it, `pptx` for *how to build* the `.pptx` and validate it. The executive summary has its own layer (`create-executive-summary`), and the client's brand comes from the client's brand skill, when there is one.

The target standard is the **consulting report**: slides that support a decision and work on their own, with substantial, structured text, not a minimalist deck of loose words. Density is not a defect here; disorganization is.

## Precedence

The user's explicit request prevails over this skill: number of slides, order, font, content, density and layout set by the user are to be respected. General precedence and versioning follow the `CLAUDE.md`.

## Prepare

- Identify the audience, purpose, expected decision or understanding, central message and form of distribution (live committee, board, sent by e-mail, working document for internal reading).
- Material for internal reading is a register of its own: nobody will present it, so density and completeness matter more than finish. What does **not** loosen is source discipline, because an internal document often becomes the basis for a decision later.
- When editing, inspect the whole deck and treat it as the main reference for language, hierarchy, typography, palette, grid and fixed elements. Use `scripts/slide_text.py` (text per slide) and `scripts/thumbnail.py` (thumbnail grid) from the `pptx` skill to map what already exists.
- Check the project's applicable context files, sources and READMEs before writing.
- Templates are a reference for form, never a factual source.

## Build the reasoning (pyramid)

- Formulate the **governing idea**: "In the end, [audience] should [decide/understand/do] because [central message]". The whole deck serves it.
- Give each slide **an action title**, a sentence that states the slide's conclusion, not its subject. Prefer "Margin falls 3 p.p. in 2025, driven by fiber cost" to "Margin analysis". Read in sequence, the titles tell the story.
- Inside the slide, support the title with evidence grouped in a MECE way: 2 to 4 blocks, each with a clear role (context, cause, implication, action).
- Choose the sequence of the deck according to the case: situation → complication → question → answer; context → alternatives → recommendation → decision; or conclusion → evidence → implications → next steps.
- Do not force a recommendation into informational material, nor create artificial alternatives to fill space.

## Write to the consulting standard

- Prefer full sentences and source-backed statements to telegraphic fragments, because the slide must defend itself when sent without a presenter.
- Each bullet or block ends in the "so what?": fact and implication, not just the data point.
- Hierarchy: action title; if useful, a one-line subtitle; structured body; and always the source of the data in the footer of the slide or the exhibit. Do not repeat the same sentence in title, subtitle and body.
- Bold only for decisive numbers and for terms that guide the reading.
- Before shrinking the font to make it fit, reorganize, group or break into another slide. Body text below ~12 pt usually means the slide needs splitting.

## Exhibits and finance

- Every relevant quantitative data point becomes an exhibit (table, chart or callout), not running text. Each exhibit has its own title stating the reading, and the source.
- Choose the chart by the message: bars for comparison, line for trend, waterfall for bridges (revenue, margin, valuation), table for precision and sensitivity, stacked for composition. Keep charts native and editable.
- In financial content, take care with explicit currency, unit and scale ($ thousand, $ mm, %); negatives in parentheses; consistent decimal places; and labels that make the period and the base clear. Follow the deck's language for typography of foreign terms: for example, a deck written in another language may set English or Latin terms in italics (*runway*, *churn*, *breakeven*, *pro rata*) while keeping acronyms (EBITDA, CAPEX, LTM) and proper names upright, and leave upright the words already naturalized in that language's financial usage. When in doubt, choose one form and repeat it across the whole deck.
- For anchor metrics, a large-number callout (KPI) with a short label communicates more than a sentence.
- Diagrams, corporate org charts, process flows and timelines obey a rule that charts do not have: **a single reading direction**. Choose the direction (top to bottom, or left to right) and keep all connectors in it. A connector that goes back forces the reader to retrace the path and is the defect that most destroys the legibility of this kind of exhibit. When a relationship seems to require going back, usually the hierarchy is built upside down. One box per entity, and the value of the relationship (percentage, term, volume) written on the connector itself, not floating in space.

## Design

From the `pptx` "Avoid" list, the finishing items apply: title in the same position across slides of the same type, uniform chart labels, contrast, text that does not overflow, no line under the title and no decorative band. What does not apply is the requirement of a visual element on every slide, the rule against text-only slides, and the "bold" palette chosen by theme: the consulting slide accommodates more text per unit, and color comes from the current deck or the brand skill. Font sizes also come from the current deck or the brand skill, not from the `pptx` typography table. Add:

- One tone per function (text, title, rule, card background), reused, with no variant close to a color already in use. When there is an official template, take the exact values from it.
- One dominant exhibit or focus per slide, except when the message is a balanced comparison.
- Cards, bands and frames only when they separate distinct dimensions, not as decoration.
- Icons and images only with an informative function.
- Preserve logos, footers, numbering and valid placeholders of the deck. Keep text, shapes, tables and charts editable; do not rasterize slides to fake visual compliance.
- Change only the slides and objects in scope. Do not copy facts, dates or assumptions from templates.

## Validate

- Confirm all explicit requirements (quantity, order, composition).
- Run the geometric check first: `python "<this skill's folder>/scripts/check.py" "path/to/deck.pptx"`. It flags overlap and elements outside the margin in seconds, and running it first saves the visual inspection of slides that will still change. Options: `--margem` (required margin in inches), `--com-imagens` (include images), `--slides 3,7,12-15`.
- Run the `pptx` QA: `scripts/slide_text.py` for content, `scripts/office/validate.py` for the file, and conversion to images to inspect every changed slide at full size. Visual inspection is still necessary, because it sees what geometry does not: text overflowing inside its own box, poor contrast, confusing hierarchy.
- Title-reading and standalone-reading test: the action titles tell the story on their own, and the slide explains itself without an oral presentation.
- Compare with the base file and confirm there are no changes outside the scope.
