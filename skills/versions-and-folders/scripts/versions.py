# -*- coding: utf-8 -*-
"""File versions in the vX.Y pattern: folder inventory and computation of the next version.

Read only. It never moves, renames or deletes: Claude does the moving, after the rule or the approval.

Subcommands and flags are in Portuguese: proxima (next), pequena|grande (small|large),
inventario (inventory), --recursivo (recursive), --sem-hash (no content hash).

    python versions.py proxima <file> pequena|grande
    python versions.py inventario <folder> [--recursivo] [--sem-hash] [--json]
"""
import argparse, hashlib, json, re, sys, time
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NOVO = re.compile(r'^(?P<base>.+?)_[vV](?P<x>\d+)\.(?P<y>\d+)(?P<resto>.*)$')
LEGADO = re.compile(r'^(?P<base>.+?)_[vV](?P<n>\d{1,3})(?![.\d])(?P<resto>.*)$')
COPIA = re.compile(r'(\s\(\d+\)|\s-\s(Copia|Cópia|Copy))$', re.I)
STATUS = re.compile(r'[\s_\-]+(final|revisad[oa]|ok|definitiv[oa]|aprovad[oa])$', re.I)
ANO = re.compile(r'[\s_\-]+(19|20)\d{2}$')
PASTAS_OLD = {'old', 'antigos', 'antigo', 'versoes antigas', 'versões antigas'}
IGNORAR = {'readme.md', 'desktop.ini', 'thumbs.db', '.ds_store'}
LIMITE_ARQUIVOS, LIMITE_MATERIAIS, DIAS_RECENTE = 6, 3, 7


def ler_nome(nome):
    """Returns (base, version, kind, rest). kind: 'novo' (vX.Y), 'legado' (vNN) or 'sem' (no version)."""
    stem = Path(nome).stem
    m = NOVO.match(stem)
    if m:
        return m['base'], (int(m['x']), int(m['y'])), 'novo', m['resto']
    m = LEGADO.match(stem)
    if m:
        return m['base'], (int(m['n']),), 'legado', m['resto']
    return stem, None, 'sem', ''


def sem_status(base):
    """Splits a status word off the end of the base name: ('Call notes', 'final')."""
    m = STATUS.search(base)
    return (base[:m.start()], m.group(1)) if m else (base, '')


def chave_ordem(tipo, versao):
    # any vX.Y is newer than any vNN, which is newer than a file with no version
    return ({'sem': 0, 'legado': 1, 'novo': 2}[tipo], versao or ())


def proxima(arquivo, tipo_mudanca):
    p = Path(arquivo)
    base, versao, tipo, resto = ler_nome(p.name)
    avisos = []
    base, status = sem_status(base)
    if status:
        avisos.append('the word %r was dropped from the name, because the rule uses no status suffix' % status)
    if resto:
        avisos.append('the current name has a suffix after the version (%r); the next one comes out without it' % resto)
    if tipo != 'novo':
        x, y = 1, 1
        avisos.append('file %s: the next one restarts at v1.1'
                      % ('in the old pattern' if tipo == 'legado' else 'with no version'))
    elif tipo_mudanca == 'pequena':
        x, y = versao[0], versao[1] + 1
    else:
        x, y = versao[0] + 1, 1
    return '%s_v%d.%d%s' % (base, x, y, p.suffix), avisos


def md5(caminho):
    h = hashlib.md5()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def eh_old(pasta):
    return pasta.name.strip().lower() in PASTAS_OLD


