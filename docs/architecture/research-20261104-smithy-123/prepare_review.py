import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-122');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=get(P/'latest-independent-admissions.json');a['previous_binding']=bind(P/'latest-independent-admissions.json');a['120F02_first_bound122_carry_only_no_current_increment']=True;put('latest-independent-admissions.json',a)
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[{
'layout':'同一民用制箭店：西短门廊接南北长厅，南两制箭工作位、北双箱与陈列，东偏北侧门入东围栏靶院；中央九格室内梯通高位带盖栅栏工作阁亭，非多间封闭卧室。完整空间研究但不提出新信用：相对097F01内梯上开放屋顶工作/储物与侧院、095F02内梯上其他工作区，增加靶块、职业和升高阁亭仍不足以确认新的整体组织，不以造型差异保通过。',
'proportion':'18×16×15，DV3953，声明4320，1605存储=1122非air483air，2715省略，109palette/2entities。地坪0/use1，高阁亭floor9/use10；中间长梯穿挑高空腔，不能每梯格算一层。无床，没有来源支持工住/卧室。两主要使用高度，不按16高称16层。',
'facade':'地面oakplanks185/log165/strippedoak26为长厅木框，混stonebrick77/stone33/cobble23；glass8。西短廊1,1/2,7门与东11,1/2,3门均oak closed/right。挂牌正反Fletcher与箭头是静态作者内容，不能算任务、营业中文或NPC交互。2实体是持bow及crossbow/firework的armorstand，不是两名箭师或射击AI。',
'roof':'南北长木坡屋盖sprucestairs106/oakstairs131并含交叉西门廊盖；中央高亭单独四坡盖，高亭y10/11外围oakfence与log柱并非密闭墙。y9 x7..9,z6..8多top oakslab和9,9,7梯口，上棚工作位不称封闭起居阁楼。通用整格图不表示真实半块或实体外观。',
'materials':'三fletchingtable为6,1,11与10,1,11及6,10,7，仍一座店；target13/15,2,12均power0，不算两座建筑或已验靶场逻辑。6chest方块包含6,1,z2/3原左右双箱，不算6经营空间；2barrel12,2,z6/8是stronghold_dispenser loot，并非发射器方块，不推自动射箭。高亭6,10,5与10,10,9 defending_tower loot不让本屋自动变军事要塞，原6箱2桶seeds保留。',
'circulation':'西入口0,1,7 empty finalstructure_void不是finalair→西门1,1/2,7west→x2..8,y1/2,z7原air（x9梯），主厅x7/8,y1/2,z3..11为主纵向净空但不概括边侧家具为空。东门11,1/2,3east→12..16,y1/2,z3显式air接院；东院下部z12两靶，不是院门。室内9,y1..9,z7为west ladder，西邻x8,z7在y1..8 air，y9 top slab，上9,y10/11,z7air；南北和西侧y10/11多air，6,10,7工作台/两高箱与边栏不写全air。未验长梯NPC能力、门口structure_void替换、靶场碰撞/射线。',
 'terrain':'底层混草/粗土/石路和oakfloor，东院与长厅同地面高度，无支柱池/村民socket。plains root size6/max80/start0/WORLD_SURFACE_WG/beardthin，selected houses权4/single rigid/mossify10。高亭与靶院不拆参考。单Jar缺原版fletcherloot/biometag/zombieprocessor不推环境缺失；DV3953不推1.20.1兼容，不证明山脚/NPC昼夜雨危/任务/付款获取或中文指南针。'
},{
'layout':'樱花主题屠宰铺只做whole/cut/y0三图及门、炉、箱等原态的有界检查，0。西双门入底工作厅，东侧另有门，东内阶有上升段，上层切面显示宽空间但尚未完整研究其边界/落脚/外廊；不把未看8图写成完整新布局，也不因樱花配色算新家族。',
'proportion':'15×15×15/DV3953，声明3375，1787存储=1221非air566air，1588省略，135palette/entities0。无床/ladder不代表没有上层；原10,1,10→10,2,9→10,3,8→10,4,7 north bottom oakstairs确有室内上升段。未验顶落脚，不能声称封闭卧室或确立完整上层用途。',
'facade_roof_materials':'strippedcherrylog113/calcite35/灰青墙材，deepslate tile/brick坡盖有层叠檐，庭外bamboo细部；仅原状态与切图，不称实机瓦面。2smoker7,1,z3/4 west/unlit，Items空且Cook/Burn0；一个butcher箱4,1,2 east seed-4481732505826484704。12面红白墙旗不作12店，正反OPEN/CLOSED挂签不证明营业AI。',
'circulation':'西3,1/2,z8/9成对cherry门west/right与left/closed，11,1/2,5 bamboo门west/right/closed；0,1,8入口empty finalstructure_void不是air。以上门阶原态不等于已验完整客户线/楼梯顶层衔接；尚无源动物实体/animal socket，不能从butcher名推实际牲畜。仅源上下文cherry root/精确权4/empty processor与optional cherry_grove，不证明当前游戏生成或中文联动。'
}]
comp=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [70,71,87,95,97,111,115]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['_door','ladder','target','fletching','smoker'])];root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=[dict(pos=b['pos'],state=pal[b['state']])for b in bs],expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','vertical']+[f'y{y}'for y in range(0,16,2)]if i==0 else['whole','cutaway','y0'],observations=obs[i],written_comparisons=comp,full_study=i==0,credit_proposal_maximum=0,context_reading=('原plains root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；精确houses权4/single rigid/mossify10。两原Trek loot JSON为箭/药箭/弓和材料候选，不是交易、发射器AI或获取回执；mossify20镇中心上下文。'if i==0 else'原cherry root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；精确houses权4/single rigid/empty processor；trek biome tag只有optional minecraft:cherry_grove。')+'Trek hotsuop/Hugger/ALDgamer MIT 1-B0.6.1；pack10支持10..102并非DV3953当前版本可运行证明。'))
put('review-config.json',dict(batch=123,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='ONE_COMPLETE_STUDY_HOLD_ZERO_AND_ONE_BOUNDED_HOLD_ZERO',scope='COD3 comparable civilian workshop spatial research only',cases=cases,image_counts=[22,14,8],limits='F01实际11图全看/109palette与地面矩阵/梯井/上工作亭矩阵/全部BE及2实体原态实际读；非1605格逐格语义阅读。完整研究不等信用，F01同族边界hold0。F02只3图/8未看，非135palette全读或完整布局。两源newformal0/pending0，120接受首次122本批仅carry0，122F01pending保留。',next='继续固定本地先去重来源；保持122F01未独立通过pending，不覆盖旧封批。',handoff='123：plains制箭作坊完整空间研究11图，但与已有内梯上工作/储藏层及侧院组织边界不足，hold0不提出新信用；高亭外围是栅栏，不写封闭卧室。cherry屠宰3图有界0，东内阶确有四段上升但未核顶落脚，不写单层。22图14实际8未看。120F02接受1首次122本批carry0；122F01旧pending精确保留，115/111/118勘误carry。无Java/游戏/声音亮度唤醒/制作/主清单改动。COD4仍153差847。'))
d=raw[0]['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):b for b in d['blocks']};pos=set()
for y in [0,1,2]:
 for z in range(2,13):
  for x in range(18):pos.add((x,y,z))
for y in range(13):
 for x in [8,9,10]:pos.add((x,y,7))
for y in [8,9,10,11]:
 for z in range(4,11):
  for x in range(5,12):pos.add((x,y,z))
put('F01-route-source-matrix.json',dict(source_audit=bind(O/'raw-source-audit.json'),positions=[dict(pos=list(p),original_stored=p in mp,state=pal[mp[p]['state']]if p in mp else None,nbt=mp.get(p,{}).get('nbt'))for p in sorted(pos)],no_omitted_as_air=True,native_pathfinding_verified=False))
s=(P/'seal_screening.py').read_text();start=s.index("admission=get('latest-independent-admissions.json')['newly_notified_admission_120_F02']");end=s.index("put('carried-forward-pending.json',carry);bindings(carry)",start)
s=s[:start]+"""oldcurrent=json.loads((prev/'carried-forward-pending.json').read_text()).get('current_batch_pending_cases',[])
retained=carry.setdefault('carried_unresolved_whole_reference_proposals',[])
for p in oldcurrent:
 if not any(x['batch']==p['batch']and x['id']==p['id']for x in retained):retained.append({**p,'author_receipt':bind(prev/'RECEIPT.json')})
check('122F01 retained once pending',sum(x['batch']==122 and x['id']=='F01'for x in retained)==1)
"""+s[end:]
s=s.replace("'prior_admissions_current_increment':1","'prior_admissions_current_increment':0")
(O/'seal_screening.py').write_text(s)
print('123 prepared')
