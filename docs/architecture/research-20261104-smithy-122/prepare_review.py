import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
assert not (O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[{
'layout':'同一两层石匠工住单体：西门进下层主工作厅，北内门通北侧楼梯下切石/储物凹位；北侧双宽外阶沿东西向上升，接北带盖落脚平台，再由南向门进上层统一四床生活房。楼梯下北条带西端开放，不称完全封闭的独立第二工作室。整体候选最多1待独立判断，不以两切石机/四床/五箱拆数。相对071F01内四阶上床层、087F02两个独立底铺/外单宽阶只上南半床室、070F02高床屋下开放热台，本例是可内门抵达的阶下冷作凹位/全宽下工上住/双宽外侧阶及带盖顶落脚的整组组织；可以因同族判0。',
'proportion':'14×14×11，DV3953，声明2156，1313存储=982非air331air，843省略不得当air；106palette/entities0。下地坪y0/主用y1，上地坪y4/主用y5，屋脊y13；两主要使用层，不按高度14称14层。北侧高平台floor4/use5，y8高箱不是第三层。',
'facade':'下段cobble120与stonebrick63砌体，上段oaklog82/planks112/whiteconcrete70木框白墙；glass13与lantern5。西oak门3,1/2,6，北内spruce门9,1/2,3，北上oak门9,5/6,3均closed。挂牌Mason\'s Residence是原静态文字，不证明NPC或中文任务；无源实体。',
'roof':'上主房高木坡屋面oakstairs100、oakslab46并含sprucestairs8/fence20构件；北楼梯顶平台x6..11,z0..2在y8是bottom oakslab小平盖，不把其当主坡屋脊。106palette读全，但通用全格图不表达半块、门和坡瓦真实几何，不推原生挡雨/碰撞。',
'materials':'两个stonecutter为6,1,1 east（北阶下）及7,1,7 north（主厅南工作带）；无炉/smoker/铁砧/熔岩/梯，不称完整打铁工艺。上层四yellowbed pairs：head x4,y5,z4..7/foot x5同z，均west且未占用；不是8床。五mason loot箱为5,2,4 south、10,2,1 south、10,2,4 south、10,6,8 north、7,8,4 south，原seed全保留；床/箱不拆参考。',
'circulation':'下西入口0,1,6 empty jigsaw finalair→x1/2,y1/2,z6显式air→门3,1/2,6west/right/closed→主厅x4..10,z5/6,y1/2显式air。厅北端9,y1/2,z4air→门9,1/2,3south/right/closed→9,y1/2,z2air，通北阶下凹位，不说北条带完全闭室。北双宽阶z1/2均x4,y1→x5,y2→x6,y3→x7,y4 bottom stonebrickstairs/east，是向东上升，绝非向北；x8..10,y4,z1/2 stonebricks为落脚，上y5/6 air，向南9,y5/6,z2air→9,5/6,3south/left/closed→9,y5/6,z4air进上层。x7..9,y5/6,z4..7多air作为床旁通道；x6,y5,z4..7 bottom oakslab、x4/5床不能统写air。未验门开合、半块实际NPC通行、楼梯西下端接地或梯下净高。',
 'terrain':'西入口单jigsaw finalair，没有补柱/村民socket；周边grass/dirt/粗土根土承托，不据源主题推实际山脚。root实际plains village jigsaw size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，houses精确mason权4/single/rigid/mossify10，非候选根自动证明在当前游戏生成；DV3953兼容、山脚落点、NPC昼夜雨危与任务/交易/中文指南针均未验。'
},{
'layout':'西主屠宰工作屋接东围栏动物院，低层一间工作/柜台空间与东门通院，不提出新整体家族；与115F01低热翼/动物院及已有侧院工房有交集。两smoker和三个动物socket不当完整独立房或已生成动物。只有whole/cut/y0三图有界阅读，0。',
'proportion':'19×12×13/DV3953，声明2964，1322存储=899非air423air，1642省略，104palette/entities0。没有床/梯或已证上使用层，不由12高推多层。',
'facade_roof_materials':'oakplanks85/log48、strippedoak25、strippedspruce17；oakstairs90/sprucestairs56等木坡盖。原infested_chiseled_stone_bricks6必须保留，不替作普通雕纹砖；water10,1,z8..10三格，非熔岩。未读全palette或上层全部投影，不对细部/院门通行作完整判断。',
'circulation':'西3,2/3,9west/left/closed门进主屋，东9,2/3,4east/right/closed门接院；smoker7/8,2,2south/unlit，原BE空Items/CookBurn0。8,2,8单箱及4,4,z6/7原双箱保留各village_butcher seeds；不说三铺。动物socket13,0,4/15,0,4/15,0,7为village/common/butcher_animals finaldirt，西入口0,1,9 empty/finalair；单Jar缺动物池不推整环境缺失。未验campfire原态、碰撞/AI/中文获取链。'
}]
comparisons=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [64,70,71,87,95,97,111,115]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','stairs','stonecutter','water','bed','smoker'])]
 root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=[dict(pos=b['pos'],state=pal[b['state']])for b in bs],expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if 'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','vertical','y0','y2','y4','y6','y8','y10','y12']if i==0 else['whole','cutaway','y0'],observations=obs[i],written_comparisons=comparisons,full_study=i==0,credit_proposal_maximum=int(i==0),context_reading=f'原plains root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；当前精确houses权{4 if i==0 else 2}/single/rigid/mossify10两.1规则，mossify20只是镇中心上下文。单Jar缺原版loot/biome/zombie processor不推环境缺失。Trek作者hotsuop/Hugger/ALDgamer，MIT，1-B0.6.1，pack10/support10..102；DV3953不推1.20.1原生兼容。'))
