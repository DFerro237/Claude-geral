# -*- coding: utf-8 -*-
"""
Primitives for building an analytical document in Word with python-docx.

These are primitives, not a ready-made document template. They solve the plumbing
that always costs time and always produces the same defects (footer repeated in
every section, blank page before each heading, table wider than the page). The
anatomy of the document, the order of the sections and what goes in each one remain
the writer's decision, on every piece of work.

Colors, font and geometry are parameters. For client material with its own visual
identity, pass the values from the client's brand guidelines instead of accepting
the defaults. The labels written into the document ("Source: ", "What this means: ")
are parameters too, so a deliverable in another language can use its own wording.

Usage as a library:

    from doc import AnalyticalDocument
    d = AnalyticalDocument(footer="Technical note  |  Internal use  |  ")
    d.h1("Situation found", num=1)
    d.p("Paragraph text.")
    d.quote("literal excerpt from the contract", source="Contract X, clause 4.2",
            authority="signed document")
    d.explain("In plain terms, this means that ...")
    d.table(["Company", "Registration no."], [["Alpha Ltd.", "00-0000000"]])
    d.table_source("Public registry lookup, 2026-01-15")
    d.save("output.docx")

Usage as a verifier of an already saved .docx:

    python doc.py --verify output.docx

The verifier measures tables and images against the usable width of the section they
are in. It is the check that replaces page-by-page inspection when PDF export is not
available, and it is worth running every time, because it is instantaneous.
"""

import argparse
import sys

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

OPEN_QUOTE = "“"
CLOSE_QUOTE = "”"
EMU_PER_CM = 360000
TWIPS_PER_CM = 1440 / 2.54


def _hex(value):
    return RGBColor.from_string(value.lstrip("#").upper())


# --------------------------------------------------------------- raw XML
# python-docx does not expose shading, paragraph borders, repeated table headers or
# page fields. All of that is hand-written XML.

def _shade(el, color_hex):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex.lstrip("#").upper())
    el.append(shd)


def shade_cell(cell, color_hex):
    _shade(cell._tc.get_or_add_tcPr(), color_hex)


def shade_paragraph(par, color_hex):
    _shade(par._p.get_or_add_pPr(), color_hex)


def paragraph_border(par, side="left", color_hex="000000", thickness=18, spacing=8):
    pPr = par._p.get_or_add_pPr()
    pbdr = pPr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        pPr.append(pbdr)
    b = OxmlElement("w:" + side)
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(thickness))
    b.set(qn("w:space"), str(spacing))
    b.set(qn("w:color"), color_hex.lstrip("#").upper())
    pbdr.append(b)


def table_borders(table, color_hex="D9D9D9", thickness=4):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(thickness))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), color_hex.lstrip("#").upper())
        borders.append(e)
    table._tbl.tblPr.append(borders)


def repeat_header(row):
    """Repeats the first row at the top of every page. A long table without this
    forces the reader to go back to find out what each column is."""
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


