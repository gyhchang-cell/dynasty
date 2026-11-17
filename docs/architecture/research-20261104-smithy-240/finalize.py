import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def binding(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def get(p):return json.loads(Path(p).read_text())
src=get(P/'sources.json')['candidates'][0];raw=get(P/'raw-source-audit.json')['candidates'][0];d=raw['nbt_decoded_original'];s=d['size'];pal=d['palette'];cells={tuple(b['pos']):b['state']for b in d['blocks']}
dims={
'layout':'完整地面单室小屋，北z2单门、内主厅x4..8/z3..11，西侧z5..8凸出砖壁炉与通高烟道，西南墙内薄板台和一盆枯灌木；中央高屋盖收拢，没有独立楼板/上层登临。原上屋一座，未组合地下室，不拆壁炉/台子/烟道计数。',
'proportion':'12×13×15 / DV3465；65palette/2BE/entities[]。2340声明位置内1067保存=794非air+273显式air，1273位置省略。13层195RLE行2340位实际读；6类色PNG全看。794非air包含火、薄件及数据标记，不称794实心承重块。',
'facade':'石墙低基/鹅卵石主体、北单扇spruce door上下1/2，z2/12端窗和西枯灌木台。vine91/leaves20为原存植被；不以类色绿色假定药草、灰色假定完整墙碰撞。北门朝south/closed，位置在北墙，朝向不等门所在南侧。',
'roof':'spruce planks122/stairs136/slab33形成逐层内收的东西双坡，ridge沿z方向。屋檐自x2/10到x6上脊，y7中央x6长段为cobblestone_wall悬置梁件，不是楼板；西砖烟道至y12砖阶围口，通高中心2,y2..12,6/7保存air。6PNG仅方格形状近似，不证明排烟或防雨。',
'materials':'西壁炉magma2,0,6/7与fire2,1,6/7，前3,1,6/7iron_bars，4,0,6/7brick近侧台；4,1,9/10top birch slab，4,2,9potted_dead_bush。没有cauldron/brewingstand/crafting/furnace/bed或实际存储箱；4,0,9原lootES及6,1,10原spawner均DATA结构方块，非实际胸箱或刷怪笼。',
'circulation':'北门7,1/2,2配对，内侧7,0,3/4oak且上1/2/3air，可描述门内连续短段。外7,y0..3,1全部省略，不能称原air或自然入口已连通。单室主道不经西砖火槽，台前等净空仅静态格查；关闭门、薄阶、铁栏、火/伤害/NPC路径未运行。',
'ground_support':'主要floor0/use1的石边框与木地面；原档不含y<0柱脚，没有楼下架空层、水位、栈桥与连续吊脚柱证据。固定Jar placed_feature用OCEAN_FLOOR高度/rarity105/biome/no_structure；不是海底或沼泽吊脚的自然验收。地下室只在较新比较源码中可选，未装配或读其NBT，不算第二参考。'}
limits=[
'本批一座完整原始上屋已读，适用NPC06药屋的用途/吊脚证据不足，HOLD0；不以森林巫师名称代替制药功能，不将火塘当锻炉，也不迁到NPC01或NPC05凑数。',
'F01法师住宅、F02双层德鲁伊、F04侧向德鲁伊仅本批机器指纹筛查，未实际整栋阅读/看图；0建筑信用，保留继续研究，未声称源穷尽。',
'完整65palette Properties、2DATA BE、entities[]，13层195RLE2340位及6PNG实际阅读；1273省略原样，与273显式air分开，未把省略填空气用于可达性。',
'固定Jar3完整JSON与2metadata实际读；没有模板池不等源永不生成，此处是feature。调色choices8/4/3/1与8条0.5苔石规则是配置，未运行palette解析、自然地形或全biome链。',
'本地DruidHutFeature.java全文只作不同版本旁证；Identifier/Optional API与原1.20.1不同，未证明二进制一致。源码描述spawner→德鲁伊刷怪、lootES→east/single箱及可选地下室；不能把旁证称本Jar实际生成回执。',
'与205、206、239各完整七维和全部限制对照全文保留；205高脚上下层、206低储物高锅台、239双入口同层渔厅与本源floor0单室砖烟道确不同，但差异本身不填补制药/吊脚相关性。旧PNG/NBT未重开，也不把旧信用再计。',
'226首次239已由Main独立闭合，本240仅绑定该闭合，新增carry0；229/232/235/239继续待Main，238HOLD0不追认。COD4仍153/1000缺847，各NPC累计null，适用1000未达禁止制作。',
'本批仅本地Python -B研究；无Java/游戏/网络/UI/声亮/唤醒/焦点/实例原档/生产/专业模型贴图/共享Jar/主清单/Git写入，无任务删除、工时或全部完成声明。']
put('manual-review.json',{'batch':240,'case':'F03','source':src,'seven_dimensions':dims,'limits':limits,'status':'COMPLETE_ORIGINAL_UPPER_HUT_HOLD_RELEVANCE_ZERO','complete_original_spatial_study':True,'new_reference_proposal':0,'formal_credit_added':0,'actual_reading':{'palette':65,'BE':2,'entities':0,'layers':13,'RLE_rows':195,'positions':2340,'stored_positions':1067,'nonair':794,'explicit_air':273,'omitted':1273,'PNG_actual_viewed':6,'full_archive_JSON':3,'full_metadata':2,'local_newer_source_full':1}})
comp=[]
for n in [205,206,239]:
 p=R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json';v=get(p);comp.append({'binding':binding(p),'original_seven_dimensions':v['seven_dimensions'],'original_limits':v['limits']})
put('saved-complete-family-comparison.json',{'comparisons':comp,'old_NBT_PNG_reopened':0,'credit':0})
closure=R/'docs/cod4/audit-20261022/coordinator-architecture226-firstcarry239-actual-closure-20261112.json';cl=get(closure)
assert cl['source_full_objects_exact']and cl['delivery_all27_file_bindings_exact']and cl['NPC01_226_whole_firstcarry']==1
put('accepted226-closure-reuse-zero.json',{'binding':binding(closure),'original_closure':cl,'first_carry_batch':239,'credit_added_this240':0,'old_source_or_PNG_reread':False})
prev=R/'docs/architecture/research-20261104-smithy-239';session=get(prev/'session.json')
common={'batch':240,'status':'DRUID_UPPER_HUT_COMPLETE_HOLD_RELEVANCE_ZERO','formal_credit_added':0,'new_whole_formal_credit_added':0,'COD4_accepted':153,'COD4_gap':847,'NPC01_total':None,'NPC05_total':None,'NPC06_total':None,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'active_pending':session['active_pending'],'226_first239_Main_confirmed':True,'old226_carry_added':0,'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'Continue bounded related complete references: F01/F02/F04 only screened, not yet read or credited. Preserve all pending and HOLD. No production before applicable1000.','not_master_todo_backup':True}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous239_binding':binding(prev/n)})
prot=[]
for a in get(prev/'protected-inputs-current.json')['files']:
 old=a['current239'];cur=binding(old['path']);prot.append({'last239_checkpoint':old,'current240':cur,'unchanged':old==cur})
