import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-127');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=get(P/'latest-independent-admissions.json');a['previous_binding']=bind(P/'latest-independent-admissions.json');a['126F01_first_bound127_carry_only_no_current_increment']=True
f=R/'docs/cod4/audit-20261022/coordinator-smithy127-carry-and-bounded-screen-review-20261109.json';b=bind(f);assert b['sha256']=='637953128e1eb3a05bd1005cc1c21836a839e14b2526acd16a9ddf1426c0f80f'
a['127_main_carry_and_bounded_screen_review']=dict(receipt=b,current_increment=0,no_new_visual_or_complete_NBT_credit=True);put('latest-independent-admissions.json',a)
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[dict(
layout='taiga制箭木塔：小地层工作室、内梯和上方窄工作平台/楼亭；仅whole/cut/y0三图有界0。与125F01同类窄木制箭塔、123F01内梯接高工作亭近族，当前不凭松木/四工作台/高度新增完整组织信用。不是断言整屋只有一使用层。',
proportion='9×16×9/DV3953，声明1296，692存储=548非air144air，604省略；68palette/entities0。三图实际，另8图未看，不称全palette/全部空间或完整梯出口研究。',
facade_roof_materials='sprucelog140/planks49、darkoakstairs53、stonebrickstairs48及低交错坡盖。四fletchingtable在5,1,5；3,5,5；2,9,6；6,9,2，不当四栋/四NPC。无床/炉砧/熔岩依据，不称锻造；两高chest使用defending_towerloot不据此改称军事塔。',
circulation='西门2,1/2,4west/right/closed；入口0,1,4west empty finalstructure_void不是air。8west ladder在5,y1..8,4，y4相邻多top/closed spruce trapdoor，不说全层air或已经碰撞可通。下chest3,1,5north seed-4170413165452087580、中3,5,4east seed6366753896104961504为fletcher；上2,9,2south/-8586407752434863517与6,9,6west/-2070808774745132332为defending_tower原loot。实际半块/高处使用/NPC未验。'
),dict(
layout='完整小型高脚屠宰铺：西侧低盖开放前作业/接客带接南侧外升阶，高处南门入东侧封闭烟熏工作小室；东地面围栏动物院直接位于高工作室之下，而非并列旁院。整组提出最多1待Main独立适用性/家族审查，不拆上下/烟熏炉/两个animal socket/招牌。相对070F02下热工上卧、087F02两不通底店上卧、115F01地层中央核分西热翼东院并内阶上冷储，本例将围动物院置于工作室下方、经营接待带在西、外南阶接高处热工作房；可借鉴把原料围场与小工作室上下安排并外置交通。是否足够区别由Main决定，未自计数。',
proportion='13×11×8/DV3953，声明1144，685存储=446非air239air，459省略，52palette/entities0。上室floor4 TOP acaciaslab/use5，屋面floor8 BOTTOM slab，上缘y9围栏/单烟柱y10；无床/ladder，不是工住阁楼或第三经营层。全部9PNG实际看、全部52palette与BE以及y0..9全幅原索引读到；不称685块逐格语义逐一验收。F01仅3图，批次20图实际12/8未看。',
facade='高室orange_terracotta44、acacialog71框架、侧glasspane2，地面acaciafence围栏86含侧界；门9,5/6,5south/left/closed，内室x8..10,z2..4；西边x2,y4,z0..6闭合BOTTOM trapdoor和x5,y5,z0..6闭合BOTTOM trapdoor为檐饰，不写开放护栏。西4banner原白红色不是已设计中文招牌；Butcher shop静态英文双面挂牌不作营业AI。',
roof='西低盖y4主要x3 BOTTOM/x4 TOP acacia slab，不能整格图当同一齐平石平台；东高室y8 BOTTOM acacia slab平盖、y9 fence边缘与烟柱，源无屋顶梯/门，不说可经营屋顶露台。高室地板是y4 TOP木半砖，保留半格与盖边非整石假象。',
materials='smoker9,5,2south/unlit，CookTime/BurnTime/CookTimeTotal全0、Items空/RecipesUsed空；9,6/7,2cobblestonewall连上烟柱，不称已工作排烟或真实烟害。上箱10,7,4west/butcherloot seed-5413868332285551073，其下10,6,4为TOP/closed/west trapdoor非air，箱高可达未验。地面唯一water10,0,2level0、无岩浆/砧/forge，水点不是淬火闭环。',
circulation='西入口0,1,6empty finalstructure_void；地层x3..5,y1/2,z1..5多air，东院在x6,1,3 closed/east acaciafencegate，动物socket8,0,2与10,0,4均butcher_animals/finalgrass非已生2动物。南外梯z7含BOTTOM/east阶5,1,7及同x叠放5,2,7、6,3,7、8,4,7；邻TOP/west承托6,1/2,7和7,3,7，不伪写成x5→6→7→8每格同向四连续底阶。末端9,4,7整acaciaplank→9,5/6,6air（下9,4,6横木）→9,5/6,5门→9,5/6,4air入工作室。低端叠阶与中段TOP反向承托的真实步进/净高/NPC碰撞未运行核查，不担保可走。',
terrain='源包括草土院、西接待带/低檐、南外梯、高室及整屋盖，无缺失房翼；两个animal pool原版单Jar缺失不是全环境缺失。真实savanna root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，houses精确weight2/single/rigid/emptyprocessor，towncenters四Trek中心各110和四vanilla zombie小权重只是语境。DV3953不推1.20.1兼容；山脚生成/半阶寻路/收摊避雨/任务付款获取/中文指南针都未验，非完整铁匠工艺。'
)]
comp=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [70,87,115,126]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt') or any(t in pal[b['state']]['Name']for t in ['door','ladder','fletching','smoker'])];root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 states={tuple(b['pos']):dict(pos=b['pos'],state=pal[b['state']])for b in bs}
 if i==1:
  for b in d['blocks']:
   x,y,z=b['pos']
   if (z==7 and 4<=x<=9 and y<=6)or(8<=x<=10 and 2<=z<=6 and 4<=y<=8):states[tuple(b['pos'])]=dict(pos=b['pos'],state=pal[b['state']])
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=list(states.values()),expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','y0']if i==0 else['whole','cutaway','vertical']+[f'y{y}'for y in range(0,11,2)],observations=obs[i],written_comparisons=comp,full_study=i==1,credit_proposal_maximum=int(i==1),context_reading=('taiga houses权2/single rigid/mossify10，源smalldoor/ladder/分层高工作位保留，不称完整动线；defendingtowerloot为箭/弓物品表非军事建筑。'if i==0 else'savanna houses精确weight2/single rigid emptyprocessor，root六级/max80/beardthin，towncenters四Trek各110和zombie权2/1/3/3，fallbackempty，非当前源应用zombieprocessor。')+'单Jar missing不推全环境缺失；Trek hotsuop/Hugger/ALDgamer MIT 1-B0.6.1，DV3953不推1.20.1兼容。'))
put('review-config.json',dict(batch=128,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='ONE_WHOLE_SPATIAL_PROPOSAL_PENDING_AND_ONE_BOUNDED_HOLD_ZERO',scope='COD3 comparable civilian workshop spatial research only',cases=cases,image_counts=[20,12,8],limits='F01三图有界0，F02九图全看/52palette/allBE/y0..9索引完整空间研究提出最多1pending，正式0。低端叠阶/反向TOP承托与实机净高/NPC未验；半砖、上箱下活板保留。旧120/122/125/126接受均carry0；127 Main只读哈希与文字复核carry0，不重审旧PNG。无Java/游戏/音亮唤醒/制作/产品/主清单改动。',next='继续固定本地预先去重的完整相关民用作坊来源；等待128F02独立适用性/家族审查，不自计信用，不重复交办。1000未达不制作。',handoff='128：taiga_fletcher有界3图0；savanna_butcher完整9图/52palette/allBE/y0..9原索引，高工作室下动物院+西低檐接待/南外梯，整体最多1pending正式0。低端5,1/2,7叠底阶与6,1/2,7及7,3,7反向TOP承托、末端8,4,7底阶→9,4,7整木→9,5/6,6air→南门的真实步进/净高未验，不伪称同向四阶或可走。上箱下TOP活板、屋盖不可当第三经营层；两个animalsocket不当动物。20图实际12/8未看。127 Main carry复核绑定但增0，126first127/125first126/122first124/120first122全carry0；111/115/118纠正和swamp限制保留。COD4仍153差847；无Java/游戏/制作/主清单修改。'))
s=(P/'seal_screening.py').read_text();start=s.index("admission=get('latest-independent-admissions.json')");end=s.index("put('carried-forward-pending.json',carry);bindings(carry)",start)
s=s[:start]+"previouscarry=json.loads((prev/'carried-forward-pending.json').read_text())\ncarry['carried_unresolved_whole_reference_proposals']=previouscarry.get('current_batch_pending_cases',[])+previouscarry.get('carried_unresolved_whole_reference_proposals',[])\n"+s[end:]
s=s.replace("'prior_admissions_current_increment':1","'prior_admissions_current_increment':0").replace("'all_generated_projections_actually_viewed':False","'all_generated_projections_actually_viewed':False,'F02_all_generated_projections_actually_viewed':True")
(O/'seal_screening.py').write_text(s)
print('128 prepared')
