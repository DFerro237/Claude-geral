---
name: professional-spreadsheets
description: Create, update, review or audit professional spreadsheets and standalone financial models: valuation, DCF, projections, cash flow, cap table, unit economics, budget, portfolio tracking, scoring matrices, preserving structure, formulas, traceability, formatting, checks and readability. Trigger whenever the deliverable is a spreadsheet or model in a .xlsx, .xlsm, .xls, .csv or .tsv file, for any client, including when the request only mentions "spreadsheet", "workbook", "model", "sheet", "tab", "formula", valuation, cap table or "the Excel file". When the same subject has to become slides, the skill is `create-professional-presentations`. It is the conventions layer over the built-in xlsx skill; for a live Microsoft Excel session, use Claude in Excel (live control of the workbook).
---

# Professional spreadsheets

## Apply the base guidance

- Load and apply Claude's built-in spreadsheet skill (`xlsx`).
- Give priority over this skill to instructions explicitly written by the user, to the current workbook and to the applicable template.
- Do not let a plan or a default silently replace the requested scope.
- Use this skill as a conventions layer; follow the general skill for tools, implementation, rendering and export.

## Prepare

- Identify the base file, sources, destination and the elements that must not be changed.
- When editing, inspect values, formulas, objects and rendering before modifying anything.
- Preserve existing formulas, formatting, validations, connections, protections, charts and structures.
- Work on a new version, unless explicitly instructed to edit the file itself.
- Run a short test on a copy when a structural change carries high risk.

## Preserve logic and references

- Insert whole rows or columns inside the structure when that preserves references and adjacent blocks.
- Do not change closed historical periods without authorization and a source.
- Compare the logic of at least two equivalent periods or blocks before replicating formulas.
- Use cell references instead of repeating values or putting magic numbers in formulas.
- Keep assumptions and inputs in labeled cells.
- Use absolute, relative and mixed references appropriately.
- Prefer simple, auditable formulas; use helper cells for complex calculations.
- Avoid circular references, volatile functions and external links unless they are necessary.
- Use English function names, not localized ones, and preserve the syntax the file already uses.
- Use error handling only for expected situations, never to hide inconsistencies.

## Handle sources and inputs

- Confirm currency, unit, scale, sign, period and the nature of the data before filling anything in.
- Record the external source when it is not clear and it is material.
- When there is no reliable data, leave the cell empty; use zero only when the source or the logic indicates zero.
- When there are material discrepancies, present the values, sources and implication before choosing.
- Avoid external links; when they are unavoidable and authorized, preserve traceability.

As a fallback when the workbook has no established convention:

- black: formulas and internal references;
- blue: manual inputs and values from external sources;
- green: formulas with authorized external links;
- red: checks, exceptions and errors.

## Format

- Preserve the existing pattern. Apply defaults only to new cells with no comparable reference.
- Store numbers, percentages, currencies and dates as typed values, not strings.
- Use invariant format codes, such as `#,##0`, `#,##0.00`, `0.0%` and `0.00%`.
- Show negatives in parentheses in financial tables when compatible with the file.
- Show zeros as `-` when that convention improves readability.
- Avoid merged cells in raw data, calculations, filters and tables.
- Use titles, units and labels that make the workbook self-explanatory.
- Avoid excessive colors, borders and conditional formatting.

## Create checks and audit

- Audit only the impacted areas and relevant dependencies, unless a full audit is requested.
- Check formula errors, references, totals, consistency across periods, unit, scale, currency and sign.
- Create checks in financial models, reconciliations and changes that affect relevant totals.
- Keep checks discreet, complete, in italics and in red.
- Expect a result of zero. When appropriate, use `ROUND(<check>,3)` to neutralize precision noise, without hiding discrepancies.
- Do not treat missing data as a passed check.
- Validate the ranges, series, labels and axes of impacted charts.

## Validate

- For questions that only require reading, do not modify or export the workbook.
- Inspect the values and formulas of the impacted areas.
- Check for errors such as `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` and `#N/A`.
- Recalculate in a compatible environment when the tool does not update results automatically.
- Render and visually review every impacted sheet.
- Confirm there is no clipping, improper line breaks, broken objects or changes outside the scope.
- Export only the final version requested and report material limitations.
