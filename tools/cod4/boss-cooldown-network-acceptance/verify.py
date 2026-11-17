"""Validate the isolated actual Boss AI/TCP receipts before closing the remaining armor row."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/cod4/audit-20261022/boss-cooldown-network-acceptance/run-01'
read=lambda n:json.loads((OUT/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=read('boss-cooldown-result.json');first=read('boss-first-save.json');fixture=read('boss-fixture.json')
assert result['passed'] and all(c['passed'] for c in result['checks'])
assert not result['clockModified'] and not fixture['manualAttackOrDamageCall']
assert fixture['type']=='dynasty:dragon_emperor' and fixture['isProductionBoss']
assert first['deadline']-first['tick']==6000 and first['alive'] and first['health']>0
hits=result['nativeDamage'];deaths=result['nativeDeaths']
a=next(h for h in hits if h['stage']==10);b=next(h for h in hits if h['stage']==11)
assert a['source']==b['source']==fixture['uuid'] and a['victim']==b['victim']
assert a['amountAfterProductionHandlers']==0 and b['amountAfterProductionHandlers']>0
assert a['bossNativeAI'] and b['bossNativeAI'] and a['tick']<b['tick']<first['deadline']
assert any(d['victim']==b['victim'] and d['tick']==b['tick'] and not d['canceled'] for d in deaths)
for name in ['death-respawn-checks.json','death-no-bypass-checks.json']:
    assert all(c['passed'] for c in read(name))
for role in ['host','peer']:
    assert (OUT/f'{role}-exit-code.txt').read_text().strip()=='0'
    for marker in ['PASS','COMPLETE','native-respawn-C2S']:
        assert (OUT/f'{role}-{marker}').exists()
    manifest=read(f'{role}-manifest.json')
    assert manifest['total_mod_jars']==4 and manifest['private_patch_manifest']['all_other_entries_byte_identical']
    log=(OUT/f'{role}-client.log').read_text(errors='replace')
    assert 'GUARD_NETWORK_QA_WINDOW visible=0 focused=0' in log and 'Stopping!' in log
    if role=='host':assert 'ThreadedAnvilChunkStorage: All dimensions are saved' in log
    assert 'soundCategory_master:0.0' in (Path(manifest['instance'])/'options.txt').read_text()
    assert read(f'{role}-death-capture.json')['captureEvent']=='AFTER_LEVEL real rendered world'
    assert (OUT/f'{role}-death-capture.png').stat().st_size>1000
host_log=(OUT/'host-client.log').read_text(errors='replace')
assert re.search(r'Cod4ArmorPeer\[/127\.0\.0\.1:\d+\] logged in',host_log)
assert re.search(r'Cod4ArmorHost\[local:[^\]]+\] logged in',host_log)
assert 'Connected to a modded server.' in (OUT/'peer-client.log').read_text(errors='replace')
assert len({p['uuid'] for p in read('host-death-capture.json')['trackedPlayers']})==2
assert (OUT/'server-PASS').exists() and (OUT/'server-COMPLETE').exists()
receipt={'status':'PASS_WITH_STATED_SCOPE','two_actual_clients':True,'peer_real_TCP':True,'registered_native_Boss_AI':True,'Boss':'dynasty:dragon_emperor','first_save_tick':a['tick'],'original_deadline':first['deadline'],'second_native_Boss_lethal_tick':b['tick'],'deadline_after_actual_C2S_re_equip_and_death':result['checks'][2]['after'],'all_checks_passed':True,'native_clock_modified':False,'manual_Boss_attack_or_damage_call':False,'hidden_unfocused_silent_clients':True,'both_clients_normal_exit':True,'original_world_touched':False,'full_modpack_or_whole_Boss_kill':False,'limits':'QA supplied armor, low starting health, water and nearby Boss spawn. AI frozen between actual attacks to allow deterministic C2S equipment/death progression. This validates the shared lastStand window, not natural survival or every Boss ability. Existing84-tier, repeat-equipment and6000tick expiry evidence remains separate.','files':{f.name:sha(f) for f in OUT.iterdir() if f.is_file() and f.name!='verification.json'}}
(OUT/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},ensure_ascii=False))
