"""Persist actual zero-credit/partial/merged observations, never promote regex candidates."""
from ledger import B,O,R
import json,hashlib
rows=[]
def add(key,repo,patterns,observation,reason):
 root=B/'sources'/repo.replace('/','__');m=json.loads((root/'source.json').read_text());refs=[]
 for pattern in patterns:
  matches=list(root.rglob(pattern));assert matches,(repo,pattern)
  for p in matches:
   rel=p.relative_to(root).as_posix();refs.append({'source_path':rel,'path':str(p.relative_to(R)),'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':f'https://github.com/{repo}/blob/{m["commit"]}/{rel}'})
 rows.append({'id':key,'repo':repo,'commit':m['commit'],'research_credit':0,'source_refs':refs,'actual_observation':observation,'reason_not_credited':reason})
add('ars-elemental-control-effects-support-only','Alexthw46/Ars-Elemental',['*Nullify*.java','*Order*.java','*WaterGrave*.java','*Repel*.java','*Enderference*.java','*Enthrall*.java'],
 '此前完整效果方法审阅：Nullify重置iframe而非通用免疫覆盖；Enthrall移除效果路径清key但外部工具未补；HYMN原生获取producer尚缺。',
 '只作支持/候选，不能把效果类数视作完整免控链或按effect名加数；大事件文件只认实际已读方法。')
add('werewolves-fur-arrow-movement-conditions-not-complete-gain-chain','TeamLapen/Werewolves',['ModPlayerEventHandler.java'],
 '完整ModPlayerEventHandler已读：wolfpawn/fur tag、移动时箭awareness概率、冲刺movementTactics条件取消。',
 '实际技能获得及启用注册未补齐，本项0，不按技能或伤害常量扩数。')
add('botania-equipment-and-entity-source-variants-merged','VazkiiMods/Botania',['EquestrianVirusItem.java','CrimsonPendantItem.java','PixieEntity.java'],
 '三个完整类已读：EquestrianVirus变异坐骑及骑乘防摔；CrimsonPendant固定火伤装备筛选；Pixie目标类型筛选。Diva/Thunder已入主账，其他包装0。',
 '原生骑乘/装备筛选与既有家族合并；坐骑转换本身不属拒控文字。')
add('alexsmobs-native-hurt-filters-insufficient-or-merged','AlexModGuy/AlexsMobs',['EntityMimicube.java','EntityRockyRoller.java','EntityMurmurHead.java'],
 '完整相关hurt方法已读：Mimicube在super hurt前复制装备；RockyRoller有DamageSource.equals字符串比较及仍调用super的反击；MurmurHead尝试parent.hurt(.5)失败退回head super。',
 '未补parent身份/生产链；装备复制非免控，反击不代表拒伤，不能按mob名计数。')
add('goety-endersent-deflection-producer-support-merged','Polarice3/Goety-2',['Endersent*.java','VoidKeyItem.java','SummonCircleBoss*.java','PotionEvents.java'],
 '完整VoidKey/SummonCircleBoss及Endersent finalizeSpawn/eyeTypeEffects/addEyeEffects/aiStep/tick关键方法已读；实际特眼赋DEflective。PotionEvents.onDeflectImpact和MobUtil.deflect完整已读：概率通过后redirect需有shooter，null shooter仍会取消impact。',
 '与既有反弹家族合并0；未把不同眼名/概率/粒子包装拆数。引用文件容器不代表大类整文件全文。')
add('cyclic-beekeeper-steady-and-pearl-merged','Lothrazar/Cyclic',['BeekeeperEnchant.java','SteadyEnchant.java'],
 '完整Beekeeper/Steady已读：Bee/bat/spit/phantom不同来源装备拒绝，Bee另清aggression；Steady为装备击退常量。珍珠通用传送不属战斗回执；Soulstone body未补。',
 '来源/装备换壳并既有家族0；不将尚未补正文Soulstone算完成。')
add('cataclysm-remaining-phase-and-source-filters-merged','lender544/new1.20.1',['Ender_Golem_Entity.java','Ender_Guardian_Entity.java','Ancient_Remnant_Entity.java','Maledictus_Entity.java','Netherite_Monstrosity_Entity.java'],
 '完整各hurt方法已读：Golem半伤、Guardian头盔阶段、Remnant睡眠/箭phase、Maledictus31–33、Monstrosity觉醒窗口；另Kobo箭乘1.5非反弹。',
 '单phase/source常量家族并0。只读hurt而非各大实体类整篇，未补其他原生phase生产时不能按新Boss名扩数。')
