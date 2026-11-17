import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
src=get(P/'sources.json')['candidates'][0];raw=get(P/'raw-source-audit.json')['candidates'][0];d=raw['nbt_decoded_original'];pa=d['palette'];cells={tuple(b['pos']):b['state']for b in d['blocks']}
dims={
'layout':'原冰术师一座完整木屋带东围栏小院：西门进入地面单室，中部brown wool/地毯，北烟炉与箱、南craft与东南单床，上南沿三桶。东x6整墙与外院分离，围栏院以东北角闭栅门对外。没有内门连院，也没有独立经营二层；屋顶营火不当室内篝火。',
'proportion':'10×8×9/DV3465，56palette/12BE/1原盔甲架。720声明位置内698保存=302nonair396显式air，22省略；8层72RLE720格与6PNG实际读看。室内主要floor0/use1，y3..5主体坡盖、y6烟柱、y7营火；三桶y4不构成阁楼。',
'facade':'spruce log立柱、planks木墙、上下活板/木阶檐与西低门廊。原保存white concrete四处是processor待替状态，并非白玻璃窗；25% cobweb再air的rule原样保留，最终帘幕/采光不据类色图断言。灰色原infested_cobblestone尤其不改称普通石材。',
'roof':'长主屋盖沿z方向，东西阶坡从x1..9檐逐步收至x4脊，西门廊小坡正交接入。北4,y0..6,1炉/石墙/infestedcobble烟柱上4,7,1 lit campfire/非signal，四向open bottom活板围顶。雪载、防雨、烟柱火扩散与营火照明未运行，屋顶火不是可达烤火工作位。',
'materials':'北smoker4,1,1south/unlit/Items[]/计时0；3,1,2south箱原iceologer_cabin loot无seed，3,1,6craft；蓝床5,1,5foot及5,1,6headsouth一对。3/4/5,4,6north三桶同原barrel loot，低前3/4/5,3,6closed top trapdoor。外院hay7,1,4/5与7,2,5；不冒称猎获物/陷阱或实际材料付款来源。空ArmorItems盔甲架相对2.5,1,5.5与NBT.Pos绝对-71.5,-60,183.5分域保存，不是巴图居民/已摆装备。',
'circulation':'西入口z4：0,0,4path上1/2air，1,0,4infestedcobble上1/2open west/right spruce门，2,0,4planks上1/2air但y3top slab；3,1,4brown carpet/2air；4,0,4up_west socket finalbrown_wool，上1/2air；5,1,4carpet。仅证源格连续组织，地毯厚度及开放门碰撞不称路径验收。craft东前4,1,6carpet/2air；床旁4,1,5air但4,1,6carpet；高桶无梯，桶面/头高/取物未证。东院9,1,0south闭栅门外连通与山羊/NPC使用未测。',
'ground_support':'楼面0贴地，西入口另0,3,4west_up/rollable empty最终air对接base plate6,3,11east_up入口，静态朝向互向；未装配旋转求解。base17×8×24仅size/2BE有界阅读，非整基座研究或新增一栋；另营火口5,1,18south_up指独立feature，未读featureNBT。root自有iceologer_cabin_structure/startbase/size5/max32/absolute0/WORLD_SURFACE_WG/beard_thin，直tag到snowy集合可证雪域题材相关，非真实自然地形基础/雪水路线验收。'}
limits=[
'COD3-8.3 NPC13原雪山木屋/夜烤火雨避的辅助居住储物空间，最多1完整建筑候选待Main判相关性与近族，正式新增0。原冰术师敌对用途与山羊院保留，不能当成巴图已入住/猎人功能或室内烤火已完成；Main可判0。',
'56palette全Properties、12BE、1盔甲架全文、8层72RLE720位置和6PNG实际读看；22省略不当air，302nonair包含薄件/设备接口，不称302实心承重方块。',
'6原pool/loot/processorJSON+6root/basepool/营火pool/直biometag/snowy集合/baseprocessorJSON与2metadata全文实际读；雪域子标签/原结构集/自有结构类型和custom盔甲架processor实现未读，root不代替原生自然生成。',
'原base只界定17×8×24/DV3465和2接头，非其全格/地形或独立参考；冰术师/山羊3个实体组件、外营火组件仅读取pool JSON，未读其NBT或实际拼装。不以接口、同屋截图、屋院分区凑栋数。',
'白混凝土processor25%蛛网后air；infested石与roof campfirelit原样保留，不替换/触发虫/开火/声音。床两块不是两住户，空盔甲架不是居民，原实体相对/绝对坐标不混用。',
'原loot箱固定bundle+4..6roll冰/木/面包/麦，桶两组2..3roll绿宝石/蛛网/线及盆/木炭，仅候选表，不当玩家库存/猎获来源/交易付款/任务或指南针回执。高桶无梯和薄活板、地毯、门/栏/床周边的碰撞操作/寻路均未运行。',
'本批F04/F05樱花tool/weaponsmith与既有山地角色/occupancy完全同族只机器筛除0；F06trial smith房间、F03法师住宅仅材料初筛0，F02lodge只有机器指纹0，F07探险屋已见历史0，不称这些整栋实际研究或来源穷尽。',
'完整保留239/240七维与8限制对照，239同层渔厅/海滩而240地面无床砖烟道，本屋单室炊事单床/高桶/外院组织不同；差异不升级其它pending/HOLD、不迁用NPC01/05/06信用。',
'226first239 Main闭合后240复用0，本241仍0；229/232/235/239pending保持。COD4153/1000缺847，NPC01/05/06/13累计null，适用1000未到，不制作。',
'只本地Python -B研究，无Java/游戏/联网/UI/声音亮度唤醒焦点/用户实例原档/专业模型贴图/生产/共享Jar/主清单/Git写入；不删任务、不宣全部完成或主动工时。']
put('manual-review.json',{'batch':241,'case':'F01_ICEOLOGER_CABIN','source':src,'seven_dimensions':dims,'limits':limits,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_SPATIAL_PENDING_MAIN','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'formal_credit_added':0,'native_acceptance':False,'actual_reading':{'palette':56,'BE':12,'entities':1,'layers':8,'RLE_rows':72,'positions':720,'stored':698,'nonair':302,'air':396,'omitted':22,'PNG_viewed':6,'full_JSON':12,'metadata':2,'bounded_base_BE':2,'old_PNG_NBT_reopened':0}})
comparisons=[]
for n in [239,240]:
 p=R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json';v=get(p);comparisons.append({'binding':bind(p),'original_seven_dimensions':v['seven_dimensions'],'original_limits':v['limits']})
