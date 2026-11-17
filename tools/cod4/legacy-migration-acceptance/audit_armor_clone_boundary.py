"""Read supplied native QA evidence and fix migration ownership boundaries; no runtime writes."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';Q=R/'docs/cod4/audit-20261022/armor-network-acceptance'
paths=[Q/'receipt-death.json',Q/'run-04/result-death.json'];receipt,result=[json.loads(p.read_text()) for p in paths]
assert receipt['productionSha256']==result['productionSha256']
assert receipt['status']=='PASS_WITH_STATED_SCOPE' and result['passed']
assert all(c['passed'] for c in result['checks'])
keys=['lastStand','cicada','guardsUntil','guardGeneration'];events=[]
def retained(s):
 match=re.search(r'dynastyCod4:\{([^{}]*)\}',s);assert match,s
 return {k:int(v) for k,v in re.findall(r'(lastStand|cicada|guardsUntil|guardGeneration):(-?\d+)L',match[1])}
for e in result['actualRespawns']:
 assert e['wasDeath'] and e['event']=='actual Forge PlayerEvent.Clone'
 before,after=retained(e['originalRawForgeData']),retained(e['newRawForgeData']);assert before==after
 events.append(dict(uuid=e['uuid'],tick=e['tick'],retained_present_keys=before,all_present_values_identical=True,missing_key_is_not_claimed_present=True))
assert len(set(e['uuid'] for e in events))==2
assert result['nativeC2S']=={'host':True,'peer':True}
assert set().union(*(e['retained_present_keys'].keys() for e in events))==set(keys)
source_paths=[R/'src/main/java/com/dynasty/expansion/EquipmentBehaviors.java',R/'src/main/java/com/dynasty/expansion/ContentProgress.java']
source=[]
for p in source_paths:
 raw=p.read_bytes();lines=raw.decode().splitlines();start,end=(26,40) if p.name=='EquipmentBehaviors.java' else (69,71)
 source.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(raw).hexdigest(),start_line=start,end_line=end,context='\n'.join(lines[start-1:end])))
record=dict(status='verified_supplied_native_receipt_not_new_test_run',external_reference_credit=0,production_change=False,qa_artifacts=[dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],production_sha256=result['productionSha256'],scope=result['scope'],actual_clone_events=events,existing_source_context=source,guardrails={'never_write_or_replace':['PlayerPersisted','PlayerPersisted.dynastyCod4','DynastyArmyV1','school/slot/secret owners already responsible for their own containers'],'root_policy':'only source-audited named permanent root fields and historical quest keys, with correct tag types and detached Tag.copy; do not copy whole getPersistentData()','do_not_generalize':'a timer can intentionally survive death inside its existing owner. Preserve saved deadlines through existing handlers; this does not justify copying transient root immunity/counterattack/charge/cooldown grants.','regression_expectation':'after minimal root fix, all existing saved deadline/generation values and before-original-deadline no-proc remain unchanged; new handler must never reset or rebase these deadlines'},limits=[result['semantics']['limitations'],'Receipt proves these four saved keys across observed events, not all armor/whole pack/permanent roots.','No independent native rerun performed by migration researcher. Local QA/source review gives zero toward external1000.'])
(O/'armor-clone-boundary.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(O/'armor-clone-boundary.md').write_text('''# 根级永久进度修复与已有盔甲Clone的职责边界

已只读核验两份主协调提供的原生证据及源码：两个UUID、三次真实Forge死亡Clone事件，host/peer均原生C2S重生；已有键lastStand、cicada、guardsUntil、guardGeneration在对应事件前后数值完全一致。不存在的键不当作实际写入0。原deadline前保命不再次proc、守卫租约与generation不刷新，均有通过回执。

EquipmentBehaviors.saved访问PlayerPersisted.dynastyCod4；ContentProgress.clone现已复制PlayerPersisted。新根级修复不得put/覆盖/合并这两个容器，也不得reset/rebase其deadline。只有来源已审定的永久root字段和历史任务键可用准确类型逐项Tag.copy。merit保留不能成为泛拷root临时免疫、反击、蓄势及计时状态的依据。

证据范围为ce9259、四模组、全新QA世界与供给装备环境；不是真实旧档导入，也未证明所有root永久进度已保留。本次未重跑QA、未写生产代码；本地证据核验不计外部1000研究数。完整artifact/source哈希及精确事件数值见armor-clone-boundary.json。
''')
print(json.dumps({'verified_native_clone_events':len(events),'unique_players':2,'existing_saved_key_families':keys,'source_files_hashed':len(source),'reference_credit':0}))
