import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=R/'docs/architecture/research-20261104-smithy-245'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
a=get(P/'raw-source-audit.json')['candidates'][0];d=a['nbt_decoded_original'];pa=d['palette'];bs=d['blocks'];cells={tuple(b['pos']):b['state']for b in bs};be=[b for b in bs if'nbt'in b]
dims={
'layout':'原snowy_taiga_small_house_4是一座完整单层草皮覆顶木屋，floor0/use1公共起居单室：南端门进门斗，中央木阶/角阶桌椅及四烛组，西靠壁一张south黄床、北靠壁一张north黄床，东北一个west箱。东西侧鼓出、南北端收窄，不是另两间房或二层。对NPC13雪山木屋夜间居住/雨避辅助空间提出至多一例，不能把双床/草顶/桌椅拆建筑。',
'proportion':'9×8×11/DV3105，51palette/14BE/entities[]。792范围全792保存=383nonair409air，无省略；8层88RLE792格全读，6PNG全看。实际只有floor0/use1；上y3..6为覆顶/木梁，y7仅5个tall_grass上半，不是可用阁楼或8楼。两床4块，非四床/四住户。',
'facade':'39去皮spruce_log立架配55spruce_planks墙，外18top closed spruce活板基边，北4,2,1一片brown玻璃，南4,1/2,9north-facing闭spruce门。墙体侧鼓与两端收窄形成小厅；门朝north是block facing，门物理位置在南端z9，不写成北外入口。桌椅侧五个jungle墙牌全文空，非中文牌或已接任务文案。',
'roof':'屋面以59grass_block/snowyfalse与55spruce阶、去皮z轴木梁、4bottom半砖结合：两端前后山墙木脊在x4，东西阶坡搭草皮外缘；中段草顶从侧y2/3升至中y5，上有grass28/tall_grass40装饰。源草顶不是石瓦、积雪已覆盖或自然地形；上部草植物不计阁楼，跨间顶梁也不当楼梯。',
'materials':'地板22darkoakplanks及3redwool、上4redcarpet，中央jungle阶7含顶角/底阶组成座桌，4,2,5一格littrue/candles4是四烛组，南4,3,10一hanging灯。两完整黄床：2,1,5foot→2,1,6head/south与3,1,2head→3,1,3foot/north；5,1,2 west箱原taiga_house loot无seed。无campfire/炉/烟熏炉/炼药锅/酿造台，不当烤火或制药完成。三up村民接头finaldarkoakplanks，南building_entrance empty口finalstructure_void，非4居民或另一栋房。',
'circulation':'南口4,1,10为south_up jigsaw/empty最终structure_void不是源air，地面4,0,10dirt，y2air、y3悬灯；门4,1/2,9原closed，门内4,1/2,8air且floor0木板，y3为top阶。x3/5,z8两格air但floor5,0,8为村民口最终木板，门内可横分。继续北z7中x4是bottom jungle座阶，两侧x3/5为墙牌，北床前4,1,3又是墙牌，西侧3,1,5是红毯。逐格原状态保留，不把所有家具薄件简化air或声称完整门→床/箱寻路无阻。',
'ground_support':'y0屋内木楼面与外dirt/path轮廓贴地，不是吊脚/水上或高台；源外y-1自然地形和门外道路未知。houses池17项中本栋weight5/legacy_single_pool/rigid/vanilla街道雪处理器；root雪针叶村size6/max116/WORLD_SURFACE_WG/absolute0/beard_thin/expansiontrue，towncenter池只有原meeting_point_1。直tag基准snowy_taiga+16optional扩展值含原无namespace snowy_coniferious_forest，保持原拼；雪域相关不等大雪山自然生成适配。未读centerNBT/街道/终止池或全装配，不拿它们加数。'}
limits=[
'对cod3 NPC13大雪山木屋夜烤火雨避只提出max1辅助居住空间参考，待Main独立整栋相关性/近族认可，formal0。单室双卧铺/桌椅与241单床炊事高桶附东院不同；本栋无火塘/炉具，不能说满足夜烤火、雪山选址、猎获交易或任务接入。',
'完整51palette Properties、14BE、entities[]、8层88RLE792格与6PNG实际读看；383nonair含薄件/草植物/接口，不等383实心承重方块。截图、旋转、双床、草屋顶/接口均不拆参考，机器指纹不同仅预筛，不证明语义唯一。',
'一houses完整JSON及root/直biometag/towncenter3JSON、3metadata已读。固定Jar缺vanilla taiga村民池/taiga_house loot/street_snowy_or_taiga processor，未假称已读/作用已解；原始街道/终止池/结构集/运行覆盖层未核。',
'南外门block facing north仍是南z9入口，外4,1,10为jigsaw最终structure_void不是直接air；不能把接口替换/相邻地形拼接当已验。三村民口最终木地板只保存语义，不称三居民，entities[]也不保证生成后永远无人。',
'入口内z8上top阶为头顶y3，不误判y1/2堵死；但z7中座阶两侧墙牌、北箱前墙牌与床侧红毯均保留，不宣全通。closed门/床/箱/薄件/蜡烛碰撞及NPC生活路线从未运行，类色立方图不代表原生薄件模型。',
'中央四烛组lit与悬灯不能当营火/烤肉工作位或原生照明/火灾安全验收；没有火炉/烟囱不补想象厨房。taiga箱loot表当前未读，不编造库存、玩家材料付款或原生获取回执。',
'草块snowyfalse及其植物是原保存状态，不能说已经积雪/适配雪载或不漏雨；雪针叶村root/tag不保证大雪山地形。无namespace optional snowy_coniferious_forest原值保留，不擅自改成推测modID。',
'完整复用241七维/10限制做单室空间对照，不重新打开旧NBT/PNG；其旧239双入口和239pending仅原历史，已被242及Main239最终单东入口和firstcarry243替代，不恢复旧判断或重复加239/226等信用。',
'COD4接受153/1000缺847不变，NPC01/05/06/12/13累计null；229/232/235/241/243/245/246待Main，证据完整性不代表独立语义或原生验收。适用1000门槛未达，不生产、不删未验提示词。',
'仅本地Python -B研究，未运行Java/游戏/网络/UI/声音亮度/唤醒焦点/进程检查，未触用户实例原档/共享Jar/生产专业资产/主清单/Git/自动化。未宣全部完成或主动工时达标。']
put('manual-review.json',{'batch':246,'case':'F01_SNOWY_TAIGA_SMALL_HOUSE4','source':get(P/'sources.json')['candidates'][0],'seven_dimensions':dims,'limits':limits,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_FORMAL0','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'new_whole_formal_credit_added':0,'formal_credit_added':0,'old239_carry_added':0,'native_acceptance':False,'actual_reading':{'palette':51,'BE':14,'entities':0,'layers':8,'RLE_rows':88,'positions':792,'stored':792,'nonair':383,'air':409,'omitted':0,'PNG_viewed':6,'full_JSON':4,'metadata':3,'old_PNG_NBT_reopened':0}})
p241=R/'docs/architecture/research-20261104-smithy-241/manual-review.json';v=get(p241)
put('saved-complete-family-comparison.json',{'binding':bind(p241),'241_original_seven_dimensions':v['seven_dimensions'],'241_original_limits':v['limits'],'judgment':'246 ground single hall/two perpendicular beds/central candle seating/grass covered narrow ends differs241 ground singlebed/northsmoker/highsouthbarrels/eastseparate animalpen/woodroofchimney. Scope only oneNPC13 auxiliary residential proposal, not automatic formal acceptance or globalnovelty. No campfire in246.','historical_supersession':'241 original239 dualentry/pending comparison is withdrawn history;242 corrected singleeastentry/Mainfinal239/firstcarry243 effective, no re-add246.','old_NBT_PNG_reopened':False,'credit':0})
ps=get(prev/'session.json');common={**{k:ps[k]for k in ['COD4_accepted','COD4_gap','NPC01_total','NPC05_total','NPC06_total','NPC12_total','NPC13_total']},'batch':246,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_FORMAL0','formal_credit_added':0,'new_whole_formal_credit_added':0,'old239_carry_added':0,'239_first_carry_batch':243,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'active_pending':ps['active_pending']+['246F01_SNOWY_TAIGA_SMALL_HOUSE4_NPC13_AUXILIARY_SPACE'],'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'not_master_todo_backup':True,'next':'Main independently review246 purpose/complete whole/source/context/circulation/near-family. Earlier229/232/235/241/243/245 remain pending;239 only firstcarry243 then0. Continue different related complete architectural references before applicable1000, no production.'}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous245_binding':bind(prev/n)})
protected=[]
for x in get(prev/'protected-inputs-current.json')['files']:
 old=x['current245'];cur=bind(old['path']);protected.append({'last245_checkpoint':old,'current246':cur,'unchanged':old==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False,'cod5_missing_not_invented':not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()})
