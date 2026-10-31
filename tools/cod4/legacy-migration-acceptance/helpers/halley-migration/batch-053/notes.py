# -*- coding: utf-8 -*-
add('betweenlands-legacy-critter-item-id-remap-and-captured-entity-payload-replacement',
[('common/BLDataFixers.java','fixTagCompound',50)]+pick('common/BLDataFixers.java','register onMissingMappings getFixVersion')+whole('item/misc/ItemMob.java')+whole('item/misc/ItemCritters.java')+pick('common/TheBetweenlands.java','preInit init registerEventHandlers')+whole('registries/Registries.java')+pick('registries/ItemRegistry.java','preInit registerItem registerItems')+pick('registries/EntityRegistry.java','preInit registerEntity'),
'TheBetweenlands.init注册模组datafix版本2的ITEM_INSTANCE fixer；MissingMappings事件同时将两个旧物品注册名重定向CRITTER。',
'旧物品根NBT的STRING id=thebetweenlands:gecko/firefly，以及原Count/Damage/tag等潜在载荷；当前CRITTER和实体类注册表。',
'两个旧物品变为thebetweenlands:critter物品，tag.Entity.id区分gecko/firefly；未知id原对象返回。两个别名、missing mapping与NBT转换为一条迁移链。',
'ItemMobFixer首先检查id的NBT类型，再按两个精确全名分支，调用CRITTER.capture(实体类)，把新ItemStack写入全新compound并直接返回。capture(Class,nullableNBT)通过EntityList.getKey取真实注册实体名，把它写进Entity子compound，new ItemStack(this)后setTagInfo；CRITTER继承ItemMob且构造maxStackSize=1、无defaultMob。ItemRegistry.preInit按字段反射并用Locale.ENGLISH小写注册CRITTER；EntityRegistry实际注册两实体为thebetweenlands:gecko/firefly。MissingMappings只修注册指向，物品内实体身份仍由fixer的Entity子载荷决定，不能把两个入口拆计。createCapturedEntity优先Entity子NBT而非显示名；createCapturedEntityFromNBT反序列化实体、生成新UUID并重置位置/速度，onItemUse确认spawn路径返回SUCCESS才在server shrink(1)。spawnCapturedEntity没有检查world.spawnEntity布尔返回值。转换没有读取原Count、Damage、自定义名称、原tag、ForgeCaps或未知根键；因此这是保住物品种类语义但可能丢数量和附加数据的真实反例，不能宣称完整无损。实体类未注册时capture返回EMPTY，新compound仍来自空栈序列化。',
'旧任务载体映射同时核对注册别名与实例载荷；先保留完整源栈数量/标签，再按批准的新格式写入身份，无法解析目标时保留可诊断原数据。对quest_ledger不能只新造默认栈就认定恢复成功。',
'固定1.12-fixes源码，不证明外部Forge数据fix walker覆盖所有嵌套存储位置或调用先后；原生ItemStack序列化/EntityList具体实现在仓外。没有运行上游、原存档或游戏，不把正常捕获/释放/每个实体名算新迁移案例。',
'同一CRITTER替代实现一次；两个旧id和MissingMappings/ITEM_INSTANCE/reader/释放为支持链。与其他模组旧ID重映射主题相近，具体捕获实体载荷替换和原Count丢失语义供Kepler最终去重；credit0。')

