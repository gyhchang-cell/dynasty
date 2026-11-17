import json, hashlib, math
from pathlib import Path
P=Path(__file__).resolve().parent; R=P.parents[2]
assert not (P/'RECEIPT.json').exists(), 'sealed evidence is immutable'
def get(p): return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p); b=p.read_bytes(); return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,v): (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def old(b): return R/f'docs/architecture/research-20261104-smithy-{b}'/'manual-review.json'
raw=get(P/'raw-source-audit.json')['candidates']; sources=get(P/'sources.json')['candidates']
dims=[{
 'layout':'单层约3×3小居室，南门、东壁north黄色单床、西南east箱，西北座阶/顶阶烛台及北空牌，中间短活动带。不是草顶双床长厅；四根蜡烛同一方块，不是四个火塘。',
 'proportion':'7×7×7/DV3105，33palette/6BE/entities[]。343全保存=186nonair157air，0省略；7层49RLE343格及6PNG已读看。floor0/use1；y3低顶活板和y4以上草顶/植被不是二层，y6只有上半高草。床两块合一床，不是两住户。',
 'facade':'spruce框架10多轴log、27spruce板和13顶闭活板构成小室墙檐，门在南z5但朝north，不能误称北入口。草顶与侧木结构按源状态保留；empty墙牌不是中文标牌，类色方块图不表示贴图/薄件碰撞。',
 'roof':'南北端x3木构收尖、东西边逐级草顶，35snowyfalse草块上15草/14高草；室内y3顶闭spruce活板压低天花，y4草覆盖、y5木端及植被、y6上半高草。没有阁楼/楼梯/烟道，不把绿色盖层当已验雪载或防雨。',
 'materials':'床4,1,2head→4,1,3foot朝north；箱2,1,4east原vanilla taiga_house无seed。2,1,2north底jungle阶座，2,1,3west顶jungle阶桌，上2,2,3littrue/candles4；3,1,2east墙牌所有Text为空。无炉/烟炉/营火/锅，灯烛不等供暖。',
 'circulation':'南3,1/2,5闭门；外3,1,6south_up入口jigsaw最终structure_void，下dirt，上y2air/y3悬灯，不称原air/已拼路。内3,z4/3,y1/2air，但y3顶闭活板；床脚南4,1/2,4air、y3顶east阶，北中央3,1,2墙牌不是air。仅静态分段，不证门/薄件/床箱操作或NPC全路线。',
 'ground_support':'floor0木地/泥缘，3,0,3up_south村民口最终darkoak板，不等居民。原17项houses中weight5/legacy_single/rigid/vanilla street_snowy_or_taiga；root size6/max116/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，直tag snowy_taiga+16optional含原未命名空间snowy_coniferious_forest。中心pool一原meetingpoint仅JSON，未读中心NBT/路网/地形；原vanilla村民/loot/processor固定Jar缺失。'
},{
 'layout':'单层3×3石室，西门直入中间横向活动带，西北south空炉及上石墙柱、东北west箱、南east蓝单床，外高悬灯。顶高不构成阁楼；不是251双床两层内梯上炉长屋，也没有241分隔东院。',
 'proportion':'7×9×7/DV3465，21palette/6BE/entities[]。441声明格193保存=163nonair30air，248省略unknown；9层63RLE441格与6PNG读看。floor0/use1，最高实存y7石墙柱，y8全省略，不称九层/顶部air；4床块不存在，两块仅一床。',
 'facade':'63cobble石墙基配80spruce板阶梯屋盖及5cobblewall，西x1,z3闭门朝east，东x5,y2,z3一玻璃薄窗，2/4,4,3高壁火把与0,5,3悬灯。物理西入口不能据facing说东入口；全立方类图不能代替薄窗/火把/灯实际形状。',
 'roof':'全木板沿南北z方向阶梯升高，z0/6处y1/2、z1/5处y3/4、z2/4处y5、z3处y6形成沿x的脊。炉上2,y2/3/4,2cobblewall、y5stone、y6/7cobblewall为烟柱形态；不证明连通烟道/排烟/通风。无压力板，不能把251的55标记迁入本屋。',
 'materials':'2,1,2south炉litfalse/Items[]/BurnTime、CookTime、CookTimeTotal全0/RecipesUsed{}。4,1,2west箱giant_taiga_house loot/seed100296574399564504；3,1,4foot→4,1,4head朝east蓝床。原loot主roll3..8及lucky_pool引用、bonusroll0/bonus_rolls1含banner图案NBT，只是表不是库存/材料付款。lucky_pool未读。',
 'circulation':'西1,1/2,3闭门下cobble，外0,0,3west_up最终east底spruce阶，但0,y1/2/3,3均省略unknown，不能填air。室内x2..4,z3,y1/2/3实air；炉前2,1/2/3,3air，箱前3,1/2,2air，床脚西2,1/2/3,4air。只证原存分段，外坡/闭门/薄件/床炉箱操作与NPC路线未验。',
 'ground_support':'石地0贴地，源下及西外地形未知。3,0,3up_north村民口最终spruce板；houses本栋weight2/legacy_single/rigid/mossify，村民候选nitwit1/baby1/unemployed10不是12居民。自有generic_jigsaw root size6/terrainradius2/range22/biomeradius1/start0/WORLD_SURFACE_WG/beard_thin/boundingboxhack，tag是oldgrowth森林及optional域，不保证雪山。mossify规则虽含压力板置换，本源无该板；center/道路/实现未读未拼。'
},{
 'layout':'覆土积雪包裹的东西向单层小木屋，西侧较高门槛进入后向东下降一级至floor0/use1居住区。东east蓝单床、东北west箱、东南顶阶魂灯台，无独立上层、炉房或隐桶。高入口与低睡卧区整体衔接是观察对象，不拆成两个建筑。',
 'proportion':'10×8×5/DV3337，25palette/5BE/entities[]。400声明格260保存=239nonair21air，140省略unknown；8层40RLE400格及6PNG读看。门floor1/use2，内floor0/use1；y7全省略不是air/第八层。单床两块，不能算两住户。',
 'facade':'44spruce板、27阶、2bottom半砖与91dirt/27草块构成嵌地小室；西3,2/3,2west闭门，朝向与物理入口均西。无玻璃窗；魂灯在7,2,3台上不是窗或火塘。草块同时有snowytrue/false，不能统一改记雪地。',
 'roof':'沿x长向木梁，南北阶檐y3→4收至z2木盖，上y5泥/草覆层、y4..6的40snow块属性layers1..4。是薄雪层而非snow_block；分类全立方白图夸大厚度，不能据图称厚雪承重/保温/防水已验。y7省略不代表开放天空。',
 'materials':'6,1,2foot→7,1,2head east蓝床，7,1,1west箱vanilla snowy_house loot/seed6424712208530489865；7,1,3east顶spruce阶台、上魂灯hangingfalse。无炉/烟炉/营火，不把灯等同夜烤火。村民口5,0,2up_west最终spruce板、外口0,3,2west_up最终structure_void，接口不等已生成居民。',
 'circulation':'外0,2,2west底阶上0,3,2接头而y4省略；x1/2,z2 floor1雪草上y2单层雪，x1,y3/4省略，x2,y3air/y4east顶阶。门3,2/3,2下3,1,2木板；内4,1,2west底阶上y2/3air，5,0,2接头上y1/2/3air。箱前6,1/2,1air/y3north顶阶；东南灯台仍占位。不同高度、雪层及闭门不能抹平成全程净空路径，碰撞/降阶/开箱/NPC未验。',
 'ground_support':'覆土外缘延至y0，并不证明天然雪坡切入、基础承载或融雪排水。houses24项本栋weight1/single_pool/rigid/emptyprocessor（不是legacy）；root minecraft:jigsaw size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，tag引用vanilla village_snowy未读标签体。startpool3自有单pool权98/49/149及3vanilla僵尸legacy权2/1/3，仅配置非六参考。vanilla snowy村民/loot固定Jar缺失，中心NBT/道路未读未拼。'
}]
common_limits=[
 '最多提出本栋1例NPC13巴图大雪山木屋居住/雨避辅助整栋参考，formal0，待Main独立原源/相关性/近族审查可HOLD0；不是建筑制作/NPC入住/夜烤火/中文任务或指南针同步完成。',
 '完整palette全Properties、所有BE/entities及全层RLE和每栋6PNG已读看；nonair含薄件/接口，不等实心承重格。尺寸、换色、床数、屋盖组件/截图和不同文件hash都不自动增加语义信用。',
 '保留显式air与省略unknown的区别；入口finalstate不当已生成块，村民口不当居民。类色cube只帮助空间检查，不是原贴图或原生视觉/碰撞/天气验收。',
 '闭门、阶/半砖/活板、灯、床和箱等源状态保留，静态邻格air不等门操作/转身/薄件碰撞/家具可用或完整NPC路线。',
 '空/未燃炉或灯烛不能完成供暖/烹饪；loot表/seed/候选NBT不能当库存、猎获来源、交易付款、原生获取或奖励回执。',
 '固定Jar元数据/DataVersion/声明兼容性不是当前运行验证或上游最新身份保证。root/tag/pool不是自然地形实例；引用但未读的中心/道路/子表/处理器不编造已解析。',
 '只复用已读旧整栋判断，并保存完整七维与限制供比较，不重开旧NBT/PNG。整栋语义差别待Main；旧239单东入口/243 stew literal100非秒/251落脚壁火把及压力板标记限制持续有效。',
 '239first243、243first247、245first248、246first250仅首次carry各1，本批旧carry全0；246Main闭环收据只读绑定0，不重复接受或累计。',
 'COD4已接受153缺847不变，NPC01/05/06/12/13累计unknown；适用1000真实相关完整建筑门槛未到，不提前生产，也不从外部提示词/镜像/pending/ownership删除未验项。',
 '仅本地Python -B研究与证据落盘；没有Java/游戏/网络/UI/进程检查/声音亮度唤醒焦点/用户实例原档/共享Jar/生产专业资产/主清单/Git/自动化操作；全部任务未完成，主动工时不作声称。'
]
special=[
 '与246同雪针叶草顶家族，材质/烛桌/单室均近；缩尺和少一床不足独立信用。仅提出短方室东床西陈设与246鼓腹长厅/两端缩窄/双垂直床/中央桌的完整组织比较，Main可归同族0。原vanilla村民/loot/streetprocessor缺失。',
 '与241同单床单室炉箱组织，须整体审查，不凭炉换烟炉或换顶加数；与251相同巨杉石木家族但本屋无内梯/上炉层/双床长厅。森林到雪山仅辅助相关。外入口上三格省略不能借内部air延伸；本源没有pressureplate，处理器规则不等实际屋顶。lucky_pool仅引用未读。',
 '与249同小型单床/箱木室，不能凭雪或魂灯换色加数。当前较高外入口→内降阶低室、土雪包覆，与249同层木室/多坡木盖/高隐桶组织不同；只是整栋差异待判。箱前顶阶保留，vanilla snowy loot/村民缺失，外雪层与省略上空不能冒称已走通。'
]
comparisons=[]
mf=R/'docs/cod4/audit-20261022/coordinator-architecture246-actual-whole-NPC13-final-20261112.json'
mv=get(mf)
comparisons.append(dict(candidate='F01',binding=bind(mf),seven_dimensions=mv['Main_seven_dimensions'],findings=mv['Main_findings'],limits=mv['Main_limits'],judgment=special[0],old_NBT_PNG_reopened=False,credit=0))
for cid,b in [('F02',241),('F02',251),('F03',249)]:
 v=get(old(b));comparisons.append(dict(candidate=cid,binding=bind(old(b)),seven_dimensions=v['seven_dimensions'],limits=v['limits'],historical_status_not_current=v['status'],judgment=special[int(cid[-1])-1],old_NBT_PNG_reopened=False,credit=0))
put('saved-complete-family-comparison.json',dict(comparisons=comparisons,current_supersessions='246 accepted first250 only;239 singleeastentry/first243;243 first247/stew literal100 notseconds;245 first248. Older pending/dualentry prose is historical and superseded.',credit=0))
studies=[]
for i,a in enumerate(raw):
 d=a['nbt_decoded_original']; size=d['size']; stored=len(d['blocks']); ext=math.prod(size)
 limits=list(common_limits);limits[6]=special[i]+' '+limits[6]
 studies.append(dict(id=a['id'],source=sources[i],seven_dimensions=dims[i],limits=limits,complete_original_spatial_study=True,new_reference_proposal_maximum=1,formal_credit_added=0,native_acceptance=False,status='COMPLETE_WHOLE_STUDY_MAX1_NPC13_AUXILIARY_PENDING_MAIN_NOT_PRODUCTION',actual_reading=dict(palette=len(d['palette']),BE=sum('nbt'in b for b in d['blocks']),entities=len(d['entities']),layers=size[1],RLE_rows=size[1]*size[2],positions=ext,stored=stored,nonair=a['nonair'],air=a['air'],omitted=ext-stored,PNG_viewed=6)))
put('manual-review.json',dict(batch=252,studies=studies,formal_credit_added=0,new_complete_whole_studies=3,new_reference_proposals_maximum=3,semantic_acceptance_pending=True,context_reading=dict(full_JSON_available=14,new_full_JSON_read=4,previous_full_JSON_exact_reused=10,metadata_available=8,new_metadata_read=3,previous_metadata_exact_reused=5),whole_NBT_PNG_already_read_this_batch=True,old_NBT_PNG_reopened=False))
closure=R/'docs/cod4/audit-20261022/coordinator-architecture246-firstcarry250-actual-closure-20261112.json'
put('246-closure-reuse.json',dict(binding=bind(closure),complete_closure=get(closure),new_credit=0,old_source_reopened=False))
prev=R/'docs/architecture/research-20261104-smithy-251'; ps=get(prev/'session.json')
common={k:ps[k] for k in ['COD4_accepted','COD4_gap','NPC01_total','NPC05_total','NPC06_total','NPC12_total','NPC13_total']}
common.update(batch=252,status='THREE_COMPLETE_WHOLE_STUDIES_PENDING_MAIN_FORMAL0',formal_credit_added=0,new_whole_formal_credit_added=0,new_complete_whole_studies=3,new_qualifying_proposals_maximum=3,old239_carry_added=0,old243_carry_added=0,old245_carry_added=0,old246_carry_added=0,active_pending=ps['active_pending']+['252'+a['id']+'_NPC13_AUXILIARY_SPACE'for a in raw],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,not_master_todo_backup=True,next='Main independently review each whole, exactsource/semantic-nearfamily/relevance; at most1perwhole, F01strongsamefamily risk. Continue fixedlocal relevant completehouse studies; no production before applicable1000 accepted.')
for n in ['session.json','active-checkpoint.json']:put(n,{**common,'previous251_binding':bind(prev/n)})
protected=[]
for x in get(prev/'protected-inputs-current.json')['files']:
 last=x['current251'];cur=bind(last['path']);protected.append(dict(last251_checkpoint=last,current252=cur,unchanged=last==cur,external_concurrency_not_reverted=last!=cur))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,cod5_missing_not_invented=not Path('/Users/a15356015027/Desktop/code x提示词/cod5.txt').exists()))
