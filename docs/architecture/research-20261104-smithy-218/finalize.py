import json,hashlib,itertools,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-217';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
rows=read(P/'raw-source-audit.json')['candidates'];ns=[r['nbt_decoded_original']for r in rows];maps=[{tuple(b['pos']):b for b in n['blocks']}for n in ns]
ck('three components one assembly not three buildings',len(rows)==3 and read(P/'derived-assembly.json')['one_whole_only'])
ck('sizes', [n['size']for n in ns]==[[7,5,8],[3,14,3],[8,6,11]])
ck('palettes and original entity counts',[len(n['palette'])for n in ns]==[22,4,25]and[len(n['entities'])for n in ns]==[0,0,2])
ck('566 stored 467 nonair 99 air 368 omitted',sum(len(n['blocks'])for n in ns)==566 and sum(r['nonair']for r in rows)==467 and sum(r['air']for r in rows)==99 and 934-566==368)
ck('ten full block entities',sum('nbt'in b for n in ns for b in n['blocks'])==10)
for r,n,c in zip(rows,ns,maps):
 expected=['Original indices; ?=omitted NOTair; each z row columns x.'];sx,sy,sz=n['size']
 for y in range(sy):
  expected.append(f'y={y}')
  for z in range(sz):expected.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c.get((x,y,z),{}).get('state','?')for x in range(sx)])))
 ck(r['id']+' full original RLE', (P/f"{r['id']}-full-layer-index-rle.txt").read_text()=='\n'.join(expected)+'\n')
