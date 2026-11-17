import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-202'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
raws=read(P/'raw-source-audit.json')['candidates'];rles=read(P/'original-index-rle.json')['cases']
for raw,rle in zip(raws,rles):
 d=raw['nbt_decoded_original'];g={tuple(b['pos']):b['state'] for b in d['blocks']};sx,sy,sz=d['size'];ident=raw['id']
 check(ident+' shape',len(rle['layers'])==sy)
 for l in rle['layers']:
  check(ident+' rows y'+str(l['y']),len(l['rows'])==sz)
  for z,row in enumerate(l['rows']):
   vals=[]
   for s in row.split():
    t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
   check(ident+' original row y%d z%d'%(l['y'],z),vals==[g.get((x,l['y'],z),-1) for x in range(sx)])
 check(ident+' fixed archive hash',bind(raw['source_archive'])['sha256']==raw['source_archive_sha256'])
 with zipfile.ZipFile(raw['source_archive']) as z:check(ident+' source member hash',hashlib.sha256(z.read(raw['member'])).hexdigest()==raw['nbt_sha256'])
 check(ident+' entities empty',d['entities']==[])
 if ident=='F01':check('F01 exact counts',len(d['palette'])==21 and sum('nbt'in b for b in d['blocks'])==4 and len(g)==179 and raw['air']==43 and raw['nonair']==136)
 else:
  check('F02 exact counts',len(d['palette'])==43 and sum('nbt'in b for b in d['blocks'])==15 and len(g)==576 and raw['air']==113 and raw['nonair']==463)
  check('continuous supported ladder original',all(g[(2,y,2)]==9 and d['palette'][g[(1,y,2)]]['Name'] in ['minecraft:stone','minecraft:stone_bricks'] for y in range(2,14)))
  check('bed two actual floors',g[(2,6,4)]==17 and g[(3,6,4)]==17)
  check('roof high furnace actual support',g[(5,14,1)]==42 and g[(5,13,1)]==3)
  check('roof hatch closed needs operation',g[(2,14,2)]==30 and g[(2,15,2)]==10)
