from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,html
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
CACHE=ROOT/'build/bestiary-v43/references/justinwon777__HumanCompanions'
PREFIX='forge 1.20.1/src/main/java/com/github/justinwon777/humancompanions/'
SHA='e51a69df6784be5ab6368e2a774bfd71971d5f76'
scopes={
'client/renderer/CompanionRenderer.java':'entire file',
'client/event/ClientModEvents.java':'entire file',
'entity/ai/LowHealthGoal.java':'entire file',
'entity/ai/EatGoal.java':'entire file',
'entity/ai/ArcherRangedBowAttackGoal.java':'entire file',
'entity/Archer.java':'entire file',
'entity/AbstractHumanCompanionEntity.java':'40-85,108-155,415-432,480-510,589-635,665-720,726-738 only',
'entity/CompanionData.java':'125-136 skin table only'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
for rel,scope in scopes.items():
 p=CACHE/(PREFIX+rel)
 sources.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p),'read_scope':scope,'url':'https://github.com/justinwon777/HumanCompanions/blob/'+SHA+'/'+(PREFIX+rel).replace(' ','%20')})
atlas=CACHE/'forge 1.20.1/src/main/resources/assets/humancompanions/textures/entities/male/medieval-man-hugh.png'
sources.append({'path':str(atlas.relative_to(ROOT)),'sha256':digest(atlas),'read_scope':'original 64x64 PNG visually inspected; also sampled on native wide body offline','url':'https://github.com/justinwon777/HumanCompanions/blob/'+SHA+'/forge%201.20.1/src/main/resources/assets/humancompanions/textures/entities/male/medieval-man-hugh.png'})
native=ROOT/'build/bestiary-v43/references/native-human-1.20.1'
for rel,scope in {'net/minecraft/client/model/PlayerModel.java':'40-146','net/minecraft/client/model/HumanoidModel.java':'45-85,135-161,233-310','net/minecraft/client/renderer/entity/HumanoidMobRenderer.java':'entire file','net/minecraft/client/renderer/entity/layers/ItemInHandLayer.java':'entire file'}.items():
 p=native/rel;sources.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p),'read_scope':scope,'provenance':'read-only extraction; archive and entry hashes in native-human-1.20.1/source.json'})
views=json.loads((ROOT/'build/bestiary-v43/human-companions-source-20261110/views.json').read_text())
record={'recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'BOUNDED_STEVE_BODY_AND_ARM_STATE_REFERENCE_NOT_PRODUCTION_ACCEPTANCE','source_commit':SHA,'sources':sources,
'findings':[
'Four registered roles share CompanionRenderer and wide PlayerModel(false); one body implementation, not four independent rigs.',
'Native base body is six cuboids: head8x8x8, torso8x12x4, arms4x12x4, legs4x12x4. Hat and garment overlays retain this anatomy.',
'Wear shells copy limb/body transforms after super.setupAnim. Separate ear/cloak declarations are not ordinary bodyParts.',
'Renderer scale is 0.9375. Source views apply this model scale; no collision or world-size claim.',
'getArmPose selects BOW_AND_ARROW/CROSSBOW_CHARGE from used hand/use ticks and CROSSBOW_HOLD from charged state; main-arm mapping assigns left/right roles.',
'Archer AI feeds actual bow holding hand into startUsingItem; native HumanoidModel bow branch makes both arms follow head pitch/yaw with asymmetric yaw.',
'Inherited HumanoidMobRenderer installs ItemInHandLayer. Actual hand stack and arm translateToHand feed third-person item transforms; no item model authored.',
'LowHealthGoal only notifies owner to provide food. It is not a hurt/feign-injury animation reference.',
'EatGoal uses offhand item and synced eating flag; CompanionRenderer has no EAT pose branch. Do not infer visible eating animation from flag alone.',
'Archer goal canUse rejects eating, but canContinue may remain true while navigation is unfinished; no claim of immediate animation interruption.'],
'visual_observations':['Original atlas uses connected pale sleeves, teal vest, belt and boots rather than added anatomical boxes.','Front/side/back preserve wide Steve silhouette; clothing hierarchy comes mostly from UV color regions and thin wear shells.','Isolated bow panel demonstrates source arm branch only; no bow object, armor or runtime locomotion.'],
'views':views,
'dedup':{'reviewed_body_family_candidates':1,'roles_counted_separately':False,'skin_variants_counted_separately':False,'new_accepted_1000_gate_credit':0,'reason':'Applicable global semantic dedup and acceptance remain unconfirmed; source study is not quota acceptance.'},
'limits':['No full game or Java run.','No Dynasty runtime model, skeleton, animation, UV or texture modified.','Reference PNG stays in ignored build cache; not copied into runtime.','No claim of completed cod1-6 tasks or applicable 1000-reference gate.','Arbalist.java downloaded but not read; not included as studied.'],
'next':'Continue applicable semantically distinct body/recovery consumer study and global evidence reconciliation before gated production.'}
(HERE/'receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
old=json.loads((ROOT/'docs/art/bestiary-v43/body-joints-20261102/receipt.json').read_text())['input_sha256']
checks=[{'path':p,'matches_prior_receipt':(ROOT/p).exists() and digest(ROOT/p)==h} for p,h in old.items()]
verify={'source_hashes_match':all(digest(ROOT/s['path'])==s['sha256'] for s in sources),'view_hashes_match':all(digest(ROOT/v['path'])==v['sha256'] for v in views['views']),'historical_inputs':checks,'historical_input_count':len(checks),'historical_inputs_changed':[c['path'] for c in checks if not c['matches_prior_receipt']],'repeated_joint_sampling':False,'java_or_game_started':False}
(HERE/'verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n')
body='<html><meta charset="utf-8"><title>史蒂夫身体与手臂状态参考 · 2026-11-10</title><body style="background:#edece6;color:#252c2c;font:18px sans-serif;max-width:1200px;margin:36px auto"><h1>Human Companions：身体与手臂状态</h1><p>外部原始资源研究，非 Dynasty 新稿，非游戏截图。四种职业只计一个身体家族；本轮未新增1000门槛验收信用。</p><img style="width:100%" src="../../../../build/bestiary-v43/human-companions-source-20261110/overview.png"><p>从左至右：正面、45度、侧面、背面、原版持弓分支单独演示（不含武器）。</p><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in record['findings'])+'</ul><p>完整固定来源、阅读范围、哈希与局限见 <a href="receipt.json">receipt.json</a>。不把低血量提示、食物状态或四种换装职业冒充四套受伤动作。</p></body></html>'
(HERE/'index.html').write_text(body)
checkpoint={'recorded_utc':record['recorded_utc'],'role':'body-models-bones-animations-attachment-interface','latest_receipt':str((HERE/'receipt.json').relative_to(ROOT)),'receipt_sha256':digest(HERE/'receipt.json'),'verification':str((HERE/'verification.json').relative_to(ROOT)),'verification_sha256':digest(HERE/'verification.json'),'production_modified':False,'all_tasks_complete':False,'next':record['next']}
(HERE/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sources':len(sources),'views':len(views['views']),'verification':verify,'checkpoint':checkpoint},ensure_ascii=False))
