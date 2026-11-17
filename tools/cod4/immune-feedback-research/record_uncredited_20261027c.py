"""Explicit zero-credit readings and incomplete chains; never promote by download count."""
from ledger import B,O,R
import json,hashlib
rows=[]
def z(k,r,paths,obs,why):
 root=B/'sources'/r.replace('/','__');m=json.loads((root/'source.json').read_text());refs=[]
 for rel in paths:
  p=root/rel
  if not p.exists():
   matches=list(root.rglob(p.name));assert len(matches)==1,(rel,matches);p=matches[0];rel=str(p.relative_to(root))
  refs.append({'source_path':rel,'path':str(p.relative_to(R)),'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':f'https://github.com/{r}/blob/{m["commit"]}/{rel}'})
 rows.append({'id':k,'repo':r,'commit':m['commit'],'research_credit':0,'source_refs':refs,'actual_observation':obs,'reason_not_credited':why})
r='Tslat/Advent-Of-Ascension';p='source/'
root=B/'sources'/r.replace('/','__')
paths=[str(x.relative_to(root)) for x in root.rglob('*.java') if x.name in ['HiveKingEntity.java','CrystocoreEntity.java']]
if paths:z('aoa-commented-boss-classes-not-live',r,paths,'两个完整实体类已读，类实现整体包在block comment内。','注释代码不当原生游戏实现，不能按Boss名填数。')
r='DivineRPG/DivineRPG';root=B/'sources'/r.replace('/','__');paths=[str(x.relative_to(root)) for x in root.rglob('*.java') if x.name in ['EntityKaros.java','EntityKingOfScorchers.java']]
if paths:z('divinerpg-explosion-filter-merged',r,paths,'两个完整实体类已读，hurt只加爆炸来源return false；Karos阶段声音/taunt不是拒绝receipt。','单一source常量筛选并既有家族0，不按实体外壳、阶段或声效重复。')
r='DaedalusGame/EmbersRekindled';p='src/main/java/teamroots/embers/'
z('embers-nonbeliever-partial-mitigation',r,[p+'item/ItemNonbelieverAmulet.java'],'完整类读：magic伤害>0.5时削减至max(0.5,amount*0.1)。','部分减伤非完全免疫，没独立拒绝/文字回执，本项0。')
z('embers-dawnstone-knockback-source-filter',r,[p+'item/ItemDawnstoneMail.java'],'完整类读：Baubles BODY装备项匹配后knockback strength置0。','单装备筛选并既有装备击退拒绝家族0。')
z('embers-ashen-loot-fx-not-refusal',r,[p+'item/ItemAshenAmulet.java',p+'network/message/MessageAshenAmuletFX.java'],'完整两类读：mob/block drops变灰，发坐标粒子和声音；非免伤事件。','战利品转换不属Boss拒控/受击回执，粒子包装不独立计数。')
r='klikli-dev/occultism';p='src/main/java/com/klikli_dev/occultism/'
z('occultism-upgraded-familiar-effect-constant-list',r,[p+'handlers/FamiliarEventHandler.java',p+'common/entity/familiar/BlacksmithFamiliarEntity.java',p+'common/entity/possessed/horde/WildSilverfishEntity.java'],'完整familiarEffectsImmunity方法已读：9个effect→type/upgrade/enabled匹配→DO_NOT_APPLY；完整Blacksmith类读升级AI/付金属；完整WildSilverfish是同trial tag直接/间接来源免伤。','不同effect/type/tag换壳与既有装备/阵营source filter并0；升级AI非combat回执不另计。大事件文件仅明确方法已读，不声称整文件全文。')
z('occultism-constant-fire-source-allies-merged',r,[p+'common/entity/possessed/AfritUnboundEntity.java',p+'common/entity/possessed/MaridUnboundEntity.java'],'完整Afrit类及Marid.isInvulnerableTo方法已读：固定来源和盟友tag筛选。','来源常量换壳0；Marid其余大类非完整阅读。')
z('occultism-headless-body-transition-not-immune',r,[p+'common/entity/familiar/HeadlessFamiliarEntity.java'],'完整actuallyHurt/mobInteract/revive方法读：先super扣血再在半血设deadvariant并发MessageHeadlessDie；集身体部件后revive重置/半血。','该分支不取消或回滚伤害；缺完整native packet consumer及tick/模型链，候选0，不接制作身体资产。')
r='TeamWizardry/Wizardry';p='src/main/java/com/teamwizardry/wizardry/'
z('teamwizardry-time-lock-dead-code',r,[p+'common/module/effects/ModuleEffectTimeLock.java',p+'common/potion/PotionTimeLock.java',p+'init/ModPotions.java'],'完整两TimeLock类均被comment整体包裹；ModPotions TIME_LOCK声明/初始化也注释。','无实际原生producer，不因UUID multimap/reverse时间样例晋级。')
z('teamwizardry-time-slow-refusal-not-complete-native-chain',r,[p+'common/module/effects/ModuleEffectTimeSlow.java',p+'common/potion/PotionTimeSlow.java',p+'api/events/SpellCastEvent.java',p+'api/spell/module/ModuleInstance.java',p+'common/item/ItemStaff.java',p+'proxy/CommonProxy.java',p+'asm/WizardryASMHooks.java',p+'asm/WizardryTransformer.java',p+'asm/WizardryCorePlugin.java',p+'common/network/PacketRenderSpell.java','src/main/resources/assets/wizardry/wizmodules/effect_time_slow.json','build.gradle'],
 '完整TimeSlow module/potion/event及核心cast/internal/sendRender方法读。静态onSpell用setSpellData(new SpellData)试图拒绝，但internalCastSpell仍run原spell，未读event.getSpellData，故不能当拒绝成功。Staff新rightclick timeScale0明确PASS，但已开始use的onUsingTick不查它。静态entityMove缩放事件参数，ASM move branch读完整，hook post后将x/y/z写回参数；amp>=19 scale0。Potion.onTick含特殊Dragon DYING例外/补tick但为instance方法，当前仅看到@Mod静态订阅；CommonProxy只显式注册ModuleEffectTimeSlow instance，未见PotionTimeSlow instance注册。',
 '保留实际消费者不采用替换payload的反例与native控制支持材料0；完整控制及全部加载入口/客户端库事件注册仍未核完，不能凭注解/方法名当原生全链成功。build manifest引用core_plugin但该属性本次尚未取得。声音为effect应用/去除，不是拒绝灰字。')
