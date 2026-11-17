import json, hashlib, math, sys
from pathlib import Path
P=Path(__file__).resolve().parent; R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
def ld(p): return json.loads(Path(p).read_text())
def put(n,v): (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
    p=Path(p).resolve(); b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
protected=[R/'docs/cod4/audit-20261022'/s for s in ['active-workstreams.json','pending-tasks.json','continuation-20261028/session.json']]+[R/f'docs/architecture/research-20261104-smithy-{n}/RECEIPT.json' for n in [301,302,304,305,306]]+[Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')]
before=[bind(p) for p in protected]
seven=dict(
 layout='一完整方形下层厅居与屋盖内上睡层：西门开向西侧低通道，东半有大片bottom oak半砖抬高的休坐区，东侧南北对座加三片closed活板低桌；西南为三烛/四烛和死珊瑚扇陈设。沿南墙west直阶上到睡层，北端两张粉床和居中的高箱，中央另有对座/低桌。下层无床，上层两床不分独立客房。无营业招牌、厨房或付费功能，不称客栈或茶馆。',
 proportion='13×10×13/DV3953=1690声明格；882保存709非air173显air，808省略unknown。81palette/14BE/entities[]；10层130行1690格索引、7分类PNG/2整高剖实际读。下层floor0/use1，东x6..9/z3..9大量y1 bottom oak半砖使站面局部抬半格；上floor4的top spruce阶/半砖及y5局部bottom半砖相叠，床在y5。两个使用层而非10层；两床共4床块。屋盖收坡压低两侧，不把模板13格宽或整上层都算足高净房宽。',
 facade='54cherry log与12cherry wood多轴木架、98calcite白填墙，西3,y1/2,6单cherry门朝east/closed。外open spruce活板裙和open fencegate檐下，cherry栅/活板窗薄件，未存玻璃。35grass/29dirt低基和13stone bricks入口。黄底红纹三旗、黑底白骷髅二旗保留原作者纹样，未存中文匾额。不凭白墙深顶或cherry命名认定徽派。无外竹林，本源只有一盆竹，不复用306林居资格。',
 roof='一套沿z的长脊双坡宽檐屋盖：y4开栅门檐下及横梁，y5外stone brick上下半砖围着deepslate brick檐带；y6两侧x3/9深砖带和x2/10薄檐，y7两侧x4/8坡阶，y8 x5/7向脊收，y9 x6,z2..10 bottom stone brick半砖与z1/11端阶封顶。上睡层放在此盖内，y7..9顶腔不增楼层。69深砖、36深砖阶、21深砖半砖、61石砖半砖、20石砖阶为原材频，不拆设计计数。不是茅草顶，无屋顶相连巷道、防雨、雪载或原生跑酷证明。',
 materials='两粉床x5/7,y5,z3head→z4foot/north，occupiedfalse；四床块BE只有bed id。下箱3,2,4east/seed4206949059566655247、上箱6,6,3south/seed2737832404626170337都为trek:village/village_cherry_house，未roll库存。下箱放3,1,4top cherry阶，上箱坐6,5,3double spruce半砖。下东8,1,z4/6南北对向底阶和8,2,z4..6 bottom closed west活板构成低桌；上同类陈设在6,5,z5/7阶与6,6,z5..7活板。西南3,1,8三支lit烛/5,1,8四支lit烛、4,1,8白毯、4,2,9死珊瑚扇不是饭菜或茶棋实证。普通灯2=9,3,3 standing及6,8,4 hanging。无炉/营火/工作台，不冒称锻造、供暖或NPC行为。',
 circulation='西0,1,6入口jigsaw最终structure_void，0,y2..4,6unknown；1,y1..4,6显air，2,y1/2,6air但y3 top closed cherry活板，3,y1/2,6闭门，内4,y1..3,6air。沿南墙8,1,9→7,2,9→6,3,9→5,4,9四west bottom oak阶，其各上两格显air。西落4,4,9top south spruce阶上y5/6air而y7坡阶；转北5,4,8top半砖叠5,5,8bottom半砖，上y6/7air但y8坡阶，保留半格过渡。床脚前5/7,5,5是bottom半砖，上6/7air、8为坡阶。下箱east前4,y1..3,4air，上4,4,4top阶；上箱south前6,6/7,4air、y8悬灯，下6,5,4bottom半砖，箱上6,7/8,3air。只证源格组织，不证闭门动作、阶/薄件真实碰撞、床箱可用或NPC全程路径。',
 terrain='原木地/草土低裙与西石砖短入口一体保留，y-1与界外未给，不能补air或假定落地。两up_west村民口5,0,z5/7最终oak planks与一west入口不同；entities[]不当已入住证明。5原context与304全文已读资源完全相同，按对象和hash复用；本屋在22项house池weight4/single_pool/rigid/emptyprocessor。root size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，3towncenters各1，biome只optional cherry_grove。原3..8roll/10物品loot与random_sequence原拼写vilage保留，未生成/开箱/发奖。街道/中心/终止件NBT及村民池未读未拼，不能声称自然城镇、生态、中文任务指南针或生存获取验收。')
limits=[
 '本批完整原源空间研究1，最多提出1个DUN05废弃民居/屋盖内竖向交通的广义东亚辅助候选；正式信用0，待Main独立整栋/用途审查，严格徽派与中国文化资格0。',
 '与297下两床上两床/北内阶、306下单床上储物/墙梯、249无上交通隐桶、304三桌厅加两个三床睡层，均先读完整七维再PNG。相近作者/风格可以研究，整体布局差异须独立评估，尺寸/楼梯/双床/换材均不单独计数。',
 'Main306已接纳1有界NPC03林居辅助实例，其完整判断和绑定在本批单独carry；不把306接纳、竹林资格或旧153总数转给307。Main304独立验收未获证，不把304称已通过。保留298全屋8床块和302非同9×9主基更正。',
 '全81palette Properties、14BE完整位置/payload、10层130行1690索引、120选格和7分类PNG实际读。分类立方将半砖/台阶/床/活板等立方化，不是原纹理/原生碰撞/模型或视觉验收；808省略unknown不当air。',
 '无适用1000门槛证据，不生产、不删任务或提示词；COD4历史153/缺847不在此批递增，各主题核实累计及缺口unknown。',
 '仅本地Python -B读固定资料、写自身307目录；无Java/Gradle/游戏/网络/UI/亮度声音/唤醒/焦点/实例/原档/共享Jar/专业资产/主清单/session/Git/自动化操作。']
put('manual-review.json',dict(batch=307,source=ld(P/'source-binding.json'),counts=ld(P/'source-counts.json'),task_source=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')),scope='DUN05民居与屋盖内交通的空间辅助；非严格徽派资格，非NPC03竹林茅屋资格',seven_dimensions=seven,limits=limits,pre_render_family_check=bind(P/'pre-render-family-check.json'),context_reuse=bind(P/'context-reuse.json'),Main306_bounded_qualification=bind(P/'Main306-bounded-qualification-carry.json'),actual_reading=dict(images=7,PNGs=['whole.png','cut-02.png','cut-04.png','cut-06.png','layers-00.png','layers-05.png','sections.png'],layers=10,rows=130,declared_cells=1690,palette=81,BE=14,entities=0,selected_probes=120,identical_context_bodies_reused_from_prior_actual_reading=5,new_selected_context_entry_actually_read=True,old_complete_seven_dimensions=[249,297,304,306]),complete_original_spatial_study=True,new_complete_whole_studies=1,auxiliary_reference_proposal_maximum=1,formal_credit_added=0,strict_Chinese_or_Hui_reference_credit_added=0,scope_total=None,scope_shortfall=None,status='HOLD0_PENDING_INDEPENDENT_RELEVANCE_AND_SEMANTIC_REVIEW',native_acceptance=False,all_tasks_complete=False))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']}; checks=[]
def ck(n,v):
    assert v,n
    checks.append(dict(check=n,passed=True))
ck('declared1690_stored882_nonair709_air173_unknown808',math.prod(d['size'])==1690 and len(bs)==882 and sum(pal[b['state']]['Name']=='minecraft:air' for b in bs.values())==173)
ck('81palette14BE_entities0',len(pal)==81 and sum('nbt'in b for b in bs.values())==14 and d.get('entities')==[])
plans=ld(P/'all-layers-state-index.json')['layers'];ck('10layers130rows',len(plans)==10 and sum(len(v['rows_z']) for v in plans)==130)
for ly in plans:
 for z,row in enumerate(ly['rows_z']):
  for x,val in enumerate(row.split()):
   b=bs.get((x,ly['y'],z)); assert val==(str(b['state']) if b else '_')
ck('all1690states_or_unknown_match_source',True)
probes=ld(P/'route-probes.json')['probes'];ck('120probes3unknown',len(probes)==120 and sum(v['state']is None for v in probes)==3)
for v in probes:
 b=bs.get(tuple(v['pos']));assert v['state']==(pal[b['state']] if b else None) and v['nbt']==(b.get('nbt')if b else None)
ck('all_probes_full_state_and_BE_match_source',True)
stairs=[(8,1,9),(7,2,9),(6,3,9),(5,4,9)]
ck('4west_bottom_stairs_with_twohigh_air',all(pal[bs[x,y,z]['state']]['Properties'].get('facing')=='west' and pal[bs[x,y,z]['state']]['Properties'].get('half')=='bottom' and all(pal[bs[x,y+dy,z]['state']]['Name']=='minecraft:air' for dy in [1,2]) for x,y,z in stairs))
ck('2north_beds',all(pal[bs[x,5,z]['state']]['Properties'].get('part')==part and pal[bs[x,5,z]['state']]['Properties'].get('facing')=='north' for x in [5,7] for z,part in [(3,'head'),(4,'foot')]))
ck('five_identical_contexts_selected_weight4',ld(P/'source-context.json')==ld(R/'docs/architecture/research-20261104-smithy-304/source-context.json') and ld(P/'context-reuse.json')['selected']['weight']==4)
ck('two_ordinary_lanterns_one_each_hanging',sorted(pal[b['state']]['Properties']['hanging'] for b in bs.values() if pal[b['state']]['Name']=='minecraft:lantern')==['false','true'])
ck('Main306_bound_credit_not_transferred',ld(P/'Main306-bounded-qualification-carry.json')['accepted_auxiliary_instances']==1 and ld(P/'Main306-bounded-qualification-carry.json')['credit_transferred_to307']==0)
put('validation.json',dict(checks=checks,boundary='Original data consistency only; no native/semantic/building credit.'))
put('active-checkpoint.json',dict(batch=307,status='COMPLETE_TWO_LEVEL_DWELLING_SOURCE_ACTUALLY_READ_PENDING_INDEPENDENT_REVIEW',new_complete_whole_studies=1,auxiliary_reference_proposal_maximum=1,formal_credit_added=0,strict_Chinese_or_Hui_credit_added=0,tasks_deleted=0,manual=bind(P/'manual-review.json'),Main306=bind(P/'Main306-bounded-qualification-carry.json'),next='Deliver for independent whole/purpose review; continue different actual related whole, prequalify purpose and compare complete prior designs before PNG. No new production below1000.'))
after=[bind(p)for p in protected];assert before==after
files=[bind(p)for p in sorted(P.iterdir())if p.is_file() and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=307,status='SEALED_COMPLETE_DWELLING_SOURCE_STUDY_PENDING_INDEPENDENT_REVIEW',files=files,data_checks=checks,protected_before=before,protected_after=after,protection_boundary='封存步骤前后稳定性，不声称整个并发时段审计。',new_complete_whole_studies=1,auxiliary_reference_proposal_maximum=1,formal_credit_added=0,strict_Chinese_or_Hui_credit_added=0,tasks_deleted=0,native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_stable=len(after)),ensure_ascii=False))
