"""Supplement one already-accepted whole's source-road interface; zero credit."""
import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
old=P.parent/'research-20261104-smithy-221';manual=ld(old/'manual-review.json');oldreceipt=ld(old/'RECEIPT.json')
oldfilechecks=[dict(binding=a,matches=bind(a['path'])==a)for a in oldreceipt['files']]
assert all(a['matches']for a in oldfilechecks)
acceptpath=R/'docs/cod4/audit-20261022/coordinator-architecture221-actual-author-ACK-final-acceptance-20261111.json'
accept=ld(acceptpath)
carrypath=P.parent/'research-20261104-smithy-224/carried-forward-pending.json'
carried=ld(carrypath)['221accepted_first224'];assert carried['first_bound_batch']==224 and carried['increment']==1
assert bind(acceptpath)==carried['final_acceptance_binding']
put('old-acceptance-status-correction.json',dict(old_manual_binding=bind(old/'manual-review.json'),old_receipt_binding=bind(old/'RECEIPT.json'),old_files_verified=oldfilechecks,original_complete_manual_preserved=manual,final_acceptance_binding=bind(acceptpath),first_carry_binding=bind(carrypath),first_carry_evidence={k:v for k,v in carried.items()if k!='final_acceptance_entire_object'},accepted_related_NPC01=1,first_carry_batch=224,current_carry_increment=0,current_new_whole=0,correction='本轮先凭221旧manual把它称待审是过时状态；追查224 firstcarry和Main final acceptance后纠正。221早已接受且224首次carry1；290不重新提案/入账。宿主换工具匠/盔甲匠/颜色不另计；201组件不是新房。',reading_boundary='本轮读221原自身完整七维/八限制、Main接受状态/完整边界和224精确firstcarry条目。未重开旧8PNG，未宣称重新完成整栋原始逐层学习。原ACK/其他旧记录仅绑定保留，不冒称重读全部。'))
source=ld(old/'sources.json')['candidates'][0];archive=bind(source['source_archive']);assert archive['sha256']==source['source_archive_sha256']
members=[]
with ZipFile(archive['path'])as z:
 for member,filename in [(source['member'],'host-original.json'),('data/kaisyn/structures/village/exclusives/rustic/streets/straight_01.nbt','road-original.json')]:
  raw=z.read(member);assert read(raw)==ld(P/filename);members.append(dict(member=member,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 assert members[0]['sha256']==source['nbt_sha256']
 for a in ld(P/'original-road-pools.json')+[ld(P/'road-processor.json')]:
  raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['sha256']and raw.decode()==a['text']and json.loads(raw)==a['json'];members.append({k:a[k]for k in ['member','bytes','sha256']})
put('source-bindings.json',dict(archive=archive,members=members,source_context_only_not_assets=True))
road=ld(P/'road-original.json');host=ld(P/'host-original.json');rb={tuple(a['pos']):a for a in road['blocks']};hb={tuple(a['pos']):a for a in host['blocks']}
matrix=[dict(y=y,rows=[[rb[(x,y,z)]['state']for x in range(3)]for z in range(15)])for y in range(2)]
connectors=[dict(pos=list(p),state=road['palette'][a['state']],nbt=a['nbt'])for p,a in rb.items()if 'nbt'in a]
parent=rb[(2,1,7)];child=hb[(0,2,4)]
assert road['palette'][parent['state']]['Properties']['orientation']=='east_up'
assert host['palette'][child['state']]['Properties']['orientation']=='west_up'
delta=[2+1-0,1-2,7-4]
assert parent['nbt']['target']==child['nbt']['name']=='minecraft:building_entrance'
put('road-source-reading.json',dict(size=road['size'],DataVersion=road['DataVersion'],stored=len(rb),palette=road['palette'],all90_state_indices=matrix,all24_connector_states=connectors,actual_reading='全90索引、7palette、24原接头完整读；路段不是完整建筑，不加引用信用。'))
put('raw-interface-derivation.json',dict(parent=dict(pos=parent['pos'],state=road['palette'][parent['state']],nbt=parent['nbt']),child=dict(pos=child['pos'],state=host['palette'][child['state']],nbt=child['nbt']),rotation=0,child_relative_origin_before_native_height_reprojection=delta,derivation='road(2,1,7)+(1,0,0)-host(0,2,4)=(3,-1,3)',meaning='Raw-template coordinate alignment only; parent road uses terrain_matching and host rigid, native heightmap projection not applied. This is not a guaranteed world origin.',road_box=[[0,2],[0,1],[0,14]],raw_host_box=[[3,13],[-1,12],[3,12]],source_boxes_nonoverlap=True,existing_module_host_relative_origin=[3,1,2],existing_module_raw_road_relative_origin=[6,0,5],marker_final='Both selected entrance markers final minecraft:structure_void, which does not certify cleared world air.',new_reference_credit=0))
protected=[]
for a in ld(P.parent/'research-20261104-smithy-289/protected-after.json')['files']:
 before=a['after'];after=bind(before['path']);protected.append(dict(previous289=before,current290=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,all_unchanged=all(a['unchanged']for a in protected),sessions_written=False))
review=dict(batch=290,status='SEALED_OLD221_FIRST224_ROAD_INTERFACE_SUPPLEMENT_ZERO_NEW_REFERENCE',new_complete_whole_studies=0,new_qualifying_reference_proposals=0,formal_credit_added=0,old221_first_carry_batch=224,old221_current_carry_increment=0,old269_current_carry_increment=0,
 actual_work=['核查201组件宿主线索，发现221已完整研究同一宿主+武器模块，停止换职业重复研究。','更正本轮口头待审描述：221原manual待审状态已由Main最终验收及224首次carry覆盖；仅保留真实既有信用。','补读rustic straight_01原道路90位置、7palette、24接头，houses/streets两个完整原池与street_rustic处理器全文。','以东向道路口(2,1,7)对西向宿主口(0,2,4)推导原格偏移(3,-1,3)，保留parent aligned/up一致/name-target匹配及两模板包围盒不交。','读16个宿主口原状态：外floor rooted_dirt、门下coarse_dirt，关闭西门、内darkoak地板和air。host(3,1,4)原air不能按宿主单独认地板洞；旧组合模块补地板，只复用旧整栋结论，不重画/改模块。'],
 pool_findings='houses11候选：八普通屋各weight2、barn weight6、temple weight1、empty14；barn legacy/rigid/minecraft:empty处理器。streets12候选各weight1/legacy/terrain_matching/street_rustic，fallback terminators。这些是原选择规则，不是实际生成12路/11屋。',
 processor_findings='八有序规则：水中terracotta/orange_terracotta转spruce_planks；terracotta随机.1 rooted_dirt和.1 coarse_dirt；orange随机.4 coarse_dirt和.4 rooted_dirt；剩余terracotta转dirt_path，orange转grass_block。未执行随机/水位处理，不把裸陶路基称游戏最终路材。',
 limits=['本批是旧已接受样本证据补充，不是新完整实例；新整栋/新提案/正式增量/旧221重复carry均0。','(3,-1,3)只是未经heightmap重投影的源坐标关系；道路terrain_matching与宿主rigid的实际高程、贴地/碰撞/形状扩展未运行，不称实机道路闭合。','父子入口final structure_void，宿主source air在legacy语境亦不清现存世界；外脚头的原air/marker不足证明现场无障碍。门、熔岩安全、磨石交互、箱盖、生产/付款/任务/中文指南针仍无原生验收。','旧221七维/八限制、Main最终验收和224首次carry严格配对保留；后续不可再把宿主换职业或201工具片算新建筑。旧图未重开，组件/路段/接头/90坐标不计完整建筑。','未读/重建整套村庄街网、城镇中心、终止段、实际群系注册或生成概率；本次仅三个新JSON和一个特定路段原始接口。','无Java/游戏/联网/下载/429/声音/亮度/焦点/唤醒/原存档/专业资产/共享Jar/主清单/pending/ownership/session/Git变化。没有删除任务或提前制作。'],
 COD4_accepted_old_observation=153,COD4_gap=847,NPC_cumulative=None,tasks_deleted=0,all_tasks_complete=False)
put('manual-review.json',review)
checks=dict(old221_33_bindings_intact=len(oldfilechecks)==33 and all(a['matches']for a in oldfilechecks),old221_accepted_first224=accept['accepted_related_complete_NPC01_reference']==1 and carried['first_bound_batch']==224,source_bound=True,road_full90=len(rb)==90,road_palette7=len(road['palette'])==7,road_connectors24=len(connectors)==24,interface_delta=delta==[3,-1,3],original_target_name_match=parent['nbt']['target']==child['nbt']['name'],both_final_structure_void=parent['nbt']['final_state']==child['nbt']['final_state']=='minecraft:structure_void',protected8_unchanged=len(protected)==8 and all(a['unchanged']for a in protected),no_new_credit=review['formal_credit_added']==review['new_complete_whole_studies']==review['new_qualifying_reference_proposals']==0)
assert all(checks.values()),checks
put('verification.json',dict(checks=checks,passed=len(checks),native_tests_run=False))
put('active-checkpoint.json',dict(batch=290,status=review['status'],manual=bind(P/'manual-review.json'),previous_receipt=bind(P.parent/'research-20261104-smithy-289/RECEIPT.json'),old221_accepted_first224=True,new_wholes=0,formal_credit_added=0,no_session_written=True,next='Rustic宿主/工具匠/盔甲匠/武器模块同体均已归221，不再追为新例。现有命名smith及广泛机器筛选已读覆盖很多，不把未见hash当语义新；新目标须先排除已归属组合，避免近似/弱相关。实际适用1000尚未达，不制作。'))
put('RECEIPT.json',dict(batch=290,status=review['status'],files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],checks=len(checks),new_complete_whole_studies=0,new_qualifying_reference_proposals=0,formal_credit_added=0,all_tasks_complete=False))
for a in ld(P/'RECEIPT.json')['files']:assert bind(a['path'])==a
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(ld(P/'RECEIPT.json')['files']),checks=len(checks)),ensure_ascii=False))
