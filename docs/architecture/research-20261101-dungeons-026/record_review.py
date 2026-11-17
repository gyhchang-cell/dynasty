#!/usr/bin/env python3
"""Manual review, explicit source limits and unchanged scoped totals."""
import copy
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
BASE=Path(__file__).resolve().parent.parent
KEYS=['layout','proportion','facade','roof','materials','circulation','terrain']
def get(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p.read_bytes()))
OBS={
 (24,'F01'):[
 '纵长低厅接偏置窄高段，y3是连续长房，y14仅余窄高段；不属于主要空间沿独立单塔竖轴叠置的岗位。',
 '保存15×40×21但非空气仅y0–25；最高细尖不能当40格塔身，长轴21也不符连厅范围24–29。',
 '低层大部围合长墙，窄高段只占一端，非独立守望塔的层台收放。',
 '长厅坡盖与单端尖盖叠接，尖帽高不作为独立守望室层。',
 '深板岩瓦、方解石、浅绿陶瓦及石木混合；分类色非原生贴图。',
 '原门(3,2,7)，梯(6,6)y3–7；原状态只证实短梯存在，不验证完整可行走路线。',
 '带草土地脚，2个socket未装配；fortified目录名不把普通村屋变为驻防堡。'],
 (24,'F02'):[
 '实际是长条低地脚/散置目标与植被，没有围合塔室主体，不能当完整驻守建筑。',
 '保存19×40×10，非空气仅y0–4；40格高度来自保存体积而非40格建筑。',
 '没有连续竖向立面，只有低栏和散置块。',
 '无完整房顶，不以保存空气体积补屋盖。',
 '草方块、草、土径、树叶和圆石为主，不能按渲染装饰色解读为高楼。',
 '无普通门梯，2个socket未扩展；低路径不是塔内动线。',
 '整片低地景零计数，不能因archer文件名视作高塔。'],
 (24,'F03'):[
 '低矮长房、偏置高房与低侧廊横向展开，y3长室/围墙清楚；不属竖向单塔。',
 '27×40×18保存体积，非空气仅y0–16；实际17格高，未达到独立塔25–53高度关系。',
 '长侧墙与侧廊立柱为主，不是守望塔的竖向墙筒。',
 '砖石高坡盖和低廊坡盖相接，坡屋盖不算额外守望层。',
 '土草、玄武岩、云杉板阶及橡木，材质不代替用途证据。',
 '单下半门(21,2,11)，无普通梯；未验证廊下碰撞。',
 '自带低地脚和2个socket，未装配外部部件；目录名不改范围。'],
 (25,'F01'):[
 '四外柱围中央细芯，中央小环台与巨大上平台上下排列；未见能直接确认普通驻守用途的围合室层。',
 '27×42×27，非空气y0–40；高细顶柱不是楼层。尺寸命中不能自动归同用途。',
 '外柱高度和上平台外挑明显，普通居室围护证据不足。',
 '顶部是大敞台与高细杆，非覆盖的普通守望室。',
 '末地石砖、紫珀柱阶和末地烛；不因异域材质本身排除，而因空间/岗位证据不足保留待查。',
 '无普通门梯；原实体含潜影贝及shulker_mimic，不能将特殊生物活动路线视为驻守人员路线。',
 '四柱自带低脚，无socket；尚缺作者用途与真实放置边界，保留完整主体证据而不宣称死资源。'],
 (25,'F02'):[
 '十字四臂围中央井，上接中央小高段，低层十字有大块实心区；没有独立院带边界。',
 '29×27×29，尺寸近堡营；不能单凭29格外包判定完整地面驻防布局。',
 '四臂窗口和中央高段同时存在，是否是完整岛上设施或嵌入主体的一段尚未确认。',
 '四向坡面/矮垛围中央帽，同F03破损态归一族，不能原状/破损各计。',
 '末地石砖及黑曜石；材料不作为新设计判据。',
 '无普通门梯；中央井不能自动视为可上下的梯井。',
 '同档案另有tower_bottom_open，未装配/未声称其就是本体必需件；地面完整边界与用途仍待查。'],
 (25,'F03'):[
 '同F02十字四臂、中央井和高段，局部顶端破损不生成第二设计。',
 '仍29×27×29；破损后的保存高不能另算实例。',
 '低臂与中央主段的围护组织对应F02。',
 '变化集中在顶端破口和少量盖面；空间原型沿用F02。',
 '同末地石砖与黑曜石组合，原状态差异已另表留档。',
 '同样无普通门梯；未把方块全格投影当碰撞或玩家路线。',
 '原状与破损同族零新增；岛面/下接边界未核实，继续待查。'],
 (27,'F01'):[
 '厚方筒包含低部腔室、y11入口房、y21上室，顶端大围栏平台；是完整竖向主体候选，但与当前守望岗位用途的对应尚不足。',
 '27×40×27，实际非空气y0–36，大段厚实体层夹房；不把40格保存体积或四面阶脚当多座塔。',
 '四面低入口及厚外筒，上部外挑、平栏与角柱共同成体；不能只凭spire名或垛口认定军用瞭望用途。',
 '大平顶带分隔图案和高角柱，没有各角独立屋室；上部平台不是四座塔。',
 '多种深板岩、goety岩墙及高岩砖，分类色合并自定义块；保留原状态，未替换本地资产。',
 '四个红树门下半在y11，两云杉门在y21；无普通梯。阶块和门记录仅为形态/入口证据，不声称已验证上下通行。',
 '四向阶脚与厚基部完整保存在同一NBT，无jigsaw；尚需作者功能与原生放置说明，保持待查而不借同规模凑数。'],
 (27,'F02'):[
 '与F01相同厚筒和房层组织，逐位置方块形态/状态对照用于同族归并。',
 '同27×40×27，不能把不同后缀当第二设计。',
 '四面入口和外挑顶栏对应F01。',
 '屋顶分隔和角柱对应F01，箱子或内部数据差异不新增建筑。',
 '主材和方块状态对照留档，不凭渲染色宣称全NBT相同。',
 '门位和朝向与F01相同；无普通梯，未原生行走。',
 '同地脚及零socket；与F01归一族，待查且额外计数0。'],
 (27,'F03'):[
 '房层、外筒和顶台对应F01，只见局部布置变化；同族不另计。',
 '同27×40×27，实际最高仍y36。',
 '相同四向入口与顶部外挑，不按局部内部陈设拆例。',
 '同平栏大平台，局部地面图案差异不等于另一完整设计。',
 '深板岩类原状态有少量差异，完整差异表保留，不称整栋完全相同。',
 '门位与F01相同，无普通梯；是否满足原岗位功能仍未证实。',
 '同地脚未额外装配，保留同族零计数。'],
 (27,'F04'):[
 '低平房与一侧院、局部高小段横向并列，是整体小驻所，非主要室层沿单塔叠置。',
 '21×26×26，非空气y0–23；长轴26小于当前堡营29–36，短轴21超连厅15–17，不能放宽范围挪计。',
 '平层院墙、侧阶和小高段并置，竖向部分不代表整栋独立塔。',
 '两块大平屋顶和小段顶，屋面高低不等于单塔多层守望。',
 '砂、切制砂岩与金合欢板为主；灰木渲染不是原生材质图。',
 '低层双门y3，上层门y8/y9和外阶存在；其中成排门也可能作装饰，不能按门数推断房间数。',
 '带低院地脚，原实体有掠夺者等，但军事实体不能纠正尺寸及空间范围不符；完整驻所保留0。']}
