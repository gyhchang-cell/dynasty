"""Manual full-method/native-context review, fixed local Vampirism revision."""
from ledger import B,O,record,verify
import json
r='TeamLapen/Vampirism';v='projects/vampirism/src/main/java/de/teamlapen/vampirism/';f='projects/faction/src/main/java/de/teamlapen/faction/';fa='projects/faction-api/src/main/java/de/teamlapen/faction/';keys=[]
def whole(q):return q,1,len((B/'sources'/r.replace('/','__')/q).read_text().splitlines())
def s(q,a,z):return q,a,z
def add(k,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定本地commit逐项全文方法/实际游戏调用上下文观察；源码导入1903文件信用0，未运行此版本。静态不证明观感、声音、TCP或本项目已修；普通阴阳体质不要求灰字，守卫旧账0转入。','native_refusal_feedback_and_anchor');keys.append(k)
d=v+'common/world/entity/dracula/Dracula.java';vp=v+'common/world/entity/player/vampire/VampirePlayer.java'
base=[s(d,126,174),s(d,188,220),s(d,237,242),s(d,560,629),whole(v+'common/world/entity/dracula/ai/DraculaState.java')]
boot=[whole(v+'VampirismMod.java'),whole(v+'common/CommonServices.java'),whole(v+'common/core/ModRegistryManager.java')]
pub=[whole(v+'common/world/entity/dracula/ServerDraculaEvent.java'),whole(v+'common/world/entity/dracula/DraculaEvent.java'),whole(v+'common/network/packets/client/ClientboundDraculaEventPacket.java'),whole(v+'common/network/ModPacketDispatcher.java')]
client=[whole(v+'client/gui/overlay/DraculaEventOverlay.java'),whole(v+'client/network/ClientPayloadHandler.java'),whole(v+'client/core/ModScreens.java'),s(v+'client/ClientServices.java',110,140),whole(f+'client/gui/overlay/BaseOverlay.java')]
add('vampirism-dracula-native-burst-triggered-mist-refusal',base+[s(d,55,61),s(d,348,362)],
 '原生actuallyHurt在RAGED时将本次amount/世界tick加入recentDamage→剔除100tick外记录，和>maxHP*0.2且冷却已过→MIST/清ATTACK_TARGET/设600tick冷却并清列表；原生isInvulnerableTo拒MIST/变身/动作记忆，下一个tick更新事件；MIST>100tick后RAGED。',
 '这是实际受伤后滑动伤量触发后续拒伤窗口，区别简单状态常量换壳；本次伤已交super再转态，不应给本次命中标immune。isInvulnerableTo先父判定，再bypass例外，不能泛称所有bypass均穿透；PASSIVE/DEFAULT投射物拒绝会反向箭，但不改owner或清已命中集合。两个飞行动作记忆门仅作上下文，未读完整动作生产链不额外计。RANGED投射物0.5/RAGED箭1.5是倍率不是免疫。',
 'Boss回执要区分当前原生拒绝与本次伤害促发的后续状态；burst触发、寿命和冷却都是实际行为，不把每个阶段/弹种独立凑数。')
add('vampirism-dracula-authoritative-state-change-publication',base+pub+boot,
 'Dracula服务端alive tick逐次updateEvent→真实ServerDraculaEvent.update读stage/isInvulnerable/HP→各setter仅值变才sendUpdate，visible时向已订阅玩家发对应operation；首次不可见更新会setVisible(true)发ADD。',
 '无敌态来自权威Boss状态而非客户端血量差值；逐tick核对但变化才发包，不是逐次攻击反馈的时间节流。不同字段同tick变化可产生多包；精确float比较，无最小变化阈值。packet命名isVulnerable/vulnerable实际承载inVulnerable，不能按英文猜极性。所有enum/codec/setter包装合计1职责。',
 '本项目控制拒绝事件与持续免疫状态需明确语义和极性；灰字事件窗口不能直接套状态只变更发布，连续不同拒绝仍应按要求限流回执。')
add('vampirism-dracula-event-uuid-client-update-isolation',pub+client,
 '实际playToClient注册→handleDraculaEventPacket.enqueueWork→Overlay.handle：ADD替换本地event；UPDATE/各字段UPDATE/REMOVE均要求当前event非空且event UUID相等；REMOVE匹配才置null。',
 'UUID是战斗事件实例身份，不是Boss实体UUID；更新/移除可防旧event串到新event，ADD却无序号或会话/维度校验且只留单槽。未知event update直接丢，没补发队列。包没有target位置、目标实体/维度或过期时间，不能称世界锚定或跨维安全。非游戏通用库不计；这里是实际Boss反馈接收策略。',
 'Boss目标反馈需要实体身份与世界代际，旧更新/旧REMOVE不能误伤新记录；ADD也应受同样有效性约束，协议有UUID不自动等同完整校验。')
add('vampirism-dracula-invulnerability-hud-clock-and-transition',pub+client,
 '原生已注册GUI层在camera overlays上方render：非空事件→wall clock Util.getMillis计算250ms免疫淡变/350ms闪光/脉冲，按免疫位叠专用fill、shield和glow；setInvulnerable仅状态变化更新时间及flash，HP降低另记500ms延迟尾条。',
 '完整render/read/setter已读，是真实游戏Boss无敌反馈，不是通用图形API；屏幕血条没有目标世界深度或浮字。采用毫秒可在低帧率按绝对时间推进，但暂停/GUI寿命观感未实测；本类未调用BaseOverlay.canRenderOverlays（alive/hideGui检查不会因继承自动生效）。ADD初始changeTime=0导致初态直接达淡变终点；同值更新不重闪。纹理样式/每次blit不另计。',
 '灰字应选清晰的tick/真实时间语义和GUI可见策略，继承检查必须实际调用；不以已提交/图形非空宣称本项目画面通过，不制作身体资产。')
add('vampirism-dracula-fight-scoped-feedback-membership-lifecycle',base+pub+[whole(v+'common/world/entity/dracula/DraculaFightData.java'),whole(v+'common/world/LevelEventHandler.java'),s(vp,612,625)]+boot,
 '实际专维LevelTick.Post→FightData.tick FIGHTING每100tick把当前level players加进ServerEvent Set；成功伤害亦addPlayer；Set新增且visible才发ADD。Boss die核对UUID→奖励→event.clear给集合REMOVE并清集合；destroyDimension也clear。',
 '这是服务端反馈订阅/事件结束生命周期，与客户端UUID过滤和发布抖动不同职责。getOpt限定ServerLevel维度类型；FightData弱Boss引用但UUID强索引。event.players是强ServerPlayer集合；本次读取仅见VampirePlayer.onDeath移除，不能声称离维/登出所有分支均清理；未运行断线/重开。复用class中的坍塌/造门/奖励等非课题实现信用0，绝不照搬删除维度。',
 '目标离追踪、死亡、卸载、世界切换要分别清临时反馈，不能用一个全局集合永久保留接收者；静态结论应限制于已读生产/清理路径。')
playerboot=boot+[whole(f+'common/CommonServices.java'),whole(f+'Services.java'),whole(f+'common/world/entities/PlayerListenerEventHandler.java'),whole(f+'common/event/PlayerEventHandlerEvent.java'),s(v+'common/core/ModEntities.java',186,191)]
dbno=[s(vp,504,506),s(vp,593,609),s(vp,628,658),s(vp,750,756),s(vp,772,884),s(vp,986,999),s(vp,1061,1089),s(vp,1269,1284),s(vp,432,438),s(v+'common/world/entity/player/ModPlayerEventHandler.java',248,255),s(v+'common/util/Helper.java',215,228),whole(v+'common/integration/PlayerReviveHelper.java')]
add('vampirism-native-down-not-dead-refusal-and-control-state',dbno+playerboot,
 'HIGHEST原生LivingDeath→VampirePlayer.onDeadlyHit实际等级/NEONATAL/可终结来源资格→DBNO timer至少1（扣PlayerRevive已倒地时长）/HP0.5/强制SLEEPING/清附近仇恨/sync→取消死亡；实际IncomingDamage附件listener在DBNO且非终结来源return true→cancel。',
 '并非永生：特定终结武器/猎人或bypass仍可杀；onUpdate倒计时到0仍处DBNO（>=0），逐tick停XZ/非正Y/清效果/补空气；giveUp先清倒地再以10000伤终结，登出倒地也清状态并kill，避免再拒死循环。loadDBNOTimer只在进出边沿开屏/改pose/refreshDimensions，本批未补通用sync内部/屏幕实现，因此不另计接收器或声称完整网络视觉。方法/武器名单不拆数；普通体质无灰字要求。',
 '拒绝死亡、拒伤与拒控是不同状态机；Boss免控不能意外固定睡姿、吞正常AI或清所有效果。拒绝反馈应保留明确最终原因，避免把倒地不死叫Boss Immune。')
action=f+'common/factions/actions/ActionHandler.java'
act=[whole(v+'common/world/entity/player/vampire/actions/VampireActions.java'),whole(v+'common/world/entity/player/vampire/actions/DefaultVampireAction.java'),whole(f+'common/factions/actions/DefaultAction.java'),s(action,196,203),s(action,278,358),s(action,409,414),s(f+'common/factions/actions/ActionHelper.java',25,28),s(f+'common/server/ServerPayloadHandler.java',121,152),whole(f+'common/network/packets/server/ServerboundToggleActionPacket.java'),whole(f+'common/network/packets/ModPacketDispatcher.java')]
add('vampirism-native-heavy-hit-blood-payment-refusal',
 playerboot+act+[s(vp,628,658),s(vp,1051,1053),s(vp,383,392),s(v+'common/world/entity/player/vampire/BloodStats.java',193,203),whole(v+'common/world/entity/player/vampire/actions/HalfInvulnerableAction.java')],
 '真实HalfInvulnerable注册→服务端toggle/onActivated设skill flag并slowness，重激活同样设flag；原生IncomingDamage附件listener→onEntityAttacked在amount>=最大HP*配置阈且<999时尝试useBlood(cost,false)，足量扣血资源后return true取消这次伤害，不足则deactivateAction清flag/移自有slow。',
 'half_invulnerable名称不表示半伤；满足阈值实际整次取消，<阈值及>=999不保护。足额原子扣血资源（源码无负cost防护，不推测合法配置故障），不足不部分消费而解除能力；与Goety全attack消耗ward积分/Enigmatic火额度恢复不同结算策略。前置DBNO/替换火伤可能提前return，未沿用它们当本重击免疫证据。仅原生重击拒绝点1。',
 '免疫反馈必须用真实最终拒绝结果，不按技能名称猜百分比；Boss控制拒绝不能依赖玩家血资源或伤害阈值。')
add('vampirism-native-freeze-eligibility-precedes-status-but-not-cue',act+boot+[whole(v+'common/world/entity/player/vampire/actions/FreezeVampireAction.java'),whole(v+'common/world/effects/FreezeMobEffect.java')],
 '实际注册Freeze动作→服务端toggle→DefaultAction.onActivated→activateServer：WATER_EVAPORATES直接SUCCESS，其它按faction/noSpectator范围找实体→先原生freeze声/雪粒子，再canFreeze false跳过→addEffect后清sharedFireFlag；效果原生applyEffectTick再次canFreeze才提高ticksFrozen。',
 '明确最终资格门并不抑制预发cue，SUCCESS还可能表示环境早退完全没施法；addEffect返回值没查，因此抗药水者亦不能据粒子证明冻结。FreezeMobEffect用原生ticksFrozen+attackSpeed modifier，未声称停止所有运动；freezeBlocks其它世界修改与免疫研究0额外。与已有完整freeze-body控制链不同，这里是vanilla canFreeze双阶段与先反馈后拒绝的生产策略。',
 '拒控回执须由确认跳过控制的分支产生，发光/声音/施法SUCCESS都不是目标被控制证据；Boss灰字不能让普通体质出现新文字义务。')
add('vampirism-native-action-denial-result-and-side-effect-order',act+[whole(fa+'api/factions/actions/IActionResult.java'),s(f+'common/core/FactionKeys.java',107,121),s(f+'common/core/FactionKeys.java',146,157),s(f+'common/event/FactionEventFactory.java',102,113)],
 '真实玩家按键按action key本地时间防抖→C2S上下文→服务端handler.toggleAction：禁用效果/active切换/CD/旁观/解锁/permission/阵营配置逐层返回IActionResult；资格通过先deactivate互斥动作，再post可取消ActivatedEvent，成功后才加实际duration/CD；handler失败按result发overlay或system消息。',
 '实际游戏动作拒绝/显式原因链，非通用网络设施；服务端目标从本world整数ID查找，未知仅警告，没在本handler做距离/LOS验证。不同reason常量/包装0；互斥动作已解除后，新ActivatedEvent仍可取消，拒绝并非完全无副作用。消息发送没有服务端按目标节流，本地按键防抖不能防重放包。deactivateAction(action,ignoreCooldown)重载将false,false传下，忽略参数，支持边界不另计。',
 '本项目最小拒控逻辑应在控制动作副作用前决定并明确返回reason，回执节流在服务端；不要把普通动作聊天当Boss目标灰字，也不要信客户端按键限速。')
p=O/'semantic-dedup.json';d=json.loads(p.read_text());d['groups'].append({'family':'vampirism-native-feedback-batch25','credited_chains':keys,'rationale':'9个独立游戏职责：受伤burst促发后续拒伤、权威状态变化发布、事件UUID接收、免疫GUI时钟、服务端订阅生命周期、倒地拒死状态机、大伤血资源拒绝、原生canFreeze双阶段/预cue、动作拒绝结果/副作用次序。Ghost纯源常量门/玩家同阵营模板/形式控制重复/配置常量0；1903源码导入0，Faction通用依赖包装0。'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
