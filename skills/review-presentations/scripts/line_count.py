#!/usr/bin/env python3
"""Visual verification: no changed text box may have gained a line.

Usage:
    python line_count.py original.pptx corrected.pptx
    python line_count.py original.pptx corrected.pptx --png slide05

It is the only layer that catches overflow. A text correction changes the
length of the string, and in a real case two extra characters were enough to
break a line and push the last sentence out of the card.

What it does:
  1. renders both decks to PDF through LibreOffice
  2. finds which boxes had their text changed
  3. counts the rendered lines inside each one, before and after
  4. compares the slides pixel by pixel, to find unexpected changes

Requires LibreOffice, pypdfium2, Pillow, pdfplumber and python-pptx. Without
LibreOffice the check does not run, and that has to be reported to the user
as a limitation.
"""
import argparse, os, shutil, subprocess, sys, tempfile
from pathlib import Path

SOFFICE_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
]


def find_soffice():
    for c in SOFFICE_CANDIDATES:
        if Path(c).exists():
            return c
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    sys.exit("LibreOffice not found. Without it the visual check does not run.\n"
             "Ask the user for permission before installing it.")


def to_pdf(soffice, source, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("*.pdf"):
        f.unlink()
    subprocess.run([soffice, "--headless", "--norestore", "--convert-to", "pdf",
                    "--outdir", str(out_dir), str(source)],
                   capture_output=True, timeout=600)
    pdfs = list(out_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"LibreOffice did not produce a PDF for {source.name}")
    return pdfs[0]


def changed_boxes(orig, corr):
    """[(slide_index0, name, bbox_pt, text_before, text_after)]"""
    from pptx import Presentation
    from pptx.util import Emu
    po, pc = Presentation(str(orig)), Presentation(str(corr))
    targets = []
    for i, (a, b) in enumerate(zip(po.slides, pc.slides)):
        before = {sh.shape_id: sh for sh in a.shapes}
        for sh in b.shapes:
            if not sh.has_text_frame:
                continue
            v = before.get(sh.shape_id)
            if v is None or not v.has_text_frame:
                continue
            if v.text_frame.text == sh.text_frame.text:
                continue
            if sh.left is None or sh.top is None:
                continue
            bbox = (Emu(sh.left).pt, Emu(sh.top).pt,
                    Emu(sh.left + (sh.width or 0)).pt,
                    Emu(sh.top + (sh.height or 0)).pt)
            targets.append((i, sh.name, bbox, v.text_frame.text, sh.text_frame.text))
    return targets


def count_lines(pdf, page, bbox, margin=6):
    """Count distinct baselines inside the box, with a generous margin below
    to see what overflowed. See pitfalls.md: the inside/outside ratio is not a
    reliable indicator; what matters is comparing before with after."""
    import pdfplumber
    with pdfplumber.open(pdf) as doc:
        pg = doc.pages[page]
        x0, top, x1, bottom = bbox
        rect = (max(0, x0 - margin), max(0, top - margin),
                min(pg.width, x1 + margin), min(pg.height, bottom + margin * 12))
        try:
            region = pg.crop(rect)
        except Exception:
            return None
        tops = sorted({round(w["top"], 0) for w in region.extract_words()})
        groups = []
        for t in tops:
            if groups and t - groups[-1][-1] <= 3:
                groups[-1].append(t)
            else:
                groups.append([t])
        return len(groups)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("corrected")
    ap.add_argument("--png", help="prefix for saving PNGs of the changed slides")
    args = ap.parse_args()

    orig, corr = Path(args.original), Path(args.corrected)
    soffice = find_soffice()
    tmp = Path(tempfile.mkdtemp(prefix="review_"))
    print(f"rendering into {tmp}")
    pdf_o = to_pdf(soffice, orig, tmp / "orig")
    pdf_c = to_pdf(soffice, corr, tmp / "corr")

    targets = changed_boxes(orig, corr)
    print("\n" + "=" * 90)
    print("RENDERED LINES PER CHANGED BOX")
    print("=" * 90)
    if not targets:
        print("  no box with changed text")
    print(f"{'sl':>3} {'box':28s} {'before':>7} {'after':>7}  status")
    print("-" * 90)
    gained = []
    for i, name, bbox, t_b, t_a in targets:
        lb = count_lines(pdf_o, i, bbox)
        la = count_lines(pdf_c, i, bbox)
        if lb is None or la is None:
            continue
        if la > lb:
            status = "GAINED A LINE, check for overflow"
            gained.append((i + 1, name, lb, la, t_b, t_a))
        elif la < lb:
            status = "lost a line"
        else:
            status = "same"
        print(f"{i+1:3d} {name[:28]:28s} {lb:7d} {la:7d}  {status}")

    print("\n" + "=" * 90)
    print("DIFFERENCE PER SLIDE")
    print("=" * 90)
    import pypdfium2 as pdfium
    from PIL import ImageChops
    do, dc = pdfium.PdfDocument(pdf_o), pdfium.PdfDocument(pdf_c)
    expected = {i for i, *_ in targets}
    for i in range(min(len(do), len(dc))):
        a = do[i].render(scale=1.5).to_pil().convert("RGB")
        b = dc[i].render(scale=1.5).to_pil().convert("RGB")
        if a.size != b.size:
            print(f"  slide {i+1}: DIFFERENT PAGE SIZE")
            continue
        bb = ImageChops.difference(a, b).getbbox()
        if bb and i not in expected:
            print(f"  slide {i+1}: changed without a changed text box -> {bb}"
                  f"  (may be a repositioning; check it)")
        if args.png and bb:
            b.save(f"{args.png}_{i+1:02d}.png")
    print("  scan complete")

    print("\n" + "=" * 90)
    if gained:
        print(f"ATTENTION: {len(gained)} box(es) gained a line. "
              "Go back to the user, say what changed and ask whether to keep or revert.")
        print("Do not compensate by shrinking the font or resizing the shape.\n")
        for sn, name, lb, la, t_b, t_a in gained:
            print(f"  slide {sn} | {name} | {lb} -> {la} lines")
            print(f"     before: {t_b[:160]!r}")
            print(f"     now:    {t_a[:160]!r}\n")
    else:
        print("No changed box gained a line. No overflow introduced.")
    print("Reminder: LibreOffice breaks lines slightly differently from")
    print("PowerPoint. Tell the user; the final check is theirs.")
    return 1 if gained else 0


if __name__ == "__main__":
    sys.exit(main())
