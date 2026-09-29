---
name: create-executive-summary
description: Create or review executive summary slide(s) in consulting-report style, synthesizing context, conclusions, alternatives, recommendation, implications or decision so they read on their own, with a finance focus. Trigger whenever the request involves an executive summary, "exec summary", executive overview, executive opening, synthesis page, an opening slide that condenses the whole deck, or a synthesis for a board, committee or steering group, including when reviewing that kind of slide. Works for any client and loads `create-professional-presentations`; the client's visual identity comes from the corresponding client brand skill, if you have one.
---

# Executive summary

A specialization of `create-professional-presentations` for the synthesis slide. Load that skill first (and `pptx` for build and QA): pyramid reasoning, action titles, consulting-style writing, the handling of exhibits and finance, and design are already there. This skill adds only what is specific to the executive summary. Do not repeat the general skill's rules here.

The summary is the slide an executive reads if they read only one. It condenses the whole story of the deck: where we are, what changes, what that implies and what is being decided, in a way that stands on its own, without a presenter.

## What is specific to the summary

- **Calibrated density:** by definition it is the densest slide in the deck, but it is still organized in blocks with a clear function. Synthesizing is not listing everything; it is choosing what is indispensable.
- **Message at the top:** open with the conclusion or with the executive question answered, unless the user asked for a different order.
- **A single reading sequence:** the eye follows one unambiguous path. Separate context, evidence/numbers, implication, recommendation and next steps without repeating the same sentence across them.
- **Explicit recommendation when there is one:** highlight it clearly, once. Do not invent a recommendation in informational material, and do not create artificial alternatives.
- **Alternatives, if any:** say what they represent, with decision-oriented titles, comparing only equivalent dimensions.

## Minimum inputs

Audience and purpose; expected decision or conclusion; sources and base file; essential context and evidence; recommendation and alternatives when they exist; content, confidentiality and design constraints; number of slides; distribution format.

When the number of slides is not defined, start with one slide and expand only when clarity requires it, without imposing a cap of one or two slides absent a request or a real constraint.

## Validate

Apply all the tests of the general skill and the `pptx` QA. In addition: on a quick read, the topic, the message and the way forward stand out; each block has an unambiguous function; the recommendation is supported or correctly absent; the slide works without a presenter when sent by email; and the requested number of slides and layout were respected.
