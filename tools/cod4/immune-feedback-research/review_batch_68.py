"""Actual brew data/native use and three independent defensive status policies."""
from ledger import B,O,record,verify
import json
r='Moriyashiine/bewitchment';p='src/main/java/moriyashiine/bewitchment/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def res(s):
 s='src/main/resources/'+s
 return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
common=[w('common/registry/BWStatusEffects.java'),w('common/registry/BWRecipeTypes.java'),w('common/recipe/CauldronBrewingRecipe.java'),f('common/block/entity/WitchCauldronBlockEntity.java',133,167),f('common/block/entity/WitchCauldronBlockEntity.java',248,342),f('common/block/entity/WitchCauldronBlockEntity.java',344,384),f('common/block/WitchCauldronBlock.java',56,66),f('common/block/WitchCauldronBlock.java',96,163),f('common/registry/BWObjects.java',229,229),f('common/Bewitchment.java',61,222),w('common/BWMixinPlugin.java'),res('fabric.mod.json'),res('bewitchment.mixins.json')]
base='真实注册的BWStatusEffects和CauldronBrewingRecipe类型→固定配方JSON→WitchCauldron原生tick接ItemEntity/insertStack选recipe.input（不是调用恒false的Recipe.matches）→BREWING模式getPotion产生原版POTION+CustomPotionEffects，原生onUse玻璃瓶在server取出/支付首瓶altar资源→原生LivingEntity防御注入/状态tick消费实际effect。'
limits='固定842cd9777b7bde2a0208099d5184baf88f24f63a，完整关键native方法/原始配方/注册与mixin启用已读；共享酿药/注册链0额外。原版PotionItem服用后续未逐行另读/未运行，不以静态代替自然获取或画面/声音实机。altar底层能量和视觉渲染不计本项，未改正式源码/模型/贴图/TODO。'
k1='bewitchment-native-ethereal-bilateral-combat-nullification-with-bypass-exception'
record(k1,r,common+[f('mixin/brew/LivingEntityMixin.java',71,90),w('common/statuseffect/EmptyStatusEffect.java'),res('data/bewitchment/recipes/cauldron_brewing/ethereal.json')],base+'ETHEREAL为NEUTRAL EmptyStatusEffect，ectoplasm配方200ticks；applyArmorToDamage HEAD在server且非BYPASSES_INVULNERABILITY，受害者有ETHEREAL或source.attacker是持ETHEREAL的Living时把amount返回0。',
 '一个双向战斗脱离的原生最终amount归零点1。并非只保护受效果者：有此effect的施加攻击者也无法对无effect目标造成此阶段伤害；按attacker判，非direct projectile判。BYPASS源放行。两端都不要求Player/Boss或阵营，不能当Boss专属免控；没有拒绝控制效果的代码，亦没有灰字/声音producer。返回0不是damage HEAD callback false，其他注入的相对执行顺序/后续改amount未在本条动态验证。ENCHANTED四分之一+amp与MAGIC_SPONGE部分转魔力不另计或冒称免疫。',
 'Boss控制免疫只绑定目标是否确实拒绝此次控制，不能将施加者状态导致攻击无效误标目标免疫。必须区分source.attacker与direct entity、amount归零与最终事件拒绝，不能依单一布尔结果泛发灰字。',limits,'native_final_damage_refusal')
k2='bewitchment-native-arrow-deflection-cancel-with-positive-velocity-rescale'
record(k2,r,common+[f('mixin/brew/LivingEntityMixin.java',92,121),w('common/statuseffect/EmptyStatusEffect.java'),res('data/bewitchment/recipes/cauldron_brewing/deflection.json')],base+'DEFLECTION注册为BENEFICIAL；phantom_membrane配方600ticks。native server damage HEAD当受害者有effect且directSource在ARROWS tag时，每速度分量乘2*(amplifier+1)，callback.setReturnValue(false)阻止此方法余下伤害。',
 '一个原生箭源拒绝并改写箭运动的最终点1，不按箭变体/amp/xyz拆。实际乘数为正数，没有反向，owner也不改，因此注释/名称deflection不能证明反射回发射者；与既有Ars Bounce的向量反转/所有者处理不同，记录真实正向加速拒伤规则而非把类名换壳算1。这个分支先于amount>0/hurtTime==0的else，零amount或正在受击也会拒箭/改速度；没有BYPASS例外、每箭命中历史或按目标节流，重复调用会重复缩放。非箭tag即使是投射物也不满足。未看到此分支显式同步速度或单独反馈包，不声称观察端实际看见加速。',
 'Boss回执中“弹开微光”须由明确拒控语义触发；不能用一个叫deflection的函数当弹开完成证据。相同来源连续事件须去重，否则逻辑修改、文字与声音可能逐次累积。',limits,'native_projectile_refusal_settlement')
k3='bewitchment-native-purity-budget-decrements-harmful-and-own-amplifiers'
record(k3,r,common+[w('common/statuseffect/PurityStatusEffect.java'),res('data/bewitchment/recipes/cauldron_brewing/purity.json')],base+'PURITY实际注册为PurityStatusEffect；原生canApplyUpdateEffect恒true，但applyUpdateEffect只server且entity.age%20==0遍历注册effects，对当前存在的HARMFUL状态，取当前Purity，移自身并在amp>0时按原duration重加低一级；移该负面并在其amp>0时重加低一级。',
 '一个由自身状态等级付费的延迟减层/清除实现1，不是所有负面常量各1，也不与Tinkers一次性按效果tag全清解药合并。同tick每处理一个HARMFUL都会重新查Purity，amp0消耗后后续效果不处理；注册表顺序影响哪个先被清。负面amp>0仅降一级不会消失，自身剩余duration保留，没有延长到新总时长。age模20是实体时钟不是效果age，不保证施加后等整20tick。HARMFUL可能含控制但代码没有Boss拒控、首次应用否决或回执，不可将后续状态被减层当免疫触发。',
 '验收Boss免控须在控制准入时核对明确拒绝，不能等下一轮清理发现无状态就判通过。若依状态去重，消耗/自然到期/减层应与“本次被拒绝”分开；避免把这种净化成功向普通阴阳体质强加灰字。',limits,'native_status_rejection_vs_removal_lifecycle')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'bewitchment-batch68-three-native-status-policies','credited_chains':[k1,k2,k3],'rationale':'双向ETHEREAL在armor amount归零；DEFLECTION原生damage HEAD拒箭+正向加速；PURITY原生periodic tick用自身amp付费减负面层。三不同最终消费点，全部recipe/常量/amp/包装0，不以负面状态最终为空证明Boss拒控。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
