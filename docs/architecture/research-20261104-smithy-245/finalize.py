import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
raw=get(P/'raw-source-audit.json')['candidates'][0];d=raw['nbt_decoded_original'];pa=d['palette'];cells={tuple(b['pos']):b['state']for b in d['blocks']};be=[b for b in d['blocks']if'nbt'in b]
dims={
'layout':'完整snowy_slopes_meeting_point_1雪坡客栈：floor0/use1石地会客厅，北侧酿造台/唱片机、南北西三外门，东侧屋外储桶及冷营火展示；floor4/use5木地卧铺/隔间/廊道，两对共四张完整床，外缘栅栏花槽及东北红毯露台。内东南双列阶转北接二层；不是243谷地客舍外登台/低储上大厅的同一组织。只整栋一例，不把四床/储桶/花槽/接头拆栋。',
'proportion':'21×12×15/DV3330，141palette、49BE和19空物品框实体；全3780位置保存=1326nonair2454air，无省略。12层180RLE全读，7PNG实际查看；y11全air，不能称12个使用层。floor0与floor4区分石地公共层和木地居住层。床8块合四张，不等8床/8居民。',
'facade':'去皮darkoak木架150、骨块99填墙，spruce木板225，白玻璃薄窗14，木门、栅栏、百叶活板及盆花收边。首层三闭外门与楼上开闭隔间门按原state保留；墙牌11个文本全空，不改称已有中文招牌/任务说明。花槽粗土、花草、莓丛保留原用途，类色渲染不代表实际MC贴图/薄件轮廓。',
'roof':'深darkoak板91、半砖189配角阶和顶阶构成沿x轴长脊及多个凸窗/短交叉坡盖，y10仍有屋脊、y11全air。上层部分外露台和花槽不等新增经营楼面；屋面几何只说明静态覆盖和立面节奏，不证积雪载荷、排水、防雨和烟路。',
'materials':'10桶均低层/东外侧：9个kaisyn:outpost/exclusives/outpost_mediterranean_barrel、1个food，4箱保留taiga/snowy_house原表及正负seed。13,1,3酿造台三个bottleflag为true且实际三瓶NBT为slowness/long_poison/strong_strength各Count1，Fuel0/BrewTime0；不以普通potion替代。14,1,3唱片机has_recordfalse、IsPlaying0。18,1,7与17,2,9两campfire均litfalse/空Items，源无炉/烟熏炉/炼药锅；不称已实现炊事。19物品框全无Item字段，非19NPC。8villager口与2decor口不计居民或完整建筑。',
'circulation':'北10,1/2,2、南10,1/2,12、西5,1/2,7三closed门两侧原地面及两格air有保存证据，但公共厅薄件/红毯阻挡未实测，不声称南北贯通。内阶双列z10/11：x12,y1→13,y2→14,y3为east底阶，各+1/+2air；x15,y3落脚后转15,y4,z9 north底阶接15,y4,z8木台。木台北15,5,7为顶阶、15,6,7盆花，不能直走。西向x14/13,z8,y5/6air，x12,z8为上下5/6原open east门，再x11两格air；仅支持静态分段连通，门碰撞、家具、床周围和全屋NPC寻路未验。',
'ground_support':'源floor0石地和条木、局部粗土到y0，但源外y-1地形未知。root为jigsaw/startabsolute0/WORLD_SURFACE_WG/beard_thin、size7/max80/use_expansion_hacktrue；直tag雪坡及3个optional扩展biome不是实测自然生成。town_centers池唯一legacy_single_pool/rigid/weight1，用street_meadow处理器；该表只变cyanconcrete，而本栋无cyanconcrete，不能凭名补成已验雪坡地基/路网。两decor口仅指向snowtable_1池，桌NBT未读未拼，不能加建筑数。'}
limits=[
'与cod3 NPC12赛半仙茶馆/驿道夜收摊雨避有关的公共会客、储物、楼上卧铺及内阶空间，最多提出1个辅助整屋参考，待Main独立相关性/不同完整建筑判定。本栋原雪坡客栈不是已制作的茶馆/占卜摊，未有茶/占卜/收摊任务功能。',
'F01猪灵塔和F02蘑菇亭仅机器指纹/材料/接口筛选，未整栋研究，本批新增完整研究只有F03一栋；机器差异、同栋7图、四床/花槽/接头都不加语义数，不重复计243或239。',
'141palette全部Properties、49BE、19实体完整原字段和12层180RLE3780位置已读，7PNG已查看。非air1326含薄件/接口/装饰，不等实心承重格。坐标保留结构relative与实体NBT.Pos/Tile不同域，未把19空框绝对坐标错套为屋内居民。',
'完整读7JSON/3metadata：towncenter/decor两pool、2桶loot、street_meadow processor、root、直biometag。decor JSON内部name原拼snowy_slpes_inn保留，不擅改；snowtable_1只见引用未读未摆放。当前固定Jar缺minecraft snowy villagers pool与taiga/snowy house loot，未编造已读或解析完成。',
'两列east阶每级+1/+2air及转north/西行open门段均另存实际原格，但门栅/红毯/座椅/压力板/花槽/床的碰撞和全部操作没有Java/原生验收。楼梯顶北盆花/顶阶阻挡有效，不能说全屋无障碍或门自动开关已验。',
'酿造台三瓶实存带有药水NBT，不构成制药功能验收/茶材料/玩家购买回执；Fuel/BrewTime0没有酿制进行。9特殊桶loot为莓/糖/瓶候选和另食品桶表是抽取规则，不是现存库存。原ID/seed不替换，不向NPC06重复计数。',
'两冷营火不是已烹饪/烤火/夜照明，唱片机无唱片且未播放，bell未敲；源照明/薄窗/屋顶不替代实机明暗、防雨、火灾或静音验收。无炉/烟熏炉/炼药锅不补想象厨房。',
'8个村民接头不等8个已生成居民；19空物品框不等住户。原legacy池、DV3330、namespace与metadata不证明当前数据包兼容/碰撞/邻居更新或自然生成成功；结构集与运行覆盖层未读。',
'复用244保存的243有效七维及11限制作空间比较，不重开243源NBT/PNG。239最终接受链已且仅首carry243，本245与244一样carry0；239单东入口修正持续有效，旧双入口历史不恢复。其他已接受旧栋不重加。',
'COD4已接受153/1000缺847不变，NPC01/05/06/12/13累计未知。229/232/235/241/243及245保持待Main，不把证据完整性通过当语义或游戏验收；适用1000未达，不制作不删未验任务。',
'仅本地Python -B研究/证据落盘；未运行Java/游戏/联网/UI，不改变声音亮度/唤醒焦点，不碰实例原存档、共享Jar、生产专业资产、主清单、Git或自动化，不声称全部完成或主动工时达标。']
put('manual-review.json',{'batch':245,'case':'F03_SNOWY_SLOPES_INN','source':get(P/'sources.json')['candidates'][0],'seven_dimensions':dims,'limits':limits,'status':'NEW_WHOLE_MAX1_NPC12_AUXILIARY_PENDING_FORMAL0','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'new_whole_formal_credit_added':0,'formal_credit_added':0,'old239_carry_added':0,'native_acceptance':False,'actual_reading':{'palette':141,'BE':49,'entities':19,'entities_all_empty_item_frames':True,'layers':12,'RLE_rows':180,'positions':3780,'stored':3780,'nonair':1326,'air':2454,'omitted':0,'PNG_viewed':7,'full_JSON':7,'metadata':3,'old_PNG_NBT_reopened':0}})
cmp=R/'docs/architecture/research-20261104-smithy-244/243-barrel-count-clarification.json';v=get(cmp)
put('saved-complete-family-comparison.json',{'binding':bind(cmp),'243_complete_effective_seven_dimensions':v['corrected_effective_seven_dimensions'],'243_complete_original_limits':v['complete_original_limits'],'judgment':'245 compact ground public hall/upper partitioned fourbeds with internal turning stairs and3externaldoors differs243 large low storage/up public hall/east2beds/externalnorthdualstairs. Different sourcewhole/spatialorganization supports oneNPC12auxiliary proposal, not automatic accepted semantics or globalnovelty. Both lack divination/tea/native task acceptance.','old_NBT_PNG_reopened':False,'credit':0})
prev=R/'docs/architecture/research-20261104-smithy-244';ps=get(prev/'session.json')
common={**{k:ps[k]for k in ['COD4_accepted','COD4_gap','NPC01_total','NPC05_total','NPC06_total','NPC12_total','NPC13_total']},'batch':245,'status':'NEW_WHOLE_MAX1_NPC12_AUXILIARY_PENDING_FORMAL0','formal_credit_added':0,'new_whole_formal_credit_added':0,'old239_carry_added':0,'239_first_carry_batch':243,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'active_pending':ps['active_pending']+['245F03_SNOWY_SLOPES_INN_NPC12_AUXILIARY_SPACE'],'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'not_master_todo_backup':True,'next':'Main independently review245 whole source/context/circulation/relevance; earlier229/232/235/241/243 remain pending.239 firstcarry243 once only; no re-add245. Continue distinct related complete architectural references before applicable1000 gate; no production.'}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous244_binding':bind(prev/n)})
protected=[]
for x in get(prev/'protected-inputs-current.json')['files']:
 old=x['current244'];cur=bind(old['path']);protected.append({'last244_checkpoint':old,'current245':cur,'unchanged':old==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False,'cod5_missing_not_invented':not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()})
rebuilt={};rle=get(P/'F03-full-layer-rle.json')
for layer in rle['layers']:
 for row in layer['rows']:
  x=0
  for state,n in row['runs']:
   for _ in range(n):
    if state>=0:rebuilt[(x,layer['y'],row['z'])]=state
    x+=1
  assert x==21
route=get(P/'key-source-route-cells.json');rc={tuple(x['pos']):x['state']for x in route};names=[pa[b['state']]['Name']for b in d['blocks']]
checks={'exact_full_RLE':rebuilt==cells,'stored_unique3780':len(cells)==len(d['blocks'])==3780,'extent_nonair_air_no_omitted':math.prod(d['size'])==3780 and raw['nonair']==1326 and raw['air']==2454,'palette141_BE49_empty_frames19':len(pa)==141 and len(be)==49 and len(d['entities'])==19 and all(e['nbt']['id']=='minecraft:item_frame'and'Item'not in e['nbt']for e in d['entities']),'seven_PNG':len(list(P.glob('*.png')))==7,'seven_JSON_three_metadata':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['full_JSON'])==7 and len(get(P/'source-context.json')['metadata'])==3,'barrels10_chests4_four_full_beds':names.count('minecraft:barrel')==10 and names.count('minecraft:chest')==4 and sum(n.endswith('_bed')for n in names)==8 and sum(pa[b['state']].get('Properties',{}).get('part')=='head'for b in d['blocks'])==4,'eight_villager_two_decor_sockets':sum(b['nbt'].get('pool')=='minecraft:village/snowy/villagers'for b in be)==8 and sum(b['nbt'].get('pool')=='kaisyn:village/snowy_slopes_inn/decor'for b in be)==2,'lower_dual_stair_two_overhead_air':all(rc[(x,y+h,z)]['Name']=='minecraft:air'for z in [10,11]for x,y in [(12,1),(13,2),(14,3)]for h in [1,2]),'west_landing_open_door':all(rc[(x,y,8)]['Name']=='minecraft:air'for x in [15,14,13,11]for y in [5,6])and all(rc[(12,y,8)]['Properties']['open']=='true'for y in [5,6]),'seven_dimensions11limits':len(dims)==7 and len(limits)==11,'no_repeat239_no_new_formal':common['old239_carry_added']==common['formal_credit_added']==0,'protected_eight_unchanged':len(protected)==8 and all(x['unchanged']for x in protected)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'file/evidence integrity only; not semantic independent or native acceptance'})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':245,'status':common['status'],'files':files,'formal_credit_added':0,'new_whole_formal_credit_added':0,'old239_carry_added':0,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
