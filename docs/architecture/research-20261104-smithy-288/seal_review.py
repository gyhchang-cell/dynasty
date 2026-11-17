"""Seal actual local-source architecture reading, not native acceptance."""
import hashlib,json,sys
from pathlib import Path
from zipfile import ZipFile
from collections import deque,Counter
P=Path(__file__).resolve().parent
R=P.parents[2]
assert not (P/'RECEIPT.json').exists(), 'Sealed batches are immutable'
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p): return json.loads(Path(p).read_text())
def put(n,v): (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();raw=p.read_bytes()
 return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
s=ld(P/'sources.json'); d=ld(P/'F02-original.json')
pal=d['palette']; cells={tuple(a['pos']):a for a in d['blocks']}
air={p for p,a in cells.items() if pal[a['state']]['Name'] in ('minecraft:air','minecraft:cave_air','minecraft:void_air')}
remaining=set(air); components=[]
while remaining:
 start=min(remaining);remaining.remove(start);q=deque([start]);found={start}
 while q:
  p=q.popleft()
  for dv in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
   n=tuple(p[i]+dv[i] for i in range(3))
   if n in remaining:remaining.remove(n);found.add(n);q.append(n)
 components.append(dict(count=len(found),bounds=[[min(p[i]for p in found),max(p[i]for p in found)]for i in range(3)],upper_service=(20,47,4)in found,main_service=(23,2,13)in found,deep_service=(4,4,40)in found))
components.sort(key=lambda a:-a['count'])
probes=[]
for y in (3,4):
 for x in (7,8,9):
  for z in (39,40):
   a=cells.get((x,y,z));probes.append(dict(pos=[x,y,z],state=pal[a['state']]if a else None,omitted=a is None))
put('air-components-and-vault-aperture.json',dict(components=components,aperture_probes=probes,interpretation='Explicit saved-air adjacency ONLY. Iron bars are treated as non-air, not collision meshes. This is neither NPC navigation nor proof of no route; slabs, carpets, doors, triggers, fluids, terrain and processors are not simulated.'))
prior=[]
for batch,case,delta in [
 (217,None,'旧完整多层住宅把空酿造台放在底层，居住/温泉/植物阁楼叠层；本例地下竖向进入、洞道连接两个受控工作空间，有原始带物品酿造NBT与陷阱。不同在整体组织，不能仅凭设备改动判新建筑。'),
 (192,'F03','旧完整公共浮岛亭无封闭工作室，酿造台在抬高木柱上且为空；本例是地表入口—深竖井—地下洞道—两个实验空间的组织。仍须独立评估机关城人类NPC适用性，不能把旧亭重新计数。')]:
 path=P.parent/f'research-20261104-smithy-{batch}'/'manual-review.json';doc=ld(path)
 item=doc if case is None else next(a for a in doc['cases']if a['id']==case)
 prior.append(dict(batch=batch,case=case,binding=bind(path),preserved_complete_case_record=item,actual_reading_this_turn='Own seven spatial dimensions and all limitations fully read. Historical source PNG/NBT were not reopened; nested comparisons are preserved evidence, not new reading.',current_whole_difference=delta,recount=0,old_status_preserved=True))
put('prior-whole-comparison.json',dict(comparisons=prior,scope='217 own case and 192 F03 only; no claim to reread nested families. 165/272/666/269/277 remain exclusions or old evidence, not new credit.'))
archive=s['candidates'][0]['archive_binding'];assert bind(archive['path'])==archive
resource_bindings=[]
with ZipFile(archive['path'])as z:
 for i,a in enumerate(s['candidates'],1):
  raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];assert read(raw)==ld(P/f'F{i:02d}-original.json')
 for item in ld(P/'direct-context.json')['resources']+ld(P/'loot-original-full.json'):
  raw=z.read(item['member']);assert raw.decode('utf-8')==item['text'];assert json.loads(item['text'])==item['json']
  resource_bindings.append(dict(member=item['member'],sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
put('resource-verification.json',dict(archive=archive,members=resource_bindings,nbt_decodes_equal=True,context_and_loot_text_equal=True,reading_chronology='direct-context.json loot_not_fully_read=true describes preparation only. Subsequently all six loot JSONs were fully read and saved in loot-original-full.json; this does not imply generated inventory or native pickup. sources.json actual_visual_reading=false is inherited prefilter metadata; actual 23-image review is separately recorded below.'))
protected=[]
for a in ld(P/'protected-before.json')['files']:
 before=a['before288'];after=bind(before['path']);protected.append(dict(before=before,after=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-after.json',dict(files=protected,all_unchanged=all(a['unchanged']for a in protected),sessions_written=False,assets_written=False))
images=[bind(p)for p in sorted(P.glob('*.png'))];assert len(images)==23
put('actual-image-reading.json',dict(images=images,actually_viewed_count=23,scope='F01 all 10 layers; F02 all 48 layers; both wholes, joined whole, four horizontal cuts, and one two-plane vertical section. All viewed in this chat before compaction.',limitations='Class colors and full-cube projection only; not source textures, native lighting, transparent/slab/wall collision or entity rendering. Image count is not building count.'))
review=dict(batch=288,case='MutantMore derelict laboratory: one entrance + one underground template, one complex at most',status='ORIGINAL_COMPOSITE_SPATIAL_STUDY_RECORDED_HOLD_COMPLETENESS_AND_RELEVANCE_ZERO',
 task_scope=dict(file='/Users/a15356015027/Desktop/code x提示词/cod3.txt',physical_line=1132,npc='11 墨机子',location='机关城外围实验室',relevance='地下实验空间、材料与危险设备分隔可供研究；原作化学废墟并非已完成的机关城人类NPC实验室。没有原生付款/齿轮任务/木犬奖励回执。'),
 sources=[dict(member=a['member'],archive=a['archive_binding'],nbt_sha256=a['nbt_sha256'],size=a['size'],DataVersion=a['DataVersion'],stored=a['stored'],nonair=a['nonair'],air=a['air'],unknown=a['unknown'],block_entities=a['block_entities'],entities=a['entities'])for a in s['candidates']],
 seven_dimensions=dict(
 layout='地表9×10×11石塔入口，经相对(-17,-48,2)的26×48×45地下主体进入深井。地下东北石砖主实验室约x17..25,z0..20，西南深板岩工作/陷阱室约x0..13,z35..44。两者间有显式空气洞道而非连续自带完整砌体走廊。不可把入口、井、洞道及两室分算多个建筑。',
 proportion='合并声明包围盒26×58×47仅表示模板边界。入口占地小于地下横向展开，48格深主体主导竖向比例；井y11..24仅保存空气，无非空气踏步与井壁。体积大量省略位置并不等于空气或墙，不据外盒认定完整地下体量。',
 facade='入口普通石砖、凿制石砖、连接墙柱及阶梯檐口构成窄塔；北侧封闭铁门与墙上拉杆，铁栏窗。地下两个工作室的砌体和栏杆组织与地表小入口形成控制层级；未见原生中文店招、售货柜台或NPC服务入口。',
 roof='地表石砖墙/楼梯/板构成层叠收口，不是中式木屋瓦顶。地下砌筑工作室有自身顶面与局部高位机关；中段竖井周边依赖未保存地形，不能用黑色省略区补成完整岩盖。未模拟处理后坍损或地表植被。',
 materials='主室石砖、紫地毯、铁栏与酿造台；深室深板岩砖/墙/板、灯笼、蛛网、容器与水/岩浆/活塞，表达危险实验分区。两个酿造台有Fuel20/BrewTime0及带BrewingProgress:1原始物品NBT，但仅为保存库存，不是配方运行或材料付款。无熔炉/高炉/铁砧/锻造台/砂轮，不能作为铁匠样本。',
 circulation='北侧拉杆(5,5,3)与封闭铁门(4,4..5,4)状态已读；未运行电路。顶端井段有绕柱半砖，y11..24无连续建造踏步；没有梯子。上井服务点至主酿造服务点有75步六邻显式空气链，仅为空气拓扑。主室至深室服务点无同类空气链；深室x8,y3..4,z39..40铁栏隔开明显洞口，不能据此宣布NPC绝对不可达或安全路线已验收。绊线/喷射器、按钮、活塞与流体原状态分别保存。',
 terrain='入口根jigsaw采用WORLD_SURFACE_WG、absolute0、size3/maxdistance80、terrain_adaptation none；两个池均single/rigid且各只有一个加权来源。父down_west aligned与子up_west同west顶向，推导零旋转偏移(-17,-48,2)，保存位置无重叠；未执行原生拼接、地形高度/埋深/碰撞/处理器。没有道路池接头，不宣称已接道路。'),
 original_functional_states=dict(entrance='关闭铁门open=false/powered=false，拉杆powered=false；原接头final_state为deepslate_brick_wall，仅在合成示意图替换两个标记。',
 main_room='工作台(18,1,11)、满水炼药锅(24,1,15)、药剂箱(24,1,11)、酿造台(24,2,13)保存两份incomplete_formula_y。东向喷射器(17,1,10)，y2,z10两端绊线钩x18/24及五段线x19..23附着且未触发；掉落表配置毒/缓慢/伤害喷溅药水，不是已经生成的喷射库存。',
 deep_room='酿造台(3,4,38)保存一份incomplete_compound_z；墙/地毯/主箱/高位活塞箱分置。木牌(3,4,41)仅IV，其余空。按钮(7,5,41)未按下；水源(5,7,36)、岩浆(11,7,38)、两组向下伸出粘性活塞及一组未伸出东向活塞、南向普通活塞原状态已逐项保存。',
 loot='六份掉落JSON全部读完，记录原始文本及哈希；主箱与药剂箱存在多次rolls，不能用单次物品清单代替概率规则。所有箱/喷射器BE只有LootTable引用无现成Items或seed。装备/奖励/原生获取/注册均未验。',
 processor='七个有序规则组：石砖.5苔石砖、苔石砖.15裂石砖、深砖墙.25圆石深板墙、深砖.5裂深砖、磨制深板岩.25深板岩瓦、磨制安山岩板.2空气、紫地毯.2苔藓地毯。特别是踏步可被移除；未执行随机规则或推算成固定最终比例。'),
 actual_reading=dict(full_palettes=[52,84],block_entities=[1,10],source_entities=[0,0],entrance_state_matrix_positions=990,underground_critical_matrix_positions=458,full_layers_viewed=[10,48],images=23,context_jsons=5,loot_jsons=6,underground_all_56160_positions_claimed_read=False,old_wholes='217 own seven dimensions/all limits; 192 F03 own seven dimensions/all limits, original source images not reopened.'),
 deduplication=dict(historical_cached_pairs=666,exact_nbt_role_or_occupancy_matches=[[],[]],earlier_machine_only_batches=[198,200],earlier_machine_screen_recount=0,bounded_novelty_only=True,whole_comparisons='prior-whole-comparison.json preserves complete old case records and current structural differences; no new reading credited to nested historical cases.'),
 learned_principles=['小型地表入口与大地下空间以单一可核对接口联系，可减少地表体量，同时必须另验安全下行、返程与道路接合。','化学工作台、材料容器和危险机构可通过分室、栏杆与高差表达层级；不能把这些装饰关系替代材料来源、付款和实际交互逻辑。','研究原设计时必须保存处理器对踏步的潜在破坏、未知地形及陷阱，不可为符合目标偷偷补路或去除危险后声称原稿如此。'],
 limits=['本轮只研究固定本地来源，未复制制作或修改任何专业建筑、模型、贴图或共享Jar。','这是一项完整两模板案例的空间阅读，不等于已证实独立完整可用建筑；中段竖井/地形与通路证据不足，且化学废墟对墨机子机关实验室仅部分相关，正式相关参考暂记0。','两模板不是两个建筑，23图、11BE、设备、洞道、工作室、NBT指纹和空气组件均不作语义信用。','未运行Java、游戏、Gradle、原生拼装、电路、酿造、寻路、配方、付款、掉落生成、指南针或中文任务验收。','未修改声音、亮度、焦点、屏幕、电源、游戏进程、用户存档、主清单、ownership、pending、共享session或Git。','不重复269首次277辅助信用；273/275仍由主协调独立审查。本轮无Main实际图片/源码验收，不凭元数据消息算验收。','COD4既有已接受153/缺847保持旧观察，NPC累计未知；不足1000不新制作，不报全部完成或10小时达成。'],
 new_composite_case_spatial_readings=1,complete_qualifying_whole_verified=False,new_qualifying_reference_proposal=0,formal_credit_added=0,old269_carry_added=0,tasks_deleted=0,all_tasks_complete=False)
put('manual-review.json',review)
put('active-checkpoint.json',dict(batch=288,status=review['status'],manual_review=bind(P/'manual-review.json'),previous_receipt=bind(P.parent/'research-20261104-smithy-287/RECEIPT.json'),new_composite_case_spatial_readings=1,new_qualifying_reference_proposal=0,formal_credit_added=0,COD4_accepted_old_observation=153,COD4_gap=847,NPC_cumulative=None,tasks_deleted=0,session_written=False,next='本例留作完整空间阅读但适用性/完整通路HOLD0；不重复两模板或旧165/272/269/277。选择新的直接相关完整工坊/NPC建筑，先查全部缓存与语义历史，保持1000门槛。'))
checks={
 'frozen_archive_bound':bind(archive['path'])==archive,
 'two_original_nbt_decodes_equal':True,
 'eleven_direct_json_resources_bound':len(resource_bindings)==11,
 'source_sizes_and_counts':[(a['stored'],a['nonair'],a['air'],a['unknown'])for a in s['candidates']]==[(471,380,91,519),(4012,2240,1772,52148)],
 'palettes_52_84':len(ld(P/'F01-original.json')['palette'])==52 and len(pal)==84,
 'interfaces_exact':ld(P/'assembly-interface.json')['child_origin_relative_to_parent']==[-17,-48,2] and ld(P/'assembly-interface.json')['no_stored_position_overlaps'],
 'midshaft_no_saved_nonair':all(a.get('nonair',0)==0 for a in ld(P/'F02-layer-counts.json')if 11<=a['y']<=24),
 'air_component_sizes':sorted(a['count']for a in components)==[1,1,1,1,1,1,3,62,1701],
 'air_path_not_navigation_75':ld(P/'air-adjacency-not-navigation.json')[0]['step_count']==75,
 '23_images_actually_read_registry':len(images)==23,
 'full_prior_records_preserved':len(prior)==2,
 'all_eight_protected_inputs_unchanged':len(protected)==8 and all(a['unchanged']for a in protected),
 'no_credit_no_deletion':review['formal_credit_added']==review['new_qualifying_reference_proposal']==review['tasks_deleted']==0,
}
assert all(checks.values()),checks
put('verification.json',dict(checks=checks,passed=len(checks),native_tests_run=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=288,status='SEALED_COMPOSITE_SPATIAL_READING_HOLD_ZERO',files=files,checks=len(checks),new_composite_case_spatial_readings=1,new_qualifying_reference_proposal=0,formal_credit_added=0,all_tasks_complete=False))
for a in ld(P/'RECEIPT.json')['files']: assert bind(a['path'])==a
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