def normalize_metadata(n,folder):
 src=get(folder/'sources.json');evidence=[]
 for a in src['source_archives']:
  with ZipFile(a['path'])as z:
   docs=[]
   for member in ['META-INF/mods.toml','fabric.mod.json','quilt.mod.json']:
    if member in z.namelist():
     raw=z.read(member);docs.append(dict(member=member,sha256=sha(raw),text=raw.decode()))
  evidence.append(dict(source_archive=a['path'],documents=docs,network_requests=0))
  if n==25 and 'legendarymonsters'in a['path']:
   a['publisher_url']=None;a['url_access']='No publisher homepage is declared in inspected local metadata; no online lookup.'
  if n==27:
   a['publisher_url']='https://github.com/k1sak1/goetyawaken/issues'
   a['url_access']='Exact issueTrackerURL in local META-INF/mods.toml; provenance only, not requested online.'
 for c in src['candidates']:
  c['publisher_url']=next(a['publisher_url']for a in src['source_archives']if a['path']==c['source_archive'])
 dump(folder/'sources.json',src);dump(folder/'local-mod-metadata.json',dict(entries=evidence,
  limits='Local author declarations only, no online publication/version verification. Goety archive filename says 1.3.8 internal test while mods.toml declares 1.3.7; keep archive SHA as identity.'))
 return src