add('psi-debug-visual-and-motion-support-only','Vazkii/Psi',['PieceTrickDebugSpamless.java','MessageVisualEffect.java','AdditiveMotion*.java'],
 '已读PieceTrickDebugSpamless、MessageVisualEffect、AdditiveMotionHandler全文：spamless入口用于debug；未取得MessageSpamlessChat，不声称其全文已读。VisualEffect制作场景，motion WeakMap在worldtick应用再clear、未按entity.world筛选。',
 '非Boss战斗拒绝或native控制预测链未补，基础包装0；已入账IMMUNE_TARGET整链不再拆。')
add('alexscaves-multipart-relay-trust-not-complete-immune','AlexModGuy/AlexsCaves',['HullbreakerPartEntity.java','MagnetronPartEntity.java','MultipartEntityMessage.java'],
 '三类全文已读：client part发送parent/entity/source float并returnfalse；handler enqueue currentlevel，parent multipart、actor<16，处理interact或generic伤害float。未校验sender==interacter及维度UUID/finite值。',
 '客户端分体false是转发协议而非Boss免控。native server父生产链未补，通用proxy并已有家族0。')
add('alexscaves-other-effects-and-projectile-receipts-merged','AlexModGuy/AlexsCaves',['WaterBoltEntity.java','LivingEntityMixin.java'],
 '完整WaterBolt tick87–157、onHit202–214、damageMobs216–236及LivingEntityMixin全文已读：hurttrue后BUBBLED addEffect忽略bool并发type1，不能证明status已接纳；SeaStaff实际producer未补。',
 '普通效果过滤/减伤并已有家族，项目配置/原生获取链未补，不加credit。')
add('wizardry-forfeit-clairvoyance-arcanejammer-support-only','Electroblob77/Wizardry',['Forfeit.java','Clairvoyance.java'],
 '完整Forfeit/Clairvoyance类已读。前者效果及随机Pre取消仍缺同步工具的实际消费者；ArcaneJammer Illager反射native AI未补。',
 '未把大文件行数/效果名数量当研究数，边界不完整保持0。')
add('aoa-additional-commented-bosses-zero','Tslat/Advent-Of-Ascension',['ShadowlordEntity.java','CottonCandorEntity.java','BaronessEntity.java'],
 '三类全文已读，核心类实现整体包在block comment内。',
 '不是活代码，0；与旧Crystocore/HiveKing记录并存而非新晋级。')
add('aoa-tyrosaur-armor-text-version-chain-incomplete','Tslat/Advent-Of-Ascension',['TyrosaurEntity.java','TESIntegration.java','IntegrationManager.java','SkullPlateMultipart.java','AoAEntityPart.java'],
 'Tyrosaur341行全文、TESIntegration和IntegrationManager全文、两分体类全文已读。armor600，非environment/nonbypass按投射物/镐/爆炸比例累加armor伤害，条件TES集成灰色数字在clamp前产生，并仍super.hurt；updateArmour改armor/toughness、4阶段crumble粒子声。SkullPlate非近战false/投射物cross方向偏转，MultipartBuilder/collision最终消费者未补。',
 '灰色护甲数字不是免控文字；AoA依赖net.tslat.tes，现有TES快照net.tslat.tslatentitystatus API不匹配，不能拼假完整版本链。matching来源/真实multipart碰撞未补前0。')
add('illages-constant-mitigation-clone-and-hay-protection-zero','TheDarkPeasant/Illage-and-Spillage--Respillaged',['AbsorberEntity.java','PreserverEntity.java','FakeMagispellerEntity.java','PreservedEffect.java','WebbedEffect.java','DisabilityEffect.java'],
 '上述完整六类已读，ForgeEventBusSubscriber全文亦读。Absorber cap/强制1不是免伤，onHurt重置iframe；Preserver跳落上PRESERVED无限状态、受击半伤/加KB抗而非完全拒伤，粒子先于admission成功判定。FakeMagispeller状态全拒/受击hurtTime10自杀，正常hurtbody不等于Boss无敌；Webbed -80%基移速且无milk cures，Disability为空效果。',
 '部分减伤/状态常量/幻象对象清理不冒充本任务Boss拒控链，不能按六文件加6。Magispeller伤害预算和专门声音锚定另入主账。')
(O/'uncredited-observations-20261027d.json').write_text(json.dumps({'effective_added':0,'note':'Only explicitly described whole classes/methods were read. References are containers, not whole-file reading claims. Prior sources and native cases retained; no candidates auto-promoted.','observations':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'saved_zero_credit_observations':len(rows)}))
