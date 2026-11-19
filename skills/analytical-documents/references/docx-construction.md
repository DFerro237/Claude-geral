# Building the .docx outside the primitives

The primitives in `scripts/doc.py` already solve the plumbing, and the code for each solution is there, commented. Read this only when you need to step outside them or open the file in Word through COM.

## Why the primitives are the way they are

If you write python-docx by hand, do not undo these choices:

- **Page break** through `page_break_before` on the heading, never `add_page_break()`. The extra paragraph of the break has height and, near the end of the page, produces a blank page that no text inspection shows.
- **Footer** built only in the first section, and the others with `is_linked_to_previous = True`; otherwise the text repeats and the numbering gets lost. The page number is a `PAGE` field, not text. A tool that only reads the XML shows the footer without a number, and that is not an error.
- **Landscape** requires changing `orientation` and also `page_width` and `page_height`, because the orientation is only a label. Return to portrait with a new section.
- **Usable width** is measured per section: Word marks the end of a section with a `sectPr` in its last paragraph, and comparing everything against the first section flags a false positive on every landscape page.
- **A single font** requires the `eastAsia` attribute in the `Normal` style and in every run created by hand; without it, Word swaps the typeface in text it classifies as non-Latin.
- **Tables** with `autofit = False` and width per cell (setting it only on the first row does not hold the others), and `w:tblHeader` on the first row to repeat the header across pages.

## Windows environment and COM

When opening the file in Word through COM to check or export it (see also an Office COM guide in `~/.claude/guides/`, when there is one):

- **One Office application per call.** Word and PowerPoint in the same call run past the timeout and leave an orphan process holding a lock on the file, and the next write fails with "being used by another process". Use `try/finally` with guaranteed `Close()` and `Quit()`.
- **The PDF export may hang** because the Word session degrades, not because of a defect in the document. If it hangs, do not insist: validate another way (open it and read the page count, measure the geometry with the checker) and **say in the report that the visual inspection was not done**.
- **Write the `.py` with the Write tool, not through a heredoc in Bash.** The heredoc turns `\n` inside a Python string into a real line break and produces `SyntaxError: unterminated string literal`.
