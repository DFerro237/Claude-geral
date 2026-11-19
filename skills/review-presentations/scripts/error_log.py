#!/usr/bin/env python3
"""Generates the review spreadsheet, three tabs, in the format the project already uses.

Usage:
    python error_log.py --config achados.json --saida "YYYY.MM.DD_Errors found by Claude in v15.xlsx"

Format of achados.json (the keys are read by this script; keep them as they are):

{
  "versao": "v15",
  "cor_cabecalho": "404040",
  "corrigido_em": "v15_Claude review",
  "erros": [
    {"id": "G01", "slide": 11, "categoria": "Grammar and spelling",
     "item": "Typo in the timeline label", "esta": "Estimated tiem",
     "deveria": "Estimated time", "prioridade": "High",
     "observacao": "The other three cards already spelled it right."}
  ],
  "nao_corrigidos": [
    {"id": "A01", "slide": 5, "categoria": "Alignment and grid",
     "item": "Title off the standard", "prioridade": "-",
     "motivo": "Decisão do usuário", "detalhe": "Frozen slide."}
  ],
  "padroes": [
    {"dimensao": "Term", "elemento": "pro rata", "padrao": "italics, no hyphen",
     "observacao": ""}
  ]
}

Keys: versao = deck version, cor_cabecalho = header color, corrigido_em = version
where the fixes went in, erros = errors, nao_corrigidos = not fixed, padroes =
standards; per row: esta = current, deveria = should be, prioridade = priority,
observacao = note, motivo = reason, detalhe = detail, dimensao = dimension,
elemento = element, padrao = standard.

`motivo` must be one of the values in MOTIVOS below (see references/error-log.md for
their meaning); any other value triggers a warning.

`cor_cabecalho` is the hex of the tabs' header color, without #. Give the main color of
the client's brand skill, when there is one, so the spreadsheet comes out in their
identity; without it, the neutral gray 404040 stays.

`slide` accepts a number or text such as "5; 8; 10". `corrigido_em` fills the Fixed
column of every error, and should only be given after verification has passed: the
column records what was checked in the file, not the intention.
"""
import argparse, json, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# Reason taxonomy for the not-fixed tab. Meanings, in order: user decision; breaks
# layout/design; not an error (reclassified); doubt; pending decision; high risk / low
# benefit.
MOTIVOS = {
    "Decisão do usuário",
    "Desconfigura layout/design",
    "Não é erro (reclassificado)",
    "Dúvida",
    "Decisão pendente",
    "Risco alto / benefício baixo",
}

CABECALHO = Font(bold=True, color="FFFFFF")
FUNDO_PADRAO = "404040"   # neutral gray; the client's color comes from cor_cabecalho


def aba(ws, colunas, linhas, larguras, fundo):
    ws.append(colunas)
    for c in range(1, len(colunas) + 1):
        cel = ws.cell(1, c)
        cel.font = CABECALHO
        cel.fill = PatternFill("solid", fgColor=fundo)
        cel.alignment = Alignment(vertical="center")
    for l in linhas:
        ws.append(list(l))
    for i, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for linha in ws.iter_rows(min_row=2):
        for cel in linha:
            cel.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A2"
    if ws.max_row > 1:
        ws.auto_filter.ref = ws.dimensions


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf8"))
    versao = cfg.get("versao", "")
    marca = cfg.get("corrigido_em", "")
    corrigido = f"Yes ({marca})" if marca else ""
    fundo = str(cfg.get("cor_cabecalho") or FUNDO_PADRAO).lstrip("#")

    erros = cfg.get("erros", [])
    nao = cfg.get("nao_corrigidos", [])
    padroes = cfg.get("padroes", [])

    # --- validations that prevent an inconsistent spreadsheet ---
    ids = [e["id"] for e in erros] + [n["id"] for n in nao]
    repetidos = {i for i in ids if ids.count(i) > 1}
    if repetidos:
        sys.exit(f"Repeated IDs across the tabs: {sorted(repetidos)}")
    invalidos = {n.get("motivo") for n in nao} - MOTIVOS
    if invalidos:
        print(f"WARNING: reasons outside the taxonomy: {sorted(invalidos)}", file=sys.stderr)
        print(f"         expected: {sorted(MOTIVOS)}", file=sys.stderr)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Errors {versao}".strip()
    aba(ws,
        ["ID", "Slide", "Category", "Item", "Current", "Should be",
         "Priority", "Fixed", "Note"],
        [(e["id"], e.get("slide", ""), e.get("categoria", ""), e.get("item", ""),
          e.get("esta", ""), e.get("deveria", ""), e.get("prioridade", ""),
          corrigido, e.get("observacao", "")) for e in erros],
        [8, 12, 22, 38, 42, 42, 11, 24, 52], fundo)

    aba(wb.create_sheet("Not fixed"),
        ["ID", "Slide", "Category", "Item", "Priority", "Reason", "Detail"],
        [(n["id"], n.get("slide", ""), n.get("categoria", ""), n.get("item", ""),
          n.get("prioridade", "-"), n.get("motivo", ""), n.get("detalhe", ""))
         for n in nao],
        [8, 16, 22, 44, 11, 28, 70], fundo)

    aba(wb.create_sheet("Standards"),
        ["Dimension", "Element", "Standard", "Note"],
        [(p.get("dimensao", ""), p.get("elemento", ""), p.get("padrao", ""),
          p.get("observacao", "")) for p in padroes],
        [14, 30, 44, 64], fundo)

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(saida)
    print(f"saved: {saida}")
    print(f"  Errors {versao}: {len(erros)} | Not fixed: {len(nao)} | Standards: {len(padroes)}")
    print(f"  Unique IDs: {len(set(ids))} of {len(ids)}")
    if not padroes:
        print("  WARNING: Standards tab is empty. It is the asset that outlives the review,")
        print("           and it is what keeps the next one from raising the same false positives.")


if __name__ == "__main__":
    main()
