#!/usr/bin/env python3
"""Compare the original deck with the corrected one and report collateral damage.

Usage:
    python verify.py original.pptx corrected.pptx
    python verify.py original.pptx corrected.pptx --forbidden "Tiem,US$400,Appendix I - "
    python verify.py original.pptx corrected.pptx --expected "Time,US$ 400"
    python verify.py original.pptx corrected.pptx --frozen 5

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


RE_SPACES = re.compile("[ \u00a0\u2007\u202f]{2,}")


def slides(z):
    return sorted((n for n in z.namelist()
                   if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                  key=lambda s: int(re.findall(r"\d+", s)[0]))


def multiple_spaces(z, path):
    """Count runs of 2 or more spaces, paragraph by paragraph.

    By paragraph, and not over the concatenated slide text: joining the text
    of different shapes invents double spaces that do not exist in the file.
    """
    total = 0
    for par in ET.fromstring(z.read(path)).iter(A + "p"):
        t = "".join(x.text or "" for x in par.iter(A + "t")).strip()
        total += len(RE_SPACES.findall(t))
    return total


def runs(z, path):
    out = []
    for r in ET.fromstring(z.read(path)).iter(A + "r"):
        t = "".join(x.text or "" for x in r.iter(A + "t"))
        pr = r.find(A + "rPr")
        g = (lambda k: pr.get(k)) if pr is not None else (lambda k: None)
        color = None
        if pr is not None:
            sf = pr.find(A + "solidFill")
            if sf is not None:
                c = sf.find(A + "srgbClr")
                color = c.get("val") if c is not None else "theme"
        lat = pr.find(A + "latin") if pr is not None else None
        out.append(dict(
            t=t, sz=g("sz"), b=g("b"), i=g("i"), u=g("u"), base=g("baseline"),
            color=color, font=lat.get("typeface") if lat is not None else None,
            link=pr is not None and pr.find(A + "hlinkClick") is not None,
        ))
    return out


def shapes(z, path):
    out = []
    for sp in ET.fromstring(z.read(path)).iter(P + "sp"):
        cnv = sp.find(f".//{P}cNvPr")
        xfrm = sp.find(f".//{P}spPr/{A}xfrm")
        off = xfrm.find(A + "off") if xfrm is not None else None
        ext = xfrm.find(A + "ext") if xfrm is not None else None
        fill_el = sp.find(f".//{P}spPr/{A}solidFill")
        color = None
        if fill_el is not None:
            c = fill_el.find(A + "srgbClr")
            color = c.get("val") if c is not None else "theme"
        out.append(dict(
            id=cnv.get("id") if cnv is not None else "?",
            name=cnv.get("name") if cnv is not None else "?",
            pos=(off.get("x"), off.get("y")) if off is not None else None,
            size=(ext.get("cx"), ext.get("cy")) if ext is not None else None,
            fill=color, rot=xfrm.get("rot") if xfrm is not None else None,
            text="".join(x.text or "" for x in sp.iter(A + "t")).strip()[:40],
        ))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("corrected")
    ap.add_argument("--forbidden", help="pieces of text that must no longer exist, comma-separated")
    ap.add_argument("--expected", help="pieces of text that must exist, comma-separated")
    ap.add_argument("--frozen", help="slides that could not change position, e.g. 5,12")
    args = ap.parse_args()

    zo, zn = zipfile.ZipFile(args.original), zipfile.ZipFile(args.corrected)
    so, sn = slides(zo), slides(zn)
    problems = 0

    print("=" * 78)
    print("1 | STRUCTURAL")
    print("=" * 78)
    print(f"  slides: {len(so)} -> {len(sn)}"
          f"{'   DIFFERS' if len(so) != len(sn) else ''}")
    print(f"  package parts: {len(zo.namelist())} -> {len(zn.namelist())}")
    missing = set(zo.namelist()) - set(zn.namelist())
    if missing:
        problems += 1
        print(f"  LOST PARTS: {sorted(missing)}")

    text = "".join("".join(x.text or "" for x in ET.fromstring(zn.read(p)).iter(A + "t"))
                   for p in sn)
    if args.forbidden:
        left = [x for x in args.forbidden.split(",") if x and x in text]
        print(f"  leftovers of the errors: {left or 'none'}")
        problems += len(left)
    if args.expected:
        absent = [x for x in args.expected.split(",") if x and x not in text]
        print(f"  expected forms missing: {absent or 'none'}")
        problems += len(absent)

    # Removing a word leaves behind the two spaces around it, and none of the
    # other layers sees that. Compare against the original, not against zero,
    # because pre-existing multiple spaces are a review finding, not a regression.
    new_spaces = 0
    for k in range(min(len(so), len(sn))):
        a, b = multiple_spaces(zo, so[k]), multiple_spaces(zn, sn[k])
        if b > a:
            new_spaces += 1
            problems += 1
            print(f"  slide {k+1}: multiple spaces {a} -> {b},"
                  f" THE CORRECTION CREATED SPACES THAT DID NOT EXIST")
    if not new_spaces:
        print("  multiple spaces: no slide gained any, the correction created none")

    print("\n" + "=" * 78)
    print("2 | FORMATTING, RUN BY RUN")
    print("=" * 78)
    fields = ["sz", "b", "i", "u", "base", "color", "font", "link"]
    changed = 0
    for k in range(min(len(so), len(sn))):
        ro, rn = runs(zo, so[k]), runs(zn, sn[k])
        if len(ro) != len(rn):
            print(f"  slide {k+1}: run count {len(ro)} -> {len(rn)}"
                  f"  (expected if an italic split happened)")
            continue
        for j, (a, b) in enumerate(zip(ro, rn)):
            diff = [c for c in fields if a[c] != b[c]]
            if diff:
                changed += 1
                print(f"  slide {k+1:2d} run {j:3d} | {diff} | {a['t'][:34]!r}")
                for c in diff:
                    print(f"        {c}: {a[c]!r} -> {b[c]!r}")
    print(f"  total runs with a changed property: {changed}")
    print("  Each one must match a correction you intended.")

    empty = 0
    for k in range(len(sn)):
        n_empty = sum(1 for r in runs(zn, sn[k]) if r["t"] == "")
        o_empty = sum(1 for r in runs(zo, so[k]) if r["t"] == "") if k < len(so) else 0
        if n_empty > o_empty:
            empty += 1
            print(f"  slide {k+1}: {n_empty} empty runs (the original had {o_empty})")
    if not empty:
        print("  no new empty run, the replacement left no leftovers")

    print("\n" + "=" * 78)
    print("3 | POSITION AND GEOMETRY")
    print("=" * 78)
    frozen = set()
    if args.frozen:
        frozen = {int(x) for x in args.frozen.split(",")}
    moved = 0
    for k in range(min(len(so), len(sn))):
        fo, fn = shapes(zo, so[k]), shapes(zn, sn[k])
        if len(fo) != len(fn):
            problems += 1
            print(f"  slide {k+1}: SHAPE COUNT {len(fo)} -> {len(fn)}")
            continue
        for a, b in zip(fo, fn):
            for key, label in (("pos", "position"), ("size", "size"),
                               ("fill", "fill"), ("rot", "rotation")):
                if a[key] != b[key]:
                    moved += 1
                    alert = "  <<< FROZEN SLIDE" if (k + 1) in frozen else ""
                    if alert:
                        problems += 1
                    print(f"  slide {k+1:2d} | {a['name'][:24]:26s} | {label}:"
                          f" {a[key]} -> {b[key]}{alert}")
                    if key == "pos" and a[key] and b[key]:
                        print(f"        in points: "
                              f"({int(a[key][0])/12700:.1f}, {int(a[key][1])/12700:.1f})"
                              f" -> ({int(b[key][0])/12700:.1f}, {int(b[key][1])/12700:.1f})")
    print(f"  total shapes changed: {moved}")

    print("\n" + "=" * 78)
    print("4 | LINKS")
    print("=" * 78)
    alive = dead = 0
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
                dead += 1
                problems += 1
                print(f"  DEAD slide {i}: {t[:44]!r} action={hl.get('action')}")
            else:
                alive += 1
    print(f"  {alive} resolve, {dead} dead")

    print("\n" + "=" * 78)
    print(f"VERDICT: {problems} problem(s) that need attention")
    print("=" * 78)
    print("Run line_count.py next: overflow does not show up in any XML check.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