ck('six actual viewed diagrams',len(list(P.glob('*.png')))==6)
ck('fixed archive hash',bind(rows[0]['source_archive'])['sha256']==rows[0]['source_archive_sha256'])
with zipfile.ZipFile(rows[0]['source_archive'])as z:
 for r in rows:ck(r['id']+' original source SHA',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 for collection in [read(P/'source-context.json')['candidates'],[dict(contexts=read(P/'extended-context.json')['contexts'])]]:
  for group in collection:
   for a in group['contexts']:assert hashlib.sha256(z.read(a['member'])).hexdigest()==a['sha256']
ck('all direct and extended context fixed',True)
connectors=[b for n in ns for b in n['blocks']if 'jigsaw'in n['palette'][b['state']]['Name']]
ck('four connectors',len(connectors)==4)
ck('surface carpet hides hatch',ns[0]['palette'][maps[0][(3,1,5)]['state']]['Name']=='minecraft:moss_carpet')
ck('all15 stored north ladders solid south supports',sum(n['palette'][b['state']]['Name']=='minecraft:ladder'for n in ns for b in n['blocks'])==15 and all(n['palette'][c[(b['pos'][0],b['pos'][1],b['pos'][2]+1)]['state']]['Name']=='minecraft:mud_bricks'for n,c in zip(ns,maps)for b in n['blocks']if n['palette'][b['state']]['Name']=='minecraft:ladder'))
ck('three jigsaw ladder final strings omit explicit facing',sum(b['nbt']['final_state']=='minecraft:ladder'for b in connectors)==3)
ck('original nonhuman frog and magma not villagers',{e['nbt']['id']for e in ns[2]['entities']}=={'minecraft:frog','minecraft:magma_cube'})
ck('loaded weakness bottle but no fuel or brew',maps[2][(5,2,8)]['nbt']['Items']==[dict(Slot=1,id='minecraft:splash_potion',Count=1,tag=dict(Potion='minecraft:weakness'))]and maps[2][(5,2,8)]['nbt']['Fuel']==0 and maps[2][(5,2,8)]['nbt']['BrewTime']==0)
# Reuse the written full old whole judgments; do not reopen old images/raw NBT.
comparators={}
for batch in [211,217]:
 f=P.parent/f'research-20261104-smithy-{batch}'/'manual-review.json';comparators[str(batch)]={**bind(f),'complete_saved_judgment':read(f)}
f=P.parent/'research-20261104-smithy-212'/'manual-review.json';comparators['212_saved_correction']={**bind(f),'saved_correction':read(f)}
put('saved-complete-family-comparison.json',comparators)
seven=dict(layout='一个完整短井组合：地表单室生活壳→隐藏竖井→地下工作室及北侧双铁栏囚格。地表不是入口组件独立加1，三NBT合为1研究对象；来源池还容许无井top及medium/long井但未研究，不能额外计数。',proportion='表屋7×5×8，井3×14×3，地下8×6×11，全部DV3465。源坐标原点依次(0,0,0)/(2,-14,4)/(0,-20,-4)，整体界8×25×12。934组件声明格=566stored(467nonair/99air)+368omitted，整体2400格另1466非组件领土不是air。51palette条/10BE/2实体/148RLE行；高度25不代表25层。',facade='地表mud圆角阶收窄小屋，北双高mangrove门、东西brown stained glass pane，外无大阳台或跨层采光；内部moss carpet、vine、床、炉、craftingtable和盆栽。地下packedmud/mudbrick围护，囚格ironbars和指向双格的墙牌；不是沼泽塔楼或人物门诊立面。',roof='地表mud实块逐层收为高4脊，未添加瓦片、檐架或独立烟囱。地下主房顶local4、井口local5；地下顶是埋覆空间的源封盖，不是另一栋地面建筑屋顶。全格示意不证明雨密、自然地形或薄件碰撞。',materials='表屋east炉(1,1,3)空未燃、床(5,1,4foot/5head)south一对。地下watercauldron(5,1,6)level2，brew(5,2,8)在top mangrove slab(5,1,8)，Slot1原装weakness splash potion1，Fuel0/BrewTime0。西箱(1,1,8)east含原lootseed；北栏x2/4,z4,y1/2，牌(3,2,5)south两行箭头。青蛙block(2,1,3)、岩浆怪block(5,1,2)原身体Size3，不是村民/僵尸村民，也不制作新模型。',circulation='表屋北门(3,1/2,1)south/right/closed，内中线地毯可到(3,1,5)，但其下(3,0,5)jigsaw最终top mangrove trapdoor且上覆苔藓地毯，不能当敞口通行。表下接口down_north连井顶up_north；井底down_north连地下顶up_north，单步邻接推导平移已存。井12+地下3共15显式north梯均有south泥砖背板；另外3连接点final_state只写minecraft:ladder，不能从jigsaw朝向擅自补朝向。地下最低梯y2，y1空/地板0，北转(3,1/2,8)显式air可到工作室；囚格铁栏需另操作/改动，不能说NPC自由出入。',ground_support='地下主室floor0，工作台使用1/2，顶4；井四向泥砖十字围护但对角省略，表屋底mud。表屋至地下间高14井一段，无擅自叠多个井。根surface/WORLD_SURFACE_WG/beardthin，start0/size2允许该两次连接的静态推导；实际埋深、液体、更新、旋转及自定义处理器未运行。')
limits=['实际完整阅读51palette条、10BE、2原实体、三组件25层/148RLE行/934声明位置；6张类色示意已查看，三张全层拼板被工具缩览，精确状态以实际阅读原RLE/调取坐标为据，不把缩览当原贴图或实机。', '来源3池+processor+箱loot共5不同直接JSON，扩展根/luckyloot/directbiometag/structureset4JSON均完整读。嵌套#repurposed_structures:collections/mangroves未展开，custom mushroom/waterlogging processor及generic jigsaw/advanced spread Java实现未读运行；元数据沿用旧同固定jar证据，不声称本批新增全文读。', 'root size2/cannot_spawn_in_liquidfalse/emptyspawnoverrides；表四种igloo各weight1，salt626760262 spacing36 separation18。未读其他三种整栋，不把重色/组件列为参考。', '箱原goldenapple和stonesword固定rolls1以及幸运池rolls0/bonus1和自定义旗帜均原样研究；候选loot不等领取/奖励接入，不能把NBT药水当基础物品。', '静态空间合为一栋已有组织，但青蛙/岩浆怪双囚格不是人类治疗；原药水苹果布置不能证明炼药原料→加工→产品物流，更不证明蛙吃怪产蛙明灯的作者工作流。NPC06相关用途不足，作者HOLD0，无达标提议。', '比对211单室锅棚及217多层植物宅的完整保存判断，不重开旧图/NBT，211原盆栽文字勘误以212保存纠正为准；当前深井双囚格虽不同组织，差异不自动构成用途达标。', '3个缺显式facing梯子、表屋苔藓地毯盖活板门、门操作、薄件、怪体积/AI/实体生命周期/地形处理均未原生验；不宣称可达、安全或治愈。', 'COD4正式153/缺847，NPC01/05/06合计未知；157first206及203first209本批均0，无新待审。不删任务，不声称1000或全部完成。', '无Java/游戏/联网/生产资产/Jar/主清单/原档/声音亮度/唤醒焦点/Git写入；只保存本专岗研究，不计等待或主协调工时。']
put('manual-review.json',dict(batch=218,case='ONE_COMPOSITE_F01_F02_F03',seven_dimensions=seven,limits=limits,status='HOLD_NONHUMAN_CONTAINMENT_NOT_PROVEN_ALCHEMY_WORKFLOW_ZERO',complete_original_spatial_study=True,new_reference_proposal=0,formal_credit_added=0,actual_reading=dict(palette_entries=51,BE=10,entities=2,piece_layers=25,RLE_rows=148,piece_positions=934,PNG_viewed=6,different_full_context_JSON=9,new_full_metadata=0)))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous217_binding']=bind(PRE/name);d['203first209_current218_increment']=0;d['157first206_current218_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['218_composite_nonhuman_purpose0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current217'];now=bind(old['path']);protected.append(dict(last217_checkpoint=old,current218=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved217 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=218,status='COMPLETE_ONE_SHORT_SHAFT_IGLOO_COMPOSITE_STUDY_HOLD_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged']for a in protected),next='Choose another frozen-source complete processing building; reuse saved valid judgments, no repeated component/recolor credit or reopening passed views.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected_unchanged=sum(a['unchanged']for a in protected)),ensure_ascii=False))
