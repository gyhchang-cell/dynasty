import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-126');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=get(P/'latest-independent-admissions.json');a['previous_binding']=bind(P/'latest-independent-admissions.json');a['125F02_first_bound126_carry_only_no_current_increment']=True
f=R/'docs/cod4/audit-20261022/coordinator-smithy126-F01-whole-review-20261109.json';b=bind(f);assert b['sha256']=='ad34036ba7de2330d18d634b0472cbbbc6bc21473236b3aafe33f6467690fd79'
a['newly_notified_admission_126_F01']=dict(receipt=b,increment=1,first_bound_batch=127,scope='COD3 NPC01 comparable complete civilian workshop spatial reference only',COD4_increment=0,current_batch_source_credit=0,not_total_cumulative=True,sealed126_preserved=True,limits=['one complete narrow shop organization, no component count','upper work gallery has open sides','spiral continues to partial high landing not third complete floor','three targets not three tested shooting lanes','no beds','spiral headroom/native NPC/halfstairs untested','natural generation/DV compatibility/quest/payment acquisition not accepted']);put('latest-independent-admissions.json',a)
raw=get(O/'raw-source-audit.json')['candidates'];ctx=get(O/'source-context.json')['candidates']
obs=[{
'layout':'cherry渔作小棚在北、邻水池/短作业台向南；同一低盖民用水边工作点，只whole/cut/y0三图有界核查，0。相对061F03前作业平台接后冷作小室、097F01室外水场与屋体等已存组织，没有从当前三图证实新分层/多区通行；并非说所有水池同一建筑，只是不凭樱花屋顶/箱桶/池水添新信用。',
'proportion':'9×9×16/DV3953，声明1296，657存储=489非air168air，639省略；70palette/entities0。无床/梯/门或第二经营层原态依据，9高不当多层。屋主体与南池同一设计，池边箱不拆另一房。只3图，5未看，不称70palette全读/完整动线。',
'facade_roof_materials':'cherrylog32/oakplanks21/spruceplanks9，deepslatetile/brick半砖和台阶形成低尖宽檐盖；水44、seagrass15/tallseagrass4并非44池/19建筑。南池外7,2,9 up barrel及内5,2,3west chest均fisherloot，原seeds1833651099477692194/8037176865470425863保留。没有炉砧/热源，不称完整锻造或鱼类自动生产。',
'circulation':'0,2,4west empty入口finalair，无门不等于所有外圈可通；棚/台/池边薄slab、围柱、含水状态与NPC入池边寻路未验，不据灰图编实心石码头或船。真实cherry root size6/max80/beardthin，精确houses权4/single rigid empty processor、optional cherry_grove；源码loot/池水不是任务交易或中文指南针。'
},{
'layout':'swamp渔棚及西抵达平台位北侧，屋前较大天然形池向南；低盖单层箱桶工作点与水场相邻，只3图有界0，不凭池面积/三socket/沼泽木色或前廊数增加完整家族。与前作业台接小工作棚/外水场等已存参考近族，尚无完整新通行机制依据。',
'proportion':'13×10×20/DV3953，声明2600，1324存储=915非air409air，1276省略；42palette/entities0。主平台socket在y3/use4箱桶，源无床/梯/门/已证第二使用层，高10不当多层。只3图，其余5未看，不能称42palette全读或1324逐格语义阅读。',
'facade_roof_materials':'spruce slab84/stairs35/planks11与木柱低檐，241water/51seagrass/2tallseagrass是水场材质，不是241参考。桶5,4,5up seed3016884872351858792与7,4,2west seed-7822150978310455012，箱5,4,6south seed-2624678968271547566原fisherloot保留；不把三储物块说三座工作屋或原生鱼交易。',
'circulation':'入口0,3,3west empty但final是east/bottom/straight/dry sprucestairs，不是air。两个villager socket5,3,3与6,3,6 up_west，final原minecraft:spruce_slab[type=top, waterlogged=false]正确含空格；不是已生成2NPC。屋/池薄地坪和实际半阶寻路未验。真实保存root/houses为swamp_vanilla、当前NBT在swamp无精确selected；村民候选与street/house处理只语境，不把邻池权重/处理或自然生成套给本源。'
}]
comp=[bind(R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json')for n in [61,97]]
cases=[]
for i,(r,c)in enumerate(zip(raw,ctx)):
 d=r['nbt_decoded_original'];pal=d['palette'];bs=[b for b in d['blocks']if b.get('nbt')or'barrel'in pal[b['state']]['Name']];root=next(t['json']for t in c['contexts']if '/worldgen/structure/'in t['member']);pool=next(t['json']for t in c['contexts']if t['member'].endswith('/houses.json'))
 cases.append(dict(id=r['id'],source_stats=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],expected_counts=r['material_counts'],expected_states=[dict(pos=b['pos'],state=pal[b['state']])for b in bs],expected_block_entities=[dict(pos=b['pos'],nbt=b['nbt'])for b in bs if'nbt'in b],selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']],root_fields=root,viewed=['whole','cutaway','y0'],observations=obs[i],written_comparisons=comp,full_study=False,credit_proposal_maximum=0,context_reading=('cherry root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，精确houses权4 single rigid empty processor、optional cherry_grove。'if i==0 else'swamp_vanilla真实root size6/max80/start0/WORLD_SURFACE_WG/terrainnone/expansiontrue，本swamp源无精确houses匹配。村民候选与swamp biometag、street/house swamp_vanilla原规则只语境，非当前源实际应用证明。')+'原版fisherloot单Jar缺失不推环境缺失；Trek hotsuop/Hugger/ALDgamer MIT 1-B0.6.1，DV3953不推1.20.1兼容。'))
put('review-config.json',dict(batch=127,history_pairs=get(O/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],status='TWO_BOUNDED_STUDIES_HOLD_ZERO',scope='COD3 comparable civilian workshop spatial research only',cases=cases,image_counts=[16,6,10],limits='两源各3图有界0，16图6实际10未看，非全palette/全位置/完整动线。当前source formal0/pending0。126F01 Main接受1首次127绑定，125first126/122first124/120first122均carry0，不回写旧批，不重看旧PNG。无Java/游戏/音亮唤醒/制作/产品/主清单改动。',next='继续固定本地先去重的完整相关民用作坊来源，保留已通过范围；1000未达不制作。',handoff='127封存cherry/swamp渔棚各3图有界0，16图6实际10未看，不按水格/箱桶/socket计参考。126F01 Mainad34036ba7de2330d18d634b0472cbbbc6bc21473236b3aafe33f6467690fd79/69321B接受1首次127绑定并解除其pending，旧封存126不改。上廊开侧、旋梯局部高落脚非第三满铺经营层、三靶非三实测靶道及半阶净高/NPC/DV/自然生成/付款任务未验限制carry。125/122/120以前接受只carry0，115/111/118纠正保留；COD4仍153差847，无Java/游戏/制作/主清单修改。'))
s=(O.with_name('research-20261104-smithy-126')/'seal_screening.py').read_text().replace("'F01_all_generated_projections_actually_viewed':True","'all_generated_projections_actually_viewed':False")
s=s.replace('newly_notified_admission_125_F02','newly_notified_admission_126_F01').replace('125F02','126F01').replace('binding126','binding127').replace("==126 and admission['receipt']","==127 and admission['receipt']").replace('37ead5c9af72eb458acb33a5b971e8cae6baf2e046f44c983d611c9e8a3c5b3b','ad34036ba7de2330d18d634b0472cbbbc6bc21473236b3aafe33f6467690fd79').replace("x['batch']==125 and x['id']=='F02'","x['batch']==126 and x['id']=='F01'").replace('126F01_resolved_accept1_first126','126F01_resolved_accept1_first127')
(O/'seal_screening.py').write_text(s)
print('127 prepared')
