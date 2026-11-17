#!/usr/bin/env python3
"""Manual whole-design decision after real source/layout/section reading."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def sha(b):return hashlib.sha256(b).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p.read_bytes()))
def get(p):return json.loads(p.read_text())
def dump(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
 src=get(OUT/'sources.json');c=src['candidates'][0];documents=[];actor_metadata=[]
 with ZipFile(c['source_archive'])as z:
  for member in ['data/trek/worldgen/structure/overworld/medium/offshore_platform_pillager.json',
   'data/trek/worldgen/template_pool/overworld/medium/offshore_platform_pillager.json',
   'data/trek/worldgen/template_pool/mobs/pillagers/pillager.json',
   'data/trek/worldgen/template_pool/mobs/pillagers/vindicator.json']:
   raw=z.read(member);documents.append(dict(member=member,sha256=sha(raw),data=json.loads(raw)))
  for member in ['data/trek/structures/mobs/pillagers/pillager.nbt','data/trek/structures/mobs/pillagers/vindicator.nbt']:
   raw=z.read(member);d=read(raw);pal=d.get('palette')or d['palettes'][0]
   actor_metadata.append(dict(member=member,nbt_sha256=sha(raw),size=d['size'],
    entities=[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id'))for e in d.get('entities',[])],
    sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{}))for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw'],
    actual_image_reading=False,placed_or_assembled=False,building_credit=0))
 dump('author-placement-evidence.json',dict(source_archive=c['source_archive'],documents=documents,actor_template_metadata=actor_metadata,
  inference_limits='Original author configuration establishes intended offshore illager use and specified guard sockets. Actor templates inspected only for role/connector semantics; no native placement, spawned positions or player collision route verified.',
  network_requests=0,java_run=False,game_run=False,actor_building_credit=0))
 observations={
 'layout':'宽脚架平台托下层棚室/棚台，沿同一高桅升至独立有盖小瞭望台；y41截面为四角柱，y40原socket明确选掠夺者。下部与上台为一个完整守望岗，不拆成两例。',
 'proportion':'整体25×48×21，位于独立塔15–27格平面、25–53格保存高范围；上部真实驻守点在y40，不能把旗帆高度折成额外房层。长细桅与宽低棚台有明确主次。',
 'facade':'下部横向栏边和棚体围护，上部只保留细桅、攀爬带和四柱小台；区别于旧例的连续墙筒、斜撑开台或宽台上紧凑上房，不仅是加高和换色。',
 'roof':'下层大棚坡盖上方出高桅，上端另有小盖覆盖瞭望台；侧向旗帆是悬挂构件，不当作墙或多个建筑。',
 'materials':'灰/青羊毛、深色橡木栏板活板门、链和梯为主；原方块名及朝向留档。仅学习棚台—细桅—小望台的组织，不复制贴图或声称适合中式立面。',
 'circulation':'原梯(13,8)y9–16、(12,7)y18–39，分别服务下部与高位；保留y17及转位处疑点，不声称无跳跃可通行。7个socket仅选择掠夺者/卫道士actor，没有外接建筑房片。',
 'terrain':'原生作者定义限定非冰冻海洋、高度偏移-6、无terrain_adaptation；带桩脚的独立海上岗位不是整个陆地古战场。当前用途范围未规定只能陆地，借鉴其小占地上下驻守组织，不据此完成海岸或地形生成验收。'}
 assembly_obs={
 'layout':'作者刚性定长下段与顶段接成一座细长轴塔，宽放射脚、窄攀爬轴和顶端开敞平台归一个整体设计；两个NBT不等于两座。',
 'proportion':'下段18×48×18，顶段18×10×18。上/下向对接原socket(0,47,0)/(0,0,0)，顶段平移(0,48,0)，完整保存18×58×18，实际非空气最高y57；超过独立塔53格上限。',
 'facade':'极细中轴带四向攀爬面，小段侧台与顶端宽台形成收放；无需因其接近参考题材就放宽高度。',
 'roof':'顶端平台有枝叶状轻帽与周边收口，完整冠部不能丢弃以把高度压回48格。',
 'materials':'按原天空根木/石木/叶类等方块原名记录，投影仅分类颜色；不复制为正式资产。',
 'circulation':'原底段四列梯分段，顶段y0–1平移为y48–49，跨接点连续部分留原状态；不把若干梯段存在当作全程攀爬验收。',
 'terrain':'作者start_pool、rigid、空处理器与 aligned socket共同限定这次零旋转拼合；保留高度图投影、碰撞与回边调度未执行的限制，不导出NBT或调用Java。'}
 controls=[
 ('011-F01','旧birch宽上房几乎占满上部轮廓；新例下棚与高位四柱小台相隔长细桅。'),
 ('011-F02','旧oriental同心层台逐级收尖；新例不是同心密叠平台。'),
 ('012-F01','旧forest偏置破损台与长外阶；新例以两段原梯和低棚/高台组织为主。'),
 ('012-F02','旧mushroom_fields束腰偏移房层；新例不是不规则错位室层塔。'),
 ('013-F01','旧snowy_plains并置小竖室和高低台；新例宽低棚与一根高桅小台关系不同。'),
 ('015-F01','旧mud连续闭合泥墙塔身；新例上部为开放细轴。'),
 ('016-F02','旧dark_forest由宽底斜撑收成两个无上室开台；新例有独立下棚盖和遥隔的有盖高望台，组织差异不只来自高度。'),
 ('013-F03','旧taiga开放底框托宽台及退进小上室；新例把棚室放在下部，高瞭望小台由长细桅分离。')]
 dump('manual-review.json',dict(entries=[dict(id='F01',source=c,decision='ACCEPT_ONE_COMPLETE_INDEPENDENT_WATCHPOST_REFERENCE',credit=1,
   credit_identity='028-F01',scope_id='DUN03-SINGLE-WATCHPOST',observations=observations,
   actual_images_viewed=[ev(OUT/'F01-whole.png'),ev(OUT/'F01-details.png')],native_acceptance=False)],
  assembly_entries=[dict(id='A01',decision='EXCLUDE_COMPLETE_AUTHORED_TOWER_OVER_SCOPE_HEIGHT',credit=0,
   source_component_ids=['C01','C02'],observations=assembly_obs,
   actual_images_viewed=[ev(OUT/'A01-whole.png'),ev(OUT/'A01-details.png')],native_acceptance=False)],
  semantic_comparisons=[dict(prior_identity=i,observation=o,additional_credit=0)for i,o in controls],
  prior_comparison_evidence=[ev(BASE/'research-20261101-dungeons-021/manual-review.json'),
   ev(BASE/'research-20261101-proposal-semantic-acceptance-010-015/scoped-reference-register.json')],
  historical_comparison_limit='Reuse previously actually read whole images/observations of eight credited designs; do not claim eight new image readings in this batch.',
  actual_new_images_viewed=4,whole_design_candidates_reviewed=2,architectural_source_templates_read=3,
  actor_templates_metadata_only=2,independent_references_added=1,
  independent_human_review_claimed=False,production_changes=0,checklist_deletions=0))
 parent=BASE/'research-20261101-dungeons-027/scoped-reference-update.json';old=get(parent);scopes=copy.deepcopy(old['scopes'])
 target=next(s for s in scopes if s['scope_id']=='DUN03-SINGLE-WATCHPOST')
 assert '028-F01'not in target['accepted_ids'];target['accepted_ids'].append('028-F01')
 target['accepted_references']=len(target['accepted_ids']);target['remaining']=1000-target['accepted_references']
 dump('scoped-reference-update.json',dict(prior_update=ev(parent),original_scope_definitions=old['original_scope_definitions'],scopes=scopes,
  added_ids=['028-F01'],added_credit=1,scope_definitions_changed=False,
  previous_two_holds_retained=['011-F04','012-F03'],other_holds_retained=['016-F01','019-F02'],
  recent_holds_retained=['025-F01','025-F02','027-F01'],previous_hold_evidence=old['previous_hold_evidence'],
  independent_human_reviewer_claimed=False,production_tasks_completed=0,production_changes=0,checklist_deletions=0,
  limits='三个用途单独1000。海上独立守望岗仅补其空间组织参考，不代表中式战场、瓮城、任务或指南针完成；58格作者原塔不得拆段挪计。'))
 (OUT/'HANDOFF.md').write_text('# 第028批：完整桅式守望岗与天境塔边界\n\n'
  '实读2个完整设计候选（3个建筑NBT），实际查看4张全景/选层图；新增有效参考1例028-F01。'
  '另2个actor模板只核对角色/连接元数据，不作建筑。\n\n'
  '028-F01：TREK offshore_platform_pillager，25×48×21。下部棚台、两段原梯和y40掠夺者连接位对应的高位有盖小瞭望台构成一个岗位；'
  '原作者配置限定海洋、monster spawn为掠夺者/卫道士。与旧8例逐项比较后按一例独立小守望岗记录，7个actor socket不多计。'
  '跨y17的路线和原生碰撞未验证；借鉴空间组织，不挪作整座中式战场或地形验收。\n\n'
  'A01：Towers of the Wild Modded，作者18×48×18下段与18×10×18顶段按up_south/down_south aligned socket零旋转接合，'
  '完整18×58×18、非空气y0–57。超过53格高度上限，计0。未丢顶段、未以两个NBT算两例，也未导出NBT或运行生成器。\n\n'
  '三个范围累计：堡营6/1000（缺994），独立塔9/1000（缺991），连厅1/1000（缺999）。范围定义与既有待查均不变。'
  '来源、七项观察、原始状态、去重和机械核验见本目录JSON；同代理证据核查不声称独立人工审批。'
  '未运行Java、游戏或网络请求，未改总清单、正式资产、任务、指南针、声音、亮度、窗口或存档。\n')
 print('Recorded 028-F01 once; excluded full 58-block A01; scoped totals 6/9/1, no production completion.')
if __name__=='__main__':main()
