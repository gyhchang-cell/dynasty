"""Install only independently reviewed evidence bytes; never publish acceptance."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / 'docs/cod4/audit-20261022/ecology-availability-research'
STAGE = Path(__file__).resolve().parent / '.work/terrapin-v5-draft'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    output = DOCS / 'coordinator-terrapin-v5-install-20261103.json'
    assert not output.exists()
    review_path = DOCS / 'independent-terrapin-v5-delta-review-20261103.json'
    review_raw = review_path.read_bytes()
    assert sha(review_raw) == 'b9db6442b34d473dbcd563b17ea949885f8275ede54ddc14ff96c06a369ab81a'
    review = json.loads(review_raw)
    assert review['status'] == 'INDEPENDENT_V5_DELTA_REVIEW_APPROVE_SCOPED_INSTALL_ONLY_NO_FORMAL_EA18_ACCEPTANCE'
    assert review['reviewer_thread_id'] == '01a12516-2eaf-73e2-b615-20f8b422158c'
    assert review['acceptance']['scoped_install_recommended'] is True
    assert review['acceptance']['formal_EA18_receipt'] is False
    for entry in review['bindings'].values():
        assert sha((ROOT / entry['path']).read_bytes()) == entry['sha256']
    manifest = json.loads((STAGE / 'manifest.json').read_bytes())
    for name, digest in manifest['files'].items():
        assert sha((STAGE / name).read_bytes()) == digest
    for entry in manifest['bindings'].values():
        assert sha((ROOT / entry['path']).read_bytes()) == entry['sha256']
    validator = Path(__file__).resolve().parent / 'receipt_validation.py'
    summary = validator.with_name('summarize.py')
    ledger_path = DOCS / 'master-acceptance-ledger.json'
    before_ledger = ledger_path.read_bytes()
    assert sha(validator.read_bytes()) == manifest['baseline_validator_sha256']
    assert sha(summary.read_bytes()) == manifest['baseline_summary_sha256']
    assert sha(before_ledger) == manifest['baseline_ledger_sha256']
    old_accepted = json.loads(before_ledger)['accepted']
    assert len(old_accepted) == 16
    assert not (DOCS / 'independent-reviews/general-EA0018.json').exists()
    batch_path = ROOT / manifest['formal_batch_target']
    assert not batch_path.exists()
    copies = json.loads((STAGE / 'source-copies.json').read_bytes())
    planned = []
    for destination, entry in copies.items():
        target = ROOT / destination
        data = (ROOT / entry['original']).read_bytes()
        assert sha(data) == entry['sha256']
        assert not target.exists() or target.read_bytes() == data
        planned.append((target, data))
    assert len(planned) == 7
    # All preconditions are checked before publishing any formal evidence bytes.
    for target, data in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open('xb') as handle:
                handle.write(data)
    with batch_path.open('xb') as handle:
        handle.write((STAGE / 'batch-013.json').read_bytes())
    validator.write_bytes((STAGE / 'receipt_validation.py').read_bytes())
    summary.write_bytes((STAGE / 'summarize.py').read_bytes())
    assert sha(batch_path.read_bytes()) == manifest['files']['batch-013.json']
    assert sha(validator.read_bytes()) == manifest['files']['receipt_validation.py']
    assert sha(summary.read_bytes()) == manifest['files']['summarize.py']
    for target, data in planned:
        assert target.read_bytes() == data
    # Actual installed source/receipt replay only; no synthetic receipt or ledger write.
    spec = importlib.util.spec_from_file_location('installed_terrapin_v5', validator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    by_id = {}
    for path in sorted(DOCS.glob('batch-*.json')):
        for record in json.loads(path.read_text())['records']:
            assert record['id'] not in by_id
            by_id[record['id']] = (path, record)
    accepted, validation, snapshot = module.aggregate(by_id)
    snapshot.stable()
    assert accepted == old_accepted
    assert ledger_path.read_bytes() == before_ledger
    assert not (DOCS / 'independent-reviews/general-EA0018.json').exists()
    result = {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'EXACT_REVIEWED_V5_EVIDENCE_INSTALLED_PENDING_REAL_GENERAL_EA18_RECEIPT',
        'independent_delta_review': {'path': str(review_path.relative_to(ROOT)), 'sha256': sha(review_raw)},
        'stage_manifest_sha256': sha((STAGE / 'manifest.json').read_bytes()),
        'installed_files': {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in [validator, summary, batch_path] + [p for p, _ in planned]},
        'actual_existing_acceptances_replayed_identically': len(accepted),
        'prior_master_bytes_unchanged': True, 'formal_general_EA18_receipt_written': False,
        'new_research_credit': 0, 'production_changes': 0, 'game_starts': 0,
        'checklist_deletions': 0, 'active_hours_claimed': 0,
        'next': 'Actual original independent source reviewer inspects installed formal package and separately creates genuine General EA18 receipt; only then aggregate.'
    }
    with output.open('x') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'receipt': str(output.relative_to(ROOT)), 'sha256': sha(output.read_bytes()), 'existing_acceptances': len(accepted), 'new_credit': 0}))


if __name__ == '__main__':
    main()
