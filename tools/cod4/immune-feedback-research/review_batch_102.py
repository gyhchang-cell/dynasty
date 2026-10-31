"""Invoker native reversible projectile shield, one policy rather than generic shield skins."""
from ledger import B,O,record,verify
import json
r='Fuzss/illager-invasion';p='Common/src/main/java/fuzs/illagerinvasion/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='illagerinvasion-native-incoming-source-flips-persisted-shield-before-parent-admission'
record(k,r,[w('world/entity/monster/Invoker.java'),w('client/render/entity/InvokerRender.java'),w('client/render/entity/layers/InvokerShieldLayer.java'),w('client/IllagerInvasionClient.java'),f('init/ModRegistry.java',48,65),f('IllagerInvasion.java',54,57)],
 '固定1.20.1游戏源码ee2743，main元数据分支19项没有游戏实现保留0。ModRegistry注册Invoker并onConstruct touch；实际Invoker.hurt server对projectile且无盾50%先播放shield_block并setShieldedState(true)，非projectile且有盾1/3先发30CRIT/破盾音再setfalse，然后才super.hurt。虚派发isInvulnerableTo基于当前shield拒projectile，witch-resistant tag无条件拒。DATA boolean同步、NBT Invul持久化、isPowered暴露；真实client renderer注册后构造InvokerShieldLayer，继承vanilla EnergySwirlLayer并用wither armor纹理。',
 '计1：当前攻击来源直接翻转持久护盾，反过来影响同次父hurt准入的可逆策略，区别固定phase/方向盾/耗次数破盾。开启shield的声效在最终super结果之前；不能据声音判造成伤害或控制已拒。非弹也可破盾后仍因其他isInvulnerable分支拒伤。概率仅server产生，client消费同步boolean；没有逐目标/逐事件receipt节流。盾不定时失效，NBT恢复保留。',
 'Boss Immune显式反馈只能由最终控制裁决发送；预判盾开启/破裂音不可泛化成免控回执。灰字节流独立于状态持续时长，正常体质保持原type9。',
 'Invoker完整实体全文、render/layer全文、client注册方法全文已读；原版EnergySwirlLayer底层提交深度未读，不声称遮挡/透明/画面通过，模型只读不复制资产。基础RegistryManager/PuzzlesLib平台分发辅助0，实际onConstruct及registerEntityType自有调用点已核。','native_reversible_shield_source_admission')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'illagerinvasion-batch102-source-mutates-shield-before-hurt','credited_chains':[k],'rationale':'Reversible stochastic source-dependent persisted shield affects same native hit before parent admission. Not a renamed phase bit, fixed damage tag or finite shield count. Render and synced getters one chain, other illager shield/half-damage skins zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
