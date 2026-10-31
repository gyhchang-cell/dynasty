"""Three newly reviewed native pet combat policies; no guard-credit transfer."""
from ledger import B,O,record,verify
import json
r='AlexModGuy/DomesticationInnovation';p='src/main/java/com/github/alexthe668/domesticationinnovation/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def data(s):
 s='src/main/resources/'+s
 return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
common=[w('DomesticationMod.java'),w('DIConfig.java'),w('server/enchantment/DIEnchantmentRegistry.java'),w('server/enchantment/PetEnchantment.java'),w('server/item/CollarTagItem.java'),f('server/item/DIItemRegistry.java',14,16),f('server/CommonProxy.java',783,944),f('server/CommonProxy.java',561,710),f('server/entity/TameableUtils.java',75,104),f('server/entity/TameableUtils.java',128,173),f('server/entity/TameableUtils.java',184,244),f('server/entity/TameableUtils.java',251,293),f('server/entity/TameableUtils.java',315,345),f('server/entity/TameableUtils.java',524,532)]
keys=[]
k='domestication-native-first-attack-attempt-arms-subsequent-rejection-window';keys.append(k)
record(k,r,common+[f('server/CommonProxy.java',162,218),f('server/CommonProxy.java',264,558),f('server/entity/TameableUtils.java',358,372),w('server/misc/CollarTickTracker.java')],
 '固定7b0fd345，原生mod注册PROXY到Forge总线；真实COLLAR_TAG可附魔，PetEnchantment IMMUNITY_FRAME注册且默认enable，EntityInteract宠物/owner判定后从collar附魔写Citadel tag；getEnchantLevel真实读该tag。LivingAttackEvent：tamed且非SIPHON，immuneTime<=0只置20+level*20、不取消本次；已有窗口才cancel/flag。LivingTick server在couldBeTamed&&canTickCollar范围每tick减时并sync。',
 '计1：以首次攻击尝试打开后续拒绝窗口，不同Vizier实际parent hurt成功后30tick窗口。首次攻击之后若被别的护盾/owner政策拒绝仍已开窗口，不能称首次成功受伤才触发；窗口不延长每次重复攻击。cancel后本方法攻击宠物的CHAIN_LIGHTNING/FROST_FANG/BUBBLING/VAMPIRE/WARPING_BITE分支仍可走，只有最终healer impulse检查!event.isCanceled。IMMUNITY_FRAME与BLAZING_PROTECTION正常附魔互斥，不能拿双装备构造当原生可得。无灰字/按目标回执去重。',
 'Boss拒控应在明确信号生产点拒全部该控制副作用；免疫持续窗口与反馈节流是两回事。只对明确Boss拒控发灰字，不借首次攻击音/取消/未掉血推断。',
 '实际关键完整方法已读，非整篇CommonProxy/TameableUtils。Citadel sync仅确认本类调用all/server PropertiesMessage，外部收包实现未读，不能声称网络身份验证或像素通过。CollarTickTracker及调用静态已读，仅支持0；不复用守卫旧账、不改生产内容。','native_attack_attempt_armed_immunity_window')
