import json, hashlib, math
from pathlib import Path
P=Path(__file__).resolve().parent; R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
a=get(P/'raw-source-audit.json')['candidates'][0]; d=a['nbt_decoded_original'];pa=d['palette'];bs=d['blocks'];cells={tuple(b['pos']):b for b in bs}
dims={
 'layout':'一座西低门厅接东高主屋的完整雪屋。下floor0/use1西入门厅、栅栏开口分隔后餐桌双座、东北低箱及东回转内阶；上floor4 top半砖/use5西侧并排两west蓝床、南north空炉、北高east箱。双高度屋盖连成一栋，不将门厅/两层/两床/烟柱分栋。与251下双床上炉长廊的分配不同，但公共低层/上卧铺也有245近族风险。',
 'proportion':'16×15×9/DV3337，61palette/11BE/entities[]。2160声明格894保存=753nonair141显式air，1266省略unknown；15层135RLE2160格全部读，7PNG实际看。floor0与floor4 top半砖两使用标高，局部上箱floor5/use6，不构成第三经营层。y12/13仅石柱、y14营火/活板，不是15楼；床4块合2床。',
 'facade':'53spruce log、64去皮spruce log、4去皮spruce wood多轴构框，135spruce板/19darkoak板为墙盖、3glasspane位于底南北及上东端。西x2,z4闭门朝west，门前1,0,4path上1/2/3air；外0,1,4west_up接头最终structure_void，上2/3却省略，不能当连续已验道路。13fence在分隔/桌脚、4悬灯、1amethyst cluster与盆spruce苗是陈设，图中cube不是薄件/原纹理。',
 'roof':'西门厅低脊与东主屋高脊同沿x方向而在x6/7附近层级交叠，74darkoak阶、36spruce阶、13top半砖与darkoak板形成檐坡/木构，120snow_block为实整块积雪，另105snow为layers1..7不同薄层，不能混记同厚。主屋y10脊雪、y11雪/端活板，南11,y6..13,6八stone_bricks柱从上炉延到y14 lit campfire，顶有三open活板。只证静态形态，不证真实排烟/防雨/积雪承载；屋顶火不可达室内烤火位。',
 'materials':'下餐桌8,1,4west底阶与10,1,4east底阶两座，9,1,4fence上9,2,4spruce_pressure_plate作桌面；本栋emptyprocessor，不迁251石压力板mossify标记规则。下箱12,1,2west snowy_house seed6618614683274208229；上箱8,6,3east同表seed7394806729930866618。床8,5,4/5head、9,5,4/5foot朝west。11,5,6north炉原Items[]/litfalse/计时0；屋顶11,14,6littrue营火也Items[]/四CookingTimes/TotalTimes均0，不是烹饪/库存回执。',
 'circulation':'西门内3,1/2/3,4air到栅栏中央7,1/2/3,4air，但继续8,1,4座阶/9,1,4fence和上压力板不是air。东内梯12,1,5north底阶→12,2,4north底阶→12,2,3木平台，再转west11,3,3→10,4,3底阶，每阶自上2格原air。南侧10,4,4top半砖上5/6air，接11,4,5top半砖上5/6air至炉north前；阶侧转身/半砖碰撞未验。床脚占9,5,z4/5，不称西行全air。下箱west前11,1/2,2是openwest活板且箱上top阶；高箱前9,6,3air但9,7,3topnorth阶，操作/净空不能过度推断。',
 'ground_support':'floor0原木地/泥/雪草边缘贴地，下面世界及边界外unknown不补air，不称雪坡承载/地形嵌合通过。两个up_west村民接头8,0,z3/5最终spruce板，非两已生NPC。houses24项本栋weight6/single_pool/rigid/empty；root minecraft:jigsaw size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，biome只引用vanilla snowy tag未读tag体。startpool三自有/三vanilla僵尸中心配置不是6例；中心NBT/道路/terminator未读未拼。原vanilla snowy村民池与snowy_house loot固定Jar缺失。'
}
limits=[
 '最多提出1完整NPC13巴图雪山木屋居住/雨避辅助参考，正式0，待Main独立近族/相关性判定可HOLD0；原雪村双层住宅不是巴图建筑已制作，也没有夜烤火/猎获/递酒/中文任务/指南针或原生获取验收。',
 '61palette所有Properties/11完整BE/entities[]与15层135RLE2160格、7PNG实际读看；1266省略unknown不补air，753nonair含雪/薄件/接口不等实心承重格。两床/两层/两个箱/7图/源文件不拆参考。',
 'F01snowytaiga小屋2和F03Trekmedium2仅机器指纹/材料BE预筛0；临时分类图未查看即移除，不冒称三栋整读。本批只有F02完成完整空间研究；机器指纹不同不证明全历史语义独特。',
 'houses/root/startpool三完整JSON及3metadata全文可用，均与252 F03已全文记录精确复用并本轮读了保存正文，复用信用0；没有凭引用把其它池项/centerNBT/道路/biometag体/缺失vanilla表说成已读或生成通过。',
 '各内阶自身+1/+2原air、12,2,3平台上air、上炉前air仅源格片段。下桌脚/压力板、分隔栏、门、上床/阶、低箱前双活板与高箱上顶阶仍保留真实状态；没有全屋NPC通路、闭门操作、转身、床箱炉使用验收。',
 '下层spruce木压力板是fence桌面原件且此屋processor empty，不能套251的stonepressureplate随机mossify规则。本源120snowblock和105layers1..7雪薄层分开，不把全cube图当真实厚度/雪载/原生mesh/当前纹理。',
 '炉empty/unlit/计时0；顶火虽littrue却在y14柱顶且空物品/计时0，不等可达夜烤火/烤肉。两个lootseed候选表不等现存库存/材料来源/付款/原生NBT变体获得或奖励；村民接口不是确定住民。',
 '完整保存251Main7维9发现10限制和245原7维11限制比较，不重开旧NBT/PNG。251下双床北双门/直升内阶上西炉，与本栋下门厅餐座/高低连盖/回转内阶上床炉有组织差别；245下公共上4床/内转阶也相近，本栋紧凑门厅餐座/两床同室/炉柱不能只凭床数或材质强认不同。Main可判近族0，非全历史穷尽。',
 '253只是251原作者逐项ACK纯数据，提议未来至多一次firstcarry而未执行，251正式仍0/累计null；239first243/243first247/245first248/246first250后续carry全0，239单东入口/243stew literal100非秒/251壁火把与marker限制持续有效。COD4接受153缺847，NPC累计unknown，1000门槛未达不制作不删未验清单。',
 '仅本地Python -B研究/证据写入，没有Java/游戏/网络/UI/进程检查/声音亮度唤醒焦点/用户实例原档/共享Jar/专业生产资产/主清单/Git/自动化操作；不以研究或身份检查宣任务完成、主动工时或全范围完成。'
]
put('manual-review.json',dict(batch=254,case='F02_TREK_SNOWY_MEDIUM_HOUSE1',source=get(P/'sources.json')['candidates'][0],seven_dimensions=dims,limits=limits,status='ONE_COMPLETE_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_MAIN_FORMAL0',complete_original_spatial_study=True,new_reference_proposal_maximum=1,formal_credit_added=0,native_acceptance=False,actual_reading=dict(palette=61,BE=11,entities=0,layers=15,RLE_rows=135,positions=2160,stored=894,nonair=753,air=141,omitted_unknown=1266,PNG_viewed=7,full_JSON_available=3,previous_full_JSON_exact_reused=3,metadata=3,old_NBT_PNG_reopened=0)))
main251=R/'docs/cod4/audit-20261022/coordinator-architecture251-actual-whole-NPC13-review-20261112.json';v=get(main251)
old245=R/'docs/architecture/research-20261104-smithy-245/manual-review.json';v245=get(old245)
put('saved-complete-family-comparison.json',dict(current_judgment=limits[7],comparison251=dict(binding=bind(main251),seven_dimensions=v['Main_seven_dimensions'],findings=v['Main_findings'],limits=v['Main_limits']),comparison245=dict(binding=bind(old245),seven_dimensions=v245['seven_dimensions'],limits=v245['limits'],historical_pending_superseded='245 firstcarry248 acceptedNPC12 auxiliary only; no carry here'),old_NBT_PNG_reopened=False,credit=0))
prev=R/'docs/architecture/research-20261104-smithy-253';s=get(prev/'session.json');s.update(batch=254,status='ONE_COMPLETE_WHOLE_MAX1_NPC13_AUXILIARY_PENDING_MAIN_FORMAL0',new_complete_whole_studies=1,new_qualifying_proposals_maximum=1,active_pending=s['active_pending']+['254F02_TREK_SNOWY_MEDIUM_HOUSE1_NPC13_AUXILIARY_SPACE'],old251_carry_added=0,first_carry251_executed=False,next='Main review254 originalwhole/full7dims10limits/nearfamily251and245/limitednativecirculation. Continue local complete related architecture, applicable1000 unmet no production.',previous253_receipt=bind(prev/'RECEIPT.json'))
for n in ['session.json','active-checkpoint.json']:put(n,s)
pr=R/'docs/architecture/research-20261104-smithy-252/protected-inputs-current.json';protected=[]
for x in get(pr)['files']:
 last=x['current252'];cur=bind(last['path']);protected.append(dict(last252=last,current254=cur,unchanged=last==cur,concurrent_external_changes_not_reverted=last!=cur))