out={};rows=0
for layer in get(P/'F01-full-layer-rle.json')['layers']:
 for row in layer['rows']:
  rows+=1;x=0
  for state,count in row['runs']:
   for xx in range(x,x+count):out[(xx,layer['y'],row['z'])]=state
   x+=count
  assert x==9
names=[pa[b['state']]['Name']for b in bs];rc={tuple(x['pos']):x['state']for x in get(P/'key-source-route-cells.json')}
checks={'exact_full_RLE792_88rows':out==cells and len(out)==792 and rows==88,'extent_stored_no_omission':math.prod(d['size'])==len(bs)==len(cells)==792,'383nonair409air':a['nonair']==383 and a['air']==409,'51palette14BE_entities0':len(pa)==51 and len(be)==14 and d['entities']==[],'six_PNG':len(list(P.glob('*.png')))==6,'four_fullJSON_three_metadata':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['full_JSON'])==4 and len(get(P/'source-context.json')['metadata'])==3,'two_full_beds_one_chest_no_fireplace':names.count('minecraft:yellow_bed')==4 and sum(pa[b['state']].get('Properties',{}).get('part')=='head'for b in bs)==2 and names.count('minecraft:chest')==1 and not any(n in names for n in ['minecraft:campfire','minecraft:furnace','minecraft:smoker']),'three_villager_one_void_entrance':sum(b['nbt'].get('pool')=='minecraft:village/taiga/villagers'for b in be)==3 and sum(b['nbt'].get('final_state')=='minecraft:structure_void'for b in be)==1,'closed_southdoor_inside_twoair':all(rc[(4,y,9)]['Properties']['open']=='false'for y in [1,2])and all(rc[(4,y,8)]['Name']=='minecraft:air'for y in [1,2])and rc[(4,1,10)]['Name']=='minecraft:jigsaw','seven_dimensions10limits':len(dims)==7 and len(limits)==10,'no_repeat239_or_new_formal':common['formal_credit_added']==common['old239_carry_added']==0,'protected_eight_unchanged':len(protected)==8 and all(x['unchanged']for x in protected)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'evidence integrity only; not independent semantic or native acceptance'})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':246,'status':common['status'],'files':files,'formal_credit_added':0,'new_whole_formal_credit_added':0,'old239_carry_added':0,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
