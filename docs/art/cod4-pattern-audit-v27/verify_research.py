"""Verify review evidence; downloading/scanning never increments reviewed counts."""
from pathlib import Path
import collections
import hashlib
import json
import re

D = Path(__file__).resolve().parent
R = D.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    initial = json.loads((D / 'reference-ledger.json').read_text())
    candidates = json.loads((D / 'method-candidates.json').read_text())
    by_site = {(m['repo'], m['revision'], m['path'], m['start'], m['end']): m
               for m in candidates['methods']}
    accepted, excluded, errors = [], [], []
    seen_sites, seen_semantics = set(), set()
    for row in initial['rows']:
        path = D / row['local']
        data = path.read_bytes()
        assert sha(data) == row['sha256'], str(path)
        assert 0 < row['lineStart'] <= row['lineEnd'] <= len(data.splitlines())
        assert re.fullmatch(r'[0-9a-f]{40}', row['commit'])
        accepted.append(dict(row, evidenceFile='reference-ledger.json',
                             reviewMode='MANUALLY_READ_SOURCE_RANGE'))
    excluded.extend(initial['excluded'])
    for file in sorted(D.glob('manual-method-reviews-v*.json')):
        batch = json.loads(file.read_text())
        assert batch['reviewed'] == len(batch['rows']), file.name
        excluded.extend(batch.get('excluded', []))
        for row in batch['rows']:
            path = R / row['local']
            data = path.read_bytes()
            assert sha(data) == row['sourceSha256'], str(path)
            assert re.fullmatch(r'[0-9a-f]{40}', row['revision'])
            actual = '\n'.join(data.decode().splitlines()[row['start']-1:row['end']])
            assert actual.strip() == row['source'].strip(), (file.name, row['id'])
            assert row['reviewMode'] == 'MANUALLY_READ_FULL_METHOD'
            assert len(row['observation']) >= 35 and row['targetScope']
            assert f"/{row['revision']}/{row['path']}#L{row['start']}-L{row['end']}" in row['url']
            site = (row['repo'], row['revision'], row['path'], row['start'], row['end'])
            if site in seen_sites:
                errors.append({'site': site, 'reason': 'Repeated exact source range'})
                continue
            seen_sites.add(site)
            # File-range reviews from the first batch already include these methods.
            overlapping = [r for r in initial['rows'] if r['repo'] == row['repo']
                           and r['commit'] == row['revision'] and r['path'] == row['path']
                           and r['lineStart'] <= row['end'] and r['lineEnd'] >= row['start']]
            if overlapping:
                errors.append({'site': site, 'reason': 'Already included in initial reviewed range'})
                continue
            current = by_site.get(site)
            # Rebuilding the candidate inventory changes numeric ids, never identity.
            semantic = current['semanticHash'] if current else row['semanticHash']
            if semantic in seen_semantics:
                errors.append({'site': site, 'reason': 'Duplicate normalized method body'})
                continue
            seen_semantics.add(semantic)
            accepted.append(dict(row, evidenceFile=file.name, verifiedSemanticHash=semantic))
    per_scope = collections.Counter(r['targetScope'] for r in accepted if 'targetScope' in r)
    source_count = len({(r['repo'], r.get('revision', r.get('commit')), r['path']) for r in accepted})
    scopes = {
        'supreme_sword': ['imperial_guard', 'imperial_decal'],
        'zhenyue_blade': ['school_melee'], 'beichen_spear': ['school_melee'],
        'liuyun_sword': ['school_melee'], 'chengying_sword': ['school_melee'],
        'zhuxing_bow': ['school_archery'], 'fengling_bow': ['school_archery'],
        'chiling_brush': ['school_talisman'], 'leifu_staff': ['school_talisman'],
    }
    # Conservative lower bound: only explicit method scopes contribute here.
    # Initial broad file ranges remain a separate pool, not silently credited to all weapons.
    goals = {item: {'required': 1000, 'explicitScopedMethodReviews': sum(per_scope[s] for s in ss),
                    'remaining': 1000-sum(per_scope[s] for s in ss), 'productionAllowed': False}
             for item, ss in scopes.items()}
    report = {
        'status': 'PASS' if not errors else 'FAIL_REQUIRES_DEDUP_REVIEW',
        'reviewedDistinctPool': len(accepted), 'reviewedSourceFiles': source_count,
        'repositories': len({r['repo'] for r in accepted}),
        'excludedRecords': len(excluded), 'candidateMethodsNotAutomaticallyReviewed': candidates['count'],
        'scopeCounts': dict(per_scope), 'targets': goals,
        'scopeCountPolicy': 'Conservative explicit-scope method counts; initial nine broad ranges not added to every target.',
        'dedupErrors': errors, 'sourceHashesAndLineRangesVerified': True,
        'candidateInventorySha256': sha((D / 'method-candidates.json').read_bytes()),
        'newPatternProductionAllowed': False, 'gameValidation': 'NOT_RUN',
        'notes': ['Source study is not game acceptance.',
                  'Semantic hash excludes identifiers, colors, numeric literals and comments.',
                  'Manual exclusions additionally merge copied algorithms and perspective adapters.',
                  'Candidate downloads and AST scans never count as reviewed implementations.']
    }
    (D / 'verified-research.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    (D / 'consolidated-reviewed.json').write_text(json.dumps({'rows': accepted, 'excluded': excluded}, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    assert not errors, 'Resolve duplicate reviews before counting them'


if __name__ == '__main__':
    main()
