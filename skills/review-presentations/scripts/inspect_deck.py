#!/usr/bin/env python3
"""Inventory and diagnosis of a .pptx for a consistency review.

Usage:
    python inspect_deck.py deck.pptx
    python inspect_deck.py deck.pptx --texto           # includes the full text
    python inspect_deck.py deck.pptx --slides 5,7-9    # limits to slides

Reads the XML directly, without depending on python-pptx, to see attributes the
API hides (baseline, buFont, theme inheritance). Does not modify the file.

Before logging any finding, read references/pitfalls.md: several things this
script shows look like errors and are not.

Some automatic checks (sections U and N) match patterns of Portuguese-language
decks, such as "R$", "milhões" and "Anexo" (appendix). Adapt the patterns to the
deck's language, or do those checks by reading.
"""
import argparse, collections, re, sys, zipfile
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
EMU = 12700.0  # EMU per point

# Starting point, not a closed list. Reconcile it with the "Standards" tab of the
# previous review before trusting it: that tab defines the project's canonical form.
# Very short or already naturalized terms were left out on purpose, because they
# produce more false positives than findings.
TERMOS_ITALICO = [
    "breakeven", "foodservice", "startup", "valuation", "premium", "payroll",
    "flip", "lock-up", "fully diluted", "founders", "ticket", "container",
    "runway", "churn", "pro rata", "due diligence", "earn-out", "carve-out",
]
# Acronyms and naturalized words that stay in roman even though they are foreign.
REDONDO = {"ebitda", "capex", "opex", "ltm", "sku", "bu", "m&a", "rol", "psf",
           "pmf", "sop", "cagr", "tranche", "tranches", "cvc", "llc", "board"}


# Regular space plus the ones PowerPoint inserts when pasting from Word and from a
# browser: non-breaking, figure and narrow. All count as \s, but none is found by
# searching for the literal " " character.
NBSP = "\u00a0\u2007\u202f"  # non-breaking, figure, narrow
RE_ESPACOS = re.compile(f"[ {NBSP}]{{2,}}")


def pontos(v):
    return round(int(v) / EMU, 1)


def visivel(s):
    """Spaces cannot be seen in a terminal. Marks each one, and tells the nbsp apart."""
    saida = []
    for c in s:
        saida.append("·" if c == " " else "⍽" if c in NBSP else c)
    return "".join(saida)


def eh_prosa(t):
    """Running text, not a label. A short label without punctuation is usually a
    label-value pair, where the spacing may be deliberate alignment."""
    return len(t.split()) >= 6 and re.search(r"[.,;:!?]", t) is not None


def classificar_espacos(slide, ocorrencias):
    """Separates a probable typo from possibly deliberate formatting.

    ocorrencias (occurrences): [(type, name, paragraph_index, text, match)]
    Returns (typos, suspeitos), suspeitos (suspects) carrying the reason for doubt.

    The default is suspect. If the signals do not add up to a clear typo, it goes
    to doubt: asking costs one message, dismantling deliberate layout costs
    redoing approved work.
    """
    por_forma = collections.defaultdict(list)
    for o in ocorrencias:
        por_forma[(o[0], o[1])].append(o)

    typos, suspeitos = [], []
    for (tipo, nome), itens in por_forma.items():
        for _, _, ip, par, m in itens:
            n = len(m.group(0))
            nbsp = any(c in NBSP for c in m.group(0))
            # A pseudo-column aligns the END of the run, which is where the value
            # starts, not the start, which varies with the label length.
            # 'Revenue' + 6 spaces and 'Cost' + 8 start at different columns
            # and end at the same one.
            col = m.end()
            alinhados = [x for x in itens
                         if x[2] != ip and abs(x[4].end() - col) <= 2]
            no_par = sum(1 for x in itens if x[2] == ip)

            if tipo == "forma" and alinhados:
                motivo = (f"{len(alinhados) + 1} runs ending at column "
                          f"~{col}, on different lines: looks like a pseudo-column")
            elif n >= 6:
                motivo = f"{n} spaces in a row: manual line break pattern"
            elif n >= 4:
                # Below this, in prose, it is typing noise: 3 spaces in the
                # middle of a long paragraph do not align with anything. Deliberate
                # spacing has to be visible, which takes a large block or
                # repetition across lines, and both cases are already caught above.
                motivo = f"{n} spaces in a row, too many for typing noise"
            elif tipo == "forma" and not eh_prosa(par):
                motivo = "short paragraph or no punctuation: looks like label and value"
            elif no_par > 1:
                motivo = f"{no_par} runs in the same paragraph"
            else:
                typos.append((slide, tipo, nome, par, m, nbsp))
                continue
            suspeitos.append((slide, tipo, nome, par, m, nbsp, motivo))
    return typos, suspeitos


