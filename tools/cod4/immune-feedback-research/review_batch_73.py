"""Simply Swords: three native policies, never credit wrapper/shape variants."""
from ledger import B,O,record,verify
import json
r='Sweenus/SimplySwords';p='common/src/main/java/net/sweenus/simplyswords/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
common=[f('SimplySwords.java',148,365),('common/src/main/resources/simplyswords-common.mixins.json',1,80)]
# JSON length is checked from the actual pinned file rather than assumed.
common[-1]=(common[-1][0],1,len((B/'sources'/r.replace('/','__')/common[-1][0]).read_text().splitlines()))
keys=[]
k='simplyswords-native-timed-parry-stack-identity-and-charge-receipt';keys.append(k)
record(k,r,common+[w('item/custom/StormbringerSwordItem.java'),w('item/interfaces/UniqueWeaponActiveAbility.java'),f('registry/ItemsRegistry.java',734,739),w('world/StormbringerParryManager.java'),w('item/component/ParryComponent.java'),f('world/StormbringerAbilityManager.java',209,234),f('world/PlayerWeaponAbilityChannelManager.java',24,39),f('world/PlayerWeaponAbilityChannelManager.java',81,146),w('mixin/ServerPlayerEntityMixin.java')],
 '实际ITEM.register stormbringer→原生Item.use→useFromDefaultInput检查解锁/CD/mana→startPlayerAbility服务端activate并setCurrentHand；原生ServerPlayer.damage HEAD在non-bypass分支调用handleIncomingDamage，true便return false。activate以UUID保存hand、原stack对象、world key、总时窗/弹反时窗。原生ServerPlayer.tick每tick验证，quit/world unload/stop清退。',
 '限时使用态+同stack对象的拒伤政策1，不按格挡/弹反/声音/电荷/两个手重复。时窗内且攻击者存活、友伤允许、距玩家在半径内才perfect，得电荷、回执声/粒子并stopUsingItem；否则普通挡击仍true。没有朝向检查，也没有amount>0判定；远处或环境源不能据此称完美弹反。电荷有容量夹取；满容量带特定tuning才有独立overflow lockout，但该附属奖励不另计。使用停止读取parried决定反击或miss；反击逐目标实际damage返回成功才做目标后效，不能以反击声反推命中。channel替代支路按同item+损坏状态+world验证，而active原stack身份仍另验。',
 '将Boss拒控明确绑定原生最终裁决与目标，声音和粒子不能倒推出拒控成功。使用态、总时窗、perfect时窗与回执节流是不同条件；本例每挡击仍可发声，不能照搬为不刷屏。',
 '固定708a57bc591e0af75ae0c5ec6beb0d8ff22f67af。关键全文方法、原生hook、物品入口和组件已读；通用mastery框架配置/溢出吸收不扩算。未启动游戏/验证音效或全平台mixin兼容。','native_timed_use_parry_refusal')
k='simplyswords-native-ion-cube-paid-heavy-hit-shield-lease';keys.append(k)
record(k,r,common+[f('registry/ItemsRegistry.java',727,732),f('world/IonboundStormscaleAbilityManager.java',80,84),f('world/IonboundStormscaleAbilityManager.java',163,240),f('world/IonboundStormscaleAbilityManager.java',580,594),f('world/IonboundStormscaleAbilityManager.java',654,663),f('world/IonboundStormscaleAbilityManager.java',761,803),f('world/IonboundStormscaleAbilityManager.java',953,957),f('world/IonboundStormscaleAbilityManager.java',966,971),f('world/IonboundStormscaleAbilityManager.java',982,985),f('world/IonboundStormscaleAbilityManager.java',1011,1014),f('world/IonboundStormscaleAbilityManager.java',1023,1034),w('entity/IonboundStormscaleVisualEntity.java'),w('mixin/ServerWorldMixin.java'),f('mixin/LivingEntityMixin.java',156,207),w('mixin/ServerPlayerEntityMixin.java')],
 '实际ServerPlayer.damage或非ServerPlayer的Living.damage HEAD→handleIncomingDamage。正amount、ServerWorld且非bypass；现有按world+UUID的未到期shield先直接拒绝并impact反馈；否则查主副手ionbound及解锁，阈值以上且非overchargedcore并实际consumeCubes成功才建立shield、可视entity和start反馈，returntrue由原生hook拒伤。ServerWorld.tick HEAD→hasActive→tick→tickShields清到期/死目标。',
 '伤害阈值触发的组件资源支付→持续无再次支付的护盾租期为独立最终点1；不是红石charge盾每击扣费或纯护甲常量变体。已经有效的租期不再查持武器/解锁/cubes，换手不立即解除；到期严格now<expiresAt。新shield visual spawn结果未检查不影响逻辑护盾入表，视觉不存在不能证明拒绝失败。impact声/粒子每个合格命中都发，没有反馈节流。ION_REBOUND横向受KB阻力缩放，Y固定.18；不可称满阻力完全不动。visual通过owner int+UUID复核，服务端UUID回查修正int，非保存实体；服务端tick跟随/寿命清除，客户端仅本world int+UUID。该身份/visual上下文同链0。',
 'Boss状态拒绝与显示成功应分开观察。灰字/微光/嗡声需要按目标限制频率，不能借短期护盾或命中不扣血当Boss拒控reason；换手不应误改变目标拒控身份。',
 '完整关键拒绝、支付、清退、native调用及实体身份方法已读。未完整审通用UniqueAbility tuning计算、补充cube自然恢复或视觉像素，不据此给这些路径信用。未运行客户端。','native_resource_paid_damage_lease')
