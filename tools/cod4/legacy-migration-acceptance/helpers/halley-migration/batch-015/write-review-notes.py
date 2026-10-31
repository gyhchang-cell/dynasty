"""Render explicitly reviewed semantic chains only; not game/build/test/upstream execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
b=Path(__file__).resolve().parent
old=(b.parent/'batch-013/review.py').read_text()
header=old[:old.index("add('akashictome")].replace('batch-013','batch-015')
footer=old[old.index('def generate():'):].replace('batch-013','batch-015')
notes=r'''
def pick(path,names):return [(path,n) for n in names.split()]
add('forestry-official-legacy-registry-and-blockentity-id-compatibility',
 pick('utils/MigrationHelper.java','registerFixable addBlockName addItemName addTileName add onMissingBlockMappings onMissingItemMappings getRemappedTileName addTileRemappingName')+
 pick('tiles/TileEntityDataFixable.java','getFixVersion fixTagCompound')+
 pick('forestry/Forestry.java','preInit')+pick('items/ItemRegistry.java','registerItem')+pick('blocks/BlockRegistry.java','registerBlock')+pick('blocks/MachineProperties.java','registerTileEntity')+pick('tiles/TileUtil.java','registerTile'),
 '注册物品/方块时建立旧无下划线别名；真实Forge MissingMappings事件执行白名单重映射。Forestry preInit注册版本1的BLOCK_ENTITY data fixer，旧forestry.*实体id在加载fix阶段转换。全部合一兼容家族，不按表条目/物品方块/代理多计。',
 '手工block/item别名字典、ignoredMappings和运行期registerItem/registerBlock生成的旧path→新path；tileRemappings保存forestry.+uncapitalize(oldName)→新path。MissingMapping携带原ResourceLocation；BE输入为仍含其他状态的NBT compound id。',
 'add只对确实含下划线的新名称生成移除下划线的旧key，且旧key已被手工/先前别名占用时不覆盖。MissingMappings优先ignore列表，否则保留原namespace组装新id，仅在目标注册存在、值非null且非AIR时remap；未知或无有效目标保留未处理。BE fixer把id字符串中的minecraft:替换为空后，只有forestry.前缀才查询旧名，成功只setString(id)、原compound其余项不动；失败记录错误返回原对象。',
 '真实别名转换与初始化发生在不同入口：物品/方块通过缺失注册事件而非直接new ItemStack重建，BE通过注册的fixer原位改id。映射许多旧温室角色到同一新block，不转换metadata/NBT角色参数；不能因为注册名可恢复就宣称旧机器功能等价。ignored greenhouse.sprinkler是显式忽略，不能作为修复成功或单条credit。handler中未直接比对namespace，外部event.getMappings筛选语义本批未深审。',
 'Dynasty quest_ledger采用显式旧→现任务入口白名单，先查目标真实注册且非AIR，保留原Count/tag；缺FTB或无有效target保持可诊断原始载荷，不把ignored或未知项当成功。永久字段/任务标记迁移必须与物品注册兼容区分，不能仅改显示名；healing_talisman按已有历史替代判断，不从广泛别名规则恢复旧回血。',
 '固定1.12官方源码，Forge版本事件/datafixAPI不直接照搬1.20.1。未重读原生物品构造、Forge Mapping.remap或世界datafix完整执行，证据只到mod注册及真实回调实现；因此不声称Count/tag所有底层格式已验。BE replace是全字符串replace而非严格前缀移除，坏id未总catch；无tile目标注册存在性检查，和item/block AIR guard不同。未见转移任意附属状态/跨模组namespace或Clone策略。',
 'MissingMappings物品与方块是同构分支不分两条；静态别名列表、下划线生成、BE helper注册/执行统一提交一条官方兼容家族。与其他MissingMappings主账家族有高重叠，Kepler可合并，不按几十别名或方法数信用，credit0。')

add('forestry-worktable-durable-recipe-memory-registry-filter-and-selection',
 pick('recipes/MemorizedRecipe.java','readFromNBT writeToNBT MemorizedRecipe getSelectedRecipe getCraftingResult getOutputIcon incrementRecipe decrementRecipe hasRecipeConflict removeRecipeConflicts hasRecipe updateLastUse getLastUsed toggleLock isLocked setCraftMatrix getCraftMatrix')+
 pick('recipes/RecipeMemory.java','RecipeMemory writeToNBT memorizeRecipe updateExistingRecipe getOldestUnlockedRecipe getExistingMemorizedRecipe getRecipe toggleLock')+
 pick('tiles/TileWorktable.java','TileWorktable readFromNBT writeToNBT chooseRecipeMemory setCurrentRecipe setCraftingDisplay getResult craftRecipe onCraftingStart onCraftingComplete')+
 pick('gui/ContainerWorktable.java','handleSelectionRequest')+
 pick('utils/InventoryUtil.java','readFromNBT writeToNBT deepCopyInventoryContents deleteExactSet')+
 pick('worktable/inventory/InventoryCraftingForestry.java','InventoryCraftingForestry copy')+
 pick('recipes/RecipeUtil.java','getCraftRecipe'),
 '玩家工作台实际合成后记忆配方，保存RecipeMemory列表；BE重载构造每个MemorizedRecipe，玩家选记忆通过container.handleSelectionRequest进入tile，选中的真实IRecipe用于合成结果与材料消费。',
 '每条记忆包含craftMatrix命名库存中的完整ItemStack compound和Slot、LastUsed long、Locked bool、SelectedRecipe int、Recipes资源ID字符串列表。库存Slot兼容byte旧型与integer新型，writer统一integer；tile另存ghost crafting display。',
 'reader先读模板库存和锁/时间，再按注册Recipes逐个查IRecipe，缺失配方跳过；RecipeMemory只加入getSelectedRecipe非null条目。writer同样只写仍有选中配方的记忆。后续真实getCraftingResult必须recipe.matches并且输出非空；craftRecipe在库存中找匹配材料，模拟时深拷贝，实际deleteExactSet并更新当前模板；完成时记录最近使用时间，最多9条常规记忆按最老未锁替换，更新同配方保留原锁。',
 '缺失配方过滤会压缩列表，但SelectedRecipe仍是旧序号；只在selectedRecipe > recipes.size()时回0，等于长度或负数未修正，非空getSelectedRecipe直接get可越界，可能使RecipeMemory构造整体中断。即使索引仍合法，也可因前面配方缺失而指向另一配方。正常新增受capacity9约束，但NBT构造不裁剪条数；toggleLock只查size>index不查非负。InventoryUtil.byte读取不做&255、也不检查slot范围/清原库存；旧byte128..255会成为负索引，重复槽后写覆盖。缺键直接return在复用对象可留旧状态。',
 'Dynasty任务/手册进度恢复使用稳定标识而非可被过滤的列表序号；修复每个条目结构后再决定替换，未知配方/任务载荷应保留供审查，不能先跳过再假设剩余序号稳定。迁移Slot需显式类型与范围检查，写整形避免byte溢出。永久历史标记可保留，工作台时间/工作库存不能据此混入玩家Clone白名单。',
 '本建议是实际配方记忆恢复，InventoryUtil只是支持，不当通用库额外计。原生ItemStack constructor/Forge recipe实现场景未执行，RecipeUtil材料等价与InventoryUtil删除更深层helper只到完整调用方法，不宣称任意模组配方原子/无损。worktable网络传输方法不是本候选持久入口，未启动GUI/网络或合成游戏验证。无真实旧recipe ID映射，仅缺注册过滤；最后写回会丢弃未识别配方列表和无选中记忆，不是无损归档。',
 'RecipeMemory、MemorizedRecipe、Slot byte/int兼容、库存/选配方/材料消费均同一工作台恢复链一条；不按9槽/每recipe/key/锁分支另计。InventoryDatabase同136槽共用codec已发现但不单拿同codec包装计数，待有实际不同对象语义再议。credit0由Kepler最终去重。')

add('forestry-analyzer-legacy-nested-energy-restoration-with-transient-work-boundary',
 pick('energy/EnergyManager.java','EnergyManager readFromNBT writeToNBT setEnergyStored drainEnergy setExternalMode')+
 pick('energy/EnergyHelper.java','scaleForDifficulty consumeEnergyToDoWork')+
 pick('tiles/TilePowered.java','TilePowered readFromNBT writeToNBT updateServerSide getTicksPerWorkCycle getEnergyPerWorkCycle setTicksPerWorkCycle setEnergyPerWorkCycle')+
 pick('tiles/TileAnalyzer.java','TileAnalyzer readFromNBT writeToNBT updateServerSide hasWork moveSpecimenToAnalyzeSlot workCycle')+
 pick('tiles/TileForestry.java','update readFromNBT writeToNBT'),
 '实际分析机重载经TilePowered恢复EnergyManager；服务端tick做有工作/红石检查，按周期扣持久电量后workCycle用蜂蜜分析遗传样本并写回样本NBT及移出分析槽。EnergyManager被其他机器复用只合一条兼容读链。',
 '旧NBT EnergyManager/EnergyStorage/Energy整数或新根级Energy；manager capacity/maxTransfer按当前难度缩放。分析槽样本和蜂蜜由各自库存/tank支持；workCounter、energyPerWorkCycle、noPowerTime不由TilePowered.writeToNBT保存。',
 '只要顶层hasKey(EnergyManager)，reader无类型约束优先取旧嵌套Energy，否则取平铺Energy，缺失读取默认0；setEnergyStored裁剪到[0,capacity]。writer仅写当前平铺Energy，若传入仍带旧EnergyManager compound不会主动删旧键，下一次read仍优先旧值；迁移若原位保留旧key会反复取旧数据。EnergyHelper按ceil(cost/ticks)扣款；TilePowered完成周期再执行真实workCycle。',
 '持久电量与临时工序不是同一保留政策。TileAnalyzer.readFromNBT恢复已占分析槽的specimenToAnalyze，但moveSpecimenToAnalyzeSlot遇非空分析槽立即return，设置每周期时间/成本仅在新移入分支；新实例TilePowered默认ticks4、energyPerWorkCycle字段默认0且不从NBT恢复，因此该路径无法据本代码保证恢复了原工序成本。workCounter亦默认0而非复原。裁剪分支会调用changeHandler，范围内赋值不回调；电量reader有旧key即优先，即使结构错误而新平铺值有效也不fallback。',
 'Dynasty Clone白名单保永久任务/功名等，经审定后从真值重建派生状态；临时计时器、免疫、反击、姿态不能因“保存存在”就全复制。旧新字段并存时定义版本/优先级，迁移成功写新格式后处理旧字段，使恢复幂等；对缺结构与合法0区别处理，不能无条件拿默认0覆盖有效新值。',
 '这是mod机器实际持久电量兼容及工序边界，不是玩家Clone实现，也不新增玩家能量机制。更深层TankManager、遗传individual.analyze/writeToNBT和InventoryUtil输出能力本批未完整深审，不宣称其无损；真实调用方法保存用于确认消费者。恢复成本问题为静态可达路径观察，未运行样本、编译或测试；不擅改机器生产代码。EnergyStorage父类剩余契约不重读，范围裁剪只依据本override。',
 '所有机器EnergyManager同reader、wrapper、Tesla/MJ平台和顶层key都只提此一条；具体分析机仅用于证明真实玩法消费。与主账能量格式迁移需Kepler语义比对，不按机器数/电量值/工作步骤另计，credit0。')
'''
attach='''\ndef attach_declarations(row):
    sys.path.insert(0,str(BASE.parent))
    from extract import PARSER,walk,norm,sha
    target='utils/MigrationHelper.java' if 'legacy-registry' in row['family'] else ('tiles/TilePowered.java' if 'nested-energy' in row['family'] else None)
    if target is None:return
    sample=next(r for r in INDEX if r['path'].endswith('/'+target))
    raw=(ROOT/sample['source']).read_bytes();decl=[]
    for node in walk(PARSER.parse(raw).root_node):
        fragment=raw[node.start_byte:node.end_byte].decode()
        keep=(target.endswith('MigrationHelper.java') and (node.type=='static_initializer' or (node.type=='field_declaration' and 'Pattern underscores' in fragment))) or (target.endswith('TilePowered.java') and node.type=='field_declaration' and any(t in fragment for t in ['int workCounter;','int energyPerWorkCycle;','int ticksPerWorkCycle;']))
        if not keep:continue
        e=dict(sample,node_type=node.type,name='<clinit>' if node.type=='static_initializer' else fragment.split(';')[0].split()[-1],start=node.start_point.row+1,end=node.end_point.row+1,text=fragment,context=fragment,excerptSha256=sha(fragment.encode()),normalizedSha256=norm(node,raw),candidate_id=sha((sample['repo']+sample['commit']+sample['path']+str(node.start_byte)).encode())[:20])
        e['url']='https://github.com/'+e['repo']+'/blob/'+e['commit']+'/'+e['path']+'#L'+str(e['start'])+'-L'+str(e['end']);decl.append(e)
    row['source_declarations']=decl
'''
footer=footer.replace('        rows.append(row)','        attach_declarations(row)\n        rows.append(row)')
(b/'review.py').write_text(header+notes+attach+footer)
p=b/'record-document-integrity.py';s=p.read_text().replace("e.get('node_type')=='field_declaration'","e.get('node_type') in ('field_declaration','static_initializer')")
s=s.replace("sum(e.get('node_type')!='field_declaration' for e in seen_nodes.values())","sum(e.get('node_type') not in ('field_declaration','static_initializer') for e in seen_nodes.values())")
s=s.replace("'complete_field_declarations_support_not_credit':", "'complete_static_initializers_support_not_credit':sum(e.get('node_type')=='static_initializer' for e in seen_nodes.values()),'complete_field_declarations_support_not_credit':")
s=s.replace("'complete_field_declarations_support_not_credit':sum(e.get('node_type') in ('field_declaration','static_initializer') for e in seen_nodes.values())", "'complete_field_declarations_support_not_credit':sum(e.get('node_type')=='field_declaration' for e in seen_nodes.values())")
p.write_text(s)
print('Three authored semantic families; credit0')
