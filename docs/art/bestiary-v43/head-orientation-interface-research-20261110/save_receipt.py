from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(rel,scope):
 p=ROOT/rel;return {'path':rel,'sha256':sha(p),'read_scope':scope}
PRE='build/item-use-references/bernie-g__geckolib/Forge/src/main/java/software/bernie/geckolib/'
sources=[entry(PRE+'model/GeoModel.java','33-52,170-285; handleAnimations, hook order and all applyMolangQueries; not entire file'),entry(PRE+'renderer/GeoEntityRenderer.java','88-100 instance ID; prior154-265 renderer data producer reused'),entry('src/main/java/com/dynasty/expansion/ExpansionClient.java','Model class32-47 has resource overrides only; prior full renderer chain reused'),entry('src/main/java/com/dynasty/expansion/SecondaryMob.java','STATE map110-113 and body controller358 reused; no new combat edits'),entry('src/main/java/com/dynasty/client/BossCuboidRenderer.java','133-158 actual head ticket consumer only; object-hiding code read as context, not altered'),entry('src/main/java/com/dynasty/client/BossFormsRenderer.java','27-49 hook context only; no object changes'),entry('src/main/java/com/dynasty/client/WhiteDeerRenderer.java','entire file; existing model without custom hook, not a new reference')]
ins=ROOT/'build/bestiary-v43/coregeomodel-interface-20261110/method-inspection.json';inspection=json.loads(ins.read_text());jar=ROOT/inspection['artifact']
with zipfile.ZipFile(jar) as z:
 assert hashlib.sha256(z.read(inspection['class_entry'])).hexdigest()==inspection['class_sha256']
assert sha(jar)==inspection['artifact_sha256']
body=[]
for n in ['swindler','herb_picker']:
 geo_rel=f'src/main/resources/assets/dynasty/geo/secondary/{n}.geo.json';anim_rel=f'src/main/resources/assets/dynasty/animations/secondary/{n}.animation.json'
 geo=json.loads((ROOT/geo_rel).read_text());anims=json.loads((ROOT/anim_rel).read_text())['animations']
 strings=[]
 def walk(x):
  if isinstance(x,str):strings.append(x)
  elif isinstance(x,list):
   for y in x:walk(y)
  elif isinstance(x,dict):
   for y in x.values():walk(y)
 walk(anims)
 body.append({'id':n,'head_bone':[{k:b.get(k) for k in ['name','parent','pivot','rotation']} for b in geo['minecraft:geometry'][0]['bones'] if b['name']=='head'],'selected_head_tracks':{c:anims[c]['bones'].get('head') for c in ['idle','special','flee','evade']},'all_clip_value_string_count':len(strings),'limits':'Numeric/string-value inspection only; no animation replay, runtime head tracking or source art reacceptance.'})
 sources += [entry(geo_rel,'head bone parent/pivot declarations only'),entry(anim_rel,'selected head tracks idle/special/flee/evade plus recursive string-value presence check; no full animation review')]