checks={}
for a,study in zip(raw,studies):
 cid=a['id'];d=a['nbt_decoded_original'];sx,sy,sz=d['size'];cells={tuple(b['pos']):b['state']for b in d['blocks']};out={};rows=0
 for layer in get(P/f'{cid}-full-layer-rle.json')['layers']:
  for row in layer['rows']:
   rows+=1;x=0
   for state,count in row['runs']:
    for xx in range(x,x+count):out[xx,layer['y'],row['z']]=state
    x+=count
   assert x==sx
 checks[cid+'_exact_full_RLE_roundtrip']={p:t for p,t in out.items()if t>=0}==cells and len(out)==sx*sy*sz and rows==sy*sz
 checks[cid+'_stored_nonair_air_unknown']=len(cells)==len(d['blocks'])==a['air']+a['nonair'] and sum(t<0 for t in out.values())==sx*sy*sz-len(cells)
 checks[cid+'_complete_palette_BE_entities_dimensions']=len(study['seven_dimensions'])==7 and len(study['limits'])==10 and d['entities']==[] and all(0<=s<len(d['palette'])for s in cells.values())
 checks[cid+'_six_PNG_and_routecells_bound']=len(list(P.glob(cid+'-*.png')))==6 and all(c['state']==(d['palette'][cells[tuple(c['pos'])]]if tuple(c['pos'])in cells else 'OMITTED_UNKNOWN')for c in get(P/f'{cid}-key-source-route-cells.json'))
