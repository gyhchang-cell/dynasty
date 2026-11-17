"""Full native Goety Boss rejection and feedback-context review. Run once."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';keys=[]
def s(q,a,z):return p+q,a,z
def whole(q):
 q=p+q;return q,1,len((B/'sources'/r.replace('/','__')/q).read_text().splitlines())
def add(k,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定02adbe7491767210f63857fa763a6f1de1262cbd；实际完整方法及注册/原生覆盖上下文。未运行，不证明Boss灰字、音量、TCP和本项目完成。普通体质不要求灰字；同链包装/常量门不另计。','native_boss_refusal_and_feedback');keys.append(k)
a='common/entities/boss/Apostle.java';e='common/entities/boss/EnderKeeper.java'
boot=[s('Goety.java',148,211),s('Goety.java',237,552),whole('common/network/ModNetwork.java')]
bar=[whole('common/network/ModServerBossInfo.java'),whole('common/network/server/SUpdateBossBar.java'),whole('client/events/BossBarEvent.java'),s('client/ClientProxy.java',22,42),s('init/ClientInitEvents.java',77,170),s(a,384,392),s(a,1165,1172)]
add('goety-apostle-native-rejected-hit-still-publishes-smite',boot+bar+[s(a,749,751),s(a,765,767),s(a,801,912),s(a,1193,1631),s(a,1758,1760),whole('common/network/server/SApostleSmitePacket.java'),s('common/entities/ModEntityType.java',609,614)],
 '原生Apostle.hurt在最终来源/二阶段/moddedInvul/obsidianInvul拒绝之前，先记受击次数，并依据directLiving攻击者SMITE立即置antiRegen/total、S2C ALL及施法冷却+10；随后仍可return false。真实aiStep两端递减antiRegen、阶段准备清0；接收按当前世界entityId+Apostle类型更新，已注册BossBar读取isSmited与比值绘制进度。',
 '一次明确拒伤仍可实际进入禁回血状态并发包，false不能表示无任何命中后果；directEntity查武器附魔，不是投射物owner。smite时长按等级clamp1..5秒但另保留原smiteLevel参与减伤。receiver无UUID/维度/epoch/期限校验，也不按目标限流，每次有效SMITE尝试可重设寿命及ALL广播。moddedInvul在actuallyHurt成功调用后按来源有无设置，aiStep递减；伤量cap/减半不是完全免疫，常量来源拒绝不额外计。',
 'Boss控制免疫应先判最终拒控，再生产明确immune回执，不能把hurt=false、普通受伤音或先发状态反馈当同一种语义；观察到的前置副作用需与拒绝结果分开。')
add('goety-enderkeeper-distance-refusal-counterteleport-not-success-gated',boot+[s('common/entities/ModEntityType.java',802,808),s(e,660,682),s(e,1774,1803),s('utils/MobUtil.java',1940,1942),s('utils/MobUtil.java',122,145),s('utils/MobUtil.java',1181,1194),s('utils/MobUtil.java',1200,1203),whole('common/network/server/SInstaLookAtPacket.java')],
 '真实EnderKeeper.hurt计算实际damageSource.getEntity到Boss距离平方；超配置范围且非bypass，即使所有传送尝试均不成功也直接false。反击前需来源非同盟且自己非攻击/隐藏，teleportTowards服务端存活时最多128候选→可取消Forge EnderTeleport→碰撞/液体门→teleportTo及同步朝向。',
 '区别已研VoidRobe传送成功才取消伤害：本门范围拒伤独立于反击传送结果；事件cancel只break反击，不使原伤害恢复。无来源range=-1不超正范围；intro的FELL_OUT_OF_WORLD例外不自动绕过后续moddedInvul。候选碰撞用现有世界AABB.move(绝对vec)，并未减当前坐标，静态不能声称安全落点正确；最后一次失败仍转头。伤害倍率Ownable0.5、canBeAffected beneficial白名单仅支持0。',
 '免控与Boss正常反击可同时发生，拒绝当前控制不意味着Boss纹丝不动或停止AI；控制是否拒绝不得依赖装饰传送成功。')
add('goety-native-boss-feedback-identity-map-los-membership',boot+bar+[s(a,182,195)],
 '真实Boss构造ModServerBossInfo、start/stopSeenByPlayer调用add/remove；add先发送barUUID+实体整数ID映射，无LOS者另放待观察Set，Boss每5tick update发现LOS才父类addPlayer；stop父类移除/清待观察Set并发remove。客户端实际consume查当前world Mob→proxy→BOSS_BARS map，GUI事件按barUUID找到实体读实时HP/状态。',
 '映射ADD先于原生可见血条，有别Vampirism事件全量可见状态发布；客户端remove必须仍能查到同id Mob且Map.remove(UUID,mob)要求同一对象，目标先卸载时remove会直接丢失，可保留强引用。全Java搜索只见add/remove，没有本类世界切换/失踪淘汰；故不声称跨维或断线清理正确。无重试/缓存未知目标，无entityUUID防id复用。全部订阅/映射职责1，三个具体Boss同包装不拆数。',
 'Boss灰字应锚实际目标但销毁清理不能依赖目标仍在世界；移除应携带稳定身份直接淘汰临时记录，未知目标不无限保留。')
q=O/'semantic-dedup.json';d=json.loads(q.read_text());d['groups'].append({'family':'goety-native-boss-batch27','credited_chains':keys,'rationale':'3实际不同职责：拒伤前SMITE副作用/发布，距离拒伤独立反击传送成败，LOS订阅与barUUID→实体对象映射生命周期。EnderKeeper有益效果白名单、Vizier常量拒伤/半伤仅支持0；不按每个Boss或每个包拆数。'});q.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
