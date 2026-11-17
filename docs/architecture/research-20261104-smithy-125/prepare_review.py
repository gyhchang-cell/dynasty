import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-124');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=get(P/'latest-independent-admissions.json');a['previous_binding']=bind(P/'latest-independent-admissions.json');a['122F01_first_bound124_carry_only_no_current_increment']=True;put('latest-independent-admissions.json',a)
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[{
'layout':'cherry小型制箭望楼，只whole/cut/y0三图有界研究0；地面小制箭位接中央长梯，上方为木构栅栏望楼形体。未完成上部楼板/落脚/使用关系研究，不能因19高、牌名Watchtower、职业或多重檐增加完整参考，也不据名称断言军事要塞。',
'proportion':'9×19×9/DV3953，声明1539，804存储=657非air147air，735省略；96palette/entities0。无床；4,1..9,4为9个west梯状态，不算9层。5,1,5唯一fletchingtable，5,1,3与3,4,3原箱，高箱不证明上层完整经营空间。只3图，10未看。',
'facade_roof_materials':'cherrylog92/stonebrick85/calcite52/strippedspruce32，deepslate砖/瓦半砖形成尖顶宽檐；白8红4墙旗和49sprucefence构架不计多栋。两fletcher箱5,1,3west seed-8818370840658505179与3,4,3east seed-4521725164380376964，Fletcher\'s Watchtower静态牌不证明中文任务/AI。无炉砧热源或床，不称完整锻坊工住。',
'circulation':'0,1,4west入口empty/finalstructure_void，2,1/2,4west/right/closed spruce门进小地面区，4,y1..9,z4west ladder原态保留；未看顶部落脚与外围栏路，不说梯口已通、NPC会爬梯或9层可用。cherry root精确权1/single rigid empty processor及optional cherry_grove只是来源语境，不作当前1.20.1运行结论。'
},{
'layout':'同一架高制箭工住单体：外西四底阶北升接西带盖长入户平台→西门进入西接待/陈列区，内侧带门隔带接东制箭/双床生活区；东内梯上独立高位带盖栅栏工作亭，南较低地段设靶位。提出整组流线最多1待独立判断，不拆双靶/双床/三台/十五socket/高亭。相对120F02外阶接单层连续L工住及凹湿场、122F01北外阶上整层床室、123F01地面长厅/内梯上开放高亭/同高东靶院，本例是架高横向两使用区/门隔带/室内梯上小工作亭，靶区在更低地段且独立于主平台；与095F02内梯多间工住家族仍有交集，可因同族或适用性判0，不以高度/沼泽藤色保证新信用。',
'proportion':'17×25×17/DV3953，声明7225，1757存储=1249非air508air，5468省略不当air；112palette/entities0。主层floor4/use5，高工作亭floor13 bottom slab/use14，尖顶最高24；y10双箱处于梯旁屋盖，不额外称第三完整生活层。低靶区地表只稀疏coarse/dirt，缺省不补地板；25高不是25层。',
'facade':'oaklog171/strippedoak28、oakplanks78/spruceplanks59/darkoakplanks74；58mudbrickwall与8glasspane围东区，西oak围护配门。西门4,5/6,3west/right/closed、南门6,5/6,9north/right/closed、内门8,5/6,7west/left/closed。内x8北段底top stairs而上局部air/栅栏，不能把隔带写完全封实隔墙或说内门是两区唯一可能通过位置；实际通行未验。10挂签9空、1写Fletcher\'s Watchtower是静态原文，不作中文营业/任务。',
'roof':'主层低宽混木slab/stair盖上接东北小高亭尖顶；spruceslab144/stairs83、darkoakstairs32/slab24为屋盖与平台混用，不称全石瓦。高亭floor13 x10..12,z4..6为bottom spruce slab，梯口12,13,5air；y14/15框架/栅栏及open air围护，不称密闭卧室。顶24oak柱/屋面空腔不计额外使用层。全格分类图不表示半砖、藤蔓、门、材料真实几何与阴影。',
'materials':'三个fletchingtable9,5,z3/4与9,14,7，两个target13,2,z11/13 power0；4lightbluebed状态是两proper pairs foot12/head13,y5,z7/8east。五箱含10,10,z4/5east左右双箱（原seed6112575477629656960与3863523198405916076）、5,1,10south seed-632849259994682359、10,5,2south seed-3570619622845313301、11,14,7north seed-7870615483723318920，箱/家具不拆信用。无炉砧熔岩；三candles状态是单个candle block candles3且unlit，不说3个热源。',
'circulation':'外阶2,1,13→2,2,12→2,3,11→2,4,10均bottom oakstairs/north，2,4,9及2/3,4,3为top oakslab，2,y5/6,z9与2/3,y5/6,z3air接西门4,5/6,3→5..7,y5/6,z3air。主内东向通道按8,5/6,7内门→9/10,y5/6,z7air进入东区；床前x11,y5,z7/8为bottom spruce slab不能写air。12,y5..12,z5west ladder，x11,z5在y5..8air、y9spruceplanks、y10..12air；y13x11 bottom slab、x12air、x13oaklog，梯顶过渡/半块净高未验。南门外z10/11,y4大片是top closed spruce trapdoor和倒阶，不写连续air或直接地面通路。低靶区x5..14,z10..14,y0大量省略/零散土，绝不写已有连续甲板；靶架13,2,z11/13不是门或第三座房。',
 'terrain':'15jigsaw=11向下oak-column socket+2villager+2入口，不计15建筑/已生居民。柱池仅此Jar缺失，原finalstructure_void保留；两个villager final原写minecraft:cobblestone_slab[type=top, waterlogged=false]，本源slab拼写正确且含空格，不能套120原slap错字。villager候选nitwit1/baby1/unemployed10非已生2人。原NBT在swamp而真实存在root/houses为swamp_vanilla，精确selected为空；不借邻名权重推本源自然入池，保存street/house_swamp_vanilla处理只上下文。架高承托和低靶区依地形/补柱，现未验；不证明山脚位置、NPC昼夜雨危、付款原生获取、任务或中文指南针。'
}]
comp=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [61,95,97,120,122,123]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['_door','ladder','bed','stairs','target','fletching'])];root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=[dict(pos=b['pos'],state=pal[b['state']])for b in bs],expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','y0']if i==0 else['whole','cutaway','vertical']+[f'y{y}'for y in range(0,25,2)],observations=obs[i],written_comparisons=comp,full_study=i==1,credit_proposal_maximum=int(i==1),context_reading=('cherry root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，精确houses权1/single rigid empty processor，optional cherry_grove。'if i==0 else'swamp_vanilla真实root size6/max80/start0/WORLD_SURFACE_WG/terrainnone/expansiontrue，本swamp NBT与保存houses无精确匹配，不推邻源权重或处理已应用。villager nitwit1/baby1/unemployed10候选，biome tag swamp；street水面土路变darkoak/草或水规则、house dirtpath/dirt遇水darkoak与slab规则均只上下文；缺柱池/原版loot只此Jar。')+'Trek hotsuop/Hugger/ALDgamer MIT 1-B0.6.1；pack10/support10..102及DV3953不证明当前1.20.1兼容/自然生成。'))
put('review-config.json',dict(batch=125,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='ONE_WHOLE_SPATIAL_PROPOSAL_PENDING_AND_ONE_BOUNDED_HOLD_ZERO',scope='COD3 comparable civilian workshop spatial research only',cases=cases,image_counts=[29,19,10],limits='F02实际16图全看/112palette全读/全部BE/主层与低靶地段、梯井和高亭矩阵读；非全部1757格逐格语义阅读或原生图/寻路。F01仅3图10未看，有界0。当前F02整体候选最多1pending/newformal0，120/122接受各自首次122/124，本批全carry0。旧纠正保留；低靶地段省略不当连续甲板。',next='继续固定本地先去重来源；125F02独立审阅前不加有效信用，达到适用1000前不制作。',handoff='125封存：cherry_fletcher只有3图有界0；swamp_fletcher全部16图/112palette/主层梯井高亭及低靶地段矩阵，整体候选最多1pending/formal0。29图19实际10未看。西四阶北上带盖平台→西区→门隔带东工作/双床区→内8梯上小开放工作亭，南较低靶地段大量缺省土位不能写连续地板，南门外高ledge为closed trapdoor。125村民final slab正确有空格，勿套120 slap错字；swamp与swamp_vanilla无精确入池、缺柱池和实机净高/碰撞/地形未验限制保留。120first122/122first124仅carry0，115/111/118纠正carry，COD4仍153差847，无Java/游戏/音亮唤醒/制作/产品/主清单改变。'))
d=raw[1]['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):b for b in d['blocks']};pos=set()
for y in [4,5,6]:
 for z in range(2,10):
  for x in range(4,15):pos.add((x,y,z))
for y in range(5):
 for z in range(9,16):
  for x in range(2,16):pos.add((x,y,z))
for y in range(4,17):
 for x in [11,12,13]:pos.add((x,y,5))
for y in [12,13,14,15]:
 for z in range(3,10):
  for x in range(8,15):pos.add((x,y,z))
for z in [3,9,10]:
 for y in [4,5,6]:
  for x in range(1,5):pos.add((x,y,z))
put('F02-route-source-matrix.json',dict(source_audit=bind(O/'raw-source-audit.json'),positions=[dict(pos=list(p),original_stored=p in mp,state=pal[mp[p]['state']]if p in mp else None,nbt=mp.get(p,{}).get('nbt'))for p in sorted(pos)],no_omitted_as_air=True,native_pathfinding_verified=False))
s=(O.with_name('research-20261104-smithy-120')/'seal_screening.py').read_text()
(O/'seal_screening.py').write_text(s)
print('125 prepared')
