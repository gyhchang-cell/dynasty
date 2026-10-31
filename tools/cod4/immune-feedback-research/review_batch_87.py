"""Per attack-phase target admission, outcome budget and qualified feedback; one site."""
from ledger import B,O,record,verify
import json
r='Antikythera-Studios/epicfight';p='src/main/java/yesman/epicfight/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='epicfight-native-phase-tried-target-dedup-versus-outcome-budget-and-qualified-hit-feedback'
record(k,r,[f('api/animation/types/AttackAnimation.java',144,347),w('api/animation/types/ComboAttackAnimation.java'),w('api/utils/HitEntityList.java'),w('api/utils/AttackResult.java'),f('gameasset/Animations.java',862,870),f('world/capabilities/entitypatch/LivingEntityPatch.java',456,478),f('world/capabilities/entitypatch/LivingEntityPatch.java',1074,1086),f('world/capabilities/entitypatch/LivingEntityPatch.java',1219,1230),f('world/capabilities/entitypatch/player/PlayerPatch.java',368,391),f('mixin/common/MixinLivingEntity.java',65,91),f('api/event/impl/VanillaEntityEventHooks.java',178,203),w('particle/HitParticleType.java')],
 '实际SWORD_AUTO1等注册ComboAttackAnimation继承AttackAnimation；服务器tick/linkTick→attackTick检测进入攻击phase，onStrike/挥击声并清两套target列表，hurtCollidingEntities取连续姿态碰撞、HitEntityList排序、maxStrikes预算。每目标parent multipart归一成Living，alive/未尝试/非团队车乘或spectator拒绝且LOS才尝试；暂置invulnerableTime0→PlayerPatch.attack调用原生Player.attack→恢复iframe。原生Living.hurt返回true的mixin标记lastAttackEntity，guard等分支也显式标记；patch关联最后尝试目标与返回result。每次已尝试均入tried；只有shouldCount占用命中预算，只有dealtDamage播放目标位置hitSound和hitParticle。',
 '独立位点为一个攻击phase内按真实目标去重、三态结果预算及声光资格的一整套原生消费者1，不按列表getter/排序方式/武器工厂或multipart数量计数。SUCCESS(true,true)、BLOCKED(false,true)、MISSED(false,false)：格挡可以占预算无命中声光，miss不占预算但该phase不再尝试同一parent。清表在新phase，不能当全局每目标时间节流。checkLastAttackSuccess命名只证明与目标相关，不能证明HP变化；Incoming可先登记结果，后来damage流程仍能改变实际损血。原生hurttrue的回执也不能替代明确控制拒绝。恢复iframe无finally，本次无异常运行验证。',
 'Boss灰字由最终拒控生产点显式发出；命中列表/目标预算/已有粒子非空都不能推导免控事实。应按目标和拒绝事件节流，不能把某phase去重当跨tick不刷屏。灰字和命中声不共用hurtfalse条件。',
 '完整phase方法、结果类、ComboAttackAnimation、HitEntityList及实际Player.attack包装/原生hurt-return注入已读；剑factory已核，未查全部数据驱动武器绑定/碰撞几何及像素。不启动游戏，不声称实际画面、声音或TCP验收。普通体质type9不新增灰字。','native_target_dedup_outcome_feedback')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'epicfight-native-phase-outcome-budget','credited_chains':[k],'rationale':'phase reset + tried parent identity + tri-state strike accounting + qualified sound/particle as one concrete independent implementation; wrappers and weapon variants zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
