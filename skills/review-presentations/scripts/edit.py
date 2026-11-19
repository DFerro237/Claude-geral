#!/usr/bin/env python3
"""Helpers for editing a .pptx that preserve formatting.

Import instead of running directly:

    import sys; sys.path.insert(0, "<scripts folder>")
    from edit import abrir, substituir, italizar, mover, redimensionar_fonte, religar

    prs = abrir("original.pptx", "corrected.pptx")   # copies and opens the copy
    substituir(prs.slides[6], "USD 10M", "USD 10 M")    # replace
    italizar(prs.slides[14], "ticket")                   # italicize
    mover(prs.slides[10], "Next steps", topo=75.7)       # move (topo = top)
    prs.save("corrected.pptx")

Function names: abrir = open, substituir = replace, substituir_no_deck = replace
in the whole deck, italizar = italicize, mover = move, redimensionar_fonte =
resize font, religar = relink, deslinkar = unlink, paragrafos = paragraphs,
forma_por_texto = shape by text.

It exists because PowerPoint text lives fragmented in runs: `foodservice`
may be split into `food` + `service`, and `Appendix III` into `Appendix II` + `I`.
Direct replacement in the XML gets these cases wrong and destroys formatting.
See references/pitfalls.md.
"""
import copy, shutil
from pptx import Presentation
from pptx.util import Pt
from pptx.oxml.ns import qn
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


# ---------------------------------------------------------------- navigation
def abrir(origem, destino=None):
    """Copies origem to destino and opens the copy. Without destino, opens in place."""
    if destino:
        shutil.copy2(origem, destino)
        return Presentation(destino)
    return Presentation(origem)


def _formas(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:  # group
            yield from _formas(sh.shapes)


def paragrafos(slide):
    """All paragraphs of the slide, including inside tables and groups."""
    for sh in _formas(slide.shapes):
        if sh.has_text_frame:
            yield from sh.text_frame.paragraphs
        if getattr(sh, "has_table", False) and sh.has_table:
            for linha in sh.table.rows:
                for celula in linha.cells:
                    yield from celula.text_frame.paragraphs


def forma_por_texto(slide, prefixo):
    """First shape whose text starts with the prefix. Shape names repeat;
    text identifies better."""
    for sh in _formas(slide.shapes):
        if sh.has_text_frame and sh.text_frame.text.strip().startswith(prefixo):
            return sh
    return None


# ---------------------------------------------------------------- text
def _trocar_no_paragrafo(par, antigo, novo):
    runs = list(par.runs)
    if not runs:
        return False
    textos = [r.text for r in runs]
    inteiro = "".join(textos)
    i = inteiro.find(antigo)
    if i < 0:
        return False
    fim = i + len(antigo)
    faixas, pos = [], 0
    for t in textos:
        faixas.append((pos, pos + len(t)))
        pos += len(t)
    # The new text goes entirely into the first run of the range; the others lose
    # only the piece that belonged to them. That way the formatting of the start wins.
    for k, (ini, term) in enumerate(faixas):
        if term <= i or ini >= fim:
            continue
        a = max(i, ini) - ini
        b = min(fim, term) - ini
        runs[k].text = textos[k][:a] + (novo if ini <= i < term else "") + textos[k][b:]
    return True


def substituir(slide, antigo, novo, todas=False):
    """Replaces `antigo` with `novo` preserving formatting. Returns how many replacements."""
    n = 0
    for par in paragrafos(slide):
        while _trocar_no_paragrafo(par, antigo, novo):
            n += 1
            if not todas:
                return n
    return n


def substituir_no_deck(prs, antigo, novo):
    """Applies the replacement on every slide. Returns the total."""
    return sum(substituir(sl, antigo, novo, todas=True) for sl in prs.slides)


# ---------------------------------------------------------------- italics
def italizar(slide, palavra, apenas_palavra=True):
    """Puts `palavra` (word) in italics, splitting the run when it is only a piece of it.

    apenas_palavra=True (word only) ensures only the foreign term gets italics,
    and not the native-language word next to it (`ticket` yes, `average` no).
    """
    for par in paragrafos(slide):
        for r in list(par.runs):
            t = r.text
            if palavra not in t:
                continue
            if r.font.italic and (t.strip() == palavra or not apenas_palavra):
                return True
            i = t.find(palavra)
            pedacos = ((t[:i], False), (palavra, True), (t[i + len(palavra):], False))
            pai = r._r.getparent()
            onde = list(pai).index(r._r)
            novos = []
            for seg, ital in pedacos:
                if seg == "":
                    continue
                nr = copy.deepcopy(r._r)
                nr.find(qn("a:t")).text = seg
                pr = nr.find(qn("a:rPr"))
                if pr is None:
                    pr = nr.makeelement(qn("a:rPr"), {})
                    nr.insert(0, pr)
                if ital:
                    pr.set("i", "1")
                novos.append(nr)
            for e in reversed(novos):
                pai.insert(onde, e)
            pai.remove(r._r)
            return True
    return False


# ---------------------------------------------------------------- position
def mover(slide, prefixo_texto, esquerda=None, topo=None):
    """Repositions in points (esquerda = left, topo = top). Does not touch size."""
    sh = forma_por_texto(slide, prefixo_texto)
    if sh is None:
        return False
    if esquerda is not None:
        sh.left = Pt(esquerda)
    if topo is not None:
        sh.top = Pt(topo)
    return True


def redimensionar_fonte(slide, prefixo_texto, pontos):
    sh = forma_por_texto(slide, prefixo_texto)
    if sh is None:
        return False
    for par in sh.text_frame.paragraphs:
        for r in par.runs:
            r.font.size = Pt(pontos)
    return True


# ---------------------------------------------------------------- links
def religar(prs, slide_origem_idx, texto_do_link, slide_destino_idx):
    """Recreates a dead internal hyperlink. Indices are 1-based.

    A disabled link shows up as an empty r:id with action=ppaction://noaction.
    """
    origem = prs.slides[slide_origem_idx - 1]
    destino = prs.slides[slide_destino_idx - 1]
    rid = origem.part.relate_to(destino.part, RT.SLIDE)
    for par in paragrafos(origem):
        for r in par.runs:
            if r.text.strip() != texto_do_link:
                continue
            pr = r._r.find(qn("a:rPr"))
            if pr is None:
                continue
            hl = pr.find(qn("a:hlinkClick"))
            if hl is None:
                hl = pr.makeelement(qn("a:hlinkClick"), {})
                pr.append(hl)
            hl.set(qn("r:id"), rid)
            hl.set("action", "ppaction://hlinksldjump")
            return rid
    return None


def deslinkar(slide, texto_exato):
    """Removes the hyperlink from a run without deleting the text."""
    for par in paragrafos(slide):
        for r in par.runs:
            if r.text != texto_exato:
                continue
            pr = r._r.find(qn("a:rPr"))
            if pr is None:
                continue
            hl = pr.find(qn("a:hlinkClick"))
            if hl is not None:
                pr.remove(hl)
                return True
    return False
