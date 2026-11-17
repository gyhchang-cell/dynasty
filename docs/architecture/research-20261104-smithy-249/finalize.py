import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=R/'docs/architecture/research-20261104-smithy-248'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
a=get(P/'raw-source-audit.json')['candidates'][0];d=a['nbt_decoded_original'];pa=d['palette'];bs=d['blocks'];cells={tuple(b['pos']):b['state']for b in bs};be=[b for b in bs if'nbt'in b]
dims={
'layout':'原old_growth_taiga_medium_house_2一座紧凑完整林间木屋：floor0/use1单居室，南闭门直面短入口，西north红床一张，东北west箱一只，东侧north砂岩底阶座位及oak顶阶盆栽台，中央床侧空墙牌。上4,5,4朝下桶夹在屋盖木构中，无上层生活楼面/内梯；不把隐桶/床/入口拆成建筑。与246侧鼓长厅双床中央烛桌草顶的生活组织不同，但仍有小型单室住宅近族风险。',
'proportion':'9×8×8/DV3105，44palette/7BE/entities[]；576范围全576保存=211nonair365air，无省略。8层64RLE576位置全部实际读，6PNG已看。小室内部约x3..5/z3..5，仅3×3活动轮廓且床/箱/座桌占位；y3..7主体屋盖/隐桶/装饰，无证二层。床2块合1床，不是2住户。',
'facade':'基缘16cobbled_deepslate和12同材底阶，36去皮spruce_wood多轴框配17spruce墙和37darkoak板；9底部open spruce活板护花/基边，3草块与2fern/1age2莓丛。西东z4及北z2共3lightgray薄窗，南4,1/2,6south闭门、两外悬灯2,2,7和6,2,7，内4,3,3另悬灯。灰类图非石瓦真实贴图，空墙牌无中文内容。',
'roof':'49darkoak上下半砖与8darkoak底阶、2spruce顶阶/1spruce顶半砖交错，从宽檐向中心缩进；y6为中央十字板带，y7五个bottom半砖形成小十字顶饰。去皮木梁分隔多向坡角及上部隐桶，呈集中收束的多坡屋盖，不称8楼/整座阁楼。屋脊/梁/半砖不能假作可达梯级，屋面不证防雨、积雪载荷或通风。',
'materials':'西红床3,1,3head和3,1,4foot/north未占，箱5,1,3west原taiga_house表无seed；墙牌4,1,4west原四Text空。5,1,4north sandstone底阶座和5,1,5east oak顶阶/5,2,5盆spruce苗组成小陈设。4,5,4桶facingdown/openfalse实存Slot13可写书Count1，保留原外语pages、displayName、RepairCost0，不翻译抄入任务/伪称中文原创指南。无campfire/炉/烟熏炉/炼药锅/酿造台，不把悬灯当夜烤火设备。',
'circulation':'南4,0,7为south_up入口jigsaw，最终north bottom cobbled_deepslate stair；自身上y1/2air/y3topdarkoak半砖。内4,0,6原cobbled_deepslate，上1/2south闭门；4,0,5村民口最终darkoak板，上1/2/3air；西3,0,5木地上1/2/3air通床脚旁。北4,1,4为空墙牌而非air，4,1/2,3air但y3悬灯；东5,1,4座阶、5,1,5顶阶/5,2,5盆栽阻占。只证分段源格组织，闭门/薄件/床/箱操作和NPC路线未验。隐桶4,5,4下4,4,4top spruce半砖，上4,6,4darkoak板，无梯，不能称可从室内正常取书。',
'ground_support':'y0原石基缘木地贴地，源下y-1与南z8外地形未知；south_up口最终north阶仅声明，不等邻路/落地已拼装。houses池20项中本栋weight3/rigid/legacy_single/emptyprocessor；root oldgrowth村size5/max116/absolute0/WORLD_SURFACE_WG/beard_thin/expansiontrue。直接tag为2oldgrowth原生林+10optional扩展域含1old_growth_snowy_taiga，只说明森林题材、非大雪山自然生成保证。startpool唯一center用street_polish，centerNBT/processor/道路/全图未读未拼，不计实例。'}
limits=[
'原森林单床木屋对cod3 NPC13大雪山木屋只有紧凑居住/雨避辅助空间可借鉴，最多提出1例待Main完整相关性/近族判定，formal0；森林与雪山地形差、无火具、不可达隐桶须保留，Main可判0/HOLD，不为凑数强认雪山/夜烤火。',
'完整44palette全Properties/7BE/entities[]、8层64RLE576格和6PNG实际读看；211nonair含薄件/植物/接口不等实心承重格。屋/床/隐桶/截图/屋盖层不拆实例，指纹不同不是语义唯一证明。',
'F01medium1与F03snowybutcher仅机器指纹及材料/BE预筛，未全palette/RLE/PNG整读，不能加参考。F01同系列/相同单床位置、石木材料与入口接口，构成近族风险；不凭单个桶/缩尺/换顶或文件号差异认定额外1例，需Main整体独立判断。',
'实际读houses池与root/直biometag/startpool共4完整JSON/3metadata。原vanilla taiga村民池/taiga_house loot固定Jar缺失；center引用street_polish processor和centerNBT/路网只见引用未读/拼接，不编造已解析生成效果或完整数据包。',
'南入口jigsaw最终石阶不是当前实物阶，floor0村民口最终木板不等村民已生；原closed门、y3顶半砖和灯保留。墙牌/座阶/盆栽/床箱的薄件碰撞、寻路与操作未运行，静态净空不等NPC可达。',
'屋盖桶朝下、下邻top半砖上邻木板且无梯，只能说原实存可写书NBT，不能说取书已验。外语书保留来源字段/Slot/Count不改成普通书冒充或抄为用户中文任务内容；没有本批游戏资产写入/翻译交付。',
'无火塘/炉具/烟囱，不证明夜烤火/供暖/烹饪；三悬灯不等夜间亮度验收。石基贴地不是吊脚/水文适配，草块snowyfalse和optional雪林tag非雪山/积雪抗载/防雨实测。',
'复用246完整7维10限制的已读单层草顶双床/烛桌组织比较，不重新开旧NBT/PNG。其旧243/245pending文字仅历史状态，243已firstcarry247、245已firstcarry248；239单东入口/firstcarry243、243stew literal100非秒维持有效，均不再加旧信用。',
'COD4接受153/1000缺847不变，NPC01/05/06/12/13累计null；229/232/235/241/246/249待Main。证据完整性不是独立语义/原生验收，适用1000未达，不制作不删未验任务。',
'仅本地Python -B研究/证据落盘，未运行Java/游戏/网络/UI/进程检查/声音亮度唤醒焦点，不触用户实例原档/共享Jar/生产专业资产/主清单/Git/自动化；未宣全部完成或主动工时达标。']
put('manual-review.json',{'batch':249,'case':'F02_OLDGROWTH_MEDIUM_HOUSE2','source':get(P/'sources.json')['candidates'][0],'seven_dimensions':dims,'limits':limits,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_RELEVANCE_AND_NEARFAMILY_PENDING_FORMAL0','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'new_whole_formal_credit_added':0,'formal_credit_added':0,'old245_carry_added':0,'native_acceptance':False,'actual_reading':{'palette':44,'BE':7,'entities':0,'layers':8,'RLE_rows':64,'positions':576,'stored':576,'nonair':211,'air':365,'omitted':0,'PNG_viewed':6,'full_JSON':4,'metadata':3,'old_PNG_NBT_reopened':0}})
p246=R/'docs/architecture/research-20261104-smithy-246/manual-review.json';v=get(p246)
put('saved-complete-family-comparison.json',{'binding':bind(p246),'246_original_seven_dimensions':v['seven_dimensions'],'246_original_limits':v['limits'],'judgment':'249 tiny3x3 singlebed/westbed northeastchest eastseat/planttable and compact converging woodroof hiddenbookbarrel differs246 elongated flaredgrassroof doublebed/candle table hall. This is a whole-layout comparison not credit for material/number/barrel changes. CurrentF01medium1 boundedprefilter shows strong family overlap, requiresMain independentnear-family; no wholeF01 study or credit. Forest/snowmountain relevance narrow, MainmayHOLD0.','historical_supersession':'246 original243/245pending outdated;243firstcarry247 and245firstcarry248 effective.239singleeastentry/firstcarry243 and243stew literal100 notseconds preserved.','old_NBT_PNG_reopened':False,'credit':0})
ps=get(prev/'session.json');common={**{k:ps[k]for k in ['COD4_accepted','COD4_gap','NPC01_total','NPC05_total','NPC06_total','NPC12_total','NPC13_total']},'batch':249,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_RELEVANCE_AND_NEARFAMILY_PENDING_FORMAL0','formal_credit_added':0,'new_whole_formal_credit_added':0,'old239_carry_added':0,'old243_carry_added':0,'old245_carry_added':0,'239_first_carry_batch':243,'243_first_carry_batch':247,'245_first_carry_batch':248,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'active_pending':ps['active_pending']+['249F02_OLDGROWTH_MEDIUM_HOUSE2_NPC13_AUXILIARY_SPACE'],'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'not_master_todo_backup':True,'next':'Main independently review249 whole/source/routes/limited forest-to-NPC13residential relevance/near-family mayHOLD0. Earlier229/232/235/241/246 remain pending.245firstcarry248once only; no applicable1000/no production/taskdeletion.'}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous248_binding':bind(prev/n)})
protected=[]
for x in get(prev/'protected-inputs-current.json')['files']:
 old=x['current248'];cur=bind(old['path']);protected.append({'last248_checkpoint':old,'current249':cur,'unchanged':old==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False,'cod5_missing_not_invented':not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()})
