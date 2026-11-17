import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=get(P/'raw-source-audit.json')['candidates'][0];d=a['nbt_decoded_original'];pa=d['palette'];bs=d['blocks'];cells={tuple(b['pos']):b for b in bs}
dims={
 'layout':'完整单脊木屋，下floor0/use1东侧一east白床、南north空炉、东侧抬高west箱，西侧两组座阶/栅栏桌面。内中部先south两阶、平台转east再两阶到东侧局部floor4 top半砖/use5夹层，夹层一west白床/北east箱；西侧不铺满楼板，另西壁高箱悬在活板托架上。不是两栋或完整双层客栈，不以床/高箱/烟柱拆数。',
 'proportion':'13×11×11/DV3337，64palette/12BE/entities[]；1573声明格811保存=661nonair150air，762省略unknown。11层121RLE1573格及7PNG全读看；floor0和局部floor4为实际使用标高。高箱3,4,4不是另一个有可达地面的房间，y8梁/9脊/10半砖与顶火不是11楼；4床块为2床。',
 'facade':'160spruce板、47spruce log与34多轴去皮spruce log构成木架和棋盘式木地，2玻璃薄窗、4灯、木阶/栏桌、活板及盆苗陈设。西2,1/2,5west/left闭门上y3topeast阶；外0,1,5入口接头与x1门前上空省略不能填air。东外4rail为两组ascending_west+east_west，邻log/底半砖但没有实体矿车/连通运输系统，不称NPC楼梯或运输线路。',
 'roof':'沿x同一连续主脊，南北坡由114spruce阶与67stonebrick阶、15stonebrick底半砖及stonebrick端缘逐级向z5收束；y8,z5为13横向log，y9,z5为11stonebrick及两端顶阶，y10,z5为13底stonebrick半砖封脊。13snowblock主要源底边、23snow均layers1，不把整片灰石檐脊称厚积雪，也不迁254的120雪块。南7,y2..9,8石砖柱上7,10,8lit营火、四open顶活板围帽；静态柱形不证排烟/火安全/防雨雪载。',
 'materials':'下床8,1,4foot→9,1,4head朝east，上床7,5,5head←8,5,5foot朝west。三箱原snowy_house表及各seed原样：9,2,5west/8361296571511337912；3,4,4east/-8995401223595532166；7,5,4east/-7566240294920873227。7,1,8north炉litfalse/Items[]/三计时0/RecipesUsed{}，顶营火littrue却Items[]/四CookingTimes和TotalTimes0。两木压力板4,2,z3/7在fence桌脚上；emptyprocessor不迁251石标记规则。loot/村民候选不是付款/库存回执。',
 'circulation':'西外0,1,5jigsaw finalstructure_void，0,y2/3,5及1,y1/2/3,5全省略；内3,1/2,5air而y3顶闭活板，5,1/2/3,5air。四底阶6,1,4south→6,2,5south→6,2,6木平台→7,3,6east→8,4,6east，每阶上+1/+2原air；9,4,6top半砖上5/6air但7顶south阶。北转9,4,5top半砖上5/6/7air为床东侧，8,5,5已床脚。上箱前8,5/6,4air/y7顶阶；下抬高箱前8,2/3,5air/y4top半砖。西高箱3,4,4下3,3,4顶闭活板，东4,3/4/5,4air而无该高度地板或梯，不称高箱取用已验。夹层西缘6,5,z4/5open竖活板不当整面护栏；所有段仅源格拓扑。',
 'ground_support':'floor0去皮木地与泥/雪草外边保留，源下与世界外unknown，未证高山雪坡嵌合或承载。5,0,z4/6两个up_west村民口最终stripped_spruce_log[axis=x]，不是spruce板/已入住两NPC。houses24项本栋weight6/single_pool/rigid/emptyprocessor；root size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue只引用vanilla snowy tag。towncenter三自有/三vanilla僵尸池仅配置，centerNBT/路网/终止件/biome体未读未拼；vanilla snowy villagers和snowy_house loot固定Jar缺失。'
}
limits=[
 '至多提出1完整NPC13巴图大雪山木屋的居住/雨避辅助整屋参考，正式新增0，待Main独立相关性/近族审查可HOLD0；没有生产/NPC入住/夜烤火/任务中文/指南针/材料获取或奖励回执。',
 '64palette完整Properties/12BE/entities[]、11层121RLE1573格和7PNG实际读看；762省略未知不补air，661nonair含薄件/接口不等实心承重格。夹层、两床、3箱、两桌/轨道/截图不拆建筑信用。',
 '本例254曾仅机器指纹和材料BE预筛0，本256才完整逐层/视觉研究；机器hash不同、文件名medium2、床色/屋盖石料不同不证明独立完整设计。254旧预筛状态不当已接受/本批重复信用。',
 'houses/root/startpool三完整JSON与3metadata精确复用254已全文读对象，复用绑定和当前同Jar回源保留；原缺vanilla池/loot、引用中心NBT/道路/biome体不编造完成。pack格式和兼容区间不是当前实例加载/运行证明。',
 '外入口省略/structure_void、闭门/顶阶/活板/床箱/栏桌均保留，四阶各上2air和平台/落点只支持分段源格；转向碰撞、阶侧跨入半砖、床/箱/炉操作和整屋NPC寻路未验。夹层竖活板不当完整防坠护栏。',
 '西壁高箱托于3,3,4闭顶活板，前方该高度无地板/梯，仅空气，不声称站位可达或绝对不可操作；下箱抬高一格/上箱顶前薄阶各自保留。外两对rail只是源state，无车/完整轨路/用途证明，不拿它们当可走楼梯或物流回执。',
 '两wood pressureplate为fence桌面，emptyprocessor不能套251stoneplate mossify；13snowblock与23layers1snow和大片stonebrick阶脊分别记录。分类cube不还原薄件厚度/贴图/雪载/天气，源灰屋盖不冒充厚雪。',
 '炉原空未燃、顶火虽lit但高柱顶/空物品计时0，不等实际烤火/炊事。三箱lootseed不是现存物品/材料付款，2村民口不是已生成居民；不用普通物品替换NBT变体或抄作者资产进入产品。',
 '完整保存254原7维10限制与251Main7维9发现10限制，旧源图不重开。254低门厅餐座/上双床炉同层/双高度盖，与本栋下床炉/局部夹层另一床箱/西挑空高箱的完整组织不同；251下双床上炉长廊也不同。仍同Trek雪屋/内转阶家族，少床、换材、加高箱本身0信用，非全历史穷尽，Main可归近族0。251/252F03作者ACK不等最终接受/首次carry，当前均0；已接受239/243/245/246后续carry0。',
 'COD4接受153缺847不变，NPC累计unknown，适用1000未达不制作不删未验提示词。仅本地Python -B研究/证据写入；无Java/游戏/网络/UI/进程/音亮唤醒焦点/实例原档/共享Jar/生产专业资产/主清单/Git/自动化修改，不宣全部完成或主动工时。'
]
put('manual-review.json',dict(batch=256,case='F01_TREK_SNOWY_MEDIUM_HOUSE2',source=get(P/'sources.json')['candidates'][0],seven_dimensions=dims,limits=limits,status='ONE_COMPLETE_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_MAIN_FORMAL0',complete_original_spatial_study=True,new_reference_proposal_maximum=1,formal_credit_added=0,native_acceptance=False,actual_reading=dict(palette=64,BE=12,entities=0,layers=11,RLE_rows=121,positions=1573,stored=811,nonair=661,air=150,omitted_unknown=762,PNG_viewed=7,route_cells=123,full_JSON_available=3,previous_full_JSON_reused=3,metadata=3,old_NBT_PNG_reopened=0)))
p254=R/'docs/architecture/research-20261104-smithy-254/manual-review.json';v=get(p254);p251=R/'docs/cod4/audit-20261022/coordinator-architecture251-actual-whole-NPC13-review-20261112.json';w=get(p251)
put('saved-complete-family-comparison.json',dict(comparison254=dict(binding=bind(p254),seven_dimensions=v['seven_dimensions'],limits=v['limits']),comparison251=dict(binding=bind(p251),seven_dimensions=w['Main_seven_dimensions'],findings=w['Main_findings'],limits=w['Main_limits']),judgment=limits[8],old_NBT_PNG_reopened=False,semantic_credit=0))
prev=R/'docs/architecture/research-20261104-smithy-255';s=get(prev/'session.json');s.update(batch=256,status='ONE_COMPLETE_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_MAIN_FORMAL0',new_complete_whole_studies=1,new_qualifying_proposals_maximum=1,active_pending=s['active_pending']+['256F01_TREK_SNOWY_MEDIUM_HOUSE2_NPC13_AUXILIARY_SPACE'],next='Main independently review256 whole/source/family254and251; continue local relevantcompletebuilding research, no production before applicable1000.',previous255_receipt=bind(prev/'RECEIPT.json'))
for n in ['session.json','active-checkpoint.json']:put(n,s)
protected=[]
for x in get(R/'docs/architecture/research-20261104-smithy-254/protected-inputs-current.json')['files']:
 last=x['current254'];cur=bind(last['path']);protected.append(dict(last254=last,current256=cur,unchanged=last==cur,external_changes_not_reverted=last!=cur))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,cod5_missing_not_invented=not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()))
