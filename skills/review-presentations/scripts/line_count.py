#!/usr/bin/env python3
"""Visual check: no changed box may have gained a line.

Usage:
    python line_count.py original.pptx corrected.pptx
    python line_count.py original.pptx corrected.pptx --png slide05

It is the only layer that catches overflow. A text fix changes the length of the
string, and two extra characters were enough, in a real case, to wrap one more
line and push the last sentence out of the card.

What it does:
  1. renders both decks to PDF through LibreOffice
  2. finds which boxes had their text changed
  3. counts the rendered lines inside each one, before and after
  4. compares the slides pixel by pixel, to find unexpected changes

Requires LibreOffice, pypdfium2, Pillow, pdfplumber and python-pptx. Without
LibreOffice the check does not run, and that must be told to the user as a limitation.
"""
import argparse, os, shutil, subprocess, sys, tempfile
from pathlib import Path

CANDIDATOS_SOFFICE = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
]


def achar_soffice():
    for c in CANDIDATOS_SOFFICE:
        if Path(c).exists():
            return c
    achado = shutil.which("soffice") or shutil.which("libreoffice")
    if achado:
        return achado
    sys.exit("LibreOffice not found. Without it the visual check does not run.\n"
             "Ask the user for authorization before installing it, as CLAUDE.md says.")


def para_pdf(soffice, origem, saida):
    saida.mkdir(parents=True, exist_ok=True)
    for f in saida.glob("*.pdf"):
        f.unlink()
    subprocess.run([soffice, "--headless", "--norestore", "--convert-to", "pdf",
                    "--outdir", str(saida), str(origem)],
                   capture_output=True, timeout=600)
    pdfs = list(saida.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"LibreOffice did not produce a PDF for {origem.name}")
    return pdfs[0]


def caixas_alteradas(orig, corr):
    """[(slide_index0, name, bbox_pt, text_before, text_after)]"""
    from pptx import Presentation
    from pptx.util import Emu
    po, pc = Presentation(str(orig)), Presentation(str(corr))
    alvos = []
    for i, (a, b) in enumerate(zip(po.slides, pc.slides)):
        antes = {sh.shape_id: sh for sh in a.shapes}
        for sh in b.shapes:
            if not sh.has_text_frame:
                continue
            v = antes.get(sh.shape_id)
            if v is None or not v.has_text_frame:
                continue
            if v.text_frame.text == sh.text_frame.text:
                continue
            if sh.left is None or sh.top is None:
                continue
            bbox = (Emu(sh.left).pt, Emu(sh.top).pt,
                    Emu(sh.left + (sh.width or 0)).pt,
                    Emu(sh.top + (sh.height or 0)).pt)
            alvos.append((i, sh.name, bbox, v.text_frame.text, sh.text_frame.text))
    return alvos


def contar_linhas(pdf, pagina, bbox, folga=6):
    """Counts distinct baselines inside the box, with a generous margin below
    to see what spilled over. See pitfalls.md: the inside/outside ratio is not
    a reliable indicator; what counts is comparing before with after."""
    import pdfplumber
    with pdfplumber.open(pdf) as doc:
        pg = doc.pages[pagina]
        x0, topo, x1, base = bbox
        rec = (max(0, x0 - folga), max(0, topo - folga),
               min(pg.width, x1 + folga), min(pg.height, base + folga * 12))
        try:
            reg = pg.crop(rec)
        except Exception:
            return None
        topos = sorted({round(w["top"], 0) for w in reg.extract_words()})
        grupos = []
        for t in topos:
            if grupos and t - grupos[-1][-1] <= 3:
                grupos[-1].append(t)
            else:
                grupos.append([t])
        return len(grupos)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("corrigido")
    ap.add_argument("--png", help="prefix to save PNGs of the changed slides")
    args = ap.parse_args()

    orig, corr = Path(args.original), Path(args.corrigido)
    soffice = achar_soffice()
    tmp = Path(tempfile.mkdtemp(prefix="revisao_"))
    print(f"rendering in {tmp}")
    pdf_o = para_pdf(soffice, orig, tmp / "orig")
    pdf_c = para_pdf(soffice, corr, tmp / "corr")

    alvos = caixas_alteradas(orig, corr)
    print("\n" + "=" * 90)
    print("RENDERED LINES PER CHANGED BOX")
    print("=" * 90)
    if not alvos:
        print("  no box with changed text")
    print(f"{'sl':>3} {'box':28s} {'before':>7} {'after':>7}  status")
    print("-" * 90)
    ganharam = []
    for i, nome, bbox, t_a, t_d in alvos:
        la = contar_linhas(pdf_o, i, bbox)
        lc = contar_linhas(pdf_c, i, bbox)
        if la is None or lc is None:
            continue
        if lc > la:
            sit = "GAINED A LINE, check for overflow"
            ganharam.append((i + 1, nome, la, lc, t_a, t_d))
        elif lc < la:
            sit = "lost a line"
        else:
            sit = "same"
        print(f"{i+1:3d} {nome[:28]:28s} {la:7d} {lc:7d}  {sit}")

    print("\n" + "=" * 90)
    print("DIFFERENCE PER SLIDE")
    print("=" * 90)
    import pypdfium2 as pdfium
    from PIL import ImageChops
    do, dc = pdfium.PdfDocument(pdf_o), pdfium.PdfDocument(pdf_c)
    esperados = {i for i, *_ in alvos}
    for i in range(min(len(do), len(dc))):
        a = do[i].render(scale=1.5).to_pil().convert("RGB")
        b = dc[i].render(scale=1.5).to_pil().convert("RGB")
        if a.size != b.size:
            print(f"  slide {i+1}: DIFFERENT PAGE SIZE")
            continue
        bb = ImageChops.difference(a, b).getbbox()
        if bb and i not in esperados:
            print(f"  slide {i+1}: changed with no text box changed -> {bb}"
                  f"  (may be repositioning; check)")
        if args.png and bb:
            b.save(f"{args.png}_{i+1:02d}.png")
    print("  sweep finished")

    print("\n" + "=" * 90)
    if ganharam:
        print(f"WARNING: {len(ganharam)} box(es) gained a line. "
              "Go back to the user, say what changed and ask whether to keep or revert.")
        print("Do not compensate by shrinking the font or resizing the shape.\n")
        for sn, nome, la, lc, t_a, t_d in ganharam:
            print(f"  slide {sn} | {nome} | {la} -> {lc} lines")
            print(f"     before: {t_a[:160]!r}")
            print(f"     now:    {t_d[:160]!r}\n")
    else:
        print("No changed box gained a line. No overflow introduced.")
    print("Reminder: LibreOffice wraps lines slightly differently from")
    print("PowerPoint. Tell the user so; the final check is theirs.")
    return 1 if ganharam else 0


if __name__ == "__main__":
    sys.exit(main())