# --------------------------------------------------------------- document
class AnalyticalDocument:
    def __init__(
        self,
        font="Calibri",
        body_pt=10.5,
        text_color="000000",
        accent_color="1F3864",
        secondary_color="2E74B5",
        muted_color="595959",
        band_color="F2F2F2",
        border_color="D9D9D9",
        footer=None,
        margin_cm=2.2,
        vertical_margin_cm=2.0,
        source_label="Source: ",
    ):
        self.font = font
        self.body_pt = body_pt
        self.text_color = _hex(text_color)
        self.accent_color = _hex(accent_color)
        self.secondary_color = _hex(secondary_color)
        self.muted_color = _hex(muted_color)
        self.accent_hex = accent_color.lstrip("#").upper()
        self.band_hex = band_color.lstrip("#").upper()
        self.border_hex = border_color.lstrip("#").upper()
        self.footer = footer
        self.margin_cm = margin_cm
        self.vertical_margin_cm = vertical_margin_cm
        self.source_label = source_label

        d = Document()
        st = d.styles["Normal"]
        st.font.name = font
        st.font.size = Pt(body_pt)
        st.font.color.rgb = self.text_color
        # rFonts needs eastAsia as well, otherwise Word swaps the font in passages it
        # considers non-Latin, and the document comes out with two typefaces.
        st.element.rPr.rFonts.set(qn("w:eastAsia"), font)
        pf = st.paragraph_format
        pf.space_after = Pt(6)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.12

        s = d.sections[0]
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = Cm(margin_cm)
        s.top_margin = s.bottom_margin = Cm(vertical_margin_cm)
        self.d = d
        self._build_footer(s, first=True)

    # ---- available width
    def usable_width_cm(self, section=None):
        """Text width of the section, in cm. Tables and images have to fit in it."""
        s = section or self.d.sections[-1]
        return (s.page_width - s.left_margin - s.right_margin) / Cm(1)

    # ---- runs and blocks
    def _run(self, par, text, size=None, bold=False, italic=False, color=None):
        r = par.add_run(text)
        r.font.name = self.font
        r.font.size = Pt(size if size is not None else self.body_pt)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color if color is not None else self.text_color
        r._element.rPr.rFonts.set(qn("w:eastAsia"), self.font)
        return r

    def h1(self, text, num=None, new_page=False):
        """Section heading. `new_page` uses page_break_before instead of inserting a
        break before it: an inserted break leaves an empty paragraph behind, and that
        is how the blank page nobody can explain shows up."""
        p = self.d.add_paragraph()
        if new_page:
            p.paragraph_format.page_break_before = True
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        self._run(p, (f"{num}. " if num else "") + text, size=15, bold=True,
                  color=self.accent_color)
        paragraph_border(p, "bottom", self.accent_hex, thickness=8, spacing=4)
        return p

    def h2(self, text):
        p = self.d.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        self._run(p, text, size=12, bold=True, color=self.accent_color)
        return p

    def h3(self, text):
        p = self.d.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        self._run(p, text, size=self.body_pt, bold=True, color=self.secondary_color)
        return p

    def p(self, text=None, parts=None, size=None, align=None, space_after=6):
        """`parts` accepts a mix of str and ("text", {"bold": True}) to emphasize
        inside the paragraph without splitting it into several."""
        par = self.d.add_paragraph()
        par.paragraph_format.space_after = Pt(space_after)
        par.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
        for item in (parts or [text]):
            if isinstance(item, str):
                self._run(par, item, size=size)
            else:
                kw = dict(item[1])
                kw.setdefault("size", size)
                self._run(par, item[0], **kw)
        return par

    def bullet(self, text=None, parts=None, size=None, level=0):
        par = self.d.add_paragraph(style="List Bullet")
        par.paragraph_format.left_indent = Cm(0.75 + 0.6 * level)
        par.paragraph_format.space_after = Pt(3)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for item in (parts or [text]):
            if isinstance(item, str):
                self._run(par, item, size=size)
            else:
                kw = dict(item[1])
                kw.setdefault("size", size)
                self._run(par, item[0], **kw)
        return par

    def quote(self, text, source, authority=None):
        """Literal excerpt, with its source attached right below.

        `authority` says what that document is (signed, unsigned draft, public
        record, working spreadsheet). Fill it in whenever the difference could change
        the reading: a draft read as a signed contract is the kind of error that runs
        through the whole document without being noticed.
        """
        p1 = self.d.add_paragraph()
        p1.paragraph_format.left_indent = Cm(0.5)
        p1.paragraph_format.space_before = Pt(7)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.keep_with_next = True
        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self._run(p1, OPEN_QUOTE + text + CLOSE_QUOTE, size=self.body_pt - 1,
                  italic=True, color=self.muted_color)
        paragraph_border(p1, "left", self.accent_hex)
        shade_paragraph(p1, self.band_hex)

        p2 = self.d.add_paragraph()
        p2.paragraph_format.left_indent = Cm(0.5)
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(7)
        label = f"{self.source_label}{source}"
        if authority:
            label += f"  [{authority}]"
        self._run(p2, label, size=self.body_pt - 2, color=self.muted_color)
        paragraph_border(p2, "left", self.accent_hex)
        shade_paragraph(p2, self.band_hex)
        return p1, p2

    def explain(self, text, label="What this means: "):
        """Translation of the quoted excerpt into plain language. It comes right after
        the quotation, because whoever reads the document usually has not opened the
        contract and has no obligation to decipher the legal wording alone."""
        par = self.d.add_paragraph()
        par.paragraph_format.left_indent = Cm(0.5)
        par.paragraph_format.space_after = Pt(10)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self._run(par, label, bold=True, color=self.accent_color)
        self._run(par, text)
        return par

    def note(self, text):
        par = self.d.add_paragraph()
        par.paragraph_format.space_after = Pt(9)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self._run(par, text, size=self.body_pt - 2, color=self.muted_color)
        return par

    def table(self, header, rows, widths=None, size=9, header_size=9,
              zebra=True):
        """Table with a colored header that repeats across pages.

        `widths` in cm. When omitted, splits the usable width of the section into
        equal parts, which guarantees the table fits. When you pass widths, check the
        sum against `usable_width_cm()`: a table wider than the page is the Word
        defect that most often goes unnoticed at generation time and most annoys the
        reader.

        A cell that starts with ** comes out in bold, to highlight a total row.
        """
        n = len(header)
        if widths is None:
            widths = [self.usable_width_cm() / n] * n

        t = self.d.add_table(rows=1, cols=n)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        table_borders(t, self.border_hex)

        hdr = t.rows[0]
        repeat_header(hdr)
        for i, text in enumerate(header):
            c = hdr.cells[i]
            c.width = Cm(widths[i])
            shade_cell(c, self.accent_hex)
            par = c.paragraphs[0]
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.space_after = Pt(2)
            self._run(par, text, size=header_size, bold=True,
                      color=RGBColor(0xFF, 0xFF, 0xFF))

        for j, values in enumerate(rows):
            row = t.add_row()
            for i, text in enumerate(values):
                c = row.cells[i]
                c.width = Cm(widths[i])
                if zebra and j % 2 == 1:
                    shade_cell(c, self.band_hex)
                par = c.paragraphs[0]
                par.paragraph_format.space_before = Pt(2)
                par.paragraph_format.space_after = Pt(2)
                text = str(text)
                self._run(par, text.replace("**", ""), size=size,
                          bold=text.startswith("**"))

        self.d.add_paragraph().paragraph_format.space_after = Pt(4)
        return t

    def table_source(self, text):
        """Source line for the table immediately before it."""
        par = self.d.paragraphs[-1]
        par.paragraph_format.space_after = Pt(10)
        self._run(par, self.source_label + text, size=self.body_pt - 2.5,
                  color=self.muted_color)
        return par

    def image(self, path, width_cm=None):
        """Centered image. Without a width, it takes the usable width of the current
        section, which is what you want for a diagram on a landscape page."""
        par = self.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(4)
        par.add_run().add_picture(path, width=Cm(width_cm or self.usable_width_cm()))
        return par

    # ---- sections
    def _build_footer(self, section, first=False):
        """Only the first section builds its own footer. The following ones inherit it.

        Without is_linked_to_previous, each new section gets an empty footer and Word
        ends up showing the text repeated or losing the page numbering.
        """
        if not first:
            section.footer.is_linked_to_previous = True
            return
        if not self.footer:
            return
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        self._run(p, self.footer, size=8, color=self.muted_color)
        self._page_field(p)

    def _page_field(self, par):
        """PAGE field. A page number written as text stops being correct as soon as
        the document grows by one page."""
        r = par.add_run()
        r.font.name = self.font
        r.font.size = Pt(8)
        r.font.color.rgb = self.muted_color
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        r._r.append(begin)
        r._r.append(instr)
        r._r.append(end)

    def landscape_section(self, margin_cm=1.5):
        """Sideways page for a wide diagram. Remember to return with portrait_section()."""
        s = self.d.add_section(WD_SECTION.NEW_PAGE)
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Cm(29.7), Cm(21.0)
        s.left_margin = s.right_margin = Cm(margin_cm)
        s.top_margin = s.bottom_margin = Cm(margin_cm)
        self._build_footer(s)
        return s

    def portrait_section(self):
        s = self.d.add_section(WD_SECTION.NEW_PAGE)
        s.orientation = WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = Cm(self.margin_cm)
        s.top_margin = s.bottom_margin = Cm(self.vertical_margin_cm)
        self._build_footer(s)
        return s

    def save(self, path):
        self.d.save(path)
        return path


