# -*- coding: utf-8 -*-
"""
Geometric check of a .pptx: overlapping objects and elements outside the margin.

Why it exists: visual inspection of a rendered slide is expensive and unreliable. In
decks of 30 or 40 slides, an overlap of a few millimeters goes unnoticed in the image
and shows up on the user's screen. This check compares the object boxes directly in
the file, in seconds, with a precision the eye does not have.

What it does NOT do: it does not see text overflowing inside its own box, contrast,
hierarchy or slide quality. Visual inspection is still needed afterwards.

Usage:
    python check.py deck.pptx
    python check.py deck.pptx --margin 0.4 --include-images
    python check.py deck.pptx --slides 3,7,12-15

Output: one line per finding, plus a summary. Exit code 1 when there are findings,
0 when the deck is clean, so it can be chained into automated verification.

Depends only on python-pptx.
"""

import argparse
import sys

from pptx import Presentation
from pptx.util import Emu

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:  # Python < 3.7
    pass


# The comparison includes the objects that take up visible space: text, table, group
# and filled box. Left out are rule lines, connectors and decorative graphics, which
# exist to run underneath the content. In an org chart the connector crosses boxes all
# the time, and that is correct.
#
# A filled box with no text of its own has to be included: in the common pattern of
# building a card as a colored rectangle with text boxes on top of it, the rectangle is
# what defines the occupied area. Leaving it out hides exactly the table that touches
# the card below, which is the most frequent defect. A rectangle that covers almost the
# whole slide is a section divider background and stays out, otherwise every chapter
# slide becomes a finding.
KIND_TEXT = "TEXT"
KIND_TABLE = "TABLE"
KIND_GROUP = "GROUP"
KIND_PICTURE = "PICTURE"
KIND_BOX = "BOX"

_GROUP = 6      # MSO_SHAPE_TYPE.GROUP
_PICTURE = 13   # MSO_SHAPE_TYPE.PICTURE
_AUTO = 1       # MSO_SHAPE_TYPE.AUTO_SHAPE
BACKGROUND_FRACTION = 0.55   # above this the shape is treated as background, not as a card


def _box(shape):
    """Position and size in inches, or None when the shape does not expose them."""
    try:
        return (
            Emu(shape.left).inches,
            Emu(shape.top).inches,
            Emu(shape.width).inches,
            Emu(shape.height).inches,
        )
    except (TypeError, AttributeError):
        return None


def _group_text(shape, limit=3):
    """Text of a group's children, used only to label the finding."""
    parts = []
    for child in shape.shapes:
        if getattr(child, "shape_type", None) == _GROUP:
            parts.extend(_group_text(child, limit))
        elif getattr(child, "has_text_frame", False):
            t = child.text_frame.text.strip()
            if t:
                parts.append(t)
        if len(parts) >= limit:
            break
    return " | ".join(parts[:limit])


def _has_fill(shape):
    """True when the shape has a solid or gradient fill, and not just an outline."""
    try:
        return shape.fill.type in (1, 3, 4, 5)  # solid, gradient, background, pattern
    except (AttributeError, TypeError, ValueError):
        return False


def collect(slide, include_images=False, width=13.333, height=7.5):
    """Visible objects of the slide, in slide coordinates.

    A group counts as a single box. python-pptx returns the position of the children
    in the group's internal coordinate system, which does not match the slide's when
    the group is scaled or offset. Using the group's own box avoids comparing
    coordinates from different worlds, which is how overlaps get invented.
    """
    slide_area = width * height
    items = []
    for shape in slide.shapes:
        box = _box(shape)
        if box is None:
            continue
        x, y, w, h = box
        shape_type = getattr(shape, "shape_type", None)

        if shape_type == _GROUP:
            label = _group_text(shape)
            if label:
                items.append((x, y, w, h, KIND_GROUP, label[:42]))
        elif getattr(shape, "has_table", False):
            items.append((x, y, w, h, KIND_TABLE, ""))
        elif getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
            items.append((x, y, w, h, KIND_TEXT, shape.text_frame.text.strip()[:42]))
        elif include_images and shape_type == _PICTURE:
            items.append((x, y, w, h, KIND_PICTURE, getattr(shape, "name", "")[:42]))
        elif (shape_type == _AUTO and _has_fill(shape)
              and w * h <= slide_area * BACKGROUND_FRACTION and w > 0.12 and h > 0.12):
            # Card with no text of its own. The minimum width and height discard rule
            # lines and accent bars, which are decoration and do not delimit content.
            items.append((x, y, w, h, KIND_BOX, getattr(shape, "name", "")[:42]))
    return items


