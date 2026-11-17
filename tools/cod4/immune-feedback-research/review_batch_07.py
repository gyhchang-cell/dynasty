from ledger import record,verify,B
p='src/main/java/com/robertx22/mine_and_slash/'
repo='RobertSkalko/Mine-And-Slash-Rework'
files={
'mmorpg/MMORPG.java':(190,210),'mmorpg/event_registers/CommonEvents.java':(48,320),
'event_hooks/damage_hooks/reworked/NewDamageMain.java':(9,86),
'event_hooks/damage_hooks/OnPlayerDamageEntityEvent.java':(15,86),
'event_hooks/damage_hooks/LivingHurtUtils.java':(42,104),
'capability/entity/EntityData.java':(445,486),
'uncommon/effectdatas/EventBuilder.java':(36,41),
'uncommon/effectdatas/EffectEvent.java':(156,251),
'database/data/stats/types/defense/DodgeRating.java':(74,114),
'database/data/stats/effects/defense/SpellDodgeEffect.java':(1,60),
'uncommon/effectdatas/rework/EventData.java':(88,93),
'uncommon/effectdatas/DamageEvent.java':(584,765),
'a_libraries/dmg_number_particle/particle/InteractionNotifier.java':(1,16),
'mmorpg/registers/client/S2CPacketRegister.java':(15,38),
'vanilla_mc/packets/interaction/ExileInteractionResultPacket.java':(1,60),
'vanilla_mc/packets/interaction/IParticleSpawnMaterial.java':(29,63),
'a_libraries/dmg_number_particle/particle/InteractionResultHandler.java':(1,121),
'a_libraries/dmg_number_particle/particle/ExileInteractionResultParticle.java':(1,64),
'a_libraries/dmg_number_particle/particle/impl/DamageNullifiedParticle.java':(1,43),
'a_libraries/dmg_number_particle/particle/style/Default.java':(1,106),
'a_libraries/dmg_number_particle/particle/style/Row.java':(1,118),
'a_libraries/dmg_number_particle/RenderUtils.java':(1,36),
'uncommon/interfaces/IAutoLocName.java':(1,46),
'uncommon/localization/Words.java':(375,411),
}
# Entire methods were read; clipping reference end to actual closing file line avoids blank-line differences.
refs=[]
root=B/'sources'/repo.replace('/','__')
for rel,(a,b) in files.items():
 q=root/(p+rel)
 if not q.exists():
  matches=list(root.rglob(rel.rsplit('/',1)[-1]));assert len(matches)==1,(rel,matches);q=matches[0]
 refs.append((str(q.relative_to(root)),a,min(b,len(q.read_text().splitlines()))))
record('mineandslash-native-nullified-receipt-particle',repo,refs,
 'MMORPG注册CommonEvents和S2C；CommonEvents→NewDamageMain注册DAMAGE_BEFORE_CALC消费者→OnPlayerDamageEntityEvent.accept（finally解除递归锁）→LivingHurtUtils.tryAttack/onAttack→无武器原生分支EntityData.unarmedAttack→EventBuilder.ofDamage/build→EffectEvent.Activate完整调度与calculateEffects→目标DodgeRating/SpellDodgeEffect.setHitAvoided→DamageEvent.activate取消原伤害并发显式DODGE/RESIST回执。InteractionNotifier只发攻击者ServerPlayer；注册的ExileInteractionResultPacket编解码实体ID和枚举→客户端配置门→当前level实体查找→nullified策略→原生ParticleEngine.add→CUSTOM DamageNullifiedParticle.render/tick→Default/Row→RenderUtils.font.drawInBatch。所有策略、元素数字、包装和语义枚举合并1条。',
 '明确拒绝判定即使无HP变化也能发文字；取消/友伤/死亡等其他提前返回没有一概冒充闪避回执。当前DODGE/RESIST选择依据attackType.isAttack，不是直接序列化IS_BLOCKED/IS_DODGED，不能照搬成精确Boss免控理由。文字WHITE非灰色；每帧type.text.getString，locName经外部CLOC.blank（外部翻译契约未验证）。随机目标眼高出生后独立粒子，不持续跟随目标；Default寿命15–19tick/Row20tick，共享ParticleGroup容量1000，非语义节流或每目标去重；Default有SHIELD_BLOCK原版声音，Row分支没有相同播放。RenderUtils明确GL_ALWAYS深度而非受墙遮挡；相机距离向量限制6不是6格外剔除。数据仅entityId，无维度/UUID/代际字段，接收端无显式缺失实体保护；这些为静态风险边界，不报成已复现故障。',
 '拒控回执必须在权威语义分支生产，并保留原因边界；现有原版盾声音可作为参考，不要求录音。目标锚定、缺失目标防护、逐目标节流与世界生命周期需要分别审查，不能以全局粒子上限代替“不刷屏”。普通角色闪避参考不赋予普通阴阳体质灰字要求。',
 '完整读本模组所列方法和调用链，事件/包底层Library of Exile及Minecraft粒子生命周期止于外部平台契约；未编译或启动游戏。旧DamageParticleRenderer.renderParticle无条件return、旧sendDamageParticle调用注释均不计有效显示。武器mechanic和其他所有技能调用未逐项认证，不据此声称覆盖全部来源。','explicit_rejection_floating_text')
verify()
