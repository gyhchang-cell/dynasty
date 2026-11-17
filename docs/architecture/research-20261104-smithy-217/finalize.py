import json,hashlib,zipfile,itertools
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-216';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
check('size DV',n['size']==[20,25,23] and n['DataVersion']==2586)
check('counts',len(pal)==240 and len(n['blocks'])==5016 and r['nonair']==3789 and r['air']==1227 and sum('nbt'in b for b in n['blocks'])==80 and len(n['entities'])==1)
check('stored omitted distinct',len(cells)==5016 and 11500-len(cells)==6484)
check('12 actual viewed diagrams',len(list(P.glob('*.png')))==12)
expected=['Original state indices; air[40]; ?=omitted NOTair; rows z; columns x.']
for y in range(25):
 expected.append(f'y={y}')
 for z in range(23):expected.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}' for v,g in itertools.groupby([cells.get((x,y,z),{}).get('state','?') for x in range(20)])))
check('full RLE exact575rows11500positions',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(expected)+'\n')
check('three pairs and three orphan feet',all(pal[cells[(6,10,z)]['state']]['Properties']['part']=='head' and pal[cells[(7,10,z)]['state']]['Properties']==dict(part='foot',facing='west',occupied='false') and pal[cells[(8,10,z)]['state']]['Properties']==dict(part='foot',facing='east',occupied='false') and pal[cells[(9,10,z)]['state']]['Name']=='minecraft:dark_oak_trapdoor' for z in [10,11,12]))
check('sole brew empty unfueled',len(brews:=[b for b in n['blocks'] if pal[b['state']]['Name']=='minecraft:brewing_stand'])==1 and brews[0]['pos']==[7,6,10] and brews[0]['nbt']==dict(Items=[],id='minecraft:brewing_stand',BrewTime=0,Fuel=0))
check('two five-step interior runs',all(pal[cells[(8+i,5+i,16)]['state']]['Properties']['facing']=='east' for i in range(5)) and all(pal[cells[(12-i,10+i,6)]['state']]['Properties']['facing']=='west' for i in range(5)))
check('one scaffold not continuous lift',sum(pal[b['state']]['Name']=='minecraft:scaffolding' for b in n['blocks'])==1)
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:check('source member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
ctx=read(P/'source-context.json');gen=read(P/'extended-generation-context.json');check('full direct4 generation3 contexts',len(ctx['candidates'][0]['contexts'])==4 and len(gen['contexts'])==3)
check('ten wine-named potion candidates',len(ctx['candidates'][0]['contexts'][1]['json']['pools'][0]['entries'])==10)
comp=read(P/'saved-complete-family-comparison.json')
for b,c in comp.items():
 original=read(c['path']);original=next(a for a in original['cases'] if a['id']=='F03') if b=='192' else original
 check('exact saved whole judgment '+b,original==c['complete_saved_judgment'] and bind(c['path'])['sha256']==c['sha256'])
seven=dict(
 layout='单整栋三使用标高：floor4/use5白羊毛隔成西设备小间/东通廊及南门后热浴小翼，floor9/use10起居储物三床区接西长露廊，floor14/use15高盖植物陈列房，土台floor15/植物16高一格。两段异向内阶连接；酿造台与植物层隔着中居层，不据空间叠置直接认定炼药供应链。',
 proportion='20×25×23/DV2586，11500声明位置=5016stored(3789非air+1227air)+6484omitted。240palette/80BE/1armorstand；全25层575RLE11500位置、12PNG全部实际读看。y23烟口营火/y24全省略，25高不是25层。',
 facade='stone/cobble/stonebrick厚基、stripped spruce/darkoak与oak框，lightgray wool及concrete/powder隔墙，cyan玻璃和lightblue terracotta；外侧低环廊、西上露廊。28空白sign原无文字，不编中文NPC牌；80BE不是80屋。原infested石砖和重力粉末保留，不自动换普通墙。',
 roof='层檐darkoak/spruce木饰与交叉高坡盖，底层后翼另低坡，顶层石阶/石砖花台下承植物层，收拢lightblue terracotta屋面、木脊和西北烟囱。上坡盖内部列为植物展示，而非第四层；全格灰图不当最终石瓦或雨密证明。',
 materials='唯一brewingstand(7,6,10)在top polishedandesite slab(7,5,10)，Items[]/BrewTime0/Fuel0/三瓶false，东侧(8,5..7,10)显式air；附近dispenser/hopper/skull等空或陈设，不推自动炼药。两smoker空未燃，4campfire均littrue空Items，后翼有magma/bubble_column。三对west床heads x6/feet x7,z10..12，另x8 east三孤foot后x9为open trapdoor，不能称6床。14barrel中多空、少数loot，2箱loot无seed。',
 circulation='外两组三宽北向darkoak阶自z17y0→z16y1→z15y2→z14y3接floor3环廊；北入口(12,5/6,6)south闭门前(12,4,5)bottom south darkoak阶，西设备间(10,5/6,11)west铁门两侧air/墙后buttons需操作，后翼门(13,5/6,17)south。主内南阶(8,5,16)到(12,9,16)逐步向east，上落脚(13,9,16)oak/其上10/11air；中层北阶(12,10,6)到(8,14,6)向west，落脚(7,14,6)darkplank/其上15air。植物床旁open jungletrapdoor是薄围边，不能统称air。单scaffold(6,10,14)上为压力板装饰，不叫连续升降井。操作/碰撞/NPC未跑。',
 ground_support='厚石基带柱支撑外廊与核心，后热浴翼floor4部分下magma/气泡，非普通炼药水槽；高植物层floor14石/infested石砖及木梁承土台floor15，中心水/海草/kelp实际保存。唯一池单source、NBT无强接翼jigsaw；worldsurface/beardthin地形位置未知，外廊与地面、6484省略格及重力/旧DV升级未原生验。')
limits=[
'240palette/全80BE/1实体全文、25层575RLE11500位置及12PNG实际完整读看，2metadata全文；source4JSON(池+三loot)与generation3JSON(根/表/directtag)全文实际读。',
'原根size2/maxdistance8/start0/WORLD_SURFACE_WG/beardthin/emptyspawnoverrides，表house1/forge1/inn2/woodcutter2、salt9928661/spacing50/separation45；只研究house一栋，另三不是3参考，maxdistance8不直接判初片失效。',
'外部#Minecraft:is_taiga、fishes物品tag与四vanilla嵌套loot未读；direct collected missing[]不代表全运行闭环。root/tag/loot配置不等实际生成、奖励或获取回执，未跨网解析customhead纹理。',
'药水loot是10个改名酒/饮料候选，一项Beer包含连续两set_potion函数，原样保留，不宣称两效果或可酿配方；普通loot含blazepowder只是候选，不把基础item冒充NBT变体或把候选当已有燃料。',
'顶层种类包括花、菌、海草/kelp和盆栽陈列，未证明种植条件、采收与炼药用途；无原料→工作间→出药的明确场所分工。三层植物宅与单酿造台可以提供布局启发，但NPC06专门炼药楼相关性不足，作者HOLD0/0提议。',
'三对床与三孤foot、28空牌、14装饰头像、1原armorstand衣物全部保留，不修作者资产、不做新增人物模型或视作NPC入住/骨骼验收。',
'完整192F03/206/211保存whole判断按原对象绑定复用，旧原图/NBT不重开；211盆栽文字旧勘误也绑定212原纠正。比较192公共开放药亭、206低屋高双锅台、211单室锅棚，当前多层植物住宅不同组织不自动满足用途门槛，旧HOLD不追认。',
'原生门操作/阶梯/薄件净空/植物重力/燃烧安全/NPC/世界地形均未运行；静态可辨路线不等实机通过。',
'157first206和203first209后续本批0，COD4153/847，NPC01/05/06总数未知，0新待审。不把5016记录、240palette、80BE、12图或25高度当建筑数量。',
'无Java/游戏/网络/生产Jar/资产/主清单/用户实例原档/声音亮度唤醒焦点/Git变动，不删任务、不声明1000/全部完成或主动工时。']
put('manual-review.json',dict(batch=217,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions=seven,limits=limits,status='HOLD_BOTANICAL_DWELLING_NOT_PROVEN_ALCHEMY_WORKFLOW_ZERO',complete_original_spatial_study=True,new_reference_proposal=0,formal_credit_added=0,actual_reading=dict(palette=240,BE=80,entities=1,layers=25,RLE_rows=575,positions=11500,PNG_actual_viewed=12,full_metadata=2,full_context_JSON=7)))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous216_binding']=bind(PRE/name);d['203first209_current217_increment']=0;d['157first206_current217_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['217F01_botanical_purpose0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current216'];now=bind(old['path']);protected.append(dict(last216_checkpoint=old,current217=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved216 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=217,status='COMPLETE_TAIGA_BOTANICAL_DWELLING_STUDY_HOLD_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Investigate frozen local complete igloo entrance-shaft-basement treatment laboratory assembly if exact pool connections close; one whole only, no component credit, no guessing offsets. Otherwise select another actual complete processing building.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