# --------------------------------------------------------------- verification
def _index_by_section(doc):
    """Maps each table and each body paragraph to the section it belongs to.

    Word marks the end of a section with a sectPr inside its last paragraph. Walking
    the body in order and counting those markers is what makes it possible to compare
    each object with the width of the right page, and not with that of the first one.
    """
    idx = 0
    mapping = []
    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag in ("p", "tbl"):
            mapping.append((tag, child, idx))
            if tag == "p":
                pPr = child.find(qn("w:pPr"))
                if pPr is not None and pPr.find(qn("w:sectPr")) is not None:
                    idx += 1
    return mapping


def verify(path):
    """Measures tables and images against the usable width of the section they are in.

    It does not replace looking at the document, but it catches the defect that
    reading the extracted text never shows: the object that overflows the page.
    """
    doc = Document(path)
    widths = []
    for s in doc.sections:
        usable = (s.page_width - s.left_margin - s.right_margin) / Cm(1)
        orient = "landscape" if s.page_width > s.page_height else "portrait"
        widths.append(usable)
        print(f"section {len(widths) - 1}: {orient}, usable width {usable:.2f} cm")

    problems = 0
    n_tbl = n_img = 0
    for tag, el, sec in _index_by_section(doc):
        usable = widths[min(sec, len(widths) - 1)]
        if tag == "tbl":
            n_tbl += 1
            grid = el.find(qn("w:tblGrid"))
            if grid is None:
                continue
            total = sum(
                int(c.get(qn("w:w")) or 0) for c in grid.findall(qn("w:gridCol"))
            ) / TWIPS_PER_CM
            if total > usable + 0.05:
                problems += 1
                print(f"  TABLE {n_tbl} (section {sec}): {total:.2f} cm in {usable:.2f} cm usable")
        else:
            for ext in el.iter(qn("wp:extent")):
                n_img += 1
                cm = int(ext.get("cx") or 0) / EMU_PER_CM
                if cm > usable + 0.05:
                    problems += 1
                    print(f"  IMAGE {n_img} (section {sec}): {cm:.2f} cm in {usable:.2f} cm usable")

    print(f"\n{n_tbl} tables, {n_img} images, {len(widths)} sections")
    print(f"objects wider than the usable width: {problems}")
    return problems


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Width checker for a .docx")
    ap.add_argument("--verify", metavar="FILE", required=True)
    args = ap.parse_args()
    sys.exit(1 if verify(args.verify) else 0)
