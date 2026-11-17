from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-network-acceptance'/sys.argv[1]
results=[json.loads(p.read_text()) for p in sorted(O.glob('result-*.json'))];assert results
checks={};fixed='ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b'
checks['fixed_jar_unchanged']=hashlib.sha256((R/'build/cod4-audit-20261022/verified-gradle/libs/dynasty-1.4.0.jar').read_bytes()).hexdigest()==fixed
cons=json.loads((O/'connections.json').read_text());checks['two_distinct_uuid_non_fake']=len(cons)==2 and len({c['uuid'] for c in cons})==2 and all(c['class']=='net.minecraft.server.level.ServerPlayer' for c in cons);checks['peer_tcp']='127.0.0.1:' in cons[1]['remote']
for role in ['host','peer']:
 manifest=json.loads((O/(role+'-manifest.json')).read_text());instance=Path(manifest['instance']);checks[role+'_own_four_jars']=manifest['total_mod_jars']==4 and all(hashlib.sha256((instance/'mods'/n).read_bytes()).hexdigest()==sha for n,sha in manifest['added_jars'].items());checks[role+'_complete']=(O/(role+'-COMPLETE')).exists();checks[role+'_exit0']=(O/(role+'-exit-code.txt')).exists() and (O/(role+'-exit-code.txt')).read_text()=='0'
 inputs=[]
 for case in results:
  n=case['index'];f=O/f'{role}-input-{n}.json';assert f.exists();v=json.loads(f.read_text());assert v['index']==n and v['name']==case['name'];inputs.append(v)
 checks[role+'_input_and_ack_every_result']=all((O/f'{role}-ack-{v["index"]}').exists() for v in inputs)
 views=[v for v in inputs if v['action']=='view'];checks[role+'_after_level_screenshot_every_view']=all((O/f'{role}-view-{v["index"]}.png').exists() and 'AFTER_LEVEL' in json.loads((O/f'{role}-render-{v["index"]}.json').read_text())['event'] for v in views)
 checks[role+'_every_view_two_players_tracked']=all(json.loads((O/f'{role}-render-{v["index"]}.json').read_text())['trackedPlayers']==2 for v in views)
# Exactly-one-death is independently checked from raw event records, not just assertion booleans.
deaths=[c for c in results if c['name'].endswith('/simultaneous-C2S-kill')]
checks['all_deaths_exactly_one_event']=all(c['after']['deathEvents']==1 and len(c['after']['drops'])==1 and c['after']['attackEvents']>=2 for c in deaths)
uuids=[e['uuid'] for c in deaths for ev in c['after']['drops'] for e in ev['entries']];checks['drop_entity_uuid_unique_across_corpses']=len(uuids)==len(set(uuids))
record={'run':sys.argv[1],'raw_case_count':len(results),'checks':checks,'structural_pass':all(checks.values()),'native_deaths':len(deaths),'drop_entities':len(uuids),'raw_failed_assertions':[{'index':c['index'],'name':c['name'],'checks':c['checks']} for c in results if not c['pass']]}
(O/'evidence-audit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
