import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-125');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=get(P/'latest-independent-admissions.json');a['previous_binding']=bind(P/'latest-independent-admissions.json')
f=R/'docs/cod4/audit-20261022/coordinator-smithy125-F02-whole-review-20261109.json';b=bind(f);assert b['sha256']=='37ead5c9af72eb458acb33a5b971e8cae6baf2e046f44c983d611c9e8a3c5b3b'
a['newly_notified_admission_125_F02']=dict(receipt=b,increment=1,first_bound_batch=126,scope='COD3 NPC01 comparable complete civilian workshop spatial reference only',COD4_increment=0,current_batch_source_credit=0,not_total_cumulative=True,sealed125_preserved=True,limits=['partial partition not sealed wall','upper ladder and halfblocks not native tested','south closed top trapdoors not direct ground route','lower target terrain has no confirmed continuous deck','swamp source no exact swamp_vanilla pool match','original correct slab with space retained','not full smithing craft, NPC, Chinese quest, native acquisition acceptance']);put('latest-independent-admissions.json',a)
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[{
'layout':'窄长制箭单体：西侧低门进地面长接待/陈列储物厅，南端围合旋梯沿四个转角逐格上升，在东侧中段出口接北向上层带盖开侧制箭长廊；旋梯再向上继续到较高围栏落脚。提出整个双高差工作组织最多1pending，不拆三个靶/三箱/八步阶为建筑。相对071F01内部同向四阶接床层、087F02外直阶只上半间、115F01内三直阶上工作储层、095/097内直梯上工作/露台、122F01外双宽阶上整层住、123F01内长梯上独立小亭，本例是嵌于窄铺南端的连续绕心阶/侧向退出至整条带盖上工作廊，并继续高落脚；可因近族或民用适用性判0，不以砂色和塔帽保通过。',
'proportion':'6×11×13/DV3953，声明858，648存储=435非air213air，210省略；45palette/entities0。下floor0/use1，上长廊floor4 top birchslab/use5；南旋梯还上到y8阶及部分top slab/围栏落脚，不把未满铺的高落脚写第三完整经营层。11高不是11层；无床/ladder，不称工住卧房。',
'facade':'砂岩sandstone68/cutsandstone71/smoothsandstone96为实下墙与南梯包墙，上廊两侧仅矮cutslab及中段junglefence柱，y6大部外侧air，是开侧长廊非封闭楼上房。唯一jungle门1,1/2,2west/right/closed；Fletcher静态挂牌不作营业AI/中文任务。13sandstonewall与18junglefence不当连续实体围墙碰撞。',
'roof':'长廊平木盖主要birchslab61，柱/墙端托盖；南梯顶y9 junglefence、y10 browncarpet和bottom cutsandstoneslab角帽为围栏收边，不当新完整有顶工室。台阶造型不等屋面，smoothsandstonestairs51包含旋梯与外缘倒阶；不是51房。通用整格图不表达原半块、栏缝、门和净高。',
'materials':'唯一fletchingtable3,5,1在上廊北端；target2/3,1,11位于下梯段后端、另3,7,1在北高位，均power0，不说三处已验有效靶道或三铺。地面2,1,10east单箱seed8158811906000575727，2,3,z6/7east左右双箱seeds-4744711407581134811/-7262726935936475806，双箱不是两独立店。无炉砧/熔岩/床，不称完整锻坊工艺。',
'circulation':'入口0,1,2west empty/finalstructure_void→门1,1/2,2→2/3,y1/2,z2..7显式air，东侧椅/栏/压力板不统写air。南主通路3,1,8air→3,1,9 west底阶→2,1,9 full smoothsandstone角落（上2,2,9air）→2,2,10south底阶→2,2,11整角（上2,3,11air）→3,3,11east底阶→4,3,11整角（上4,4,11air）→4,4,10north底阶→4,4,9整角（上4,5,9air）→4,5/6,8air，以4,4,8cutfloor退出北长廊。上廊x2..4,y4,z1..7 top birchslab、y5/6多air但3,5,1工作台保留。再续3,5,9west→2,6,10south→3,7,11east→4,8,10north底阶，接y8局部top slab与y9围栏；不写全部顶面满铺或已验NPC小旋梯净高/转角/台阶碰撞。',
 'terrain':'单empty入口无村民/补柱socket，整条砂岩底y0，但x0外侧较多省略不作air或接街地坪证明。真实desert root jigsaw size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；精确houses权2/single rigid/empty processor。单Jar缺原版fletcherloot/biometag/zombieprocessor，不推全环境缺失。DV3953当前1.20.1兼容/山脚自然落点/NPC昼夜雨危/任务付款获取/中文指南针未验。'
},{
'layout':'snowy小型制箭工住屋只whole/cut/y0三图有界核查，0；床/工作台/箱集中低位内室，外部土雪/低木坡盖包覆。单小工住室和覆雪外形不足以确认新整体家族，不把雪色或隐藏小内腔作完整新信用，未研究全部内边界或覆土地形接口。',
'proportion':'9×8×11/DV3953，声明792，385存储=357非air28air，407省略。29palette/entities0，不能把407省略填air扩大室内；单bluebed pair foot3/head4,y1,z6east。无梯/高经营层已证，8高不当多层。',
'facade_roof_materials':'strippedsprucelog41/spruceplanks13，sprucestairs48/slab5；snow66为原雪状态，snowblock2不同，不能直接把整格图白块称66个整雪块。一个fletchingtable4,1,4，箱4,2,5west seed6506224587238251748；静态Fletcher挂签非中文任务/居民。无热炉砧熔岩，不称锻造屋。',
'circulation':'0,1,5west empty入口finalair，1,1/2,5west/left/closed spruce门；4,1,5为top closed west sprucetrapdoor，不能概括室内全空。只3图，上部4张未看；门/床旁/半块路径、覆雪与地面衔接和原生获取未验。源snowy root/精确权4 rigid empty processor只是来源上下文。'
}]
comp=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [71,87,95,97,115,122,123]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['_door','stairs','target','bed','fletching','trapdoor'])];root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=[dict(pos=b['pos'],state=pal[b['state']])for b in bs],expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','vertical']+[f'y{y}'for y in range(0,11,2)]if i==0 else['whole','cutaway','y0'],observations=obs[i],written_comparisons=comp,full_study=i==0,credit_proposal_maximum=int(i==0),context_reading=f'真实{ "desert" if i==0 else "snowy"} village root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；精确houses权{2 if i==0 else 4}/single rigid/empty processor。单Jar缺原版loot/biome等不推环境缺失。Trek hotsuop/Hugger/ALDgamer MIT 1-B0.6.1；DV3953不推1.20.1原生兼容。'))
put('review-config.json',dict(batch=126,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='ONE_WHOLE_SPATIAL_PROPOSAL_PENDING_AND_ONE_BOUNDED_HOLD_ZERO',scope='COD3 comparable civilian workshop spatial research only',cases=cases,image_counts=[16,12,4],limits='F01实际9图全看/45palette全读/全部BE和地面至上工作廊y0..7主索引与梯高段y8..10/转角原态实际读；非648格全部逐格语义或原生碰撞。F02仅3图4未看，非29palette全读/完整布局。当前源formal0/F01最多1待独立；125F02 Main接受1首次126绑定，不重复旧120/122信用，不回写125。',next='继续固定本地先去重来源，126F01独立复核前不加信用；适用1000未达不制作。',handoff='126封批：desert_fletcher全部9图/45palette及主上下层矩阵，南端内旋梯接上层开侧有盖制箭长廊候选最多1pending；snowy小工住屋只3图有界0。16图12实际4未看。旋梯四转west/south/east/north和实角台及4,5,8退出上廊原态保留，高落脚不写第三满铺层。125F02 Main37ead5c9af72eb458acb33a5b971e8cae6baf2e046f44c983d611c9e8a3c5b3b接受1首次126精确绑定并解除其pending，旧120first122/122first124carry0；125内隔带不封实/低靶无连续地板/梯顶半块未验/无精确入池/正确slab空格限制及115/111/118纠正保留。无Java/游戏/音亮唤醒/制作/产品或主清单更改，COD4仍153差847。'))
d=raw[0]['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):b for b in d['blocks']};pos={(x,y,z)for y in range(8)for z in range(13)for x in range(1,6)}|{(x,y,z)for y in [8,9,10]for z in range(8,13)for x in range(1,6)}
put('F01-route-source-matrix.json',dict(source_audit=bind(O/'raw-source-audit.json'),positions=[dict(pos=list(p),original_stored=p in mp,state=pal[mp[p]['state']]if p in mp else None,nbt=mp.get(p,{}).get('nbt'))for p in sorted(pos)],no_omitted_as_air=True,native_pathfinding_verified=False))
s=(O.with_name('research-20261104-smithy-120')/'seal_screening.py').read_text().replace("'F02_all_generated_projections_actually_viewed':True","'F01_all_generated_projections_actually_viewed':True").replace("'prior_admissions_current_increment':0","'prior_admissions_current_increment':1")
needle="put('carried-forward-pending.json',carry);bindings(carry)"
replacement="""admission=get('latest-independent-admissions.json')['newly_notified_admission_125_F02']
check('125F02 first accepted binding126',admission['first_bound_batch']==126 and admission['receipt']['sha256']=='37ead5c9af72eb458acb33a5b971e8cae6baf2e046f44c983d611c9e8a3c5b3b' and admission['increment']==1)
accepted=json.loads(Path(admission['receipt']['path']).read_text())
check('125F02 independent COD3 only',accepted['decision']=='ACCEPT_ONE_COMPLETE_RELATED_COD3_CIVILIAN_WORKSHOP_SPATIAL_REFERENCE_ONLY' and accepted['new_related_whole_COD3_reference']==1 and accepted['new_COD4_whole_building_credit']==0)
previouscarry=json.loads((prev/'carried-forward-pending.json').read_text())
old=previouscarry.get('current_batch_pending_cases',[])+previouscarry.get('carried_unresolved_whole_reference_proposals',[])
check('125F02 previous pending exactly one',sum(x['batch']==125 and x['id']=='F02'for x in old)==1)
retained=[x for x in old if not(x['batch']==125 and x['id']=='F02')]
carry['carried_unresolved_whole_reference_proposals']=retained
carry['125F02_resolved_accept1_first126']=admission
put('carried-forward-pending.json',carry);bindings(carry)"""
assert needle in s;s=s.replace(needle,replacement);(O/'seal_screening.py').write_text(s)
print('126 prepared')