out={};rows=0
for layer in get(P/'F02-full-layer-rle.json')['layers']:
 for row in layer['rows']:
  rows+=1;x=0
  for state,count in row['runs']:
   for xx in range(x,x+count):out[(xx,layer['y'],row['z'])]=state
   x+=count
  assert x==9
names=[pa[b['state']]['Name']for b in bs];rc={tuple(x['pos']):x['state']for x in get(P/'key-source-route-cells.json')};barrel=next(b for b in be if b['nbt']['id']=='minecraft:barrel')
checks={'exact_RLE576_64rows':out==cells and len(out)==576 and rows==64,'extent_stored_no_omission':math.prod(d['size'])==len(bs)==len(cells)==576,'211nonair365air':a['nonair']==211 and a['air']==365,'44palette7BE_entities0':len(pa)==44 and len(be)==7 and d['entities']==[],'six_PNG':len(list(P.glob('*.png')))==6,'fourfullJSON_threemetadata':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['full_JSON'])==4 and len(get(P/'source-context.json')['metadata'])==3,'onebed_onechest_onebarrel_nohearth':names.count('minecraft:red_bed')==2 and names.count('minecraft:chest')==names.count('minecraft:barrel')==1 and not any(n in names for n in ['minecraft:campfire','minecraft:furnace','minecraft:smoker']),'hiddenbarrel_originalbook':barrel['pos']==[4,5,4]and pa[barrel['state']]['Properties']['facing']=='down'and barrel['nbt']['Items'][0]['Slot']==13 and barrel['nbt']['Items'][0]['id']=='minecraft:writable_book'and barrel['nbt']['Items'][0]['Count']==1 and len(barrel['nbt']['Items'][0]['tag']['pages'])==1,'closed_southdoor_insideair':all(rc[(4,y,6)]['Properties']['open']=='false'for y in [1,2])and all(rc[(4,y,5)]['Name']=='minecraft:air'for y in [1,2]),'seven_dimensions10limits':len(dims)==7 and len(limits)==10,'no_oldrepeat_or_newformal':common['formal_credit_added']==common['old239_carry_added']==common['old243_carry_added']==common['old245_carry_added']==0,'protected_eight_unchanged':len(protected)==8 and all(x['unchanged']for x in protected)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'evidence integrity only, not semantic relevance/near-family/native acceptance'})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':249,'status':common['status'],'files':files,'formal_credit_added':0,'new_whole_formal_credit_added':0,'old245_carry_added':0,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
