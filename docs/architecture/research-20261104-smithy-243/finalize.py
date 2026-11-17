import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
main=R/'docs/cod4/audit-20261022/coordinator-architecture239-actual21-ACK-final-20261112.json';mf=get(main);assert bind(main)['sha256']=='a904a123407c29c3e6261a6857980d81a75106629eff139b988713b40c7141ee'
ack=R/'docs/architecture/research-20261104-smithy-242/239-actual-author-ACK.json';a=get(ack);orig=R/'docs/architecture/research-20261104-smithy-239/manual-review.json';o=get(orig);pre=R/'docs/cod4/audit-20261022/coordinator-architecture239-actual-whole-preACK-20261112.json'
assert mf['complete_actual_author_ACK']==a and mf['complete_Main_preACK']==get(pre) and mf['complete_original_manual']==o and mf['effective_seven_dimensions']==a['corrected_effective_seven_dimensions']
assert mf['allowed_first_formal_carry_credit']==mf['accepted_whole_reference_credit']==1 and mf['subsequent_carry_credit']==0
put('239-final-acceptance-first-carry.json',{'Main_final_binding':bind(main),'complete_Main_final_original':mf,'actual_author_ACK_binding':bind(ack),'complete_actual_author_ACK_original':a,'original239_manual_binding':bind(orig),'complete_original_seven_dimensions':o['seven_dimensions'],'complete_original_eight_limits':o['limits'],'effective_corrected_seven_dimensions':mf['effective_seven_dimensions'],'unique_whole_identity':'fixedDungeonsArise_fishing_hut_main_NBT8f26c2abd3d1eec4b5f774434255b0e8df746c1a998aa0cfaad1631f80b7dd99','first_carry_batch':243,'NPC06_auxiliary_spatial_whole_credit_added_this_batch':1,'subsequent_carries':0,'NPC06_cumulative':None,'COD4_credit_added':0,'scope':'one whole auxiliary spatial reference only; single east entry effective. No swamp stilts/hydrology/alchemy/rain insect/nightlight/native/task acceptance. Original preacceptance flags and withdrawn double-entry judgments preserved immutable history, not effective analysis.','source_PNG_NBT_reopened':False,'actual_reading':'Main final new decision/relevance/correction/supersession and scope fields actually read; previously actually read completeMainpreACK/originalmanual/21actualACK/corrected7dim exact-object compared and fully retained, not new source reading.'})
src=get(P/'sources.json')['candidates'][0];raw=get(P/'raw-source-audit.json')['candidates'][0];d=raw['nbt_decoded_original'];pa=d['palette'];cells={tuple(b['pos']):b['state']for b in d['blocks']};s=d['size']
dims={
'layout':'原valley_lodge一座完整两层山谷木屋：低floor0/use1长储桶区和中央长桌，上floor5/use6西侧炊事/座席、中部会客与南三火塘、西东座席、东独立双卧铺间，北侧外露阶台和两组桌椅。北两阶各通一门后同一主厅，东室西门接主厅。低层西门独立，未证明低层内部到上厅登临；不拆储层/卧室/阶台/火塘算多例。',
'proportion':'29×19×19/DV3578，131palette/27BE/entities[]。10469声明范围内10231保存=2456nonair7775显式air，238省略；19层361RLE10469位和8PNG全读看。上层实际floor5/use6，y9以上主要交接屋盖/烟柱，y18只一末阶，不以19高度称19使用层。',
'facade':'下部鹅卵石围护与去皮spruce柱，上部oak木板/去皮oak立架、灰玻璃薄窗32，北门两组和东卧室门均关闭保存。北外台木栅/门栅环边，桌椅为birch阶/栅/压力板薄件原状态；灰类色不等石屋顶或实际透明窗/可坐功能。南烟柱与近侧小烟柱高出交叉屋盖，石木分层明确。',
'roof':'东西长厅双坡和中央北向高山墙坡盖相交；深板岩tile stair141/brick stair83和darkoak stair129配角阶/顶阶收檐，脊上木石末饰。中央高坡盖比两翼更高，但没有新经营楼面。南三营火上方y8混合石阶/半砖集罩、南墙石柱上行至y18，西烟炉柱3,6,11上亦有石烟柱；未证真实烟路/防雨/危火安全或原生照明。',
'materials':'低层12个桶：11/12/13/15/16/17,2,7朝south与12..16,2,16朝north，上层3,6,13另up桶，共12；其中4个terralith:lodge_drinkables，其余原village_taiga_house。上西smoker3,6,11east及南13/15,6,16north smoker、14,6,16north炉全未燃/Items空/timers0。13..15,6,15lit campfire/空烹饪数组，前z14floor5为原深板岩tile，y6..8air。东24/25,6,11与24/25,6,15为两张完整east床，非4床/4住户；4原villager jigsaw不是现成居民。',
'circulation':'北两组三宽south底阶x11..13与15..17：z3/y1→z4/y2→z5/y3→z6/y4→z7/y5。实际核x12/16每阶+1/+2air，接z8/9floor5木台及use6/7air，再到x12/16,z10上下6/7closed north门，门内z11灰毯。这支持静态外登台/关门边界，未证开门/毯厚/NPC寻路。低层西6,1/2,9west闭门外5,1/2,9air且地面gravel；不把侧装饰阶/南烟柱阶混作已证室内楼梯。南火塘前x13..15,z14/use6..8air但操作、火伤和护栏未运行，东卧室通门/床周围装饰薄件亦未验。',
'ground_support':'原下层石围、条柱及局部gravel边缘延至y0，地面在源下y-1未知；坡地基础/北阶脚真实落地、溪水/积雪不由源格推定。原池唯一single_pool/rigid/emptyprocessor，root size1/max80/startabsolute0/WORLD_SURFACE_WG/beard_thin，直biometag valley_clearing/shield_clearing为山谷/盾地开阔区；不是雪山保证或自然茶馆验收。独立两层住宅全源完整，不把每条坡/储桶和原villager小口拆参考。'}
limits=[
'实际公共会客/储饮/炊事/卧铺组织更接近cod3物理1133赛半仙茶馆/驿道“白天占卜/夜收摊/雨避”的辅助空间，至多1NPC12 whole待Main独立整屋相关性/近族判断，新增正式0。原valley_lodge不改称已成茶馆/算命摊/中国古建，缺茶/占卜道具和NPC功能，Main可判0。',
'开始按NPC13山居选源，但完整阅读显示公共双层会客储饮用途；本批改以NPC12单一主适用范围提出，不向NPC13/06/01/05重复加数，源原NBT未改变。8PNG不是8实例、两床/三火塘/两阶/低储层都不拆栋。',
'完整131palette全部Properties、27BE/entities[]、19层361RLE10469位置和8PNG实际读看。238省略不填air，2456nonair包含薄件/接口/火，并非2456实心承重格；低层地面与楼面高度按源状态保留。',
'固定源2pool/lootJSON和root/directbiometag2JSON、3metadata完整读。当前Jar缺原minecraft村民pool与taigahouse loot，未伪造namespace或假称已读，原运行数据包/结构集/overlay/legacy引擎/生成邻居更新未核。',
'NPC接头4个不是4居民，entities[]不是生成后永无居民；原单池single_pool不能改称legacy。DV3578不证明当前1.20.1实例实际加载兼容，modpack/metadata声明不代替原生运行。',
'4饮品桶表候选含strong_swiftness/long_night_vision/healing、水药瓶/蜜/碗/瓶和6种100秒效果炖菜，保持药水NBT/炖菜效果；不能普通potion/stew冒充，亦不是茶、现成存货、玩家付款或任务领取回执。',
'北阶两条中心各逐阶+1/+2air证据独立保存，门仍closed、屋内gray carpet非air，桌面压力板/木阶座位/门栅/床/桶/火塘实际碰撞操作和NPC工作生活路线未运行。低储层到上厅内部路线尚未证，不因外台阶存在就补成内通。',
'三lit火塘空Items/times0与前侧air不是实际烤火/做饭、防火/排烟/夜灯或多人安全验收；两对床不证明NPC睡眠，两空cauldron不证明制药。各炉空且未燃不称材料加工或完整供应链。',
'本批239按Main最终仅首次carry NPC06辅助空间1，单东入口修正有效；原239/240/241双入口旧判断只保留历史。与241七维10限完整保留比较，不重开旧PNG/NBT、不把241待审当已验，也不重复226/225/224/221/203/157等旧接受。',
'COD4153/1000缺847不变，NPC01/05/06/12/13累计未知。229/232/235/241及本243待Main；240及238HOLD0保留。适用1000门槛仍未达，不制作、不删未验任务。',
'仅本地Python -B研究及证据落盘；无Java/游戏/网络/UI/声音亮度唤醒焦点/实例原档/生产专业资产/共享Jar/主清单/Git或自动化写入，不宣全部完成、原生验收或主动工时。']
put('manual-review.json',{'batch':243,'case':'F01_VALLEY_LODGE','source':src,'seven_dimensions':dims,'limits':limits,'status':'NEW_WHOLE_MAX1_NPC12_AUXILIARY_PENDING_PLUS239_FIRSTCARRY1','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'new_whole_formal_credit_added':0,'old239_first_carry_NPC06_auxiliary':1,'formal_credit_added':1,'formal_credit_scope':'Only already finally accepted239 one whole auxiliary spatial reference, firstcarry243; new243formal0','native_acceptance':False,'actual_reading':{'palette':131,'BE':27,'entities':0,'layers':19,'RLE_rows':361,'positions':10469,'stored':10231,'nonair':2456,'air':7775,'omitted':238,'PNG_viewed':8,'full_JSON':4,'metadata':3,'old_PNG_NBT_reopened':0}})
p241=R/'docs/architecture/research-20261104-smithy-241/manual-review.json';v241=get(p241)
put('saved-complete-family-comparison.json',{'comparisons':[{'binding':bind(p241),'original_seven_dimensions':v241['seven_dimensions'],'original_limits':v241['limits'],'status':'241NPC13 pending, not current accepted cumulative'}],'corrected239_Mainfinal_binding':bind(main),'239_effective_corrected_seven_dimensions':mf['effective_seven_dimensions'],'239_original_eight_limits':o['limits'],'judgment':'243 two-level low storage/up public hall west food/east pairbed + exterior north dual stairflights differs241 compact ground single living-room/highbarrels/externalgoatpen, and239 corrected single-east-entry samefloor longservicehall. Only oneNPC12auxiliary candidate, not automatic relevance or globalnovelty proof.','old_source_images_reopened':False,'credit':0})
prev=R/'docs/architecture/research-20261104-smithy-242';ps=get(prev/'session.json');pending=[x for x in ps['active_pending']if not x.startswith('239F01')]+['243F01_VALLEY_LODGE_NPC12_AUXILIARY_SPACE']
common={'batch':243,'status':'NEW_WHOLE_MAX1_NPC12_AUXILIARY_PENDING_PLUS239_FIRSTCARRY1','formal_credit_added':1,'formal_credit_scope':'239NPC06 auxiliary whole firstcarry only','new_whole_formal_credit_added':0,'COD4_accepted':153,'COD4_gap':847,'NPC01_total':None,'NPC05_total':None,'NPC06_total':None,'NPC12_total':None,'NPC13_total':None,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'active_pending':pending,'accepted239_firstcarry243':1,'old226_carry_added':0,'other_old_carries_added':0,'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'Main verify239 firstcarry243 full original chain once1 then0; independently review243NPC12 auxiliary and earlier241/229/232/235. Continue genuinely different related whole studies, no production before applicable1000.','not_master_todo_backup':True}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous242_binding':bind(prev/n)})
protected=[]
for x in get(prev/'protected-inputs-current.json')['files']:
 old=x['current242'];cur=bind(old['path']);protected.append({'last242_checkpoint':old,'current243':cur,'unchanged':old==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False})
rebuilt={}
for layer in get(P/'F01-full-layer-rle.json')['layers']:
 for row in layer['rows']:
  x=0
  for state,n in row['runs']:
   for _ in range(n):
    if state>=0:rebuilt[(x,layer['y'],row['z'])]=state
    x+=1
  assert x==29
route=get(P/'key-source-route-cells.json');rc={tuple(x['pos']):x['state']for x in route}
checks={'exact_original_full_RLE':rebuilt==cells,'stored_unique10231':len(cells)==len(d['blocks'])==10231,'extent_nonair_air_omitted':math.prod(s)==10469 and raw['nonair']==2456 and raw['air']==7775 and 10469-len(cells)==238,'palette131_BE27_entities0':len(pa)==131 and len([b for b in d['blocks']if'nbt'in b])==27 and d['entities']==[],'eight_PNG':len(list(P.glob('*.png')))==8,'four_JSON_three_metadata':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['full_JSON'])==4 and len(get(P/'source-context.json')['metadata'])==3,'both_north_flights_two_air_overhead':all(rc[(x,y+h,z)]['Name']=='minecraft:air'for x in [12,16]for y,z in [(1,3),(2,4),(3,5),(4,6),(5,7)]for h in [1,2]),'seven_dimensions11limits':len(dims)==7 and len(limits)==11,'239_Mainfinal_full_exact':get(P/'239-final-acceptance-first-carry.json')['complete_Main_final_original']==get(main),'239_actual21ACK_full_exact':get(P/'239-final-acceptance-first-carry.json')['complete_actual_author_ACK_original']==get(ack),'239_original7_8_corrected7_exact':get(P/'239-final-acceptance-first-carry.json')['complete_original_seven_dimensions']==o['seven_dimensions']and get(P/'239-final-acceptance-first-carry.json')['complete_original_eight_limits']==o['limits']and get(P/'239-final-acceptance-first-carry.json')['effective_corrected_seven_dimensions']==a['corrected_effective_seven_dimensions'],'239_firstcarry1_only':get(P/'239-final-acceptance-first-carry.json')['NPC06_auxiliary_spatial_whole_credit_added_this_batch']==1 and common['new_whole_formal_credit_added']==0 and common['old226_carry_added']==0,'protected_eight_unchanged':len(protected)==8 and all(x['unchanged']for x in protected)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'evidence integrity, not new243 semantic or native acceptance'})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':243,'status':common['status'],'files':files,'formal_credit_added':1,'formal_credit_scope':common['formal_credit_scope'],'new_whole_formal_credit_added':0,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks));print('CARRY',bind(P/'239-final-acceptance-first-carry.json'))
