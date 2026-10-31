"""Actual native resource denial and Boss phase/status paths; static only."""
from ledger import B,O,record,verify
import json
keys=[]
def whole(r,f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
def add(k,r,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定本地源码Git blob/SHA256；完整相关方法和原生调用链静态观察，无游戏、TCP、像素/声音或Mixin运行验证。通用BrandonsCore/CCL网络实现仅调用边界支持0，未假定其内部保证；不改正式代码/资产/TODO，不给普通阴阳新增灰字。','native_damage_refusal_and_boss_feedback');keys.append(k)
c='Lothrazar/Cyclic';cp='src/main/java/com/lothrazar/cyclic/'
add('cyclic-native-damage-pre-scaling-and-dual-charm-consumption',c,[whole(c,cp+'ModCyclic.java'),whole(c,cp+'registry/EventRegistry.java'),whole(c,cp+'util/CharmUtil.java'),whole(c,cp+'item/bauble/ItemBaseToggle.java'),(cp+'event/ItemEventHandler.java',230,305),(cp+'registry/ItemRegistry.java',222,241)],
 '注册真实LivingDamage.Pre→onEntityDamage按原生DamageTypes判定→damageFinder查启用装备、乘当前newDamage、零下界、耐久调用。Player受伤与非Player遭玩家攻击分支互斥；原生库存/Curios/toggle已全文。',
 '一个最终装备伤害缩放家族计1，不把各来源常量/装备名、horse火/水持久标志分支多计。factor0是结算零伤，magic/dragonBreath factor0.5是减半，不能都叫免疫。CHARM_CREEPER实际仅PLAYER_EXPLOSION，非注释泛称所有爆炸；火分支依次两次damageFinder，若两个charm都存在即使已为0仍分别耐久调用，未按成功首个短路。饥饿/溺水的附带eat/effect在找到装备时触发，不查实际原伤>0或效果接纳。原生return true语义是找到装备，不是Boss拒控原因。',
 '要明确区别零伤/减半/资源保护，发免疫反馈之前统一结算原因及去重，避免多个监听/装备重复提示。')
r='Draconic-Inc/Draconic-Evolution';p='src/main/java/com/brandon3055/draconicevolution/'
base=[(p+'DraconicEvolution.java',20,52),(p+'entity/guardian/GuardianFightManager.java',211,240),(p+'entity/guardian/DraconicGuardianEntity.java',151,188)]
add('draconic-guardian-native-part-hit-crystal-phase-denial-settlement',r,base+[whole(r,p+'entity/guardian/DraconicGuardianPartEntity.java'),(p+'entity/guardian/DraconicGuardianEntity.java',523,584),(p+'entity/guardian/GuardianFightManager.java',280,294),(p+'entity/guardian/GuardianFightManager.java',309,311),whole(r,p+'entity/guardian/control/PhaseManager.java'),(p+'entity/guardian/control/Phase.java',67,69),(p+'entity/guardian/control/ChargeUpPhase.java',212,220),(p+'entity/guardian/control/ChargeUpPhase.java',230,233),(p+'entity/guardian/control/LaserBeamPhase.java',26,39),(p+'entity/guardian/control/LaserBeamPhase.java',174,184),(p+'entity/guardian/control/LaserBeamPhase.java',194,197)],
 '原生Part.hurt先isInvulnerableTo，再parent.attackEntityPartFrom；主体hurt服务器也走同门。DYING/自源→false；护盾音→5tick幅度门→剩晶体拒绝→当前Phase.onAttacked→护盾消费/血量分段。ChargeUp最终伤害0，Laser继承但仅beamCharge<0.5免疫。',
 '同Boss最终伤害结算/phase门合计1，水晶/部位名/阈值不拆数。护盾音在cooldown和晶体/phase最终拒绝之前发，未见按反馈音节流；5tick内较小hit仍更新lastDamage，后续门槛随之改变。phase伤害0且shield>0会走return true但无消费，true不保证扣血/扣盾。没有shield且非头部damage0经(damage/4)+min(damage,1)仍0后false；实际伤害仅Player来源/EXPLOSION调用super，其他来源可以true却没HP变化。盾耗尽用旧getShieldPower扣溢出，fullshield减损并非Boss永久免疫。',
 'Boss免疫必须从准确拒控分支生产，不从hurt布尔或已播盾音倒推。阶段免疫、晶体保护、普通吸收、冷却拒绝需要不同语义；不冻结Boss自然AI。')
add('draconic-native-boss-uuid-status-snapshot-delta-and-hud-consumer',r,base+[whole(r,p+'world/ShieldedServerBossInfo.java'),(p+'network/DraconicNetwork.java',39,47),(p+'network/DraconicNetwork.java',82,85),(p+'network/DraconicNetwork.java',218,224),(p+'network/ClientPacketHandler.java',33,75),(p+'init/DEClient.java',57,89),whole(r,p+'client/CustomBossInfoHandler.java'),whole(r,p+'entity/guardian/control/PhaseManager.java')],
 '真实GuardianFightManager.guardianUpdate按guardian UUID匹配→阶段isInvulnerable写ShieldedServerBossInfo；值改变才对可见players发UUID+op增量；addPlayer/setVisible发全快照，remove隐藏发删除。原生网络C_BOSS_SHIELD_INFO→客户端UUID map→实际BossEventProgress替换渲染，LoggingOut清map。',
 '独立Boss状态订阅/增量/生命周期显示链1，非每个setter/packet wrapper计数。UUID是boss bar id不等于世界目标实体UUID；此处显示青色/红色护盾与水晶计数，没有灰色免疫浮字。immune只取phase，不包含仍存晶体/命中冷却等真实拒绝，不能当所有拒绝总标志。客户端op2/3/4对未知id直接get.set无nullguard，缺维度/代际序号/有限值范围；logout清理不等于跨维度/乱序安全已验。100ms插值用墙钟，不是tick寿命；增量去同值不是逐目标攻击反馈节流。',
 '文字需目标锚定和明确单次事件语义；状态同步可用首快照+变化增量避免重复，但不能拿boss条替代原需求灰字，也不能将UI缓存uuid当世界目标校验。')
add('draconic-native-modular-shield-two-stage-absorption-and-environment-sound-cooldown',r,[(p+'DraconicEvolution.java',20,52),(p+'handlers/ModularArmorEventHandler.java',64,79),(p+'handlers/ModularArmorEventHandler.java',184,240),(p+'items/equipment/IModularArmor.java',102,109),(p+'api/capability/DECapabilities.java',21,24),(p+'api/modules/ModuleTypes.java',23,23),(p+'init/DEModules.java',211,216),(p+'api/modules/entities/ShieldControlEntity.java',44,373),(p+'api/modules/lib/ModuleEntity.java',541,545)],
 '原生LOW Incoming/Pre伤害→真护甲ModuleHost→先Undying再ShieldController→完整tryBlockDamage及blockEnvironmentalDamage；incoming能全吸收则cancel，Pre支持剩余盾部分扣除/零伤。成功调用onShieldHit重置同步动画并原生playSound；环境来源另用envDmgCoolDown40tick音门，tick逐次递减。',
 '同控制器两伤害阶段/环境反馈合计1，未按四种TechLevel或各伤害来源常量多计。Incoming明确BYPASSES_INVULNERABILITY+source::is UNBLOCKABLE；Pre却UNBLOCKABLE.contains(DamageSource)，集合是ResourceKey类型，不是同一判定且缺bypass tag门；不能宣称/kill以外所有豁免一致。环境cost按固定每秒/20非本次amount，只该环境声音40tick门，普通命中声音每次onShieldHit均可播；部分破盾仍亮动画但damageBlocked=false不发相同full-block音。shieldAnim/indicator在服务端tick衰减，持久/stream codec包含它们；未跟完整host同步/armor renderer，故不声称客户端身体闪光验收通过。',
 '可参考明确拒绝与部分吸收区分、环境音节流职责；正式Boss拒控路径统一入口/旁路标签，灰字和闪光/嗡声按同一拒绝事件节流，不扩展玩家普通体质。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'native-refusal-batch34','credited_chains':keys,'rationale':'Cyclic实际最终newDamage装备结算1；Draconic Boss最终结算1、UUID boss状态订阅HUD1、装备盾两阶段+环境音门1。颜色/部位/常量/wrapper/原生帧几何0额外，498文件导入0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
