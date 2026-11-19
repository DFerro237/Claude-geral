# PowerPoint review pitfalls

False positives and method errors that have already cost rework in a real review. Check this before logging a finding, especially in the font, superscript and position dimensions.

## False positives that look like serious errors

### Arial in the middle of an all-Calibri deck

A sweep for `typeface="Arial"` flagged 7 occurrences. None was an error: all were `<a:buFont typeface="Arial"/>`, the font of the **list bullet glyph**, not of the text. Using Arial for bullets is standard PowerPoint practice and is invisible.

The occurrences in the theme do not count either: they are per-script fallbacks, for Arabic, Armenian and Vietnamese.

**Check the context of the attribute.** Only `<a:latin>` inside the `<a:rPr>` of a run sets the text font.

### Note marker that seems not to be superscript

Text extraction returned `USD 500k1` and `grace period2`, suggesting a note marker without superscript. That was wrong: the digits were runs of their own with `baseline="30000"`, that is, real superscripts. It was the concatenation of the runs that produced the appearance of an error.

**Superscript in OOXML is an attribute, not a character.** A deck may use two mechanisms at once, `baseline` on some slides and the characters `¹²³` on others. Both render the same, so it is not a visible error, at most a hygiene note.

### "Unbalanced" parentheses in a footnote

Numbered notes start with `1)`, `2)`, `i)`. A balance test flags all of them. They are not errors, they are notation.

### "Missing" period before a capital letter

A proper name in the middle of a sentence, such as `Alpha Capital`, `House of Example` or `ExampleTech`, trips any naive end-of-sentence heuristic.

### Finding that crosses a shape boundary

Concatenating the text of a whole slide before applying a regex creates excerpts that do not exist, such as `market overviewSource:`, the joining of one shape's title with the start of another.

**Run searches per paragraph**, not over the concatenated slide text.

## Method errors

### Never replace a string directly in the XML

PowerPoint text lives fragmented in runs for formatting reasons. Real cases found: `foodservice` split into `food` and `service`; `Appendix III` split into `Appendix II` and `I`; `sensitivity` split into `s` and `ensitivity`.

Direct replacement gets these cases wrong and can destroy formatting. Use the helpers in `scripts/edit.py`, which work at paragraph level, map the position in each run and preserve its properties.

### Double-space search done by hand

`inspect_deck.py` already covers the three method errors. If you search outside the script, repeat the precautions: a double space almost always comes after punctuation (do not require `\w` on both sides); the non-breaking space (`U+00A0`, `U+2007`, `U+202F`) escapes a literal search for `" "`; and the output must mark each space, because in the terminal it cannot be seen.

### Before assuming you broke something, look at the original

A render showed `Appendix IV - Pr` broken in the middle of the word, with text spilling out of the card. It looked like damage from the fix. It was not: the original rendered identically.

**Always compare against the rendered original**, not against your expectation. And check the run structure of both: if it is the same, the problem predates you.

### Two characters are enough to overflow a box

Changing `USD 1 million` to `USD 1.0 million` added 2 characters, wrapped one more line and pushed the last sentence over the edge of the card.

A box with `spAutoFit` grows and accommodates. A box **without** autofit lets the text overflow silently. Check the autofit mode of the boxes you changed, and prioritize the visual check on them.

### The "inside the box" count does not measure overflow on its own

When cropping a box's region to count lines, the crop has to extend below the edge, otherwise the text that spilled over does not show. The side effect is capturing lines from neighboring shapes.

**The reliable signal is the before-versus-after comparison**, not the ratio of lines inside and outside.

## Tool limits

### LibreOffice is not PowerPoint

The rendering works very well to catch gross overflow, such as a sentence leaving the card. But it wraps lines slightly differently, so a borderline case may behave differently in PowerPoint.

Say so in the report. It is a real limitation and the user needs to know the final check is theirs.

## Classification

### A number diverging across slides is a factual error

The same value cited as `USD 250k` on one slide and `USD 249k` on two others is not a matter of style. Treat it as high priority, and look for arithmetic in the deck itself that settles which one is right. In one such case, the next sentence had `USD 400k`, and `249 + 151 = 400` settled the question.

### A structural difference between blocks is not misalignment

Appendices I and II with the description line in one position and Appendices III and IV in another is a structural choice, not an alignment error. Log it as doubt and explain both formats, instead of proposing to make them uniform.

### A run of spaces may be layout, not a typo

Three deliberate uses that show up in decks:

- **pseudo-column**, like `Revenue      USD 1.2M` repeated across several lines of the same box;
- **manual line break**, a block of spaces pushing the next word to the line below;
- **indent** at the start of a continuation.

The script already separates the cases: it identifies the pseudo-column by the **end** of the run aligned across lines (labels of different lengths start at different columns) and sends every run of 4 or more spaces to doubt. Up to 3 spaces in prose, with no aligned lines, is a typo.

The default is doubt. Asking costs one message, dismantling approved layout costs redoing work.

### A frozen slide is frozen

When the user says a slide must not be touched, that holds for alignment, size and position, even when you are sure it is off the grid. Text fixes on that slide still apply, but with extra attention to overflow, because you cannot compensate by touching the box.
