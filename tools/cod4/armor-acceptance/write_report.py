"""Build an evidence index without claiming headless tests are graphical/multiplayer acceptance."""
from pathlib import Path
import datetime,difflib,hashlib,json,re
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];E=BASE/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((E/'final-current-receipt.json').read_text())
assert receipt['exit_code']==0 and receipt['completed_required_tests']==63 and receipt['inputs_unchanged']
assert receipt['log_sha256']==sha(E/'final-current.log')
assert all(sha(ROOT/path)==digest for path,digest in receipt['inputs_sha256'].items())
assert json.loads((E/'test-inventory.json').read_text())['count']==63
source=ROOT/'src/main/java/com/dynasty/expansion/EquipmentBehaviors.java'
qi=ROOT/'src/main/java/com/dynasty/expansion/QiConstitution.java'
frozen=json.loads((E/'frozen-source-sha256.json').read_text())
assert all(sha(p)==frozen[str(p.relative_to(ROOT))] for p in (source,qi))
source_files=[source,qi,ROOT/'src/main/java/com/dynasty/expansion/SummonedGuard.java',ROOT/'src/main/java/com/dynasty/DynastyMerit.java',ROOT/'src/main/java/com/dynasty/DynastyKeju.java']
behaviors={
'cloth':['满饱食移动速度','睡醒后的限时攻击加成','奔跑时返还部分消耗'],
'bamboo':['降低摔落距离','竹林奔跑加速','概率反射箭矢'],
'leather':['潜行加速','带冷却的潜行攻击加成','潜行脚步静音'],
'brocade':['大臣来源功勋加成','脱战回复','科举答题时间加成'],
'bronze':['受击概率盾音','格挡后的限时护甲','减免朝廷士兵伤害'],
'general':['抗击退','静止蓄势护甲','静止蓄势攻击'],
'silver':['对亡灵增伤','夜间增伤','夜间按实际伤害回血'],
'jade':['附魔等级消费累计返还','满血增伤','满血加速'],
'cinnabar':['缩短有限负面状态','净化自身及附近友方煞气','解除中毒'],
'dragon_scale':['水中补气','水中增伤','水中护甲'],
'phoenix':['火伤免疫','受火后的短暂加速','有冷却的近敌火环'],
'qilin':['幸运','概率整击格挡','低血量长冷却护盾'],
'sea_silk':['水中加速','游泳属性','水中海豚恩惠与回血'],
'xuantian':['四种属性加成','对Boss增伤','削弱附近正在攻击自己的非Boss'],
'sky':['下降减速','空中增伤','摔落免疫及可撤销跳跃II'],
'dark_iron':['抗击退','静止受击积累共享蓄势','消耗五点蓄势增伤'],
'draco_king':['水中补气及夜视','有租期的虾兵','同租期虾兵蟹将配对'],
'xuanwu':['完美格挡与单次反击','提高反击增伤','完美格挡保命壳，共享长冷却'],
'zhuque':['火伤免疫及夜视','火属性伤害加成','共用长冷却的致死保护'],
'qinglong':['蓄满普攻共享连击增伤','五连击波及有限冷却','连击波回复与短暂真气'],
'baihu':['对非Boss击退','冲刺打击冷却','冲刺打击破势'],
'beidou':['移动加速','近期移动增伤','连续奔跑十步、四刻无敌、有限冷却'],
'tiangang':['白天增伤','白天击杀回血','正午属性与白天阴气免疫/清除'],
'disha':['夜间增伤','夜间击杀回血','午夜属性与夜间阳气免疫/清除'],
'taiyi':['四种属性加成','现有技能冷却减少','等级门槛回血与长冷却'],
'ziwei':['幸运','概率暴击并打开短窗口','暴击窗口中的增伤'],
'hunyuan':['昼夜不同属性','阴阳真实相消后的短暂平衡','五点蓄势换短暂真气及冷却'],
'hongmeng':['四种属性加成','对镇渊增伤','共用长冷却的致死保护'],
}
specific={
'cloth':['window_cloth'], 'bronze':['window_bronze','unworn_bronze_cannot_prestore_window'],
'phoenix':['window_phoenix','existing_phoenix_armor','existing_phoenix_ring','other_fire_set_cannot_prestore_phoenix_window'],
'ziwei':['window_ziwei'], 'sky':['existing_sky_potions'], 'qilin':['existing_qilin'],
'brocade':['existing_brocade'], 'cinnabar':['existing_cinnabar'],
'beidou':['existing_star_steps','star_immunity_reads_live_gear','existing_modifiers'],
'xuanwu':['existing_perfect_guard','existing_native_guard','existing_native_guard_controls','xuanwu_counter_cannot_transfer_to_duck','owned_counter_original_damage_once'],
'draco_king':['existing_guard_lease','existing_blocked_guard','existing_guard_pair'],
'hunyuan':['existing_hunyuan','existing_qi_pill'], 'qinglong':['existing_qinglong'],
'taiyi':['existing_taiyi'], 'zhuque':['existing_last_stand','native_last_stand_save_swap_owner'],
'hongmeng':['native_last_stand_save_swap_owner'], 'tiangang':['QiConstitutionGameTests'], 'disha':['QiConstitutionGameTests'],
}
sets=[]
for name,tiers in behaviors.items():
 refs=[]
 for p in source_files:
  for line,text in enumerate(p.read_text().splitlines(),1):
   if '"'+name+'"' in text:refs.append({'path':str(p.relative_to(ROOT)),'line':line})
 sets.append({'id':name,'reviewed_2_3_4_piece_mechanisms':dict(zip(['2','3','4'],tiers)),
 'implementation_locations':refs,'code_reviewed':True,
 'headless_native_equipment_matrix':{'passed':True,'test':'matrix_'+name,'sequence':[2,3,4,3,2,0],
 'assertions':['实际ServerPlayer/LivingEntity装备变更','七种属性重复刷新不叠加','卸装恢复基线','外部高阶夜视药水保留','另一离线服务端测试角色属性不变'],
 'does_not_prove':'没有逐档触发所有条件行为；不能当作3项实机行为验收'},
 'additional_tests':specific.get(name,[]),'all_three_live_behaviors_accepted':False,'human_multiplayer_accepted':False})