def state(i,p):
 d=raw[i]['nbt_decoded_original'];b=next((b for b in d['blocks']if b['pos']==list(p)),None);return d['palette'][b['state']]if b else {'Name':'OMITTED_UNKNOWN'}
checks['F02_external_unknown_not_air']=all(state(1,(0,y,3))['Name']=='OMITTED_UNKNOWN'for y in [1,2,3])
checks['F02_empty_unlit_furnace_no_pressureplates']=state(1,(2,1,2))['Properties']['lit']=='false' and next(b['nbt']for b in raw[1]['nbt_decoded_original']['blocks']if b['pos']==[2,1,2])['Items']==[] and not any(p['Name']=='minecraft:stone_pressure_plate'for p in raw[1]['nbt_decoded_original']['palette'])
checks['F03_snowlayers_not_snowblock']=state(2,(1,2,2))['Properties']['layers']=='1'and not any(p['Name']=='minecraft:snow_block'for p in raw[2]['nbt_decoded_original']['palette'])
checks['F03_entry_levelchange_and_unknown']=state(2,(3,2,2))['Name']=='minecraft:spruce_door'and state(2,(4,1,2))['Properties']['facing']=='west'and all(state(2,(5,y,2))['Name']=='minecraft:air'for y in [1,2,3])and state(2,(1,3,2))['Name']=='OMITTED_UNKNOWN'
checks['14contextJSON_8metadata']=sum(len(x['contexts'])for x in get(P/'source-context.json')['candidates'])+sum(len(x['full_JSON'])for x in get(P/'bounded-generation-context.json')['candidates'])==14 and len(get(P/'source-context.json')['metadata'])==8
checks['newformal_and_oldcarry_all0']=all(common[k]==0 for k in ['formal_credit_added','old239_carry_added','old243_carry_added','old245_carry_added','old246_carry_added'])
checks['protected_current_readable_eight']=len(protected)==8
assert all(checks.values()),checks
put('verification.json',dict(checks=checks,passed=True,scope='Evidence integrity only; no independent semantic/native acceptance'))
put('RECEIPT.json',dict(batch=252,status=common['status'],files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'],formal_credit_added=0,new_reference_proposals_maximum=3,old_credit_added=0,production=False,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(get(P/'RECEIPT.json')['files']),checks=len(checks)),ensure_ascii=False))
