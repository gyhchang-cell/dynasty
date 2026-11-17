"""Two actual source-qualified target control/damage policies, no runtime work."""
from ledger import B,O,record,verify
import json
r='team-abnormals/endergetic';p='src/main/java/com/teamabnormals/endergetic/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='endergetic-native-boof-trigger-versus-final-push-eligibility-and-ten-tick-source-lease'
record(k,r,[f('core/EndergeticExpansion.java',95,154),f('core/registry/EEBlocks.java',132,133),f('core/registry/EEBlockEntityTypes.java',30,31),f('core/registry/EEEntityTypes.java',41,41),w('core/other/tags/EEEntityTypeTags.java'),w('common/block/poise/boof/BoofBlock.java'),w('common/block/poise/boof/DispensedBoofBlock.java'),w('common/block/entity/boof/BoofBlockTileEntity.java'),w('common/block/entity/boof/DispensedBlockBoofTileEntity.java'),w('common/entity/BoofBlockEntity.java')],
 '真实registry与BoofBlock.getTicker→server BE tick只在未BOOFED且范围有非旁观、非潜行玩家/非玩家、非resistant实体时生成BoofBlockEntity；addFreshEntity true才设BOOFED并inflate声。该实体原生tick最终查询排乘客，再逐目标resistant tag拒绝直接push，箭另设ForProjectile并移除原方块。10tick后按origin加载/方块/ForProjectile条件恢复方块并discard。Dispensed native ticker也按同tag排除，方向push且10tick消失，合并同玩法家族。',
 '计1：实际陷阱/可作战位移源在触发资格与最终目标资格上不同，不能以启动音/进入范围认定被推动。潜行玩家和旁观者只在BE激活查询排除；一旦其他目标激活，实体push阶段未再次排它们。resistant tag在生产和最终执行均读取，拒绝时无免疫回执；直接push没有读取KnockbackResistance。实体tick没有client side guard，只有非Player写hurtMarked，不能声称两端权威一致。Dispensed ticker不排乘客/旁观/潜行且没有server guard，不为同tag第二实现或三轴常量加数。ForProjectile恢复分支只查区域加载，可覆盖届时替换方块；tickCount未写NBT，不能称保存重开仍精确剩余10tick。',
 'Boss免控需守住最终写速度处，激活资格或播放声不能替代接纳；按来源/目标记明确拒绝，不把属性免击退自动套用到直接push。',
 '关键来源BE、两个block/ticker、BoofBlockEntity和tag声明全文已读；未读tag默认成员，不声称具体Boss已在tag。BoofDispenseBehavior正文已读但本缓存未找到实际registerBehavior，不将该入口断言已装载；天然方块ticker链完整。没有屏幕/两TCP测试/免疫文字；通用RegistryHelper平台内部不计。','native_trigger_final_target_eligibility_with_bounded_control_source_lifetime')
k2='lycanites-native-mounted-target-damage-denial-inherits-mount-policy-at-hurt-event'
r='Lycanite/LycanitesMobs';p='src/main/java/com/lycanitesmobs/'
record(k2,r,[f('LycanitesMobs.java',208,216),f('EventListener.java',322,373),f('core/entity/EntityCreatureBase.java',3475,3494),f('core/entity/EntityCreatureBase.java',3731,3739),f('core/entity/EntityCreatureRideable.java',156,161),f('core/entity/EntityCreatureRideable.java',338,365),f('core/entity/EntityCreatureRideable.java',398,415),f('plainsmobs/entity/EntityRoc.java',29,50)],
 '真实mod注册EventListener，原生processInteract→getInteractCommands/assessInteractCommand→Rideable Mount命令→server startRiding；LivingHurt HIGHEST在尚未取消且source/entity非空时检查目标当前载具。Rideable上的目标inWall直接amount0+cancel；其他来源调用实际载具isDamageTypeApplicable(type,source,amount)，false则置零取消并return。pickedUp的inWall保护同方法支持合并。',
 '计1：实际伤害事件将当前载具的伤害源准入政策动态投射给另一个受害实体，区别已有骑手每tick清负面效果（可能先应用）、Fear搬运资格和单体Boss伤害预算。不是所有载具能力都继承：没有读canBurn/isEntityInvulnerable/isDamageEntityApplicable；基础policy仅稀有/Boss的inWall/cactus与全局inWall/drown配置，子类可覆写。inWall在handler先无条件拒，不等载具policy允许。目标可不是玩家/owner/控制者，只有当前riding实体类型门；本入口不读主副手或控制状态，不按来源名/坐骑类型拆数。',
 '必须记录真正拒控的实体身份与权威原因，不能从骑手受保护反推Boss自己免疫，也不能把tick清状态等同施加时拒绝。借用别的实体政策时核实具体采用了哪一组规则。',
 '完整onLivingHurt、准入query与真实交互关键方法已读；Roc构造表明实际Rideable子类，但没有展开JSON实体注册/外部Forge事件裁决，因此不声称当前整包可自然获得该坐骑或所有后续监听无法解cancel。未读全部子类policy、不将其算新条。无灰字/嗡声/画面测试。','native_cross_entity_current_mount_damage_admission_projection')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch119-native-control-source-final-target-versus-mounted-damage-projection','credited_chains':[k,k2],'rationale':'One boof gameplay family merges natural/dispenser tag wrappers; one actual LivingHurt cross-entity source-policy projection distinct from existing per-tick effect cleanse. No tag constants, item names, empty hurt=false or source getters counted separately.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
