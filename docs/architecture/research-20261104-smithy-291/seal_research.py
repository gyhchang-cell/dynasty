"""Seal private source research only; never edit game assets or task lists."""
import json, hashlib, math
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
P=Path(__file__).resolve().parent
R=P.parents[2]
assert not (P/'RECEIPT.json').exists(), 'Sealed batches are immutable'
def ld(p): return json.loads(Path(p).read_text())
def put(n,v): (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve(); b=p.read_bytes()
 return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(label,value):
 assert value,label
 checks.append(label)
a=ld(P/'F02-source.json'); counts=ld(P/'source-counts.json'); d=ld(P/'F02-original.json')
ck('archive still exactly frozen source',bind(a['source_archive'])==counts['archive'])
with ZipFile(a['source_archive']) as z:
 ck('original source member exact',hashlib.sha256(z.read(a['member'])).hexdigest()==a['nbt_sha256'])
 for f in ld(P/'foundation-sockets.json')['foundations']:
  raw=z.read(f['member']); ck('foundation socket source '+f['member'],len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'])
 for f in ld(P/'original-context.json')['resources']:
  raw=z.read(f['member']); ck('full context JSON '+f['member'],raw.decode()==f['text'] and hashlib.sha256(raw).hexdigest()==f['sha256'] and json.loads(raw)==f['json'])
ck('original volume accounting',counts['stored']==65680 and counts['air']==44111 and counts['nonair']==21569 and counts['unknown']==44912 and math.prod(d['size'])==110592)
vectors=ld(P/'all-palette-property-vectors.json'); rebuilt={}
for g in vectors:
 for row in g['states']:
  v=dict(Name=g['name'])
  if g['keys']: v['Properties']=dict(zip(g['keys'],row[1:]))
  rebuilt[row[0]]=v
ck('all 593 palette states lossless',len(vectors)==167 and len(rebuilt)==593 and all(rebuilt[i]==v for i,v in enumerate(d['palette'])))
actual_BE={tuple(b['pos']):b['nbt'] for b in d['blocks'] if 'nbt'in b}; reconstructed={}
for g in ld(P/'all-BE-lossless-groups.json'):
 for pos in g['positions']: reconstructed[tuple(pos)]=g['nbt']
ck('48 unique NBT groups lossless 1066 positions',len(actual_BE)==1066 and len(ld(P/'all-BE-lossless-groups.json'))==48 and actual_BE==reconstructed)
profiles=ld(P/'entity-spatial-reading.json')
ck('57 entity position and identity profiles',len(profiles)==57 and all(v['pos']==d['entities'][i]['pos'] and v['id']==d['entities'][i]['nbt']['id'] for i,v in enumerate(profiles)))
dedup=ld(P/'historical-fingerprint-check.json'); ck('old candidate identity found, never new source identity',len(dedup['matches'])==1 and dedup['current']==dedup['matches'][0]['fingerprints'])
search=ld(P/'prior-own-record-search.json'); ck('bounded 272 own record search explicit',len(search['paths_checked'])==272 and search['hits']==[])
prior=ld(P/'prior-whole-comparison.json')
for e in prior['prior']: ck('previous comparison immutable '+e['entry']['id'],bind(e['binding']['path'])==e['binding'])
pngs=sorted(P.glob('*.png')); ck('20 actual-viewed source drawings exist',len(pngs)==20)
status='SEALED_ONE_WHOLE_SOURCE_STUDY_DUN04_SUBSPACE_ONLY_HOLD_ZERO_QUALIFIED_REFERENCE'
review=dict(
 batch=291,status=status,original_source=counts['archive'],member=a['member'],source_nbt_sha256=a['nbt_sha256'],publisher_url='https://www.curseforge.com/minecraft/mc-mods/ati-structures',
 source_url_boundary='Historical source attribution only; no current network verification or download.',
 new_complete_whole_studies=1,new_qualifying_reference_proposals=0,formal_credit_added=0,
 source_identity_was_previously_known=True,whole_source_first_read_boundary='Old B002 candidate explicitly UNREVIEWED_CANDIDATE_NOT_CREDITED. Current 272 bounded own-record files have no own fortified_temple entry. This is first completed spatial reading found in those records, not proof all chat history searched.',
 scope='cod2 DUN04 黑风阿兰若：仅寺院厅楼/侧塔组织的局部原则，不把平地堡寺当作已满足山道—崖窟—山顶烧毁大殿全布局。NPC01平民工坊不适用。',
 source_counts=counts,
 observations=dict(
  layout='同一连体堡寺内，东北厅楼、东南高厅通过中腰接合；西北中高厅与西南窄转梯塔形成不对称体量。下部隔间/储藏和上部房层、露台同属一个设计，不把各厅、侧塔、每层、屋盖分别计数。',
  proportion='保存48×48×48，实际非空气21569格；宽低基座承托高低不齐厅楼，东南主块最高到y45，西南侧塔檐盖约y33。保存y46/47不能作为另两层使用空间；不会以48格高误认48层。',
  facade='白/浅色墙身与红木色地板、深色檐饰分层，封闭房间与露台/栏杆/廊口并置。大量活板门、栅栏门、墙牌做立面与栏饰，分类立方体图只表示来源占位和材料类，不表现实际薄片与碰撞轮廓。',
  roof='多个不同高度的厚挑檐、台阶状收分屋盖和露台叠合；东北较低、西北及窄侧塔居中、东南高盖形成重心。y31处脚手架大面积保存，不能当作168条独立垂直交通。屋面灰色分类不等同真实全石瓦。',
  materials='主要为mushroom_stem2722、bone_block1427的浅墙，grass_block1576底面，red_carpet1047；birch_slab926、oak_planks889、birch_planks744、mangrove_planks651、dark_oak_stairs586等形成木质层次。369loom、128空beehive和112lectern部分用作纹理/家具，不能据数量推导生产能力。保留全部593原状态；含一项waterlogged spruce stair，不声称全无水状态。',
  circulation='已看全部48层平面与4整高剖面；原状态可见41扇门的上下半。西南塔双宽楼梯依次south y2..6、east7..11、north12..16、west17..21；随后原x5/6,z25/26有y22/23两步短阶转到y23平台，再接east24..28。短阶因长度2不在21条>=3直段候选内，并非楼梯缺失。部分落点有闭门、闭栅栏门、牌和活板门；y28落点x12,z30还有双格高围栏，旁道需检查。仅证明原楼梯/平台空间组织，未认证全通/安全通顶。SE下部另有south2..6与east7..10阶，SE高部east27..32阶接y32木台；中央birch west17..20、east21..26段分别有上半阶平台与墙牌。12格梯只是六组y11/12短梯，不是通顶梯。',
  terrain='根结构以WORLD_SURFACE_WG定位、rigid、terrain_adaptation none，适用平原/林地等原biome tag；不是源生峭壁寺院。主接头(23,0,23)down_west，target/name/pool均terrain_large，rollable，final dirt。两原terrain48³各仅一up接头(23,47,23)，指向匹配同名池，final dirt。按未旋转源坐标相邻对接推导地形原点偏移(0,-48,0)，只是源码接口关系，无最终现场高程、旋转选择、地形穿插、崖边栈道/洞窟证明。'
 ),
 actual_reading=dict(
  current_png=[bind(p)for p in pngs],current_png_actually_viewed=20,current_full_plan_layers_actually_viewed=48,current_whole_or_cut_isometric_sheets=6,current_full_height_section_planes=4,
  palette='593 states in 167 lossless name/property-vector groups actually read; not individually visiting every stored position.',
  block_entities='48 unique exact NBT payload groups actually read, preserving all1066 lossless positions; not claiming1066 independent interaction inspections.',
  entities='57 position/type/held/armor profiles actually read. Full original NBT is retained, but AI/attributes/item-frame contents not all manually read. Contains evoker/pillager/vindicator,4 armor stands and9 item frames; hostile source is not a populated civil monastery.',
  stair_endpoints='All21 flight endpoint name sequences read; selected full state/properties and SW short turn cells read. Full landing matrices retained as reproduction evidence, not claiming manual inspection of every matrix index.',
  context='All4 root/biome/temple pool/terrain_large pool JSON fully read. Both terrain NBT headers and all sockets read only; no full terrain spatial credit.',
  prior='Two own full seven-dimension observations plus credit/limits read. Historical images not reopened or recounted.'
 ),
 source_functions='All48 unique BE groups read: empty smelters/brewers/beehives, blank signs, source loot-table references,10 beds, one source book, one explicitly stocked chest and empty no-record jukeboxes. Loot tables themselves not read; references do not prove rolls, pickup, ownership or payment. Source book is not Chinese lore; no lyrics reproduced. No audio played.',
 relevance_decision='HOLD0。完成1个来源的完整建筑空间研究，但当前证据只对应DUN04厅楼/侧塔局部。缺山道入口、危崖高差、崖窟和烧毁大殿整体空间组织，不能自动增加目标1000计数。保留观察供后续完整相关案例归纳，不改生产资产。',
 applications=[
  '未来达到适用参考门槛后，可用不等高厅楼+独立窄转梯塔安排寺院垂直层次；设计前先确定平台/门/围栏净空，避免只放阶梯外观。',
  '以墙身、柱/栏、层间平台、挑檐和屋盖逐层收分区分体量；学习方法，禁止复制作者模板/材质冒充原创。',
  '目标山道→寺院→崖窟→山顶路径必须另有完整相关案例与地形证据；基础模块、地形块、半层和截图不分拆计建筑。'
 ],
 limits=[
  '无Java/Gradle/游戏/运行测试，无地形生成、碰撞、寻路或原生图像验收；源分类图不是游戏实景。',
  '敌对实体分布只说明来源保存内容，不证明任务战斗平衡、生成生态或Dungeon阶段。未改模组注册、任务、奖励、中文指南针。',
  'F01 monastery_tower此前已有实际研究，本批仅机器提取后排除。source.json/original.json属于F01；F02-source.json/F02-original.json才是当前fortified。F01/地形2模块/图数/21直段/593状态信用都0。',
  '旧221首次carry224、旧269首次carry277，本批均不重复carry。COD4正式153/缺847仅旧观察；NPC累计未知null，不据本批推算最新总数。',
  '初次指纹计算误含air，与旧nonair法不可比；封存前按旧法更正，准确匹配原B002。该更正和原始方法边界保留，不用首次无匹配宣称新设计。',
  '来源指纹仅原候选命中，无换名/旋转/换色新品证明；272文件搜索无自有阅读记录不等同全历史无重复。主协调仍可据额外证据否定首次完整阅读。',
  'Main仅收到元数据不等于Main实际看图/读源码或最终接受。本批自定HOLD0，不请求把阅图数量转为参考信用。',
  '只写本批研究目录，不写主清单、pending、ownership、共享Jar、专业资产、session或旧已封存批次；未删除任何任务，未提交推送。'
 ],
 COD4_accepted_old_observation=153,COD4_gap_old_observation=847,NPC_cumulative=None,old221_current_carry_increment=0,old269_current_carry_increment=0,tasks_deleted=0,all_tasks_complete=False
)
# Count source profiles rather than guessing entity composition in prose.
review['source_entity_type_counts']=dict(Counter(v['id']for v in profiles))
put('manual-review.json',review)
put('raw-foundation-interface.json',dict(host_socket=[23,0,23],host_front='down',desired_child_socket=[23,-1,23],child_original_socket=[23,47,23],unrotated_source_offset=[0,-48,0],derivation='(23,-1,23)-(23,47,23)',joint='rollable',native_generation_accepted=False,source_rotation_or_processor_executed=False,whole_building_credit=0))
protected=[]
for row in ld(P/'protected-before.json')['files']:
 before=row['before291']; after=bind(before['path'])
 protected.append(dict(before=before,after=after,unchanged=after==before,this_chat_wrote_file=False,concurrent_change_does_not_authorize_overwrite=True))
put('protected-current.json',dict(files=protected,boundary='Read-only observation of shared state; differences may come from other authorized work. Never overwrite or claim this chat owns them.'))
ck('production shared Jar unchanged',all(e['unchanged'] for e in protected if e['before']['path'].endswith('.jar')))
cp=ld(P/'active-checkpoint.json');cp.update(status=status,images_actually_viewed=20,new_complete_whole_studies=1,qualifying_reference_proposal=0,formal_credit_added=0,next='继续冻结本地来源中真正未完整阅读、用途/尺度/空间组织相关的完整建筑；无1000合格参考不制作。当前DUN04子空间原则HOLD0，主清单保留。')
put('active-checkpoint.json',cp)
ck('one whole source, no qualification/credit/task deletion',review['new_complete_whole_studies']==1 and review['new_qualifying_reference_proposals']==review['formal_credit_added']==review['tasks_deleted']==0)
put('verification.json',dict(passed=True,checks=checks,checks_count=len(checks),kind='Source consistency and private evidence accounting only; no runtime tests or independent acceptance',java_run=False,game_run=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file() and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=291,status=status,files=files,checks=len(checks),new_complete_whole_studies=1,new_qualifying_reference_proposals=0,formal_credit_added=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(e['unchanged']for e in protected),protected_total=len(protected)),ensure_ascii=False))
