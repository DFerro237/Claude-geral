#!/usr/bin/env python3
"""Inventory and diagnosis of a .pptx for a consistency review.

Usage:
    python inspect_deck.py deck.pptx
    python inspect_deck.py deck.pptx --text            # include the full text
    python inspect_deck.py deck.pptx --slides 5,7-9    # limit to some slides

Reads the XML directly, without python-pptx, to see attributes the API hides
(baseline, buFont, theme inheritance). Does not modify the file.

Before recording any finding, read references/pitfalls.md: several things
this script shows look like errors and are not.
"""
import argparse, collections, re, sys, zipfile
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
EMU = 12700.0  # EMU per point

# A starting point, not a closed list. Reconcile it with the "Standards" sheet
# of the previous review before trusting it: that sheet defines the project's
# canonical form. Very short or already naturalized terms were left out on
# purpose, because they produce more false positives than findings.
# The list holds English terms that a Portuguese-language deck sets in italics.
# For a deck in another language, replace it with that deck's foreign terms;
# for a deck written in English, leave it empty.
ITALIC_TERMS = [
    "breakeven", "foodservice", "startup", "valuation", "premium", "payroll",
    "flip", "lock-up", "fully diluted", "founders", "ticket", "container",
    "runway", "churn", "pro rata", "due diligence", "earn-out", "carve-out",
]
# Acronyms and naturalized words that stay in roman even though they are foreign.
ROMAN = {"ebitda", "capex", "opex", "ltm", "sku", "bu", "m&a", "rol", "psf",
         "pmf", "sop", "cagr", "tranche", "tranches", "llc", "board"}


# Regular space plus the ones PowerPoint inserts when pasting from Word or a
# browser: non-breaking, figure and narrow. All of them count as \s, but none
# is found by searching for the literal " " character.
NBSP = "\u00a0\u2007\u202f"  # non-breaking, figure, narrow
RE_SPACES = re.compile(f"[ {NBSP}]{{2,}}")


def points(v):
    return round(int(v) / EMU, 1)


def visible(s):
    """Spaces are invisible in a terminal. Mark each one, and tell nbsp apart."""
    out = []
    for c in s:
        out.append("·" if c == " " else "⍽" if c in NBSP else c)
    return "".join(out)


def is_prose(t):
    """Running text, not a label. A short label without punctuation is usually
    a label and value pair, where the spacing may be deliberate alignment."""
    return len(t.split()) >= 6 and re.search(r"[.,;:!?]", t) is not None


def classify_spaces(slide, occurrences):
    """Separate a likely typo from possibly deliberate formatting.

    occurrences: [(kind, name, paragraph_index, text, match)]
    Returns (typos, suspects), suspects carrying the reason for the doubt.

    The default is suspect. If the signals do not add up to a clear typo, it
    becomes a question: asking costs one message, dismantling a deliberate
    layout costs redoing approved work.
    """
    by_shape = collections.defaultdict(list)
    for o in occurrences:
        by_shape[(o[0], o[1])].append(o)

    typos, suspects = [], []
    for (kind, name), items in by_shape.items():
        for _, _, ip, par, m in items:
            n = len(m.group(0))
            nbsp = any(c in NBSP for c in m.group(0))
            # A pseudo-column aligns the END of the run of spaces, which is
            # where the value starts, not the beginning, which varies with the
            # label length. 'Revenue' + 6 spaces and 'Cost' + 9 start in
            # different columns and end in the same one.
            col = m.end()
            aligned = [x for x in items
                       if x[2] != ip and abs(x[4].end() - col) <= 2]
            in_par = sum(1 for x in items if x[2] == ip)

            if kind == "shape" and aligned:
                reason = (f"{len(aligned) + 1} runs of spaces ending at column "
                          f"~{col}, on different lines: looks like a pseudo-column")
            elif n >= 6:
                reason = f"{n} consecutive spaces: pattern of a manual line break"
            elif n >= 4:
                # Below this, in prose, it is typing noise: 3 spaces in the
                # middle of a long paragraph align with nothing. Deliberate
                # spacing has to be visible, which takes a large block or
                # repetition across lines, and both cases are caught above.
                reason = f"{n} consecutive spaces, too many for typing noise"
            elif kind == "shape" and not is_prose(par):
                reason = "short paragraph or no punctuation: looks like label and value"
            elif in_par > 1:
                reason = f"{in_par} runs of spaces in the same paragraph"
            else:
                typos.append((slide, kind, name, par, m, nbsp))
                continue
            suspects.append((slide, kind, name, par, m, nbsp, reason))
    return typos, suspects


