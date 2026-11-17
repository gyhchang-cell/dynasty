"""Seal Japanese whole-house auxiliary study with zero formal credit."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
b=ld(P/'source-binding.json');d=ld(P/'source-original.json');c=ld(P/'source-counts.json')
ck('fixed archive unchanged',bind(b['archive']['path'])==b['archive'])
with ZipFile(b['archive']['path'])as z:
 raw=z.read(b['member']);ck('original NBT exact',hashlib.sha256(raw).hexdigest()==b['raw_sha256']and read(raw)==d)
 for row in ld(P/'source-context.json')['resources']:
  raw=z.read(row['member']);ck('original context '+row['member'],hashlib.sha256(raw).hexdigest()==row['sha256']and raw.decode()==row['text']and json.loads(raw)==row['json'])
ck('full source accounting',c['stored']==2548 and c['nonair']==926 and c['air']==1622 and c['omitted']==0 and c['stored']==math.prod(d['size']))
ck('palette BE entities accounting',len(d['palette'])==66 and len(ld(P/'all-BE-original.json'))==14 and not d['entities'])
ck('six images present',len(list(P.glob('*.png')))==6)
ck('old machine fingerprints no match',not ld(P/'historical-fingerprint-check.json')['matches'])
old=R/'docs/architecture/continuation-20261022/references/whole-candidates/review-batch-001.json';o=ld(old);lib=R/'docs/architecture/research-20261101-dungeons-007/manual-review.json';l=next(x for x in ld(lib)['entries']if x['id']=='F04')
put('complete-old-whole-comparison.json',dict(old_W018_binding=bind(old),review_method=o['review_method'],counting_boundary=o['counting_boundary'],historical_limits=o['limitations'],old_W018_whole_observations=o['accepted']['W018'],old_F04_binding=bind(lib),old_F04={k:l[k]for k in ['id','member','observations','independent_design_basis','status','proposed_target','credit_proposal','formal_credit_added','native_acceptance']},actual_current_reading='All eight W018 complete-own observations plus method/limits and all seven F04 observations/boundary read; old source images not reopened or counted.',current_comparison='旧W018方单室小祠9×13×9、单西门与三层收分盖，旧F04书屋同方室减盖/改内装早已判同族0。当前房为14×14×13两层四床、东西双门、一条四步内阶及上层箱，明确存在两张使用楼板而非新增屋顶层。但外框柱/深檐/白填墙同属该日式族，不凭放大、檐数、材质或用途ID单独加数，Main可判近族/题材HOLD0。旧祭祀范围信用不转给DUN05或客栈。'))
meta=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';entries=ld(meta)['entries'];terms=['chinese','chinatown','pagoda','teahouse','restaurant','oriental','japanese','inn']
selection=[{k:e[k]for k in ['member','size','source_archive','nbt_sha256']}for e in entries if any(t in e['member'].lower()for t in terms)and min(e.get('size')or[0])>=6]
put('bounded-local-topic-screen.json',dict(metadata=bind(meta),terms=terms,minimum_dimension=6,candidates=selection,boundary='Only saved fixed26 metadata names/sizes screened; not all disk/content or all Chinese architecture exhausted. Names are not actual viewing or style verification. Most nearby complete structures already read; current Japanese two-storey residence remains auxiliary, never relabelled Hui inn.'))
probes=ld(P/'actually-read-route-probes.json');m={tuple(v['pos']):d['palette'][v['state']]for v in d['blocks']}
ck('four original inner rising stairs',all(m[(x,y,4)]['Name']=='minecraft:spruce_stairs'and m[(x,y,4)]['Properties']['half']=='bottom'and m[(x,y,4)]['Properties']['facing']=='west'for x,y in [(8,2),(7,3),(6,4),(5,5)]))
ck('upper landing original floor and headroom',m[(4,5,4)]['Name']=='minecraft:spruce_planks'and all(m[(4,y,4)]['Name']=='minecraft:air'for y in [6,7]))
status='SEALED_ORIGINAL_JAPANESE_TWO_STOREY_DWELLING_AUXILIARY_HUI_INN_RELEVANCE_UNCONFIRMED_ZERO_FORMAL'
review=dict(batch=297,status=status,source=b,source_url='https://www.curseforge.com/minecraft/mc-mods/towns-and-towers',source_url_boundary='Historical original-source attribution reused from W018 candidate; no new network visit.',new_complete_source_whole_studies=1,new_qualifying_buildings_confirmed=0,auxiliary_reference_proposal_maximum=1,formal_credit_added=0,tasks_deleted=0,native_acceptance=False,
 actual_reading=dict(images_actually_viewed=6,images=[bind(p)for p in sorted(P.glob('*.png'))],all_plan_layers_actually_viewed=14,full_height_section_planes_actually_viewed=2,palette_states_actually_read=66,complete_BE_payloads_and_positions_actually_read=14,source_entities=0,complete_context_JSON_actually_read=4,saved_selected_coordinate_cells_actually_read=probes['count'],all2548_cells_individually_read=False,old_W018_eight_observations_and_old_F04_seven_dimensions_actually_read=True),
 seven_dimensions=dict(
 layout='一整栋日式双层民宅，底层floor1/use2完整室内两床分在西北与东南，东西各一闭门，中北单宽直阶向西上行；上层floor5/use6集中南侧两床和西南一箱。房内不是四个客房，也没有客栈公共厅/厨房/柜台。无待接住宅翼，街道/四村民接头分开记录，整屋四床和二层不拆数。',
 proportion='14×14×13/DV3105，全2548格存储=926nonair+1622显式air，零省略；66palette/14BE/entities[]。两生活层floor1和5，源y9..13主要高盖与空腔，最高y13屋脊，不能叫14层楼。底层8床块实为四完整床对，下两对/上两对；原高宽与檐外挑不等14格可用室宽。',
 facade='spruce_log142作框与梁，calcite56填墙，外四角立柱、低条裙和双层深檐；birch门下半(3,2,6)west及(10,2,6)east，实际两门非四。12原hanging lantern与若干栅/门构成细饰；y5两侧10closed fencegate是栏/檐下细构件，不把其全当首层入口。源无中文招牌、徽派马头墙或客栈名称。',
 roof='下层大檐位于y5附近，覆盖较大方形底室；上层小方室及其高双坡盖在y9..13，南北两坡逐层向z6脊收拢，端角有挑起薄半砖/小墙饰。deepslate brick slab106/tile slab104、brick stairs22/tile stairs36为真实盖材之一，类别灰图保留材质界限；屋盖高空腔不算可用第三层。没有屋顶连通街区或实测上房路线。',
 materials='四white床：下(5,2,3head/4foot)north、(8,2,8foot/9head)south；上(6/8,6,7foot/8head)south。唯一箱(4,6,8)north/single/dry，vanilla plains_house loot及seed1986455296729116469，无现存Items。本批未读loot表，不作稳定客栈库存/奖励。原无炉、食物制作台、工作柜台；不能仅四床认经营客栈。',
 circulation='西接街socket(0,1,6)west_up；源西三宽阶x1,y1,z5..7east，x2,y1,z6 top slab上y2/3air，门x3,y2/3,z6需开，内x4,y2/3,z6air且y4灯。东门外x11,y1,z6 top slab上y2/3air；完整外街未验。内阶(8,2,4)→(7,3,4)→(6,4,4)→(5,5,4)west bottom，上各两高air，西落脚(4,5,4)plank/y6/7air，南侧(5,5,5)也同；其北(5,6/7,3)为柱，不能任意绕行。箱前(4,6/7,7)air、箱上y7/8air只是静态开盖线索，碰撞/门动作/NPC和全屋路径未运行。',
 terrain='源grass/dirt低台和四角木柱、入口cobble台随本体保存，source y-1未知。四up mob sockets在lowerfloor两处/upperfloor两处，final spruce/birch planks，pool vanilla plains villagers未读取，不证明四居民出现或固定NPC。房在houses池weight4/legacy rigid/mossify10，fallback terminators；根从towncenters池两广场50/25起，不直接从本屋起，size6/max116/WORLD_SURFACE_WG/start0/beardthin/expansiontrue。花林及15 optional生物群系名已全文读；没读街道/广场NBT或执行随机处理，不能声称落地完整日式村、中华城或中文指南针。'),
 dedup='历史153NONAIR指纹无精确/role/occupancy匹配；旧manual/legacy ID review与ledger未命中本屋。旧007/059/084/118/146 source-context的名字仅houses池候选，旧285仅机器元数据actual_visual_readingfalse，均不是本屋已整栋阅图。机器无命中不证明所有别名/近族不存在，完整旧W018/F04对照已保存。',
 applicability=dict(target='DUN05狭窄商铺民宅与客栈、屋顶/石巷立体穿梭的辅助空间研究。',useful='双层木框住宅的四格楼面间距、阶前后净空、上层落脚与厚盖空腔可借鉴；一屋多床和同族深檐只形成一个完整实例。',unmet='日式花林民宅不是中式徽派城镇客栈，缺马头墙/中文招牌/营业分区/密集巷道与可达屋顶，正式0。Main可仅留辅助记录，不纳1000合格相关建筑。'),
 applications=['选择旧同题材完整建筑先比真实楼板和内阶，叠檐/换书架/缩屋顶不算新增空间。','分清入街标记、住宅实体边界、mob接头和实际使用层，不把生成配置当NPC验收。','方室深檐的外框宽度不能代替床边通道净宽；先核门阈/楼梯两高净空和顶端落脚。'],
 limits=['本轮新完整源研究1，正式合格确认0、正式信用0、最多1辅助候选待Main独立审查；未达1000不制作、不删任务。旧293–296信用和sealed文件保持历史原样。','6PNG分类色/完整方块近似不等原生材质/薄件碰撞；14全层和两整剖已看，2548原格保存不等全部逐格人工读。','未执行mossify处理/街道生成/村民池/loot/日夜雨或路径，source palette和属性原样保留，原native验收false。','仅写297目录，无贴图/人物模型/程序/主清单/session/pending/ownership/共享Jar/原档变化，不运行Java或游戏，不触声音亮度唤醒焦点/UI/实例/网络/Git/自动化。'],NPC_cumulative=None,all_tasks_complete=False)
put('manual-review.json',review)
protected=[]
for row in ld(R/'docs/architecture/research-20261104-smithy-296/protected-current.json')['files']:
 before=row['current'];after=bind(before['path']);protected.append(dict(previous296_observation=before,current=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,boundary='Compared with prior296 end observation, not a fabricated297 start; concurrent changes never reverted.'))
ck('shared jar unchanged since296',all(x['unchanged']for x in protected if x['current']['path'].endswith('.jar')))
cp=ld(P/'active-checkpoint.json');cp.update(status=status,images_actually_viewed=6,new_complete_source_whole_studies=1,new_qualifying_buildings_confirmed=0,auxiliary_reference_proposal_maximum=1,formal_credit_added=0,next='仅日式住宅辅助，优先继续固定本地未读且用途/尺度/动线相近整栋；中式不足不改题材或重复同族凑数。');put('active-checkpoint.json',cp)
put('verification.json',dict(passed=True,count=len(checks),checks=checks,java_run=False,game_run=False,independent_acceptance=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=297,status=status,files=files,checks=len(checks),new_complete_source_whole_studies=1,new_qualifying_buildings_confirmed=0,auxiliary_reference_proposal_maximum=1,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(x['unchanged']for x in protected)),ensure_ascii=False))