findings=[
'GeoEntityRenderer creates EntityModelData from body/head yaw difference and pitch, using negative netHeadYaw/headPitch in the data ticket. Merely producing this ticket does not rotate a named head bone.',
'Entity instance ID is entity.getId(), not the generic GeoRenderer hashCode default. GeoModel retrieves manager by this ID, tracks current-frame timing and avoids repeat processing of the same rendered instance/frame. This is source behavior, not multi-entity runtime acceptance.',
'GeoModel.handleAnimations performs processor setup/tick before calling setCustomAnimations. A local hook therefore runs after authored keyframe processing in the inspected path. Detailed current AnimationProcessor blending/transition behavior remains outside this bounded study.',
'Current dependency CoreGeoModel.setCustomAnimations is default no-op: exact bundled4.8.4 class method Code consists of single opcode b1(return), max_stack0. This was read as classfile bytes with Python; no Java/JVM run or full decompilation. Earlier cached4.4.4 processor source is explicitly not substituted for4.8.4.',
'ExpansionClient.Model does not override setCustomAnimations. For current two IDs the inspected model path therefore supplies no custom head-ticket-to-bone transform. Their numeric authored head tracks independently swing yaw between-3 and+3 degrees in idle/special/flee/evade; no Molang string expressions exist in either animation dictionary.',
'This does not mean head geometry is frozen: authored head/neck/ancestor animation and whole-entity rotation still apply. It only distinguishes authored motion from an explicit local look-at offset. No screenshot or runtime failure claimed.',
'Existing BossCuboidRenderer.Model supplies an explicit comparison: reads ENTITY_MODEL_DATA, exits for dying Mob, adds clamped data.netHeadYaw and headPitch (radians) to current head rotation. Limits .6yaw/.35pitch radians. This is a current project body implementation example, not a new creature reference or authority to transplant it into approved models.',
'Existing WhiteDeerRenderer and BossForms hook context were checked only to distinguish resource-only and other-purpose hooks. Neither is counted as a new independent body study, and their approved resources are untouched.',
'Any future look-at adaptation must preserve authored pose, verify data sign in the actual model coordinate basis, decide death/attack-state gating and account for additive reset. No clamp/sign/animation-timeline change is implemented under unmet applicable production gate.'
]
record={'recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'BOUNDED_HEAD_ORIENTATION_PRODUCER_DEFAULT_HOOK_AND_CURRENT_BODY_CONSUMER_REVIEW','sources':sources,'exact_core_default_hook_inspection':{'path':str(ins.relative_to(ROOT)),'sha256':sha(ins),'evidence':inspection},'current_body_track_observations':body,'findings':findings,'credit':{'new_distinct_creature_references':0,'new_accepted':0,'current_applicable_accepted_total':None,'gap':None,'historical_counts_unchanged':True},'limits':['No300-card rescan, no reacceptance of historical figures.','No production model, skeleton, animation, UV, PNG, collision, skill or sharedJar modification.','Body head/pose/attachment interface only; no armor or held/hanging object authored.','No Java/game/audio/brightness/focus/world operation.','Only explicitly listed source ranges and class method bytes inspected; no full runtime or full engine-source equivalence claim.']}
(HERE/'receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(HERE/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>头部朝向数据与实际骨骼消费者</title><style>body{max-width:1040px;margin:40px auto;background:#eeede8;color:#28343c;font:18px/1.7 sans-serif}li{margin:22px 0}</style><h1>有朝向数据，不等于骨骼自动转头</h1><p>GeckoLib4.8.4固定本地源码／依赖字节与当前身体接口研究。未修改认可模型；非实机验收。</p><ol>'+''.join('<li>'+html.escape(f)+'</li>' for f in findings)+'</ol><p><a href="receipt.json">精确范围、哈希、默认方法字节和现有头部轨道</a> · <a href="../secondary-body-renderer-research-20261110/index.html">前条身体受击与死亡显示链</a></p>')
verification={'source_hashes_match':all(sha(ROOT/s['path'])==s['sha256'] for s in sources),'exact_dependency_class_hash_matches':True,'core_default_hook_code':'b1','java_started':False,'production_modified':False,'historical_cards_rescanned':False,'old22_input_hash_check':'prior batch evidence retained; not rerun this turn'}
(HERE/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
def artifact(p):return {'path':str(p.resolve()),'sha256':sha(p)}
progress={'recorded_utc':record['recorded_utc'],'previous_progress':'docs/art/bestiary-v43/secondary-body-renderer-research-20261110/progress.json','receipt':artifact(HERE/'receipt.json'),'index':artifact(HERE/'index.html'),'verification':artifact(HERE/'verification.json'),'accepted_total':None,'gap':None,'new_accepted':0,'all_tasks_complete':False,'production_modified':False,'next':'Continue exact-version body/controller pose/reset consumer only where evidence remains missing; do not import4.4.4 state machinery into4.8.4 acceptance. Preserve existing applicability ledger and body/object ownership.'}
(HERE/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
handoff={'receipt':artifact(HERE/'receipt.json'),'progress':artifact(HERE/'progress.json'),'index':artifact(HERE/'index.html'),'verification':artifact(HERE/'verification.json'),'accepted_total':None,'gap':None,'new_accepted':0,'body_object_boundary':record['limits'][2]}
(HERE/'handoff-metadata.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'receipt':artifact(HERE/'receipt.json'),'progress':artifact(HERE/'progress.json'),'handoff':artifact(HERE/'handoff-metadata.json'),'verification':verification},ensure_ascii=False))
