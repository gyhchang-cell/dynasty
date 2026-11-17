"""Main-owned audit of helper bytes/ranges; never transfers proposed credit.

Use Python 3.12 for tree-sitter. Semantic decisions are separately authored in
reviews, not inferred by this script. Helper inputs are read-only.
"""
from pathlib import Path
import sys, json, hashlib, datetime, collections

assert sys.version_info[:2] == (3, 12)
R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / 'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language, Parser
import tree_sitter_java
parser = Parser(Language(tree_sitter_java.language()))
O = R / 'docs/cod4/audit-20261022/sweep-receipt-research'
H = O / 'helpers/apugli-rpginventory'
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)

files = ['batch-001.json', 'scope-pending-reviewed.json', 'auxiliary-reviewed.json']
inputs = {name: json.loads((H / name).read_text())['entries'] for name in files}
errors, sources, spans = [], {}, set()
nodes_checked = 0
cache = R / 'tools/cod4/sweep-receipt-research/helpers/apugli-rpginventory/sources/MerchantPug__Apugli'
commit = json.loads((cache / 'commit.json').read_text())
tree = json.loads((cache / 'git-tree.json').read_text())
assert commit['sha'] == 'fcbadb4b288996f1767ce3d954522270e88681aa'
assert not tree['truncated']
git_object = lambda kind, raw: hashlib.sha1(kind + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
tree_nodes = {e['path']: e for e in tree['tree']}
blobs_checked = 0
uncached_blobs = []
for relative, e in tree_nodes.items():
    if e['type'] == 'blob':
        f = cache / 'tree' / relative
        if not f.is_file():
            uncached_blobs.append(relative)
            continue
        assert git_object(b'blob', f.read_bytes()) == e['sha']
        blobs_checked += 1
directories = [''] + [p for p, e in tree_nodes.items() if e['type'] == 'tree']
for directory in directories:
    children = [e for p, e in tree_nodes.items()
                if ('' if str(Path(p).parent) == '.' else str(Path(p).parent)) == directory]
    # Git sorts tree entries as though directory names had a trailing slash.
    children.sort(key=lambda e: Path(e['path']).name + ('/' if e['type'] == 'tree' else ''))
    data = b''.join((e['mode'].lstrip('0') + ' ' + Path(e['path']).name).encode()
                    + b'\0' + bytes.fromhex(e['sha']) for e in children)
    expected = commit['commit']['tree']['sha'] if not directory else tree_nodes[directory]['sha']
    assert git_object(b'tree', data) == expected, directory
for name, records in inputs.items():
    for r in records:
        for e in [r, *r['evidence']]:
            local = e['source_local']
            raw = (R / local).read_bytes()
            relative = str((R / local).relative_to(cache / 'tree'))
            assert git_object(b'blob', raw) == tree_nodes[relative]['sha']
            source_sha = sha(raw)
            text = '\n'.join(raw.decode().splitlines()[e['line']-1:e['end_line']])
            label = [name, r['chain_id'], local, e['line']]
            if source_sha != e['source_sha256']:
                errors.append([label, 'source_sha256'])
            if sha(e['excerpt'].encode()) != e['snippet_sha256']:
                errors.append([label, 'snippet_sha256'])
            if text.strip() != e['excerpt'].strip():
                errors.append([label, 'range_excerpt'])
            methods = [n for n in walk(parser.parse(raw).root_node)
                       if n.type == 'method_declaration'
                       and n.start_point.row + 1 <= e['line'] <= n.end_point.row + 1
                       and n.end_point.row + 1 == e['end_line']]
            if len(methods) != 1 or methods[0].has_error:
                errors.append([label, 'not_full_valid_method'])
            sources[local] = source_sha
            spans.add((local, e['line'], e['end_line']))
            nodes_checked += 1
rows = [json.loads(line) for line in (O / 'reviewed.jsonl').read_text().splitlines()]
merged = [r for r in rows if 'apugli-rpginventory/' in
          r.get('helper_provenance', {}).get('batch', '')]
report = {
    'generated_at': datetime.datetime.now().astimezone().isoformat(),
    'helper_files_modified': False,
    'input_hashes': {name: sha((H/name).read_bytes()) for name in files},
    'primary_proposals': len(inputs['batch-001.json']),
    'scope_pending_proposals': len(inputs['scope-pending-reviewed.json']),
    'auxiliary_proposals': len(inputs['auxiliary-reviewed.json']),
    'nodes_integrity_checked_with_repeated_primary': nodes_checked,
    'unique_method_ranges_integrity_checked': len(spans),
    'unique_sources_integrity_checked': len(sources),
    'git_blobs_independently_checked': blobs_checked,
    'git_trees_independently_reconstructed': len(directories),
    'tree_blobs_not_saved_by_helper': uncached_blobs,
    'commit_root_tree': commit['commit']['tree']['sha'],
    'errors': errors, 'integrity_check_awards_credit': 0,
    'human_review_boundary': '主审已全文审阅batch-001七个主方法与50段支持，以及scope-pending-reviewed两个主方法与17段支持；合计7接受、2排除。三条auxiliary仅做完整性核对，不冒称已全文语义审阅，不计有效研究。',
    'main_decisions': dict(collections.Counter(r['decision'] for r in merged)),
    'main_review_candidates': [r['candidate_index'] for r in merged],
    'rpginventory_credit': 0,
    'rpginventory_reason': '精确请求地址404，无可核验源码；未猜测替代项目。',
    'production_changed': False, 'upstream_code_executed': False,
}
(O / 'apugli-rpginventory-main-review.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:report[k] for k in (
    'unique_method_ranges_integrity_checked', 'unique_sources_integrity_checked',
    'main_decisions', 'errors')}, ensure_ascii=False))
assert not errors
