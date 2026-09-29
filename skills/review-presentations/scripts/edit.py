#!/usr/bin/env python3
"""Editing helpers for .pptx that preserve formatting.

Import them instead of running this file:

    import sys; sys.path.insert(0, "<scripts folder>")
    from edit import open_copy, replace, italicize, move, resize_font, relink

    prs = open_copy("original.pptx", "corrected.pptx")   # copies and opens the copy
    replace(prs.slides[6], "USD 10M", "USD 10 M")
    italicize(prs.slides[14], "ticket")
    move(prs.slides[10], "Next steps", top=75.7)
    prs.save("corrected.pptx")

It exists because PowerPoint text lives fragmented in runs: `foodservice`
may be split into `food` + `service`, and `Appendix III` into `Appendix II` + `I`.
A direct replacement in the XML fails in these cases and destroys formatting.
See references/pitfalls.md.
"""
import copy, shutil
from pptx import Presentation
from pptx.util import Pt
from pptx.oxml.ns import qn
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


# ---------------------------------------------------------------- navigation
def open_copy(source, target=None):
    """Copy source to target and open the copy. Without a target, open in place."""
    if target:
        shutil.copy2(source, target)
        return Presentation(target)
    return Presentation(source)


def _shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:  # group
            yield from _shapes(sh.shapes)


def paragraphs(slide):
    """Every paragraph on the slide, including inside tables and groups."""
    for sh in _shapes(slide.shapes):
        if sh.has_text_frame:
            yield from sh.text_frame.paragraphs
        if getattr(sh, "has_table", False) and sh.has_table:
            for row in sh.table.rows:
                for cell in row.cells:
                    yield from cell.text_frame.paragraphs


def shape_by_text(slide, prefix):
    """First shape whose text starts with the prefix. Shape names repeat;
    text identifies a shape better."""
    for sh in _shapes(slide.shapes):
        if sh.has_text_frame and sh.text_frame.text.strip().startswith(prefix):
            return sh
    return None


# ---------------------------------------------------------------- text
def _replace_in_paragraph(par, old, new):
    runs = list(par.runs)
    if not runs:
        return False
    texts = [r.text for r in runs]
    whole = "".join(texts)
    i = whole.find(old)
    if i < 0:
        return False
    end = i + len(old)
    spans, pos = [], 0
    for t in texts:
        spans.append((pos, pos + len(t)))
        pos += len(t)
    # The new text goes entirely into the first run of the span; the others
    # lose only the piece that belonged to them. That way the formatting of
    # the start prevails.
    for k, (start, stop) in enumerate(spans):
        if stop <= i or start >= end:
            continue
        a = max(i, start) - start
        b = min(end, stop) - start
        runs[k].text = texts[k][:a] + (new if start <= i < stop else "") + texts[k][b:]
    return True


def replace(slide, old, new, all_occurrences=False):
    """Replace `old` with `new` preserving formatting. Returns how many replacements."""
    n = 0
    for par in paragraphs(slide):
        while _replace_in_paragraph(par, old, new):
            n += 1
            if not all_occurrences:
                return n
    return n


def replace_in_deck(prs, old, new):
    """Apply the replacement on every slide. Returns the total."""
    return sum(replace(sl, old, new, all_occurrences=True) for sl in prs.slides)


# ---------------------------------------------------------------- italics
def italicize(slide, word, whole_word=True):
    """Set `word` in italics, splitting the run when it is only part of it.

    whole_word=True makes sure only the foreign term gets italics, and not
    the neighboring native word (`ticket` yes, the word next to it no).
    """
    for par in paragraphs(slide):
        for r in list(par.runs):
            t = r.text
            if word not in t:
                continue
            if r.font.italic and (t.strip() == word or not whole_word):
                return True
            i = t.find(word)
            pieces = ((t[:i], False), (word, True), (t[i + len(word):], False))
            parent = r._r.getparent()
            where = list(parent).index(r._r)
            new_runs = []
            for seg, ital in pieces:
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
                new_runs.append(nr)
            for e in reversed(new_runs):
                parent.insert(where, e)
            parent.remove(r._r)
            return True
    return False


# ---------------------------------------------------------------- position
def move(slide, text_prefix, left=None, top=None):
    """Reposition in points. Does not touch the size."""
    sh = shape_by_text(slide, text_prefix)
    if sh is None:
        return False
    if left is not None:
        sh.left = Pt(left)
    if top is not None:
        sh.top = Pt(top)
    return True


def resize_font(slide, text_prefix, points):
    sh = shape_by_text(slide, text_prefix)
    if sh is None:
        return False
    for par in sh.text_frame.paragraphs:
        for r in par.runs:
            r.font.size = Pt(points)
    return True


# ---------------------------------------------------------------- links
def relink(prs, source_slide_idx, link_text, target_slide_idx):
    """Recreate a dead internal hyperlink. Indexes are 1-based.

    A disabled link shows up as an empty r:id with action=ppaction://noaction.
    """
    source = prs.slides[source_slide_idx - 1]
    target = prs.slides[target_slide_idx - 1]
    rid = source.part.relate_to(target.part, RT.SLIDE)
    for par in paragraphs(source):
        for r in par.runs:
            if r.text.strip() != link_text:
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


def unlink(slide, exact_text):
    """Remove the hyperlink from a run without deleting the text."""
    for par in paragraphs(slide):
        for r in par.runs:
            if r.text != exact_text:
                continue
            pr = r._r.find(qn("a:rPr"))
            if pr is None:
                continue
            hl = pr.find(qn("a:hlinkClick"))
            if hl is not None:
                pr.remove(hl)
                return True
    return False
