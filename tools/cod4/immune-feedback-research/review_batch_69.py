"""Two final native Hurt policies: unconditional pet substitution and bounded retaliation."""
from ledger import B,O,record,verify
import json
r='Aizistral-Studios/Enigmatic-Legacy';p='src/main/java/com/aizistral/enigmaticlegacy/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
common=[f('handlers/EnigmaticEventHandler.java',2014,2343),f('EnigmaticLegacy.java',200,244),f('EnigmaticLegacy.java',246,252),f('registries/EnigmaticItems.java',22,24),f('registries/EnigmaticItems.java',442,549),w('registries/AbstractRegistry.java'),f('handlers/SuperpositionHandler.java',277,280),f('handlers/SuperpositionHandler.java',1146,1155)]
k1='enigmatic-native-distance-qualified-pet-damage-redirect-before-owner-settlement'
record(k1,r,common+[w('items/HunterGuidebook.java')],
 '实际EnigmaticLegacy注册EnigmaticEventHandler且loadClass实例化EnigmaticItems→DeferredRegister实际hunter_guidebook/PetGuidebook。完整原生onEntityHurt在后段TamableAnimal且isTame→owner为Player且inventory compartments有HunterGuidebook、owner与pet同world且distance<=config24→event.cancel，再owner.hurt同DamageSource和当前amount；有AnimalGuidebook则乘配置剩余默认50%。',
 '一个带同维距离和背包被动道具判定的原生宠物替伤生产点1，不按宠物/两个guidebook/包装拆。取消发生在owner.hurt之前且不检查结果，owner拒伤时宠物仍受保护；与Bewitchment必须替代活体实际承伤成功后才amount归零不同。没有消耗道具/耐久/cooldown，不是给宠物施加通用免疫状态。hasItem遍历原生inventory.compartments，不是Curios装备槽；不同维度或>24不保护，等于24包含。源DamageSource沿用，归属不重写，不能自动叫宠物Boss拒控。此前方法可能调整amount/甚至cancel，但本listener没有另加event.isCanceled防护；没有本分支声音/灰字producer。',
 'Boss拒控语义应生产于权威拒绝点，不将补偿方hurt结果或缺少伤害数字等同免控。跨实体转移链必须说明谁被保护、谁接收伤害，回执目标不能从source反推。',
 '固定a0294f119a0a84a4627b008bc90fe31808dbf596，完整330行onEntityHurt已按片段逐段全文读，注册/库存查询/配置全文已读。未跑原版damage事件重入或模组优先级，静态不证明最终数值/画面/TCP；未改正式代码/资产/TODO。','native_damage_redirection_settlement')
k2='enigmatic-native-cube-underlimit-random-cancel-retaliation-not-success-gated'
record(k2,r,common+[f('handlers/SuperpositionHandler.java',1322,1324),f('items/TheCube.java',66,89),f('items/TheCube.java',143,164),w('registries/EnigmaticSounds.java')],
 '同一完整native LivingHurt onEntityHurt最后：目标ServerPlayer且directSource为Living且Curios装备Cube→当前amount<=getDamageLimit(cursed150else100)并随机<=.35→cancel、directLiving.hurt沿用原DamageSource/currentAmount、再目标坐标play SWORD_HIT_REJECT；否则Cube.applyRandomEffect(directLiving,false)从实际debuff list选随机duration/amp addEffect。',
 '一个低于阈值概率拒伤+无条件报声/反伤的最终点1。与既有Cube LOW endEntityHurt的超阈整次拒绝是两个不同native listener和可触发负例，不能仅按同物品合并所有语义，也不因9个debuff或两阈值拆。超过阈值或随机失败仅对directLiving加随机debuff，本阶段不cancel，不能全算免疫。拒伤后不论攻击者hurt返回真假仍响拒绝声；source归属不重写，若native攻击者也是source.entity，则是以原归属向自己伤害，而非确认源已反转。无每目标/每攻击者节流、有限资源或事件序号，同次递归若满足其余条件仍需动态看pipeline。负面addEffect未检查接纳，不能以声/状态最终为空判断反伤或拒控成功。',
 '为Boss文字/嗡声设置明确拒控reason与一次回执；反伤结果、加debuff失败和声音生产独立，不能从任何一个反推其余已通过。保持普通阴阳体质type9边界。',
 '固定源码，完整native方法及随机选择/helper/构造debuff表/音注册已读；没有读音频资源或实机听音，不将原版SoundEvent提交当实际S2C感官通过。native阈值事件优先级组合与并发不静态宣称已验。未改正式Java/资产/任务。','native_final_damage_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'enigmatic-batch69-pet-and-cube-underlimit','credited_chains':[k1,k2],'rationale':'Pet按距离/同维+库存持物，无条件先拒后替伤；Cube另一个native Hurt点在低额随机拒绝并反击/报声。全方法内其他伤害buff、实体常量、随机debuff表、注册/音wrapper0。Cube超额LOW listener既有条目不重复。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
