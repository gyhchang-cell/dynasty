"""Two native target-validation/budget policies; all supporting wrappers remain zero."""
from ledger import B,O,record,verify
import json
keys=[]
r='Lothrazar/Cyclic';p='src/main/java/com/lothrazar/cyclic/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='cyclic-native-laser-client-render-time-gate-and-server-hit-settlement-validation';keys.append(k)
record(k,r,[w('ModCyclic.java'),w('item/LaserItem.java'),w('net/PacketEntityLaser.java'),w('render/OutlineRenderer.java'),w('registry/PacketRegistry.java'),f('registry/ItemRegistry.java',278,278),w('registry/CapabilityRegistry.java'),w('capabilities/item/ItemEnergyCap.java')],
 '固定b221360，真实LASER_CANNON/use启动使用，ModCyclic.setupClient注册OutlineRenderer；AFTER_ENTITIES真实渲染回调主手Laser且using且足能时，近距crosshair或远距ProjectileUtil+block clip选目标，world.getGameTime()%4==0发entityId/crosshair C2S且本地射击声。PacketRegistry.playToServer接handle enqueueWork，本level按ID找目标、重验主手、活体/无敌及模拟足能；hurt成功后才实际耗能并resetStackDamageCool。ItemEnergyCap实际CUSTOM_DATA持久化能量。',
 '计1：真实客户端渲染时钟目标选择与服务器最终拒伤/付款配对的整条游戏裁决，非通用网络库。模4在每个render调用判断，未记lastSentTick，同一game tick可多发，不是每目标去重；getDamageCooldown只读CustomData.EMPTY副本，reset只改EMPTY副本未写stack，且本链无调用getDamageCooldown/DELAYDAMAGETICKS。服务端canShoot未判target null（先target.isAlive），未复验using/距离/LOS/crosshair真实性/发包节流，仅在本level查ID；不存在实体有静态空引用风险，未实机复现。hurt=false不耗能，发包端已可出声/绘线，不是Boss灰字语义。',
 'Boss拒控反馈按服务端明确原因生产；节流用目标身份与事件/实际tick历史，不能借渲染tick取模；S2C先核当前世界与目标存在、身份一致和有限生命周期。普通阴阳体质保留type9。',
 '上述whole文件全文已读；ItemRegistry只读实际字段。外部lothrazar library RenderEntityToBlockLaser/ChatUtil/SoundUtil/能源wrapper未读，辅助0，不声称最终深度/灰字/能量基类行为或客户端观感。LastStand只部分减伤并非本条免疫实现，不额外计数。','native_target_request_validation_and_render_time_throttle')
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
k='goety-native-bubble-shared-collision-budget-acceptance-and-incoming-defuse-exclusion';keys.append(k)
record(k,r,[w('common/entities/projectiles/BouncyBubble.java'),w('common/entities/projectiles/SpellHurtingProjectile.java'),w('common/entities/projectiles/WaterHurtingProjectile.java'),w('common/magic/spells/abyss/BouncyBubbleSpell.java'),w('common/items/magic/MagicFocus.java'),f('common/items/ModItems.java',379,379),f('common/magic/ModSpells.java',122,122),f('common/entities/ModEntityType.java',300,305),f('common/items/magic/DarkWand.java',548,568),f('common/items/magic/DarkWand.java',762,845),f('utils/ModDamageSource.java',235,242)],
 '真实focus注册到ModSpells.BOUNCY_BUBBLE；DarkWand.finishUsingItem→MagicResults server→BouncyBubbleSpell原生造owner弹体入world。WaterHurtingProjectile.tick→hitDetection（Forge impact可取消）→BouncyBubble.onHit。实体碰撞只有hurt成功才增BOUNCE_TIMES，实心块碰撞则反转速度后无条件增；两种来源共享budget，到已有>=6时下一次碰撞explode。原生hurt先通用invulnerability/removed/exploding拒绝；水伤或同类直接弹体不触发explode但返回true，其余触发explode。',
 '计1：共享方块碰撞/实际hurt成功预算与弹体自身受击的条件引爆裁决整家族，非每碰撞/每方法加数；不同SpellCloud按ACTIVE阶段累计成功数退出，本例块碰撞也耗预算、失败实体碰撞不耗，水攻击/同类受击返回true却无引爆/HP parent。BOUNCE_TIMES+SIZE同步并存NBT，伤害未按目标记录，不能据hurt失败推Boss immune或拒绝重复反馈。explode先以exploding/isRemoved防重并置exploding，server才建SpellExplosion/粒子/两声，最后discard；tick>=100也走同幂等出口，块碰撞没有server guard，本机可先discard，未验TCP效果。',
 'Boss的拒控/拒伤/物理碰撞/伤害成功与声光预算应分开；不要把弹体返回true或消失当作伤害接纳。对明确拒控事件以server裁决和逐目标节流发送灰字/闪光/嗡声。',
 'BouncyBubble、两父弹体、实际spell与focus全文和finishUsingItem/MagicResults完整已读。SpellExplosion伤害展开本批未读，不以构造声明冒称爆炸命中链或观感通过；WaterHurtingProjectile注释注明借鉴Iron通用运动/命中，辅助0不重复入Herschel来源。无模型/资产/正式代码修改。','native_mixed_collision_success_budget_and_defuse_gate')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch107-native-laser-render-time-validation-and-bubble-mixed-impact-budget','credited_chains':keys,'rationale':'Laser actual request/validation/settlement is one game chain; renderer modulo is not target dedup and cached EMPTY tag is not cooldown. Bubble mixed block/accepted-hurt budget plus conditional incoming defuse is one distinct native policy; base borrowed impact helpers and lifecycle wrappers zero, not another SpellCloud phase implementation.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
