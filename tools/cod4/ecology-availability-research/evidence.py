"""Evidence packaging only: read upstream as text; never execute/build it."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'tools/cod4/ecology-availability-research'
DOCS = ROOT / 'docs/cod4/audit-20261022/ecology-availability-research'
CACHE = ROOT / 'tools/cod4/legacy-migration-acceptance/.work/sources'
REPOS = {
    'am': ('AlexModGuy__AlexsMobs', 'AlexModGuy/AlexsMobs'),
    'tf': ('TeamTwilight__twilightforest', 'TeamTwilight/twilightforest'),
    'iaf': ('AlexModGuy__Ice_and_Fire', 'AlexModGuy/Ice_and_Fire'),
    'mw': ('BobMowzie__MowziesMobs-Public', 'BobMowzie/MowziesMobs-Public'),
    'cs': ('Momo-Softworks__Cold-Sweat', 'Momo-Softworks/Cold-Sweat'),
}
AM = 'src/main/java/com/github/alexthe666/alexsmobs/'
TF = 'src/main/java/twilightforest/'
IAF = 'src/main/java/com/github/alexthe666/iceandfire/'
MW = 'src/main/java/com/bobmowzie/mowziesmobs/'
CS = 'src/main/java/com/momosoftworks/coldsweat/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(name, data):
    DOCS.mkdir(parents=True, exist_ok=True)
    target = DOCS / name
    temporary = target.with_name('.' + target.name + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(target)


def source(key, path):
    name, repo = REPOS[key]
    base = (ROOT / 'tools/cod4/immune-feedback-research/sources' / name) if key in ('mw', 'cs') else CACHE / name
    meta_raw = (base / 'source.json').read_bytes()
    tree_raw = (base / 'tree.json').read_bytes()
    meta, tree = json.loads(meta_raw), json.loads(tree_raw)
    revision = meta.get('sha', meta.get('commit'))
    assert meta['repo'] == repo and re.fullmatch('[a-f0-9]{40}', revision)
    assert tree['sha'] == revision and tree['truncated'] is False
    raw = (base / path).read_bytes()
    git_hash = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    blob = next(x for x in tree['tree'] if x['path'] == path)
    assert blob['type'] == 'blob' and blob['sha'] == git_hash, (repo, path)
    dest = TOOLS / 'sources' / name
    (dest / path).parent.mkdir(parents=True, exist_ok=True)
    (dest / path).write_bytes(raw)
    (dest / 'source.json').write_bytes(meta_raw)
    (dest / 'tree.json').write_bytes(tree_raw)
    return dict(repo=repo, revision=revision, path=path,
                source_local=str((dest / path).relative_to(ROOT)), source_sha256=sha(raw),
                git_blob_sha1=git_hash, pinned_tree_match=True,
                source_metadata=str((dest / 'source.json').relative_to(ROOT)),
                tree_metadata=str((dest / 'tree.json').relative_to(ROOT)),
                provenance='local cached official-repo identity and fixed recursive Git tree; no fresh online verification'), raw.decode().splitlines()


def span(key, path, start, end, role, kind='supporting_range'):
    info, lines = source(key, path)
    assert 1 <= start <= end <= len(lines)
    info.update(line=start, end_line=end, excerpt='\n'.join(lines[start-1:end]), role=role, evidence_kind=kind)
    info['excerpt_sha256'] = sha(info['excerpt'].encode())
    info['url'] = f"https://github.com/{info['repo']}/blob/{info['revision']}/{path}#L{start}-L{end}"
    return info


def method(key, path, signature, role):
    _, lines = source(key, path)
    hits = [i for i, line in enumerate(lines) if signature in line]
    assert len(hits) == 1, (path, signature, hits)
    start = hits[0]
    body = '\n'.join(lines[start:])
    mask = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/',
                  lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), body)
    opening = mask.index('{')
    assert ';' not in mask[:opening]
    depth = 0
    for i in range(opening, len(mask)):
        depth += (mask[i] == '{') - (mask[i] == '}')
        if depth == 0:
            end = start + mask[:i + 1].count('\n')
            break
    else:
        raise ValueError(signature)
    while start and lines[start-1].lstrip().startswith('@'):
        start -= 1
    return span(key, path, start+1, end+1, role, 'complete_method')


def record(identifier, key, semantic, primary, chain, observation, application, limits, dedup, status='reviewed_proposed'):
    return dict(id=identifier, semantic_key=semantic, status=status,
                proposed_credit=1 if status == 'reviewed_proposed' else 0, accepted_credit=0,
                **{k:v for k,v in primary.items() if k != 'role'},
                chain=[primary]+chain, observation=observation, application=application,
                limits=limits, deduplication=dedup, upstream_code_executed=False,
                independent_acceptance='pending; no production or runtime acceptance credited')


def verify_records(records):
    seen = set()
    for r in records:
        assert r['semantic_key'] not in seen
        seen.add(r['semantic_key'])
        for e in r['chain']:
            raw = (ROOT/e['source_local']).read_bytes()
            assert sha(raw) == e['source_sha256']
            excerpt = '\n'.join(raw.decode().splitlines()[e['line']-1:e['end_line']])
            assert excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256']
    return {'kind':'text/hash/range integrity inspection only; no compile/test/game execution',
            'records':len(records), 'unique_semantic_keys':len(seen),
            'complete_method_evidence':sum(e['evidence_kind']=='complete_method' for r in records for e in r['chain']),
            'supporting_ranges_are_not_credit':True, 'all_copied_bytes_match_pinned_git_blobs':True}
