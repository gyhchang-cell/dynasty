"""Seal only this unsealed batch's bounded component exclusions; no game execution."""
import json,hashlib,math,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def restore(v):
 if isinstance(v,dict):
  if set(v)=={'__original_nbt_byte_array_hex__'}:return bytes.fromhex(v['__original_nbt_byte_array_hex__'])
  return {k:restore(w)for k,w in v.items()}
 if isinstance(v,list):return [restore(w)for w in v]
 return v
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
raw=get('raw-source-audit.json')['candidates'];ctx=get('source-context.json');screen=get('pre-render-history-screen.json');cases=[];functional=[];context_notes=[]
why=[{'purpose':'开放式武器工棚和额外塔段接口，不当完整民用山脚铁匠铺。','observed':'长形木框浅灰篷顶，侧面开放；西侧小台与4,3,3向上jigsaw连接后续tower_pieces；模板高21但非air仅y0..7，不是21层/高塔。工作台、磨具和水缸都在y0，脚下y-1模板未含，不把外部地面视为已验完整地板。','boundary':'4jigsaw含2grunt角色点、1empty入口与1塔段连接，不当4建筑/已生NPC；未装配塔段/整座营地，不计本棚为完整相关建筑。'}, {'purpose':'开放式营地工棚，未建立独立完整工坊地面与顾客/工住空间。','observed':'单长棚，木框浅灰篷顶、两端旗帜；同层smith/grind/watercauldron在y0，底下y-1不在源内。没有门/热加工炉/床/梯，角色jigsaw不是实体或住宅房间。','boundary':'wooded_badlands同源bytealias已于渲染前排除，不新增第三建筑。仅保存当前两源初筛，未做全层完整相关建筑家族研究。'}]
for a,r,reason in zip(get('sources.json')['candidates'],raw,why):
 ident=a['id'];sr=next(x for x in screen['rows']if x['id']==ident)
 check(ident+' history/raw/role/occupancy pre-render exclusion',sr['eligible_for_new_source_study']and not any(sr[k]for k in ['known_history','historical_exact_matches','within_batch_exact_matches']))
 check(ident+' fixed archive unchanged',bind(a['source_archive'])==sr['fixed_archive'])
 with ZipFile(a['source_archive'])as z:
  b=z.read(a['member']);d=read(b);pal=d['palette'];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);mp={tuple(x['pos']):pal[x['state']]for x in d['blocks']}
  check(ident+' original source lossless',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']and d==restore(r['nbt_decoded_original']))
  check(ident+' original positions bounds full stored no omission',len(mp)==len(d['blocks'])==math.prod(d['size'])and all(0<=x['state']<len(pal)and all(0<=x['pos'][i]<d['size'][i]for i in range(3))for x in d['blocks']))
  check(ident+' full material/air count',dict(counts)==r['material_counts']and sum(counts[n]for n in AIR)==r['air']and len(d['blocks'])-r['air']==r['nonair'])
  for alias in sr['same_bytes_aliases']:check(ident+' same Jar alias bytes excluded not extra body '+alias,z.read(alias)==b)
  x0=6 if ident=='F01'else 3;gx=8 if ident=='F01'else 5
  check(ident+' ground smith grind water original',mp[x0,0,8]['Name']=='minecraft:smithing_table'and mp[gx,0,7]=={'Name':'minecraft:grindstone','Properties':{'face':'floor','facing':'east'}}and mp[gx,0,8]=={'Name':'minecraft:water_cauldron','Properties':{'level':'3'}})
  check(ident+' no heat beds ladder door anvil entities',d['entities']==[]and all(counts[n]==0 for n in ['minecraft:blast_furnace','minecraft:furnace','minecraft:smoker','minecraft:lava','minecraft:anvil','minecraft:ladder'])and not any(n.endswith(('_bed','_door'))for n in counts))
  check(ident+' no nonair above7 despite dimensions',max(x['pos'][1]for x in d['blocks']if pal[x['state']]['Name']not in AIR)==7)
  check(ident+' actual DV and exact volume material totals', (d['DataVersion'],len(d['blocks']),r['nonair'],r['air'],len(pal))==((3578,3780,300,3480,56)if ident=='F01'else(3105,1080,228,852,43)))
  c=next(x for x in ctx['candidates']if x['id']==ident)
  for m in [x for x in ctx['metadata']if x['id']==ident]:check(ident+' metadata '+m['member'],hashlib.sha256(z.read(m['member'])).hexdigest()==m['sha256']and z.read(m['member']).decode()==m['original_text'])
  for cc in c['contexts']:check(ident+' context '+cc['member'],hashlib.sha256(z.read(cc['member'])).hexdigest()==cc['sha256']and json.loads(z.read(cc['member']))==cc['json'])
  check(ident+' no missing recorded contexts',not c['missing'])
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if x['member'].endswith('/side/workshop.json'));el=pool['elements'][0]
  check(ident+' exact selected side pool not root body',len(pool['elements'])==1 and el=={'weight':1,'element':{'location':c['location'],'processors':'minecraft:empty','projection':'rigid','element_type':'minecraft:legacy_single_pool_element'}}and pool['fallback']=='minecraft:empty'and root['start_pool']!=c['location'])
  check(ident+' root context original',root['size']==(4 if ident=='F01'else 5)and root['max_distance_from_center']==80 and root['start_height']=={'absolute':0}and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and root['terrain_adaptation']=='beard_thin'and root['use_expansion_hack']is True)
  be=[x['nbt']for x in d['blocks']if x.get('nbt')];sockets=[x for x in be if x['id']=='minecraft:jigsaw'];boxes=[x for x in be if x['id']=='minecraft:chest']
  check(ident+' actual two grunt sockets not spawned',sum(x['pool']=='kaisyn:outpost/pillagers/grunt'for x in sockets)==2)
  check(ident+' armory chest data original',len(boxes)==(2 if ident=='F01'else 1)and all(x['LootTable']=='kaisyn:outpost/common/armory'for x in boxes)and ([x['LootTableSeed']for x in boxes]==[-3494257963291929490]*2 if ident=='F01'else all('LootTableSeed'not in x for x in boxes)))
  if ident=='F01':
   tower=next(x['json']for x in c['contexts']if x['member'].endswith('/side/tower_pieces.json'))
   check('F01 tower connection original not complete assembled tower',len(sockets)==4 and next(x['nbt']for x in d['blocks']if x['pos']==[4,3,3])['pool']=='kaisyn:outpost/camps/savanna_plateau/side/tower_pieces'and len(tower['elements'])==14 and tower['fallback']=='kaisyn:village/savanna_plateau_ramshackled/tower_tops')
  else:check('F02 one bytealias and3sockets',len(sr['same_bytes_aliases'])==1 and len(sockets)==3)
  functional.append({'id':ident,'declared_volume':math.prod(d['size']),'stored_records':len(d['blocks']),'omitted_positions':0,'nonair':r['nonair'],'explicit_air':r['air'],'original_entities':d['entities'],'states':[{'pos':x['pos'],'state':pal[x['state']],'original_block_entity':x.get('nbt')}for x in d['blocks']if x.get('nbt')or pal[x['state']]['Name']in ['minecraft:smithing_table','minecraft:grindstone','minecraft:water_cauldron']],'underfoot_y_minus1_not_stored':True})
  ims=[bind(OUT/(ident+'-'+n+'.png'))for n in ['whole','cutaway','y0']]
  for im in ims:
   with Image.open(im['path'])as pic:pic.verify()
   check('current actually viewed '+im['path'],True)
  cases.append({**a,'screening_observations':reason,'images_actually_viewed':ims,'actual_full_reference_study_complete':False,'credit_proposal_maximum':0,'formal_credit_added':0,'status':'OPEN_WORKSHELTER_EXTERNAL_GROUND_AND_ASSEMBLY_BOUNDARY_ZERO','native_acceptance':False})
  context_notes.append({'id':ident,'root_context_not_direct_body':root,'actual_selected_pool':pool,'recorded_missing_single_archive':c['missing'],'world_assembly_spawn_loot_execution':False})
