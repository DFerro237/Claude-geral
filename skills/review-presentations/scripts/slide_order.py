"""Reads the displayed slide order and the internal relationships of a PPTX."""
import posixpath
import xml.etree.ElementTree as ET
from urllib.parse import unquote

P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def rels_path(part):
    return posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')

def resolve_part(part, target):
    target = unquote(target.split('#', 1)[0]).replace('\\', '/')
    if target.startswith('/'):
        return posixpath.normpath(target.lstrip('/'))
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))

def relationships(package, part):
    try:
        root = ET.fromstring(package.read(rels_path(part)))
    except KeyError:
        return {}
    return {item.get('Id'): dict(item.attrib) for item in root}

def slide_order(package):
    part = 'ppt/presentation.xml'
    rels = relationships(package, part)
    root = ET.fromstring(package.read(part))
    result = []
    for item in root.findall(f'{P}sldIdLst/{P}sldId'):
        rel = rels.get(item.get(R + 'id'))
        if not rel or not rel.get('Type', '').endswith('/slide') or rel.get('TargetMode') == 'External':
            raise ValueError('Missing or invalid slide relationship in the presentation order')
        target = resolve_part(part, rel['Target'])
        if target not in package.namelist():
            raise ValueError('Missing slide part: ' + target)
        result.append(target)
    return result

def hyperlink_resolves(package, part, relationship_id, action=''):
    if not relationship_id:
        return action.startswith('ppaction://hlinkshowjump?')
    rel = relationships(package, part).get(relationship_id)
    if not rel or not rel.get('Target'):
        return False
    if rel.get('TargetMode') == 'External':
        return True  # link integrity only; the URL itself is not fetched
    return resolve_part(part, rel['Target']) in package.namelist()