def main():
 parent=BASE/'research-20261101-dungeons-023/scoped-reference-update.json'
 for n in [24,25,26,27]:
  folder=BASE/f'research-20261101-dungeons-{n:03d}';entries=[]
  if n!=26:
   src=normalize_metadata(n,folder)
   for c in src['candidates']:
    decision=('EXCLUDE_SPACE_TYPE_OR_SIZE'if n==24 or(n==27 and c['id']=='F04')else
     'SAME_FAMILY_NO_ADDITIONAL_REFERENCE'if(n==25 and c['id']=='F03')or(n==27 and c['id']in ['F02','F03'])else
     'HOLD_FUNCTION_AND_WHOLE_PLACEMENT_EVIDENCE')
    entries.append(dict(id=c['id'],source=c,decision=decision,credit=0,
     observations=dict(zip(KEYS,OBS[(n,c['id'])])),
     actual_images_viewed=[ev(folder/f"{c['id']}-whole.png"),ev(folder/f"{c['id']}-details.png")],
     native_acceptance=False,independent_human_review=False))
  dump(folder/'manual-review.json',dict(entries=entries,actual_images_viewed=len(entries)*2,
   previously_unregistered_templates_visually_reviewed=len(entries),independent_references_added=0,
   reviewer='Same Codex agent; not independent human approval',
   scope_limit='Metadata rows, actors, changed contents, roof damage and fragments do not add whole designs. No automatic credit.'))
  prior=get(parent)
  update=dict(prior_update=ev(parent),original_scope_definitions=prior['original_scope_definitions'],
   scopes=copy.deepcopy(prior['scopes']),added_ids=[],added_credit=0,scope_definitions_changed=False,
   previous_two_holds_retained=['011-F04','012-F03'],other_holds_retained=['016-F01','019-F02'],
   new_hold_family_representatives=(['025-F01','025-F02']if n==25 else['027-F01']if n==27 else[]),
   previous_hold_evidence=prior['previous_hold_evidence'],
   independent_human_reviewer_claimed=False,production_changes=0,production_tasks_completed=0,checklist_deletions=0,
   limits='各范围分别1000，计数保持堡营6/独立塔8/连厅1。新资料审查不是有效计数；同族与待查0。')
  dump(folder/'scoped-reference-update.json',update);parent=folder/'scoped-reference-update.json'
  (folder/'HANDOFF.md').write_text(f'# 第{n:03d}批本地建筑研究\n\n本批实际查看{len(entries)}个新登记主体/地景候选、{len(entries)*2}张图；新增有效参考0。'
   '用途范围不放宽，旧阻塞不变，三类计数仍6/8/1。详见manual-review.json及scoped-reference-update.json。未制作建筑、未运行Java或游戏、未改任务/指南针/总清单。\n')
 metadata=get(BASE/'research-20261101-dungeons-026/all-structure-metadata.json')
 candidates=[r for r in metadata['entries']if r.get('size_prefilter_scopes')]
 # Every remaining size hit stays in a concrete queue. A filename-based hint
 # never becomes a semantic exclusion or a visual-reading claim.
 selected=set()
 for n in [24,25,27]:
  selected.update((c['source_archive'],c['member'])for c in get(BASE/f'research-20261101-dungeons-{n:03d}/sources.json')['candidates'])
 queue=[dict(source_archive=r['source_archive'],member=r['member'],size=r['size'],occupied_bounds=r['occupied_bounds'],
  stage='NOT_VISUALLY_REVIEWED_IN_THIS_BATCH_PRIOR_STATUS_REQUIRES_RECONCILIATION',credit=0)for r in candidates if(r['source_archive'],r['member'])not in selected]
 dump(BASE/'research-20261101-dungeons-026/remaining-size-review-queue.json',dict(entries=queue,
  count=len(queue),includes_previously_studied_rows=True,
  limits='Not a list of confirmed new buildings. Includes old sources, fragments, streets and unrelated uses; reconcile original identities before any next visual batch. Fixed sources are not semantically exhausted.'))
 needs=[dict(scope_id=s['scope_id'],accepted=s['accepted_references'],missing=s['remaining'],scope_definition=s['scope_definition'])for s in prior['scopes']]
 dump(BASE/'research-20261101-dungeons-027/source-needs.json',dict(scopes=needs,
  source_exhaustion_claimed=False,fixed_directory_metadata_complete=True,
  local_followups=['data/eeeabsmobs/structures/guling_1.nbt through guling_4.nbt: verify four pieces vs four complete designs before counting',
   'data/trek/structures/overworld/medium/offshore_platform_pillager.nbt: verify sea/platform placement and guard space before considering relevance',
   'data/totw_modded/structures/aether/aether_skyroot_1.nbt: verify full authored structure boundary, not just one layer'],
  held_source_requirements=['025-F01 shulker tower: author placement/use and ordinary guard-space organization, not just hostile entities',
   '025-F02/F03: author whole tower boundary including relationship to tower_bottom_open; original/damaged are one family',
   '027-F01/F02/F03: author intended use/placement and correspondence of room/platform organization to the current watchpost scope; variants are one family'],
  usable_source_requirements=['Whole relevant building examples with traceable author/project and unique design identity',
   'Complete NBT/schematic or documented whole assembly with entrance/room/roof/ground boundary; not isolated components',
   'If only pictures are available, enough layout/section/approach views to assess seven aspects and deduplicate one full design',
   'Chinese fortification/camp/watchpost examples of the existing purposes and scales; no screenshots, recolours, rotations or damage states counted twice'],
  network_requests=0,rate_limited_sources_retried=False,building_credit_added=0))
 (BASE/'research-20261101-dungeons-027/HANDOFF.md').write_text('# 第024–027批合并交接\n\n'
  '固定目录292个JAR内7139个结构NBT已完成离线尺寸元数据筛查，含5869个未命中关键词的成员；解析错误0。'
  '489条仅命中尺寸，其中374条未命中关键词。它们不是489座有效参考。\n\n'
  '实际新查看10个主体/地景候选、20张全景及选层图；新有效参考0。fortified村屋/射箭地景不等于塔，'
  '末地塔原状/破损归一族，boreal_spire三个版本归一族。后两类保留功能与完整放置边界待查；不把缺乏相同形状散列当独立性证明。\n\n'
  '堡营6/1000（缺994），独立塔8/1000（缺992），连厅1/1000（缺999）。原待查011-F04、012-F03、016-F01、019-F02保留。'
  '尚有元数据候选待作语义核查，因此没有声称固定源已穷尽。具体后续本地成员、待查缺失证据与合适新来源要求见source-needs.json；'
  '全量候选队列见第026批remaining-size-review-queue.json。\n\n'
  '未运行Java、游戏或网络请求，未制作建筑或改任务/指南针/总清单，未动声音、亮度、窗口及存档。'
  '联验入口为第026批verify_delivery.py；同代理证据验证不代表独立人工或游戏内验收。\n')
 for n in [24,25,27]:
  folder=BASE/f'research-20261101-dungeons-{n:03d}';path=folder/'discovery-boundary.json';boundary=get(path)
  changes=boundary.get('source_metadata_corrections',[])
  for e in boundary['indices_checked']:
   actual=sha(Path(e['path']).read_bytes())
   if actual!=e['sha256']:
    assert '/research-20261101-dungeons-025/sources.json'in e['path']
    changes.append(dict(path=e['path'],initial_sha256=e['sha256'],current_sha256=actual,
     reason='Removed provisional homepage link not declared in local author metadata; archive/member identities and NBT bytes unchanged.'))
    e['sha256']=actual
  boundary['source_metadata_corrections']=changes;dump(path,boundary)
 print('Recorded ten new screening candidates; all credit 0; totals remain 6/8/1.')
if __name__=='__main__':main()
