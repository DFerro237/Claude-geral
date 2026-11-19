# -*- coding: utf-8 -*-
"""
Geometric check of a .pptx: overlapping objects and elements outside the margin.

Why it exists: visual inspection of a rendered slide is expensive and fails. In
decks of 30 or 40 slides, an overlap of a few millimeters goes unnoticed in the image
and shows up on the user's screen. This check compares the object boxes directly in
the file, in seconds, with a precision the eye does not have.

What it does NOT do: it does not see text overflowing inside its own box, contrast,
hierarchy or slide quality. Visual inspection is still needed afterwards.

Usage:
    python check.py deck.pptx
    python check.py deck.pptx --margem 0.4 --com-imagens
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
TIPO_TEXTO = "TEXT"
TIPO_TABELA = "TABLE"
TIPO_GRUPO = "GROUP"
TIPO_IMAGEM = "PICTURE"
TIPO_CAIXA = "BOX"

_GRUPO = 6      # MSO_SHAPE_TYPE.GROUP
_IMAGEM = 13    # MSO_SHAPE_TYPE.PICTURE
_AUTO = 1       # MSO_SHAPE_TYPE.AUTO_SHAPE
FRACAO_FUNDO = 0.55   # above this the shape is treated as background, not as a card


def _caixa(shape):
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


def _texto_do_grupo(shape, limite=3):
    """Text of a group's children, only to label the finding."""
    partes = []
    for filho in shape.shapes:
        if getattr(filho, "shape_type", None) == _GRUPO:
            partes.extend(_texto_do_grupo(filho, limite))
        elif getattr(filho, "has_text_frame", False):
            t = filho.text_frame.text.strip()
            if t:
                partes.append(t)
        if len(partes) >= limite:
            break
    return " | ".join(partes[:limite])


def _tem_preenchimento(shape):
    """True when the shape has a solid or gradient fill, and not only an outline."""
    try:
        return shape.fill.type in (1, 3, 4, 5)  # solid, gradient, background, pattern
    except (AttributeError, TypeError, ValueError):
        return False


def coletar(slide, com_imagens=False, largura=13.333, altura=7.5):
    """Visible objects of the slide, in slide coordinates.

    A group counts as a single box. python-pptx returns the children's position in
    the group's internal coordinate system, which does not match the slide's when the
    group has scaling or an offset. Using the box of the group itself avoids comparing
    coordinates from different worlds, which is how overlaps get invented.
    """
    area_slide = largura * altura
    itens = []
    for shape in slide.shapes:
        caixa = _caixa(shape)
        if caixa is None:
            continue
        x, y, w, h = caixa
        tipo_forma = getattr(shape, "shape_type", None)

        if tipo_forma == _GRUPO:
            rotulo = _texto_do_grupo(shape)
            if rotulo:
                itens.append((x, y, w, h, TIPO_GRUPO, rotulo[:42]))
        elif getattr(shape, "has_table", False):
            itens.append((x, y, w, h, TIPO_TABELA, ""))
        elif getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
            itens.append((x, y, w, h, TIPO_TEXTO, shape.text_frame.text.strip()[:42]))
        elif com_imagens and tipo_forma == _IMAGEM:
            itens.append((x, y, w, h, TIPO_IMAGEM, getattr(shape, "name", "")[:42]))
        elif (tipo_forma == _AUTO and _tem_preenchimento(shape)
              and w * h <= area_slide * FRACAO_FUNDO and w > 0.12 and h > 0.12):
            # Card with no text of its own. The minimum width and height discard rule
            # lines and accent bars, which are decoration and do not bound content.
            itens.append((x, y, w, h, TIPO_CAIXA, getattr(shape, "name", "")[:42]))
    return itens


def _contem(a, b, tol=0.03):
    """True when box `a` contains box `b`. Text inside a card is nesting, not
    overlap, and must be told apart from the object that crosses the edge."""
    xa, ya, wa, ha = a[:4]
    xb, yb, wb, hb = b[:4]
    return (xb >= xa - tol and yb >= ya - tol
            and xb + wb <= xa + wa + tol and yb + hb <= ya + ha + tol)