z('teamwizardry-telekinesis-and-sonic-support',r,[p+'common/module/effects/ModuleEffectTelekinesis.java',p+'common/module/effects/ModuleEffectSonic.java',p+'common/potion/PotionNullMovement.java'],
 '3个完整类读：telekinesis每目标扣费后先写motion再加nullgravity，未接Boss policy；Sonic临时hurtResistantTime0调用伤害再还原，忽略boolean；NULL_MOVEMENT client tick替换MovementInput并在结束时重建默认input。',
 '直接运动/伤害包装及输入临时替换与既有家族支持合并0，缺本项独立最终免控/免伤或显式拒绝receipt，不按粒子和效果名增加。')
r='lender544/new1.20.1';p='src/main/java/com/github/L_Ender/cataclysm/entity/'
z('cataclysm-simple-filter-and-existing-parry-family',r,[p+'InternalAnimationMonster/Coralssus_Entity.java',p+'InternalAnimationMonster/AcropolisMonsters/Clawdian_Entity.java'],'完整Coralssus.hurt只HOT_FLOOR拒伤；Clawdian.hurt先canBlock声效returnfalse，再rider来源排除/回血延迟/成功hit backstep。','伤害常量及既有方向招架/搭载来源家族0，未读完整canBlock native stateproducer，不能按新mob名扩数。')
r='Sweenus/SimplySwords';p='common/src/main/java/net/sweenus/simplyswords/'
z('simplyswords-magislam-window-merged',r,[p+'world/MagispearAbilityManager.java'],'完整blocksIncomingDamage方法读：world ownerUUID活动map、非rooted、age在LEAP_START到impactTick范围且非bypass时true。','动作窗口免伤并既有phase family0，尚未核其native起跳/终止与final消费者，保持支持材料。')
(O/'uncredited-observations-20261027c.json').write_text(json.dumps({'effective_added':0,'observations':rows,'note':'References are provenance containers; complete reading claims apply only to explicitly stated classes/methods. No automatic promotion.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'zero_credit_observations':len(rows),'effective_added':0}))
