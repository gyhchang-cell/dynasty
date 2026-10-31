"""Handwritten research decisions. Helpers never award master credit."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-002'
INDEX=json.loads((BASE/'method-index.json').read_text())
SPECS=[]
def add(family,selectors,trigger,input,output,observation,application,limits,risk):
    SPECS.append(dict(family=family,selectors=selectors,trigger=trigger,input=input,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))

add('corpse-legacy-death-snapshot-and-recovery',[
 ('CorpseEntity.java','readAdditionalSaveData'),('CorpseEntity.java','addAdditionalSaveData'),
 ('CorpseEntity.java','createFromDeath'),('CorpseEntity.java','tick'),('CorpseEntity.java','remove'),
 ('CorpseEntity.java','interact'),('DeathEvents.java','playerDeath'),
 ('CorpseInventoryContainer.java','transferItems'),('CorpseInventoryContainer.java','fill'),
 ('CorpseAdditionalContainer.java','transferItems'),('MessageTransferItems.java','executeServerSide'),
 ('CorpseContainerBase.java','stillValid')],
 '尸体实体从旧存档装载，随后玩家通过服务端已打开容器取回死亡物品。',
 '新 Death 复合标签，或旧 IDMost/IDLeast、DeathIDMost/Least、InventorySize、Inventory、Equipment、Name；Age 与可选 EmptyAge。',
 '新格式优先；仅无 Death 才组装旧 Death.Builder。恢复归属/装备/模型/年龄；取回时原位填槽，冲突物与余量回附加库存。后续保存只写新 Death。',
 '完整 reader 有显式新旧二择一，而不是把旧字段覆盖新状态。InventorySize 控制旧附加列表大小，旧槽内容交 ItemUtils；缺 EmptyAge 保留构造器 -1。tick 以恢复年龄判骨架、强制消失和清空计时。fill 先保存玩家原槽冲突物，再清源槽并转移尸体 stack；附加转移每次写回 insertItem 余量。remove 不区分 RemovalReason 就尝试掉出 death.getAllItems，不能从这里推定卸载事务安全。',
 'quest_ledger 应只在确认旧 ID 且新表示缺失时迁移，保留 Count/tag；永久字段和临时生命周期分别定义。用原槽冲突/容量不足/重开后的剩余库存作只读验收思路。',
 '已补读匹配 corelib 1.20.1-1.1.3 的 Death/ItemUtils：Death 内部旧 Most/Least UUID 对反而优先于新 UUID；缺两者随机生成身份，不能说处处新格式优先。完整 ItemStack.of 保留合法 Count/tag，未知注册项行为仍由原生 reader 定义。库存大小无本地上界，contains 未约束 Death 标签类型。drop 清除先于 addFreshEntity 且未检查添加返回值，不能照搬原子恢复保证。此项一条链，支持方法不另计。',
 '与原生实体保存/普通库存 reader 在外形上相近；独立点是明确旧 UUID/扁平库存到 Death 的兼容分支和其真实消费者。主责仍需跨账语义去重。')

add('evilcraft-werewolf-villager-selective-roundtrip',[
 ('EntityWerewolf.java','replaceVillager'),('EntityWerewolf.java','replaceWithVillager'),
 ('EntityWerewolf.java','replaceEntity'),('EntityWerewolf.java','addAdditionalSaveData'),
 ('EntityWerewolf.java','readAdditionalSaveData'),('EntityWerewolf.java','transformWerewolfVillager'),
 ('EntityWerewolf.java','initializeWerewolfVillagerData'),('EntityWerewolf.java','aiStep'),
 ('EntityWerewolf.java','isWerewolfTime'),('EntityWerewolf.java','removeWhenFarAway')],
 '满月夜晚有天空亮度的狼人职业村民变形，或狼人白天/非满月/和平时还原。',
 '原村民 addAdditionalSaveData 产生的局部快照、fromVillager 标志和当前位置；重载时读取 villager 复合标签。',
 '狼人保存原村民专属数据，跨实体存盘后还原为新的村民并读取该快照；位置单独 copyPosition，来自村民的狼人不按普通远距规则消失。',
 '捕获使用 addAdditionalSaveData 而非 saveWithoutId/load 全实体，分离跨物种转移域。replaceEntity 先移除旧实体再 addFreshEntity；replaceWithVillager 在替换入世界后才 readAdditionalSaveData，捕获 RuntimeException 只打印。initialize 默认职业等级2先设置，再允许保存数据覆回；fromVillager 只影响 removeWhenFarAway，aiStep 转回并不以该标志为条件。',
 'Clone 白名单应按持久状态所属域分离，把位置/实体 UUID/网络生命周期留给新对象；验收应包含重载后再转换和默认值与旧值的先后顺序。',
 '不是玩家 Clone，也不是事务保证；旧实体先删除，加载失败留下默认村民。未比较 vanilla 村民 reader 的每个字段，不能断言完整保留交易或身份。不要用此快照模式复制 Dynasty 整包 ForgeData。',
 '与旧批 dragonhorn/stone-statue 的实体快照有家族风险；此处区别是周期双向物种转换、持久原物种数据和远距消失边界，主责可按宽家族合并。')

add('evilcraft-exalted-crafter-dual-slot-schema',[
 ('item/ItemExaltedCrafter.java','getItemList'),('item/ItemExaltedCrafter.java','setItemList'),
 ('item/ItemExaltedCrafter.java','setStackInSlot'),('item/ItemExaltedCrafter.java','insertItem'),
 ('item/ItemExaltedCrafter.java','extractItem'),('item/ItemExaltedCrafter.java','initCapabilities'),
 ('item/ItemExaltedCrafter.java','getSupplementaryInventory'),('item/ItemExaltedCrafter.java','empower')],
 '木制 Exalted Crafter 的真实物品 capability 读取/插入/取出库存；升级 empowerment 时更换物品。',
 'inventory 列表，旧 int index 或当前 byte Slot，以及完整 ItemStack NBT；固定27槽。',
 'index 存在时优先，否则 Slot；范围有效才恢复 ItemStack.of。修改后写当前 Slot schema，只序列化正数量非空 stack；升级复制原 tag 到新物品。',
 'getItemList 是实际 IItemHandler 读改写闭环的一环，非孤立取值器；旧 index 优先后一次真实修改即写成 Slot。外层原 tag 保留其他键，插入模拟不写源，extract 读取的是刚反序列化的局部 stack。木制才暴露本地 capability；非木制 supplementaryInventory 用玩家末影箱，不得误复制给每个 crafter。empower 新建 stack 默认数量，只有 tag 被复制。',
 '旧物品 ID 迁移需明确哪个表示优先、如何保留不相关标签和 Count；玩家全局库存与物品自有库存不能混为同一归属。可以用双键冲突/越界/模拟写入检查迁移边界。',
 '旧 index 存在但越界不会再退 Slot；未知/移除物品随 ItemStack.of 可能变空。外部 NBTSimpleInventoryItemHeld 内部尚未闭合；本项只对自有 capability 的明确 reader/writer 作建议。empower 不保留 Count，不能照搬任务物品升级。',
 '与其他兼容 Slot/index reader 可能语义近似；与同文件 empower 不拆两项，平台和键名变化不另计。')

add('evilcraft-broom-parts-and-modifiers-reconstruction',[
 ('BroomPartRegistry.java','getBroomParts'),('BroomPartRegistry.java','setBroomParts'),
 ('BroomPartRegistry.java','getBaseModifiersFromBroom'),
 ('BroomModifierRegistry.java','getModifiers'),('BroomModifierRegistry.java','setModifiers'),
 ('EntityBroom.java','saveWithoutId'),('EntityBroom.java','load'),('EntityBroom.java','getModifiers'),
 ('EntityBroom.java','getModifier'),('EntityBroom.java','getBroomStack'),('EntityBroom.java','setBroomStack'),
 ('EntityBroom.java','updateMountedServer'),('EntityBroom.java','consume'),('EntityBroom.java','tick'),
 ('EntityBroom.java','onDismount'),('item/ItemBroom.java','use')],
 '扫帚 stack 读取部件与数值改造属性，或写回改造结果。',
 '部件字符串 ID 列表、modifier 的 id/value 复合列表；当前注册表与默认 base modifier。',
 '合法且已注册部件才加入；全部无效/缺失时且默认件已注册才给默认三件。modifier 先铺默认基础值，再按保存的已知 ID 覆盖。写 modifier 同步其等级对应外观部件。',
 '这是同一实际装备配置链的两种数据，不拆计数。部件部分无效时只丢失无效项，不补全三件；只有列表整体空时整套默认。未知 modifier 被忽略而基础默认保留；ID 语法失败未 catch。setModifiers 按 tier 追加对应外观件但不删除旧件，重复调用不保证幂等。实体通过 saveWithoutId/load 单独保存 broomItem，忽略空恢复结果而保留默认扫帚；getModifiers 懒缓存部件基础值与改造值，updateMountedServer 用实际属性决定速度、机动、浮力与血液消耗。getBroomStack 强制 Count=1。setBroomStack 未显式清 cachedModifiers。',
 '迁移旧 ID 时区分未知条目隔离和整个结构缺失默认重建；配置默认值应先于已知保存值，补丁执行还需重复运行幂等检查。',
 '已闭合到 EntityBroom 的保存/加载与实际移动消费者。getModifiers 无参重载是列表支持，不能额外计数。没有旧 ID 映射表，不能声称保留未知 ID。默认替代可能隐藏旧物品丢失；运行中更换配置还涉及缓存失效。ItemBroom.use 未检查实体添加/骑乘返回值便消耗物品，不提供原子保证。',
 '与其他注册表 ID 列表 reader 近似；独立性取决于默认重建、属性覆盖和部件联动的整体语义，主责可合并。')

# The library methods below are supporting evidence for the actual Corpse gameplay,
# never an independent inventory of generic serialization helpers.
SPECS[0]['selectors'] += [('corelib/death/Death.java','fromNBT'),('corelib/death/Death.java','toNBT'),
 ('corelib/death/Death.java','fromPlayer'),('corelib/death/Death.java','processDrops'),
 ('corelib/death/Death.java','processInventory'),('corelib/death/DeathEvents.java','playerDeath'),
 ('corelib/item/ItemUtils.java','readInventory'),('corelib/item/ItemUtils.java','saveInventory'),
 ('corelib/item/ItemUtils.java','readItemList'),('corelib/item/ItemUtils.java','saveItemList')]

add('corpse-independent-death-history-file-recovery',[
 ('corpse/gui/Guis.java','openCorpseGUI',62),('corpse/gui/Guis.java','openCorpseGUI',29),
 ('corpse/gui/Guis.java','openAdditionalItems'),('corpse/net/MessageRequestDeathHistory.java','sendDeathHistory'),
 ('corpse/net/MessageShowCorpseInventory.java','executeServerSide'),('corpse/events/DeathEvents.java','deleteOldDeaths'),
 ('corelib/death/DeathManager.java','addDeath'),('corelib/death/DeathManager.java','getDeath'),
 ('corelib/death/DeathManager.java','getDeaths'),('corelib/death/DeathManager.java','removeDeathsOlderThan'),
 ('corelib/death/DeathManager.java','getDeathFile'),('corelib/death/DeathManager.java','getPlayerDeathFolder'),
 ('corelib/death/DeathManager.java','getDeathFolder'),('corelib/death/Death.java','fromNBT'),
 ('corelib/death/Death.java','toNBT'),('corpse/gui/CorpseContainerBase.java','stillValid')],
 '玩家打开死亡历史或按死亡 UUID 预览/创造恢复已持久化的历史条目；死亡事件可独立写历史文件。',
 '世界 deaths/<playerUUID>/<deathUUID>.dat 的 Death 快照；读取目标玩家 UUID、死亡 UUID、文件时间及内部 Timestamp。',
 '文件读取失败返回 null/跳过单个历史，历史按内部时间倒序；构造一个未加入世界的临时 CorpseEntity 作为容器，只有 instabuild 玩家可编辑。',
 '这是世界外部死亡历史文件的实际恢复消费者，和仍在区块中的尸体实体是两个存储所有者。getDeaths 使用 UUID 文件名过滤，单文件异常隔离；Guis 按指定玩家和死亡 UUID 查找，missing 即不打开。历史传给客户端的 toNBT(false) 省库存但仍有装备；服务端容器持有完整读取对象。历史容器 stillValid 恒 true，真实尸体才检查距离与存活。旧历史清理先看文件 mtime，再解码并核对内部 timestamp，解析失败不会删。所有库方法都只作为这条玩法的证据。',
 '旧任务凭证迁移要区分当前实体/玩家状态与历史证据文件；历史读取不能自行发放普通玩家奖励，坏条目隔离不应让全部玩家档案不可读。',
 'addDeath 直接写目标文件而非可见临时文件替换，异常只打印，不代表原子写。历史创造恢复未删除或改写历史文件，不能声称一次消费；服务端未在此链复核请求 UUID 属于请求者，但编辑仍受 instabuild 控制。getDeaths(ServerPlayer) 自递归未被实际 sendDeathHistory 调用，保留为负面支持而不另计。',
 '与上一尸体链共享 Death codec，若主责按全部死亡恢复宽家族归并应降为支持；独立建议仅建立在历史文件所有者、坏文件隔离、预览/编辑权限和保留策略，不因文件名另计。')

add('evilcraft-environmental-accumulator-resumable-job',[
 ('BlockEntityEnvironmentalAccumulator.java','read'),('BlockEntityEnvironmentalAccumulator.java','saveAdditional'),
 ('BlockEntityEnvironmentalAccumulator.java','update'),('BlockEntityEnvironmentalAccumulator.java','updateEnvironmentalAccumulatorIdle'),
 ('BlockEntityEnvironmentalAccumulator.java','decreaseStackSize'),('BlockEntityEnvironmentalAccumulator.java','dropItemStack'),
 ('BlockEntityEnvironmentalAccumulator.java','activateIdleState'),('BlockEntityEnvironmentalAccumulator.java','activateProcessingItemState'),
 ('BlockEntityEnvironmentalAccumulator.java','activateFinishedProcessingItemState'),('BlockEntityEnvironmentalAccumulator.java','activateCooldownState'),
 ('DegradationExecutor.java','read'),('DegradationExecutor.java','write'),('DegradationExecutor.java','runRandomEffect'),
 ('RecipeEnvironmentalAccumulator.java','assemble'),('RecipeEnvironmentalAccumulator.java','getResultItem')],
 '环境收集器在处理/完成等待/冷却任一阶段存盘，重载后继续天气与物品加工。',
 '单槽库存、degradation、tick、整数 state、可选 recipe ID；degradationExecutor 的间隔与当前刻。',
 'reader 暂存 recipeId，首个已有 level 的 ticker 查配方后清引用；持久 tick 决定后续产出或冷却。找不到配方时产回输入，完成等待后清槽。',
 'read 不依赖尚未可用的 level 查询配方，而是延迟到 ticker；直接强制转换得到 RecipeEnvironmentalAccumulator，不复验输入天气/配方 matches。dropItemStack 若 recipe 为空退回整槽；正常配方 assemble 优先保留结果已有标签，仅补输入缺失键。产出发生在 PROCESSING 结束，清库存发生在下一 FINISHED 结束，二者跨不同刻。reader 缺 degradationExecutor 子键会把默认间隔1写成0。saveAdditional 只写已解析的 recipe，不写等待中的 recipeId。',
 '迁移后初始化依赖的世界/注册表应延迟，但待解析 ID 也需要在重复保存中保留；永久任务状态不能照搬任务处理中间态。用产出前/产出后未清槽/解析前再保存作为边界检查。',
 '没有事务日志；两阶段产出清槽在崩溃窗口可能重复或丢失，不能作为一次消费保证。缺 recipe 与非法 ID/配方类型各有不同风险；这里只做静态观察，不执行上游。recipe assemble 只是支持，不按补键操作额外计。',
 '与主账已审其他加工机器有进度快照家族风险；独特点是延迟配方绑定、天气副作用、丢配方退输入和完成等待后清槽的联合状态机。')

add('evilcraft-biome-extract-registry-and-chunk-persistence',[
 ('item/ItemBiomeExtract.java','getBiome'),('item/ItemBiomeExtract.java','createItemStack'),
 ('item/ItemBiomeExtract.java','use'),('entity/item/EntityBiomeExtract.java','onHit'),
 ('entity/item/EntityBiomeExtract.java','setBiome'),('entity/item/EntityBiomeExtract.java','updateChunkAfterBiomeChange')],
 '携带 biomeKey 的生物群系萃取物被使用并击中方块，实际改写区块群系。',
 '物品 biomeKey 注册名和当前世界的 biome registry；噪声群系坐标、区块调色板与对应 Holder。',
 '物品先确认注册表有该 ID 才发射；命中再次解析，转换为当前世界注册表 Holder，改区块群系并 setUnsaved(true)，再发区块/颜色更新。',
 'reader 不是只供 tooltip：真实弹体命中用相同 reader。setBiome 注释解释同一 biome 多实例导致存盘 invalid id:-1；实现从活跃 registry 找 Holder，失败再通过 Forge registry key 回查。坐标经噪声放大偏移和高度 clamp 后写 PalettedContainer，显式标脏。未加载区块只警告，外围仍可能把 ChunkPos 收入更新集合。',
 '旧 ID 恢复为对象后仍需匹配当前存档注册表身份；迁移任务物品不可仅按显示名替代。保存后的消费者和同步要使用同一个权威表示，避免只修显示。',
 '没有旧 biome ID 重命名表，未知 ID 返回 null，语法错误未 catch。Holder 第二回查直接 get，失败可抛；更新包路径未检查 chunkSafe 为 null。世界群系改写不等于玩家 Clone 字段迁移，只借鉴注册表身份与显式持久化边界。',
 '与一般 registry reader 有重合，独立点仅为真实区块调色板身份修复/标脏闭环；如果主责只收玩家/物品状态，可降级不计。')

add('evilcraft-weather-container-enum-fallback-consumption',[
 ('item/ItemWeatherContainer.java','getWeatherType'),('item/ItemWeatherContainer.java','setWeatherType'),
 ('item/ItemWeatherContainer.java','use'),('item/ItemWeatherContainer.java','onUse'),
 ('item/ItemWeatherContainer.java','onFill'),('entity/item/EntityWeatherContainer.java','onHit'),
 ('core/weather/WeatherType.java','valueOf')],
 '天气容器从物品标签恢复内容、抛出命中改变世界天气，或收集当前天气。',
 'weather 的枚举名字；当前世界天气和投射物内复制的 ItemStack。',
 '缺 tag 或不能 valueOf 的名字统一解释 EMPTY；真实命中按类型执行天气激活，然后将持有 stack 写 EMPTY。填充选择当前激活类型并停用对应天气。',
 'ItemWeatherContainer 中名称字符串是当前实际格式，文件头仍说 damage ordinal，注释不能当已实现旧 ordinal 兼容。getWeatherType 捕获 IllegalArgumentException；EMPTY 会阻止服务端发射。嵌套 enum onUse 先服务端校验再 type.activate，随后 setWeatherType(EMPTY)；onFill 循环最后匹配类型获胜，若全部无匹配 currentWeatherType 仍 EMPTY，其 type 为 null 却直接 deactivate。',
 '迁移须以实际 reader 而非过时注释判断旧格式是否支持；未知持久枚举回默认会损失原含义，永久任务状态应明确隔离和记录而非沉默清空。',
 '未发现 damage 到 string 的兼容分支，不能声称有旧 ID 升级。投射物 stack 未在本类自定义 NBT 保存，跨卸载保持天气内容仍须父类审查；这条建议只以物品持久枚举与即时消费者为界。不同天气枚举值不是不同实现。',
 '与其它枚举兜底 reader 可能被宽家族合并；只有真实天气填充/消耗边界提供额外语义，不因三个天气值凑数。')

add('evilcraft-entangled-chalice-world-owned-contents',[
 ('evilcraft/core/fluid/WorldSharedTankCache.java','readFromNBT'),('evilcraft/core/fluid/WorldSharedTankCache.java','writeToNBT'),
 ('evilcraft/core/fluid/WorldSharedTankCache.java','reset'),('evilcraft/core/fluid/WorldSharedTankCache.java','setTankContent'),
 ('evilcraft/core/fluid/WorldSharedTankCache.java','getTankContent'),('evilcraft/core/fluid/WorldSharedTankCache.java','shouldRefreshFluid'),
 ('evilcraft/core/fluid/WorldSharedTankCache.java','getMapID'),('evilcraft/core/fluid/WorldSharedTankCache.java','removeMapID'),
 ('evilcraft/core/fluid/WorldSharedTankCache.java','bufferPacket'),('evilcraft/core/fluid/WorldSharedTankCache.java','onTick'),
 ('evilcraft/core/fluid/WorldSharedTankCache.java','onLoggedIn'),('evilcraft/core/fluid/WorldSharedTank.java','readFromNBT'),
 ('evilcraft/core/fluid/WorldSharedTank.java','writeToNBT'),('evilcraft/core/fluid/WorldSharedTank.java','reset'),
 ('evilcraft/core/fluid/WorldSharedTank.java','readTankFromNBT'),('evilcraft/core/fluid/WorldSharedTank.java','writeTankToNBT'),
 ('evilcraft/core/fluid/WorldSharedTank.java','readWorldFluid'),('evilcraft/core/fluid/WorldSharedTank.java','writeWorldFluid'),
 ('evilcraft/core/fluid/WorldSharedTank.java','fill'),('evilcraft/core/fluid/WorldSharedTank.java','drain'),
 ('evilcraft/core/fluid/WorldSharedTank.java','replaceInnerFluid'),('evilcraft/item/ItemEntangledChalice.java','getFluid'),
 ('evilcraft/item/ItemEntangledChalice.java','setFluid'),('evilcraft/item/ItemEntangledChalice.java','getTankID'),
 ('evilcraft/item/ItemEntangledChalice.java','setTankID'),('evilcraft/item/ItemEntangledChalice.java','itemStackDataToTile'),
 ('evilcraft/blockentity/BlockEntityEntangledChalice.java','read'),('evilcraft/blockentity/BlockEntityEntangledChalice.java','saveAdditional'),
 ('evilcraft/loot/functions/LootFunctionCopyEntangledChaliceData.java','run'),('evilcraft/EvilCraft.java','EvilCraft'),
 ('cyclopscore/persist/world/WorldStorage.java','onAboutToStartEvent'),('cyclopscore/persist/world/WorldStorage.java','onStartedEvent'),
 ('cyclopscore/persist/world/WorldStorage.java','onStoppingEvent'),('cyclopscore/persist/world/WorldStorage.java','initDataHolder'),
 ('cyclopscore/persist/world/WorldStorage.java','load'),('cyclopscore/persist/world/WorldStorage.java','save'),
 ('cyclopscore/persist/world/WorldStorage.java','isDirty'),('cyclopscore/init/ModBase.java','onServerAboutToStart'),
 ('cyclopscore/init/ModBase.java','onServerStarted'),('cyclopscore/init/ModBase.java','onServerStopping'),
 ('cyclopscore/init/ModBase.java','registerWorldStorage'),('cyclopscore/fluid/Tank.java','readFromNBT'),
 ('cyclopscore/fluid/Tank.java','writeToNBT'),('cyclopscore/fluid/Tank.java','readTankFromNBT')],
 '纠缠圣杯跨物品/方块形式共享流体；服务端启动装载全局存储，物品掉落和重新放置只携带 tankID。',
 '世界 SavedData 中 tankCache key/value 列表与每只圣杯的 tankID/容量；运行时缓存另加 C/S 侧后缀。',
 '世界统一存实际 FluidStack，圣杯只恢复共享引用；运行时读返回 copy，写实际执行时回全局缓存，掉落/放置保留同一 tankID，服务器重启先 reset 再由主世界 SavedData 装载。',
 '这不是通用缓存：真实圣杯 capability 与方块流体的唯一所有者是 WorldSharedTankCache。WorldSharedTank.replaceInnerFluid=false 阻止将世界内容再存进单个杯的 tank NBT；TankData 重置/读写委托该 cache，WorldStorage 使用 OVERWORLD 数据存储并 isDirty 恒 true。序列化去掉侧后缀，读入通过 setTankContent 重建当前侧键。setTankContent 的 shouldRefresh 只比较 amount；等量不同 fluid/tag 不进入 put，属于持久表示的局限。',
 'Clone 或旧 ID 升级必须保留数据所属域：玩家只复制引用，不把共享全局内容复制出第二份。验证重启后同 ID 两个载体仍共享、客户端会话缓存重置、模拟操作不落盘。',
 '未核实 CyclopsCore 发布二进制 build750 与所选同语义版本 tag 的逐字节对应，仅分别固定真实源码 commit。setTankContent 无量变化可能丢流体类型/标签更新；多世界靠服务生命周期 reset，不能将此 static singleton 直接照搬到 Dynasty。库 WorldStorage/Tank 为此实际圣杯链支持，零独立信用。',
 '与 SophisticatedStorage 世界 UUID 内容库有数据所有权家族风险；独立点是共享流体按引用跨物品/方块保持、两侧缓存键重建及世界生命周期重置，仍由主责最终归并。')

add('evilcraft-spirit-box-selective-capture-release-state',[
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','read'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','initializeState'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','initializeLidAngle'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','captureSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','setSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','releaseSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','createNewVengeanceSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','clearSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','setState'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','updateState'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','onStateChanged'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','onBoxOpened'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','updateLidAngle'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','pullEntity'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','getTargetSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','setTargetSpirit'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','setSpiritTag'),
 ('evilcraft/blockentity/BlockEntityBoxOfEternalClosure.java','getSpiritTag'),
 ('evilcraft/item/ItemBlockBoxOfEternalClosure.java','itemStackDataToTile'),
 ('evilcraft/loot/functions/LootFunctionCopyBoxOfEternalClosureData.java','run'),
 ('evilcraft/entity/monster/EntityVengeanceSpiritData.java','readNBT'),
 ('evilcraft/entity/monster/EntityVengeanceSpiritData.java','writeNBT'),
 ('evilcraft/entity/monster/EntityVengeanceSpiritData.java','getPlayerUUID'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','fromNBT'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','readAdditionalSaveData'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','addAdditionalSaveData'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','aiStep'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','getInnerEntity'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','canSustain'),
 ('evilcraft/entity/monster/EntityVengeanceSpirit.java','setInnerEntity'),
 ('cyclopscore/blockentity/CyclopsBlockEntity.java','load'),('cyclopscore/blockentity/CyclopsBlockEntity.java','read'),
 ('cyclopscore/blockentity/CyclopsBlockEntity.java','saveAdditional'),
 ('cyclopscore/persist/nbt/NBTProviderComponent.java','generateNBTPersistedFields'),
 ('cyclopscore/persist/nbt/NBTProviderComponent.java','writeGeneratedFieldsToNBT'),
 ('cyclopscore/persist/nbt/NBTProviderComponent.java','readGeneratedFieldsFromNBT'),
 ('cyclopscore/persist/nbt/NBTProviderComponent.java','writePersistedField'),
 ('cyclopscore/persist/nbt/NBTProviderComponent.java','readPersistedField'),
 ('cyclopscore/persist/nbt/NBTClassType.java','getType'),('cyclopscore/persist/nbt/NBTClassType.java','getTypeSilent'),
 ('cyclopscore/persist/nbt/NBTClassType.java','performActionForField'),
 ('cyclopscore/persist/nbt/NBTClassType.java','persistedFieldAction'),
 ('cyclopscore/persist/nbt/NBTClassType.java','readPersistedField',59),
 ('cyclopscore/persist/nbt/NBTClassType.java','readPersistedField',78),
 ('cyclopscore/persist/nbt/NBTClassType.java','readPersistedField',118),
 ('cyclopscore/persist/nbt/NBTClassType.java','readPersistedField',192),
 ('cyclopscore/persist/nbt/NBTClassType.java','writePersistedField',187)],
 '永闭盒捕获冻结灵魂、跨存盘/方块掉落放置保持灵魂，开启盒盖后释放新灵魂。',
 '带 NBTPersist 的 spiritTag/playerId/playerName/targetSpiritId/lidAngle；灵魂域的实体类型、寿命、冻结、swarm、玩家 UUID 字符串。',
 '捕获仅存 EntityVengeanceSpiritData 域而非整个实体；重载按是否有灵魂重建开闭和角度，释放新实体后清 spiritTag/cache，重设冻结和寿命。',
 '已追到真实注解读取：NBTProvider 扫字段，NBTClassType 按字段名取值；缺键 useDefaultValue=true 则写该类型默认，false 保留构造器值。盒子的 targetSpiritId/lidAngle 标 false，但它们仍会在存在时恢复，尤其 runtime entityId 不等于持久身份。read 后 initializeState/initializeLidAngle 依据有无 spirit 重建状态，避免把开盖中间态当永久业务状态。捕获先 remove 原灵魂，后保存独立数据；释放 addFreshEntity 后无条件 clear，不看成功返回值。玩家灵魂只记录 UUID/name 并将类型记为 ZOMBIE，不含完整玩家档案。',
 '永久任务字段应该有明确持久域白名单；从旧对象恢复后重建短时动画/目标引用，不能整包复制 runtime entityId/冻结计时。区分真正任务事实与为展示生成的代理实体。',
 '注解默认行为来自分别固定的同版本 CyclopsCore tag，build750 二进制对应未独立证明。无实体生成成功事务保证；clearSpirit 不在本方法显式 setChanged，是否另由 ticker 标脏不能由此断言。玩家 UUID 解析失败 getPlayerUUID 返回 null；类型字符串语法错误未 catch。整个捕获/盒存/掉落/释放/灵魂 reader 合为一条，库反射方法不另计。',
 '与旧批 dragonhorn 或其他魂容器存在实体快照家族风险；只建议按选择性域、重建生命周期与玩家代理语义判断独立性，主责允许降为支持。')

def generate():
    rows=[]
    for spec in SPECS:
        evidence=[]
        for selector in spec['selectors']:
            suffix,name=selector[:2]
            matches=[r for r in INDEX if r['path'].endswith(suffix) and r['name']==name and (len(selector)<3 or r['start']==selector[2])]
            assert matches,(suffix,name)
            for r in matches:
                evidence.append(dict(r,revision=r['commit'],private_file=r['source'],start_line=r['start'],end_line=r['end'],method=r['name'],file_sha256=r['sourceSha256'],method_sha256=r['excerptSha256'],structural_fingerprint=r['normalizedSha256'],context=r['text'],source_url_or_coordinate='https://github.com/'+r['repo']+'/blob/'+r['commit']+'/'+r['path']+'#L'+str(r['start'])+'-L'+str(r['end'])))
        # Explicitly keep supporting overloads within one family.
        evidence=list({e['candidate_id']:e for e in evidence}.values())
        primary=evidence[0]
        row={k:v for k,v in spec.items() if k!='selectors'}
        row.update(primary)
        row.update(status='helper_reviewed_pending_coordinator',credit=0,accepted=False,evidence=evidence,preservation=spec['observation'],application_limit=spec['limits'],url=primary['source_url_or_coordinate'],excerpt=primary['text'],source_local=primary['source'],source_sha256=primary['sourceSha256'],line=primary['start'],end_line=primary['end'])
        rows.append(row)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    (DOC/'batch-002.json').write_text(json.dumps({'schema':1,'helper':'Halley','credit':0,'master_merge_owner':'Kepler','reviewed_chains':len(rows),'records':rows},ensure_ascii=False,indent=2)+'\n')
    print('Hand-reviewed families',len(rows),'helper credit 0')
if __name__=='__main__':generate()
