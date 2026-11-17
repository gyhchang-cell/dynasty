import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=R/'docs/architecture/research-20261104-smithy-250'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
a=get(P/'raw-source-audit.json')['candidates'][0];d=a['nbt_decoded_original'];pa=d['palette'];bs=d['blocks'];cells={tuple(b['pos']):b['state']for b in bs};be=[b for b in bs if'nbt'in b]
dims={
'layout':'原RS giant_taiga medium_house_2一座完整长条双层石木住宅：floor0/use1东西各一张south床，同一低层连厅，北两门各入床旁，中部沿z2向east的三步内梯到floor3/use4长窄上室，西端east炉、长向活动带及南北玻璃。不是双翼各拆一栋，也非炉在无登临屋顶的装饰物；上层是否原生可达须保留火把/薄件限制。',
'proportion':'14×9×7/DV3465，25palette/8BE/entities[]。882声明位置433保存=370nonair63air，449省略unknown不补air；9层63RLE882位置全部读，6PNG已看。实际lowerfloor0/use1及upperfloor3/topslab→use4；y7上盖、y8多压力板标记不称9生活层，4床块为2完整床不是4住户。长屋内部南北净宽约2格，属紧凑长向分层组织。',
'facade':'110stone主墙、23cobblestone局部粗边、105spruce_planks楼面/墙/屋盖配44spruce半砖，10glass_pane分下南壁4片和上南北壁6片。北5/9,1/2,1两south-facing原closed spruce门，外各5/9,0,0south底石阶；facing south不把物理入口误称南门。外散石/压力板为源边界，类色cube不代表最终石材风化、窗透光或真实薄件。',
'roof':'横向x2..12长木板与spruce上下半砖层层收檐，上方窄双排x2..12,z2/3,y7木板为主体顶盖；y8有22stone_pressure_plate，外围其它压力板合55。处理器会把压力板随机置button/半砖/air，因此不把类色渲染顶层厚灰板当最终石瓦屋顶。内上房另有floor3 top spruce slab，不把所有中层梁误作屋盖；风化/孔洞/抗雪和防雨尚未生成核验。',
'materials':'下西red床4,1,2foot/4,1,3head、下东blue床10,1,2foot/10,1,3head均south/occupiedfalse。上西4,4,3east炉原litfalse/Items[]/CookTime/BurnTime/CookTimeTotal0/RecipesUsed{}；无存料箱/桶/loot或营火，不能声称夜烤火、烤肉供给/实际付款完成。5walltorch保留原facing；2up村民口最终spruceplanks和北7,0,0入口口最终cobble不是3住户。',
'circulation':'北两闭门外阶5/9,0,0上1/2air，门内5/9,1/2,2air，低层中7,2,3walltorch不可填air。梯z2：6,0,2木起步上1/2air，7,1→8,2→9,3三east底阶各自身+1/+2原air。东落脚10,3,2topslab上4air但5west壁火把，不声称两格air。南转9,3,3topslab及沿z3西行x8..5各floor3topslab/use4/5air，接炉east前5,4/5,3air。仅支持分段源格组织，阶侧转身/火把真实碰撞/半砖厚度/闭门操作和完整NPC路线未验。',
'ground_support':'原stone/cobble楼面/边石到y0，源外y-1/北z-1地形未知，不称吊脚/高山落地通过。houses本栋weight3/legacy_single/rigid/mossify，村民pool3候选nitwit/baby/unemployed仅配置。root自有generic_jigsaw_structure/size6/terrainradius2/range22/biomeradius1/start0/WORLD_SURFACE_WG/beard_thin/bounding_box_hack；directtag→giant_taigas集合为2原生oldgrowth林+optional森林域，原wythers old_growth_taiga_swamp重复值保留不算不同案例。没有大雪山自然生成/地形承重验收，startcenterNBT/路网/结构类型实现未读未拼。'}
limits=[
'最多提出1NPC13雪山木屋的辅助完整居住/内梯/炉房空间参考，待Main原源/相关性/近族审查，formal0；原巨杉林长条石木住宅与大雪山题材仍有限差异，不把炉空未燃等同夜烤火功能、NPC入住或已制作任务。Main可HOLD0。',
'25palette全Properties/8BE/entities[]、9层63RLE882格与6PNG实际读看；449省略不是air，370nonair含薄件/标记/接口，不等全实心承重格。两个床翼/两层/炉/楼梯/截图不拆参考，机器hash不同只筛选不自动语义信用。',
'F01butcher与F03mountainfisher只做机器指纹+材料BE预筛，未全palette/RLE/PNG完整研究，均0；不把它们缺床/水池/烟炉拼入本栋。整屋比较用246Main已接受7维/8findings8limits，不重新打开旧源NBT/PNG或重计246。',
'3pool/processor完整JSON+root/directtag/gianttaigas集合3JSON共6及2metadata实际读，contexts无缺文件不等全数据包穷尽。村民各NBT/center/道路/terminator/自有结构类型实现/运行覆盖层未读或装配；optional集合重复值保留不以值数加参考。',
'处理器原cobble/stone多条随机苔石/煤矿/铁矿置换，原pressureplate依序.01button/.01bottomcobbleslab/.99air，未运行不合并成独立概率或说必消失；源pressureplate不是最终持久石屋盖、矿源付款或确切供应链。',
'三east阶本体上2air是真实保存值；x10,z2落脚上y5壁火把不是air。南x9,z3及西行x8..5同floor3topslab上4/5air只给静态替代段，不冒充阶侧转角可走/火把无碰撞/半砖寻路已验。北闭门、底层中央火把和床边操作仍须原生验收。',
'炉empty/unlit/timer0没有烧炼/做饭/供暖回执；上炉前air不等操作或NPC工作站功能。2床非4住户，村民pool3候选非3居民。全源无箱桶loot/实际获得物品，不能普通物品冒充NBT变体/材料付款或发奖励。',
'对照246单层草顶双床中央烛桌，251低层东西双床/北双门/中内阶/上西炉长室的分层组织不同；仅有界已读整体比较，非全世界原创性证明。246首次carry250、245first248、243first247、239first243均后续0；239单东入口/243stew literal100非秒等修正继续有效。',
'COD4接受153/1000缺847不变，NPC01/05/06/12/13累计null。229/232/235/241/249/251仍待Main，证据完整性非语义/原生验收；适用1000门槛未达，不生产不删未验提示词。',
'仅本地Python -B研究/证据落盘，未运行Java/游戏/网络/UI/进程检查/声音亮度唤醒焦点，不触实例原档/共享Jar/生产专业资产/主清单/Git/自动化；不宣全部完成或主动工时达标。']
put('manual-review.json',{'batch':251,'case':'F02_GIANT_TAIGA_MEDIUM_HOUSE2','source':get(P/'sources.json')['candidates'][0],'seven_dimensions':dims,'limits':limits,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_FORMAL0','complete_original_spatial_study':True,'new_reference_proposal_maximum':1,'new_whole_formal_credit_added':0,'formal_credit_added':0,'old246_carry_added':0,'native_acceptance':False,'actual_reading':{'palette':25,'BE':8,'entities':0,'layers':9,'RLE_rows':63,'positions':882,'stored':433,'nonair':370,'air':63,'omitted':449,'PNG_viewed':6,'full_JSON':6,'metadata':2,'old_PNG_NBT_reopened':0}})
p246=R/'docs/cod4/audit-20261022/coordinator-architecture246-actual-whole-NPC13-final-20261112.json';v=get(p246)
put('saved-complete-family-comparison.json',{'binding':bind(p246),'246_Main_seven_dimensions':v['Main_seven_dimensions'],'246_Main_complete_findings':v['Main_findings'],'246_Main_complete_limits':v['Main_limits'],'judgment':'251 long two-level lower twin bedends/northdualdoors/internal east three steps/upperwestfurnaceroom differs246 turf-covered ground-only hall perpendicularbeds/central candlefurniture/pinchedends. Wholeorganization proposal only, not creditforbednumber/furnace/component; forest-to-NPC13snowcabin relevance and family novelty requireMain independent judgment.','old_NBT_PNG_reopened':False,'credit':0})
ps=get(prev/'session.json');common={**{k:ps[k]for k in ['COD4_accepted','COD4_gap','NPC01_total','NPC05_total','NPC06_total','NPC12_total','NPC13_total']},'batch':251,'status':'NEW_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_FORMAL0','formal_credit_added':0,'new_whole_formal_credit_added':0,'old239_carry_added':0,'old243_carry_added':0,'old245_carry_added':0,'old246_carry_added':0,'239_first_carry_batch':243,'243_first_carry_batch':247,'245_first_carry_batch':248,'246_first_carry_batch':250,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':1,'active_pending':ps['active_pending']+['251F02_GIANT_TAIGA_MEDIUM_HOUSE2_NPC13_AUXILIARY_SPACE'],'java_run':False,'game_run':False,'network_used':False,'production':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'not_master_todo_backup':True,'next':'Main independently review251 fullwhole/source/context/stairsegments and upperfurnace/lowerbeds/limitedforest relevance and near-family. Earlier229/232/235/241/249 remain pending.246 firstcarry250 once only then0; applicable1000 unmet no production/taskdeletion.'}
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous250_binding':bind(prev/n)})
protected=[]
for x in get(prev/'protected-inputs-current.json')['files']:
 old=x['current250'];cur=bind(old['path']);protected.append({'last250_checkpoint':old,'current251':cur,'unchanged':old==cur})
put('protected-inputs-current.json',{'files':protected,'this_chat_product_writes':False,'cod5_missing_not_invented':not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()})
out={};rows=0
for layer in get(P/'F02-full-layer-rle.json')['layers']:
 for row in layer['rows']:
  rows+=1;x=0
  for state,count in row['runs']:
   for xx in range(x,x+count):out[(xx,layer['y'],row['z'])]=state
   x+=count
  assert x==14
stored={p:t for p,t in out.items()if t>=0};names=[pa[b['state']]['Name']for b in bs];rc={tuple(x['pos']):x['state']for x in get(P/'key-source-route-cells.json')};furnace=next(b for b in be if b['nbt']['id']=='minecraft:furnace')
checks={'exact_RLE882_63rows':stored==cells and len(out)==882 and rows==63,'extent433stored449unknown':math.prod(d['size'])==882 and len(cells)==len(bs)==433 and sum(t<0 for t in out.values())==449,'370nonair63air':a['nonair']==370 and a['air']==63,'25palette8BE_entities0':len(pa)==25 and len(be)==8 and d['entities']==[],'six_PNG':len(list(P.glob('*.png')))==6,'sixfullJSON_twometadata':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['full_JSON'])==6 and len(get(P/'source-context.json')['metadata'])==2,'twobeds_one_empty_upperfurnace':names.count('minecraft:red_bed')==names.count('minecraft:blue_bed')==2 and furnace['pos']==[4,4,3]and furnace['nbt']['Items']==[]and furnace['nbt']['BurnTime']==0 and pa[furnace['state']]['Properties']['lit']=='false','three_steps_twoair':all(rc[(x,y+h,2)]['Name']=='minecraft:air'for x,y in [(7,1),(8,2),(9,3)]for h in [1,2]),'eastlanding_torch_notair':rc[(10,5,2)]['Name']=='minecraft:wall_torch','upper_southturn_west_segment_furnacefront_air':all(rc[(x,3,3)]['Name']=='minecraft:spruce_slab'and rc[(x,3,3)]['Properties']['type']=='top'and all(rc[(x,y,3)]['Name']=='minecraft:air'for y in [4,5])for x in range(9,4,-1)),'seven_dimensions10limits':len(dims)==7 and len(limits)==10,'no_oldrepeat_or_newformal':common['formal_credit_added']==common['old239_carry_added']==common['old243_carry_added']==common['old245_carry_added']==common['old246_carry_added']==0,'protected_eight_unchanged':len(protected)==8 and all(x['unchanged']for x in protected)}
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'pass':True,'scope':'evidence integrity only, not semantic relevance/near-family/native acceptance'})
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',{'batch':251,'status':common['status'],'files':files,'formal_credit_added':0,'new_whole_formal_credit_added':0,'old246_carry_added':0,'all_tasks_complete':False});print('SEALED',bind(P/'RECEIPT.json'),'FILES',len(files),'CHECKS',len(checks))
