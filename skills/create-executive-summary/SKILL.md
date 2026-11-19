---
name: create-executive-summary
description: >-
  Creates or reviews the executive summary slide in consulting style: a self-sufficient synthesis of context, conclusions, recommendation and decision, with a finance bias. Use when the request says "make the executive summary", "executive summary of the deck", "opening slide that sums it all up" or "synthesis for the board". Loads create-professional-presentations; the brand comes from the client's brand skill, when there is one.
---

# Executive summary

A specialization of `create-professional-presentations` for the synthesis slide. Load it first, and `pptx` for building and QA: pyramid, action titles, writing, exhibits, finance and design are there. This skill adds only what is specific to the executive summary.

The summary is the slide an executive reads if they read only one. It condenses the whole story of the deck: where we are, what changes, what that implies and what is being decided, in a way that stands on its own, without a presenter.

## What is specific to the summary

- **Calibrated density:** it is the densest slide of the deck by definition, but still organized in blocks with a clear role. Synthesizing is not listing everything; it is choosing what is indispensable.
- **Message at the top:** open with the conclusion or with the executive question answered, unless the user asked for another order.
- **A single reading sequence:** the eye follows an unambiguous path. Separate context, evidence and numbers, implication, recommendation and next steps without repeating the same sentence among them.
- **Recommendation highlighted once**, when there is one, and alternatives with decision-oriented titles, comparing only equivalent dimensions.
- **Confidentiality:** the summary is the slide that most often circulates alone, by e-mail and forwarded. Confirm the content restrictions before writing and do not put in it an unapproved number, an M&A target or confidential data that the deck handles with care.
- **Quantity:** with no number set, start with one slide and expand only when clarity requires it, without imposing a ceiling of one or two slides with no request or real constraint.

## Validate

Apply the tests of the general skill and the `pptx` QA. In addition: at a quick read, theme, message and next step stand out; each block has an unambiguous role; the recommendation is supported or correctly absent; the slide works without a presenter when sent by e-mail; and the requested quantity and layout were respected.
