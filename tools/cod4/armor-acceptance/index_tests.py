"""Index frozen test registrations; completion is established by the separate log and receipt."""
from pathlib import Path
import json,re,hashlib
b=Path(__file__).resolve().parent;root=b.parents[2];p=b/'src/ArmorAcceptanceGameTests.java';s=p.read_text();q=b/'src/QiConstitutionGameTests.java';qs=q.read_text()
loc=lambda text,needle:text[:text.index(needle)].count('\n')+1
rel=lambda path:str(path.relative_to(root))
sets=re.findall(r'"([a-z_]+)"',re.search(r'SETS=List.of\((.*?)\);',s)[1]);cases=[]
for name in sets:cases.append({'test':'matrix_'+name,'category':'native_equipment_matrix','fixture':'disconnected_ServerPlayer','source':rel(p),'line':loc(s,'@GameTestGenerator public static Collection<TestFunction> matrix()'),'observed_pass_marker':True,'actual_three_tier_behavior_acceptance':False})
inherited=re.findall(r'r.add\(test\("(existing_[^"]+)",([^:]+)::([^\)]+)\)\);',s)
for name,cls,method in inherited:cases.append({'test':name,'category':'inherited','fixture':'FakePlayer' if cls=='ExpansionGameTests' else 'disconnected_ServerPlayer','source':rel(p),'line':loc(s,'r.add(test("'+name+'"'),'delegate':cls+'::'+method,'human_multiplayer':False})
for name in ['cloth','bronze','phoenix','ziwei']:cases.append({'test':'window_'+name,'category':'new_regression','fixture':'disconnected_ServerPlayer','source':rel(p),'line':loc(s,'for(String set:List.of('),'trigger_level':'native_onFire_hurt' if name=='phoenix' else 'explicit_event_call','actual_equipment_tick':True})
new=re.findall(r'r.add\(test\("(?!existing_|window_)([^"]+)"',s)
for name in new:cases.append({'test':name,'category':'new_regression','fixture':'disconnected_ServerPlayer','source':rel(p),'line':loc(s,'r.add(test("'+name+'"'),'trigger_level':'explicit_step_and_damage_event_calls' if name in ['star_immunity_reads_live_gear','unworn_bronze_cannot_prestore_window'] else 'native_hurt_or_block_with_explicit_assertion_events','human_multiplayer':False})
for name in re.findall(r'public static void (\w+)\(GameTestHelper h\)',qs):cases.append({'test':name,'category':'inherited_qi','fixture':'disconnected_ServerPlayer','source':rel(q),'line':loc(qs,'public static void '+name),'trigger_level':'native_effect_API_and_explicit_equipment_or_tick_events','human_multiplayer':False})
assert len(cases)==len({c['test'] for c in cases})==63
log=(b/'evidence/final-current.log').read_text();observed=re.findall(r'ARMOR_MATRIX_PASS set=(\w+)',log);assert sorted(observed)==sorted(sets)
result={'count':63,'ordinary_ServerPlayer_fixtures':sum(c['fixture']=='disconnected_ServerPlayer' for c in cases),'FakePlayer_fixtures':sum(c['fixture']=='FakePlayer' for c in cases),'evidence':'final-current.log All 63 required tests passed and receipt exit_code=0; 28 matrix names separately logged','claim_boundary':'Inventory comes from executed frozen QA source registrations; it is not itself execution evidence or 84 live behavior acceptance. The completed log/receipt establishes suite success.','source_sha256':{rel(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [p,q]},'cases':cases}
assert result['ordinary_ServerPlayer_fixtures']==52 and result['FakePlayer_fixtures']==11
receipt=json.loads((b/'evidence/final-current-receipt.json').read_text())
assert all(v==receipt['inputs_sha256'][k] for k,v in result['source_sha256'].items())
(b/'evidence/test-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('63 case names cross-checked; 28 matrix pass markers; 52 disconnected normal /11 FakePlayer')
