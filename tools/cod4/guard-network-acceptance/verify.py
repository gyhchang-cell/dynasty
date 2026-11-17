"""Independently inspect real client receipts; never infer full-pack or survival acceptance."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/cod4/audit-20261022/guard-network-acceptance/run-04'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda name:json.loads((OUT/name).read_text())
connections=read('connections.json')
assert len(connections)==2 and len({p['uuid'] for p in connections})==2
assert any(p['remote'].startswith('/127.0.0.1:') for p in connections)
assert any(p['remote'].startswith('local:') for p in connections)
peer=next(p for p in connections if p['name']=='Cod4ArmorPeer')['uuid']
cases=[]
for n,ticks in [(7,95),(8,650)]:
    result=read(f'case-result-{n}.json');safety=read(f'guard-safety-{n}.json')
    assert result['passed'] and all(c['passed'] for c in result['checks'])
    assert safety['observedTicks']==ticks and safety['illegalPlayerTargets']==0 and not safety['playerAttackAttempts']
    assert not safety['forcedTargetOrDamage']
    if n==8:assert any(not h['canceled'] and h['amount']>0 for h in safety['positiveEnemyHits'])
    for role in ['host','peer']:
        sync=read(f'{role}-guards-{n}.json')
        assert sync['serverGuards']
        assert all(g['owner']==peer and g['entity'] in sync['trackedEntityIds'] for g in sync['serverGuards'])
        assert read(f'{role}-equipped-frame-{n}.json')['captureEvent']=='AFTER_LEVEL actual equipped world frame'
        assert (OUT/f'{role}-case-{n}.png').stat().st_size>1000
    cases.append({'case':n,'pieces':n-4,'native_observation_ticks':ticks,'assertions':len(result['checks']),'positive_native_guard_hits':len(safety['positiveEnemyHits'])})
assert len(read('guard-expect-8.json'))==2
assert all(g['generation']==2 for g in read('guard-expect-8.json'))
for role in ['host','peer']:
    assert (OUT/f'{role}-exit-code.txt').read_text().strip()=='0'
    assert (OUT/f'{role}-PASS').exists() and (OUT/f'{role}-COMPLETE').exists()
    manifest=read(f'{role}-manifest.json')
    assert manifest['total_mod_jars']==4
    assert manifest['private_patch_manifest']['all_other_entries_byte_identical']
    log=(OUT/f'{role}-client.log').read_text(errors='replace')
    assert 'GUARD_NETWORK_QA_WINDOW visible=0 focused=0' in log
    assert 'Stopping!' in log
    if role=='host':assert 'ThreadedAnvilChunkStorage: All dimensions are saved' in log
    instance=Path(manifest['instance'])
    assert 'soundCategory_master:0.0' in (instance/'options.txt').read_text()
assert (OUT/'server-PASS').exists() and (OUT/'server-COMPLETE').exists()
receipt={'status':'PASS_WITH_STATED_SCOPE','real_clients':2,'peer_transport':'actual localhost TCP','host_transport':'native integrated local channel','distinct_offline_player_uuids':2,'case_results':cases,'assertions_passed':sum(c['assertions'] for c in cases),'zero_guard_player_attack_attempts':True,'zero_observed_player_targets':True,'normal_host_and_peer_exit':True,'hidden_unfocused_windows_confirmed':True,'master_volume_zero':True,'production_overlay_entries':read('host-manifest.json')['private_patch_manifest']['changed_entries'],'all_other_baseline_entries_byte_identical':True,'original_worlds_touched':False,'full_modpack_verified':False,'whole_boss_fight_verified':False,'limitations':['Supplied equipment and water/health fixtures, not natural survival acquisition.','Client guard tracking receipts capture initial observed server list, not proof that both clients captured every regenerated pair.','Bystander is naturally moved by water during the observation; not asserted continuously within aggro range for all650 ticks.','No whole boss battle or model/texture/visual approval is inferred.'],'files':{f.name:sha(f) for f in OUT.iterdir() if f.is_file() and f.name!='verification.json'}}
(OUT/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},ensure_ascii=False))
