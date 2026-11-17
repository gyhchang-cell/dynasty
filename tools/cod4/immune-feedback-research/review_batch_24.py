"""Manually observed Enigmatic Legacy native refusal/feedback responsibilities."""
from ledger import B,O,record,verify
import json
r='Aizistral-Studios/Enigmatic-Legacy';p='src/main/java/com/aizistral/enigmaticlegacy/';keys=[]
def whole(s):
 q=p+s
 return q,1,len((B/'sources'/r.replace('/','__')/q).read_text().splitlines())
def span(s,a,z):return p+s,a,z
boot=[span('EnigmaticLegacy.java',202,244),span('EnigmaticLegacy.java',331,402)]
helpers=[span('handlers/SuperpositionHandler.java',277,292),span('items/EnigmaticAmulet.java',129,143)]
impact=[span('handlers/EnigmaticEventHandler.java',1605,1689)]+boot+helpers
def add(k,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定commit本地源码全文方法/原生调用上下文静态观察；未启动游戏，不能证明运行时注册资源、网络或观感通过。普通阴阳体质不要求灰字；守卫旧账不计入。','native_refusal_feedback_and_anchor');keys.append(k)
add('enigmatic-native-projectile-impact-deflection-settlement',impact,
 '原生ProjectileImpactEvent→服务端命中Player→实际装备资格概率合并→取消本次impact→反向速度/朝向→箭清已命中集合/穿透并改owner（trident例外），火球改owner/加速度→同维64格S2C纠正+DEFLECT声。',
 '三个装备概率合并1，不按物品/弹种换壳计数；概率和没clamp。实际偏转在碰撞原生拒绝点发生，与Ars spell-pre-resolve生成反射轨道不同；旧onEntityAttacked复制弹体代码全在注释，不计。源码Accessor clearHitEntities调用已见，mixin资源生效未验证。',
 '先确认最终拒绝及真实控制改动再生产原因正确的反馈；来源owner变更、实际方向和hurt结果不同职责，不能以hurt=false猜拒控。')
add('enigmatic-deflected-projectile-owner-reentry-window',impact,
 '同一原生碰撞点先检查Projectile.owner==本次受击玩家，扫描AB_DEFLECTED:<projectile.tickCount>，差值<10直接return；成功偏转删除旧tag并写新tick。',
 '这是弹体/归属局部回流窗口，专门防同一碰撞反复偏转；窗口内不cancel，注释说明cancel会让弹体陷无限碰撞。不是伤害无敌窗，也不是客户端包去重；不存在全目标统一冷却或异常tag限量，split/parse失败仅打印。',
 '拒控仍应逐次执行，节流的是反馈；抑制回流/重复反馈不能误取消原生事件造成状态卡住。按弹体局部回流职责计1，不按tag或tick常量计数。')
add('enigmatic-deflection-client-correction-target-validation',impact+[whole('packets/clients/PacketForceArrowRotations.java')],
 '原生成功偏转产生纠正包→已注册handler主线程→当前ClientLevel按entityID查目标→存在即标redirected并moveTo/setDeltaMovement/当前与旧朝向一起写。',
 '只检查非null，变量名arrow不代表校验Projectile；没有方向限制、UUID/维度/代际/有限浮点校验、过期序号或去重。未知目标当次丢掉无重试。redirected在原处理器客户端消费分支被注释；网络位置纠正并不等同视觉免疫成功。',
 'Boss短反馈必须校验当前世界与真实目标身份，避免整数ID复用；主线程排队与包名S2C都不能自动提供这些保证。仅此原生偏转纠正策略1，codec包装0。')
quota=[span('handlers/EnigmaticEventHandler.java',1691,1896),span('handlers/EnigmaticEventHandler.java',1016,1266),whole('objects/TransientPlayerData.java')]+boot+helpers
add('enigmatic-lava-immunity-recovering-quota-and-first-cue',quota+[whole('packets/clients/PacketWitherParticles.java')],
 '真实LivingAttack非创造无敌/无FireResistance/有BlazingCore/未取消/LAVA→timer<cap且<cap-diff才cancel，timer==0原生灭火声+32格烟包，再timer+200；ServerPlayer LivingTick按燃烧100或非燃烧200回收额度并dirty同步。',
 '这是可恢复额度门，与永久源常量免疫不同；cap32000而拒伤阈30000，阈值后仍可消耗直到cap。首声只在0起始，不等于所有拒绝都发声。setter clamp timer却把未clamp输入写last；烟包num8循环<=实际9，坐标快照非跟随，client无level/player空检查。该额度拒绝/首cue一族1。',
 'Boss控制免疫本身不应随反馈额度耗尽；明确将控制判定与灰字/闪光/嗡声节流分离，静态可检查每次拒绝仍有效且窗口只影响反馈。')
add('enigmatic-immunity-quota-uuid-state-receiver-boundary',quota+[whole('packets/clients/PacketSyncTransientData.java'),span('proxy/ClientProxy.java',113,118),span('proxy/ClientProxy.java',309,314)],
 '真实quota setter置needsSync→ServerPlayer tick syncToPlayer→序列化玩家UUID及timer/cap/last→decode在当前level按UUID找Player，找不到返回null→enqueueWork仅data非空且目标level客户端才写回该玩家TransientPlayerData。',
 '此处实际免疫额度状态接收与偏转整数ID包策略不同；未知玩家不排队补发。decode已经通过proxy访问world（不在handler排队闭包），没有显式dimension/epoch且候选弱引用可失效。setter/codec/查表包装不分别计数，未把通用网络库算研究。',
 '反馈包应在客户端主线程解析目标，不在decode读取世界；UUID目标、世界代际和短期过期校验需同时设计，不能因携带UUID就宣称切维安全。')
add('enigmatic-immunity-quota-native-hud-render-policy',quota+[span('handlers/EnigmaticEventHandler.java',585,723),span('handlers/SuperpositionHandler.java',1492,1508)],
 '真实RenderGuiOverlayEvent.Pre仅经验条位置、有装备且timer>0时cancel原经验条；按TransientPlayerData抛物线比例画免疫额度条，逐render本地化标题+语言配置偏移并画四向描边。',
 '是实际免疫额度展示策略，不是通用blitAPI。getFireImmunityFraction接partialTick但difference*=0，实际只取last；last是setter未clamp输入而非上一tick。没有屏幕GUI/世界代际主动清理证据；替换XP可能与其他HUD冲突。空气/饥饿分支与本任务无关0。',
 'Boss灰字需独立短生命周期并避免替换全局HUD，渲染tick/partialTick语义应准确；静态调用不证明画面可辨或低帧率平滑。')
add('enigmatic-protected-animal-hostility-arbitrates-denial',
 [span('handlers/EnigmaticEventHandler.java',1691,1896),span('handlers/SuperpositionHandler.java',1146,1155),span('items/PetGuidebook.java',104,106)]+boot,
 '真实Animal受击且来源Player背包有guidebook/受保护判定→先cancel；若animal现target、TargetGoal.targetMob或Brain.ATTACK_TARGET指向该玩家则再setCanceled(false)。',
 '是依真实敌意状态撤销自身拒伤的最终仲裁，不是仅owner/来源tag名单。NeutralMob默认例外又明确Hoglin/Bee/Wolf；不按实体常量加数。Brain读内存捕NullPointerException而非其他错误；撤销可能覆盖更早优先级取消，不能提前发immune后称终态。',
 '灰字要在最终确认拒绝处生成；存在后续反取消时，早期候选理由不代表最终免疫，不新增普通体质灰字需求。')
add('enigmatic-revive-self-delayed-world-ready-feedback',
 [span('handlers/EnigmaticEventHandler.java',1554,1574),span('handlers/EnigmaticEventHandler.java',1016,1266),span('items/TheCube.java',239,284),whole('packets/clients/PacketCosmicRevive.java'),span('proxy/ClientProxy.java',121,148)]+boot+helpers,
 '原生LOW LivingDeath符合Cube且无spellstoneCooldown→cancel/回血/触发实际能力及效果→同维128格CosmicRevive；client自玩家type非0设scheduledCubeRevive=5，其它目标立即按ID播放；本地LivingTick在非ReceivingLevelScreen时倒数到0后播放。',
 '独立职责是自玩家切换/接收level期间延迟反馈，区别TF立即camera/目标轨道。scheduledCubeRevive是全局单整数不含UUID/维度/请求序号，新包重置5tick；倒数由各Player LivingTick分支驱动，不限定本地玩家，因此多玩家场景可能加速。非0任意值都当Cube；实际FX为目标trackingEmitter/51火焰+原版TOTEM_USE，自玩家才物品激活动画。没有运行验证。',
 'Boss反馈应按目标/事件存短记录并校验世界会话，不将全局延迟计数当目标生命周期；已有合适原版声音可优先考虑，但复活声语义不直接照搬免疫嗡声。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'enigmatic-native-refusal-and-feedback-batch24','credited_chains':keys,'rationale':'8个独立职责：原生弹体偏转、归属回流窗、目标运动纠正校验、可恢复免疫额度、额度UUID收包、原生额度HUD、自身敌意仲裁拒伤、世界就绪延迟反馈；装备概率/源常量/codec/声粒子包装/注释旧实现0。EyeOfNebula失败仍拒伤与已计Rapier家族合并；Etherium静态来源门/减伤0；Poison全局mixin旗标缺本地bootstrap资源证据维持待核0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
