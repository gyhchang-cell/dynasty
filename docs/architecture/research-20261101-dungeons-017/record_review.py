#!/usr/bin/env python3
"""Manual observations after actual whole/selected-section views; no scale drift."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ASPECTS=['layout','proportion','facade','roof','materials','circulation','terrain']
DATA=[
 ('EXCLUDED_SCOPE_SCALE','9格小石岗，尺度不足；不是现有25–53格高守望塔的新增例。',[
  '方形小室沿竖轴叠置，底部阶状外撇，中腰较开敞，顶台环短垛，无横向长厅或独立院。',
  '存储9×17×9，y12..16仅细旗杆／旗，主要顶台到y11；不能把旗高作为室层高度。',
  '厚石地脚收进窄中段，四侧开口夹短木构，顶台重新放宽；破损苔斑不是新空间。',
  '现存开放垛台，无覆盖平台的大屋盖；旗杆不是遮蔽屋顶。',
  'stone64、stone_bricks64、stone_brick_stairs27，苔石及少量木栏；分类色不代表原贴图。',
  '下门(1,1,4)朝西；梯(3,5)y1..4换至(5,3)y5..9，台内需转换位置。楼梯块含地脚饰边，未认证全程可走。',
  'y0有土石地脚；4个外围路径片接口不等于现有完整营地。未生成地形或验证基础入土。']),
 ('EXCLUDED_SCOPE_SCALE','11格小木岗，尺度不足；与旧015-F03等中心柱小塔仍需家族对照。',[
  '紧凑方形木室叠层，主塔身沿单轴，上端放宽为有栏台，底部一侧叶团不构成新翼。',
  '11×22×11，y16..21为细旗及旗杆，实际主要驻守体到y15；体量小于既定范围。',
  '四角深色木柱夹板墙和小开口，顶台托角、短垛及栏杆外挑。',
  '最高驻守台开放，栏及旗不能作为另一个有盖房间；不根据外观补造屋顶。',
  'dark_oak_planks139、dark_oak_log92、dark_oak_stairs56；石脚37及叶团25为底部层次。',
  '下门(5,1,3)朝北，内门(4,5,4)朝西；梯(6,6)y1..10再换至(5,4)y11..13，换梯关系保留而不宣称碰撞可达。',
  '小土脚、侧叶团与4个外围路径接口；路径和演员模板未拼装，不计为额外完整建筑。']),
 ('EXCLUDED_SCOPE_SCALE_AND_SHARED_FAMILY','低型红树林岗屋；与F04保留同族关系，不另立用途计数。',[
  '偏置木屋主体接一侧低平台，底层架空柱脚，上方单室再叠开放瞭望层，平台与主室相邻而非围院。',
  '12×12×11、屋盖y11，最下室门y4；不属于约15–27格平面、25–53格高的既定守望塔。',
  '木柱伸出方室墙角，低平台短栏、柱帽和外挑托构强调入口侧。',
  '方形浅盖、外缘阶块及四角托构，无长坡脊；不能按屋盖截图增加例数。',
  'mangrove_log109、mangrove_planks92、mangrove_stairs34，grass_block102及低层草叶为原存地脚。',
  '门(5,4,5)朝西，(6,4,4)/(7,4,4)朝北；梯(8,6)y4..7，连接室内与上层，未作原生通行认证。',
  '宽草地脚一侧承托低平台；三个pillager演员接口不改变完整岗屋数量，未证湿地生成高度。']),
 ('EXCLUDED_SCOPE_SCALE_AND_SHARED_FAMILY','高型红树林岗：基部、门与平台延续F03，伸高部分不能自动独立加例。',[
  '同一偏置屋体和侧低平台，向上延长柱筒／通道，顶部仍是窄开放层和浅方盖；没有独立院或厅翼。',
  '12×23×11；与低型保持相同平面，门由y4变y3。多一段高筒不足以证明独立设计；仍低于既定高度和占地。',
  '木柱、墙片及侧台托角延续低型，中间长段用细栏／墙件形成竖向节奏。',
  'y21浅方盖、y22少量叶片；与低型帽顶及上层围护关系相同，不能按升高盖顶计第二例。',
  'mangrove_log172、planks105、fence66、mud_brick_wall56、fence_gate48；新增中段材料不等于新布局。',
  '三处下门平面与F03完全相同但下移1；同轴梯(8,6)y3..17。保留真实长梯，不把其长度当独立布局证明。',
  '草地脚及侧平台沿用；四个演员接口不是另四栋，未装配任何外围营地或地形。'])]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def get(p):return json.loads(p.read_text())
def dump(name,d):(OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def scope_record(batch):
 original=BASE/'research-20261101-proposal-semantic-acceptance-010-015/scoped-reference-register.json'
 if batch==17:
  scopes=[]
  for s in get(original)['scopes']:
   r={k:s[k] for k in ['scope_id','scope_definition','accepted_ids','accepted_references','remaining']}
   if r['scope_id']=='DUN03-SINGLE-WATCHPOST':r.update(accepted_ids=r['accepted_ids']+['016-F02'],accepted_references=7,remaining=993)
   r.update(target=1000,construction_allowed=False);scopes.append(r)
  prior=BASE/'research-20261101-dungeons-016/scoped-reference-update.json'
 else:
  prior=BASE/f'research-20261101-dungeons-{batch-1:03d}/scoped-reference-update.json'
  scopes=get(prior)['scopes']
 if batch==19:
  s=next(s for s in scopes if s['scope_id']=='DUN03-MEDIUM-GROUND-GARRISON')
  assert s['accepted_references']==4
  s.update(accepted_ids=s['accepted_ids']+['019-F01'],accepted_references=5,remaining=995)
 if batch==20:
  s=next(s for s in scopes if s['scope_id']=='DUN03-MEDIUM-GROUND-GARRISON')
  assert s['accepted_references']==5
  s.update(accepted_ids=s['accepted_ids']+['020-F01'],accepted_references=6,remaining=994)
 return dict(prior_update=ev(prior),original_scope_definitions=ev(original),scopes=scopes,
  added_ids=[f'{batch:03d}-F01'] if batch in [19,20] else [],added_credit=1 if batch in [19,20] else 0,
  previous_two_holds_retained=['011-F04','012-F03'],scope_definitions_changed=False,
  previous_hold_evidence=ev(BASE/'research-20261101-dungeons-016/hold-review.json'),
  previous_hold_evidence_reopened_this_batch=False,independent_human_reviewer_claimed=False,
  production_tasks_completed=0,production_changes=0,checklist_deletions=0,
  limits='用途分别累计；未达各1000禁止制作。城堡／废塔研究不是15米夯土瓮城、全古战场或任务／指南针验收。')
def main():
 batch=int(OUT.name.rsplit('-',1)[1]);sources=get(OUT/'sources.json');dedup=get(OUT/'dedup-evidence.json')
 entries=[]
 for c,(status,reason,obs) in zip(sources['candidates'],DATA):
  assert len(obs)==7
  entries.append(dict(id=c['id'],source=c,decision=status,credit=0,reason=reason,
   observations=dict(zip(ASPECTS,obs)),actual_images_viewed=[ev(OUT/(c['id']+s)) for s in ['-whole.png','-details.png']],
   images_generated_but_not_viewed=[c['id']+'-plan.png',c['id']+'-vertical.png'],native_acceptance=False,
   exact_hash_absence_is_not_novelty=True))
 assert len(entries)==len(sources['candidates'])==len(DATA)
 dump('manual-review.json',dict(entries=entries,templates_studied=len(entries),actual_new_images_viewed=2*len(entries),
  independent_references_added=0,network_requests=0,java_run=False,game_run=False,
  historical_identities_screened=dedup['historical_unique_local_archive_member_pairs'],
  history_is_indexed_identities_not_all_visually_read=True,
  scope_boundary='固定原用途及尺度，不为小模板降低门槛；本批研究不自动成为新独立用途账本。',
  image_limits='分类色、整方块近似；紫色可能是门或jigsaw，青色亦可能为其他类别。门梯身份以原始方块状态为准；未验碰撞、地形、递归装配。'))
 dump('scoped-reference-update.json',scope_record(batch))
 print(f'Batch {batch}: {len(entries)} reviewed; 0 credited; original scopes unchanged.')
if __name__=='__main__':main()
