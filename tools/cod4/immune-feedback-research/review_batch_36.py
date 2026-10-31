"""Four independent native TConstruct policy sites; data definitions auxiliary zero."""
from ledger import B,O,record,verify
import json
r='SlimeKnights/TinkersConstruct';p='src/main/java/slimeknights/tconstruct/';keys=[]
def whole(f):return p+f,1,len((B/'sources'/r.replace('/','__')/(p+f)).read_text().splitlines())
def add(k,refs,chain,obs,lesson):
 record(k,r,refs,chain,obs,lesson,'固定f4e77d43f39ba1047bf93ae816b7e1beaab514c2。实际JSON启用全文网页观察另存tinker-native-resources-web.json；不冒充raw blob验证，不为JSON/通用loader/网络包装额外计数。无游戏或观感结论，不改正式源/资产/待办，普通阴阳不新增灰字。','native_control_refusal_and_target_feedback');keys.append(k)
base=[(p+'TConstruct.java',104,156),(p+'tools/TinkerModifiers.java',360,366),(p+'library/modifiers/ModifierManager.java',285,315),(p+'library/modifiers/impl/ComposableModifier.java',30,79)]
add('tconstruct-native-equipped-effect-immunity-multiset-threshold',base+[whole('library/modifiers/modules/armor/EffectImmunityModule.java'),whole('tools/logic/EquipmentChangeWatcher.java'),whole('library/tools/capability/TinkerDataCapability.java'),(p+'tools/logic/ModifierEvents.java',155,170),(p+'tools/TinkerTools.java',290,313),(p+'library/modifiers/modules/technical/ArmorLevelModule.java',83,85)],
 '真实mithridatism数据定义effect_immunity(poison)→ModifierManager条件加载ComposableModifier→装备变更钩子有效slot/未broken/condition时加减multiset→原生Applicable从目标cap读取count>amplifier才DENY。原生server装备事件即时更新，client每5tick比较副本调用同组hook；Living cap只存内存，invalidate保留旧Holder以应对维度切换。',
 '以最终等级阈值拒绝点计1，毒/其他效果、等级、装备槽、onEquip/onUnequip包装合并0。multiset是等级贡献之和而非取最大；严格大于amplifier，默认255不等于无限。只判接纳不主动清除已存在状态，无灰字/声音/收包回执。装备移除也有未broken条件，不能凭条件推测已复现残留。仅server/客户端本地重建，不把cap当服务端同步包或持久化。',
 'Boss拒控应在最终接纳判定区分原因；不可将所有addEffect失败或普通装备毒免疫改成Boss灰字。')
add('tconstruct-native-timed-shield-reflection-owner-and-skip',base+[whole('library/modifiers/modules/build/VolatileIntModule.java'),(p+'tools/logic/ModifierEvents.java',410,574),(p+'tools/logic/InteractionHandler.java',456,477),(p+'common/network/TinkerNetwork.java',45,82),(p+'common/network/TinkerNetwork.java',129,143)],
 'reflecting实际定义每级volatile int40→原生ProjectileImpact LOW：server/nonblacklist/非自身owner/真正在用SHIELDS→active GeneralInteract BLOCK且使用age>=5且<反射时间、canBlock方向→保留特殊owner或重设owner及arrow pickup→真实shoot和动力→motion包调用+原版盾音+SKIP_ENTITY+损耗3。',
 '最终时窗反弹拒绝计1；角度/owner/pickup/velocity/声音和wrapper同链不多计。反射后没有return，仍可进入本方法下方Enderference手动伤害，SKIP_ENTITY不证明后续逻辑皆停止。time边界严格；事件未设独立每目标节流。网络调用参数Packet,target使用继承NetworkWrapper重载，不用本地反序参数重载冒充已验证收件范围。canBlock null源拒绝，水平方向但view含y，acos没夹值；仅静态边界不称运行故障。',
 '最终拒控后必须明确终止本次控制管线；一个回执窗口统管文字/闪光/声音，不能把反射尝试音当伤害成功。')
add('tconstruct-native-enderference-final-teleport-cancellation',base+[whole('shared/TinkerEffects.java'),whole('common/TinkerEffect.java'),(p+'tools/logic/ModifierEvents.java',576,581)],
 '原生TinkerEffects注册HARMFUL可见enderference及实际普通/long potion，并commonSetup注册酿造；实际enderference modifier定义亦有武器/armor效果生产→原生EntityTeleportEvent检查Living hasEffect→setCanceled(true)。',
 '以独立最终传送拒绝点1，不把药水长短/颜色/同效果的武器与armor应用计数。hasEffect门本身不区分Boss；拒绝当前teleport而非所有AI，未发送专用拒控反馈。TinkerEffect.apply弃掉addEffect布尔返回而返回构造的instance，不能把instance当成功或免疫回执。数据模块生产链仅作激活支持，不声称读取完其所有攻击调用者。',
 'Boss控制免疫应保留普通AI并只拒绝当前尝试；正式灰字由明确Boss原因生产，普通体质仍用原type9。')
add('tconstruct-native-enderference-arrow-immunity-override-settlement',[(p+'tools/logic/ModifierEvents.java',410,574),whole('shared/TinkerEffects.java'),whole('library/modifiers/entity/ReusableProjectile.java')],
 '同一原生ProjectileImpact后半：Enderman+实际enderference+箭且非黑名单→pierce预算/记目标id→速度/暴击伤害→MELEE_ARROW刻意绕原版箭免疫→临时火→真实hurt结果分支；成功击退/附魔/箭音/清箭，失败恢复火/反向慢弹，最后取消原版impact。',
 '独立于teleport门与盾反射的最终箭伤结算位点计1，不按每个伤害/粒子/实体id另计。pierce在hurt前消费target ID，本分支不检查contains，不在false回滚；失败不等于Boss免疫。ReusableProjectile.discard只删singleUse，带可复用tag/interface可留下。目标没受伤也取消原版impact，不能以event canceled作伤害成功证明。方法整体没有统一server-only门，不能声称全部分支仅server。',
 '回执需以实际控制政策结果而非hurt=false推断；预算/去重应在明确结果处定义，复用投射物生命周期不能套一次性清理。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'tconstruct-native-batch36','credited_chains':keys,'rationale':'装备效果等级阈值拒绝、盾时窗反弹、最终传送拒绝、箭免疫旁路结算各1；数据换名/level/slots/loader/网络包装0额外。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