k='simplyswords-native-observer-combat-status-uuid-worldtime-presentation';keys.append(k)
record(k,r,common+[f('SimplySwords.java',389,485),f('api/SimplySwordsAPI.java',196,213),w('api/ObserverStatusVisualRegistry.java'),w('api/ObserverStatusEffectSyncRegistry.java'),w('api/ObserverStatusEffectSnapshot.java'),w('world/ObserverStatusEffectSyncManager.java'),w('network/SimplySwordsNetwork.java'),w('network/ObserverStatusEffectsPacket.java'),w('client/ObserverStatusEffectClientState.java'),w('client/api/ObserverStatusEffectClientApi.java'),f('mixin/LivingEntityMixin.java',111,128),w('mixin/client/WaxEncasedLivingEntityRendererMixin.java'),f('mixin/client/WorldRendererMixin.java',46,56),f('client/renderer/ObserverStatusVisualRenderer.java',63,98),f('client/renderer/ObserverStatusVisualRenderer.java',711,770)],
 '实际init为bloodplague/ionparalysis等注册observer visual，注册style同步加入effectID白名单；原生onStatusEffectApplied/Upgraded/Removed TAIL→服务端manager增量。JOIN/RESPAWN/换维发本world全量replace快照，Entity.ADD发当前效果。实际S2C payload注册→客户端receiver.queue→presentation cache；原生LivingEntityRenderer.TAIL→按style读取entity本world维度+UUID+effect缓存，bloodplague走groundring；WorldRenderer.HEAD清当前帧辅助状态。',
 '一个战斗状态观察者展示的完整UUID/维度/服务端到期时间快照增量链1，全部effect形状/包装/packet字段不拆计。区别既有Ars整数ID且排本地玩家，Draconic BossbarUUID：本例以实际Living UUID+dimension查展示缓存、不注入vanillaeffectmap；active用packet.serverWorldTime+max(0,duration)，查询用客户端worldtime懒清，到期不再绘制。replaceAll清所有维度；退出清空。发送同world全部玩家，无tracking/range筛选；包size限65536但amp/duration无独立clamp，无序号/会话/迟包回滚防护，不能声称跨维并发已测。GROUND_RING在entity本地矩阵y.055/.061画双面环，未采地形；emissive最大光照不证明穿墙。只完整观察groundring和分发，不把未读其他shape称已观察。',
 'Boss灰字应有目标UUID+维度/会话与过期清除，状态展示快照不等于控制拒绝回执；不能为每个展示字段或形状加研究数，也不能给普通体质自动加Boss灰字。',
 '固定版本，关键生产hook、manager、codec、cache、native renderer入口和groundring全文方法已读。removeEntity方法存在但本批未确认实际销毁调用，故不宣称实体销毁必发清退；其他复杂Gloam形状非本项信用，实机像素/延迟/TCP/声音均未验。','native_combat_status_observer_presentation')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'simplyswords-batch73-native-policies','credited_chains':keys,'rationale':'时窗同stack弹反、电荷支付重击触发租期、战斗状态UUID世界时快照展示三独立政策。每个回执/包装/shape不拆计，与旧方向盾、按击charge、Bossbar及整数ID状态链逐项对照；普通phase dash候选仍0。'})
(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
