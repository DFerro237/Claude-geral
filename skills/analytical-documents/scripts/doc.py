# -*- coding: utf-8 -*-
"""
Primitives for building an analytical document in Word with python-docx.

They are primitives, not a ready-made document template. They solve the plumbing
that always costs time and always produces the same defects (footer repeated in
every section, blank page before each heading, table wider than the page). The
anatomy of the document, the order of the sections and what goes in each one remain
the writer's decision, for each piece of work.

Colors, font and geometry are parameters. In client material with its own brand
identity, pass the values from the brand skill instead of accepting the defaults.

Usage as a library (class and method names are in Portuguese; see the comments):

    from doc import Documento
    d = Documento(rodape="Technical note  |  Internal use  |  ")
    d.h1("Situation found", num=1)
    d.p("Paragraph text.")
    d.citacao("literal passage of the contract", fonte="Contract X, clause 4.2",
              autoridade="signed document")         # quotation
    d.explica("In plain language, this means that ...")  # what this means
    d.tabela(["Company", "Tax ID"], [["Alpha", "00.000.000/0001-00"]])  # table
    d.fonte_tabela("Public registry lookup, 2026-08-07")  # source line of the table
    d.save("output.docx")

Usage as a checker of a saved .docx:

    python doc.py --verificar output.docx

The checker measures tables and images against the usable width of the section they
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

ASPA_ABRE = "“"
ASPA_FECHA = "”"
EMU_POR_CM = 360000
TWIPS_POR_CM = 1440 / 2.54


def _hex(valor):
    return RGBColor.from_string(valor.lstrip("#").upper())


# --------------------------------------------------------------- raw XML
# python-docx does not expose shading, paragraph border, repeated header or page
# field. All of that is XML by hand.

def _shade(el, cor_hex):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor_hex.lstrip("#").upper())
    el.append(shd)


def sombrear_celula(cell, cor_hex):
    _shade(cell._tc.get_or_add_tcPr(), cor_hex)


def sombrear_paragrafo(par, cor_hex):
    _shade(par._p.get_or_add_pPr(), cor_hex)


def borda_paragrafo(par, lado="left", cor_hex="000000", espessura=18, espaco=8):
    pPr = par._p.get_or_add_pPr()
    pbdr = pPr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        pPr.append(pbdr)
    b = OxmlElement("w:" + lado)
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(espessura))
    b.set(qn("w:space"), str(espaco))
    b.set(qn("w:color"), cor_hex.lstrip("#").upper())
    pbdr.append(b)


def bordas_tabela(table, cor_hex="D9D9D9", espessura=4):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(espessura))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), cor_hex.lstrip("#").upper())
        borders.append(e)
    table._tbl.tblPr.append(borders)


def repetir_cabecalho(row):
    """Repeats the first row at the top of each page. A long table without this
    forces the reader to go back to find out what each column is."""
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


# --------------------------------------------------------------- document
class Documento:
    def __init__(
        self,
        fonte="Calibri",
        corpo_pt=10.5,
        cor_texto="000000",
        cor_destaque="1F3864",
        cor_apoio="2E74B5",
        cor_discreta="595959",
        cor_faixa="F2F2F2",
        cor_borda="D9D9D9",
        rodape=None,
        margem_cm=2.2,
        margem_vertical_cm=2.0,
    ):
        self.fonte = fonte
        self.corpo_pt = corpo_pt
        self.cor_texto = _hex(cor_texto)
        self.cor_destaque = _hex(cor_destaque)
        self.cor_apoio = _hex(cor_apoio)
        self.cor_discreta = _hex(cor_discreta)
        self.hex_destaque = cor_destaque.lstrip("#").upper()
        self.hex_faixa = cor_faixa.lstrip("#").upper()
        self.hex_borda = cor_borda.lstrip("#").upper()
        self.rodape = rodape
        self.margem_cm = margem_cm
        self.margem_vertical_cm = margem_vertical_cm

        d = Document()
        st = d.styles["Normal"]
        st.font.name = fonte
        st.font.size = Pt(corpo_pt)
        st.font.color.rgb = self.cor_texto
        # rFonts needs eastAsia as well, otherwise Word swaps the font in text it
        # considers non-Latin, and the document comes out with two typefaces.
        st.element.rPr.rFonts.set(qn("w:eastAsia"), fonte)
        pf = st.paragraph_format
        pf.space_after = Pt(6)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.12

        s = d.sections[0]
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = Cm(margem_cm)
        s.top_margin = s.bottom_margin = Cm(margem_vertical_cm)
        self.d = d
        self._montar_rodape(s, primeira=True)

    # ---- available width
    def largura_util_cm(self, section=None):
        """Text width of the section, in cm. Tables and images must fit in it."""
        s = section or self.d.sections[-1]
        return (s.page_width - s.left_margin - s.right_margin) / Cm(1)

    # ---- runs and blocks
    def _run(self, par, texto, size=None, bold=False, italic=False, cor=None):
        r = par.add_run(texto)
        r.font.name = self.fonte
        r.font.size = Pt(size if size is not None else self.corpo_pt)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = cor if cor is not None else self.cor_texto
        r._element.rPr.rFonts.set(qn("w:eastAsia"), self.fonte)
        return r

    def h1(self, texto, num=None, nova_pagina=False):
        """Section heading. `nova_pagina` (new page) uses page_break_before instead
        of inserting a break before it: an inserted break leaves an empty paragraph,
        and that is how the blank page nobody can explain shows up."""
        p = self.d.add_paragraph()
        if nova_pagina:
            p.paragraph_format.page_break_before = True
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        self._run(p, (f"{num}. " if num else "") + texto, size=15, bold=True,
                  cor=self.cor_destaque)
        borda_paragrafo(p, "bottom", self.hex_destaque, espessura=8, espaco=4)
        return p

    def h2(self, texto):
        p = self.d.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        self._run(p, texto, size=12, bold=True, cor=self.cor_destaque)
        return p

    def h3(self, texto):
        p = self.d.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        self._run(p, texto, size=self.corpo_pt, bold=True, cor=self.cor_apoio)
        return p

    def p(self, texto=None, partes=None, size=None, align=None, space_after=6):
        """`partes` (parts) accepts a mix of str and ("text", {"bold": True}) to
        emphasize inside the paragraph without splitting it into several."""
        par = self.d.add_paragraph()
        par.paragraph_format.space_after = Pt(space_after)
        par.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
        for item in (partes or [texto]):
            if isinstance(item, str):
                self._run(par, item, size=size)
            else:
                kw = dict(item[1])
                kw.setdefault("size", size)
                self._run(par, item[0], **kw)
        return par

    def bullet(self, texto=None, partes=None, size=None, nivel=0):
        par = self.d.add_paragraph(style="List Bullet")
        par.paragraph_format.left_indent = Cm(0.75 + 0.6 * nivel)
        par.paragraph_format.space_after = Pt(3)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for item in (partes or [texto]):
            if isinstance(item, str):
                self._run(par, item, size=size)
            else:
                kw = dict(item[1])
                kw.setdefault("size", size)
                self._run(par, item[0], **kw)
        return par

    def citacao(self, texto, fonte, autoridade=None):
        """Literal passage (quotation), with the source attached right below.

        `autoridade` (authority) says what that document is (signed, unsigned draft,
        public record, working spreadsheet). Fill it in whenever the difference could
        change the reading: a draft read as a signed contract is the kind of error
        that runs through the whole document unnoticed.
        """
        p1 = self.d.add_paragraph()
        p1.paragraph_format.left_indent = Cm(0.5)
        p1.paragraph_format.space_before = Pt(7)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.keep_with_next = True
        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self._run(p1, ASPA_ABRE + texto + ASPA_FECHA, size=self.corpo_pt - 1,
                  italic=True, cor=self.cor_discreta)
        borda_paragrafo(p1, "left", self.hex_destaque)
        sombrear_paragrafo(p1, self.hex_faixa)

        p2 = self.d.add_paragraph()
        p2.paragraph_format.left_indent = Cm(0.5)
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(7)
        rotulo = f"Source: {fonte}"
        if autoridade:
            rotulo += f"  [{autoridade}]"
        self._run(p2, rotulo, size=self.corpo_pt - 2, cor=self.cor_discreta)
        borda_paragrafo(p2, "left", self.hex_destaque)
        sombrear_paragrafo(p2, self.hex_faixa)
        return p1, p2

    def explica(self, texto, rotulo="What this means: "):
        """Translation of the quoted passage into plain language. It comes right
        after the quotation, because the reader of the document usually has not
        opened the contract and has no obligation to decipher the legal drafting
        alone."""
        par = self.d.add_paragraph()
        par.paragraph_format.left_indent = Cm(0.5)
        par.paragraph_format.space_after = Pt(10)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self._run(par, rotulo, bold=True, cor=self.cor_destaque)
        self._run(par, texto)
        return par

    def nota(self, texto):
        par = self.d.add_paragraph()
        par.paragraph_format.space_after = Pt(9)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self._run(par, texto, size=self.corpo_pt - 2, cor=self.cor_discreta)
        return par

    def tabela(self, cabecalho, linhas, larguras=None, size=9, cab_size=9,
               zebra=True):
        """Table with a colored header repeated across pages.

        `larguras` (widths) in cm. When omitted, it splits the usable width of the
        section into equal parts, which guarantees that the table fits. When you pass
        widths, check the sum against `largura_util_cm()`: a table wider than the
        page is the Word defect that most often goes unnoticed in generation and
        most bothers the reader.

        A cell that starts with ** comes out in bold, to highlight a total row.
        """
        n = len(cabecalho)
        if larguras is None:
            larguras = [self.largura_util_cm() / n] * n

        t = self.d.add_table(rows=1, cols=n)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        bordas_tabela(t, self.hex_borda)

        hdr = t.rows[0]
        repetir_cabecalho(hdr)
        for i, texto in enumerate(cabecalho):
            c = hdr.cells[i]
            c.width = Cm(larguras[i])
            sombrear_celula(c, self.hex_destaque)
            par = c.paragraphs[0]
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.space_after = Pt(2)
            self._run(par, texto, size=cab_size, bold=True,
                      cor=RGBColor(0xFF, 0xFF, 0xFF))

        for j, linha in enumerate(linhas):
            row = t.add_row()
            for i, texto in enumerate(linha):
                c = row.cells[i]
                c.width = Cm(larguras[i])
                if zebra and j % 2 == 1:
                    sombrear_celula(c, self.hex_faixa)
                par = c.paragraphs[0]
                par.paragraph_format.space_before = Pt(2)
                par.paragraph_format.space_after = Pt(2)
                texto = str(texto)
                self._run(par, texto.replace("**", ""), size=size,
                          bold=texto.startswith("**"))

        self.d.add_paragraph().paragraph_format.space_after = Pt(4)
        return t

    def fonte_tabela(self, texto):
        """Source line of the immediately preceding table."""
        par = self.d.paragraphs[-1]
        par.paragraph_format.space_after = Pt(10)
        self._run(par, "Source: " + texto, size=self.corpo_pt - 2.5,
                  cor=self.cor_discreta)
        return par

    def imagem(self, caminho, largura_cm=None):
        """Centered image. With no width given, it takes the usable width of the
        current section, which is what you want for a diagram on a landscape page."""
        par = self.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(4)
        par.add_run().add_picture(caminho, width=Cm(largura_cm or self.largura_util_cm()))
        return par

    # ---- sections
    def _montar_rodape(self, section, primeira=False):
        """Only the first section builds its own footer. The following ones inherit.

        Without is_linked_to_previous, each new section gets an empty footer and Word
        ends up showing the text repeated or losing the numbering.
        """
        if not primeira:
            section.footer.is_linked_to_previous = True
            return
        if not self.rodape:
            return
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        self._run(p, self.rodape, size=8, cor=self.cor_discreta)
        self._campo_pagina(p)

    def _campo_pagina(self, par):
        """PAGE field. A number written as text stops being right as soon as the
        document grows by one page."""
        r = par.add_run()
        r.font.name = self.fonte
        r.font.size = Pt(8)
        r.font.color.rgb = self.cor_discreta
        ini = OxmlElement("w:fldChar")
        ini.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        fim = OxmlElement("w:fldChar")
        fim.set(qn("w:fldCharType"), "end")
        r._r.append(ini)
        r._r.append(instr)
        r._r.append(fim)

    def secao_paisagem(self, margem_cm=1.5):
        """Landscape page for a wide diagram. Remember to return with secao_retrato()
        (portrait section)."""
        s = self.d.add_section(WD_SECTION.NEW_PAGE)
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Cm(29.7), Cm(21.0)
        s.left_margin = s.right_margin = Cm(margem_cm)
        s.top_margin = s.bottom_margin = Cm(margem_cm)
        self._montar_rodape(s)
        return s

    def secao_retrato(self):
        s = self.d.add_section(WD_SECTION.NEW_PAGE)
        s.orientation = WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = Cm(self.margem_cm)
        s.top_margin = s.bottom_margin = Cm(self.margem_vertical_cm)
        self._montar_rodape(s)
        return s

    def save(self, path):
        self.d.save(path)
        return path


# --------------------------------------------------------------- checking
def _indice_por_secao(doc):
    """Maps each table and each body paragraph to the section it is in.

    Word marks the end of a section with a sectPr inside its last paragraph. Walking
    the body in order and counting those markers is what makes it possible to compare
    each object with the width of the right page, and not with that of the first.
    """
    idx = 0
    mapa = []
    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag in ("p", "tbl"):
            mapa.append((tag, child, idx))
            if tag == "p":
                pPr = child.find(qn("w:pPr"))
                if pPr is not None and pPr.find(qn("w:sectPr")) is not None:
                    idx += 1
    return mapa


def verificar(caminho):
    """Measures tables and images against the usable width of the section they are in.

    It does not replace looking at the document, but it catches the defect that
    reading the extracted text never shows: the object that overflows the page.
    """
    doc = Document(caminho)
    larguras = []
    for s in doc.sections:
        util = (s.page_width - s.left_margin - s.right_margin) / Cm(1)
        orient = "landscape" if s.page_width > s.page_height else "portrait"
        larguras.append(util)
        print(f"section {len(larguras) - 1}: {orient}, usable width {util:.2f} cm")

    problemas = 0
    n_tab = n_img = 0
    for tag, el, sec in _indice_por_secao(doc):
        util = larguras[min(sec, len(larguras) - 1)]
        if tag == "tbl":
            n_tab += 1
            grid = el.find(qn("w:tblGrid"))
            if grid is None:
                continue
            total = sum(
                int(c.get(qn("w:w")) or 0) for c in grid.findall(qn("w:gridCol"))
            ) / TWIPS_POR_CM
            if total > util + 0.05:
                problemas += 1
                print(f"  TABLE {n_tab} (section {sec}): {total:.2f} cm in {util:.2f} cm usable")
        else:
            for ext in el.iter(qn("wp:extent")):
                n_img += 1
                cm = int(ext.get("cx") or 0) / EMU_POR_CM
                if cm > util + 0.05:
                    problemas += 1
                    print(f"  IMAGE {n_img} (section {sec}): {cm:.2f} cm in {util:.2f} cm usable")

    print(f"\n{n_tab} tables, {n_img} images, {len(larguras)} sections")
    print(f"objects beyond the usable width: {problemas}")
    return problemas


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Width checker for a .docx")
    ap.add_argument("--verificar", metavar="FILE", required=True)
    args = ap.parse_args()
    sys.exit(1 if verificar(args.verificar) else 0)