def _contains(a, b, tol=0.03):
    """True when box `a` contains box `b`. Text inside a card is nesting, not
    overlap, and has to be told apart from an object that crosses the border."""
    xa, ya, wa, ha = a[:4]
    xb, yb, wb, hb = b[:4]
    return (xb >= xa - tol and yb >= ya - tol
            and xb + wb <= xa + wa + tol and yb + hb <= ya + ha + tol)


def overlaps(items, slack, min_area):
    """Pairs that cross each other beyond the slack. `slack` absorbs intentional contact."""
    findings = []
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            ia, ib = items[a], items[b]
            if _contains(ia, ib) or _contains(ib, ia):
                continue
            xa, ya, wa, ha, ta, na = ia
            xb, yb, wb, hb, tb, nb = ib
            ox = min(xa + wa, xb + wb) - max(xa, xb)
            oy = min(ya + ha, yb + hb) - max(ya, yb)
            if ox > slack and oy > slack and ox * oy > min_area:
                findings.append((ox * oy, ta, na, tb, nb))
    return findings


def outside_margin(items, width, height, margin, tolerance):
    findings = []
    for x, y, w, h, kind, name in items:
        sides = []
        if x < margin - tolerance:
            sides.append(f"left ({x:.2f})")
        if y < margin - tolerance:
            sides.append(f"top ({y:.2f})")
        if x + w > width - margin + tolerance:
            sides.append(f"right ({x + w:.2f} of {width:.2f})")
        if y + h > height - margin + tolerance:
            sides.append(f"bottom ({y + h:.2f} of {height:.2f})")
        if sides:
            findings.append((kind, name, ", ".join(sides)))
    return findings


def _parse_slides(spec):
    """'3,7,12-15' -> {3, 7, 12, 13, 14, 15}. None when not provided."""
    if not spec:
        return None
    target = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            target.update(range(int(start), int(end) + 1))
        elif part:
            target.add(int(part))
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("file", help="path to the .pptx")
    ap.add_argument(
        "--margin",
        type=float,
        default=0.0,
        help="required margin in inches. 0 (default) flags only what goes off the slide; "
        "use the grid's real value to require breathing room, for example 0.4",
    )
    ap.add_argument(
        "--slack",
        type=float,
        default=0.05,
        help="overlap tolerated on each axis, in inches (default 0.05). Absorbs "
        "objects placed in contact on purpose and EMU rounding",
    )
    ap.add_argument(
        "--min-area",
        type=float,
        default=0.05,
        help="minimum overlap area for a finding, in square inches (default 0.05)",
    )
    ap.add_argument(
        "--include-images",
        action="store_true",
        help="includes images in the comparison. Off by default because background "
        "photos and corner graphics produce findings that are not defects",
    )
    ap.add_argument("--slides", help="restricts the check to these slides, e.g. 3,7,12-15")
    args = ap.parse_args()

    prs = Presentation(args.file)
    width = Emu(prs.slide_width).inches
    height = Emu(prs.slide_height).inches
    target = _parse_slides(args.slides)

    n_overlaps = 0
    n_outside = 0

    for i, slide in enumerate(prs.slides, 1):
        if target and i not in target:
            continue
        items = collect(slide, include_images=args.include_images,
                        width=width, height=height)

        for area, ta, na, tb, nb in overlaps(items, args.slack, args.min_area):
            n_overlaps += 1
            print(f"slide {i:>3}  overlaps  {area:.2f} in2  [{ta}] {na!r} x [{tb}] {nb!r}")

        for kind, name, sides in outside_margin(items, width, height, args.margin, 0.02):
            n_outside += 1
            print(f"slide {i:>3}  outside   [{kind}] {name!r} -> {sides}")

    scope = f"{len(target)} slides" if target else f"{len(prs.slides)} slides"
    print(
        f"\n{scope}, slide size {width:.2f} x {height:.2f} in, required margin "
        f"{args.margin:.2f} in"
    )
    print(f"overlaps: {n_overlaps}   outside margin: {n_outside}")

    return 1 if (n_overlaps or n_outside) else 0


if __name__ == "__main__":
    sys.exit(main())