put('saved-complete-family-comparison.json',{'comparisons':comparisons,'credit':0,'old_images_NBT_reopened':0})
cl=R/'docs/cod4/audit-20261022/coordinator-architecture226-firstcarry239-actual-closure-20261112.json';put('accepted226-closure-reuse-zero.json',{'binding':bind(cl),'original_closure':get(cl),'first_carry_batch':239,'credit_added_this241':0})
p=R/'docs/architecture/research-20261104-smithy-240';old=get(p/'session.json');pending=old['active_pending']+['241F01_ICEOLOGER_CABIN_NPC13_AUXILIARY_SPACE']
common={'batch':241,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_SPATIAL_PENDING_MAIN','formal_credit_added':0,'new_whole_formal_credit_added':0,'COD4_accepted':153,'COD4_gap':847,'NPC01_total':None,'NPC05_total':None,'NPC06_total':None,'NPC13_total':None,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'active_pending':pending,'226_first239_Main_confirmed':True,'old226_carry_added':0,'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'Main actual independent whole/7dim review may accept or reject NPC13 auxiliary-related candidate. Continue genuinely related different complete buildings; no repeats or production before1000.','not_master_todo_backup':True}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous240_binding':bind(p/n)})
protected=[]
for a in get(p/'protected-inputs-current.json')['files']:
 prev=a['current240'];cur=bind(prev['path']);protected.append({'last240_checkpoint':prev,'current241':cur,'unchanged':prev==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False})
rle=get(P/'F01-full-layer-rle.json');rebuild={}
for layer in rle['layers']:
 for row in layer['rows']:
  x=0
  for state,n in row['runs']:
   for _ in range(n):
    if state>=0:rebuild[(x,layer['y'],row['z'])]=state
    x+=1
  assert x==10
checks={'exact_full_RLE_reconstruction':rebuild==cells,'original_positions_unique':len(cells)==len(d['blocks'])==698,'counts720_698_302_396_22':math.prod(d['size'])==720 and raw['nonair']==302 and raw['air']==396 and 720-698==22,'palette56_BE12_entity1':len(pa)==56 and len([b for b in d['blocks']if'nbt'in b])==12 and len(d['entities'])==1,'six_views':len(list(P.glob('*.png')))==6,'full_JSON12':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['full_JSON'])==12,'seven_dimensions_ten_limits':len(dims)==7 and len(limits)==10,'original_prior_comparisons_exact':all(c['original_seven_dimensions']==get(c['binding']['path'])['seven_dimensions']and c['original_limits']==get(c['binding']['path'])['limits']for c in comparisons),'226_reuse_credit_zero':get(P/'accepted226-closure-reuse-zero.json')['credit_added_this241']==0,'protected_eight_unchanged':len(protected)==8 and all(a['unchanged']for a in protected)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'evidence integrity not native or semantic acceptance'})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':241,'status':common['status'],'files':files,'formal_credit_added':0,'new_qualifying_proposal_maximum':1,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