out={};rows=0
for layer in get(P/'F01-full-layer-rle.json')['layers']:
 for row in layer['rows']:
  rows+=1;x=0
  for t,n in row['runs']:
   for xx in range(x,x+n):out[xx,layer['y'],row['z']]=t
   x+=n
  assert x==13
def st(p):return pa[cells[p]['state']]if p in cells else 'OMITTED_UNKNOWN'
route=get(P/'key-source-route-cells.json');steps=[(6,1,4),(6,2,5),(7,3,6),(8,4,6)]
checks={
 'exact121RLE1573positions':len(out)==1573 and rows==121 and {p:t for p,t in out.items()if t>=0}=={p:b['state']for p,b in cells.items()},
 '811stored150air661nonair762unknown':len(bs)==len(cells)==811 and a['air']==150 and a['nonair']==661 and sum(t<0 for t in out.values())==762,
 '64palette12BE_entities0':len(pa)==64 and sum('nbt'in b for b in bs)==12 and d['entities']==[],
 'sevenPNG':len(list(P.glob('*.png')))==7,
 'all123routecells_exact':len(route)==123 and all(c['state']==st(tuple(c['pos']))for c in route),
 'foursteps_each_twoair':all(st((x,y+h,z))['Name']=='minecraft:air'for x,y,z in steps for h in [1,2]),
 'turnplatform2andupperlanding4':st((6,2,6))['Name']=='minecraft:spruce_planks'and all(st((6,y,6))['Name']=='minecraft:air'for y in [3,4])and st((9,4,6))['Properties']['type']=='top'and all(st((9,y,6))['Name']=='minecraft:air'for y in [5,6]),
 'outer_unknown_notair':all(st((1,y,5))=='OMITTED_UNKNOWN'for y in [1,2,3])and cells[0,1,5]['nbt']['final_state']=='minecraft:structure_void',
 'westhighbox_nofrontfloor':st((3,4,4))['Name']=='minecraft:chest'and st((3,3,4))['Properties']['half']=='top'and all(st((4,y,4))['Name']=='minecraft:air'for y in [3,4,5]),
 'local_loft_notfullfloor':st((7,4,5))['Name']=='minecraft:spruce_slab'and st((4,4,5))['Name']=='minecraft:air',
 'two_whole_beds_three_chests_fourrails':a['material_counts']['minecraft:white_bed']==4 and a['material_counts']['minecraft:chest']==3 and a['material_counts']['minecraft:rail']==4,
 'woodtables_not_stonemarkers':a['material_counts']['minecraft:spruce_pressure_plate']==2 and all(st((4,2,z))['Name']=='minecraft:spruce_pressure_plate'and st((4,1,z))['Name']=='minecraft:spruce_fence'for z in [3,7]),
 'snow13full23thin':a['material_counts']['minecraft:snow_block']==13 and a['material_counts']['minecraft:snow']==23,
 'empty_cold_furnace_roof_lit_emptyfire':cells[7,1,8]['nbt']['Items']==[]and st((7,1,8))['Properties']['lit']=='false'and cells[7,10,8]['nbt']['Items']==[]and st((7,10,8))['Properties']['lit']=='true',
 'full3JSON3metadata':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['candidates'][0]['full_JSON'])==3 and len(get(P/'source-context.json')['metadata'])==3,
 'seven_dimensions_tenlimits':len(dims)==7 and len(limits)==10,
 'eight_protected_readable':len(protected)==8,
 'zero_formal_carry_production':s['formal_credit_added']==s['old251_carry_added']==s['old252F03_carry_added']==0 and not s['production']and not s['masterlists_edited']
}
assert all(checks.values()),checks
put('verification.json',dict(checks=checks,passed=True,scope='Evidence integrity only not Mainsemantic/native acceptance'))
put('RECEIPT.json',dict(batch=256,status=s['status'],files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],formal_credit_added=0,old_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(get(P/'RECEIPT.json')['files']),checks=len(checks)),ensure_ascii=False))
