import json, hashlib, zipfile, itertools
from pathlib import Path
P=Path(__file__).resolve().parent
PRE=P.parent/'research-20261104-smithy-224'
assert not (P/'RECEIPT.json').exists()
def read(p): return json.loads(Path(p).read_text())
def put(n,d): (P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
    p=Path(p).resolve();b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(k,v):
    checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original']
c={tuple(b['pos']):b for b in n['blocks']};pal=n['palette']
ck('host original source history eligible',read(P/'pre-render-history-screen.json')['rows'][0]['eligible_for_new_source_study'])
ck('15x9x11 DV3578 70palette 13BE 0entity',n['size']==[15,9,11] and n['DataVersion']==3578 and len(pal)==70 and sum('nbt'in b for b in n['blocks'])==13 and not n['entities'])
ck('all1485positions 538nonair947air no omission',len(c)==1485 and r['nonair']==538 and r['air']==947)
lines=['Original state indices; rows z columns x; all declared positions stored.']
for y in range(9):
    lines.append(f'y={y}')
    for z in range(11): lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[(x,y,z)]['state']for x in range(15)])))
ck('new host9layers99RLE1485 positions exact',(P/'F01-full-layer-index-rle.txt').read_text()=='\n'.join(lines)+'\n')
reuse=read(P/'reused-component.json');b=reuse['source_binding']
ck('reused224 full original child binding fixed',bind(b['path'])['sha256']==b['sha256'] and reuse['component']==read(b['path'])['candidates'][1])
ck('reused component RLE byte exact',(P/'F04-full-layer-index-rle.txt').read_bytes()==(PRE/'F04-full-layer-index-rle.txt').read_bytes())
a=read(P/'derived-assembly.json');allcells=read(P/'derived-source-cells.json')['cells'];d={tuple(b['pos']):b['state']for b in allcells}
ck('original parent up_south aligned and child down_south aligned',pal[c[(11,0,7)]['state']]['Properties']['orientation']=='up_south' and c[(11,0,7)]['nbt']['joint']=='aligned' and reuse['component']['nbt_decoded_original']['palette'][4]['Properties']['orientation']=='down_south')
ck('original assembly no rotation inside bbox zero overwrites',a['module_origin']==[10,1,5] and a['module_box']==[[10,1,5],[12,2,7]] and a['all_inside_parent'] and not a['overlap_nonair'] and a['derived_nonair']==541)
ck('toolsmith service cells and chest lid explicit air',all(d[q]['Name']=='minecraft:air'for q in [(11,1,5),(11,2,5),(11,1,6),(11,2,6),(12,1,6),(12,2,6),(10,2,5),(11,1,7),(11,2,7)]))
ck('workroom full floor0 darkoak',all(d[(x,0,z)]['Name']=='minecraft:dark_oak_planks'for x in range(10,13)for z in range(5,8)))
ck('ladder four continuous south-facing original cells',all(d[(7,y,2)]['Name']=='minecraft:ladder' and d[(7,y,2)]['Properties']['facing']=='south'for y in range(1,5)))
ck('ladder upper exit air landing top slab',all(d[q]['Name']=='minecraft:air'for q in [(7,5,2),(7,4,3),(7,5,3),(6,4,3),(6,5,3)]) and d[(7,3,3)]['Properties']['type']=='top')
ck('jukebox source has no playing record',c[(5,4,3)]['nbt']['IsPlaying']==0 and pal[c[(5,4,3)]['state']]['Properties']['has_record']=='false')
ck('final_state slab properties preserved',d[(7,0,9)]['Name']=='minecraft:andesite_slab' and d[(7,0,9)]['Properties']['type']=='double')
ck('eight final current diagrams viewed',len(list(P.glob('*.png')))==8)
ctx=read(P/'source-context.json')['candidates'][0]['contexts']
priorctx={c['member']:c for row in read(PRE/'source-context.json')['candidates']for c in row['contexts']}
with zipfile.ZipFile(r['source_archive'])as z:
    ck('frozen archive and member exact',bind(r['source_archive'])['sha256']==r['source_archive_sha256'] and hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
    ck('all three context objects exact previous full reading reuse',len(ctx)==3 and all(c==priorctx[c['member']] and hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx))
support=[bind(PRE/f)for f in ['source-context.json','extended-generation-context.json','vanilla-local-support-context.json']]
put('support-context-reuse.json',dict(bindings=support,source_contexts_reused_exact=ctx,root_and_tag_and_townsset_reused_entire_object=read(PRE/'extended-generation-context.json'),vanilla_reused_entire_object=read(PRE/'vanilla-local-support-context.json'),new_full_JSON_reads=0,old_NBT_or_PNG_reopened=False,limits='Reuse224 houses/chance1/processor complete written objects, Iberian root/tag, townsset and vanilla savanna villager/house loot/toolsmith loot. Does not count any new architecture or generated inhabitants.'))
old=read(PRE/'manual-review.json')
comparison=dict(previous224_binding=bind(PRE/'manual-review.json'),previous224_seven_dimensions=old['seven_dimensions'],previous224_limits=old['limits'],older095_221_comparison_binding=bind(PRE/'saved-complete-family-comparison.json'),comparison='224南西工作前间接前庭/北内折阶上卧室/南边廊东上卧室；225东低工作间与西南单床间隔着中通道，北部底单床上内竖梯到书架唱片机小室。当前上下层功能与工具间/通道/两间底床室关系不同，不以房号、旋转或相同工具模块判新。与095上三分工作/药/床不同，也不是221中央高火台环阶工坊。只有完整关系最多1待Main独立判断，不证明穷尽历史语义库。',old_NBT_or_PNG_reopened=False)
put('saved-complete-family-comparison.json',comparison)
seven=dict(
layout='原Iberian中屋6与唯一原工具匠模块组成一个15×9×11工住组合：南中通道两侧是西南单床小室和东低盖工具间；通道北门进入北楼底单床/箱室，北墙内竖梯上书架与空唱片机小室。工具与卧室分侧、娱乐书室在北上层，非224内阶上两卧室布局，所有围合和共同铺地属同栋。',
proportion='新宿主DV3578/70palette/13BE/entities0，全1485格=538非air947air，无省略；旧模块DV3105/5palette/2BE/entities0、18格/4非air14air完整证据复用，不重开旧图。149?实际1503源记录(1485+18)包含18重合，独立bbox仍1485；final后541非air。宿主9层99RLE全读，8最终PNG看完，只有使用标高1与4，不将9高作9层；屋脊y8薄件。',
facade='129bricks基墙、andesiteslab63含基座，darkoak板20/上层TOPslab与spruce楼盖。13blackglass窄窗，spruce四扇门8上下块；南中开通道两侧低翼、北两层小楼，薄trapdoor檐和花盆点缀。类别灰格不代表原材质或完整碰撞。',
roof='spruceplanks56、slabs101、stairs1、trapdoor50和fencegate8构成西南/东侧低坡盖、北上层较高双坡叠檐。北阁室墙至y6、盖y7/8，南北/侧柱与砖墙接地，不把顶层窗、悬链3/灯6当额外室/承重机构；无独立室外高塔经营层。',
materials='旧工具模块不旋转：胸10,1,5east，chippedanvil12,1,5east，smithingtable10,1,6。胸原toolsmithloot无seed是候选非库存；宿主胸5,1,4east用savannahouse无seed。两完整床对：西南蓝3,1,7foot→3,1,8headsouth，北青5,1,2head→5,1,3footnorth。北上jukebox5,4,3原has_recordfalse/IsPlaying0，书架4块、空白sign两块；不播放声音、不编NPC/中文任务。无炉或热锻设施。',
circulation='南接街socket6,0,10finalandesite，其上6,1,10openbottomtrapdoor不是air；旁8,1/2,10air接中通道7,1/2,9air，家具/灯/薄件实际碰撞未验。工具间westdoor9,1/2,7west/right/closed及southdoor11,1/2,8south/left/closed；内11,1/2,7→11,1/2,6→11,1/2,5clear，分别服务工作台/胸，砧south位12,1/2,6clear，胸顶10,2,5air。北门7,1/2,5south/left接北室，梯7,y1..4,z2south，南侧7,1/2,3air；上7,5,2air，南出口7,4/5,3air，floor7,3,3TOPdarkoakslab，西6,4/5,3air也有同高板。只静态有连续梯和落脚，不称NPC攀爬、箱盖/砧交互通过。',
ground_support='host up_south aligned11,0,7，上邻格减childdown_south aligned1,0,2得origin10,1,5，childbox10..12/1..2/5..7全内含，无原nonair覆撞。floor0工作间全darkoak，hostsocketfinal板；三个villager底socket一darkoak、两andesiteslab[type=double]属性已正确保留。legacy忽略air/structurevoid和processor只源码证据复用，未清空世界。Iberian root size4/max116/heightmap/start0/beardthin，14optional biome/tag与townsset证据复用，towncenters/road/terrain未完整重建或原生验。')
seven['proportion']=seven['proportion'].replace('149?实际','共')
limits=[
'仅宿主加一个原工具模块作为最多1完整NPC01相关冷作工住参考；旧模块单独0，同宿主换职业/颜色/旋转/房间/截图零额外信用。历史hash筛选只排exact，整体组织仍交Main独立适用和语义近族判断。',
'实际新全文70palette/13BE/0entities，9层99RLE1485位置、8最终PNG；旧224组件5palette/2BE/2层6RLE18位置只固定证据复用，不声称本批新读旧原始NBT/旧PNG。首次图标题house4误标在未封存阶段已改成house6并看最终图，不将重复查看计新参考。',
'图是源格分类与finalstate静态推导，非原纹理、碰撞或实机；门开合、薄件/灯、梯出口、NPC路径、胸盖/工具作用范围未验，梯存在不等居民已能用。',
'host实际houses medium6权2、chance1工具权1，复用224已读完整三个池/processor对象，不借chance2权3或其他职业计数。house随机砖/石替换未运行，input Properties含义不超原源码证据；Legacy/canAttach仅复用限定片段。',
'两床对、三个villager socket并非三个实存NPC；原空jukebox无唱片不播放。上层书室不当新增炼药/锻造室，箱loot不当材料实存、交易付款、任务或指南针原生回执。',
'root/tag/townsset及三个vanilla支持JSON完整证据复用，新全文JSON0；固定本地来源不证明远端最新真实性。两个DataVersion兼容/升级与生成、可选群系注册、道路/地形接合未验。',
'本批新案例最多1待独立验收，正式增量0；221已first224本批及未来0，157first206/203first209不重复。保留224原七维八限与pending，COD4保持153/847，NPC累计未知，不达到1000不制作。',
'不运行Java/游戏/联网，不碰实例/存档/共享Jar/声音亮度/焦点，不写生产资产/主清单/Git，不删未验提示词；研究不是建筑完成，无全部完成/工时声明。']
put('manual-review.json',dict(batch=225,case='F01_HOST_PLUS_REUSED224F04',seven_dimensions=seven,limits=limits,new_reference_proposal=1,formal_credit_added=0,status='ONE_COMPLETE_COLD_WORK_DWELLING_LIBRARY_MAX1_PENDING',native_acceptance=False,actual_reading=dict(new_palette=70,new_BE=13,new_entities=0,new_layers=9,new_RLE_rows=99,new_source_positions=1485,new_final_PNG_viewed=8,new_full_JSON=0,reused_child_palette=5,reused_child_BE=2,reused_child_RLE=6,old_PNG_reopened=0)))
put('key-source-derived-route-cells.json',dict(cells=[b for b in allcells if (9<=b['pos'][0]<=12 and 4<=b['pos'][2]<=9 and b['pos'][1]<=3)or(5<=b['pos'][0]<=8 and 1<=b['pos'][2]<=5 and b['pos'][1]<=6)or(b['pos'][2]>=9 and 6<=b['pos'][0]<=9)],static_not_native_or_collision=True))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
    # Compact binding preserves history, without recursively duplicating megabytes.
    d=dict(previous224_binding=bind(PRE/name),older_history_retained=True,accepted221_first224_current225_increment=0,accepted203_first209_current225_increment=0,accepted157_first206_current225_increment=0,current_batch_formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
    if name.startswith('carried'):
        d.update(current_batch_new_pending=1,prior_active_pending=['224F01_HOST_PLUS_F04_TOOLSMITH'],current_batch_pending_cases=[dict(case='225F01_HOST_PLUS_REUSED224F04',NPC='NPC01',maximum_independent_credit=1,formal_credit_added=0,status='PENDING_MAIN_INDEPENDENT_WHOLE_RELEVANCE_AND_SEMANTIC_DEDUP')],not_master_todo_backup=True)
    put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
    old=f['current224'];now=bind(old['path']);protected.append(dict(last224_checkpoint=old,current225=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True))
ck('eight protected inputs unchanged',len(protected)==8 and all(f['unchanged']for f in protected))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=225,status='NEW_IBERIAN_HOUSE6_TOOL_WORK_DWELLING_LIBRARY_MAX1_PENDING',formal_credit_added=0,accepted221_first224_current_increment=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=1,active_pending=['224F01_HOST_PLUS_F04_TOOLSMITH','225F01_HOST_PLUS_REUSED224F04'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not f['unchanged']for f in protected),next='Main independent224 and225 relevance/dedup; continue different complete whole, not same-host profession variants.221 first224 later increment0.')
put('session.json',s);put('active-checkpoint.json',s)
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json']
put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected_unchanged=sum(f['unchanged']for f in protected)),ensure_ascii=False))
