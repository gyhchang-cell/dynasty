"""Three actual independent Enigmatic native rejection producers, wrappers merged."""
from ledger import B,O,record,verify
import json
r='Aizistral-Studios/Enigmatic-Legacy';p='src/main/java/com/aizistral/enigmaticlegacy/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
base=[(p+'EnigmaticLegacy.java',212,220),(p+'EnigmaticLegacy.java',236,236),w(p+'registries/AbstractRegistry.java'),(p+'handlers/EnigmaticEventHandler.java',1692,1898)]
def add(k,refs,c,o,l):
 for f,a,z in base+refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
 record(k,r,base+refs,c,o,l,'固定本地source.json commit及Git tree/blob、SHA源，原生onEntityAttacked完整方法及本条实际关键链已读；泛用注册、Curios外部查询/原生teleport实现内部辅助0，静态不证明游戏像素/听感/TCP。无正式源码/资产/TODO改动，不启动游戏。','native_final_damage_denial');keys.append(k)
add('enigmatic-native-molten-heart-effect-preempts-remaining-attack-listeners',[w(p+'effects/MoltenHeartEffect.java'),w(p+'registries/EnigmaticEffects.java'),(p+'registries/EnigmaticPotions.java',70,72),(p+'registries/EnigmaticPotions.java',100,102),(p+'items/UltimatePotionBase.java',100,135),(p+'helpers/PotionHelper.java',40,89),(p+'helpers/PotionHelper.java',104,106),(p+'helpers/PotionHelper.java',208,225),(p+'EnigmaticLegacy.java',275,284)],
 '真实MoltenHeart effect注册、实际AdvancedPotion定义和酿造配方→native UltimatePotionBase.finishUsingItem服务器从NBT potion id解析效果并addEffect→native server Player LivingAttack：hasEffect且providesImmunity匹配LAVA/IN_FIRE/ON_FIRE/HOT_FLOOR，立即cancel并return；effect每tick clearFire。',
 '独立临时效果寿命内的最终拒伤门1，不按四来源/三种时长/药瓶包装拆。return跳过本handler后续免疫/闪避/火quota逻辑，不等于停止其他mod的所有监听。clearFire并未在此阻止温度/其他移动状态；这个源list不是所有IS_FIRE标签。药水addEffect bool忽略，不能把饮用动作当已接纳；native拒伤实际hasEffect才通过。此链无专门灰字/闪光/嗡声，fog配置不是战斗回执。酿造在大注册method内的相关实际定义已观察，非全量上游启动/配方可获取实机证明。',
 '临时免疫策略与资源型防御分开，明确拒控再派反馈；提前return的优先级不得遮蔽其他应播回执。')
add('enigmatic-native-equipped-spellstone-damage-source-list-cancel',[w(p+'items/generic/ItemSpellstoneCurio.java'),(p+'handlers/SuperpositionHandler.java',210,228),(p+'items/AngelBlessing.java',82,91),(p+'registries/EnigmaticItems.java',458,464)],
 '真实AngelBlessing注册构造填FALL/FLY_INTO_WALL immunityList→native Player LivingAttack取实际Curios inventory里ItemSpellstoneCurio列表→每item immunityList.anyMatch(source::is)则cancel，继续遍历。',
 '装备来源清单裁决1，所有spellstone/来源表值不拆；不是效果型MoltenHeart门：真实装备槽而不是临时hasEffect，且cancel后不return。公开isImmuneTo(String)以String查ResourceKey列表不匹配，但原生监听直接anyMatch正确使用ResourceKey，不拿未接活String helper算额外错误/研究。rawCurios迭代未查native activeStates/组件disabled，配置multiequip只在canEquip门不等于遍历时做最终合法性重审。没有独立反馈/目标节流。MAGENTA低落伤阈值是同事件另常量门，未额外credit。',
 '免疫资格来源要明确，不能把可装备配置/文字颜色当拒控语义；同来源清单和实体常量不凑数。')
add('enigmatic-native-nebula-dodge-denial-independent-of-teleport-success',[(p+'items/EyeOfNebula.java',43,101),(p+'registries/EnigmaticItems.java',458,458),(p+'handlers/SuperpositionHandler.java',277,280),(p+'handlers/SuperpositionHandler.java',533,596),w(p+'packets/clients/PacketPortalParticles.java'),w(p+'packets/clients/PacketRecallParticles.java'),(p+'EnigmaticLegacy.java',347,355)],
 '实际EyeOfNebula物品及默认15%/DodgeRange16配置→native LivingAttack已非canceled/装备真存在/roll成功/原invulnerableTime<=10/source.entity Living→最多33次validTeleportRandomly寻找实心地上两空格→成功点附近Portal/Recall包+原版teleport声/原生teleport调用→无论33次是否成功均invulnerableTime20并cancel当前伤害。',
 '一个独立概率闪避最后拒绝生产点1，33次候选/上下搜索/声包渲染wrapper合并不拆。失败搜索也免伤且无teleport声光，不能把无粒子判未触发；validTeleport true在void teleport后返回，未单独读原生最终传送事件/重定位，不能保证旁路mod下真移位。坐标int强转负数向0不是floor。包出生坐标不跟随目标，无UUID/dimension/generation/finite/countcap/nullPlayer防护；for<=amount实际数量+1，check=false忽略quality倍率。两声源位置传送前后各一次，不能代替Boss嗡声，且没有逐目标冷却字段(原生20tick窗口可再触发条件<=10)。不新增普通体质灰字。',
 '拒控事实与回放成功要分层；以明确server拒绝语义生灰字，用自己的按目标窗口统一节流文字/闪光/嗡声，不把可见传送当免疫唯一证据。')
f=O/'semantic-dedup.json';x=json.loads(f.read_text());x['groups'].append({'family':'enigmatic-native-batch44','credited_chains':keys,'rationale':'临时效果最终拒伤、装备来源表最终取消、概率闪避/位置搜索结果独立于拒伤各1；所有来源/稀有度/时长、teleport/粒子包装0。KNOCKBACK_THAT_BASTARD只是攻击增强且无本项独立免控/反馈，0。'});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');verify()
