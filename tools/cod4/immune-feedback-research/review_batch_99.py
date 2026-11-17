"""Native damage-triggered release and target-wide anti-recapture admission, one whole policy."""
from ledger import B,O,record,verify
import json
r='team-abnormals/endergetic';p='src/main/java/com/teamabnormals/endergetic/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
e='common/entity/eetle/GliderEetle.java';k='endergetic-native-health-loss-grounding-release-and-target-wide-recapture-denial'
record(k,r,[f(e,87,150),f(e,163,235),f(e,295,379),f(e,436,438),f(e,455,474),w('common/entity/eetle/ai/glider/GliderEetleGrabGoal.java'),w('common/entity/eetle/ai/glider/GliderEetleBiteGoal.java'),w('common/entity/eetle/ai/glider/GliderEetleFleeAttackerGoal.java'),w('core/other/EEDataProcessors.java'),f('core/other/EEEvents.java',64,68),f('core/other/EEEvents.java',112,158),f('core/registry/EEEntityTypes.java',49,49),f('core/EndergeticExpansion.java',113,123)],
 '实际Glider注册Grab/Bite/FleeGoal。Grab canUse/continue拒large、target catchingCooldown>0、已Glider乘坐等，tick真startRiding成功才swoop。native hurt super true且living来源/飞行且有乘客，累加max(实际prevHP-newHP-rand0..2,0)，>=16重置累计、记录attacker、makeGrounded80..120及setFlying(false)。同步Flying改变处理立刻removeVehicle并做头顶无碰撞上抬尝试；removePassenger给目标IDataManager cooldown累计+40..50。实际注册trackedData NOPE默认0，server LivingTick每tick减1。冷却内Grab拒绝而Bite可继续正常伤害，groundedAttacker驱动FleeGoal。',
 '完整计1：实际健康损失预算触发解控及目标跨抓取者重抓免疫窗口，不按几套Goal包装/尺寸/随机常量再计。与TF全局allowDismount强制锁乘客不同；Gloam按施术者限制不同，此data附在目标上所有Glider读取。hurt累计只在成功且有乘客飞行时更新，未见add/removePassenger清damageTakenWhileFlying，未触阈值的累计可跨多轮抓取。Grab tick最终startRiding前不重新读cooldown/large，仅依赖goal调度前条件；不能声称无同tick竞争。NOPE表示无客户端同步，不把冷却字段当可见灰字。',
 'Boss拒控及文字节流是两层：目标免再控不等于伤害免疫，也不等于回执防刷屏；最终应用前重验条件，生产一次明确拒控原因，普通体质保持原type9。',
 '完整关键hurt/同步回调/tick/乘客/尺寸helper/三个Goal及冷却消费者、注册callsite已读。Blueprint IDataManager底层存储和bus内部不独立加数；不宣称真两端画面通过，无正式修改。','native_damage_release_recontrol_immunity')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'endergetic-batch99-target-recapture-window','credited_chains':[k],'rationale':'Actual HP-loss grounding ends capture, target-wide timer excludes recapture while normal bite remains admitted. Entire lease admission and teardown one family, not renamed generic hostile mount or sender-owned immunity.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