add('betweenlands-fixed-legacy-blockentity-id-rewrite-preserving-payload',
[('common/BLDataFixers.java','fixTagCompound',123)]+pick('common/BLDataFixers.java','register getFixVersion')+pick('common/TheBetweenlands.java','init registerEventHandlers')+whole('registries/Registries.java')+whole('registries/TileEntityRegistry.java')+whole('tile/TileEntityPurifier.java')+whole('tile/TileEntityBasicInventory.java'),
'模组初始化把TileEntityNameFixer版本1注册到BLOCK_ENTITY；存档block entity compound进入fixTagCompound。',
'旧id=minecraft:tile.thebetweenlands.<固定历史名>及原坐标/库存/机器NBT；冻结NAMES表和新TileEntityRegistry。',
'命中冻结历史表时只在原compound.setString(id,new)后返回同一对象；非命中原样返回；不按33个表项计数。',
'静态初始化将固定NAMES构造精确旧前缀到thebetweenlands:<name>映射，并有不要添加新TE的注释。fixTagCompound没有重建compound，没有复制子树或抹去未知键，因而此方法边界内Inventory/waterTank/progress等载荷仍留在原对象。TileEntityRegistry.init实际以新ResourceLocation(ModInfo.ID,baseName)注册目标类；以purifier为完整消费端补证：readFromNBT调用父类清库存并读取Inventory后恢复waterTank/state/progress；writer回写对应字段；update实际检查燃料/输出/水，完成时消耗库存与水并产物。它证明重命名后的对象不是仅界面名称变化，但purifier读写/通用库存都只是该ID修复链的消费者，不另计机器迁移建议。父类只在Inventory为compound时交Forge ItemStackHandler.deserializeNBT，缺值清空库存。',
'批准的旧实体/物品ID重定向宜原地只改身份键，保留业务载荷和未知扩展；维护精确历史清单，不用通配前缀误把所有旧名导向任意新类型。',
'此方法getString未先做STRING类型检查，不存在独立逐项错误隔离/历史版本链回滚。方法内保留NBT不等于目标reader保留未知内容；底层Forge handler/FluidTank及原生datafix触发在外部，未展开或运行。没有把purifier加工计时带入玩家Clone白名单。',
'所有旧TE名统一映射控制流一家族，版本号和每个机器名0额外信用；与critter新栈替换不同目标类型/转换/保留边界，可供独立候选但须Kepler跨主账复核，credit0。')

add('betweenlands-herblore-manual-item-owned-discovery-history-restore-and-multi-carrier-union',
pick('api/aspect/DiscoveryContainer.java','updateFromNBT')+whole('api/aspect/DiscoveryContainer.java')+whole('item/herblore/ItemManualHL.java')+whole('api/aspect/IAspectType.java')+whole('api/aspect/AspectItem.java')+pick('herblore/aspect/AspectManager.java','readAspectItemFromNBT writeAspectItemToNbt getAspectItem getStaticAspects get')+pick('registries/AspectRegistry.java','getAspectTypeFromName')+pick('block/container/BlockGeckoCage.java','onBlockActivated')+whole('api/aspect/ItemAspectContainer.java'),
'手册getContainer从自身ItemStack根NBT恢复知识；gecko cage服务端发现消耗材料，将新发现写入玩家库存全部可写手册。',
'discoveries列表，每项完整item栈和aspects列表的type名字；当前AspectItem匹配表、IAspectType注册表。',
'清空后重建AspectItem→已发现类型列表；多手册按列表union查询；写入同一手册根compound的discoveries键，保留其他根标签。',
'ItemManualHL.getContainer确保物品有compound，创建绑定该stack的DiscoveryContainer并updateFromNBT(false)。reader对每项调用AspectManager.readAspectItemFromNBT：从item compound构造ItemStack，再经当前Item→AspectItem matcher定位；aspects逐个IAspectType.readFromNBT按精确名字查注册表。reader没有过滤null item或null type；重复同item项后写覆盖先写。writer会移除null key/空列表，但非空列表中的null type仍调用writeToNBT，可能抛错，未保留未知类型原始文本。mergeDiscoveries对缺item直接共享other列表引用，已有item才contains判重union；查询合并体没有provider，修改共享列表不等于自动持久化源手册。实际gecko流程先要求有手册/活gecko/静态元素，mergedKnowledge.discover后对NEW/LAST写回每本手册、设置恢复600tick、触发成就消息，非creative扣1材料；END不再消费。discover按已存列表长度判断END，并未按当前有效静态集合交集计数，因此过时或重复类型会影响发现资格。getDiscoveredStaticAspects和ItemAspectContainer.getAspects用当前类型过滤可见静态元素，动态数量不受知识门槛。手册本身不是玩家UUID能力，死亡保留依赖实际物品载体生命周期，未见本链Clone拷贝。',
'永久手册历史应有明确载体归属、当前注册解析和幂等集合合并；未知条目隔离保留，不能把查不到或列表长度直接当完成事实。恢复quest_ledger时保留原栈其他tag并核对历史消费者；角色永久白名单与库存携带知识分开审定。',
'只审当前真实格式，不假称有旧字段重命名；未知类型没有安全fallback、writer可能清除或报错；合并存在共享可变列表。知识消费包括发现资格与可见类型，不声称掌握知识是所有炼药配方的服务端权限。没有游戏测试、玩家Clone/inventory外部路径证明。',
'每本书/每item/type/读写/union/gecko发现均同一物品知识恢复家族一次；世界随机分配是另一持久对象且不等同知识。与Patchouli/Roots手册恢复需Kepler语义复核，支持方法共享0额外信用。')

