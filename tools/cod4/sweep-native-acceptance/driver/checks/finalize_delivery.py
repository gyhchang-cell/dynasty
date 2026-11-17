"""Offline final input freeze + static prep contract checks. Never imports or executes prep/launcher."""
from pathlib import Path
import ast, hashlib, json, re, uuid, zipfile
R=Path(__file__).resolve().parents[5]
B=R/'tools/cod4/sweep-native-acceptance/driver'
D=R/'docs/cod4/audit-20261022/sweep-native-acceptance/driver'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def rel(p):return str(p.relative_to(R))
prep=R/'tools/cod4/sweep-native-acceptance/prepare_pair.py'; raw=prep.read_text();tree=ast.parse(raw)
source=B/'src/com/dynasty/sweepdriver/SweepStageDriver.java';java=source.read_text()
compile=load(D/'compile01.json');checks=load(D/'offline-checks01.json')
assert sha(source)==compile['source_sha256']==checks['source_sha256']
assert compile['status']=='PASS' and checks['status']=='PASS_OFFLINE_PROTOCOL_ONLY'
work=R/compile['work']
assert sha(work/'frozen/com/dynasty/sweepdriver/SweepStageDriver.java')==sha(source)
for p,h in compile['classes_sha256'].items():assert sha(work/'classes'/p)==h
# Inspect the actual AST; candidates/downloads are irrelevant here. No import of coordinator tooling.
def assigned_dict(name):
 matches=[n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
 assert len(matches)==1 and isinstance(matches[0],ast.Dict),name
 return {ast.literal_eval(k):v for k,v in zip(matches[0].keys,matches[0].values)}
props=assigned_dict('props');plan=assigned_dict('plan')
expected_props={
 'dynasty.sweepqa.enabled':'true','dynasty.sweepqa.instance':'str(instance)', 'dynasty.sweepqa.output':'str(out)',
 'dynasty.sweepdriver.enabled':'true','dynasty.sweepdriver.role':'role', 'dynasty.sweepdriver.bridge':'str(bridge)',
 'ecology.nativeqa.enabled':'false','ecology.nativegate.observe':'false','ecology.bounded.observe':'false'}
for k,v in expected_props.items():
 actual=ast.literal_eval(props[k]) if isinstance(props[k],ast.Constant) else ast.unparse(props[k])
 assert actual==v,(k,actual,v)
for k in ['run','private_root','host_instance','peer_instance','host_output','peer_output','host_uuid','peer_uuid','saved_world','bootstrap_existing_world','qa_sha256','driver_sha256','production_sha256']:
 assert k in plan and '"'+k+'"' in java,k
assert ast.literal_eval(plan['saved_world'])=='sweep-world' and ast.literal_eval(plan['bootstrap_existing_world']) is True
assert "not s.startswith('-Decology.')" in raw
assert "argv[argv.index(flag)+1]=value" in raw and "argv.count(flag)!=1" in raw
assert "'dynasty.sweepqa.instance'" in raw and 'SweepQA.OUT.toRealPath()' in java
identities={}; checkpoint=R/'build/cod4-mob-network-20261023/run-12/host/saves/mob-qa-1793198631800'
for role,expected in [('host','6c3ab68c-2707-3e49-bca5-7e82a37ca29f'),('peer','ca2fb277-2f95-3b5d-a212-139f545d2321')]:
 name='Cod4Mob'+role.title();u=str(uuid.UUID(bytes=hashlib.md5(('OfflinePlayer:'+name).encode()).digest(),version=3));assert u==expected
 p=checkpoint/'playerdata'/(u+'.dat');assert p.is_file()
 identities[role]={'username':name,'uuid':u,'native_uuid_arg':u.replace('-',''),'existing_checkpoint_playerdata':rel(p),'playerdata_sha256':sha(p)}
# Freeze only owned source/resources; no game directory/world/asset copy.
snapshot=work/'delivery01'
inputs=[source]+sorted((B/'resources').rglob('*'))
inputs=[p for p in inputs if p.is_file()]
freeze={}
for p in inputs:
 target=snapshot/p.relative_to(B);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert sha(target)==sha(p),'Refuse frozen input overwrite'
 else:target.write_bytes(p.read_bytes())
 freeze[str(p.relative_to(B))]=sha(target)
assert load(snapshot/'resources/pack.mcmeta')['pack']['pack_format']==15
srg=load(D/'coordinator-reobf01.json');assert srg['frozen_inputs']==freeze
assert sha(R/srg['jar'])==srg['jar_sha256']
with zipfile.ZipFile(R/srg['jar']) as z:
 for p,h in srg['archive_entries_sha256'].items():assert hashlib.sha256(z.read(p)).hexdigest()==h
old=load(D.parent/'metadata03-delivery.json')
prior={p:sha(R/p)==h for p,h in old['prior_files_sha256'].items()};assert all(prior.values())
qa_receipt=D.parent/'coordinator-reobf03.json';qa=load(qa_receipt)
qa_jar=R/'build/cod4-sweep-native-20261029/helper-build03/libs/dynasty-sweep-native-acceptance-2.0.jar';assert sha(qa_jar)==qa['jar_sha256']
quiet_receipt=R/'docs/cod4/audit-20261022/ecology-native-acceptance/inputs-01/helper-integration-compile20.json'
quiet=R/'build/cod4-ecology-native-20261028/inputs-01/host/mods/dynasty-ecology-native-acceptance-1.4.0.jar';assert sha(quiet)==load(quiet_receipt)['to_helper_sha256']
with zipfile.ZipFile(quiet) as z:
 mixins=json.loads(z.read('ecology-native-qa.mixins.json'));assert mixins['client']==['QuietWindowMixin']
 assert len(mixins['mixins'])==3 and json.loads(z.read('pack.mcmeta'))['pack']['pack_format']==15
prod_receipt=D.parent/'current-bundle-private-integration.json';prod=R/'build/cod4-sweep-native-20261029/current-bundle/dynasty-1.4.0.jar';assert sha(prod)==load(prod_receipt)['private_jar_sha256']
shared=R/'modpack/mods/dynasty-1.4.0.jar';assert sha(shared)=='0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
protocol_paths=[R/'tools/cod4/mob-network-acceptance'/p for p in ['src/com/dynasty/mobnetworkqa/MobNetworkAcceptance.java','run.py','launch.py','README.md']]
protocol_paths += [R/'tools/cod4/ecology-native-acceptance/launch_once.py',R/'tools/cod4/sweep-native-acceptance/pair_watchdog.py']
files=[p for p in B.rglob('*') if p.is_file() and '.work' not in p.parts and '__pycache__' not in p.parts]
result={
 'status':'FINAL_OFFLINE_DRIVER_DELIVERY_PREP_STATIC_CONTRACT_MATCH',
 'scope':'One new default-off private driver, no production or QA02 Java changes',
 'frozen_root':rel(snapshot),'frozen_inputs_sha256':freeze,
 'frozen_manifest_sha256':hashlib.sha256(json.dumps(freeze,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
 'official_classes':rel(work/'classes'),'official_classes_sha256':compile['classes_sha256'],
 'coordinator_SRG_jar':srg['jar'],'coordinator_SRG_jar_sha256':srg['jar_sha256'],
 'SRG_provenance':'Coordinator reobf01 independently read; no reobf/build repeated here',
 'delivery_files_sha256':{rel(p):sha(p) for p in sorted(files)},
 'prep':{'source':rel(prep),'sha256':sha(prep),'executed':False,'imported':False,'properties':expected_props,
         'plan_keys':sorted(plan),'identities':identities,'instance_output_binding':'host/peer and host-evidence/peer-evidence under same fresh private root; launcher game_directory=instance; actual gameDir and SweepQA.OUT checked by driver',
         'limits':['prep regex has no 30-character cap; use short sweepNN IDs <=30 chars','Changing driver SRG Jar requires updating coordinator receipt binding','Same-machine shared bridge/output filesystem only','Prepared inputs/final argv still need independent review before runtime'],
         'ecology_flags':'All existing -Decology.* removed; only three explicit false flags reinjected'},
 'quiet_compile20':{'jar':rel(quiet),'sha256':sha(quiet),'remaining_common_mixins':mixins['mixins'],
   'client_mixins':mixins['client'],'observation_flags_disabled':True,'mixins_removed':False,
   'actual_bytecode_read':rel(D/'quiet-compile20-bytecode.txt'),'actual_bytecode_sha256':sha(D/'quiet-compile20-bytecode.txt')},
 'QA03_jar_sha256':sha(qa_jar),'private_production_jar_sha256':sha(prod),'shared_production_jar_sha256':sha(shared),
 'prior_QA02_files_unchanged':prior,'protocol_sources_read_sha256':{rel(p):sha(p) for p in protocol_paths},
 'evidence_receipts_sha256':{rel(p):sha(p) for p in [D/'compile01.json',D/'offline-checks01.json',D/'coordinator-reobf01.json',qa_receipt,quiet_receipt,prod_receipt]},
 'offline_verification':{'real_Forge_QA_javac':True,'JDK_assertions':checks['assertions'],'schedule_combinations':36,'Minecraft_or_Forge_runtime_loaded_by_JDK_checks':False,'static_prep_contract_checks':True,'original_fixture_byte_copy_and_SHA_checks':True},
 'game_started':False,'prep_or_instance_copy_performed':False,'production_or_shared_Jar_written':False,
 'native_chat_C2S_TCP_verified':False,'pixels_reviewed':False,'overall_acceptance':False,
 'pending':['Independent source/SRG/prepared-input review','One coordinator-owned bounded hidden host/peer run','Actual age1 per view and six nonempty negatives','Full analyze.py calibration/identity/END coverage and original mesh/crescent coexistence checks','Manual first/third-person native pixel/shape/occlusion/composition review','Normal exit/save evidence; coordinator alone updates main TODO']}
(D/'final-delivery01.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:result[k] for k in ['status','frozen_root','frozen_inputs_sha256','frozen_manifest_sha256','official_classes','coordinator_SRG_jar','coordinator_SRG_jar_sha256','game_started','overall_acceptance']},indent=2))
