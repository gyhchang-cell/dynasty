"""Summarize completed native receipts, keeping failures and fixture limitations visible."""
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/cod4/audit-20261022/interaction-acceptance'
main=json.loads((OUT/'run6-receipt.json').read_text());extra=json.loads((OUT/'run8-receipt.json').read_text())
assert main['native_finished'] and extra['native_finished'] and main['inputs_unchanged'] and extra['inputs_unchanged']
a=json.loads((OUT/'run6-observations.json').read_text());b=json.loads((OUT/'run8-observations.json').read_text());rows=a+b
placements=[r for r in rows if r['kind']=='placement'];walks=[r for r in rows if r['kind']=='entrance_walk'];ids=sorted({r['id'] for r in placements})
assert len(ids)==15 and len(placements)==120 and len(walks)==60
assert extra['required_all_pass']==4
clock={r['id']:r['elapsed_world_ticks'] for r in a if r['kind']=='real_clock_generic'}
clock.update(ancient_well=next(r['elapsed_world_ticks'] for r in a if r['kind']=='real_clock_well'),puzzle_box=next(r['elapsed_world_ticks'] for r in a if r['kind']=='real_clock_puzzle'))
for id in ['wayside_tea_stall','ghost_market_boat','mortuary_room']:clock[id]=next(r['elapsed_world_ticks'] for r in a if r['kind']=='real_clock_scenes')
clock['sword_scar_wall']=max(r['elapsed_world_ticks'] for r in b if r['kind']=='real_clock_sword_step')
assert set(clock)==set(ids)
fail_ids=[r['id'] for r in a if r['kind']=='internal_direct_use_range' and r['changed']]
result={'status':'NATIVE_ACCEPTANCE_COMPLETED_WITH_TWO_UNRESOLVED_REQUIRED_FAILURES','date_client':'2026-10-23','minecraft':'1.20.1','forge':'47.4.10','java':'17.0.20',
 'registered_distinct_interactions':ids,'main_suite':{'receipt':'run6-receipt.json','required_total':sum(int(n) for _,n in main['test_batches']),'required_failed':main['required_failed'],'failures':main['failures']},
 'additional_suite':{'receipt':'run8-receipt.json','required_passed':4,'required_failed':0},'combined_required_total':43,'combined_passed':41,'combined_failed':2,
 'coverage':{'production_piece_placement_shape_collision_cases':120,'entrance_continuous_native_walk_paths':60,'scene_two_owner_spawn_cases':12,'remote_native_packet_sites':15,'near_native_packet_positive_sites':14,'near_sword_wall':'positive tested via production moonlight context and native block use; no packet-positive assertion for this time-gated case','eye_distance_boundary_packet_cases':30,'forged_hit_packet_rejections':15,'real_clock_completion_ticks':clock,'furnace_edges':['empty','full_output','burn_time_1601','outside_search_range_4','valid_payment_burn_time_1600'],'physical_waterwheel_shared_personal_rewards_isolated':True},
 'findings':[{'id':'INTERNAL_DIRECT_USE_RANGE','status':'REPRODUCED_REQUIRED_FAILURE','affected_ids':fail_ids,'detail_zh':'9种通用互动的内部BlockState.use调用可在30格外启动进度。15种远程ServerboundUseItemOnPacket均被拒绝，另有近距正对照与6.01/5.99格眼部距离边界；不是已证实的网络远程利用。','evidence':['run6.log','run6-observations.json']},
 {'id':'LEGACY_SWORD_FIXTURE_FOCUS_LOST','status':'UNRESOLVED_REQUIRED_FAILURE','detail_zh':'既有复制测试actualGroundedNativeAirSwingsMatchThreeStepsAndOriginalRewards在平面测试夹具中第一式时DanceFocused变false，Count未推进；保留失败，未归因为正式游戏缺陷。现有药庐原生piece的侧方空地流程，真实800/1600/2400 tick三式及双ServerPlayer个人奖励另已通过。','evidence':['run6.log','run8-observations.json']},
 {'id':'DIRECT_FRONT_DANCE_AUTO_STEP','status':'POSITIONAL_LIMITATION_REPRODUCED_ALTERNATIVE_VERIFIED','detail_zh':'architecture给出的局部(13,1,27)是可达接近点，不保证可完成剑舞。面前第三次北移会原生自动踏上13/16格石壁碰撞，高度81→81.8125超过动作容差而重置。改从现有空地局部(15,1,27)开始，无改建筑，实际2400 tick三式与一次性奖励通过。','evidence':['run7.log','run7-observations.json','run8.log','run8-observations.json']}],
 'limits':['Two constructed native ServerPlayer identities and NBT/clone checks, not human authenticated multiplayer.','Existing structure piece postProcess and chunk clips are real; biome frequency, terrain selection and full Structure generation are not claimed.','120 collision observations and60 continuous paths use native physics; no visual screenshots in headless server.','Real-clock cases use actual accelerated GameTestServer ticks. Historical copies explicitly seed clock fields only for legacy/negative/clone checks.','Playerless harness keeps production-scene chunks forced and waits80 ticks before NPC use; earlier untracked-NPC fixture failures are preserved in run3/run4/run5 logs.','No architecture was newly created; no1000-building quota completion claimed.','Ecology material acquisition in tomb/ruin/cave tags remains outside this interaction placement/collision/ownership run.'],
 'formal_java_changed':False,'assets_changed':False,'todo_changed':False,'new_buildings_created':0,'frozen_inputs_manifest':'frozen-source-sha256.json'}
(OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
with (OUT/'interaction-matrix.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['id','orientation','style','world_position','approach_world','ground_support','collision_two_states','native_entrance_path_steps','walk_copy_entrance_world','walk_copy_goal_world','real_completion_ticks','direct_internal_far_guard'])
 for r in placements:
  if r['lit']:continue
  path=next(p for p in walks if p['id']==r['id'] and p['orientation']==r['orientation'])
  w.writerow([r['id'],r['orientation'],r['style'],r['world'],r['approach'],r['supported'],'PASS false/true',path['steps'],path['entrance_world'],path['goal_world'],clock[r['id']],'FAIL' if r['id'] in fail_ids else 'PASS'])
# Preserve all22 architectural follow-up rows and explicitly leave unrelated ecology pending.
source=ROOT/'docs/architecture/continuation-20261022/interaction-native-followup.tsv'
with source.open() as f: follow=list(csv.DictReader(f,delimiter='\t'))
for r in follow:
 r['status']='NATIVE_PASS_WITH_LIMITS' if r['id']!='ecology_materials' else 'NOT_RUN_OUTSIDE_INTERACTION_SCOPE'
 r['native_evidence']='interaction-matrix.tsv;run6-observations.json;run8-observations.json' if r['id']!='ecology_materials' else ''
 if r['id']=='sword_scar_wall':r['status']='PLACEMENT_PASS_DANCE_SIDE_START_PASS_LEGACY_FIXTURE_FAIL'
with (OUT/'architecture-followup-results.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(follow[0]),delimiter='\t');w.writeheader();w.writerows(follow)
(OUT/'report.txt').write_text('COD4-13 原生验收结果（2026-10-23）\n\n主套39项：37通过、2失败；补充套4项：全部通过。合计43项，41通过、2失败。\n15个注册互动均实际完成了原生计时流程，真实tick见result.json；不得把这个结论解释为全部验收全绿。\n\n已完成：120个生产piece放置/选择形状/碰撞状态检查（15×4朝向×2状态）；60条入口到互动的原生连续行走路径；12组场景双服务端玩家实体归属；15项远程网络点击拒绝、14项近距正对照、30项6格边界及15项伪造命中拒绝；风箱5类分支；个人付款/奖励/进度与NBT/克隆检查。\n\n保留失败：\n1. 9种通用互动内部BlockState.use缺少距离兜底，可30格外开始；原生网络包入口没有复现远程利用。\n2. 旧复制剑舞平面夹具在第一式丢失DanceFocused，尚未解释，日志保留。现有药庐侧方空地真实2400 tick剑舞已完成，个人奖励不重复。\n\n另外：正前方接近点会在第三式原生踏上石壁，导致高度容差重置；现有局部(15,1,27)空地可完成，未修改建筑或碰撞。\n\n仅编写了允许的测试和证据目录。无正式Java、资产或原TODO改动；没有制作新建筑。两个ServerPlayer实例代表服务端身份与持久化隔离，不代表真人双人联机。生态材料标签、世界生成选址频率及客户端画面不在本次原生验收结论内。\n\n详细证据：result.json、interaction-matrix.tsv、architecture-followup-results.tsv、run6/7/8日志、对应observations与receipt。\n')
print(json.dumps({'combined_total':43,'passed':41,'failed':2,'registered':len(ids),'real_clock_sites':len(clock),'placement':len(placements),'walks':len(walks)},ensure_ascii=False))
