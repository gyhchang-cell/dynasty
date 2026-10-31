"""Local research utilities: read Java as text, never import upstream code."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[4]
DOCS = WORKSPACE / 'docs/cod4/audit-20261022/sweep-receipt-research/helpers/apugli-rpginventory'
CACHE = HERE / 'sources/MerchantPug__Apugli'
REPO = 'ChrysanthCow/apugli'
PINS = {'default': 'fcbadb4b288996f1767ce3d954522270e88681aa',
        'behavior': '5cf41d11dbb4308b0796505e6c9d3541bad09217',
        'next': '456c63617e147a845dd6908d6a9ef29c60ac7dd4'}
ROOTS = {name: CACHE / ('tree' if name == 'default' else name + '-tree-003') for name in PINS}
METADATA = {name: CACHE / ('commit.json' if name == 'default' else name + '-commit-003.json') for name in PINS}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def method(branch, path, signature, role):
    p = ROOTS[branch] / path
    raw = p.read_bytes()
    lines = raw.decode().splitlines()
    hits = [i for i, line in enumerate(lines) if signature in line]
    assert len(hits) == 1, (path, signature, hits)
    start = hits[0]
    body = '\n'.join(lines[start:])
    mask = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/',
                  lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), body)
    opening = mask.index('{')
    assert ';' not in mask[:opening], 'not a concrete method'
    depth = 0
    end = None
    for i in range(opening, len(mask)):
        depth += (mask[i] == '{') - (mask[i] == '}')
        if depth == 0:
            end = start + mask[:i + 1].count('\n')
            break
    assert end is not None
    while start and lines[start - 1].lstrip().startswith('@'):
        start -= 1
    excerpt = '\n'.join(lines[start:end + 1])
    metadata = METADATA[branch]
    return dict(repo=REPO, revision=PINS[branch], path=path,
                method=re.search(r'([\w$]+)\s*\(', lines[hits[0]]).group(1),
                source_metadata=str(metadata.relative_to(WORKSPACE)),
                source_root=str(ROOTS[branch].relative_to(WORKSPACE)),
                source_local=str(p.relative_to(WORKSPACE)), source_sha256=sha(raw),
                line=start + 1, end_line=end + 1, excerpt=excerpt, snippet_sha256=sha(excerpt.encode()),
                role=role, url=f'https://github.com/{REPO}/blob/{PINS[branch]}/{path}#L{start + 1}-L{end + 1}')


def standard(branch, short, signature, role):
    platform, name = short.split(':', 1)
    if branch == 'next':
        platform = {'common': 'Common', 'fabric': 'Fabric', 'forge': 'Forge'}[platform]
    return method(branch, f'{platform}/src/main/java/net/merchantpug/apugli/{name}.java', signature, role)


def behavior(name, signature, role):
    return method('behavior', f'src/main/java/io/github/merchantpug/apugli/{name}.java', signature, role)


def dump(name, data):
    (DOCS / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