def analisar_pasta(pasta):
    vivos, travas, old_dirs, subpastas = [], [], [], []
    for item in sorted(pasta.iterdir(), key=lambda x: x.name.lower()):
        if item.is_dir():
            (old_dirs if eh_old(item) else subpastas).append(item)
        elif item.name.startswith('~$'):
            travas.append(item.name[2:])
        elif item.name.lower() not in IGNORAR:
            vivos.append(item)
    materiais = defaultdict(list)
    agora = time.time()
    for f in vivos:
        base, versao, tipo, resto = ler_nome(f.name)
        base, status = sem_status(COPIA.sub('', base))
        materiais[base].append({
            'arquivo': f.name, 'tipo': tipo, 'versao': versao, 'sufixo': resto, 'status': status,
            'copia': bool(COPIA.search(Path(f.name).stem)),
            'recente': (agora - f.stat().st_mtime) < DIAS_RECENTE * 86400,
            # Word writes the lock file as ~$ plus the name without its first two characters
            'aberto': any(t and f.name.endswith(t) for t in travas),
        })
    saida = []
    for base, arqs in sorted(materiais.items(), key=lambda kv: kv[0].lower()):
        arqs.sort(key=lambda a: chave_ordem(a['tipo'], a['versao']))
        topo = chave_ordem(arqs[-1]['tipo'], arqs[-1]['versao'])
        vigentes = [a for a in arqs if chave_ordem(a['tipo'], a['versao']) == topo]
        duvidas = []
        if any(a['tipo'] == 'sem' for a in arqs) and any(a['tipo'] != 'sem' for a in arqs):
            duvidas.append('there is a file with no version next to numbered versions: which one is current?')
        exts = {Path(a['arquivo']).suffix.lower() for a in vigentes}
        if len(vigentes) > 1 and len(exts) < len(vigentes):
            duvidas.append('more than one file competes for the place of current file: %s' % ' | '.join(a['arquivo'] for a in vigentes))
        for a in arqs:
            if a['sufixo']:
                duvidas.append('%s: suffix after the version' % a['arquivo'])
            if a['status']:
                duvidas.append('%s: "%s" in the name, may be the delivered copy' % (a['arquivo'], a['status']))
            if a['copia']:
                duvidas.append('%s: looks like a download copy or a duplicate' % a['arquivo'])
            # recent only matters for files that would move: the current one stays either way
            if a['recente'] and a not in vigentes:
                duvidas.append('%s: candidate for old, but modified in the last %d days' % (a['arquivo'], DIAS_RECENTE))
            if a['aberto']:
                duvidas.append('%s: is open (~$ file present)' % a['arquivo'])
        saida.append({
            'material': base,
            'vigente': [a['arquivo'] for a in vigentes],
            'candidatos_old': [a['arquivo'] for a in arqs if a not in vigentes],
            'legados': [a['arquivo'] for a in arqs if a['tipo'] == 'legado'],
            'duvidas': duvidas,
        })
    # the same material with a year in the name ("Deck 2025" and "Deck 2026") is not grouped, only flagged
    por_raiz = defaultdict(list)
    for m in saida:
        por_raiz[ANO.sub('', m['material'])].append(m)
    for grupo in por_raiz.values():
        if len(grupo) > 1:
            nomes = [m['material'] for m in grupo]
            for m in grupo:
                outros = ', '.join(n for n in nomes if n != m['material'])
                m['duvidas'].append('may be the same material as "%s", with a different year in the name' % outros)
    return {
        'pasta': str(pasta),
        'arquivos_fora_de_old': len(vivos),
        'materiais': saida,
        'pastas_old': [d.name for d in old_dirs],
        'subpastas': [d.name for d in subpastas],
        'travas': travas,
        'baguncada': len(vivos) > LIMITE_ARQUIVOS or len(saida) >= LIMITE_MATERIAIS,
    }, subpastas


def duplicados(raiz, recursivo):
    por_tamanho = defaultdict(list)
    it = raiz.rglob('*') if recursivo else raiz.iterdir()
    for f in it:
        if f.is_file() and not f.name.startswith('~$') and f.name.lower() not in IGNORAR:
            por_tamanho[f.stat().st_size].append(f)
    grupos = defaultdict(list)
    for tam, fs in por_tamanho.items():
        if len(fs) > 1 and tam > 0:          # only reads content when the size matches
            for f in fs:
                grupos[md5(f)].append(str(f.relative_to(raiz)))
    return [sorted(v) for v in grupos.values() if len(v) > 1]


def inventario(raiz, recursivo, com_hash):
    relatorio, fila = [], [raiz]
    while fila:
        pasta = fila.pop(0)
        r, subs = analisar_pasta(pasta)
        relatorio.append(r)
        if recursivo:
            fila.extend(subs)
    dups = duplicados(raiz, recursivo) if com_hash else None
    return relatorio, dups


def imprimir(relatorio, dups, raiz):
    for r in relatorio:
        p = Path(r['pasta'])
        print('=== %s ===' % (p.relative_to(raiz) if p != raiz else '.'))
        print('files outside old: %d | materials: %d | messy folder: %s' % (
            r['arquivos_fora_de_old'], len(r['materiais']), 'yes' if r['baguncada'] else 'no'))
        if r['pastas_old']:
            print('existing folder for old files: %s' % ', '.join(r['pastas_old']))
        if r['subpastas']:
            print('subfolders: %s' % ', '.join(r['subpastas']))
        for m in r['materiais']:
            print('\n  material: %s' % m['material'])
            print('    current: %s' % ' | '.join(m['vigente']))
            if m['candidatos_old']:
                print('    candidates for old (%d): %s' % (len(m['candidatos_old']), ' | '.join(m['candidatos_old'])))
            if m['legados']:
                print('    in the old vNN pattern: %d' % len(m['legados']))
            for d in m['duvidas']:
                print('    doubt: %s' % d)
        print()
    if dups is None:
        print('duplicates: not checked (--sem-hash)')
    elif dups:
        print('files identical by content:')
        for g in dups:
            print('  - ' + ' = '.join(g))
    else:
        print('files identical by content: none')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p1 = sub.add_parser('proxima')
    p1.add_argument('arquivo')
    p1.add_argument('mudanca', choices=['pequena', 'grande'])
    p2 = sub.add_parser('inventario')
    p2.add_argument('pasta')
    p2.add_argument('--recursivo', action='store_true')
    p2.add_argument('--sem-hash', action='store_true',
                    help='does not read content; use on a synced cloud drive, where reading forces the file download')
    p2.add_argument('--json', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'proxima':
        nome, avisos = proxima(a.arquivo, a.mudanca)
        print(nome)
        for av in avisos:
            print('warning: ' + av, file=sys.stderr)
    else:
        raiz = Path(a.pasta)
        if not raiz.is_dir():
            raise SystemExit('folder not found: %s' % raiz)
        rel, dups = inventario(raiz, a.recursivo, not a.sem_hash)
        if a.json:
            print(json.dumps({'pastas': rel, 'duplicados': dups}, ensure_ascii=False, indent=1))
        else:
            imprimir(rel, dups, raiz)


if __name__ == '__main__':
    main()