put('protected-inputs-current.json',{'files':prot,'this_chat_product_writes':False})
rle=get(P/'F03-full-layer-rle.json');rebuild={}
for layer in rle['layers']:
 for row in layer['rows']:
  x=0
  for state,n in row['runs']:
   for _ in range(n):
    if state>=0:rebuild[(x,layer['y'],row['z'])]=state
    x+=1
  assert x==s[0]
checks={'rle_exact_reconstruction':rebuild==cells,'all_original_positions_unique':len(cells)==len(d['blocks'])==1067,'declared_count':math.prod(s)==2340,'nonair_air_omitted':raw['nonair']==794 and raw['air']==273 and math.prod(s)-len(cells)==1273,'all65palette_read':len(pal)==65,'two_data_markers':len([b for b in d['blocks']if 'nbt'in b])==2,'six_views':len(list(P.glob('*.png')))==6,'three_fixed_JSON':len(get(P/'bounded-generation-context.json')['original_archive_JSON_full_read'])==3,'seven_dimensions_eight_limits':len(dims)==7 and len(limits)==8,'three_prior_full_comparisons_exact':all(c['original_seven_dimensions']==get(c['binding']['path'])['seven_dimensions'] and c['original_limits']==get(c['binding']['path'])['limits']for c in comp),'226_reuse_zero':get(P/'accepted226-closure-reuse-zero.json')['credit_added_this240']==0,'protected_all_eight_unchanged':len(prot)==8 and all(a['unchanged']for a in prot)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'evidence integrity only; no native acceptance or new semantic credit'})
files=[binding(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',{'batch':240,'status':common['status'],'files':files,'verification':binding(P/'verification.json'),'formal_credit_added':0,'all_tasks_complete':False})
print('SEALED',binding(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
