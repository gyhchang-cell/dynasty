"""Bind current local cuboid resources/JAR to accepted real native evidence."""
import hashlib
import json
from pathlib import Path
import zipfile
from cull_internal_faces import IDS, cull, geometry_without_uv

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / 'docs/art/secondary-cuboid-v1'
FACE = OUT / 'face-cull-v1'
LOAD_RUN = 'secondary-load20-gecko-final-06'
VIEW_RUN = 'secondary-cull-gecko-views-final-04'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def runtime(run, jar_sha):
    root = OUT / 'native' / run
    assert (root / 'PASS.txt').exists() and not (root / 'FAIL.txt').exists(), run
    manifest = json.loads((root / 'runtime-manifest.json').read_text())
    assert manifest['production']['jarSha256'] == jar_sha
    assert sha((REPO / 'build/secondary-art-native' / run / 'production.jar').read_bytes()) == jar_sha
    # Every actual runtime source byte matches the intended frozen build. Native
    # dev classes are not compared to reobfuscated SRG bytes as if equivalent.
    for tree in manifest['trees'][:2]:
        for f in tree['files']:
            assert sha((Path(tree['snapshot']) / f['path']).read_bytes()) == f['sha256'], (run, f['path'])
            assert sha((Path(tree['source']) / f['path']).read_bytes()) == f['sha256'], ('Build changed after run', f['path'])
    return root, manifest

def main():
    jar = REPO / 'build/libs/dynasty-1.4.0.jar'
    jar_sha = sha(jar.read_bytes())
    diff = json.loads((FACE / 'jar-diff.json').read_text())
    assert jar_sha == diff['afterJarSha256']
    assert jar.read_bytes() == (REPO / 'build/reobfJar/output.jar').read_bytes()
    before_jar = Path('/Users/a15356015027/Desktop/dynasty/build/maintenance-artifacts/art-guard-18/dynasty-1.4.0.jar')
    with zipfile.ZipFile(jar) as current, zipfile.ZipFile(before_jar) as old:
        assert set(current.namelist()) == set(old.namelist())
        changed = {n for n in current.namelist() if current.read(n) != old.read(n)}
        assert changed == {'META-INF/MANIFEST.MF'} | {f'assets/dynasty/geo/secondary/{id}.geo.json' for id in IDS}
        assert not any('ClientQa' in n for n in current.namelist())
        for id in IDS:
            for rel in (f'geo/secondary/{id}.geo.json', f'animations/secondary/{id}.animation.json', f'textures/entity/secondary/{id}.png'):
                assert current.read('assets/dynasty/' + rel) == (REPO / 'src/main/resources/assets/dynasty' / rel).read_bytes()
    proof = json.loads((FACE / 'occlusion-proof.json').read_text())
    software = json.loads((FACE / 'software-comparison.json').read_text())
    for id in IDS:
        before = json.loads((FACE / f'before/{id}.geo.json').read_text())
        actual_bytes = (REPO / f'src/main/resources/assets/dynasty/geo/secondary/{id}.geo.json').read_bytes()
        actual = json.loads(actual_bytes)
        assert geometry_without_uv(before) == geometry_without_uv(actual)
        cull(before); assert before == actual
        assert sha(actual_bytes) == proof[id]['afterSha256']
        assert software[id]['comparedAnimationViews'] == 228 and software[id]['largestChangedPixelCount'] == 0
    view_root, _ = runtime(VIEW_RUN, jar_sha)
    states = [json.loads(p.read_text()) for p in sorted(view_root.glob('*-state.json'))]
    assert len(states) == 33 and {s['entity'] for s in states} == set(IDS)
    for id in IDS:
        matched = [s for s in states if s['entity'] == id]
        assert len(matched) == 11
        for s in matched:
            assert s['nativeBaked']['cuboids'] == proof[id]['cuboids']
            assert s['nativeBaked']['nonNullQuads'] == proof[id]['facesAfter']
            assert s['nativeOcclusionProof']['omittedFacesChecked'] == proof[id]['facesBefore'] - proof[id]['facesAfter']
            assert s['nativeOcclusionProof']['survivingFacesUnchanged'] == proof[id]['facesAfter']
        assert len(list(view_root.glob(f'*-{id}-*.png'))) == 11
    load_root, _ = runtime(LOAD_RUN, jar_sha)
    measurements = [json.loads((load_root / f'{i:02d}-state.json').read_text()) for i in range(5)]
    for i, r in enumerate(measurements):
        assert r['frames'] >= 120 and len(r['frameIntervalsMs']) == len(r['renderedCounts']) == r['frames']
        assert r['count'] == (0 if i == 0 else 20)
        assert r['medianFrameMs'] < 50 and r['p95FrameMs'] < 100
        if i:
            assert r['all20RenderedFraction'] >= .9 and r['entitiesWithActualBoneMotion'] >= 18
        if i in (2, 3):
            assert all(not a['noAi'] for s in r['serverSamples'] for a in s['actors'])
    ground = measurements[2]; ranged = measurements[3]
    assert ground['movedOver1Block'] >= 18 and len(ground['actorsBuiltNonemptyPaths']) >= 18 and len(ground['actorsTraversedPathNodes']) >= 18
    assert ranged['projectiles'] >= 40 and ranged['acceptedHits'] >= 40
    assert len(ranged['shooters']) >= 18 and len(ranged['hitters']) >= 18
    assert ranged['particlePeak'] >= 60 and ranged['actorsRenderedNaturalSpecial'] >= 18
    assert measurements[1]['baked']['locust_swarm']['nonNullQuads'] == proof['locust_swarm']['facesAfter']
    assert ranged['baked']['tree_spirit']['nonNullQuads'] == proof['tree_spirit']['facesAfter']
    report = {'jarSha256': jar_sha, 'nativeViews': VIEW_RUN, 'nativeLoad': LOAD_RUN,
              'visualReview': 'Five software views plus native original front/45/side/back and load frames must be inspected separately.',
              'geometryPreserved': True, 'removedInvisibleFaces': sum(v['facesBefore'] - v['facesAfter'] for v in proof.values()),
              'softwareAnimationViews': sum(v['comparedAnimationViews'] for v in software.values()),
              'measurements': [{k: r[k] for k in ['stage', 'count', 'viewport', 'frames', 'medianFrameMs', 'p95FrameMs', 'serverAverageTickMs', 'particlePeak', 'projectiles', 'acceptedHits']} | ({'all20RenderedFraction': r['all20RenderedFraction']} if i else {}) for i, r in enumerate(measurements)],
              'groundActorsMoved': ground['movedOver1Block'], 'groundBuiltPaths': len(ground['actorsBuiltNonemptyPaths']), 'groundTraversedPaths': len(ground['actorsTraversedPathNodes']),
              'realRangedShooters': len(ranged['shooters']), 'realRangedHitters': len(ranged['hitters']),
              'promptParagraphDeleted': False,
              'remaining': 'Original basic-mob face budget not met; whole cod4 performance paragraph retained. Fixtures/automatic client do not satisfy humans, natural ecosystems or long gameplay.'}
    (FACE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 72 invisible faces omitted without losing cuboids; native33 and native20 AI/particles bound to exact JAR', jar_sha)

if __name__ == '__main__':
    main()
