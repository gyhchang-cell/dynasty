"""Two native Dungeons Mobs control settlement/dedup policies; no per-wrapper credits."""
from ledger import B,O,record,verify
import json
r='Infamous-Misadventures/Dungeons-Mobs';p='src/main/java/com/infamous/dungeons_mobs/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
keys=[]
k='dungeonsmobs-native-stomp-knockback-cancellation-leaves-independent-vertical-control';keys.append(k)
record(k,r,[w('entities/golem/SquallGolemEntity.java'),w('DungeonsMobs.java'),f('mod/ModEntityTypes.java',293,300),f('mod/ModEntityTypes.java',582,598)],
 '固定f04b11游戏源，ModEntityTypes构造SquallGolem并在模组构造注册。registerGoals添加真实MeleeAttackGoal子类；doHurtTarget server且attackID0时写STOMP；MeleeGoal.start广播负byte，tick30 AreaAttack。实际AreaAttack对弧内非盟友两次hurt（均忽略结果），forceKnockback先发布ForgeHooks事件，取消即仅从helper返回；caller随后无条件velocity.y+=0.3333333。客户端handleEntityEvent重置本地attackTimer，tick30地面粒子仅表现攻击阶段，不包含每个目标的裁决。',
 '计1：实际原生攻击的取消作用域被后续物理分量绕过，区别完全不发布KnockBack的push以及临时属性恢复家族。即便事件被取消，caller独立Y位移仍执行；若不取消，则strength乘1-resistance*0.35，resistance1仍保留65%而非完全免控。两次hurt false均不阻断后果。范围判断&&/||括号使跨360角度分支不受水平range子条件限制，但候选仍在膨胀AABB内。',
 'Boss免控应在完整控制结算前给出明确结果，跳过所有运动分量后才生成一次灰字/闪光/嗡声；不能仅监听Forge击退取消就宣布完整免疫，也不能从hurt布尔推导。',
 '完整SquallGolem已读，包含原生doHurtTarget→Goal启动，不把未触发的helper当运行通过。固定快照存在旧DamageSource常量/GeckoLib3等版本上下文，本研究未编译上游、未运行游戏；未核ForgeHooks底层或证明TCP/视觉。动画/byte/sound/注册包装0；普通体质仍无灰字要求。','native_control_cancellation_scope')
k='dungeonsmobs-native-paired-impact-zones-share-attempt-history-not-health-success';keys.append(k)
record(k,r,[w('entities/summonables/AreaDamageEntity.java'),f('entities/jungle/LeapleafEntity.java',101,129),f('entities/jungle/LeapleafEntity.java',467,576),w('utils/PositionUtils.java'),w('DungeonsMobs.java'),f('mod/ModEntityTypes.java',265,272),f('mod/ModEntityTypes.java',556,563),f('mod/ModEntityTypes.java',582,598)],
 '原生Leapleaf.registerGoals→LeapGoal.canUse/start/tick，从跳起落地进入smashAnimationTick；actionPoint18创建左右两个AreaDamage，双向connectedAreaDamages后加入world。AreaDamage.baseTick server逐alive目标，canEntityBeDamaged先排owner/友伤/自身已命中列表，再遍历关联区域列表；准入后hurt结果不读，distance>=0.5直接push、可disableShield、最后将entity加入自身damagedEntities。两个区域据对方历史在同次生命周期跨载体合并一次目标尝试。',
 '计1：双实体AOE共享“尝试”历史的原生去重位点，不同于每tick父分体盾一次/独立箭pierce名单。首次hurt失败也消费所有关联区域机会；这不是每次免控回执防刷，也不证明控制已拒（push/禁盾仍执行）。只有被遍历的关联区域constantDamage=false时其历史才拦，不是递归传递闭包。extraTime/增长控制server销毁；NBT存damage等但不存owner、damageSource、friendlyFire、damagedEntities、connectedAreaDamages或extraTimeTick，保存重开不可声称保持去重与归属。',
 '灰字去重键和生命周期应显式定义为目标+拒控反馈窗口，不能复用伤害命中名单；一次区域伤害拒绝不等于Boss控制免疫。可按明确事件共享回执预算，维度切换和载体失效清理另核。',
 'AreaDamage全文、LeapGoal完整嵌套类与注册方法、PositionUtils全文已读。原生跳跃准备其它Goal仅作上下文，不宣称整篇Leapleaf全文。实体event粒子坐标属于区域本体而非目标浮字；vanilla30盾声并非免疫嗡声。上游未执行，实际画面/网络未验；构造/位置数学/packet spawn包装0。','native_cross_carrier_target_dedup')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'dungeonsmobs-batch103-native-control-scope-and-paired-zone-attempts','credited_chains':keys,'rationale':'Two distinct final game policies: canceled horizontal control helper followed by unconditional vertical motion; reciprocal native AOE entities sharing failed-or-successful attempt history. Entity naming, sound/particle wrappers and static immunity lists zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
