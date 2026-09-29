# Building the .docx with python-docx

Plumbing. Read this when you generate the file. The primitives in `scripts/doc.py` already solve everything described here; this document exists for when you need to go beyond them or understand why they are built the way they are.

## Contents

- [Page break without a blank page](#page-break-without-a-blank-page)
- [Footer and page numbering](#footer-and-page-numbering)
- [Landscape section](#landscape-section)
- [Usable width and sizing](#usable-width-and-sizing)
- [Single font](#single-font)
- [Table](#table)
- [What python-docx does not expose](#what-python-docx-does-not-expose)
- [Windows environment and COM](#windows-environment-and-com)

## Page break without a blank page

Use `page_break_before` on the heading paragraph:

```python
p = doc.add_paragraph()
p.paragraph_format.page_break_before = True
```

Do not use `document.add_page_break()`. It creates a paragraph just to carry the break, and that paragraph has height. When the previous content ends near the bottom of the page, that paragraph alone pushes onto the next one and the document gains a blank page that shows up in no text inspection. It is one of the most annoying defects to diagnose later, because the `.docx` is formally correct.

## Footer and page numbering

Each new section is born with its own empty footer. If you build the footer in every section, the text repeats and the numbering gets lost. Build it only in the first section and inherit it in the others:

```python
section.footer.is_linked_to_previous = True
```

The page number has to be a field, not text. Written as a string, it stops being correct as soon as the document grows by one page:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

r = paragraph.add_run()
begin = OxmlElement("w:fldChar");  begin.set(qn("w:fldCharType"), "begin")
instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
instr.text = " PAGE "
end = OxmlElement("w:fldChar");  end.set(qn("w:fldCharType"), "end")
for el in (begin, instr, end):
    r._r.append(el)
```

Word calculates the field when it opens the file. A tool that only reads the XML will show the footer without a number, and that is not an error.

## Landscape section

Changing `orientation` is not enough: you also have to swap the page dimensions, because Word uses `page_width` and `page_height`, and the orientation is only a label.

```python
s = doc.add_section(WD_SECTION.NEW_PAGE)
s.orientation = WD_ORIENT.LANDSCAPE
s.page_width, s.page_height = Cm(29.7), Cm(21.0)
```

Return to portrait after the diagram, with a new section and the dimensions swapped back. A document that goes into landscape and never comes out stays sideways until the end.

## Usable width and sizing

```python
usable = (s.page_width - s.left_margin - s.right_margin) / Cm(1)
```

On A4 portrait with 2.2 cm margins, that comes to 16.60 cm. On A4 landscape with 1.5 cm margins, it comes to 26.70 cm.

Every table and every image has to fit within that number, in the section where it sits. A table wider than the page is the Word defect that most often goes unnoticed at generation time: the file opens normally, the extracted text is correct, and only on reading does the column show up cut off.

`scripts/doc.py --verify file.docx` measures this by mapping each object to its section. The mapping is necessary because Word marks the end of a section with a `sectPr` inside its last paragraph; comparing everything against the width of the first section flags a false positive on every diagram on a landscape page.

## Single font

Set the font on the `Normal` style **and** on the `eastAsia` attribute:

```python
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
```

Without this, Word swaps the typeface in passages it classifies as non-Latin and the document comes out with two fonts. Repeat it on each run when you create runs by hand.

## Table

- `table.autofit = False` and width per cell, not per column. python-docx applies width to the cell; setting it only on the first row does not hold the others.
- Repeat the header across pages with `w:tblHeader` on the first row. A long table without it forces the reader to go back to find out what each column is.
- Borders and shading are hand-written XML (`w:tblBorders`, `w:shd`). They are ready-made in `scripts/doc.py`.

## What python-docx does not expose

These need hand-written XML: cell and paragraph shading, paragraph border, repeated header, page field, `sectPr` outside the normal flow. All of them are already implemented in `scripts/doc.py`; copy from there instead of rewriting.

## Windows environment and COM

When you open the file in Word via COM to check or export it:

- **One Office application per call.** Word and PowerPoint in the same call exceed the timeout and leave an orphaned process holding a lock on the file, and the next write fails with a "file is being used by another process" error. Use `try/finally` with guaranteed `Close()` and `Quit()`.
- **PDF export may hang** because the Word session has degraded, not because the document is defective. If it hangs, do not insist: validate another way (open the file and read the page count, measure the geometry with the verifier) and **state in the report that the visual inspection was not done**. Staying silent about it is reporting a validation that did not happen.
- **Write the `.py` file with the Write tool, not through a heredoc in Bash.** The heredoc turns `\n` inside a Python string into a real line break and produces `SyntaxError: unterminated string literal`.
