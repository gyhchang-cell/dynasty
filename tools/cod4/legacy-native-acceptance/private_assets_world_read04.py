"""Bind private official assets to the unused read01 attempt; no launch without new review."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().with_name('world_read_plan.py')
BASE_SHA = '2f1190fe322faad836405bffd0e38f0489c4b7d3d4d2544b4ad7713c999f95fa'
DOC = ROOT / 'docs/cod4/audit-20261022/legacy-native-acceptance'
PREP = DOC / 'coordinator-private-official-assets-preparation-20261109.json'
PREP_SHA = 'a2a3a57aea8b2d1e416b4915f3a336e1eda382e3a95a17659310833ba4ab5882'
ASSETS = ROOT / 'build/cod4-legacy-native-20261102/assets-official-5-20261109'
REVIEWER = '01a12516-2eaf-73e2-b615-20f8b422158c'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def base_tool():
    # Read exact reviewed source bytes, never .pyc or an ambient imported module.
    raw = BASE.read_bytes()
    assert sha(raw) == BASE_SHA, 'Base world-reader source changed before import'
    spec = importlib.util.spec_from_file_location('_legacy_private_assets_base', BASE)
    module = importlib.util.module_from_spec(spec)
    exec(raw, module.__dict__)
    return module


def snapshot(base):
    # This only hashes/reads existing inputs; it calls none of prepare/plan/run.
    observed = base.snapshot()
    pair = base.pair
    raw = pair.canonical(PREP).read_bytes()
    assert sha(raw) == PREP_SHA, 'Private assets preparation changed'
    prep = json.loads(raw, object_pairs_hook=pair.unique_object)
    assert prep['status'] == 'PREPARED_PRIVATE_FIXED_OFFICIAL_ASSETS_ONLY_NO_RUNTIME_APPROVAL'
    assert prep['root'] == str(ASSETS)
    assert pair.canonical(ASSETS).parent == base.BUILD
    files = pair.manifest(ASSETS)
    assert files == prep['files'] and len(files) == 3576
    index = ASSETS / 'indexes/5.json'
    index_raw = index.read_bytes()
    assert hashlib.sha1(index_raw).hexdigest() == '50ce48459eb9e29836662862273d7b15d41c2c33'
    official = ROOT / prep['official_source']['path']
    assert official.read_bytes() == index_raw and sha(index_raw) == prep['official_source']['sha256']
    original_argv = list(observed['argv'])
    argv = list(original_argv)
    assert argv.count('--assetsDir') == argv.count('--assetIndex') == 1
    assets_arg = argv.index('--assetsDir') + 1
    assert argv[assets_arg] == str(pair.MC / 'assets')
    assert argv[argv.index('--assetIndex') + 1] == '5'
    argv[assets_arg] = str(ASSETS)
    assert [i for i, (a, b) in enumerate(zip(original_argv, argv)) if a != b] == [assets_arg]
    # Keep the complete original runtime bindings as conservative inputs, even
    # though this attempt now reads assets from the independently copied tree.
    observed['schema'] = 'legacy-one-owned-world-read-private-assets-v1'
    observed['argv'] = argv
    observed['private_assets'] = {'root': str(ASSETS), 'files': files,
                                  'index_sha1': hashlib.sha1(index_raw).hexdigest(),
                                  'source_url': prep['official_url']}
    observed['private_assets_argv_delta'] = {'index': assets_arg,
                                            'before': original_argv[assets_arg],
                                            'after': argv[assets_arg]}
    observed['tools'].update(pair.bind_files([Path(__file__), BASE]))
    observed['inputs'].update(pair.bind_files([PREP, official]))
    return observed


def review_documents(base):
    pair = base.pair
    ready_path = pair.canonical(base.RUN / 'reviewed-world-read-ready04.json')
    raw = ready_path.read_bytes()
    ready = json.loads(raw, object_pairs_hook=pair.unique_object)
    rel = Path(ready['independent_review'])
    assert not rel.is_absolute() and '..' not in rel.parts
    report_path = pair.canonical(ROOT / rel)
    assert report_path.is_relative_to(DOC) and report_path != ready_path
    report_raw = report_path.read_bytes()
    assert sha(report_raw) == ready['independent_review_sha256']
    report = json.loads(report_raw, object_pairs_hook=pair.unique_object)
    assert ready['status'] == 'READY_FOR_ONE_BOUNDED_LEGACY_WORLD_READ_PRIVATE_ASSETS'
    assert report['status'] == 'INDEPENDENT_READY_FOR_ONE_BOUNDED_LEGACY_WORLD_READ_PRIVATE_ASSETS'
    for d in (ready, report):
        assert d['reviewer_thread'] == REVIEWER and d['one_attempt_only'] is True
        assert d['private_root'] == str(base.RUN) and d['private_assets'] == str(ASSETS)
    assert ready['snapshot_sha256'] == report['snapshot_sha256']
    return ready, report, sha(raw), sha(report_raw)


def run(base):
    documents = review_documents(base)
    observed = snapshot(base)
    assert documents[0]['snapshot_sha256'] == base.pair.digest_json(observed)
    # Current platform admission only after the new complete input/review bind.
    base.pair.require_awake()
    base.require_no_game()
    assert snapshot(base) == observed, 'Inputs changed after platform observation'
    assert review_documents(base) == documents, 'Independent readiness changed'
    marker = {'ready_sha256': documents[2], 'independent_review_sha256': documents[3],
              'snapshot_sha256': base.pair.digest_json(observed), 'one_attempt_only': True,
              'private_assets': str(ASSETS)}
    # Exactly the same unused read01 marker, not a replacement attempt/world.
    base.write(base.RUN / 'execution-started.json', marker)
    watchdog = base.pair.load_tool('_legacy_private_assets_owned_watchdog',
        ROOT / 'tools/cod4/ecology-native-acceptance/watchdog.py',
        base.pair.REVIEWED_METADATA_SHA['watchdog.py'])
    result = watchdog.run_owned(observed['argv'], instance=base.HOST, evidence=base.OUT,
        startup_seconds=240, runtime_seconds=300, absolute_seconds=600,
        save_grace_seconds=60, term_grace_seconds=15)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['plan', 'run'])
    args = parser.parse_args()
    base = base_tool()
    if args.mode == 'plan':
        observed = snapshot(base)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
        target = base.RUN / ('snapshot-private-assets-not-ready-' + stamp + '.json')
        base.write(target, observed)
        print(json.dumps({'status': 'PLANNED_PRIVATE_ASSETS_NOT_RUNTIME_READY',
                          'snapshot': str(target.relative_to(ROOT)),
                          'snapshot_sha256': base.pair.digest_json(observed),
                          'snapshot_file_sha256': sha(target.read_bytes()),
                          'game_starts': 0, 'marker_consumed': False}))
    else:
        run(base)