class Deck:
    def __init__(self, caminho):
        self.z = zipfile.ZipFile(caminho)
        self.slides = sorted(
            (n for n in self.z.namelist()
             if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
            key=lambda s: int(re.findall(r"\d+", s)[0]),
        )

    def raiz(self, n):
        return ET.fromstring(self.z.read(self.slides[n - 1]))

    def rels(self, n):
        try:
            xml = self.z.read(f"ppt/slides/_rels/slide{n}.xml.rels")
        except KeyError:
            return {}
        return {r.get("Id"): r.get("Target") for r in ET.fromstring(xml)}

    def texto(self, n):
        return "".join(t.text or "" for t in self.raiz(n).iter(A + "t"))

    def paragrafos_ctx(self, n):
        """[(type, shape_name, text)], with type in {'forma' (shape), 'tabela' (table)}.

        The type matters to classify multiple spaces: inside a table nobody
        fakes a column with spaces, because the column already exists.
        """
        raiz = self.raiz(n)
        saida = []
        for sp in raiz.iter(P + "sp"):
            cnv = sp.find(f".//{P}cNvPr")
            nome = cnv.get("name") if cnv is not None else "?"
            for par in sp.iter(A + "p"):
                t = "".join(x.text or "" for x in par.iter(A + "t")).strip()
                if t:
                    saida.append(("forma", nome, t))
        for gf in raiz.iter(P + "graphicFrame"):
            cnv = gf.find(f".//{P}cNvPr")
            nome = cnv.get("name") if cnv is not None else "?"
            for tc in gf.iter(A + "tc"):
                for par in tc.iter(A + "p"):
                    t = "".join(x.text or "" for x in par.iter(A + "t")).strip()
                    if t:
                        saida.append(("tabela", nome, t))
        return saida

    def paragrafos(self, n):
        return [t for _, _, t in self.paragrafos_ctx(n)]

    def formas(self, n):
        """(id, name, left, top, width, height, body_pt, autofit, text)"""
        saida = []
        for sp in self.raiz(n).iter(P + "sp"):
            cnv = sp.find(f".//{P}cNvPr")
            xfrm = sp.find(f".//{P}spPr/{A}xfrm")
            off = xfrm.find(A + "off") if xfrm is not None else None
            ext = xfrm.find(A + "ext") if xfrm is not None else None
            corpo = sp.find(f".//{A}bodyPr")
            if corpo is not None and corpo.find(A + "normAutofit") is not None:
                fit = "normAutofit"
            elif corpo is not None and corpo.find(A + "spAutoFit") is not None:
                fit = "spAutoFit"
            else:
                fit = "none"
            tam = None
            for rpr in sp.iter(A + "rPr"):
                if rpr.get("sz"):
                    tam = int(rpr.get("sz")) / 100
                    break
            saida.append((
                cnv.get("id") if cnv is not None else "?",
                cnv.get("name") if cnv is not None else "?",
                pontos(off.get("x")) if off is not None else None,
                pontos(off.get("y")) if off is not None else None,
                pontos(ext.get("cx")) if ext is not None else None,
                pontos(ext.get("cy")) if ext is not None else None,
                tam, fit,
                "".join(x.text or "" for x in sp.iter(A + "t")).strip(),
            ))
        return saida

    def runs(self, n):
        """(text, font, size, bold, italic, baseline, color, link_rid)"""
        saida = []
        for r in self.raiz(n).iter(A + "r"):
            t = "".join(x.text or "" for x in r.iter(A + "t"))
            pr = r.find(A + "rPr")
            g = (lambda k: pr.get(k)) if pr is not None else (lambda k: None)
            lat = pr.find(A + "latin") if pr is not None else None
            cor = None
            if pr is not None:
                sf = pr.find(A + "solidFill")
                if sf is not None:
                    c = sf.find(A + "srgbClr")
                    cor = c.get("val") if c is not None else "tema"
            hl = pr.find(A + "hlinkClick") if pr is not None else None
            saida.append((
                t, lat.get("typeface") if lat is not None else None,
                g("sz"), g("b"), g("i"), g("baseline"), cor,
                (hl.get(R + "id"), hl.get("action")) if hl is not None else None,
            ))
        return saida


def sec(titulo):
    print(f"\n{'=' * 78}\n### {titulo}\n{'=' * 78}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--texto", action="store_true", help="includes the full text")
    ap.add_argument("--slides", help="e.g.: 5,7-9")
    args = ap.parse_args()

    d = Deck(args.deck)
    todos = list(range(1, len(d.slides) + 1))
    if args.slides:
        alvo = set()
        for parte in args.slides.split(","):
            if "-" in parte:
                a, b = parte.split("-")
                alvo.update(range(int(a), int(b) + 1))
            else:
                alvo.add(int(parte))
        todos = [s for s in todos if s in alvo]

    texto_total = "".join(d.texto(s) for s in todos)

    sec(f"SUMMARY: {len(d.slides)} slides in the file, {len(todos)} inspected")

    # ---------- F: fonts ----------
    sec("F | FONTS")
    faces = collections.Counter()
    for s in todos:
        for r in d.runs(s):
            faces[r[1] or "(herda do tema)"] += 1
    for k, v in faces.most_common():
        print(f"  {v:5d}  {k}")
    # The dominant font comes only from the explicit ones. Including "(herda do tema)"
    # (inherits from theme) would invert the logic in a deck where most runs inherit,
    # and would flag precisely the correct font as a deviation.
    explicitas = {k: v for k, v in faces.items() if k != "(herda do tema)"}
    if len(explicitas) > 1:
        dominante = max(explicitas, key=explicitas.get)
        print(f"\n  More than one explicit typeface. Dominant: {dominante}. Deviations:")
        for s in todos:
            for r in d.runs(s):
                if r[1] and r[1] != dominante:
                    print(f"    slide {s:2d} | {r[1]:12s} | {r[0][:46]!r}")
    print("\n  Reminder: buFont and theme fallback do not count. See pitfalls.md")

    # ---------- A: positions ----------
    sec("A | POSITIONS (pt) AND AUTOFIT MODE")
    for s in todos:
        print(f"-- slide {s} --")
        for f in d.formas(s):
            if f[2] is None:
                continue
            print(f"   L={f[2]:7.1f} T={f[3]:7.1f} {str(f[4]):>7}x{str(f[5]):<7}"
                  f" sz={str(f[6]):>6} fit={f[7]:11s} | {f[1][:24]:26s} | {f[8][:40]!r}")

    # ---------- L: links ----------
    sec("L | HYPERLINKS")
    mapa = {"I": None, "II": None, "III": None, "IV": None}
    for s in todos:
        rels = d.rels(s)
        for r in d.runs(s):
            if not r[7]:
                continue
            rid, acao = r[7]
            destino = rels.get(rid, "")
            estado = "OK" if rid and rid in rels else "DEAD"
            print(f"  [{estado:5s}] slide {s:2d} | {r[0][:44]!r} -> {destino or acao}")
    print("\n  Check that the label matches the target (Appendix I must go to the Appendix I slide).")

    # ---------- I: italics ----------
    sec("I | ITALICS ON FOREIGN TERMS")
    achou = False
    for s in todos:
        for r in d.runs(s):
            baixo = r[0].lower()
            for termo in TERMOS_ITALICO:
                if re.search(rf"\b{re.escape(termo)}\b", baixo) and r[4] != "1":
                    if termo in REDONDO:
                        continue
                    print(f"  slide {s:2d} | {termo!r} in roman | {r[0][:52]!r}")
                    achou = True
    if not achou:
        print("  no term from the list in roman")
    print(f"\n  Roman by rule: {', '.join(sorted(REDONDO))}")

    # ---------- U: numbers ----------
    sec("U | NUMBERS, CURRENCY AND DATE")
    print("  currency without a space after the symbol:",
          re.findall(r"(?:R\$|USD|US\$)\d[^\s]{0,10}", texto_total) or "none")
    print("  number stuck to the magnitude unit:",
          re.findall(r"(?:R\$|USD)\s?[\d.,]+(?:M|Bi|MM)\b", texto_total) or "none")
    print("  undue plural below two ('milhões'):",
          re.findall(r"[\d.,]*1,\d+ milhões", texto_total) or "none")
    datas = collections.Counter()
    for m in re.findall(r"\b\d{2}/\d{2}/(\d{2,4})\b", texto_total):
        datas[f"year with {len(m)} digits"] += 1
    print("  date formats:", dict(datas) or "no dd/mm date")

    # ---------- N: terms ----------
    sec("N | SPELLING VARIANTS OF THE SAME TERM")
    pares = [("pro rata", "pro-rata"), ("foodservice", "food service"),
             ("breakeven", "break-even"), ("cap table", "captable")]
    for a, b in pares:
        ca = len(re.findall(rf"\b{re.escape(a)}\b", texto_total, re.I))
        cb = len(re.findall(rf"\b{re.escape(b)}\b", texto_total, re.I))
        if ca and cb:
            print(f"  COEXIST: {a!r} ({ca}x) and {b!r} ({cb}x)")
    anexo_h = re.findall(r"Anexo [IVX]+ - ", texto_total)
    anexo_t = re.findall(r"Anexo [IVX]+ \u2013 ", texto_total)  # \u2013 = en dash
    if anexo_h and anexo_t:
        print(f"  COEXIST: appendix with hyphen ({len(anexo_h)}x) and with en dash ({len(anexo_t)}x)")

    # ---------- G: text hygiene ----------
    sec("G | MULTIPLE SPACES")
    typos, suspeitos = [], []
    for s in todos:
        ocorr = []
        for ip, (tipo, nome, par) in enumerate(d.paragrafos_ctx(s)):
            for m in RE_ESPACOS.finditer(par):
                ocorr.append((tipo, nome, ip, par, m))
        t, sus = classificar_espacos(s, ocorr)
        typos += t
        suspeitos += sus

    print("\n-- PROBABLE TYPO: treat as a normal error, goes into the table as 'fix' --")
    if not typos:
        print("  none")
    for s, tipo, nome, par, m, nbsp in typos:
        antes = repr(par[m.start() - 1]) if m.start() else "start of paragraph"
        marca = " WITH NON-BREAKING SPACE" if nbsp else ""
        print(f"  slide {s:2d} | {len(m.group(0))} spaces after {antes}{marca}"
              f" | {tipo} {nome[:24]!r}")
        ini, fim = max(0, m.start() - 34), m.end() + 34
        print(f"       {'...' if ini else ''}{visivel(par[ini:fim])}"
              f"{'...' if fim < len(par) else ''}")

    print("\n-- POSSIBLY DELIBERATE FORMATTING: ASK before proposing a fix --")
    print("   Goes into the chat table as 'doubt'. It may be a pseudo-column, a manual")
    print("   line break or an indent. Fixing it dismantles layout made on purpose.")
    if not suspeitos:
        print("  none")
    porforma = collections.defaultdict(list)
    for item in suspeitos:
        porforma[(item[0], item[1], item[2])].append(item)
    for (s, tipo, nome), itens in porforma.items():
        print(f"\n  slide {s:2d} | {tipo} {nome[:34]!r}")
        for motivo in dict.fromkeys(i[6] for i in itens):
            print(f"       reason: {motivo}")
        # Whole paragraph, not a snippet: it is the alignment across lines that
        # reveals the pseudo-column, and a snippet hides it.
        for par in dict.fromkeys(i[3] for i in itens):
            print(f"       {visivel(par)[:150]}")

    sec("G | LINE-BREAK HYPHEN")
    for s in todos:
        for par in d.paragrafos(s):
            for m in re.finditer(r"[a-zà-ú]{2,}-[a-zà-ú]{2,}", par):
                print(f"  slide {s:2d} hyphen: {m.group(0)!r} (confirm whether it is a legitimate compound)")

    # ---------- H: file hygiene ----------
    sec("H | HYGIENE")
    for s in todos:
        bruto = d.z.read(d.slides[s - 1]).decode("utf8", "replace")
        if not d.texto(s).strip():
            print(f"  slide {s}: no text | shapes={bruto.count('<p:sp>')}"
                  f" images={bruto.count('<p:pic>')}")

    if args.texto:
        sec("FULL TEXT, BY PARAGRAPH")
        for s in todos:
            print(f"\n===== SLIDE {s} =====")
            for par in d.paragrafos(s):
                print("  " + par)


if __name__ == "__main__":
    main()