put('functional-evidence.json',{'candidates':functional,'original_states_preserved':True,'native_function_not_verified':True})
viewed=[x for c in cases for x in c['images_actually_viewed']];paths={x['path']for x in viewed};unviewed=[bind(p)for p in sorted(OUT.glob('*.png'))if str(p)not in paths]
put('visual-reading-boundary.json',{'viewed':viewed,'not_viewed_generated':unviewed,'unviewed_not_references_or_observations':True,'no_claim_all_layers_or_navigation_reviewed':True,'generic_class_fullcell_not_actual_textures_collision_entities':True,'initial_truncated_two_image_call_not_counted':True})
put('manual-review.json',{'scope':'Open work-shelter component/ground-boundary screening only.','cases':cases,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_current_png':21,'actual_current_images_viewed':6,'unviewed_png':15,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'no_independent_self_admission':True})
put('source-context-reading.json',{'cases':context_notes,'reading_scope':'各whole/cutaway/y0共6PNG，原功能位置/jigsaw/箱体/实体/root/选中pool/armory/biome/meta；未看15图，不逐56/43palette及所有层/动线或塔段主体研究。','metadata':'T&T Forge ${file.jarVersion}/Fabric1.12，Kubek,Biban_Auriu,Cristelknight999，CCBYNCSA4，pack18，不推当前兼容。NBT namespace kaisyn/root与tag towns_and_towers不强行改名。','assembly':'F01 root4/F02root5均max80/start0/surface/beardthin/expansiontrue；root从base_plate起，不把sideworkshop当整座root。F01四接口含塔段连接，其14候选部件及fallback非14完整建筑。F02三个接口不当三建筑。grunt池两个等重vindicator/pillager不当实际NPC。','loot':'armory一个uniform1..3池，铁斧5/附魔铁斧2(level10treasure)/铁剑5/附魔铁剑1(level20treasure)/皮甲各5/锁链各3/普通铁甲各5/另附魔铁盔1(level20treasure)/盾6/粗铁与木炭各7且uniform2..7；是原世界生成loot，不是材料付款任务回执。F01两箱同原Seed保留，F02箱原无Seed不编造。','biomes':'F01savannaplateau必需+3optional；F02sparsejungle必需+14optional条目，其中terrestria:volcanic_island重复两条保留不计两个不同biome/建筑。optional不等已安装。','counting':'samebyte F02wooded_badlands排除；完整地面/全装配未验，当前两源0完整相关研究/0pending/formal0。098/101F01已Main bounded0首次104，当前只carry0，不继续pending；095/097已接受carry0。COD4仍153/1000差847。','limits':'无Java/Gradle/游戏/QA/唤醒音亮/用户实例存档/Jar/产品/任务指南针/人物建模贴图/主清单/网络/提交发布。'})
prev=ROOT/'docs/architecture/research-20261104-smithy-104'
put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()))
carry=json.loads((prev/'carried-forward-pending.json').read_text());carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');carry['098_101_zero_first104_carry_only']=True;put('carried-forward-pending.json',carry)
check('351 history archive/member pairs not semantic refs',screen['history_unique_archive_member_pairs']==351)
check('saved prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
for f in get('protected-inputs.json')['files']:check('protected input unchanged '+f['path'],bind(f['path'])==f)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
bindings(get('latest-independent-admissions.json'));bindings(carry)
check('21generated6viewed15notviewed',len(list(OUT.glob('*.png')))==21 and len(viewed)==6 and len(unviewed)==15)
check('old098101 no currentpending',carry['prior_pending']==[]and carry['current_batch_new_pending']==0 and carry['098F01_resolved_zero_once_104']and carry['101F01_resolved_zero_once_104'])
put('verification.json',{'status':'PASS_CURRENT_COMPONENT_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'all_tasks_complete':False})
status='SEALED_OPEN_WORKSHELTER_COMPONENT_BOUNDARY_EXCLUSIONS_ZERO_COMPLETE_STUDIES'
session={'batch':105,'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_png':21,'actual_images_viewed':6,'unviewed_generated':15,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'prior_admissions_current_increment':0,'098_101_relevance_zero_first104_carry_only':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'106继续固定本地小型完整民用功能建筑；本批排除不反复，不提前制作/删任务。'}
put('session.json',session);put('active-checkpoint.json',{**session,'verification':bind(OUT/'verification.json'),'next_batch':106})
(OUT/'HANDOFF.md').write_text('105初筛两处T&T side/workshop，当前0完整相关研究/0pending/formal0。F01savanna_plateau12×21×15/DV3578全3780=300非air3480air；56palette原存，实际非air只y0..7，高21非21层。开放工棚旁4,3,3向上jigsaw接tower_pieces，未装配完整塔。F02sparse_jungle9×8×15/DV3105全1080=228非air852air，43palette；开放单工棚，与wooded_badlands bytealias渲染前排除，不加一栋。两源smith/grind/watercauldron位y0，脚下y-1不存，不视为地面承托已验完整独立工坊。无炉/床/门/梯/anvil；原entities0，grunt角色接口不等实际人。\n\n21生成PNG，仅各whole/cut/y0共6实际看，15未看逐绑定；未逐全部palette/全层或完整导航研究，最初2图截断未计实际看。原NBT/BE/entities/metadata/context保留并逐字节核对；351历史pair非语义计数。F01root4/F02root5、max80/start0/surface/beardthin/expansiontrue来自base_plate，不把side源当整座营地；selected均单legacy权1/rigid/empty。armory原loot保留不是材料→付款任务链。\n\n098F01/101F01 Main bounded用途0已104首次承接且移除pending，当前carry0；097F01 first100 accepted1/095F02 first097 accepted1亦carry0。旧其他pending不取消。COD4仍153差847，未满1000，不制作新建筑、不改主清单/外部提示词或任务中文指南针。无Java/Gradle/游戏/QA/唤醒音亮/用户存档实例/Jar/网络/提交发布。继续106固定本地完整民用小工坊。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',{'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'actual_current_images_viewed':6,'generated_png':21,'unviewed_png':15,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks':len(checks),'complete_studies':0,'actual_views':6,'pending':0,'credit':0},ensure_ascii=False))