k='domestication-native-lethal-prehit-recall-serialization-and-spawn-result-asymmetric-refusal';keys.append(k)
record(k,r,common+[w('server/entity/RecallBallEntity.java'),w('server/entity/DIEntityRegistry.java'),f('server/entity/TameableUtils.java',747,750)],
 '同一真实collar启用TOTAL_RECALL。LivingAttack最终救援分支仅前面flag=false、tamed非SIPHON且health-rawamount<=2、非zombie、ownerUUID非null。先ambient/close声，创建RecallBall，写宠物addAdditionalSaveData/type/owner UUID，放原位且至少minBuildHeight+1，setInvulnerable，原宠物stopRiding；addFreshEntity成功才discard原宠物，但无论结果都cancel本次攻击。',
 '计1：在原生攻击结算前将受保护活体序列化为独立受owner约束的恢复容器，区别LifeCharm/普通图腾/瞬移救援与Endergetic转伤。未按护甲/实际最终伤害判致命；创建失败仍拒伤且已下马和播声。容器owner交互才OPENED，native tick开至1后按类型重建并readAdditionalSaveData、回血max(2,maxHP*.25)、入世界；不检查重建addFreshEntity返回就FINISHED，后闭合discard。OPENED不存NBT，FINISHED存；shouldBeSaved排除finished。RecallBall.isInvulnerableTo只返回source.isCreativePlayer且不super，不能从setInvulnerable字段宣称挡全部伤害。',
 '拒控反馈与实体转换/掉落/保存成功分别判定，避免因已播放close/portal就误记成功或Boss免疫；S2C文本不用恢复实体/模型系统，状态生命周期清理必须有实际结果依据。',
 'RecallBall全文、原生生产方法、注册和owner/tag方法已读。addAdditionalSaveData不等于完整save(entity UUID/乘客/位置等)，不冒称无损保存或真实重开通过。renderer/像素/外部Citadel收包未验；本条只研究最终拒伤和转换生命周期，不制作模型或清总待办。','native_lethal_attack_serialized_rescue_container')
k='domestication-native-bubble-break-source-denial-and-dismount-lock-lifecycle';keys.append(k)
record(k,r,common+[w('server/entity/GiantBubbleEntity.java'),w('server/entity/DIEntityRegistry.java'),f('server/CommonProxy.java',776,781),w('server/enchantment/PetEnchantmentLootOnly.java'),w('server/misc/DILootModifier.java'),w('server/misc/DILootRegistry.java'),data('data/domesticationinnovation/loot_modifiers/bubbling_enchanted_book.json'),data('data/forge/loot_modifiers/global_loot_modifiers.json')],
 '真实global loot列bubbling_enchanted_book，buried_treasure条件loot_type1→DILootModifier默认.65概率造BUBBLING书（treasure-only），原生collar交互启用。LivingAttack攻击者是tamed且bubbling>0、目标root vehicle非bubble且onGround/water/lava时建bubble，copyPosition，先target.startRiding(force=true)忽略结果，再setpopsIn(level*40+40)/addFreshEntity忽略结果、inflate声。',
 '计1：捕获壳的原生最终破壳准入与禁止下马政策整链；Bubble.hurt仅正伤IS_PROJECTILE或FELL_OUT_OF_WORLD才pop并true，其余false，非通用hurt=false→Bossimmune。pop先声音/server粒子，再ejectPassengers、discard；tick先上升，再pops<=0 pop否则decrement，计时字段同步+NBT。EntityMount在bubble alive时取消所有isDismounting，pop调用eject发生discard之前，须保留与该取消器交互的边界，未读vanilla强制eject内部故不推测玩家无法释放的运行bug。跟Ars Bubble任意伤害/乘客转伤与Wizardry恒重绑不同，这是来源限定释放与mount事件最终拒绝。',
 'Boss拒控必须在原生挂载前判定，不让取消伤害后仍被捕；灰字不由捕获失败/被泡壳拒伤推断。生命周期出口的物理释放与同帧可见回执需分别验，body动画仍原建模负责。',
 'Bubble全文、native event producer/EntityMount、真实loot JSON/config+modifier全文已读；模型/渲染/原生eject内部和TCP未读未验，不计普通上升/注册包装或每来源常量。无新增机制/游戏启动/资产修改。','native_capture_shell_break_source_and_dismount_denial')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch109-native-pet-window-recall-and-shell-release-admission','credited_chains':keys,'rationale':'Three independent final native policies: first-attempt armed future immunity; raw-lethal attack converted to UUID-owner serialized rescue container; capture shell break-source gate plus active dismount refusal. Guard old ledger credit0. Siphon mirrors existing Enigmatic distance-owner redirect => support0; Blazing producer resource filename mismatches actual global list => pending0; plain source/owner/effect constants and helpers0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