put('protected-inputs-current.json',dict(files=protected,this_chat_production_writes=False,cod5_missing_not_invented=not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()))
out={};rows=0
for layer in get(P/'F02-full-layer-rle.json')['layers']:
 for row in layer['rows']:
  rows+=1;x=0
  for t,n in row['runs']:
   for xx in range(x,x+n):out[xx,layer['y'],row['z']]=t
   x+=n
  assert x==16
rc=get(P/'F02-key-source-route-cells.json')
def st(p):return pa[cells[p]['state']]if p in cells else 'OMITTED_UNKNOWN'
steps=[(12,1,5),(12,2,4),(11,3,3),(10,4,3)]
checks={
 'exact_135RLE_2160positions':len(out)==2160 and rows==135 and {p:t for p,t in out.items()if t>=0}=={p:b['state']for p,b in cells.items()},
 'stored894_air141_nonair753_unknown1266':len(bs)==len(cells)==894 and a['air']==141 and a['nonair']==753 and sum(t<0 for t in out.values())==1266,
 '61palette_11BE_entities_empty':len(pa)==61 and sum('nbt'in b for b in bs)==11 and d['entities']==[],
 'seven_actual_PNG':len(list(P.glob('*.png')))==7,
 'all_key_route_states_exact':all(x['state']==st(tuple(x['pos']))for x in rc),
 'four_inner_steps_each_two_air':all(st((x,y+h,z))['Name']=='minecraft:air'for x,y,z in steps for h in [1,2]),
 'north_turn_platform_twoair':st((12,2,3))['Name']=='minecraft:spruce_planks'and all(st((12,y,3))['Name']=='minecraft:air'for y in [3,4]),
 'table_woodplate_not_marker':st((9,2,4))['Name']=='minecraft:spruce_pressure_plate'and st((9,1,4))['Name']=='minecraft:spruce_fence',
 'lower_chest_front_not_air':all(st((11,y,2))['Name']=='minecraft:spruce_trapdoor'for y in [1,2]) and st((12,2,2))['Properties']['half']=='top',
 'two_beds_not_four':sum(pa[b['state']]['Name']=='minecraft:blue_bed'for b in bs)==4,
 'empty_cold_furnace_roof_lit_empty_campfire':cells[11,5,6]['nbt']['Items']==[]and st((11,5,6))['Properties']['lit']=='false'and cells[11,14,6]['nbt']['Items']==[]and st((11,14,6))['Properties']['lit']=='true',
 '120snowblock_105snowlayers':a['material_counts']['minecraft:snow_block']==120 and a['material_counts']['minecraft:snow']==105,
 'outside_connector_unknown_not_air':st((0,2,4))==st((0,3,4))=='OMITTED_UNKNOWN'and cells[0,1,4]['nbt']['final_state']=='minecraft:structure_void',
 'complete_seven_dimensions_ten_limits':len(dims)==7 and len(limits)==10,
 'full_JSON3_metadata3':len(get(P/'source-context.json')['candidates'][0]['contexts'])+len(get(P/'bounded-generation-context.json')['candidates'][0]['full_JSON'])==3 and len(get(P/'source-context.json')['metadata'])==3,
 'no_formal_oldcarry_or_production':s['formal_credit_added']==s['old251_carry_added']==0 and not s['production']and not s['masterlists_edited'],
 'eight_protected_current_readable':len(protected)==8
}
assert all(checks.values()), checks
put('verification.json',dict(checks=checks,passed=True,scope='Evidence integrity only; semantic relevance/family/native acceptance pending'))
put('RECEIPT.json',dict(batch=254,status=s['status'],files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],new_complete_whole_studies=1,formal_credit_added=0,old251_carry_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(get(P/'RECEIPT.json')['files']),checks=len(checks)),ensure_ascii=False))
