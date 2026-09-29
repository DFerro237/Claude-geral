# PowerPoint review pitfalls

False positives and method errors that have already cost rework in real reviews. Read this before recording a finding, especially in the font, superscript and position dimensions.

## False positives that look like serious errors

### Arial in the middle of an all-Calibri deck

A scan for `typeface="Arial"` reported 7 occurrences. None was an error: all of them were `<a:buFont typeface="Arial"/>`, the font of the **bullet glyph**, not of the text. Using Arial for bullets is standard PowerPoint practice and is invisible.

Occurrences in the theme do not count either: they are per-script fallbacks for Arabic, Armenian and Vietnamese.

**Check the context of the attribute.** Only `<a:latin>` inside the `<a:rPr>` of a run defines the font of the text.

### Footnote marker that seems not to be superscript

Text extraction returned `$500k1` and `grace period2`, suggesting footnote markers without superscript. That was wrong: the digits were their own runs with `baseline="30000"`, that is, real superscripts. Concatenating the runs is what created the appearance of an error.

**Superscript in OOXML is an attribute, not a character.** A deck may use two mechanisms at once, `baseline` on some slides and the characters `¹²³` on others. Both render the same, so it is not a visible error, at most a hygiene note.

### "Unbalanced" parentheses in footnotes

Numbered notes start with `1)`, `2)`, `i)`. A balance test flags all of them. They are not errors, they are notation.

### "Missing" period before a capital letter

A proper noun in the middle of a sentence, such as `Alpha Capital`, `House of Example` or `ExampleTech`, triggers any naive end-of-sentence heuristic.

### Finding that crosses a shape boundary

Concatenating the text of a whole slide before applying a regex creates strings that do not exist, such as `market overviewSource:`, the junction of one shape's title with the start of another.

**Run searches per paragraph**, not over the concatenated slide text.

## Method errors

### Never replace a string directly in the XML

PowerPoint text lives fragmented in runs for formatting reasons. Real cases found: `foodservice` split into `food` and `service`; `Appendix III` split into `Appendix II` and `I`; `sensitivity` split into `s` and `ensitivity`.

A direct replacement fails in these cases and may destroy formatting. Use the helpers in `scripts/edit.py`, which work at paragraph level, map the position in each run and preserve its properties.

### Searching for double spaces goes wrong in three ways

All three were in the first version of `inspect_deck.py` at the same time.

1. **Requiring `\w` on both sides misses most cases.** The expression was `\w\s\s+\w`, and a double space in running text almost always comes after punctuation, where the left side is `.`, `,`, `)` or `:`. Run against a real deck, it found the spaces between words and missed the ones after a period.
2. **Non-breaking spaces escape a literal search.** `U+00A0`, `U+2007` and `U+202F` come in when pasting from Word or a browser. They count as `\s`, but not as `" "`, and their fix is not the same.
3. **Spaces are invisible in a terminal.** Printing the raw excerpt forces you to count characters on screen. The output has to mark each space, and mark the non-breaking one differently.

### Before assuming you broke something, look at the original

A render showed `Appendix IV - Pr` broken in the middle of the word, with text spilling out of the card. It looked like damage from the correction. It was not: the original rendered identically.

**Always compare against the rendered original**, not against your expectation. And check the run structure of both: if it is the same, the problem predates you.

### Two characters are enough to overflow a box

Changing `US$ 1 million` to `US$ 1.0 million` added 2 characters, broke one more line and pushed the last sentence past the edge of the card.

A box with `spAutoFit` grows and accommodates. A box **without** autofit lets the text overflow silently. Check the autofit mode of the boxes you changed, and prioritize the visual check on them.

### The "inside the box" count does not measure overflow on its own

When cropping a box's region to count lines, the crop has to extend below the edge, otherwise the text that spilled out does not show. The side effect is capturing lines from neighboring shapes.

**The reliable signal is the before versus after comparison**, not the ratio between lines inside and outside.

## Tool limits

### LibreOffice is not PowerPoint

Rendering works very well to catch gross overflow, such as a sentence leaving the card. But it breaks lines slightly differently, so a borderline case may behave differently in PowerPoint.

Say so in the report. It is a real limitation and the user needs to know the final check is theirs.

### Encoding on Windows

A Python script that reads or writes files with accented characters needs `PYTHONUTF8=1` or an explicit `encoding`. On Windows, Python may still default to cp1252, and the corruption is silent.

## Classification

### A number that differs between slides is a factual error

The same value cited as `$250k` on one slide and `$249k` on two others is not a matter of style. Treat it as high priority, and look for arithmetic in the deck itself that settles which one is right. In a case like this, the next sentence showed `$400k`, and `249 + 151 = 400` settled the question.

### A structural difference between blocks is not misalignment

Appendices I and II with a descriptive line in one position and Appendices III and IV in another is a structural choice, not an alignment error. Record it as a question and explain the two formats, instead of proposing to make them uniform.

### A run of spaces may be layout, not a typo

Three deliberate uses that show up in decks:

- **pseudo-column**, such as `Revenue      $1.2M` repeated on several lines of the same box;
- **manual line break**, a block of spaces pushing the next word onto the line below;
- **indent** at the start of a continuation.

What identifies a pseudo-column is the **end** of the run of spaces aligned across lines, not the start: `Revenue` plus 6 spaces and `Cost` plus 9 start in different columns and end in the same one. Comparing the start misses exactly the case where the labels have different lengths, which is the normal case.

A short run in the middle of a long prose paragraph, on the other hand, aligns with nothing and is typing noise. The cutoff the script uses is 4: up to 3 spaces in prose, with no aligned siblings, is a typo; 4 or more goes to question.

The default is question. Asking costs one message, dismantling an approved layout costs redoing work.

### A frozen slide is frozen

When the user says a slide must not be touched, that applies to alignment, size and position, even when you are sure it is off the grid. Text corrections on that slide still apply, but pay double attention to overflow, because you cannot compensate by changing the box.
