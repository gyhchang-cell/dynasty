"""Sync only accepted art resources, with a compare-before-write ownership guard.

Requires accepted native runs for the exact current resource bytes. Never pushes,
stages Git, changes gameplay, or removes independent prompt acceptance conditions.
"""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from build_models import REPO, OUT

PRIMARY = Path('/Users/a15356015027/Desktop/dynasty')
PROMPTS = Path('/Users/a15356015027/Desktop/code x提示词')

def digest(data): return hashlib.sha256(data).hexdigest()

def main():
    accepted = json.loads((OUT/'accepted-runs.json').read_text())
    static = json.loads((OUT/'static-validation.json').read_text())
    baseline = json.loads((OUT/'source-snapshot.json').read_text())['files']
    previous = json.loads((OUT/'primary-sync.json').read_text())['files'] if (OUT/'primary-sync.json').exists() else {}
    files = {}
    native = {}
    for id, run in accepted.items():
        folder = OUT/'native'/run
        assert (folder/'PASS.txt').exists(), (id, 'native run failed')
        trees = json.loads((folder/'runtime-manifest.json').read_text())['trees']
        entries = {e['path']:e['sha256'] for e in trees[0]['files']}
        for path, sha in static[id]['resources'].items():
            assert digest((REPO/path).read_bytes()) == sha
            assert entries[path.removeprefix('src/main/resources/')] == sha, (id, 'unverified current bytes')
            files[path] = sha
        native[id] = run
    binding = 'src/main/java/com/dynasty/expansion/ExpansionClient.java'
    files[binding] = digest((REPO/binding).read_bytes())
    jar = REPO/'build/libs/dynasty-1.4.0.jar'
    with zipfile.ZipFile(jar) as z:
        assert not any('SecondaryArtClientQa' in n or 'QuietWindowAgent' in n for n in z.namelist())
        for p, sha in files.items():
            if p.startswith('src/main/resources/'):
                assert digest(z.read(p.removeprefix('src/main/resources/'))) == sha
    # Verify the compiled binding used by the latest native runtime is the build output.
    latest = json.loads((OUT/'native'/list(accepted.values())[-1]/'runtime-manifest.json').read_text())['trees'][1]
    classes = {e['path']:e['sha256'] for e in latest['files']}
    for cls in ['ExpansionClient.class','ExpansionClient$Model.class']:
        path = 'com/dynasty/expansion/'+cls
        assert digest((REPO/'build/classes/java/main'/path).read_bytes()) == classes[path]
    # ForgeGradle remaps production class names, so production class bytes are
    # expected to differ from the development classes used by the native client.
    assert digest(jar.read_bytes()) == digest((REPO/'build/reobfJar/output.jar').read_bytes())
    # All destinations must still be the frozen source, previous own sync, or current result.
    captured = {}
    for path, sha in files.items():
        dest = PRIMARY/path
        old = dest.read_bytes() if dest.exists() else None
        oldsha = digest(old) if old is not None else None
        assert oldsha in {baseline.get(path), previous.get(path), sha}, (path, 'concurrent change; refuse overwrite')
        captured[path] = old
    for path in files:
        dest = PRIMARY/path
        assert (dest.read_bytes() if dest.exists() else None) == captured[path], (path, 'changed during sync')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO/path, dest)
        assert digest(dest.read_bytes()) == files[path]
    artifact = PRIMARY/'build/maintenance-artifacts'/('art-20261011-'+str(len(accepted)))/jar.name
    artifact.parent.mkdir(parents=True, exist_ok=True);shutil.copy2(jar,artifact)
    record = {'files':files,'nativeRuns':native,'artifact':str(artifact),'jarSha256':digest(jar.read_bytes()),
              'scope':'Frozen isolated source plus accepted art; not a claim of all latest concurrent primary changes',
              'gameplayHumansPerformance':'Independent pending conditions retained'}
    (OUT/'primary-sync.json').write_text(json.dumps(record,indent=2)+'\n')
    # Shrink only the model-resource scope. All gameplay, ecology, polygon-budget,
    # multiplayer and performance lines remain byte-for-byte in the prompt file.
    prompt = PROMPTS/'cod4.txt';original = prompt.read_bytes();text = original.decode()
    lines = text.splitlines(keepends=True)
    index = [i for i,l in enumerate(lines) if l.startswith('[ ] 逐只核对原表要求的 silhouette') or l.startswith('[ ] 继续核对并修复其余')]
    remaining = sorted(p.name.removesuffix('.geo.json') for p in (OUT/'source').glob('*.geo.json') if p.name.removesuffix('.geo.json') not in accepted)
    assert len(index)==1 or (len(index)==0 and not remaining)
    replacement = '[ ] 继续核对并修复其余'+str(len(remaining))+'只（'+', '.join(remaining)+'）的 silhouette、分段骨骼、材质与七态动作；须在真实客户端检查。\n' if remaining else ''
    oldline = lines[index[0]] if index else ''
    if index: lines[index[0]] = replacement
    updated = ''.join(lines).encode()
    if updated != original:
        backup = PROMPTS/'美术重做原文备份-20261010'/('cod4-before-'+str(len(accepted))+'-art-'+digest(original)[:10]+'.txt')
        backup.parent.mkdir(parents=True,exist_ok=True)
        if backup.exists(): assert backup.read_bytes()==original
        else: backup.write_bytes(original)
        assert prompt.read_bytes()==original, 'Prompt changed during verification'
        prompt.write_bytes(updated)
        edits = json.loads((OUT/'prompt-edits.json').read_text()) if (OUT/'prompt-edits.json').exists() else []
        edits.append({'file':str(prompt),'backup':str(backup),'before':digest(original),'after':digest(updated),
                      'oldLine':oldline,'newLine':replacement,'acceptedArtIds':list(accepted),
                      'evidence':native,'independentConditionsRetained':True,'cod6Unchanged':True})
        (OUT/'prompt-edits.json').write_text(json.dumps(edits,ensure_ascii=False,indent=2)+'\n')
    progress = json.loads((OUT/'progress.json').read_text())
    progress.pop('completedArtPendingFinalCarp',None)
    progress.update(completedArt=list(accepted),remainingSecondary=remaining,primarySync='accepted resource bytes synced',nativeRuns=native)
    (OUT/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
    for own in ['docs/art/secondary-cuboid-v1','tools/art/secondary-cuboid']:
        shutil.copytree(REPO/own,PRIMARY/own,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    print('Synced',len(accepted),'accepted entities; remaining',len(remaining),'; JAR',record['jarSha256'])

if __name__=='__main__': main()
