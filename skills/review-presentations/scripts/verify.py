#!/usr/bin/env python3
"""Compares the original deck with the corrected one and reports collateral damage.

Usage:
    python verify.py original.pptx corrected.pptx
    python verify.py original.pptx corrected.pptx --proibido "tiem,USD400,Appendix I - "
    python verify.py original.pptx corrected.pptx --esperado "time,USD 400"
    python verify.py original.pptx corrected.pptx --congelado 5

Flags: --proibido = forbidden excerpts, --esperado = expected excerpts,
--congelado = frozen slides.

Layers:
  1. structural  leftovers of the errors, shapes created or removed
  2. formatting  run-by-run comparison: size, color, bold, italic, link
  3. position    changed coordinates, in EMU and in points
  4. links       everything resolves, no orphan r:id

The visual layer, the only one that catches overflow, is in line_count.py.
"""
import argparse, re, sys, zipfile
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


RE_ESPACOS = re.compile("[ \u00a0\u2007\u202f]{2,}")


def slides(z):
    return sorted((n for n in z.namelist()
                   if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                  key=lambda s: int(re.findall(r"\d+", s)[0]))


def espacos_multiplos(z, caminho):
    """Counts runs of 2 or more spaces, counting per paragraph.

    Per paragraph, not over the slide's concatenated text: joining the text of
    different shapes invents double spaces that do not exist in the file.
    """
    total = 0
    for par in ET.fromstring(z.read(caminho)).iter(A + "p"):
        t = "".join(x.text or "" for x in par.iter(A + "t")).strip()
        total += len(RE_ESPACOS.findall(t))
    return total


def runs(z, caminho):
    saida = []
    for r in ET.fromstring(z.read(caminho)).iter(A + "r"):
        t = "".join(x.text or "" for x in r.iter(A + "t"))
        pr = r.find(A + "rPr")
        g = (lambda k: pr.get(k)) if pr is not None else (lambda k: None)
        cor = None
        if pr is not None:
            sf = pr.find(A + "solidFill")
            if sf is not None:
                c = sf.find(A + "srgbClr")
                cor = c.get("val") if c is not None else "tema"
        lat = pr.find(A + "latin") if pr is not None else None
        saida.append(dict(
            t=t, sz=g("sz"), b=g("b"), i=g("i"), u=g("u"), base=g("baseline"),
            cor=cor, fonte=lat.get("typeface") if lat is not None else None,
            link=pr is not None and pr.find(A + "hlinkClick") is not None,
        ))
    return saida


def formas(z, caminho):
    saida = []
    for sp in ET.fromstring(z.read(caminho)).iter(P + "sp"):
        cnv = sp.find(f".//{P}cNvPr")
        xfrm = sp.find(f".//{P}spPr/{A}xfrm")
        off = xfrm.find(A + "off") if xfrm is not None else None
        ext = xfrm.find(A + "ext") if xfrm is not None else None
        preench = sp.find(f".//{P}spPr/{A}solidFill")
        cor = None
        if preench is not None:
            c = preench.find(A + "srgbClr")
            cor = c.get("val") if c is not None else "tema"
        saida.append(dict(
            id=cnv.get("id") if cnv is not None else "?",
            nome=cnv.get("name") if cnv is not None else "?",
            pos=(off.get("x"), off.get("y")) if off is not None else None,
            tam=(ext.get("cx"), ext.get("cy")) if ext is not None else None,
            fill=cor, rot=xfrm.get("rot") if xfrm is not None else None,
            texto="".join(x.text or "" for x in sp.iter(A + "t")).strip()[:40],
        ))
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("corrigido")
    ap.add_argument("--proibido", help="excerpts that must no longer exist, comma-separated")
    ap.add_argument("--esperado", help="excerpts that must exist, comma-separated")
    ap.add_argument("--congelado", help="slides that could not change position, e.g.: 5,12")
    args = ap.parse_args()

    zo, zn = zipfile.ZipFile(args.original), zipfile.ZipFile(args.corrigido)
    so, sn = slides(zo), slides(zn)
    problemas = 0

    print("=" * 78)
    print("1 | STRUCTURAL")
    print("=" * 78)
    print(f"  slides: {len(so)} -> {len(sn)}"
          f"{'   DIVERGES' if len(so) != len(sn) else ''}")
    print(f"  package parts: {len(zo.namelist())} -> {len(zn.namelist())}")
    faltando = set(zo.namelist()) - set(zn.namelist())
    if faltando:
        problemas += 1
        print(f"  LOST PARTS: {sorted(faltando)}")

    texto = "".join("".join(x.text or "" for x in ET.fromstring(zn.read(p)).iter(A + "t"))
                    for p in sn)
    if args.proibido:
        resta = [x for x in args.proibido.split(",") if x and x in texto]
        print(f"  leftovers of the errors: {resta or 'none'}")
        problemas += len(resta)
    if args.esperado:
        falta = [x for x in args.esperado.split(",") if x and x not in texto]
        print(f"  expected forms missing: {falta or 'none'}")
        problemas += len(falta)

    # Removing a word leaves the two spaces that surrounded it, and none of the
    # other layers sees that. It compares against the original, not against zero,
    # because a preexisting multiple space is a review finding, not a regression.
    novos = 0
    for k in range(min(len(so), len(sn))):
        a, b = espacos_multiplos(zo, so[k]), espacos_multiplos(zn, sn[k])
        if b > a:
            novos += 1
            problemas += 1
            print(f"  slide {k+1}: multiple spaces {a} -> {b},"
                  f" THE FIX CREATED SPACES THAT DID NOT EXIST")
    if not novos:
        print("  multiple spaces: no slide gained any, the fix created none")

    print("\n" + "=" * 78)
    print("2 | FORMATTING, RUN BY RUN")
    print("=" * 78)
    campos = ["sz", "b", "i", "u", "base", "cor", "fonte", "link"]
    alteradas = 0
    for k in range(min(len(so), len(sn))):
        ro, rn = runs(zo, so[k]), runs(zn, sn[k])
        if len(ro) != len(rn):
            print(f"  slide {k+1}: run count {len(ro)} -> {len(rn)}"
                  f"  (expected if there was an italics split)")
            continue
        for j, (a, b) in enumerate(zip(ro, rn)):
            dif = [c for c in campos if a[c] != b[c]]
            if dif:
                alteradas += 1
                print(f"  slide {k+1:2d} run {j:3d} | {dif} | {a['t'][:34]!r}")
                for c in dif:
                    print(f"        {c}: {a[c]!r} -> {b[c]!r}")
    print(f"  total runs with a changed property: {alteradas}")
    print("  Each one must match a fix you intended.")

    vazios = 0
    for k in range(len(sn)):
        n_vazios = sum(1 for r in runs(zn, sn[k]) if r["t"] == "")
        o_vazios = sum(1 for r in runs(zo, so[k]) if r["t"] == "") if k < len(so) else 0
        if n_vazios > o_vazios:
            vazios += 1
            print(f"  slide {k+1}: {n_vazios} empty runs (original had {o_vazios})")
    if not vazios:
        print("  no new empty run, the replacement left no leftovers")

    print("\n" + "=" * 78)
    print("3 | POSITION AND GEOMETRY")
    print("=" * 78)
    congelados = set()
    if args.congelado:
        congelados = {int(x) for x in args.congelado.split(",")}
    movidas = 0
    for k in range(min(len(so), len(sn))):
        fo, fn = formas(zo, so[k]), formas(zn, sn[k])
        if len(fo) != len(fn):
            problemas += 1
            print(f"  slide {k+1}: SHAPE COUNT {len(fo)} -> {len(fn)}")
            continue
        for a, b in zip(fo, fn):
            for chave, rotulo in (("pos", "position"), ("tam", "size"),
                                  ("fill", "fill"), ("rot", "rotation")):
                if a[chave] != b[chave]:
                    movidas += 1
                    alerta = "  <<< FROZEN SLIDE" if (k + 1) in congelados else ""
                    if alerta:
                        problemas += 1
                    print(f"  slide {k+1:2d} | {a['nome'][:24]:26s} | {rotulo}:"
                          f" {a[chave]} -> {b[chave]}{alerta}")
                    if chave == "pos" and a[chave] and b[chave]:
                        print(f"        in points: "
                              f"({int(a[chave][0])/12700:.1f}, {int(a[chave][1])/12700:.1f})"
                              f" -> ({int(b[chave][0])/12700:.1f}, {int(b[chave][1])/12700:.1f})")
    print(f"  total shapes changed: {movidas}")

    print("\n" + "=" * 78)
    print("4 | LINKS")
    print("=" * 78)
    vivos = mortos = 0
    for i, p in enumerate(sn, 1):
        try:
            rels = {r.get("Id"): r.get("Target")
                    for r in ET.fromstring(zn.read(f"ppt/slides/_rels/slide{i}.xml.rels"))}
        except KeyError:
            rels = {}
        for r in ET.fromstring(zn.read(p)).iter(A + "r"):
            pr = r.find(A + "rPr")
            hl = pr.find(A + "hlinkClick") if pr is not None else None
            if hl is None:
                continue
            rid = hl.get(R + "id")
            t = "".join(x.text or "" for x in r.iter(A + "t"))
            if not rid or rid not in rels:
                mortos += 1
                problemas += 1
                print(f"  DEAD slide {i}: {t[:44]!r} action={hl.get('action')}")
            else:
                vivos += 1
    print(f"  {vivos} resolve, {mortos} dead")

    print("\n" + "=" * 78)
    print(f"VERDICT: {problemas} problem(s) that need attention")
    print("=" * 78)
    print("Run line_count.py next: overflow does not show up in any XML check.")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