def sobreposicoes(itens, folga, area_min):
    """Pairs that cross each other beyond the slack. `folga` (slack) absorbs
    deliberate touching."""
    achados = []
    for a in range(len(itens)):
        for b in range(a + 1, len(itens)):
            ia, ib = itens[a], itens[b]
            if _contem(ia, ib) or _contem(ib, ia):
                continue
            xa, ya, wa, ha, ta, na = ia
            xb, yb, wb, hb, tb, nb = ib
            ox = min(xa + wa, xb + wb) - max(xa, xb)
            oy = min(ya + ha, yb + hb) - max(ya, yb)
            if ox > folga and oy > folga and ox * oy > area_min:
                achados.append((ox * oy, ta, na, tb, nb))
    return achados


def fora_da_margem(itens, largura, altura, margem, tolerancia):
    achados = []
    for x, y, w, h, tipo, nome in itens:
        lados = []
        if x < margem - tolerancia:
            lados.append(f"left ({x:.2f})")
        if y < margem - tolerancia:
            lados.append(f"top ({y:.2f})")
        if x + w > largura - margem + tolerancia:
            lados.append(f"right ({x + w:.2f} of {largura:.2f})")
        if y + h > altura - margem + tolerancia:
            lados.append(f"bottom ({y + h:.2f} of {altura:.2f})")
        if lados:
            achados.append((tipo, nome, ", ".join(lados)))
    return achados


def _parse_slides(spec):
    """'3,7,12-15' -> {3, 7, 12, 13, 14, 15}. None when not given."""
    if not spec:
        return None
    alvo = set()
    for parte in spec.split(","):
        parte = parte.strip()
        if "-" in parte:
            ini, fim = parte.split("-", 1)
            alvo.update(range(int(ini), int(fim) + 1))
        elif parte:
            alvo.add(int(parte))
    return alvo


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("arquivo", help="path to the .pptx")
    ap.add_argument(
        "--margem",
        type=float,
        default=0.0,
        help="required margin in inches. 0 (default) flags only what leaves the slide; "
        "use the real value of the grid to require breathing room, for example 0.4",
    )
    ap.add_argument(
        "--folga",
        type=float,
        default=0.05,
        help="tolerated crossing on each axis, in inches (default 0.05). Absorbs "
        "objects touching on purpose and EMU rounding",
    )
    ap.add_argument(
        "--area-min",
        type=float,
        default=0.05,
        help="minimum crossing area to become a finding, in sq in (default 0.05)",
    )
    ap.add_argument(
        "--com-imagens",
        action="store_true",
        help="includes images in the comparison. Off by default because background "
        "photos and corner graphics produce findings that are not defects",
    )
    ap.add_argument("--slides", help="restricts to slides, e.g.: 3,7,12-15")
    args = ap.parse_args()

    prs = Presentation(args.arquivo)
    largura = Emu(prs.slide_width).inches
    altura = Emu(prs.slide_height).inches
    alvo = _parse_slides(args.slides)

    n_sobrepostos = 0
    n_fora = 0

    for i, slide in enumerate(prs.slides, 1):
        if alvo and i not in alvo:
            continue
        itens = coletar(slide, com_imagens=args.com_imagens,
                        largura=largura, altura=altura)

        for area, ta, na, tb, nb in sobreposicoes(itens, args.folga, args.area_min):
            n_sobrepostos += 1
            print(f"slide {i:>3}  overlaps  {area:.2f} sq in  [{ta}] {na!r} x [{tb}] {nb!r}")

        for tipo, nome, lados in fora_da_margem(itens, largura, altura, args.margem, 0.02):
            n_fora += 1
            print(f"slide {i:>3}  outside   [{tipo}] {nome!r} -> {lados}")

    escopo = f"{len(alvo)} slides" if alvo else f"{len(prs.slides)} slides"
    print(
        f"\n{escopo}, slide of {largura:.2f} x {altura:.2f} in, required margin "
        f"{args.margem:.2f} in"
    )
    print(f"overlaps: {n_sobrepostos}   outside the margin: {n_fora}")

    return 1 if (n_sobrepostos or n_fora) else 0


if __name__ == "__main__":
    sys.exit(main())
