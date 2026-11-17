import json,hashlib,zipfile,itertools
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-213';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];cells={tuple(b['pos']):b for b in n['blocks']}
check('size DV',n['size']==[7,15,8] and n['DataVersion']==3105)
check('counts',len(pal)==33 and len(n['blocks'])==840 and r['nonair']==119 and r['air']==721 and sum('nbt'in b for b in n['blocks'])==9 and n['entities']==[])
check('full stored volume',len(cells)==840)
check('8 actual viewed diagrams',len(list(P.glob('*.png')))==8)
expected=['All original state indices; air[12]; ?=omitted; rows z; columns x.']
for y in range(15):
 expected.append(f'y={y}')
 for z in range(8):expected.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}' for v,g in itertools.groupby([cells[(x,y,z)]['state'] for x in range(7)])))
check('full RLE exact original120rows840positions',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(expected)+'\n')
check('no ladder stair bed furnace palette',not any(any(k in a['Name'] for k in ['ladder','stairs','bed','furnace','smoker']) for a in pal))
check('six campfires all unlit empty',len(fires:=[b for b in n['blocks'] if pal[b['state']]['Name']=='minecraft:campfire'])==6 and all(pal[b['state']]['Properties']['lit']=='false' and b['nbt']['Items']==[] for b in fires))
check('grindstone support wall',pal[cells[(1,7,3)]['state']]['Name']=='minecraft:grindstone' and pal[cells[(1,6,3)]['state']]['Name']=='minecraft:stone_brick_wall')
check('upper levels8to14allair',all(pal[b['state']]['Name']=='minecraft:air' for b in n['blocks'] if b['pos'][1]>=8))
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:check('source member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
ctx=read(P/'source-context.json');check('three full metadata zero existing context',len(ctx['metadata'])==3 and ctx['candidates'][0]['contexts']==[])
comp=read(P/'saved-complete-family-comparison.json')
for b,c in comp.items():check('full saved judgment '+b,read(c['path'])==c['complete_saved_judgment'] and bind(c['path'])['sha256']==c['sha256'])
seven=dict(
 layout='八细泥砖墙柱承floor3/use4单层小工作亭，北桶、西制图台、南切石机，屋盖高处西端砂轮。不凭不同岗位设备拆成数栋，不把屋顶砂轮叫可达二层。',
 proportion='7×15×8/DV3105，840全保存=119非air+721air、0省略，33palette/9BE/entities[]。全15层120行840格实际读，实物最高y7，y8..14全air；15高不是15层。',
 facade='绿陶土/混凝土粉/瓜/海绵/loom/木柱混合围合，四侧bottom slab与closed bottom活板环檐，南突起west closed栅门上灯。没有标准门，不把封栅当默认可通入口。',
 roof='y5西北斜向top spruce slab链，y6屋面bottom/top slab及closed bottom oak活板，y7东南斜脊为三个unlit campfire，旁配bottom slab与closed bottom spruce活板。类色全格图不表达薄件碰撞，不把屋面营火当加工热源或台阶。',
 materials='切石机(3,4,4)east，下north loom；制图台(2,4,3)下east loom；桶(3,4,2)up Items[]下south loom。砂轮(1,7,3)floor/east下石砖墙。6营火均unlit且Items[]/四槽烹时0，不是已点燃工艺设备。无炉/烟炉/高炉/砧/锻造台/床/梯。',
 circulation='南侧几何呈(0,0,6)top slab→(1,1,7)top slab→(2,2,7)unlit campfire/邻(3,2,7)top slab，再到(3,3,6)bottom slab。起点平面斜邻、营火薄件和半砖高差不等连续楼梯；(4,3,7)closed fence gate非air。地面到工作台连通未证，未运行操作或碰撞；无升至y7砂轮的梯/阶链。',
 ground_support='八柱主要为x2/4,z0/6及x0/6,z2/4的mud brick wall到y2，其中(6,0/1,2)air、仅y2墙，保留东侧一柱下两格缺口。设备下floor3实体loom可辨；柱脚y-1世界及地形/重力/邻居更新未知，细柱不当实心基。')
limits=[
'实际完整读33palette/9BE/entities[]、15层120RLE/840位置，8PNG逐一实际看；3metadata与213完整保存对象逐字段相同后复用，不重复记新增全文阅读；0完整contextJSON。',
'引用minecraft:village/jungle/jungle_village_20池当前固定Jar缺失，全部JSON字面搜索0，仅当前来源范围；root/biome/structureset/processor实现及其它包未读，不补namespace或虚构选择闭环。',
'南侧抬高入口含斜邻、营火/半砖与closed栅门，不能把外形折线当可通楼梯；屋顶砂轮无升降链，东柱下缺口。碰撞/邻居更新/设备和NPC路径/生成完整性未验。',
'完整205七维9限制和213七维7限制原样复用绑定；同为丛林小工作亭/高差平台族，当前不设床也无完整热作区，不因切石机/制图台/砂轮职业替换直接加建筑信用。',
'当前整体静态读完，但用途/入口/支持与选择缺口仍HOLD0；0新合格提议/待审。9BE含6营火+2接头+1桶，砂轮/切石无BE，设备数不算建筑数。',
'157first206和203first209历史各一次+1，本批后续0；COD4153/847，NPC01/05/06总数未知，1000门槛未满足。',
'不改原作者源/生产资产/任务表，不运行Java/游戏/网络，不碰共享Jar、用户实例/原档、声音亮度唤醒焦点、Git发布，不声明全部完成或主动工时。']
put('manual-review.json',dict(batch=214,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions=seven,limits=limits,status='HOLD_WORK_PAVILION_ACCESS_SUPPORT_POOL_ZERO',complete_original_spatial_study=True,new_reference_proposal=0,formal_credit_added=0,actual_reading=dict(palette=33,BE=9,entities=0,layers=15,RLE_rows=120,positions=840,PNG_actual_viewed=8,full_metadata=0,metadata_exact_reuse=3,full_context_JSON=0)))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous213_binding']=bind(PRE/name);d['203first209_current214_increment']=0;d['157first206_current214_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['214F01_work_access_support_pool0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current213'];now=bind(old['path']);protected.append(dict(last213_checkpoint=old,current214=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved213 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=214,status='COMPLETE_ORIGINAL_JUNGLE_WORK_PAVILION_STUDY_HOLD_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Screen saved213remaining camp or shelter candidates for relevant complete building purpose before new full study; no production before1000.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