failures=[]
for line,text in enumerate((E/'before.log').read_text().splitlines(),1):
 m=re.search(r'dynasty_armor_qa\.(\S+) failed! (.*)',text)
 if m:failures.append({'test':m[1],'assertion':m[2],'log_line':line})
assert len(failures)==7
baseline=BASE/'.work/before-EquipmentBehaviors.java'
(E/'EquipmentBehaviors.patch').write_text(''.join(difflib.unified_diff(baseline.read_text().splitlines(True),source.read_text().splitlines(True),fromfile='before/EquipmentBehaviors.java',tofile='after/EquipmentBehaviors.java')))
supplement=E/'armor-references.json'
research=json.loads(supplement.read_text()) if supplement.exists() else {}
count=research.get('summary',{}).get('accepted_implementation_sites',0)
report={
 'scope':'COD4-4 28套盔甲代码复核；没有模型/贴图/建筑/GUI改动',
 'updated_at':datetime.datetime.now().astimezone().isoformat(),
 'status':'正式修复及63项自动测试完成；专属研究已事后补足1000处；84项实机/真人验收独立保留' if count>=1000 else '正式修复及63项自动测试完成；专属研究与84项实机/真人验收独立保留',
 'production_files':[{'path':str(source.relative_to(ROOT)),'changed':True,'before_sha256':sha(baseline),'after_sha256':sha(source)},
                     {'path':str(qi.relative_to(ROOT)),'changed':False,'sha256':sha(qi),'note':'读取复核并复用四项体质回归，保留其他聊天已有未跟踪文件'}],
 'fixes':[
  {'issue':'布衣休息、青铜格挡、凤羽加速、紫微暴击窗口失去三件门槛后仍保存，可通过再穿回激活','fix':'失去门槛即撤销瞬时授权；青铜/凤羽仅在来源装备达标时开窗','regressions':['window_cloth','window_bronze','window_phoenix','window_ziwei','unworn_bronze_cannot_prestore_window','other_fire_set_cannot_prestore_phoenix_window']},
  {'issue':'双钺移除副手后仍留反击，玄武反击也能经换装到双钺保留','fix':'记录原反击来源并在刷新和实际增伤入口核验；单次消费同时清理来源','regressions':['duck_offhand_revokes_counter','xuanwu_counter_cannot_transfer_to_duck','owned_counter_original_damage_once'],'compatibility':'未标来源的旧三秒临时反击窗失效；永久冷却、装备ID和存档数据不清除'},
  {'issue':'北斗四刻无敌在装备变更事件之前不检查实时件数','fix':'伤害接受入口同时要求实时四件','regressions':['star_immunity_reads_live_gear']}],
 'verification':{
  'completed':True,'latest_run':receipt,'latest_log':'tools/cod4/armor-acceptance/evidence/final-current.log',
  'previous_core_comparison':{'before_total':60,'before_failed':7,'after_passed':60,'before_failures':failures,'before_log':'tools/cod4/armor-acceptance/evidence/before.log','after_log':'tools/cod4/armor-acceptance/evidence/after.log'},
  'initial_fixture_run_excluded':'initial-fixture.log 中4项受ServerPlayer出生保护影响；修正为先经过61次原生tick后重新获得7项产品复现，不将夹具失败冒充产品缺陷。',
  'test_types':[
   {'count':28,'kind':'普通ServerPlayer原生装备检测及属性/药水回退矩阵','not':'84项全部条件动作或GUI验收'},
   {'count':11,'kind':'原ExpansionGameTests的FakePlayer事件/辅助函数回归','covers':'幂等、归属、保命、药水、麒麟、步伐、火焰、朱砂、科举、真气；不是两名真人'},
   {'count':9,'kind':'原有普通ServerPlayer专项：1太乙、6装备格挡/蓄势/召唤、2原生格挡输入','not':'真人网络客户端'},
   {'count':4,'kind':'复用QiConstitutionGameTests原生效果及装备/昼夜事件回归','not':'双客户端免疫反馈验收'},
   {'count':11,'kind':'本次专项：四窗口、两反击撤销、北斗实时件数、原生Boss来源伤害/NBT冷却、正向反击一次结算、两未穿装备禁止预存窗口','detail':'混合原生hurt/格挡/装备/NBT读写与明确构造的事件级断言，不把全部用例称作完整原生输入验收'}],
  'ordinary_serverplayer_fixture_tests':52,'fakeplayer_fixture_tests':11,
  'test_inventory':'tools/cod4/armor-acceptance/evidence/test-inventory.json',
  'completion_log_markers':[{'line':n,'text':text.strip()} for n,text in enumerate((E/'final-current.log').read_text().splitlines(),1) if 'All 63 required tests passed' in text or 'BUILD SUCCESSFUL' in text],
  'frozen_sources':'tools/cod4/armor-acceptance/evidence/frozen-source-sha256.json',
  'isolated_output_root':'tools/cod4/armor-acceptance/.work','shared_build_outputs_changed':False,
  'latest_snapshot_includes_main_agent_launch_changes':True,'launch_specific_suite_run':False,
  'gui_client_launched':False,'true_two_human_players_tested':False},
 'reference_gate':{
  'required':1000,'accepted_armor_specific_sites':count,'shortfall':max(0,1000-count),'met':count>=1000,
  'original_status_corpus':{'path':'docs/cod4/audit-20261022/status-reference-1000.json','verified_pinned_excerpts':1000,
   'verification':'tools/cod4/armor-acceptance/evidence/references.json',
   'boundary':'包含状态施加/解除、伤害免疫及fireImmune静态注册等宽泛上下文。虽已核对哈希/行号/摘录，不能因此计为本次换装窗口、反击归属、持久冷却1000门槛。'},
  'five_initial_followup_ranges':'仅为五段相关补读，不是1000处专属研究，且有同一方法重叠；不会直接按五处追加。',
  'process_exception':'既有修复发生于本次专属1000门槛满足之前。保留已复现修复和自动测试证据，不以事后补读冒称制作前门槛已满足；按用户最新指示不再追加正式代码改动。',
  'supplement':'tools/cod4/armor-acceptance/evidence/armor-references.json' if supplement.exists() else None,
  'supplement_status':research.get('summary',{}).get('status','正在从现有外部源码补读、筛选、去重；尚未计入有效实现'),
  'supplement_summary':research.get('summary',{}),
  'synthesis':'tools/cod4/armor-acceptance/evidence/armor-research-summary.json',
  'scope_boundary':'接受数仅为已逐段研究的保守下限；候选、未读片段、注册或外观字段不能补数；没有穷尽外部源码。'},
 'sets':sets,
 'remaining_acceptance':[
  {'task':'28套每套2/3/4件的84项条件行为，全部真实客户端操作与卸装','status':'未全部验收；装备矩阵不作替代'},
  {'task':'临时效果、蓄势、反击、召唤物、无敌帧在第一/第三人称及换装时的表现','status':'主代理GUI验收；本报告只证明所列服务端断言'},
  {'task':'两名真实玩家状态/召唤物/冷却归属、换装同步及重复装备','status':'未验收；FakePlayer及离线ServerPlayer不能替代'},
  {'task':'Boss实战完整300秒限制，死亡重生、登出重登、服务器重启后的保命冷却','status':'仍待实际流程；已有Boss来源原生hurt、装备切换及NBT save/load断言'},
  {'task':'1000处本次相关外部实现研究','status':'门槛未满足' if count<1000 else '现有独立研究已补足；不能追溯宣称制作前完成','accepted':count,'missing':max(0,1000-count)}],
 'coordination':{'formal_java_changes_frozen':True,'other_files_requiring_changes':[], 'todo_modified':False,'game_content_removed':False,'new_chat_created':False,'live_armor_acceptance_owner':'Herschel；本账本不替代其真实双客户端、长冷却及死亡绕过核查','migration_research_owner':'Kepler主账本；本分工仅贡献独立研究账本，不写迁移生产新类','tests_rerun_during_final_research':False},
 'subsequent_research_queue':{
  'topic':'真实旧档registry/持久数据迁移',
  'reported_by':'主协调2026-10-23消息；本分工尚未独立复查旧档日志或进行迁移',
  'reported_gap':'9/11旧档独立副本载入时quest_ledger/healing_talisman缺registry被移除，实际背包quest_ledger丢失；历史d0007965将healing_talisman替换为vajra_talisman，quest_ledger改FTB/手册但未remap。',
  'reported_evidence':['build/cod4-old-world-20261023/run-01.log:229-247','docs/cod4/audit-20261022/old-world-acceptance'],
  'required_before_code':1000,'accepted_registry_migration_sites':0,
  'cross_reference_boundary':'盔甲研究643/651是冷却NBT读写，652为装备资源恢复，636为登录暂态属性恢复；已读但没有旧registry ID到新ID转换，全部不计迁移门槛。',
  'reviewed_persistent_field_migration_crosslinks':[{'armor_candidate_index':2728,'review_status':'已逐段阅读，旧字段到新字段的实际转换','mechanism':'AccessoriesHolderImpl.read使用dfuKeysCarrier将AccessoriesContainers/CosmeticsShown/LinesShown/EquipControl四旧键改为新键后解码，重建合法槽并清缓存','registry_id_remap':False,'independent_migration_gate_accepted':False}],
  'implementation_status':'已按用户要求联系Kepler，独立研究Clone死亡白名单、跨死冷却与旧物品替代；不在本写集实现MissingMappings，不提前修改代码。',
  'contribution_directory':'tools/cod4/armor-acceptance/migration-research',
  'count_boundary':'本报告的0指尚未合并确认的独立registry迁移贡献数，不代表Kepler主账本数；盔甲1000不自动计入迁移门槛。'},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(E.iterdir()) if p.is_file()},
}
assert sum(x['count'] for x in report['verification']['test_types'])==63
out=ROOT/'docs/cod4/audit-20261022/armor-acceptance.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Wrote',out,'63/63 complete; research',count,'/1000; 84 live scenarios and real multiplayer remain pending.')
