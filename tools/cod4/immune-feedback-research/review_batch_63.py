"""Etherium native low-health full-set rejection, not an inferred deflection."""
from ledger import B,O,record,verify
import json
r='Aizistral-Studios/Enigmatic-Legacy';p='src/main/java/com/aizistral/';k='enigmatic-etherium-native-health-threshold-projectile-refusal-and-double-melee-cue'
def w(f):
 f=p+f
 return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
record(k,r,[w('etherium/core/EtheriumEventHandler.java'),w('etherium/items/EtheriumArmor.java'),(p+'enigmaticlegacy/config/EtheriumConfigHandler.java',49,68),(p+'enigmaticlegacy/config/EtheriumConfigHandler.java',160,177),(p+'enigmaticlegacy/config/EtheriumConfigHandler.java',234,237),w('enigmaticlegacy/objects/Perhaps.java'),(p+'enigmaticlegacy/EnigmaticLegacy.java',200,244),(p+'enigmaticlegacy/registries/EnigmaticItems.java',170,184),(p+'enigmaticlegacy/registries/EnigmaticItems.java',479,482),(p+'enigmaticlegacy/handlers/SuperpositionHandler.java',1333,1335)],
 '实际EnigmaticLegacy constructor注册EtheriumEventHandler且初始化config/EnigmaticItems；四槽EtheriumArmor实际注册→hasFullSet严格getClass==EtheriumArmor，全套且currentHP/maxHP<=config阈值→native server LivingAttackEvent仅AbstractArrow/AbstractHurtingProjectile direct源最终cancel+盾触发声；另native LivingHurtEvent在同状态按配置乘剩余比例，directLiving源击退attacker并连续两次playSound。',
 '一个低血量全套原生最终裁决家族1，四槽/两弹类/后段partial与音包装不拆。默认阈值40%、Hurt减伤50%，ArchitectFavor分支可覆阈值；无每目标cooldown/资源消耗，临界HP<=包含边界，全套按class精确相等不含子类。Attack分支注释deflection但没反向/owner改写，仅cancel；不能宣称反弹成功。Hurt对directLiving判定后cast source.entity为Living，若异常伤害源的direct与entity归属类型不一致，静态未防护。触发声同一方法重复提交两次，不是可靠单次回执或节流；Hurt不代表全拒，可能仍伤50%，不可显示Boss免疫。',
 'Boss只在实际控制拒绝时广播一次语义回执；同状态多层伤害事件/重复音调用需去重，不从注释“deflection”推反射。阈值和精确实体/装备类型应形成负例，不能只看护罩状态。',
 '固定a0294f119a0a84a4627b008bc90fe31808dbf596，包含核心方法/实际原生注册、hasShield与配置getter已读。ArchitectFavor的专属身份判据链、完整config基础设施及音资源内容非本项新增有效，仅记录getter覆写而不声称全部特殊身份已验。未验渲染/双端/实际音质；无正式代码、模型资产或待办修改。','native_final_damage_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'enigmatic-etherium-batch63','credited_chains':[k],'rationale':'不同于既有永久spellstone来源列表或概率nebula，当前HP比例+严格全套决定实际原生拒弹/后段减伤；四槽/弹类别/声音wrapper与同状态partial合1。未用配置项数或上游疑似重复声缺陷另加数。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
