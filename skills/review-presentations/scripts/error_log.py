#!/usr/bin/env python3
"""Build the review spreadsheet, three sheets, in the format the project already uses.

Usage:
    python error_log.py --config findings.json --output "YYYY.MM.DD_Review findings V15.xlsx"

Format of findings.json:

{
  "version": "V15",
  "header_color": "404040",
  "fixed_in": "V15_Claude review",
  "errors": [
    {"id": "G01", "slide": 11, "category": "Spelling and typing",
     "item": "Typo in the timeline label", "current": "Estimated tiem",
     "should_be": "Estimated time", "priority": "High",
     "note": "The other three cards already spelled it right."}
  ],
  "not_fixed": [
    {"id": "A01", "slide": 5, "category": "Alignment and grid",
     "item": "Title off the standard", "priority": "-",
     "reason": "User decision", "detail": "Frozen slide."}
  ],
  "standards": [
    {"dimension": "Term", "element": "pro rata", "standard": "italics, no hyphen",
     "note": ""}
  ]
}

`header_color` is the hex color of the sheet headers, without #. Use the main
color of the client's brand skill, when there is one, so the spreadsheet comes
out in the client's identity; without it, the neutral gray 404040 is used.

`slide` accepts a number or text such as "5; 8; 10". `fixed_in` fills the
Fixed column of every error, and should only be set after the verification
has passed: the column records what was checked in the file, not the intention.
"""
import argparse, json, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

REASONS = {
    "User decision",
    "Breaks layout/design",
    "Not an error (reclassified)",
    "Open question",
    "Pending decision",
    "High risk / low benefit",
}

HEADER = Font(bold=True, color="FFFFFF")
DEFAULT_FILL = "404040"   # neutral gray; the client's color comes from header_color


def sheet(ws, columns, rows, widths, fill):
    ws.append(columns)
    for c in range(1, len(columns) + 1):
        cell = ws.cell(1, c)
        cell.font = HEADER
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(vertical="center")
    for r in rows:
        ws.append(list(r))
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A2"
    if ws.max_row > 1:
        ws.auto_filter.ref = ws.dimensions


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf8"))
    version = cfg.get("version", "")
    mark = cfg.get("fixed_in", "")
    fixed = f"Yes ({mark})" if mark else ""
    fill = str(cfg.get("header_color") or DEFAULT_FILL).lstrip("#")

    errors = cfg.get("errors", [])
    not_fixed = cfg.get("not_fixed", [])
    standards = cfg.get("standards", [])

    # --- checks that prevent an inconsistent spreadsheet ---
    ids = [e["id"] for e in errors] + [n["id"] for n in not_fixed]
    repeated = {i for i in ids if ids.count(i) > 1}
    if repeated:
        sys.exit(f"IDs repeated across sheets: {sorted(repeated)}")
    invalid = {n.get("reason") for n in not_fixed} - REASONS
    if invalid:
        print(f"WARNING: reasons outside the taxonomy: {sorted(invalid)}", file=sys.stderr)
        print(f"         expected: {sorted(REASONS)}", file=sys.stderr)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Errors {version}".strip()
    sheet(ws,
          ["ID", "Slide", "Category", "Item", "Current", "Should be",
           "Priority", "Fixed", "Note"],
          [(e["id"], e.get("slide", ""), e.get("category", ""), e.get("item", ""),
            e.get("current", ""), e.get("should_be", ""), e.get("priority", ""),
            fixed, e.get("note", "")) for e in errors],
          [8, 12, 22, 38, 42, 42, 11, 24, 52], fill)

    sheet(wb.create_sheet("Not fixed"),
          ["ID", "Slide", "Category", "Item", "Priority", "Reason", "Detail"],
          [(n["id"], n.get("slide", ""), n.get("category", ""), n.get("item", ""),
            n.get("priority", "-"), n.get("reason", ""), n.get("detail", ""))
           for n in not_fixed],
          [8, 16, 22, 44, 11, 28, 70], fill)

    sheet(wb.create_sheet("Standards"),
          ["Dimension", "Element", "Standard", "Note"],
          [(p.get("dimension", ""), p.get("element", ""), p.get("standard", ""),
            p.get("note", "")) for p in standards],
          [14, 30, 44, 64], fill)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"saved: {out}")
    print(f"  Errors {version}: {len(errors)} | Not fixed: {len(not_fixed)} | Standards: {len(standards)}")
    print(f"  Unique IDs: {len(set(ids))} of {len(ids)}")
    if not standards:
        print("  WARNING: the Standards sheet is empty. It is the asset that outlives the review,")
        print("           and it keeps the next review from raising the same false positives.")


if __name__ == "__main__":
    main()
