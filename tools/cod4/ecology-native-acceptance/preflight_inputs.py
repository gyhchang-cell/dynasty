"""Read-only final private-input validation, including declared presentation overrides.

This does not enable runtime_ready or update a frozen helper. It refuses any
unrecorded delta, symlink escape, missing byte, or changed copied world.
"""
from pathlib import Path
import argparse
import datetime
import json
from prepare_inputs import ROOT,EVIDENCE,BUILD,SOURCE,sha,manifest


def inspect(label):
    import re
    if not re.fullmatch(r'inputs-\d{2,}',label):raise ValueError('Explicit input label required')
    evidence=EVIDENCE/label;receipt=evidence/'session-inputs.json'
    data=json.loads(receipt.read_text())
    instance=Path(data['instance']);world=Path(data['copied_world'])
    expected_instance=BUILD/label/'host'
    if instance!=expected_instance or world!=instance/'saves/ecology-checkpoint':raise RuntimeError('Unexpected private input root')
    # resolve() equality covers root and ancestor symlinks, not only descendants.
    for path in [ROOT,BUILD,evidence,instance,world,Path(data['source_own_qa_checkpoint'])]:
        if path.absolute()!=path.resolve(strict=True):raise RuntimeError('No input root/ancestor symlink allowed: '+str(path))
    if Path(data['source_own_qa_checkpoint'])!=SOURCE:raise RuntimeError('Only already-owned QA checkpoint permitted')
    expected=data['world_files_sha256']
    if manifest(SOURCE)!=expected or manifest(world)!=expected:raise RuntimeError('Source or copied checkpoint changed')
    final={}
    for folder in ['mods','config','defaultconfigs','resourcepacks']:
        if (instance/folder).exists():final.update({folder+'/'+k:v for k,v in manifest(instance/folder).items()})
    options=instance/'options.txt'
    if options.is_symlink():raise RuntimeError('Symlink options rejected')
    final['options.txt']=sha(options)
    baseline=data['production_snapshot_sha256'];helper='mods/dynasty-ecology-native-acceptance-1.4.0.jar'
    allowed={'options.txt','config/fml.toml','config/dynamic_fps.json',helper}
    deltas={key:{'production_sha256':baseline.get(key),'private_sha256':final.get(key)}
            for key in set(baseline)|set(final) if baseline.get(key)!=final.get(key)}
    if not set(deltas).issubset(allowed):raise RuntimeError('Undeclared private delta: '+str(set(deltas)-allowed))
    if any(final.get(key)!=value for key,value in baseline.items() if key not in allowed):raise RuntimeError('Production file changed')
    if final.get(helper)!=data['private_helper_sha256']:raise RuntimeError('Frozen helper changed without integration receipt')
    fml=(instance/'config/fml.toml').read_text()
    if not re.search(r'(?m)^earlyWindowControl\s*=\s*false\s*$',fml):raise RuntimeError('Early window not disabled')
    if json.loads((instance/'config/dynamic_fps.json').read_text()).get('enabled') is not False:raise RuntimeError('Private dynamic FPS override missing')
    if 'soundCategory_master:0.0' not in options.read_text().splitlines():raise RuntimeError('Private mute setting missing')
    return {'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'READ_ONLY_FINAL_INPUTS_MATCH_DECLARED_FROZEN_SNAPSHOT',
        'session_inputs_sha256':sha(receipt),'preflight_source_sha256':sha(Path(__file__)),
        'private_final_files_sha256':final,'declared_actual_deltas':deltas,
        'world_files_verified':len(expected),'input_roots_and_ancestors_realpath_confined':True,
        'helper_version':'compile03 frozen snapshot; newer compiled helper not yet integrated',
        'runtime_ready':False,'game_started':False,'worlds_written':False,
        'newer_helper_integration_and_scene_driver_still_required':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('label');p.add_argument('output_name');a=p.parse_args()
    if Path(a.output_name).name!=a.output_name or not a.output_name.endswith('.json'):raise ValueError('Fresh JSON filename only')
    result=inspect(a.label)
    with (EVIDENCE/a.label/a.output_name).open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(result['status'],len(result['private_final_files_sha256']),'private files;',result['world_files_verified'],'world files; runtime_ready=false')
