"""Native Epic Fight damage qualification/settlement and explicit result loss, not model study."""
from ledger import B,O,record,verify
import json
r='Antikythera-Studios/epicfight';p='src/main/java/yesman/epicfight/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
shared=[f('registry/entries/EpicFightSkills.java',67,77),f('platform/neoforge/event/NeoForgeEntityEvent.java',55,62),f('api/event/impl/VanillaEntityEventHooks.java',178,203),f('world/capabilities/entitypatch/LivingEntityPatch.java',396,405),w('api/event/types/entity/TakeDamageEvent.java'),w('api/utils/AttackResult.java'),f('world/capabilities/entitypatch/player/PlayerPatch.java',484,513),f('world/capabilities/entitypatch/HurtableEntityPatch.java',151,176),f('world/capabilities/entitypatch/LivingEntityPatch.java',665,671),f('world/capabilities/entitypatch/LivingEntityPatch.java',699,717),w('network/server/SPAnimatorControl.java'),w('network/common/AbstractAnimatorControl.java'),f('network/EpicFightClientBoundPayloadHandler.java',86,96),f('network/EpicFightNetworkManager.java',53,57),w('particle/HitParticleType.java')]
ks=[]
k='epicfight-native-guard-resource-break-still-denies-hit-and-cancelled-result-collapses';ks.append(k)
record(k,r,[w('skill/guard/GuardSkill.java'),w('skill/guard/ParryingSkill.java')]+shared,
 '实际注册GUARD/PARRYING工厂；GuardSkill完整onInitiate将TAKE_DAMAGE_INCOME listener接入技能container，已激活且holding本skill才判damageSource位置前方，GUARD_PUNCTURE提前放行。guard检source后先CLASH声+原版server particle snapshot，再penalty累积×impact并consumeForSkill；消费失败只选GUARD_BREAK动作/声音，仍dealEvent取消事件并setResult BLOCKED，计hurtTime/通知攻击方。原生NeoForge Incoming→onDamageIncomes→patch.tryHurt→最终取消hurt。',
 '一个方向+持续持有+递增资源惩罚/破防结算独立拒伤点1。关键：资源不足不意味着当次伤害放行；闪光/声先于支付判定。TakeDamageEvent保存明确BLOCKED，但LivingEntityPatch.tryHurt遇cancel一律构造MISSED，未读getResult；因此最终lastAttackResult丢失了格挡与闪避区分，不能据枚举名推断通知保留。Parrying完整类已读，同一guard家族合并0：成功窗口消耗LAST_ACTIVE=0、重按须>2window重新武装，投射物advanced放宽；多武器动作列表/动作counter不拆数。',
 '拒控reason必须沿最终消费者保留，不能在统一cancel包装中丢成MISS；Boss灰字只随明确免控reason，不随所有格挡/破防或伤害布尔。节流须按拒绝目标而非防御penalty恢复计时。',
 '全文Guard/Parrying与关键原生消费者/支付方法/回放packet已读。同步动作发送tracking实体，client当前world数值id查patch，无UUID/维度/事件序号；原版声音/粒子只读生产点及锚点，未读所有粒子provider/像素。固定版本，只读，无游戏/正式改动，不新增普通体质灰字。','native_guard_refusal_settlement')
k='epicfight-native-impact-guard-recursive-partial-hit-before-outer-refusal';ks.append(k)
record(k,r,[w('skill/guard/ImpactGuardSkill.java'),w('skill/guard/GuardSkill.java')]+shared,
 '实际注册IMPACT_GUARD extends Guard；同原生Incoming listener虚派发guard，爆炸以原amount作impact，advanced资格传super。覆写dealEvent对特殊来源先将来源转EpicFightDamageSource并加runtime UNBLOCKALBE+NO_STUN，再递归player.hurt(amount*damageReducer)，忽略nested boolean；之后setResult SUCCESS或BLOCKED、计hurtTime、改原EpicFight源stun NONE、cancel外层，并可发AIR_BURST/attackBlocked回调。',
 '这是独立的“递归部分结算+外层拒绝”位点1，非换常量的普通guard；内层runtime UNBLOCKALBE防自身重入，NO_STUN仅嵌套链，与Boss免控不同。outercancel并不等于完全免伤；嵌套hurt结果未检查不能证明减伤已经落HP。若传入原本EpicFightDamageSource，efsource复用同实例，runtime tag也可影响后续观察，不是隔离copy。外层设置SUCCESS仍在patch.tryHurt取消分支坍缩成MISSED，故cannot将其当权威免疫/成功receipt。',
 'Boss拒控需要独立结果及不会递归污染来源的reason；不要从外层取消标灰字，保留部分伤害/完全拒绝的差别。任何拒绝闪光/嗡鸣应节流且不暗示普通护甲或体质被Boss规则覆盖。',
 '完整ImpactGuard/基类、显式注册、native incoming consumer、支付及动作回放关键方法已读，无native复现/编译/像素或声音听验；本模组独立实现研究不等于项目修复，不复制动作/模型。','native_partial_settlement_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'epicfight-batch85-guard-final-settlement','credited_chains':ks,'rationale':'资源破防仍拒伤、递归部分hurt再拒外层为2个最终结算位点；PARRYING同基类家族0，材质/动作/枚举/声音包装和S2C通用消费者不额外加数。不同于已计Boss拒晕和Wither冲刺Arrow final result。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
