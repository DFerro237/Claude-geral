---
name: professional-spreadsheets
description: >-
  Creates, updates, reviews or audits a spreadsheet or financial model (valuation, DCF, projection, cash flow, cap table, budget), preserving formulas, traceability, formatting and checks. Use when the request says "build a model", "review this spreadsheet", "do the valuation in Excel", "update the cap table" or "check the formulas". Not for spreadsheets that have an update routine of their own (see that skill) nor for slides (create-professional-presentations).
---

# Professional spreadsheets

A layer of conventions over the native `xlsx` skill, which provides the tools, recalculation (`recalc.py`) and the formula error check. Precedence, versioning and evidence follow the `CLAUDE.md`; the current workbook and the applicable template come before this skill.

## Prepare

- Identify the base file, sources, destination and elements that must not be changed.
- When editing, inspect values, formulas, objects and rendering before modifying, and preserve existing formulas, formatting, validations, connections, protections, charts and structures.
- Run a short test on a copy when the structural change carries high risk.

## Preserve logic and references

- Insert whole rows or columns inside the structure when that preserves references and adjacent blocks.
- Do not change closed historical periods without authorization and a source.
- Compare the logic of at least two equivalent periods or blocks before replicating formulas.
- Use cell references instead of repeating values or putting magic numbers in formulas, with assumptions and inputs in identified cells.
- Use absolute, relative and mixed references appropriately.
- Prefer simple, auditable formulas; use helper cells for complex calculations.
- Avoid circular references, volatile functions and external links without need; when unavoidable and authorized, preserve traceability.
- Use English function names and preserve the syntax adopted by the file.
- Use error handling only for expected situations, never to hide inconsistencies.

## Handle sources and inputs

- Confirm currency, unit, scale, sign, period and nature of the data before filling in.
- When there is no reliable data, leave the cell empty; use zero only when the source or the logic indicates zero.
- Record an external source when it is not clear and is material.
- In material divergences, present the values, sources and implication before choosing.

Colors, when the workbook has no established convention. This is this skill's convention and it prevails over that of the native `xlsx`, which uses green for links between sheets and red for links to another file:

- black: formulas and internal references;
- blue: manual inputs and values from external sources;
- green: formulas with authorized external links;
- red: checks, exceptions and errors.

## Format

- Preserve the existing standard. Apply defaults only to new cells with no comparable reference.
- Store numbers, percentages, currencies and dates as typed values, not strings.
- Use invariant format codes, such as `#,##0`, `#,##0.00`, `0.0%` and `0.00%`.
- Show negatives in parentheses in financial tables when compatible with the file, and zeros as `-` when that improves reading.
- Avoid merged cells in data bases, calculations, filters and tables.
- Use titles, units and labels that make the workbook self-explanatory, without excess colors, borders and conditional formatting.

## Create checks and audit

- Audit only the impacted areas and relevant dependencies, unless a full audit is requested.
- Check references, totals, consistency across periods, unit, scale, currency and sign.
- Create checks in financial models, reconciliations and changes that affect relevant totals: discreet, complete, in italics and red.
- Expect a zero result. When appropriate, use `ROUND(<check>,3)` to neutralize precision noise, without hiding divergences.
- Do not treat missing data as a passed check.
- Validate ranges, series, labels and axes of impacted charts.

## Validate

- For reading questions, do not modify or export the workbook.
- Recalculate and check formula errors through `xlsx`; render and visually review the impacted sheets (clipping, inappropriate breaks, broken objects, changes outside the scope).
- Export only the requested final version and report material limitations.
