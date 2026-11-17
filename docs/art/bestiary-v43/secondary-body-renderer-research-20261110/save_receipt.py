from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
CACHE=ROOT/'build/item-use-references/bernie-g__geckolib';PIN='7d6f32db9168a24e14b327c0ad9f8f87dfc204de'
scopes={
'Forge/src/main/java/software/bernie/geckolib/renderer/GeoEntityRenderer.java':'class declaration40-51;154-265 render/animation/layer path;316-374 rotations;416-442 overlay',
'Forge/src/main/java/software/bernie/geckolib/renderer/GeoRenderer.java':'48-72 type/color;118-152 defaultRender;173-182 top-level bones delegation',
'Forge/src/main/java/software/bernie/geckolib/model/GeoModel.java':'94-103 default render type only',
'gradle.properties':'entire file; version4.8.4 and Minecraft1.20.1 identity'}
sources=[]
for rel,scope in scopes.items():
 p=CACHE/rel;sources.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'read_scope':scope,'url':'https://github.com/bernie-g/geckolib/blob/'+PIN+'/'+rel})
for rel,scope in {'src/main/java/com/dynasty/expansion/ExpansionClient.java':'17-58 registration/model paths/renderer overrides only; no particle changes','src/main/java/com/dynasty/expansion/SecondaryMob.java':'100-115,136-153,298-307,350-359; state mapping/update/hurt/controller; other battle logic not a new study','src/main/java/com/dynasty/client/steve/SteveFighterBindings.java':'entire file; named exceptions only'}.items():
 p=ROOT/rel;sources.append({'path':rel,'sha256':sha(p),'read_scope':scope})
clipnames={}
for n in ['swindler','herb_picker']:
 rel='src/main/resources/assets/dynasty/animations/secondary/'+n+'.animation.json';p=ROOT/rel;d=json.loads(p.read_text());clipnames[n]=list(d['animations']);sources.append({'path':rel,'sha256':sha(p),'read_scope':'animation dictionary keys only; no new full clip playback or curve acceptance'})
jar=ROOT/'libs/repo/software/bernie/geckolib/geckolib-forge-1.20.1/4.8.4/geckolib-forge-1.20.1-4.8.4.jar'
with zipfile.ZipFile(jar) as z:
 meta={n:{'sha256':hashlib.sha256(z.read(n)).hexdigest(),'text':z.read(n).decode()} for n in ['META-INF/MANIFEST.MF','META-INF/mods.toml']}
