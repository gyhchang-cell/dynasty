import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent/'research-20261104-smithy-191'
assert not (P/'RECEIPT.json').exists()
def rd(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=p.resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
pre=rd(P/'preassessment-original-sources.json')['rows'];raw=rd(P/'raw-source-audit.json')['candidates'][0];r=raw['nbt_decoded_original'];screen=rd(P/'pre-render-history-screen.json');priorpath=P.parent/'research-20261104-smithy-187/manual-review.json';priorcase=rd(priorpath)['cases'][0]
put('saved-comparison.json',{'prior187_binding':bind(priorpath),'prior187_id':'F01','prior187_full_observations_preserved':priorcase['observations'],'prior187_status':priorcase['status'],'actual_reading':'本轮完整读187七项原书面观察，首次试图含全部嵌套比较的输出截断不计完整比较，随后只提取七项/状态完整读；旧原NBT/PNG/context未重开。','F02_comparison':'旧187四柱草盖切石/箱/脚手，无独立屋室，整体职业亭scope0。当前F02只有单切石、箱、低红白羊毛盖和外围碎石/草地，不因色块/小帐篷形态/职业名突破此限制，原状态有界预筛0，不称完整视觉研究。','F03_comparison':'旧187亭未达到整铺相关性。本例建筑完整性比小棚大，三向公共平台交汇、开放柱廊及东陈设架，仍无私室/生活翼/加工间。酿造台立在高柱上不等新增可用工作层；柱高/高坡屋顶/浮岛/炼金名不能替代NPC01石工工居相关性。因此完整原例研究后保守相关性未证0，不提新待审、不称与187原NBT完全相同。','formal_credit_added':0})
obs={
'layout':'F03西x0/z8、北x7/z1、南x7/z15三个原街接头在y18同一公共平台汇合；东部宽平台设高位酿造台柱与东侧箱。全部柱间开敞，无door/bed/封闭工作间/独立生活翼。不是多层工居楼；底部浮岛与四个屋面部分不拆成建筑计数。',
'proportion':'15×40×16/DV'+str(r['DataVersion'])+'，9600全存=1539非air+8061air、0省略；66palette/6BE/entities[]实际全读，40层9600原索引RLE640行全部实际阅读。y0全air，岩尖始y1，公共地板y18，最高屋脊y38；不是40层或上下连续工位。',
'facade':'quartz_pillar136在四组高柱及入口柱中竖向连续，白色矿物框架配开放栏杆、树花和木地坪。柱间无墙窗/门，东高柱上端多段acacia log连接装饰屋面，不能将柱廊空腔认成未完成墙或已封闭生产房。',
'roof':'西低坡盖和北南/东高坡盖于y24..38逐层变化，主材polished_diorite190/quartz_bricks42/purple_terracotta79/magenta_terracotta66及木构。类色视图灰色不代表全石屋顶；高屋面间空腔无上层连续地板。链灯在不同高度悬挂，不当垂直交通。',
'materials':'stone645/granite50原存承浮岛与平台，spruce_planks93为公共板、石柱/彩陶为盖架。唯一brewing_stand(10,21,8)为空瓶状态/Fuel0/BrewTime0/Items[]，下(10,20,8)及(10,19,8)去皮金合欢木、(10,18,8)stone形成高柱，不称可站立二层实验台；箱(11,18,8)east原weaponsmith loot seed8895408471760439387，不能改名炼金战利品或石工产出。',
'circulation':'三个街socket y18最终spruce_planks，仅路径连接不是缺房翼。西侧x1..8/z8 cyan carpet y19引入主平台，南北x7主带绕东侧陈设柱；(3,19,6/10)quartz stairs与(5,19,4/12)west stairs是西装饰台边，(7/8,19,4..12)jungle stairs/trapdoors为板边陈设，不存在可升y20/21并接工位的楼梯序列。上层原索引已读，无bed/ladder/新楼板，不虚构NPC上下行。',
'terrain':'y1..17连续石质浮岛从尖端展宽到y18地板，全部原存，无补造地面。三个街头需外界桥梁，pool引用已读不把桥条目当3建筑；本源自身底座/板/柱/盖完整，未研究实际桥NBT/root生成、processor结果、碰撞/交互或实机NPC。'}
imgs=[bind(P/n) for n in ['F03-whole.png','F03-cutaway.png','F03-y0.png','F03-y17.png','F03-y18.png','F03-y21.png','F03-vertical.png']]
limits=['完整建筑原源研究不等符合NPC01石工工居相关性；当前无石作/热工设备、无生活翼，高位空酿造台展示不能补足，保守0。','无游戏/原生寻路/床/交互验收；保留武器师loot而不因alchemist名改职业，村民池单候选不是实存居民。','housepool33元素/选中权50 single rigid house_processor，桥池7元素，村民池1元素，武器箱代理vanilla weaponsmith，processor3有序规则组均完整读；桥/villagerNBT、terminator/root/外部vanilla loot未读。','7图是分类颜色/整格近似，未原样材质/模型碰撞渲染；未运行processor，不声称石上随机概率可简单叠加。','没有声称1000参考完成、NPC01累计、主动10小时或任一产品任务完成。']
cases=[]
for i,a in enumerate(pre[:2]):
 s={k:a[k] for k in ['id','source_archive','member']};s['source_archive_sha256']=screen['rows'][i]['fixed_archive']['sha256'];s['nbt_sha256']=screen['rows'][i]['nbt_sha256'];s.update({'size':a['original']['size'],'DataVersion':a['original']['DataVersion'],'formal_credit_added':0})
 cases.append(s)
cases[0].update({'status':'PARTIAL_FUNCTIONAL_RELEVANCE_SCREEN_ZERO','functional_observations':'14×11×15 tanner1，33palette/7完整BE/entities[]及材料/全部功能位置实际读；3water_cauldron在11,1,z4/7/10，原level2/3/1。西北(2..4,1,3)3未点燃campfire含原leather摆件，木/皮革加工陈设非石工作坊。无bed/door/stonecutter/furnace。没有阅读11全原索引层/PNG/context，不能据功能统计称完整作坊研究或完整染作院；只将该候选作为NPC01相关性未证0边界。','actual_original_layers_read':[],'actual_visual_reading':False,'formal_credit_added':0})
cases[1].update({'status':'BOUNDED_OPEN_STONEWORK_CANOPY_SCOPE_ZERO','observations':{'layout':'7×7低羊毛职业棚，中心stonecutter(3,1,3)south、北西箱(2,1,2)south，外围低石陈设，完全无封闭生活/储物分室。','proportion':'7×5×7/DV3120，245全存=88非air157air，21pal/3BE/entities[]，5原索引层245位置全实际读；无图未作完整整栋视觉验收。','facade':'低sprucefence5承红白wool19，西北少stonebricks/墙，柱间开敞没有door/bed，零散墙不当封闭侧翼。','roof':'y3零散红白边、y4红白收拢盖，围中心作业点的低亭式盖；未生成真实材质图，不把5存储高度称多层。','materials':'切石3,1,3south，下面3,0,3dirt，南3,1,4air且下3,0,4grass；原箱vanilla village_mason/noSeed，candle2,2,1 candles4/littrue只读。无炉/床/锻造台/砧/水槽。','circulation':'南3,1,6south_up/empty最终structure_void是街入口，4,0,2up_south原minecraft taiga villagers/finaldirt_path为居民插槽，不是缺附楼；中央同一开敞坪通工位箱，无私室和上下层路线。','terrain':'y0原土草路基完整245存、无省略；5原层仅有界预筛，selectedpool机器片段未读，0完整context/metadata/PNG。不补坡地、不把两接头作两建筑。'},'full_reference_study_complete':False,'formal_credit_added':0})
cases.append({'id':'F03','source_archive':raw['source_archive'],'member':raw['member'],'observations':obs,'limitations':limits,'images_actually_viewed':imgs,'full_original_spatial_study_complete':True,'qualifying_related_reference':False,'status':'COMPLETE_PUBLIC_PAVILION_SOURCE_STUDY_RELEVANCE_UNPROVEN_ZERO','proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False})
put('manual-review.json',{'cases':cases,'complete_original_source_spatial_studies':1,'new_qualifying_related_reference_proposals':0,'formal_credit_added':0})
put('sources.json',{'candidates':[cases[0]|{'observations_omitted_here':True},cases[1],{k:raw[k]for k in ['id','source_archive','source_archive_sha256','member','nbt_sha256','size','DataVersion','purpose','formal_credit_added']}],'machine_index_not_credit':True})
put('actual-reading-boundary.json',{'F01':{'palette_full':33,'BE_full':7,'entities':0,'functional_positions_and_material_counts':True,'full_layers':False,'PNG':0,'full_context':0,'study':'partial functional relevance prefilter only'},'F02':{'original_layers':list(range(5)),'positions':245,'palette_full':21,'BE_full':3,'entities':0,'PNG':0,'full_context':0,'study':'raw bounded scope0 only'},'F03':{'original_index_RLE_layers':list(range(40)),'positions':9600,'rows':640,'palette_full':66,'BE_full':6,'entities':0,'all7PNG_actual_viewed':imgs,'full_JSON':5,'full_metadata':2,'study':'complete source spatial study, related-whole-reference admission0'},'prior187':{'complete7_observations_and_status_actual_read':True,'entire_nested_family_comparison_not_claimed':'initial diagnostic clipped; only seven-observation bounded output counted'},'formal_credit_added':0})
for n in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=rd(O/n)
 if n.startswith('carried'):d['previous_batch_receipt']=bind(O/'RECEIPT.json')
 put(n,d)
ss={'batch':192,'status':'ONE_COMPLETE_PUBLIC_NPC_PAVILION_STUDY_AND_TWO_BOUNDED_FILTERS_ALL_RELEVANCE_SCOPE_ZERO','formal_credit_added':0,'prior_admissions_current_increment':0,'186first187_later_carry_increment':0,'actual_new_original_semantic_source_studies':{'complete':1,'bounded_full_layers':1,'partial_functional':1},'complete_new_qualifying_whole_reference_studies':0,'complete_original_spatial_studies':1,'current_PNG':7,'PNG_actual_viewed':7,'COD4_accepted_baseline':153,'COD4_gap':847,'COD4_increment':0,'NPC05_increment':0,'NPC01_cumulative_not_inferred':True,'java_run':False,'game_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'190F01/157W01待审保留；继续找完整相关生产-工居空间，避开已判小亭及仅职业名差异；不能以192炼金展示亭填石工整铺参考。'}
put('session.json',ss);checks=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
g={tuple(b['pos']):b['state'] for b in r['blocks']};out={}
for l in rd(P/'F03-original-index-rle.json')['layers']:
 for z,row in enumerate(l['rows_z0_15']):
  x=0
  for run in row.split():
   v,_,c=run.partition('x');c=int(c)if c else 1
   for _ in range(c):out[(x,l['y'],z)]=int(v);x+=1
  ck('F03_RLE_width_y%s_z%s'%(l['y'],z),x==15)
ck('all9600_indices_exact',out==g and len(g)==9600);ck('F03_palette_BE_emptyentities',len(r['palette'])==66 and sum('nbt'in b for b in r['blocks'])==6 and not r['entities']);ck('air8061',sum(r['palette'][v]['Name']=='minecraft:air'for v in g.values())==8061)
for i,a in enumerate(pre):
 sh=screen['rows'][i];ck('archive_hash:'+a['id'],bind(Path(a['source_archive']))==sh['fixed_archive'])
 with zipfile.ZipFile(a['source_archive'])as z:ck('NBT_hash:'+a['id'],hashlib.sha256(z.read(a['member'])).hexdigest()==sh['nbt_sha256'])
for f in rd(P/'protected-inputs.json')['files']:ck('protected:'+f['path'],bind(Path(f['path']))==f)
ca=rd(P/'carried-forward-pending.json');ck('190_pending_kept',any(x['batch']==190 for x in ca['carried_unresolved_whole_reference_proposals']));ck('157_pending_kept',any(x['batch']==157 for x in ca['carried_unresolved_whole_reference_proposals']))
for k in ['182F01_NPC01_resolved_initial_review_HOLD0_first184','174F01_NPC01_resolved_accept1_first177','186F04_NPC01_resolved_accept1_first187']:ck('carry_exact:'+k,ca[k]==rd(O/'carried-forward-pending.json')[k])
ck('7PNGonlyF03',len(list(P.glob('*.png')))==7);ck('no_current_proposal',not ca['current_batch_new_pending'])
v={'status':'PASS'if all(c['passed']for c in checks)else'FAIL','checks':checks,'check_count':len(checks),'machine_assertions_not_credit':True};put('verification.json',v);put('active-checkpoint.json',{**ss,'verification':v['status']})
(P/'HANDOFF.md').write_text('192：F01Terralith tanner仅33pal7BE/功能材料边界读，未全层/图/context，不计整例。F02T&T snowy_taiga_mason7×5×7：5全原层/21pal3BE读，0图/context，对187完整7观察复用，小职业棚scope0。F03SkyVillagesalchemist15×40×16/DV3120：40层9600原索引RLE、66pal6BE空entities、5完整JSON2metadata，7图实际看；完整公共三向柱廊/高柱酿造展示亭，并非多层工居建筑，相关性未证0，不提新pending。190F01及157W01待审、182HOLD/174与186首次接纳全文承接，当前均不重复计。只写192，无Java/游戏/网络请求/清单/产品/共享Jar变更。\n')
assert v['status']=='PASS'
put('RECEIPT.json',{**ss,'files':[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(rd(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))
