"""Illage native incoming-damage bank and game-specific sound anchoring, two families."""
from ledger import B,O,record,verify
import json
r='TheDarkPeasant/Illage-and-Spillage--Respillaged';p='src/main/java/com/yellowbrossproductions/illageandspillage/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
e='entities/MagispellerEntity.java'
common=[w('IllageAndSpillage.java'),f('init/ModEntityTypes.java',123,123),f(e,164,189),f(e,210,226),f(e,248,262)]
k='illage-native-negated-damage-bank-interrupts-heal-with-qualified-failure-receipt'
record(k,r,common+[f(e,349,979),f(e,981,987),f(e,1383,1468),f(e,1499,1541),f(e,2226,2288),w('entities/MagiHealEntity.java'),w('events/ForgeEventBusSubscriber.java'),w('packet/PacketHandler.java'),w('packet/ParticlePacket.java')],
 '实际Magispeller注册和HealGoal原生AI挂接。canUse要求无攻击/假身/邻近illager、健康未满/无regen/冷却等；start重置damageTaken=0，gotHealed=true、wavingArms=true、生成MagiHeal ring。原生hurt先普通伤害cap20等，Forge LivingHurt magispellerNegateDamage对waving+非kill/void+未取消事件累加event.amount再置0。完整tick在HEAL_ATTACK且累计>30置gotHealed=false；Goal下一次continue停止并stop，gotHealed真才heal8+regen，假且非balloon则发50 angry粒子+interrupt声，全部清wave/attack并cooldown200。',
 '计1：零伤吸收仍保存来伤预算，预算打断治疗并分叉成功/失败回执；不同于Scylla招架受击次数阈值/反击蓄力，也不是按伤害常量换壳。累计来自LivingHurt当时amount，非实际HP损失或原始完整来伤。恰好30不打断、超过30才打断；导致超阈值的当前hit仍被置0。首次inactive hurt可把amount0并激活，不等于明确控制拒绝。MagiHeal持非同步owner引用，server跟随/失效/150tick上限；client若无owner不跟随由正常位置同步承担，不能冒称client owner已同步。',
 'Boss Immune应从最终控制拒绝生产；吸收零伤、蓄积打断和控制免疫须区分。一次终态失败回执可在状态退出时生产并节流，不能按每个hurt=0都发灰字。',
 '完整tick349–979、HealGoal及native hurt/event listener/三种粒子方法已读，注册callsite核对；ParticlePacket全链 enqueue/currentlevel null check但只有坐标无维度UUID事件id，未设包内粒子数量上限。固定快照静态源码不是实机效果；不按ring/particle/sound包装再计。','native_negated_hit_budget_and_interrupt_receipt')
k2='illage-native-combat-sound-follows-target-with-action-specific-anchor-freeze'
record(k2,r,common+[f(e,349,979),f(e,1919,1921),f(e,2655,2701),f('util/EntityUtil.java',142,146),w('packet/MobFollowingSoundPacket.java'),w('packet/PacketHandler.java'),w('util/MobFollowingSoundPlayer.java'),w('client/sound/MobFollowingSound.java'),w('util/ClientHelper.java')],
 '原生LifestealGoal.canUse资格+start设置type2并发prepare音，native tick攻击36发LIFESTEAL音。EntityUtil仅server→tracking+self，包含entityId/SoundEvent registryId/volume/pitch/loop；handler enqueue后currentLevel/entity/sound非空才交SoundManager创建MobFollowingSound。tick目标alive/未removed/非silent且动作许可时更新当前坐标；死亡/移除/silent/动作不许则stop。另特定Magispeller type3假身阶段attackTicks>=49冻结声音位置，Croco/Hinder有charging/healing限定及首tick宽限。',
 '计1：游戏原生战斗音效的实体生命周期和动作相关锚定政策，区别Goety按包内世界点播一次声音/忽略dimension；不是通用音频底层库计数。同一Sound类不同音源、Croco/Hinder分支与registry/handler包装全并1。无entityUUID/dimension/事件id/重复实例map，重复包可多次play；type2 Lifesteal不走额外动作许可，活体时动作结束未主动stop，通常依音频自然完成。特定type3位置冻结不能笼统称始终跟随目标。',
 '灰字嗡鸣可使用一次server目标回执+短原版音，不需要长循环；若需跟随音，明确alive/world/结束条件且同目标节流，避免每tick叠新实例；不借音频开始证明免控已发生。',
 '完整声音生产Goal/目标资格方法、native tick、包/播放器/声音类及注册调用已读；未读原版SoundManager底层，不计底层、不声称声音听感或实际播放成功。Croco/Hinder本轮未读完整native producer，只作为该声音类额外边界描述不加数。','native_combat_audio_target_anchor_lifecycle')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'illage-batch101-damage-bank-interrupt-and-anchored-audio','credited_chains':[k,k2],'rationale':'Incoming damage negation funds a heal-interruption budget with terminal success/failure receipt. Separate native combat-audio delivery has action-specific moving/frozen anchor and lifecycle stop policy. Same packet/render/sound wrappers, boss skins and constants are zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