findings=[
'Exact pinned source snapshot declares GeckoLib4.8.4/Minecraft1.20.1. Repository dependency jar manifest and mods.toml declare4.8.4; jarSHA4518779a31b6c2abb92c98b5ad17ef3d60177df68626bfc86c44de2764913c2b matches prior isolated build snapshot. This is version/provenance confirmation, not bytecode-source equivalence or runtime loading proof.',
'GeoEntityRenderer extends EntityRenderer directly, not LivingEntityRenderer. Native LivingEntityRenderer research cannot by itself prove the GeckoLib body behavior; current follow-up reads GeckoLib consumers explicitly.',
'ExpansionClient registers SecondaryMobs.TYPES into its own GeoEntityRenderer, resolves per-ID geo and animation resources, and uses dedicated PNGs for swindler/herb_picker. The reviewed SteveFighterBindings named LOWEST list excludes both; this is bounded static registration evidence, not runtime final-renderer acceptance.',
'ExpansionClient Renderer does not override applyRotations/getDeathMaxRotation/getPackedOverlay. Only ghost family uses translucent type; only wandering_spirit has color multiply override. Neither applies to these two human IDs in this renderer.',
'GeoRenderer.defaultRender obtains renderColor and getPackedOverlay(animatable,0,partialTick), resolves baked model, then dispatches actuallyRender. Default color isWHITE; GeoModel defaults entityCutoutNoCull. This closes the actual packed-overlay producer/consumer handoff without claiming all shader overrides reviewed.',
'GeoEntityRenderer.getPackedOverlay selects native row3 while hurtTime>0 OR deathTime>0. Geometry animation is separate from this overlay; default red tint is not an authored body recoil clip.',
'GeoEntityRenderer.actuallyRender applies pose-stack rotations before adding AnimationState model data and invoking currentModel.handleAnimations. It continues handling model animation for a dead actor while passing zero locomotion values; it does not automatically select a death clip.',
'GeoEntityRenderer.applyRotations uses deathTime and the sqrt/cap formula with default getDeathMaxRotation90. This is whole-model Z rotation. Existing root/keyframe transforms occur inside that model transform; adding another collapse can compose with it and needs a deliberate review, not automatic double-fall accusations.',
'SecondaryMob.animation maps STATE into idle/wander/hunt/flee/attack/special/evade and named skills. The single body controller has transition4 and thenLoop(animation()). Neither native hurtTime nor deathTime directly chooses another clip here.',
'Server aiStep returns after super.aiStep when dead, before the custom STATE clock/update. Thus death does not author a new custom STATE through this method. Current animation dictionaries have19 clips each, none named hurt/death; presence of arbitrary other channels was not revalidated this turn.',
'SecondaryMob.hurt can select evade/flee, then swindler sets deceptionStage3 and STATEflee for200. Until exposed, swindler aiStep requests special repeatedly. These are gameplay state producers separate from native hurt tint; no gameplay timing edited.',
'GeckoLib4.8.4 source read closes the rendering state mechanism only. It does not satisfy per-creature art acceptance or a100/1000 semantic reference requirement and adds zero distinct creatures.'
]
record={'recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'BOUNDED_CURRENT_SECONDARY_BODY_DAMAGE_DEATH_RENDERER_CHAIN_READ_ONLY','sources':sources,'fixed_geckolib_commit':PIN,'dependency':{'path':str(jar.relative_to(ROOT)),'sha256':sha(jar),'metadata':meta,'source_binary_equivalence_proven':False},'findings':findings,'actual_clip_keys':clipnames,'scope_limits':['No gameplay/source/renderer fixes made.','No game/Java/GPU playback; inheritance and state evidence only.','No reference images or animation frame samples newly credited.','No armor/held-object/accessory model, PNG or UV made.','No exhaustive global event-registration/mixin/shader override audit; final runtime renderer remains unverified.','Existing body-joint animation QA is reused, not rerun or claimed as new acceptance.'],'ownership':{'body_specialist':'Body skeleton/controller and attachment transform interface evidence.','texture_specialist':'Armor/wornUV and held/hanging object model/texture/UV; untouched.'},'reference_credit':{'new_creature_families':0,'new_accepted_credit':0,'current_applicable_accepted_total':None,'gap':None,'historical_target100_and_static1000_preserved':True}}
(HERE/'receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(HERE/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>SecondaryMob 身体显示链 · GeckoLib4.8.4</title><style>body{max-width:1060px;margin:40px auto;background:#efeee8;color:#28343c;font:18px/1.7 sans-serif}li{margin:20px 0}</style><h1>当前身体的真实受击与死亡显示链</h1><p>GeckoLib4.8.4固定源码 → ExpansionClient → SecondaryMob STATE → body controller。只读研究，不是游戏验收。</p><ol>'+''.join('<li>'+html.escape(f)+'</li>' for f in findings)+'</ol><p><a href="receipt.json">来源、阅读范围、依赖身份与边界</a> · <a href="../reference-reconciliation-20261110/receipt.json">历史参考账有界对账</a></p>')
old=json.loads((ROOT/'docs/art/bestiary-v43/body-joints-20261102/receipt.json').read_text())['input_sha256']
verify={'sources_match':all(sha(ROOT/s['path'])==s['sha256'] for s in sources),'historical22_input_hashes_unchanged':all((ROOT/p).exists() and sha(ROOT/p)==h for p,h in old.items()),'production_changes':False,'game_started':False,'java_started':False,'native_runtime_verified':False}
(HERE/'verification.json').write_text(json.dumps(verify,indent=2)+'\n')
progress={'recorded_utc':record['recorded_utc'],'previous_progress':'docs/art/bestiary-v43/reference-reconciliation-20261110/progress.json','receipt':{'path':str((HERE/'receipt.json').relative_to(ROOT)),'sha256':sha(HERE/'receipt.json')},'index':{'path':str((HERE/'index.html').relative_to(ROOT)),'sha256':sha(HERE/'index.html')},'verification':{'path':str((HERE/'verification.json').relative_to(ROOT)),'sha256':sha(HERE/'verification.json')},'new_accepted':0,'accepted_total':None,'gap':None,'production_modified':False,'all_tasks_complete':False,'next':'Use reconciled target-specific evidence without resetting. Continue genuinely applicable unresolved authored body-state consumers; keep runtime acceptance pending and preserve approved art.'}
(HERE/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'receipt':progress['receipt'],'progress_sha256':sha(HERE/'progress.json'),'verification':verify},ensure_ascii=False))
