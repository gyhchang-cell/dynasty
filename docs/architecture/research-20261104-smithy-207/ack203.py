import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-206';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
mp=Path('docs/cod4/audit-20261022/coordinator-architecture203-whole-work-tower-preack-review-20261111.json');m=read(mp);a=read(P.parent/'research-20261104-smithy-203/manual-review.json')['cases'][1]
assert bind(mp)['sha256']=='490ce486ffce90fc0967cd97cac8fabe4564694be57310c3a0b42c7b0677789f'
assert m['complete_original_author_judgment']==a and len(a['seven_dimensions'])==7 and len(a['limits'])==13
responses=[
'确认仅一栋8×16×7/DV3337，896范围576保存/320省略非air；43palette/15BE/entities[]，16层112RLE与8PNG是阅读范围，不能按层/图/块数计建筑。',
'确认底储物炉室floor1/use2→独立床/工作储物floor6/use7→开敞屋顶热作floor13/use14由12段直梯贯穿，16高不是16层，三功能区不拆三例。',
'确认东侧x5门朝west，门外6/7,y2/3,z3省略不当air；原门闭合，内侧空格只证明所读局部，不能推实际地面入口/开门穿行。',
'确认12梯背确stone/stonebrick，但中层2,7,3为north/bottom/open spruce trapdoor，不是air；顶2,14,2为east/bottom/closed同木活板，需操作，上2,15,2air不证明安全攀登/NPC会开。三格已从保存203原解码独立定位，不重开旧PNG/NBT。',
'确认双箱各seed和2空桶，三中桶含4,7/8,4叠放，屋顶双桶非独立楼；两bed块仅一床，炉均静态未燃空时钟，不因高炉/职业换新族，不宣锻造全工序。',
'确认石砖/裂砖/圆石壳和木TOP半砖真实状态，分类全格图不是原纹理/薄块碰撞/灯光；屋顶开齿墙无完整防雨盖，不称民用阁楼或生产资产。',
'确认两mob socket与root skeleton完整范围配置，entities[]不等和平民用。6JSON/3metadata仅既读语境，tour2/skeletonNBT/嵌套tag/structure_set未读；排除误搜desert上下文，不擅扩运行闭环。',
'确认197中心柱绕阶多环工位、126旋阶侧出整条带盖廊、138地下花床/侧入/后脚手架到空井塔脚与屋顶的完整比较及全部限制；当前整体差异限紧凑直梯串储物热室/独立卧层/屋顶热区，非塔高或设备数信用，不保证全历史唯一。',
'已实际完整读095F02/097F01/123F01各七项含嵌入限制：095附低石作棚/内梯上砧药床三向隔间，097地面L混工住/内梯上开放储顶/侧水院，123长制箭厅/侧靶院/长梯上单亭且作者HOLD0。承认共用直梯家族，差异只能落在整体分区与路径，不追授123/改旧状态；至多1待Main最终接受。'
]
assert len(responses)==len(m['Main_findings'])==9 and len(m['Main_limits'])==8
rawpath=P.parent/'research-20261104-smithy-203/raw-source-audit.json';n=read(rawpath)['candidates'][1]['nbt_decoded_original'];g={tuple(b['pos']):b for b in n['blocks']};rows=[]
for c in [(2,7,3),(2,14,2),(2,15,2)]:rows.append(dict(pos=list(c),state=n['palette'][g[c]['state']]))
assert rows[0]['state']['Name']=='minecraft:spruce_trapdoor' and rows[0]['state']['Properties']['open']=='true'
assert rows[1]['state']['Properties']['open']=='false' and rows[2]['state']['Name']=='minecraft:air'
for k in ['source_receipt','source_manifest','manual_judgment']:
 assert bind(m[k]['path'])==m[k]
for c in m['complete_prior_saved_comparisons']['additional_close_whole_judgments']:
 assert bind(c['binding']['path'])==c['binding'] and len(c['complete_saved_observations'])==7
put('203-preack-author-ack.json',dict(batch=207,scope='203F02实际作者ACK，最大1NPC01完整空间参考，未获最终接受前0',Main_review_binding=bind(mp),full_Main_judgment_preserved_exact=m,original_author_judgment_preserved_exact=a,actual_reading=dict(Main_findings=9,Main_limits=8,original_seven_dimensions=7,original_limits=13,additional_complete_prior_judgments=['095F02','097F01','123F01'],additional_full_observation_groups=21,complete_existing_comparisons=['197F04','126F01','138F02'],images_or_raw_NBT_reopened=0,queried_saved_original_states=3,bounded_unclipped_text=True),saved_original_decoded_binding=bind(rawpath),actual_exact_trapdoor_records=rows,Main_finding_responses=[dict(finding=x,response=y) for x,y in zip(m['Main_findings'],responses)],Main_limit_responses=[dict(limit=x,response='逐条确认、完整保留；只限NPC01相关整栋空间研究，不升级实机/生产/奖励付款/任务删除或累计1000达标。') for x in m['Main_limits']],current_actual_author_ACK=True,Main_actual_author_ACK_received_historical_false_preserved=True,original203_preserved=True,formal_credit_added=0,NPC01_current_increment=0,NPC01_total=None,COD4_count=153,COD4_gap=847,NPC05_increment=0,accepted157_first206_later_increment=0,case203_still_pending_until_Main_final=True,all_tasks_complete=False))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous206_binding']=bind(PRE/name)
 # First carry is historical in the nested exact record; current increment is explicitly zero.
 d['157W01_first206_current207_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:
  assert [(x['batch'],x['id']) for x in d['carried_unresolved_whole_reference_proposals']]==[(203,'F02')]
  d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['203F02_actual_ACK207_pending_final']=dict(binding=bind(P/'203-preack-author-ack.json'),formal_credit_added=0)
 put(name,d)
s=dict(batch=207,status='ACTUAL_203_AUTHOR_ACK_SAVED_RESEARCH_CONTINUES',active_pending=['203F02'],formal_credit_added=0,accepted157_first206_current_increment=0,COD4_count=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,java_run=False,game_run=False,production=False,masterlists_edited=False,next='Continue one fresh related whole building original study; final Main203 decision pending; no repeated accepted reference credit or production.')
put('active-checkpoint.json',s);print(json.dumps(bind(P/'203-preack-author-ack.json'),ensure_ascii=False))
