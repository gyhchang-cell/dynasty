import json, hashlib, zipfile, itertools
from pathlib import Path
P = Path(__file__).resolve().parent
PRE = P.parent / 'research-20261104-smithy-223'
ROOT = P.parents[2]
assert not (P / 'RECEIPT.json').exists()
def read(p): return json.loads(Path(p).read_text())
def put(n, d): (P/n).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')
def bind(p):
    p=Path(p).resolve(); b=p.read_bytes()
    return dict(path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):
    checks.append(dict(check=k,passed=bool(v)))
    assert v,k
rows=read(P/'raw-source-audit.json')['candidates']
ck('only selected F01 F04 are whole sources', [r['id'] for r in rows]==['F01','F04'])
for r,size,dv,pc,be,non,air in zip(rows,[[14,11,12],[3,2,3]],[3578,3105],[104,5],[18,2],[706,4],[1142,14]):
    n=r['nbt_decoded_original']; c={tuple(b['pos']):b for b in n['blocks']}
    ck(r['id']+' original size DV palette BE entities stored', n['size']==size and n['DataVersion']==dv and len(n['palette'])==pc and sum('nbt' in b for b in n['blocks'])==be and not n['entities'] and len(c)==size[0]*size[1]*size[2] and r['nonair']==non and r['air']==air)
    lines=['Original state indices; rows z columns x; all declared positions stored.']
    for y in range(size[1]):
        lines.append(f'y={y}')
        for z in range(size[2]): lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}' for v,g in itertools.groupby([c[(x,y,z)]['state'] for x in range(size[0])])))
    ck(r['id']+' all source RLE exact', (P/f"{r['id']}-full-layer-index-rle.txt").read_text()=='\n'.join(lines)+'\n')
    with zipfile.ZipFile(r['source_archive']) as z:
        ck(r['id']+' frozen archive and original member',bind(r['source_archive'])['sha256']==r['source_archive_sha256'] and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
a=read(P/'derived-assembly.json')
ck('one rotated original socket assembly inside host',a['module_origin']==[3,1,9] and a['module_box']==[[3,1,7],[5,2,9]] and a['all_inside_parent'] and a['one_whole_only'])
ck('no overwritten original solid and 709 derived nonair',not a['overlap_nonair'] and a['derived_nonair']==709 and a['source_processor_not_executed'])
allcells=read(P/'derived-source-cells.json')['cells']; cells={tuple(b['pos']):b['state'] for b in allcells}
ck('rotated anvil and chest north',all(cells[q]['Properties']['facing']=='north' for q in [(3,1,7),(3,1,9)]))
ck('chest anvil service fronts explicit air with clear second cell',all(cells[q]['Name']=='minecraft:air' for q in [(3,1,8),(3,2,8),(4,1,8),(4,2,8),(5,1,8),(5,2,8),(5,1,9),(5,2,9)]))
ck('workroom source floor and chest lid clear',all(cells[(x,0,z)]['Name']=='minecraft:dark_oak_planks' for x in range(3,6) for z in range(7,10)) and cells[(3,2,9)]['Name']=='minecraft:air')
ck('north stairs turn east original properties',all(cells[q]['Properties']['facing']=='north' and cells[q]['Properties']['half']=='bottom' for q in [(5,1,4),(5,2,3)]) and cells[(6,3,2)]['Properties']['facing']=='east' and cells[(6,3,2)]['Properties']['half']=='bottom')
ck('scaffold single potted furniture not tower ladder',cells[(8,4,4)]['Name']=='minecraft:scaffolding' and cells[(8,5,4)]['Name']=='minecraft:potted_fern' and not any('ladder' in b['state']['Name'] for b in allcells))
ck('nine new diagrams actually viewed across continuation',len(list(P.glob('*.png')))==9)
contexts={c['member']:c for r in read(P/'source-context.json')['candidates'] for c in r['contexts']}
extended=read(P/'extended-generation-context.json')
with zipfile.ZipFile(rows[0]['source_archive']) as z:
    ck('six distinct new mod JSON contexts exact',len(contexts)==4 and all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256'] for c in list(contexts.values())+extended['contexts']))
    ck('reused towns structure set exact',all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256'] for c in extended['reused221_structure_set']))
v=read(P/'vanilla-local-support-context.json')
ck('vanilla client fixed',bind(v['archive'])['sha256']==v['archive_sha256'])
with zipfile.ZipFile(v['archive']) as z:
    ck('two new vanilla JSON exact',len(v['contexts'])==2 and all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256'] for c in v['contexts']))
for b in [extended['reused221_structure_set_binding'],v['reused222_binding']]: ck('saved support binding '+Path(b['path']).name,bind(b['path'])==b)
old95=read(P.parent/'research-20261104-smithy-216/saved-complete-family-comparison.json')['95']
old221=read(P.parent/'research-20261104-smithy-221/manual-review.json')
put('saved-complete-family-comparison.json',dict(saved095_binding=bind(old95['path']),saved095_seven_dimensions=old95['complete_saved_case']['observations'],saved221_binding=bind(P.parent/'research-20261104-smithy-221/manual-review.json'),saved221_seven_dimensions=old221['seven_dimensions'],comparison='095下西侧石作棚+内竖梯上北西砧室/东药室/南床室；221中央高石火台+绕行阶升磨石、无住室。本例南西独立单层三器具冷作间，经南铺地前庭到北起居厅，内折阶上北卧室/南屋顶边廊再东卧室；工作集中前间而起居分上下后部，不以职业、砖色或工具换装计差异。完整空间组织最多提NPC01相关1，仍须Main独立适用/近族核查；不保证历史语义全库唯一。',old_NBT_or_PNG_reopened=False))
seven=dict(
layout='同一14×11×12伊比利亚中屋4通过原profession socket接一个3×2×3工具匠模块：南西独立前间放箱/砧/锻造台，南中铺地前庭分向北起居厅和东底层床室，北厅折阶上北卧室，再经南门/边廊向东上卧室。不是三个独立住屋，也不把模块当建筑。',
proportion='宿主DV3578/104palette/1848stored=706非air1142air，模块DV3105/5palette/18stored=4非air14air；均无省略、无entity。共1866源坐标记录，模块18格在宿主范围内重合，独立bbox1848格，原非air零覆撞，忽略air/finalstate后709非air。只两层使用标高1与4；y7骷髅装饰区没有连续梯阶，不叫第三经营层。9张新合成/剖面/横断图实际看完，宿主11层132RLE与模块2层6RLE全读。',
facade='185bricks主墙、63andesiteslab基铺地、深色darkoak内地/折阶，18blackstainedglasspane窄窗；spruce木楼面、活板门檐饰与jungle座椅/空白sign。六扇sprucedoor上下对共12块，不当12入口。独立西前间低盖和后方双层房体在同一铺地基座组合，实材质不等于分类色块图的灰棕。',
roof='spruceplanks77/slabs116/stairs18组成错高屋盖、短檐和后段高盖，trapdoor63含檐饰/栏边，不都当屋顶。低工作间盖y3附近、中后盖y6、东南高装饰盖至y10，最高层并不表示新营业层；脚手架8,4,4仅一块，上8,5,4盆蕨，不能拿它解释通往顶层。',
materials='模块源胸(0,0,0)east与chippedanvil(2,0,0)east逆时针90后均north，合成胸3,1,9、砧3,1,7，smithingtable4,1,9。原toolsmithloot无seed仅候选非实存；另两宿主箱用savannahouse候选loot无seed。三完整床对：底蓝east(9/10,1,6)，上青north(8,4,2/3)，上浅蓝north(10,4,6/7)。无炉/熔岩/热锻链；骷髅头9,7,7是源skull BE非生物人物。',
circulation='工作前间东门6,1/2,9east/right/closed，东7,1,9是wall_sign而非air，头7,2,9air；侧7,1/2,8air，南7..9,1,10air。胸north前3,1/2,8air，砧东/南4,1/2,7和3,1/2,8服务位，工作台北4,1/2,8与东5,1/2,9air，floor0darkoak连续；箱顶3,2,9air。北厅bottomnorth阶5,1,4→5,2,3到5,2,2双slab上，再东bottom阶6,3,2→7,3,2topstairs接上层use4；邻torch、栏片、门需碰撞实机验。南接街socket6,0,11finalandesite，上方6,1,11openbottomtrapdoor/6,2,11closedtoptrapdoor，不称该格无阻；东8,0,11north底阶上8,1/2,10clear进铺地前庭是静态备选，不证明道路对接或NPC已通过。',
ground_support='host up_east/aligned(5,0,8)→上邻格，child down_south/aligned(1,0,2)以CCW90(x,y,z)=(z,y,-x)变down_east，origin(3,1,9)，childbox3..5/1..2/7..9全在host内部。parenttarget=childname bottom，原地板在接口finaldarkoakplanks；legacy忽略air/structurevoid且未执行houseprocessor，不能当清空世界或实际原生生成。root village_iberian size4/max116/start0/WORLD_SURFACE_WG/beardthin，towncenters未重建，directtag14optional第三方群系，注册/街路/地形未知。')
limits=[
'最多一个完整NPC01冷作/工具维护工住空间参考；模块、房间、床位、同宿主换职业/换色及截图不另计。与095/221保存完整七维文本比较，历史hash未命中不证明全语义去重。',
'原始108?不是108：宿主104+模块5共109palette原状态全读；18+2BE全读，实体均空；F02/F03仅界面筛选，未读完原始全源/未画整栋，不计数。',
'九PNG是源格分类图，没有原生纹理/薄件碰撞；closeddoor、wall_sign、stairs、torch、trapdoor、头顶/箱盖、砧与工作台范围、居民寻路未原生验。上装饰骷髅区无连续上行设施。',
'houses中medium4权2；host实际chance1，toolsmith权1，chance2权3只上下文而非选中池。chance1名称不等空概率；其它职业池选项不当新参考或实际生成。',
'houseprocessor四条随机brick/andesiteslab替换未运行；input Properties字段按原JSON保留，不声称BlockMatch会按它过滤或各概率互斥。Legacy/Single/JigsawPlacement/parent canAttach只复用221/223已读限定片段，不称读完或运行整个引擎。',
'六个新mod JSON、两个新vanilla JSON全文实际读；townsset与toolsmithloot复用准确旧收据。savanna villagers只权1nitwit/1baby/10unemployed池，实际村民NBT未读未生成，四villager socket不等四入住NPC；所有箱loot不当已获得材料/付款/任务回执。',
'224新案例只提最多1待独立验收，正式增量0；本批另对221已正式验收整栋首次carry NPC01增量1且仅此一次，157/203不再加。COD4保持153/847，NPC01/05/06累计未知，1000适用门槛未满足，不制作/删任务。',
'不运行Java/游戏，不联网/操作实例/存档/声音/亮度/焦点，不写生产资产/共享Jar/主清单/Git。不把研究收据当建筑已制作或中文任务/指南针已同步；无主动工时或全部完成声明。']
limits[1]=limits[1].replace('原始108?不是108：','')
put('manual-review.json',dict(batch=224,case='F01_HOST_PLUS_F04_TOOLSMITH',seven_dimensions=seven,limits=limits,status='ONE_COMPLETE_COLD_TOOL_WORK_DWELLING_MAX1_NPC01_PENDING',new_reference_proposal=1,formal_credit_added=0,native_acceptance=False,actual_reading=dict(new_palette=109,new_BE=20,new_entities=0,new_piece_layers=13,new_RLE_rows=138,new_source_positions=1866,new_PNG_viewed=9,new_full_JSON=8,reused_full_JSON=2,old_PNG_reopened=0)))
route=[dict(pos=b['pos'],state=b['state']) for b in allcells if (2<=b['pos'][0]<=8 and 6<=b['pos'][2]<=11 and b['pos'][1]<=3) or (5<=b['pos'][0]<=7 and 2<=b['pos'][2]<=5 and b['pos'][1]<=5)]
put('key-source-derived-route-cells.json',dict(cells=route,static_not_collision_or_native=True))
final=ROOT/'docs/cod4/audit-20261022/coordinator-architecture221-actual-author-ACK-final-acceptance-20261111.json'
f=read(final); ack=PRE/'actual-author-ACK-221.json'; manual=P.parent/'research-20261104-smithy-221/manual-review.json'
ck('final Main acceptance exact',bind(final)['sha256']=='c8d6d7963c21c2f5aaebe13a77874e78e9456e78080bd7dd1f4ad63d15f1fa6c' and f['accepted_related_complete_NPC01_reference']==1 and not f['first_carry_already_observed'])
ck('original seven and eight exact preserved',f['original_seven_dimensions_preserved']==old221['seven_dimensions'] and f['original_eight_limits_preserved']==old221['limits'])
ck('actual author ACK exact',bind(ack)==f['actual_author_ACK'])
carry=dict(case='221F01_HOST_PLUS220F08',first_bound_batch=224,increment=1,scope='NPC01 complete related architecture only',COD4_increment=0,NPC01_cumulative_total=None,final_acceptance_binding=bind(final),original_whole_manual_binding=bind(manual),original_whole_receipt_binding=bind(manual.parent/'RECEIPT.json'),actual_author_ACK_binding=bind(ack),actual_author_receipt_binding=bind(PRE/'RECEIPT.json'),final_acceptance_entire_object=f,actual_author_ACK_entire_object=read(ack),not_production_or_TODO_authority=True)
put('first-carry-221.json',carry)
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
    d=read(PRE/name);d['previous223_binding']=bind(PRE/name);d['221accepted_first224']=carry
    d['203first209_current224_increment']=0;d['157first206_current224_increment']=0
    d['current_batch_formal_credit_added']=1
    if name.startswith('carried'):
        d['current_batch_new_pending']=1
        d['current_batch_pending_cases']=[dict(case='224F01_HOST_PLUS_F04_TOOLSMITH',NPC='NPC01',maximum_independent_credit=1,formal_credit_added=0,status='PENDING_MAIN_INDEPENDENT_WHOLE_RELEVANCE_AND_SEMANTIC_DEDUP')]
        d['221_resolved_accepted_first224']=True
    put(name,d)
protected=[]
for old in read(PRE/'protected-inputs-current.json')['files']:
    b=old['current223'];now=bind(b['path']);protected.append(dict(last223_checkpoint=b,current224=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True))
ck('eight protected files unchanged',len(protected)==8 and all(q['unchanged'] for q in protected))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=224,status='221_FIRST_CARRY1_AND_NEW_IBERIAN_WHOLE_MAX1_PENDING',formal_credit_added=1,formal_credit_scope='221 previously finally accepted NPC01 only;224 candidate0',accepted221_first224_current_increment=1,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=1,active_pending=['224F01_HOST_PLUS_F04_TOOLSMITH'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not q['unchanged'] for q in protected),next='Main independent224 whole relevance and dedup; continue different whole, no same-host profession variant.221 first224 recorded once, future carry zero.')
put('session.json',s);put('active-checkpoint.json',s)
files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json']
put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected_unchanged=sum(q['unchanged'] for q in protected)),ensure_ascii=False))
