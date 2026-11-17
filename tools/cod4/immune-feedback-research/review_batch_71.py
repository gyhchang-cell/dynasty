"""Arcanus native denial policies; complete critical native chain, not renderer counts."""
from ledger import B,O,record,verify
import json
r='CammiesCorner/Arcanus';p='src/main/java/dev/cammiescorner/arcanus/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
common=[f('Arcanus.java',50,128),w('ArcanusMixinConfig.java'),('src/main/resources/arcanus.mixins.json',1,len((B/'sources'/r.replace('/','__')/'src/main/resources/arcanus.mixins.json').read_text().splitlines())),w('common/registry/ArcanusSpellComponents.java'),w('common/networking/serverbound/ServerboundSyncPatternPacket.java'),w('api/spell/Spell.java'),w('api/spell/components/SpellShape.java'),w('api/spell/components/SpellGroup.java'),w('common/spell_component/shapes/SelfSpellShape.java')]
keys=[]
def add(k,refs,chain,obs,lesson,limits,cat):
 keys.append(k);record(k,r,common+refs,chain,obs,lesson,'固定6a098ad2c95f3366b14d395e311e353da6bc4c70，所引完整方法/调用链逐项读；'+limits,cat)
add('arcanus-native-one-use-danger-sense-source-qualified-refusal', [w('common/spell_component/effects/support/DangerSenseSpellEffect.java'),w('common/registry/ArcanusMobEffects.java'),f('mixin/common/LivingEntityMixin.java',82,125),f('ArcanusConfig.java',1133,1169)],
 '实际注册danger_sense_effect与MobEffect→原生C2S已装备Staff/法术书/组件知识/大小/cooldown等校验→Spell.cast→Self.shape按HashSet去同effect→DangerSense.effect给Living target上有时长状态；Living.hurt HEAD正amount且原生盾未挡，状态存在且IS_PROJECTILE或IS_EXPLOSION，随机<base.035*(amp+1)进入。Server最多16次randomTeleport，成功才GameEvent与新旧坐标声音；分支最后无论传送成功与否removeEffect并hurt返回false。',
 '一个由原生施法赋予、仅投射/爆炸且成功roll后消耗整次状态的拒伤点1。与Nebula装备被动闪避有状态消耗和伤源资格差异，与Goety voidrobe明确成功传送才拒伤不同。amp构造(int)Math.min(potency-1,0)不是max，不能据potency声称层数增强；本地效果消费/returnfalse在ServerLevel块外，声只服务端成功传送分支，没有统一拒伤声，更没有Boss控制reason。所有随机失败保留状态，无CD字段；未加BYPASSES_INVULNERABILITY排除。',
 '拒控回执必须与最终拒绝绑定，不能以移动/传送声代替；未移动也可能确实拒伤。普通阴阳体质不增加灰字。',
 '完整原生hurt方法、实际施法支持和配置已读；未审vanilla randomTeleport内部及框架调度、未启游戏/音像/网络并发验证。构造/状态注册/16次尝试0。','native_consumable_source_qualified_damage_refusal')
add('arcanus-native-mana-barrier-collision-context-and-expiring-visible-lease', [w('common/spell_component/effects/support/ManaShieldSpellEffect.java'),w('common/entity/magic/ManaShield.java'),w('mixin/common/EntityGetterMixin.java'),w('common/registry/ArcanusEntities.java'),w('client/renderer/entity/magic/ManaShieldRenderer.java'),w('client/ArcanusClient.java')],
 '已注册mana_shield_effect原生cast→同world查ownerUUID盾，先kill list.size()-10个再新增1→setProperties(ownerUUID,targetLocation.y-.7,maxage)并addFreshEntity。原生EntityGetter.getEntityCollisions HEAD把正在求碰撞的实体置ThreadLocal，RETURN remove；实际ManaShield.canBeCollidedWith在context为空返回true，否则剩余寿命>20且context实体当前AABB不交盾才true。实际ticker查同world owner存活/实体挤压/真实age和无人时收尾；注册ManaShieldRenderer随实体生命周期按剩余20tick缩放发光三角。',
 '一个实际物理屏障按碰撞上下文及剩余寿命拒绝外部进入的原生点1，非Wizardry projectilehurt shield换名：内部重叠实体可穿出、收尾20tick不挡context碰撞但仍画，collision与alpha不同步边界必须留证。无UUID同步字段给owner但服务端查ownerUUID；不能跨维canChangeDimensions=false，server找不到owner就kill；无人重叠把maxage缩至age+20，之后不会延长。原生列表清理不是严格10上限，size=10时新增为11，未写错误上限。renderer alpha用clamp且scale3*alpha，实际vertexalpha1而RGB乘alpha；RenderType additive、COLOR_DEPTH_WRITE、NO_CULL，没有NO_DEPTH_TEST。几何只是提交，不是观感通过。无灰字/拒控receipt。',
 'Boss字/闪光的可见寿命不应隐式代表实际免控窗口；锚定生命周期和生效判定须各自有准确来源，不能靠几何非空宣称命中拒绝成功。',
 '完整native spell/barrier/ticker/NBT/collision/renderer/RenderType和注册已读。ThreadLocal没有try/finally异常清理，本项只记录结构不宣称实际异常复现；原版碰撞内部及TCP实体同步不计独立credit。未制作资产。','native_collision_control_barrier_lifecycle')
add('arcanus-native-component-stun-locks-mob-attack-without-effect-admission', [w('common/spell_component/effects/attack/ElectricSpellEffect.java'),w('common/component/entity/StunComponent.java'),f('common/registry/ArcanusComponents.java',81,112),f('common/registry/ArcanusComponents.java',238,248),w('mixin/common/MobMixin.java'),w('mixin/client/MinecraftMixin.java')],
 '原生已注册Electric.effect在实体hit内若双方Player且caster.canHarmPlayer为false先return；其他Living直接setStunTimer(baseTime*potency)→真实STUN_COMPONENT living factory NEVER_COPY/setter同步。服务端组件每tick正值减1并对Player resetAttackStrengthTicker；Mob.doHurtTarget HEAD在stun>0返回false。客户端Minecraft.tick清施法pattern，handleKeybinds HEAD取消输入，两者读同步组件。',
 '一个组件计时型控制使原生Mob攻击被最终拒绝的实现点1；不是把状态名换成stun或拆多个输入wrapper。Electric不通过addEffect或hurt成功结果，原生状态免疫canBeAffected与damage拒绝不会自动拦此控制；只有PlayerPvP前置关系排除。setter直接覆盖而非max，新短值可缩短已有stun。未见此链Boss例外/免疫灰字；服务端C2S handle未另查stunned，因此客户端输入锁不等于服务端所有施法拒绝，完整消费者方法已读不得误标安全。',
 'Boss控制免疫需接在真正写入控制的点，不能只拦药水addEffect或hurt；应区别控制被拒绝与受控后攻击被锁，回执语义不得混淆。',
 '本项的有效单位是原生组件驱动攻击拒绝链；客户端输入/注册/组件同步是上下文0。StunOverlay源码虽已读，尚未确认实际render接入，不以它证明HUD存在，也不增信用。未启游戏/制作动画。','native_control_driven_attack_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'arcanus-batch71-native-policy','credited_chains':keys,'rationale':'状态消耗型闪避、带出入方向/生命周期碰撞屏障、组件stun原生Mob攻击拒绝是三个最终策略。native施法链/renderer/input包装和常量均0。未将普通warding建筑权限提示或孤立stunoverlay计入。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