class Deck:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self.slides = sorted(
            (n for n in self.z.namelist()
             if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
            key=lambda s: int(re.findall(r"\d+", s)[0]),
        )

    def root(self, n):
        return ET.fromstring(self.z.read(self.slides[n - 1]))

    def rels(self, n):
        try:
            xml = self.z.read(f"ppt/slides/_rels/slide{n}.xml.rels")
        except KeyError:
            return {}
        return {r.get("Id"): r.get("Target") for r in ET.fromstring(xml)}

    def text(self, n):
        return "".join(t.text or "" for t in self.root(n).iter(A + "t"))

    def paragraphs_ctx(self, n):
        """[(kind, shape_name, text)], with kind in {'shape', 'table'}.

        The kind matters when classifying multiple spaces: nobody fakes a
        column with spaces inside a table, because the column already exists.
        """
        root = self.root(n)
        out = []
        for sp in root.iter(P + "sp"):
            cnv = sp.find(f".//{P}cNvPr")
            name = cnv.get("name") if cnv is not None else "?"
            for par in sp.iter(A + "p"):
                t = "".join(x.text or "" for x in par.iter(A + "t")).strip()
                if t:
                    out.append(("shape", name, t))
        for gf in root.iter(P + "graphicFrame"):
            cnv = gf.find(f".//{P}cNvPr")
            name = cnv.get("name") if cnv is not None else "?"
            for tc in gf.iter(A + "tc"):
                for par in tc.iter(A + "p"):
                    t = "".join(x.text or "" for x in par.iter(A + "t")).strip()
                    if t:
                        out.append(("table", name, t))
        return out

    def paragraphs(self, n):
        return [t for _, _, t in self.paragraphs_ctx(n)]

    def shapes(self, n):
        """(id, name, left, top, width, height, body_pt, autofit, text)"""
        out = []
        for sp in self.root(n).iter(P + "sp"):
            cnv = sp.find(f".//{P}cNvPr")
            xfrm = sp.find(f".//{P}spPr/{A}xfrm")
            off = xfrm.find(A + "off") if xfrm is not None else None
            ext = xfrm.find(A + "ext") if xfrm is not None else None
            body = sp.find(f".//{A}bodyPr")
            if body is not None and body.find(A + "normAutofit") is not None:
                fit = "normAutofit"
            elif body is not None and body.find(A + "spAutoFit") is not None:
                fit = "spAutoFit"
            else:
                fit = "none"
            size = None
            for rpr in sp.iter(A + "rPr"):
                if rpr.get("sz"):
                    size = int(rpr.get("sz")) / 100
                    break
            out.append((
                cnv.get("id") if cnv is not None else "?",
                cnv.get("name") if cnv is not None else "?",
                points(off.get("x")) if off is not None else None,
                points(off.get("y")) if off is not None else None,
                points(ext.get("cx")) if ext is not None else None,
                points(ext.get("cy")) if ext is not None else None,
                size, fit,
                "".join(x.text or "" for x in sp.iter(A + "t")).strip(),
            ))
        return out

    def runs(self, n):
        """(text, font, size, bold, italic, baseline, color, link_rid)"""
        out = []
        for r in self.root(n).iter(A + "r"):
            t = "".join(x.text or "" for x in r.iter(A + "t"))
            pr = r.find(A + "rPr")
            g = (lambda k: pr.get(k)) if pr is not None else (lambda k: None)
            lat = pr.find(A + "latin") if pr is not None else None
            color = None
            if pr is not None:
                sf = pr.find(A + "solidFill")
                if sf is not None:
                    c = sf.find(A + "srgbClr")
                    color = c.get("val") if c is not None else "theme"
            hl = pr.find(A + "hlinkClick") if pr is not None else None
            out.append((
                t, lat.get("typeface") if lat is not None else None,
                g("sz"), g("b"), g("i"), g("baseline"), color,
                (hl.get(R + "id"), hl.get("action")) if hl is not None else None,
            ))
        return out


def section(title):
    print(f"\n{'=' * 78}\n### {title}\n{'=' * 78}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--text", action="store_true", help="include the full text")
    ap.add_argument("--slides", help="e.g. 5,7-9")
    args = ap.parse_args()

    d = Deck(args.deck)
    selected = list(range(1, len(d.slides) + 1))
    if args.slides:
        target = set()
        for part in args.slides.split(","):
            if "-" in part:
                a, b = part.split("-")
                target.update(range(int(a), int(b) + 1))
            else:
                target.add(int(part))
        selected = [s for s in selected if s in target]

    full_text = "".join(d.text(s) for s in selected)

    section(f"SUMMARY: {len(d.slides)} slides in the file, {len(selected)} inspected")

    # ---------- F: fonts ----------
    section("F | FONTS")
    faces = collections.Counter()
    for s in selected:
        for r in d.runs(s):
            faces[r[1] or "(inherits from theme)"] += 1
    for k, v in faces.most_common():
        print(f"  {v:5d}  {k}")
    # The dominant font is taken only among explicit fonts. Including
    # "(inherits from theme)" would invert the logic in a deck where most runs
    # inherit, and would flag the correct font as the deviation.
    explicit = {k: v for k, v in faces.items() if k != "(inherits from theme)"}
    if len(explicit) > 1:
        dominant = max(explicit, key=explicit.get)
        print(f"\n  More than one explicit typeface. Dominant: {dominant}. Deviations:")
        for s in selected:
            for r in d.runs(s):
                if r[1] and r[1] != dominant:
                    print(f"    slide {s:2d} | {r[1]:12s} | {r[0][:46]!r}")
    print("\n  Reminder: buFont and theme fallback do not count. See pitfalls.md")

    # ---------- A: positions ----------
    section("A | POSITIONS (pt) AND AUTOFIT MODE")
    for s in selected:
        print(f"-- slide {s} --")
        for f in d.shapes(s):
            if f[2] is None:
                continue
            print(f"   L={f[2]:7.1f} T={f[3]:7.1f} {str(f[4]):>7}x{str(f[5]):<7}"
                  f" sz={str(f[6]):>6} fit={f[7]:11s} | {f[1][:24]:26s} | {f[8][:40]!r}")

    # ---------- L: links ----------
    section("L | HYPERLINKS")
    for s in selected:
        rels = d.rels(s)
        for r in d.runs(s):
            if not r[7]:
                continue
            rid, action = r[7]
            target = rels.get(rid, "")
            state = "OK" if rid and rid in rels else "DEAD"
            print(f"  [{state:5s}] slide {s:2d} | {r[0][:44]!r} -> {target or action}")
    print("\n  Check that the label matches the target (Appendix I must go to the Appendix I slide).")

    # ---------- I: italics ----------
    section("I | ITALICS ON FOREIGN TERMS")
    found = False
    for s in selected:
        for r in d.runs(s):
            low = r[0].lower()
            for term in ITALIC_TERMS:
                if re.search(rf"\b{re.escape(term)}\b", low) and r[4] != "1":
                    if term in ROMAN:
                        continue
                    print(f"  slide {s:2d} | {term!r} in roman | {r[0][:52]!r}")
                    found = True
    if not found:
        print("  no term from the list in roman")
    print(f"\n  Roman by rule: {', '.join(sorted(ROMAN))}")

    # ---------- U: numbers ----------
    # The magnitude and plural checks follow Portuguese conventions (R$, "Bi",
    # "MM", and "1,5 milhões" where Portuguese wants the singular "milhão").
    # On a deck in another language they simply find nothing.
    section("U | NUMBERS, CURRENCY AND DATES")
    print("  currency with no space after the symbol:",
          re.findall(r"(?:R\$|USD|US\$)\d[^\s]{0,10}", full_text) or "none")
    print("  number glued to the magnitude unit:",
          re.findall(r"(?:R\$|USD)\s?[\d.,]+(?:M|Bi|MM)\b", full_text) or "none")
    print("  plural used below two (Portuguese):",
          re.findall(r"[\d.,]*1,\d+ milhões", full_text) or "none")
    dates = collections.Counter()
    for m in re.findall(r"\b\d{2}/\d{2}/(\d{2,4})\b", full_text):
        dates[f"year with {len(m)} digits"] += 1
    print("  date formats:", dict(dates) or "no dd/mm date")

    # ---------- N: terms ----------
    section("N | SPELLING VARIANTS OF THE SAME TERM")
    pairs = [("pro rata", "pro-rata"), ("foodservice", "food service"),
             ("breakeven", "break-even"), ("cap table", "captable")]
    for a, b in pairs:
        ca = len(re.findall(rf"\b{re.escape(a)}\b", full_text, re.I))
        cb = len(re.findall(rf"\b{re.escape(b)}\b", full_text, re.I))
        if ca and cb:
            print(f"  COEXIST: {a!r} ({ca}x) and {b!r} ({cb}x)")
    annex = r"(?:Anexo|Annex|Appendix)"
    annex_hyphen = re.findall(rf"{annex} [IVX]+ - ", full_text)
    annex_dash = re.findall(rf"{annex} [IVX]+ \u2013 ", full_text)
    if annex_hyphen and annex_dash:
        print(f"  COEXIST: appendix title with hyphen ({len(annex_hyphen)}x) and with dash ({len(annex_dash)}x)")

    # ---------- G: text hygiene ----------
    section("G | MULTIPLE SPACES")
    typos, suspects = [], []
    for s in selected:
        occ = []
        for ip, (kind, name, par) in enumerate(d.paragraphs_ctx(s)):
            for m in RE_SPACES.finditer(par):
                occ.append((kind, name, ip, par, m))
        t, sus = classify_spaces(s, occ)
        typos += t
        suspects += sus

    print("\n-- LIKELY TYPO: treat as a normal error, goes into the table as 'fix' --")
    if not typos:
        print("  none")
    for s, kind, name, par, m, nbsp in typos:
        before = repr(par[m.start() - 1]) if m.start() else "start of paragraph"
        mark = " WITH NON-BREAKING SPACE" if nbsp else ""
        print(f"  slide {s:2d} | {len(m.group(0))} spaces after {before}{mark}"
              f" | {kind} {name[:24]!r}")
        ini, end = max(0, m.start() - 34), m.end() + 34
        print(f"       {'...' if ini else ''}{visible(par[ini:end])}"
              f"{'...' if end < len(par) else ''}")

    print("\n-- POSSIBLY DELIBERATE FORMATTING: ASK before proposing a fix --")
    print("   Goes into the chat table as 'question'. It may be a pseudo-column, a")
    print("   manual line break or an indent. Fixing it dismantles a deliberate layout.")
    if not suspects:
        print("  none")
    by_shape = collections.defaultdict(list)
    for item in suspects:
        by_shape[(item[0], item[1], item[2])].append(item)
    for (s, kind, name), items in by_shape.items():
        print(f"\n  slide {s:2d} | {kind} {name[:34]!r}")
        for reason in dict.fromkeys(i[6] for i in items):
            print(f"       reason: {reason}")
        # The whole paragraph, not an excerpt: the alignment between lines is
        # what reveals the pseudo-column, and an excerpt hides it.
        for par in dict.fromkeys(i[3] for i in items):
            print(f"       {visible(par)[:150]}")

    section("G | LINE-BREAK HYPHENS")
    for s in selected:
        for par in d.paragraphs(s):
            for m in re.finditer(r"[a-zà-ú]{2,}-[a-zà-ú]{2,}", par):
                print(f"  slide {s:2d} hyphen: {m.group(0)!r} (confirm it is a legitimate compound)")

    # ---------- H: file hygiene ----------
    section("H | HYGIENE")
    for s in selected:
        raw = d.z.read(d.slides[s - 1]).decode("utf8", "replace")
        if not d.text(s).strip():
            print(f"  slide {s}: no text | shapes={raw.count('<p:sp>')}"
                  f" images={raw.count('<p:pic>')}")

    if args.text:
        section("FULL TEXT, BY PARAGRAPH")
        for s in selected:
            print(f"\n===== SLIDE {s} =====")
            for par in d.paragraphs(s):
                print("  " + par)


if __name__ == "__main__":
    main()