put('review-config.json',dict(batch=122,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='ONE_WHOLE_SPATIAL_PROPOSAL_PENDING_AND_ONE_BOUNDED_HOLD_ZERO',scope='COD3 comparable complete civilian workshop spatial research only',cases=cases,image_counts=[19,13,6],limits='F01全部10投影实际已看、106palette全读与主要上下层/北阶带索引矩阵和全部BE读取；非1313格逐格语义阅读/原生图。F02只有3图，余6未看。当前源formal0，F01最多1待独立；120F02既有Main接受1首次122绑定，不重看旧图，不改120/121。无Java/游戏/声音亮度唤醒/实例/产品或主清单修改。',next='继续固定本地相关工坊来源前置去重；122F01等待独立审阅，未通过不入信用。',handoff='122封批：plains石匠两层工住候选1pending与plains屠宰侧院有界0；19图13实际6未看，F01全部10图已看。北双宽外阶沿east上升4,1,z1/2→7,4,z1/2，非north；北阶下冷作凹位西端开放，不称独立封闭房。全宽上层四床只一整体，不按组件计数。120F02 Main接受1首次122精确绑定并解除其pending；120/121旧收据不改。115开trapdoor/torch、111四柱y1..3、118DV3465/3105纠正继续carry。COD4仍153差847，尚未达1000前不制作。'))
d=raw[0]['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):b for b in d['blocks']};positions=set()
for y in range(7):
 for z in range(5):
  for x in range(1,12):positions.add((x,y,z))
for y in [0,1,2,4,5,6]:
 for z in range(4,9):
  for x in range(4,11):positions.add((x,y,z))
for y in range(4):
 for x in range(5):positions.add((x,y,6))
put('F01-route-source-matrix.json',dict(source_audit=bind(O/'raw-source-audit.json'),positions=[dict(pos=list(pos),original_stored=pos in mp,state=pal[mp[pos]['state']]if pos in mp else None,nbt=mp.get(pos,{}).get('nbt'))for pos in sorted(positions)],no_omitted_as_air=True,native_collision_or_pathfinding_verified=False))
s=(O.with_name('research-20261104-smithy-120')/'seal_screening.py').read_text().replace("'F02_all_generated_projections_actually_viewed':True","'F01_all_generated_projections_actually_viewed':True").replace("'prior_admissions_current_increment':0","'prior_admissions_current_increment':1")
needle="put('carried-forward-pending.json',carry);bindings(carry)"
replacement="""admission=get('latest-independent-admissions.json')['newly_notified_admission_120_F02']
check('120F02 first accepted binding122 only',admission['first_bound_batch']==122 and admission['receipt']['sha256']=='13b991b7795ba22680d1909876e1dbacf76ff63151bb7e052a3c71510f7a207f' and admission['increment']==1)
accepted=json.loads(Path(admission['receipt']['path']).read_text())
check('120F02 independent decision1 onlyCOD3',accepted['decision']=='ACCEPT_ONE_COMPLETE_RELATED_COD3_WORKSHOP_SPATIAL_REFERENCE_ONLY' and accepted['new_related_whole_COD3_reference']==1 and accepted['new_COD4_whole_building_credit']==0)
old=carry.get('carried_unresolved_whole_reference_proposals',[])
check('resolve only retained120F02 pending',sum(x['batch']==120 and x['id']=='F02'for x in old)==1)
carry['carried_unresolved_whole_reference_proposals']=[x for x in old if not(x['batch']==120 and x['id']=='F02')]
carry['120F02_resolved_accept1_first122']=admission
put('carried-forward-pending.json',carry);bindings(carry)"""
assert needle in s;s=s.replace(needle,replacement)
(O/'seal_screening.py').write_text(s)
print('122 review prepared; not sealed')
