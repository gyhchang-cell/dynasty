"""BloodMagic real effect damage gate; bounce merged into existing Ars family, no new credit."""
from ledger import B,O,record,attach_auxiliary,verify
import json
r='WayofTime/BloodMagic';p='src/main/java/wayoftime/bloodmagic/'
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
base=[(p+'BloodMagic.java',130,135),(p+'BloodMagic.java',145,160),(p+'common/item/BloodMagicItems.java',390,392),(p+'common/item/potion/ItemAlchemyFlask.java',166,198),w(p+'potion/PotionBloodMagic.java')]
key='bloodmagic-native-obsidian-cloak-amplifier-gated-nonmagic-mitigation'
record(key,r,base+[(p+'util/handler/event/GenericHandler.java',216,275),(p+'potion/BloodMagicPotions.java',30,32),(p+'common/recipe/PotionRecipeProvider.java',59,59)],
 '实际注册效果/炼金药瓶，native finishUsingItem服务器从瓶中PotionUtils效果addEffect→已注册GenericHandler原生LivingHurt完整方法先结算攻击/盔甲，最后检查非DamageTypes.MAGIC且目标hasEffect(OBSIDIAN_CLOAK)→setAmount(amount*max(0,1-.2*(amp+1)))。',
 '这是临时效果随等级缩减的独立最终伤害结算点1；不是按伤害常量/等级拆分。amp0只是80%伤害，amp4以上数学上归零，不取消事件且不拒控；原生配方声明实际观察到HARD_CLOAK+diamond/crying_obsidian转换，但未读完整炼金容器配方执行链/等级升级可达上限，不声称正常获取到全免。仅排除精确MAGIC，不是所有魔法标签。瓶addEffect结果未检查，真正拒减伤入口以hasEffect为准。没有特定拒绝回执、按目标节流、S2C灰字、微光或嗡声。LivingArmor各source lambda和ProjectileArmorProvider空TODO不另计。',
 '灰字须来自当前控制明确被拒，不能把临时减伤百分比/最终0伤推为Boss免控；资源/等级/来源要在裁决语义里区分。',
 '固定source.json提交及Git blob核验，全包含方法和实际事件登记已读；配方行仅实际定义，不代表完整可获取实机。无游戏、正式源码、资产或待办改动。','native_damage_mitigation_not_control_immunity')
attach_auxiliary('ars-bounce-fall-source-avoidance-and-next-tick-motion',r,base+[(p+'util/handler/event/GenericHandler.java',102,145),(p+'potion/BloodMagicPotions.java',30,31),(p+'common/recipe/PotionRecipeProvider.java',44,44)],
 '全文观察BloodMagic原生Bounce：Player效果时总damageMultiplier0，非蹲且distance>1.5客户端反转Y入UUID map，服务器cancel；END tick消费map恢复Y。与已计Ars/Tinkers fall source取消+下一tick恢复Y同家族，只有阈值/队列形式/范围差异，主审0新增。效果瓶实际执行及注册为辅助，不转守卫旧账。')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'bloodmagic-batch45','credited_chains':[key],'merged_zero':['BloodMagic Bounce -> ars-bounce-fall-source-avoidance-and-next-tick-motion'],'rationale':'Obsidian amplifier结算独立1；Bounce完整读取但fall/下一tick恢复同家族0；未接活空armor TODO0。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
