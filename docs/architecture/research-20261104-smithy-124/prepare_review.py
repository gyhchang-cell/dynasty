import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-123');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[{
'layout':'樱花石匠低层工住屋，西门进南工作/储物带，北侧并排两床，z5低木条/开活板及上木板隔带在东x7留无门缺口。只是whole/cut/y0三图及主要地层矩阵的有界核查，0；床区、工区相邻和单低盖组织与116F02石匠工住及060F02相邻匠室近族，樱花瓦色/两床不自行证明新整体家族。不是完全封闭两间或串联双门床室。',
'proportion':'11×10×13/DV3953，声明1430，819存储=658非air161air，611省略；96palette/entities0。floor0/use1，4pinkbed状态=两proper pairs headx3/footx4,y1,z3/4west，不是4床；无梯或上使用层已证，高箱y4不构成阁楼。只3图，不称96palette全读。',
'facade_roof_materials':'cherrylog44/calcite84/oakplanks35，deepslatetile/brick各类台阶半砖形成宽低盖；calcite不标白木板。8红旗与2黑旗为源装饰，3decoratedpot不是3铺；Mason\'s House静态挂牌不证明中文任务。stonecutter6,1,9north，箱7,2,8west seed-526669018178031202及3,4,9north seed-8284532678436069887，非热锻工艺。',
'circulation':'0,1,6 west入口empty/finalstructure_void，门2,1/2,6west/right/closed；x3..7,y1/2,z6/7为原air→x7,y1/2,z5air绕入北床旁。z5x3..6下strippedsprucewood/中open spruce trapdoor/上spruceplanks，不能把整隔带写air或实墙；北x5..7,y1,z3/4为bottom oakslab不是air。半块/床侧通行、门开合和山脚地形均未原生验。cherry root/权4 rigid empty processor与optional cherry_grove只源语境。'
},{
'layout':'针叶林屠宰主屋在西、围栏动物院在东，东门通院/西门接外来路；与122F02 plains butcher主房接东院同族边界明显，木种、烟囱和树socket不作为新完整空间，bounded0。只有whole/cut/y0三图，未看8张上部投影；不把屋顶高箱写已验经营阁楼。',
'proportion':'19×15×15/DV3953，声明4275，1480存储=975非air505air，2795省略；113palette/entities0。门use2，院地面use1，非统一平地净空已验；无床/梯或已证第二经营层，15高不当15层。',
'facade_roof_materials':'sprucelog57/darkoakplanks96、cobble98/cobbleddeepslate33构成木石主房，stonebrickstairs56与darkoakstairs87多层坡面；外campfire1,1,7 east与烟囱7,14,3south均littrue/Items空，不能说屋中无火。两smoker7/8,2,3south/unlit，Cook/Burn0/空Items；三个box块含4,4,z7/8左右双箱与8,2,9单箱，各原seed保留。高箱非上层地板证据。',
'circulation':'西3,2/3,10west/left/closed门和东9,2/3,5east/right/closed门，入口0,1,10 empty finalair；院边10,1,z9..11水level0三格。13,0,5/15,0,8/16,0,10为animal池，final分别dirt/coarsedirt/rooteddirt；15,0,5为spruce树池，不能把全部5jigsaw当5动物/建筑。源树池权1 feature_pool_element minecraft:spruce、fallback自池，不证明已生成树；单Jar缺原版animalpool不推环境缺失。未验NPC/院路水槽/柱栏碰撞，静态Butcher\'s Shop牌非营业AI或中文链。'
}]
comp=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [60,116,122]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['_door','bed','stonecutter','water','smoker'])];root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=[dict(pos=b['pos'],state=pal[b['state']])for b in bs],expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','y0'],observations=obs[i],written_comparisons=comp,full_study=False,credit_proposal_maximum=0,context_reading=('cherry root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，houses精确权4 single rigid empty processor；optional cherry_grove。'if i==0 else'taiga root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，houses精确权2 single rigid/mossify10两.1规则；树池权1 rigid feature minecraft:spruce，fallback自池；tree socket非独立完整建筑。')+'Trek hotsuop/Hugger/ALDgamer MIT 1-B0.6.1，DV3953不推1.20.1可运行；单Jar缺原版资源不推环境缺失。'))
put('review-config.json',dict(batch=124,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='TWO_BOUNDED_STUDIES_HOLD_ZERO',scope='COD3 comparable civilian workshop spatial research only',cases=cases,image_counts=[19,6,13],limits='各实际3图，有界核查不等完整研究或语义新信用；共19图6实际13未看。未全读96/113palette、全部819/1480位置，未验原生模型/碰撞/AI。当前source formal0/pending0；122F01新Main接受1首次124绑定，仅COD3，120接受首次122仅carry0，旧封批不回写。',next='继续固定本地相关完整工坊前置去重，复用已有有效收据，1000门槛未达不制作。',handoff='124封存樱花石匠/针叶林屠宰各3图有界0；19图6实际13未看，无完整新候选。122F01 Main38cdecc15b10e68d2345be1bb4f1654ea1c98a53b3c8ac3fe1a38d365cad0e20接受1首次124精确绑定并解除其pending，保留封存122/123与120first122。北双宽阶east/阶下西端开放/净高门碰撞自然生成完整锻造未验限制保留；115开trapdoor/torch、111四柱y1..3、118DV3465/3105勘误carry。无Java/游戏/音亮唤醒/制作/产品/主清单更改。COD4仍153差847。'))
d=raw[0]['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):b for b in d['blocks']};positions=[(x,y,z)for y in [0,1,2,3]for z in range(2,11)for x in range(2,9)]
put('F01-ground-source-matrix.json',dict(source_audit=bind(O/'raw-source-audit.json'),positions=[dict(pos=list(p),original_stored=p in mp,state=pal[mp[p]['state']]if p in mp else None,nbt=mp.get(p,{}).get('nbt'))for p in positions],no_omitted_as_air=True,native_pathfinding_verified=False))
s=(O.with_name('research-20261104-smithy-122')/'seal_screening.py').read_text().replace("'F01_all_generated_projections_actually_viewed':True","'all_generated_projections_actually_viewed':False")
s=s.replace("admission=get('latest-independent-admissions.json')['newly_notified_admission_120_F02']","admission=get('latest-independent-admissions.json')['newly_notified_admission_122_F01']").replace('120F02','122F01').replace('binding122','binding124').replace("==122 and admission['receipt']","==124 and admission['receipt']").replace('13b991b7795ba22680d1909876e1dbacf76ff63151bb7e052a3c71510f7a207f','38cdecc15b10e68d2345be1bb4f1654ea1c98a53b3c8ac3fe1a38d365cad0e20').replace('ACCEPT_ONE_COMPLETE_RELATED_COD3_WORKSHOP_SPATIAL_REFERENCE_ONLY','ACCEPT_ONE_COMPLETE_RELATED_COD3_CIVILIAN_WORKSHOP_SPATIAL_REFERENCE_ONLY').replace("x['batch']==120 and x['id']=='F02'","x['batch']==122 and x['id']=='F01'").replace('122F01_resolved_accept1_first122','122F01_resolved_accept1_first124')
(O/'seal_screening.py').write_text(s)
print('124 prepared')