old196=read(P.parent/'research-20261104-smithy-196/manual-review.json')['cases'][0]
old197=next(c for c in read(P.parent/'research-20261104-smithy-197/manual-review.json')['cases'] if c['id']=='F04')
comparison197=read(P.parent/'research-20261104-smithy-197/saved-complete-family-comparison.json')
put('saved-complete-family-comparison.json',dict(binding196=bind(P.parent/'research-20261104-smithy-196/manual-review.json'),full196case=old196,binding197=bind(P.parent/'research-20261104-smithy-197/manual-review.json'),full197case=old197,binding126_138_saved=bind(P.parent/'research-20261104-smithy-197/saved-complete-family-comparison.json'),full126_138_saved_comparison=comparison197,current_comparison='F01仍共同室，保守family0。F02不是197绕柱阶逐四级退出环平台，也不是126阶侧出上长廊或138后脚手架上空井塔脚；直梯贯穿实底楼板连接下储物炉室/中独立床层/屋顶炉作，至多1待审。职业、床炉数量或塔高均不作新增信用。',old_NBT_or_PNG_reopened=False,formal_credit_added=0))
sources=[{k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']} for r in raws]
common=['仅完整原始静态研究，不是生成/实机/碰撞/NPC路径/任务材料付款领物或中文指南针验收。原稿/专业资产均未修改。','完整pool/processor/loot/root与直接biome标签只说明所读子范围，不代表全部运行依赖。嵌套tag、structure_set、生物NBT及其它变体未读。','原索引-1省略不是air，类色整格图不表达实际半块/门/栏缝碰撞或贴图。DV原样，不称已版本转换。','197first199与190first193仅旧一次接受，本批后续0；182HOLD0/064不追认/174186旧接受不变；157旧待审保留。COD4153/847,NPC05+0,NPC01累计未知。','无Java/游戏/网络/声音亮度唤醒/用户实例/资产/共享Jar/Git/主清单改动，不删任务、不称全完成/工时。']
c1=dict(id='F01',source=sources[0],seven_dimensions={
'layout':'北3,1/2,0单扇门入紧凑同层共同室；西北营火与墙饰、西南高炉、东中工作台、东南一对床，中央共享空间。无分室、独立工翼、上层或楼梯；不能把炉/床/工作台拆栋。对完整196底层共室炉床布局及其全部限制比较，改小石壳/位置仍共同室，保守family0。',
'proportion':'7×5×8/DV3465，280声明=179保存(136非air+43air)+101省略；21palette/4BE/entities[]。5层40原行280格全读；floor0/use1，5高石盖无经营二层。',
'facade':'苔石/圆石/安山岩厚壁拱壳，north spruce door/right/closed完整一扇，西东灰玻璃窗，wall薄件构营火围边和顶饰。北入口不是接头，原源无jigsaw，不因目录top就说它是缺下半的组件。',
'roof':'y3侧壁收拢、y4中央3×3实体石盖，西北墙饰从营火上方air到两层wall；无梯、上部地板或可达阁楼。未证明墙缝烟道、热安全/防雨，类色图绿色是苔石，不等草屋顶。',
'materials':'营火1,1,2north littrue/Items[]，高炉1,1,5east litfalse/Items[]/timer0，craft5,1,3，灰床5,1,4foot与5,1,5headsouth一对。无砧、水、熔岩，不据littrue等生产任务已运行。',
'circulation':'北门内3,1/2,1air通中央；高炉东前2,1,5air，工作台西侧4,1,3air，床西侧4,1,4/5air。营火外围墙薄件不叫全air；原始静态通路不等碰撞/NPC/危险距离验证。',
'ground_support':'y0苔石/圆石/安山岩环和中央podzol；炉下1,0,5安山岩，床两半下5,0,4安山岩与5,0,5圆石均实际实体。y-1真实地形未知。root generic_jigsaw size2/start0/WORLD_SURFACE_WG/beardthin/cannot_liquidtrue只配置，非落地证明。'},limits=common+[
'6PNG实际逐张看，全部21palette/4BE/entities[]、5层40行/280位置、pool+root+biometag共3JSON及2metadata全文实际读。',
'选池top/top_trapdoor各权1/single rigid/empty processor；仅top当前整栋研究，trapdoor变体未读，不算第二屋或替代其地窖。原source无jigsaw，与有地下接口版本分开。',
'直接biome tag仅引用giant_taigas/rocky_mountains两集合，集合内部未读；root spawn_overrides{}不保证运行世界无生物。',
'与完整196炉床共室全七维/12限制比较，未出现空间工序新组织。196只是作者0已收到，引用它不是Main新接受；F01本批family0/新提议0。'],complete_original_spatial_study=True,status='AUTHOR_SHARED_WORK_LIVING_ROOM_FAMILY_ZERO',formal_credit_added=0,new_reference_proposal_maximum=0)
c2=dict(id='F02',source=sources[1],seven_dimensions={
'layout':'东墙5,2/3,3门（门状态朝west）入底层储物/炉室，西北2,y2..13,2直梯；floor6/use7独立床/工作台/三桶层；floor13/use14开敞屋顶高炉/工作台/两桶。三层由同一垂直梯带贯穿，不拆三屋。相对197中柱绕阶/多层环形工位、126侧出长工作廊和138空井塔脚/屋顶组合，为紧凑直梯工作-生活-屋顶工区整体，至多1相关NPC01空间参考待Main判。',
'proportion':'8×16×7/DV3337；896声明=576保存(463非air+113air)+320省略。43palette/15BE/entities[]，16层112原行896位置全读。实际floor1/use2、floor6 top木slab/use7、floor13 top木slab/use14；窗檐/顶冠不是16层。',
'facade':'圆石/石砖/裂石砖厚石塔、stone内壁，入口东侧x7,1,3west底阶与x6,1,3实石平台，x6,2,3省略不当air。外角扶壁及半阶檐/木栏饰，唯一spruce闭门west/left；内闭合塔身不叫外绕公共通道。',
'roof':'y13挑边倒石阶及顶木半砖楼板，y14环墙，y15间隔bottom stonebrick slab形成开齿雉堞；屋顶高炉平台无遮雨盖，不编为密闭阁楼。楼板梯洞存在，防坠/天候/通烟均未验。',
'materials':'底2/3,2,4双箱north两半各原loot seed、3/4,2,2空桶与4,2,4north未燃普通炉；中层床2/3,7,4west一对，craft4,7,2、三loot桶；屋顶高炉5,14,1south/未燃空timer0、craft1,14,5及两loot桶。储物块不等独立仓楼，完整loot仍不表示已发材料。',
'circulation':'东门入5,2/3,3后4/3/2,y2/3,z3中央空格；直梯2,y2..13,2 east，背1,y2..13,2逐层stone/stonebrick实体。y6侧出床层、床南/东邻通路和2,7,3open trapdoor保留原状态。顶2,14,2 east/bottom/closed trapdoor，顶上2,15,2air，需打开才能从梯上到屋顶；不叫当前全部air出口，不声称NPC会开/爬或碰撞实测。',
'ground_support':'源y0全56格dirt/grass基础；实际底炉4,2,4下4,1,4stonebrick，床下2/3,6,4TOP spruce slab，屋顶高炉下5,13,1stonebrick均实体。底层mob socket4,1,3 finalstonebrick，另一3,5,3 finalair，都是skeleton接口不是建筑翼；y-1和门外省略地形未验。'},limits=common+[
'8PNG逐张实际看；全43palette/15BE/entities[]和16层112RLE/896位；4pool/loot/processor JSON+精确root1+直接biometag1共6JSON，3metadata全文读。',
'root全boundingbox monster skeleton权1/minmax1，两个mob socket指skeleton pool；entities[]不是无敌人。skeleton NBT未读，原敌对塔只可提建筑空间参考，未变成民用老陈铺。',
'pool tour_1/tour_2各权1、single rigid/mossify20；只读_1；完整mossify仅cobble/stonebrick各0.2苔化，不据变体/苔化各计一屋。root exact startpool tour仅1，substring误匹配旧tour_desert root/tag读到后排除当前闭环与信用。',
'loot主pool5rolls苹果/骨1..6/线2..7/铁1..2/金，副pool1roll空5/石剑3；原全部seed和双箱类型保留，无运行或兑换材料回执。',
'完整197七维/12限制、126七组全嵌入限制和138七组全嵌入限制实际读以比较；保留197原历史pending措辞但实际199已接受仅历史一次1，本批不重开旧PNG/NBT或再授。',
'候选整体差异是直梯穿实层板的储物炉室→独立床层→屋顶炉作，非仅职业替换/塔高/床或炉新增；仍可因近族/相关性/敌对用途/活板门与窄路适用性由Main判0，不保证全历史唯一。',
'无floor间循环楼梯、没有连续材料运输验证；顶hatch闭合必须操作，床位可达和整条梯净高/玩家开门/防坠/防火/生成均未验。',
'只提交新待审上限1，正式0；本批活跃whole待审在旧157W01外新增203F02，197不重新列pending。'],complete_original_spatial_study=True,status='WHOLE_SPATIAL_REFERENCE_PROPOSAL_PENDING_MAIN_FAMILY_RELEVANCE_REVIEW',formal_credit_added=0,new_reference_proposal_maximum=1)
put('manual-review.json',dict(batch=203,cases=[c1,c2],actual_current_images_viewed=14,formal_credit_added=0,new_whole_proposal_maximum=1))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 v=read(PRE/name)
 if name.startswith('latest'):
  v['previous_binding']=bind(PRE/name);v['current_batch_formal_credit_added']=0;v['all_prior_acceptances_carry_only_no_current_increment_203']=dict(increment=0,old_raw_or_PNG_reopened=False)
 else:
  v['previous_batch_receipt']=bind(PRE/'RECEIPT.json');v['current_batch_new_pending']=1;v['current_batch_pending_cases']=['203F02'];v['carried_unresolved_whole_reference_proposals'].append(dict(batch=203,id='F02',maximum=1,independent_admission=False,target='COD3 NPC01 独眼铁匠·老陈 山脚铁匠铺（主世界）空间组织参考',source_fragments_not_separate_references=True));v['197first199_later_carry_increment_203']=0;v['190first193_later_carry_increment_203']=0
 put(name,v)
orig=read('docs/cod4/audit-20261022/coordinator-smithy197-F04-ring-work-tower-whole-review-20261110.json')
check('197 objects unchanged',read(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_197_F04']['full_Main_judgment_preserved_exact']==orig and read(P/'carried-forward-pending.json')['197F04_NPC01_resolved_accept1_first199']['full_Main_judgment_preserved_exact']==orig)
check('pending old157 plus new203 only',[(r['batch'],r['id']) for r in read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(203,'F02')])
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current202'];now=bind(old['path']);protected.append(dict(last202_checkpoint=old,current203=now,unchanged=old==now))
check('8 inputs unchanged',len(protected)==8 and all(f['unchanged'] for f in protected));put('protected-inputs-current.json',dict(files=protected,baseline='202 checkpoint not new start203 snapshot',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
check('14 actual image files',len(list(P.glob('*.png')))==14)
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_semantic_credit=True))
s=dict(batch=203,status='TWO_WHOLE_STUDIES_F01_FAMILY_ZERO_F02_NEW_PENDING',formal_credit_added=0,new_qualifying_reference_proposals_maximum=1,actual_new_original_spatial_studies=2,current_PNG=14,PNG_actual_viewed=14,full_current_context_JSON=9,full_metadata=5,old_PNG_NBT_reopened=False,accepted197_first199_later_increment=0,accepted190_first193_later_increment=0,COD4_accepted_baseline=153,COD4_gap=847,COD4_increment=0,NPC05_increment=0,NPC01_cumulative_not_inferred=None,java_run=False,game_run=False,network_used=False,product_files_written=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue another whole related local reference; no stop pending Main. Frozen203 formal credit zero until independent judgment.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
