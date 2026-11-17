"""Native smeltery adaptive-source refusal and success-gated conversion, not generic library credit."""
from ledger import B,O,record,verify
import json
r='SlimeKnights/TinkersConstruct';p='src/main/java/slimeknights/tconstruct/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def data(s):
 s='src/generated/resources/'+s
 return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
k='tconstruct-native-adaptive-smeltery-source-final-immunity-before-success-gated-fluid-conversion'
record(k,r,[f('smeltery/TinkerSmeltery.java',294,304),f('smeltery/TinkerSmeltery.java',338,338),w('smeltery/block/controller/SmelteryControllerBlock.java'),w('smeltery/block/entity/controller/SmelteryBlockEntity.java'),f('smeltery/block/entity/controller/HeatingStructureBlockEntity.java',74,78),f('smeltery/block/entity/controller/HeatingStructureBlockEntity.java',115,115),f('smeltery/block/entity/controller/HeatingStructureBlockEntity.java',230,289),f('smeltery/block/entity/controller/HeatingStructureBlockEntity.java',524,537),f('smeltery/block/entity/controller/HeatingStructureBlockEntity.java',686,688),w('smeltery/block/entity/module/EntityMeltingModule.java'),w('library/recipe/entitymelting/EntityMeltingRecipeCache.java'),f('common/TinkerDamageTypes.java',19,22),f('common/TinkerDamageTypes.java',88,102),data('data/tconstruct/damage_type/smeltery_heat.json'),data('data/tconstruct/damage_type/smeltery_magic.json'),data('data/minecraft/tags/damage_type/is_fire.json')],
 '固定f4e77d43，实际smeltery_controller与BE注册、block.getTicker→HeatingStructure serverTick在结构成立时heat，每20tick周期tick12实体交互。EntityMeltingModule先扫bounds；Living黑名单、按fireImmune选择heat/magic后isInvulnerableTo、player abilities.invulnerable、任何FIRE_RESISTANCE最终排除，再懒取本轮共享燃料资格。有原生recipe则产物/damage取recipe，缺省2伤+liquidSoul；实际hurt返回true才tank.fill并melted=true。',
 '计1：自适应伤害源下显式最终拒伤资格→成功受击才转换产物的原生世界玩法，不把库中的每种fluid/source当独立研究。fireImmune本身不会免炉，改走magic；fire resistance仍阻magic分支。生成data仅heat列IS_FIRE，不能将magic的burning效果字样等同IS_FIRE。canMeltEntity不通过时不取燃料资格；hurt=false也可能因外部事件/伤害窗，不能给Boss贴免疫。canMeltEntities只检查hasFuel或findFuel(false)>0，原生heat返回melted后才走findFuel(true)，不是在这预检查直接消费。',
 'Boss反馈需明确拒控类型，不能把未产物/未掉血当immune。资格检查所用source必须与真实执行一致，受伤成功回执与拒绝回执分别定义；状态/光/音效包装不加数。',
 'native block/controller和EntityMeltingModule全文、父serverTick/canMeltEntities/insertIntoInventory/getTicker完整方法、真实damage JSON及cache全文已读；不是全量多方块构建/燃料模块/配方实现全文。自定义recipe匹配/产出仅见实际调用，不声称资源全验、S2C/像素/运行通过。只有native拒伤+结算1credit，通用cache/source helper支持0。','native_adaptive_source_final_refusal_and_conversion_settlement')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch113-native-smeltery-adaptive-source-refusal-settlement','credited_chains':[k],'rationale':'One actual smeltery gameplay final admission with target-dependent source choice, explicit creative ability/fire resistance denial before shared fuel qualification, output only after hurt success. Not a generic fluid library, not source constants or recipes counted separately.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
