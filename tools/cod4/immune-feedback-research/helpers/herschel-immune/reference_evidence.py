"""Local text evidence only; imports no upstream Java and performs no game action."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[5]
DOC = ROOT / 'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'
SOURCES = ROOT / 'tools/cod4/immune-feedback-research/sources'

def sha(data):
    return hashlib.sha256(data).hexdigest()

reader_path = ROOT / 'tools/cod4/immune-feedback-research/helpers/halley-immune/inspect_methods.py'
reader = {'__name__': 'static_text_reader', '__file__': str(reader_path)}
exec(reader_path.read_text(), reader)

class Evidence:
    def __init__(self, batch):
        self.batch = batch
        self.files = {}
        self.out = Path(__file__).parent / f'sources-batch{batch:03}'
        self.master_path = DOC.parent.parent / 'reviewed.json'
        self.master_before = sha(self.master_path.read_bytes())
        self.prior = []
        for path in sorted(DOC.glob('batch-*.json')):
            if int(path.stem.split('-')[-1]) >= batch:
                continue
            for row in json.loads(path.read_text()).get('rows', []):
                for ref in row.get('source_refs', []):
                    if ref.get('normalized_excerpt_sha256'):
                        self.prior.append((ref['normalized_excerpt_sha256'], row['id']))

    def ref(self, repo, file, method=None, signature=None, span=None, focus=None):
        base = SOURCES / repo
        paths = [base / (file + '.java')] if '/' in file else list(base.rglob(file + '.java'))
        if len(paths) != 1 or not paths[0].is_file():
            raise ValueError(('ambiguous/missing file', repo, file, paths))
        path = paths[0]
        raw = path.read_bytes()
        lines = raw.decode().splitlines(keepends=True)
        rel = path.relative_to(base).as_posix()
        metadata = json.loads((base / 'source.json').read_text())
        tree = json.loads((base / 'tree.json').read_text()) if (base / 'tree.json').exists() else None
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if tree is not None:
            expected = next(x['sha'] for x in tree['tree'] if x['path'] == rel)
            if tree['sha'] != metadata['commit'] or blob != expected:
                raise ValueError(('fixed-source mismatch', repo, rel))
            proof = 'pinned Git tree blob SHA1 and source SHA256'
        else:
            entries = [x for x in metadata.get('files', []) if x['path'] == rel]
            if len(entries) != 1 or entries[0]['sha256'] != sha(raw) or not metadata.get('archive_sha256'):
                raise ValueError(('pinned archive inventory mismatch', repo, rel))
            proof = 'pinned archive source.json SHA256 inventory; blob computed, not remotely tree verified'
        key = repo + '/' + rel
        target = self.out / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        for name in ['source.json', 'tree.json']:
            if not (base/name).exists():
                continue
            dest = self.out / repo / name
            if not dest.exists():
                shutil.copyfile(base/name, dest)
        self.files[key] = dict(repo=metadata['repo'], commit=metadata['commit'], path=rel,
            local=str(target.relative_to(ROOT)), sha256=sha(raw), git_blob_sha1=blob,
            fixed_tree_verified=tree is not None, tree_url=tree.get('url') if tree else None,
            proof=proof, archive_sha256=metadata.get('archive_sha256'))
        if span:
            start, stop = span
            unit = 'complete_registration_statements_support_only'
        elif method:
            candidates = [n for n, line in enumerate(lines, 1)
                if re.match(r'\s*(public|private|protected|default|static)\s', line)
                and re.search(r'\b'+re.escape(method)+r'\s*\(', line)
                and not line.strip().endswith(';') and (not signature or signature in line)]
            if len(candidates) != 1:
                raise ValueError(('ambiguous/missing method', file, method, signature, candidates))
            start = candidates[0]
            stop = reader['end_method'](lines, start)
            unit = 'complete_method'
        else:
            start, stop = 1, len(lines)
            unit = 'complete_file_support_only'
        excerpt = ''.join(lines[start-1:stop])
        normalized = sha(re.sub(r'\s+', '', excerpt).encode())
        ref = dict(unit=unit, source_key=key, method=method, lines=[start,stop],
            fixed_commit=metadata['commit'], file_sha256=sha(raw),
            url=f"https://github.com/{metadata['repo']}/blob/{metadata['commit']}/{rel}#L{start}-L{stop}",
            excerpt=excerpt, excerpt_sha256=sha(excerpt.encode()),
            normalized_excerpt_sha256=normalized,
            prior_helper_exact_normalized_matches=sorted(set(row for value,row in self.prior if value == normalized)))
        if focus:
            a, b = focus
            if not start <= a <= b <= stop:
                raise ValueError(('focus outside complete method', method, start,stop,focus))
            focused = ''.join(lines[a-1:b])
            ref['decision_focus'] = dict(lines=[a,b], excerpt=focused, excerpt_sha256=sha(focused.encode()))
        return ref

    def finish(self, rows, exclusions=None):
        if sha(self.master_path.read_bytes()) != self.master_before:
            master_boundary = 'Master changed concurrently; helper never writes it. Semantic final review still required.'
        else:
            master_boundary = 'Master bytes unchanged during this evidence serialization.'
        pending = sum(r['status'] == 'pending_primary_semantic_review' for r in rows)
        batch = dict(batch=f'herschel-immune-{self.batch:03}', research_credit=0,
            suggested_credit=0, effective_promoted=0, reviewed_units=len(rows),
            pending_primary_review_units=pending, support_only_units=len(rows)-pending,
            rows=rows, exclusions=exclusions or [],
            counting_policy='Method/hash/file counts are not research credit. Fixed full containing methods plus manual observations; Russell must review semantic independence. Missing chains remain support0.',
            master_observation=master_boundary)
        path = DOC/f'batch-{self.batch:03}.json'
        def write(name, data):
            (DOC/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
        write(path.name, batch)
        write(f'source-manifest-{self.batch:03}.json', dict(files=self.files, research_credit=0))
        receipt = dict(status='HELPER_HANDOFF_PENDING_PRIMARY_NOT_ACCEPTANCE',
            batch_sha256=sha(path.read_bytes()), reviewed_units=len(rows), pending_primary=pending,
            support_only=len(rows)-pending, source_files=len(self.files), research_credit=0,
            production_writes=0, master_writes=0, asset_writes=0, todo_writes=0,
            game_launches=0, gui_actions=0, compilations=0, runtime_tests=0,
            external_requests=0, evidence='Manual static source review + pinned byte/blob and excerpt checks; no runtime claim')
        write(f'receipt-{self.batch:03}.json', receipt)
        return receipt

def row(batch, number, key, status, refs, observation, application, dedup, limits):
    return dict(id=f'herschel-{batch:03}-{number:02}', semantic_dedup_key=key,
        status=status, research_credit=0, suggested_credit=0, source_refs=refs,
        concrete_observation=observation, application_to_boss_immune=application,
        semantic_dedup=dedup, limitations=limits)
