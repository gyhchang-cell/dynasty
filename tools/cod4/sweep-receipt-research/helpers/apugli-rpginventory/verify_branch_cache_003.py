"""Read archives as data, extract text only, verify pinned Git objects; execute no upstream code."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE / 'sources/MerchantPug__Apugli'
WORKSPACE = HERE.parents[4]
DOCS = WORKSPACE / 'docs/cod4/audit-20261022/sweep-receipt-research/helpers/apugli-rpginventory'
PINS = {'behavior': '5cf41d11dbb4308b0796505e6c9d3541bad09217',
        'next': '456c63617e147a845dd6908d6a9ef29c60ac7dd4'}


def git_hash(kind, payload):
    return hashlib.sha1(kind.encode() + b' ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()


def main():
    result = []
    for name, pin in PINS.items():
        commit = json.loads((BASE / f'{name}-commit-003.json').read_text())
        tree = json.loads((BASE / f'{name}-tree-003.json').read_text())
        assert commit['sha'] == pin and not tree['truncated']
        entries = tree['tree']
        expected_trees = {x['path']: x['sha'] for x in entries if x['type'] == 'tree'}
        expected_trees[''] = commit['commit']['tree']['sha']
        for directory, expected in expected_trees.items():
            children = [x for x in entries if ('' if str(PurePosixPath(x['path']).parent) == '.' else str(PurePosixPath(x['path']).parent)) == directory]
            children.sort(key=lambda x: PurePosixPath(x['path']).name + ('/' if x['type'] == 'tree' else ''))
            payload = b''.join((x['mode'].lstrip('0') + ' ' + PurePosixPath(x['path']).name).encode() + b'\0' + bytes.fromhex(x['sha']) for x in children)
            assert git_hash('tree', payload) == expected, directory
        blobs = {x['path']: x['sha'] for x in entries if x['type'] == 'blob'}
        root = BASE / f'{name}-tree-003'
        verified = []
        with tarfile.open(BASE / f'{name}-snapshot-003.tar.gz', 'r:gz') as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                relative = PurePosixPath(*PurePosixPath(member.name).parts[1:])
                assert not relative.is_absolute() and '..' not in relative.parts
                if relative.suffix not in {'.java', '.json', '.md', '.gradle', '.properties'} and relative.name != 'LICENSE':
                    continue
                data = archive.extractfile(member).read()
                data.decode('utf-8')
                assert git_hash('blob', data) == blobs[str(relative)], str(relative)
                target = root / str(relative)
                if target.exists():
                    assert target.read_bytes() == data
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                verified.append({'path': str(relative), 'source_local': str(target.relative_to(WORKSPACE)),
                                 'source_sha256': hashlib.sha256(data).hexdigest(), 'git_blob_sha1': blobs[str(relative)]})
        result.append({'branch_label': name, 'revision': pin, 'git_tree_sha': expected_trees[''],
                       'all_tree_objects_reconstructed': True, 'downloaded_code_executed': False,
                       'files': verified})
    (DOCS / 'branch-source-index-003.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{'branch': x['branch_label'], 'verified_files': len(x['files']), 'revision': x['revision']} for x in result]))


if __name__ == '__main__':
    main()