add('betweenlands-world-static-aspect-assignment-restore-preserve-existing-and-fill-new-items',
pick('herblore/aspect/AspectManager.java','loadAndPopulateStaticAspects')+whole('herblore/aspect/AspectManager.java')+whole('api/aspect/Aspect.java')+whole('api/aspect/AspectItem.java')+whole('api/aspect/AspectContainer.java')+whole('api/aspect/ItemAspectContainer.java')+pick('registries/AspectRegistry.java','getAspectTypeFromName')+pick('world/storage/BetweenlandsWorldStorage.java','init readFromNBT writeToNBT getAspectManager forWorld forWorldNullable')+pick('world/storage/WorldStorageImpl.java','onWorldCapability getNewInstance serializeNBT deserializeNBT register')+pick('common/TheBetweenlands.java','registerEventHandlers')+pick('tile/TileEntityInfuser.java','getInfusingAspects isItemValidForSlot'),
'World capability attach新建BetweenlandsWorldStorage并init；原生能力read后用世界seed读itemAspects并填当前新注册项。',
'世界itemAspects.entries，每项原始item栈及aspects[{aspect,amount}]；当前物品matcher、注册aspects、世界seed派生随机种子。',
'保留已读入的item→元素数量分配，仅对当前注册表中不存在于matchedAspects的物品生成补项；缺entries整表重新生成。',
'WorldStorageImpl.onWorldCapability真实绑定world_data并setWorld/init，序列化代理注册IWorldStorage storage，最终调用BetweenlandsWorldStorage.read/write；服务端读itemAspects调用loadAndPopulateStaticAspects。nbt只按hasKey(entries)判分支，loadStaticAspects直接强转entries/aspects为NBTTagList；缺失/错型可能中断。每条ItemStack经当前matcher定位，找不到跳过；任何一个Aspect.readFromNBT类型找不到便continue外层，舍弃整item映射，不保留原始未知项。有效数量int不钳制。updateAspects先containsKey跳过已恢复item（包括空列表），为缺失item按组要求用固定seed随机生成并合并同类型数量，保持已存分配避免升级重洗全部资源；未知/坏类型丢掉的当前item会随后补生成，可能改变既有化学配方。save重新写完整栈身份与aspect名字/amount。实际ItemAspectContainer的Storage.getAmount在未hasStoredStatic时查询世界分配，发生减少才固定storedStatic；Infuser.isItemValidForSlot据这些真实元素决定材料入槽，getInfusingAspects读取实际库存类型；并非仅贴图。世界cap框架、item resource容器及Infuser消费仅补证，不新增容器数量候选。',
'升级恢复先保留原有分配/历史事实，仅对确实新增对象生成默认；把解析失败与从未存在分开，避免因一个缺失依赖使旧进度被重新随机初始化。对旧任务键可采用依赖就绪后补缺策略并保留诊断原始输入。',
'强转/负数/大数/ItemStack解析异常没有逐项保护；固定seed不代表新增项在不同注册遍历顺序/版本下稳定相同，不能称完全确定迁移。已恢复空列表仍阻止补全。WorldStorage同方法还含环境事件/生态时间/kill token，但本项只审itemAspects，不拆它们计数；没有执行Forge或游戏。',
'同一world aspect assignment读写/补缺/物品query/入槽消费者一家族；不按注册item/aspect/group数拆。与手册知识共用身份解析支持，但权威世界随机映射和个人携带发现集合是不同对象与恢复策略，待Kepler最终语义去重；credit0。')

add('excluded-betweenlands-legacy-pouch-type-is-color-default-only',
pick('item/equipment/ItemLurkerSkinPouch.java','checkForLegacyPouch onItemRightClick getColorMultiplier'),
'服务端打开旧pouch时调用checkForLegacyPouch。','缺type的物品根NBT。','只写默认type=7，供染色查询；非任务/库存/永久进度迁移。',
'完整checkForLegacyPouch只确保compound并补type整数；getColorMultiplier将type映射EnumBLDyeColor颜色。虽然方法名带Legacy，未转换Inventory或Clone永久字段，排除不计。onItemRightClick调用仅作真实触发证据，未执行GUI。',
'用实际字段消费者鉴别相关性，不因Legacy关键词增加信用。',
'本记录不裁定整个pouch库存是否另有相关实现，仅排除该颜色默认链。',
'颜色变化/键名默认不独立计数；0候选信用。')
