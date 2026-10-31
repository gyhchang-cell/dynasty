"""Hand-authored semantic reviews; packaging never promotes master credit."""
import json, hashlib, shutil
from pathlib import Path
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=ROOT/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration'
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
INDEX=json.loads((BASE/'method-index.json').read_text())
ALIASES={'a':'wisp-forest/accessories','p':'VazkiiMods/Patchouli','f':'XFactHD/FramedBlocks','i':'AlexModGuy/Ice_and_Fire','s':'P3pp3rF1y/SophisticatedStorage','w':'TwelveIterations/Waystones'}
reviews=[]
def add(alias, family, primary, support, trigger, inp, output, observation, application, limits, risk):
    reviews.append(dict(alias=alias,family='halley-'+family,primary=primary,support=support,trigger=trigger,input=inp,output=output,observation=observation,application=application,limits=limits,semantic_duplicate_risk=risk))

add('a','accessories-deferred-slot-restore',('AccessoriesHolderImpl','read',299),
 [('AccessoriesHolderImpl','decode'),('AccessoriesHolderImpl','init'),('AccessoriesHolderImpl','encode'),('AccessoriesContainerImpl','read'),('AccessoriesContainerImpl','encode'),('AccessoriesContainerImpl','update'),('AccessoriesCapabilityImpl','clearCachedSlotModifiers'),('AccessoriesEventHandler','onLivingEntityTick'),('EndecUtils','dfuKeysCarrier')],
 '附件反序列化先暂存 carrier；capability 初始化后恢复，实体 tick 返还 invalidStacks。',
 '旧大写键、槽类型映射、带槽号物品/外观栈、永久与缓存 modifier。',
 '按当前实体槽配置恢复；不存在的槽提取其栈送入 invalidStacks；服务端返还玩家或掉落。',
 'decode 不立即访问实体注册表；init 在锁内创建当前槽再调用 read。旧键通过 dfuKeysCarrier 写到新键，容器区分同步 modifier 与持久/缓存 modifier；缓存属性复算。CONTAINERS_KEY 闭包处理失效槽，resize 同时保留可容纳的物品和外观，溢出物品先卸下属性再返还。',
 '旧任务载体先保留原始载荷，等目标能力/注册表就绪再转换；把无法安放的真实栈纳入可追踪返还路径。',
 '改键函数若旧键存在会覆盖新键，并不删除旧键。AttributeModifier codec getOrThrow 可中断。闭包缩容遍历从 size-1 开始，可能重复收集末个有效槽；不能照搬。未把附件 copyOnDeath 注册当成永久字段白名单。',
 'holder/container/codec/resize/tick 属同一槽恢复家族，仅建议一项；Fabric/NeoForge copyOnDeath 不另计。')

add('p','patchouli-manual-quest-disk-progress',('PersistentData','BookData'),
 [('PersistentData','setup'),('PersistentData','save'),('PersistentData','DataHolder'),('PersistentData','serialize',79),('PersistentData','serialize',133),('PageQuest','isCompleted'),('PageQuest','questButtonClicked'),('FabricClientInitializer','onInitializeClient')],
 '客户端启动 setup 读 patchouli_data.json；手动任务按钮修改后 save。',
 'bookData 按书 Identifier 分组的 completedManualQuests 等数组。',
 '恢复书内手工完成标记，缺数组为空；每书 serialize 再写完成标记。',
 'PageQuest.isCompleted 对无 trigger 的任务直接查询该持久列表；有 trigger 的任务查询 advancement，不混作同一种进度。BookData 同时读取 history，但 serialize 未写回 history。任一本书的解析异常会冒泡到 setup，将整个文件改成默认值并保存。',
 '为原任务完成标记建立明确持久消费者，并区分客户端手动标记和服务端成就权威；损坏时避免整文件默认覆盖。',
 '此处只有本机书籍手动勾选，没有服务端 Clone/账号隔离保证，不能把它等同服务器任务奖励或功名。GUI 缩放、书签、history 不单独建议。',
 'setup/BookData/serialize/PageQuest 同链一项；旧 page 字段书签保留不新增 credit。')

add('f','framed-camo-validated-restoration',('FramedBlockEntity','loadAdditionalInternal'),
 [('FramedBlockEntity','loadAdditional'),('FramedBlockEntity','loadAndValidateCamo'),('FramedBlockEntity','saveAdditionalInternal'),('FramedDoubleBlockEntity','loadAdditional'),('FramedDoubleBlockEntity','saveAdditional')],
 '方块实体从世界 ValueInput 读回；双材质子类追加第二材质。',
 'camo codec 载荷、overlay、glowing/intangible/reinforced/emissive。',
 '恢复材料和实体状态；未知/无效 camo 降为空并告警；亮度恢复触发强制光照更新。',
 'loadAndValidateCamo 在 codec 成功后仍执行当前 factory 的合法性校验，针对配置/tag 变化可主动移除旧材料；不是只看 NBT 是否能解码。双材质复用同一校验。',
 '旧物品恢复应分开记录解码失败和当前规则不合法，避免静默消失；恢复永久字段后重建派生缓存。',
 '此实现主动丢弃无效材料，不提供隔离保留栈，不能作为 Dynasty 丢任务册的安全 fallback；未声称支持未知历史格式。',
 '基础读取/校验/双材质及 sign/hopper/bookshelf 的委派均同家族；双 camo 不另算。')

add('f','framed-secret-storage-content',('FramedStorageBlockEntity','loadAdditional'),
 [('FramedStorageBlockEntity','saveAdditional'),('FramedStorageBlockEntity','createMenu'),('FramedStorageBlockEntity','preRemoveSideEffects')],
 '秘密储物方块 loadAdditional 恢复，菜单和拆除路径消费同一 handler。',
 'inventory 子对象及 custom_name 组件。',
 '恢复真实存储库存和可选名称；缺 inventory 用空子输入；名称经 parseCustomNameSafe。',
 '恢复的是 27 槽 handler 的库存，菜单直接传入该 handler；拆除时掉落后清空，证实不是仅 tooltip 或网络镜像数据。名称独立安全解析，读库存委托 NeoForge handler。',
 '旧载体内容与显示名称可分离恢复，逐一标明底层 handler 的错误处理边界；实际库存消费者可用于验收。',
 'handler deserialize 实现在本仓之外，本项不能证明其遇到未知 Item ID 会保留原栈；不执行游戏验证。',
 'storage save/load/menu 同链一项；与锯床不同，后者还恢复配方和能量。')

add('f','framed-item-frame-held-stack',('FramedItemFrameBlockEntity','loadAdditional'),
 [('FramedItemFrameBlockEntity','saveAdditional'),('FramedItemFrameBlockEntity','removeItem'),('FramedItemFrameBlockEntity','tickWithMap')],
 '物品展示框方块从世界持久输入恢复，交互取物或地图 tick 使用。',
 'OPTIONAL_CODEC 物品栈、rotation 字节、map_tick_offset 整数。',
 '保存物品组件和数量所需完整 ItemStack，默认空栈；恢复朝向及地图更新相位。',
 '存档恢复 heldItem 与地图 tick 相位，removeItem 使用该真实栈而非重建默认物品。它同时说明并非所有存储字段都是永久进度：mapTickOffset 属派生/调度状态。',
 '替换 quest_ledger 应传递真实栈的 Count/组件，避免只凭物品 ID 构造一个默认新栈；定义需要保留的字段清单。',
 'OPTIONAL_CODEC 失败直接为空；不是无损未知格式回收方案。rotation 未见显式加载范围校验。',
 '地图更新、保存与交互取物作为支持，不将三个字段各算一处。')

add('f','framed-ownable-window-uuid',('FramedOwnableBlockEntity','loadAdditional'),
 [('FramedOwnableBlockEntity','saveAdditional'),('FramedOwnableBlockEntity','setOwner'),('FramedOneWayWindowBlock','isOwnedBy')],
 '单向窗实体持久加载，窗交互检查玩家 UUID 是否等于 getOwner。',
 'UUIDUtil.CODEC owner。',
 '合法 UUID 恢复，缺失或解码失败为 null。',
 'owner 使用 UUID codec 而不是会话实体整数；与玩家对象生命周期分离。setOwner 只有发生变化或 forceSync 时同步。实际交互权限调用见 FramedOneWayWindowBlock 的 owner 比较。',
 '跨 Clone/重登的永久归属使用稳定 UUID；缺归属时由明确业务策略处理，不自动把当前玩家补为主人。',
 '本方法只有存储类型兼容，没有旧名称转换；null 的权限效果取决于消费者，不能推断统一拒绝。',
 '网络读 owner 是持久读取的平行同步入口，不新增；若主账收过同窗 owner 链需合并。')

add('f','framed-powered-saw-resume',('PoweredFramingSawBlockEntity','loadAdditional'),
 [('PoweredFramingSawBlockEntity','saveAdditional'),('PoweredFramingSawBlockEntity','onLoad'),('PoweredFramingSawBlockEntity','tick')],
 '锯床方块 loadAdditional 后 onLoad 解析所选配方，tick 消耗库存/能量。',
 '可选 recipe 字符串、inventory 与 energy 子对象。',
 'ID 语法合法才构造 RECIPE ResourceKey；库存/能量独立恢复。',
 '读取阶段仅保存 recipe key，不把存档中的名字当成已存在配方；onLoad 用运行时 recipe manager 解析并核对配方类型。读取 recipe 缺失时未主动清已有 selectedRecipeId。',
 'FTB 入口恢复采用先解析稳定 ID、后在依赖就绪时解析目标的两阶段处理，入口失效不应连带删除库存。',
 '底层 handler/energy codec 不在仓内；方法不恢复当前加工进度。未证明未知旧物品无损。',
 '配方键、库存、能量同一次锯床恢复只建议一项；不按子对象拆分。')

add('f','framed-tank-fluid-retention',('TankFluidResourceHandler','deserialize'),
 [('TankFluidResourceHandler','serialize'),('FramedTankBlockEntity','loadAdditional'),('FramedTankBlockEntity','saveAdditional')],
 '储罐 BE.loadAdditional 调用流体 handler.deserialize。',
 'FLUID_NBT_KEY 对应 FluidStack.OPTIONAL_CODEC 载荷。',
 '仅解码得到值时设置第零槽；缺值时不替换当前内容。',
 'ifPresent 与 orElse(empty) 有不同恢复含义：新对象通常保留初始化空槽，但对复用对象重读时可能保留旧流体。此处恢复的是实际可提取流体，不是材料贴图。',
 '为原进度键明确“字段缺失保持”或“清为默认”的策略，不能在不同入口中混用。',
 '此方法没有旧流体 ID 重映射，且复用对象可能残留状态；底层资源系统容量约束需另审。',
 'BE 代理/handler reader/writer 合并一项。')

add('f','framed-flower-pot-registry-restore',('FramedFlowerPotBlockEntity','loadAdditional'),
 [('FramedFlowerPotBlockEntity','saveAdditional'),('FramedFlowerPotBlockEntity','addAdditionalDrops'),('FramedFlowerPotBlockEntity','applyMiscComponents')],
 '花盆世界存档恢复，拆除掉落与物品组件恢复共用 flowerBlock。',
 'flower 注册表字符串，物品组件上的花种块值。',
 'tryParse 后注册表 getValue 解析花种；拆除时生成该块物品。',
 '存档不保存显示名称，使用稳定 registry ID；真正的消费者会把保存的花种变成物品掉落，故区别于纯渲染字段。组件路径另有空值/默认处理。',
 '遗留物品映射以 registry key 为证据，读回后追踪到真实物品消费者，不能用语言名称当身份。',
 'tryParse 返回 null 时再交给 registry 的行为本方法未保护；未知 ID 不保留原始字符串，不能照搬为任务物品 fallback。',
 '世界 load、组件入口和掉落同一花种恢复链；不算三个案例。')

add('f','framed-deformation-saved-shape',('FramedCollapsibleBlockEntity','loadAdditional'),
 [('FramedCollapsibleBlockEntity','saveAdditional'),('FramedCollapsibleBlockEntity','unpackOffsets'),('FramedCollapsibleBlockEntity','collectMiscComponents'),('FramedCollapsibleBlockEntity','applyMiscComponents'),('FramedCollapsibleBlock','getShape')],
 '变形方块持久加载 packed offsets；getShape 据此查询/重建 VoxelShape。',
 'offsets packed int，缺省0；物品组件存储展开偏移。',
 '恢复玩家编辑的几何形状，参与实际选择/形状查询。',
 '此字段不是只影响颜色：FramedCollapsibleBlock.getShape 把保存的偏移与 face 合并作为缓存 key 构建形状。世界存档和物品组件都保留 packed int，unpackOffsets 按四个5-bit区间展开供消费者使用。',
 '恢复持久编辑状态后按当前代码重建缓存，不把运行时缓存本身搬进 Clone；区分 schema 与派生表示。',
 '加载只取整值未验证每个 bit/偏移；这是方块持久状态借鉴，对玩家功名无直接字段对应。',
 'Copycat offsets 与 adjustable height 的相近单值 reader 不另计；几何变体合并本族。')

add('f','framed-paint-roller-consumable-codec',('PaintRollerContents','deserialize'),
 [('PaintRollerContents','insert'),('PaintRollerContents','extract'),('PaintRollerContents','shrink')],
 '物品持久组件 CODEC 解码调用 deserialize，涂料提取/消耗使用恢复值。',
 '可选 BlockOverlay holder 与0..256 count；CODEC 字段声明随证据保留。',
 '无 overlay 时归一为 NO_OVERLAY(0)；有 overlay 保留 count。',
 'RecordCodecBuilder 的持久 codec 有 count 范围检查，而平行网络 StreamCodec 仅 VAR_INT；共同 deserialize 不再检查 count。extract 会将 count 变成真实源物品并减去提取数。',
 '旧载体恢复时校验类型与数量的依赖关系，防止身份已丢失仍保留可兑现数量；持久校验与网络校验分别审。',
 '缺 overlay 时剩余 count 被抛弃；0 count 且有 overlay 不归一为空。不可将该策略直接用于有价任务栈。',
 '持久 codec/网络 codec/insert/extract 合并一项；涂料颜色种类不各计。')

add('i','ice-dragon-horn-transactional-carrier',('ItemDragonHorn','useOn'),
 [('ItemDragonHorn','interactLivingEntity'),('EntityDragonBase','readAdditionalSaveData'),('EntityDragonBase','addAdditionalSaveData')],
 '服务器主手对已拥有的龙装入号角；对上表面使用号角恢复实体。',
 'DragonHornEntityID + 完整 EntityTag，可选旧 EntityUUID。',
 '按注册表类型新建实体并 load；addFreshEntity 成功才删三个载体键。',
 '捕获先 save 再移除龙；释放成功才清载体，显式兼容外部旧 EntityUUID。DragonBase load 恢复装备/成长/家及绑定状态，且把攻击/飞行等临时状态也混在同一快照中。',
 '任务册替换必须先确认目标真正接收，再清原载荷；旧 UUID 兼容应显式限定；永久字段不能按全实体快照搬运。',
 'type.create 可为空而后被解引用；释放没有显式服务端 guard；DragonBase 的两支库存读取只有一支限制槽<=4，均非通用安全迁移模板。',
 '号角捕获/释放、DragonBase reader/writer 同链合并；火/冰/雷龙不重复。')

add('i','ice-crystal-uuid-world-recall',('ItemSummoningCrystal','useOn'),
 [('ItemSummoningCrystal','hasDragon'),('ItemSummoningCrystal','summonEntity'),('DragonPosWorldData','load'),('DragonPosWorldData','save'),('DragonPosWorldData','get')],
 '召唤水晶读取保存 UUID，在玩家当前维度查现有实体；DragonPosWorldData 为召回提供位置。',
 '键名包含 Dragon 的子 tag、DragonUUID，世界 DragonMap UUID->坐标。',
 '移动已有实体；成功 flag 后清空水晶 tag；世界 reader 先 clear 再建 UUID 映射。',
 '与号角新建并导入实体 NBT 不同，这条恢复引用已存在实体，位置表只是索引。查找只针对当前维度；chunkLoad 分支含服务端代码里的 isClientSide 条件和未置 true 的 flag2，不能当成可用的跨 chunk 保证。',
 '永久进度引用需明确维度与身份；找不到目标时保留载体以便后续恢复，而不是凭 UUID 再生成重复对象。',
 '任意包含 Dragon 的键都被消费；一次成功会清全部 tag，多条记录可能部分丢失。未见释放时重新校验主人。不能复制此宽松匹配。',
 '水晶/DragonPosWorldData 读取/索引消费只建议一项；位置表不再计独立项。')

add('i','ice-owner-name-to-uuid-family',('EntityDreadMob','readAdditionalSaveData'),
 [('EntityDreadMob','addAdditionalSaveData'),('EntityDreadMob','getCommander'),('TileEntityEggInIce','load'),('TileEntityEggInIce','saveAdditional'),('TileEntityEggInIce','tickEgg')],
 'Dread 实体重载 CommanderUUID；同族冰蛋重载 OwnerUUID 后孵化传给龙。',
 '现代 UUID NBT 或旧字符串名称；冰蛋还携带类型和孵化 age。',
 'UUID 优先，旧字符串用 OldUsersConverter；非 null 才设置所属身份。',
 'Dread 转换调用发生在 try 外，仅 setCommanderId 包了 Throwable；冰蛋则捕获旧字符串转换异常。tickEgg 在服务端新龙上设置 ownerUUID。两者展示同一种旧身份转换，不按键或对象名拆数。',
 '明确稳定 UUID 优先及旧名称转换的失败隔离；审计异常边界是否实际涵盖转换调用。',
 '不能推断 OldUsersConverter 内部在线/离线账号策略；冰蛋 enum 直接用字节作数组下标，损坏数据可能在转换前崩溃。',
 'CommanderUUID 与 OwnerUUID 合并一族；主账已有 MyrmexHive 名称身份链，协调需判断共享 OldUsersConverter 是否进一步语义重复，本项不预给 credit。')

add('i','ice-pet-inventory-rehydration',('EntityHippogryph','readAdditionalSaveData'),
 [('EntityHippogryph','addAdditionalSaveData'),('EntityHippogryph','initHippogryphInv'),('EntityHippocampus','readAdditionalSaveData'),('EntityHippocampus','addAdditionalSaveData')],
 '驯养坐骑实体 NBT 读取恢复装备、箱子库存与指令。',
 'Items compound 列表，Slot unsigned byte；Feedings/Command/Home 和装备标志。',
 '初始化容器后按槽放回完整 ItemStack；已有库存的初始化复制当前栈。',
 'Hippogryph null 分支每个条目再次 init，但 init 会复制旧容器已有非空栈，不能仅凭循环中重建就断言前条目丢失。Hippocampus 相似读取只有 inventory 非 null 才读 Items，作为同族差异保留。',
 '旧库存恢复核查创建时机和重建是否复制已有内容，验证 Count/tag 与槽边界，而不是只验证方法被调用。',
 '读取槽无上界保护；home 的三个坐标非0条件会排除合法零轴地点；飞行/hover 等瞬态被一并保存不应移植到玩家永久进度。',
 'Hippogryph/Hippocampus 近似库存模板合并；不把两种坐骑或多个装备键计为多项。')

add('i','ice-cockatrice-taming-progress-identity-risk',('EntityCockatrice','readAdditionalSaveData'),
 [('EntityCockatrice','addAdditionalSaveData'),('EntityCockatrice','getTamingPlayer')],
 '实体载入驯化积累和命令；getTamingPlayer 用保存整数查当前实体。',
 'TamingLevel、TamingPlayer 整数、Command、HomePosition、Hen/Staring。',
 '恢复驯化累积及当前驯化者引用，缺数字默认为0。',
 '长期驯化进度与会话 entityId 混存，getTamingPlayer 在当前世界按整数查找。该引用在重启/跨维度后并不由 UUID 保证；这是身份边界反例，非普通伤害字段。',
 '永久功名/任务标记绑定玩家 UUID；不保存实体运行期 ID 当完成者身份，同时把暂态凝视状态排除 Clone 白名单。',
 '没有声明格式版本或旧身份纠正。不能凭存储了 tamingPlayer 就声称跨重启仍指同人；home 零轴限制同样存在。',
 '与 Dread 的稳定 UUID/旧名称转换控制流不同；相同 HomePosition 支持不另计。')

add('i','ice-amphithere-riding-taming-home',('EntityAmphithere','readAdditionalSaveData'),
 [('EntityAmphithere','addAdditionalSaveData')],
 '飞蛇实体读档后继续骑乘驯化计时、命令与家位置。',
 'RidingTime、FlightCooldown、Command、HasHomePosition、HomeArea XYZ、Variant/Flying。',
 '整数/布尔直接恢复，只有 HasHomePosition 且三坐标非0才构造 home。',
 'RidingTime 是驯化过程持久累积，与已驯化主人并不是同一个字段；FlightCooldown/Flying 是短期行为状态。一个 reader 混合两种寿命，不能整体复制为“永久”。',
 '建立逐字段寿命分类；历史任务进行中标记与短期战斗/移动冷却分别处理，坐标存在性用明确字段而非0值。',
 '没有范围钳制和 schema 版本。此项只建议持久生命周期边界，不认为应保留玩家飞行状态或所有计时器。',
 'Home 坐标模板与其他宠物重复，仅 RidingTime 驯化累积/冷却寿命组合为差异；协调若认为只是近似读字段模板，应整项降重。')

add('i','ice-pixie-carrier-owner-and-production',('TileEntityJar','load'),
 [('TileEntityJar','saveAdditional'),('TileEntityJar','tick'),('TileEntityJar','releasePixie'),('TileEntityPixieHouse','load'),('TileEntityPixieHouse','saveAdditional')],
 '瓶/屋世界持久载入，生产 tick 和释放精灵消费恢复字段。',
 'HasPixie、PixieType、TamedPixie、PixieOwnerUUID、单槽物品；瓶额外 HasProduced/TicksExisted。',
 '重建单槽并读物品、恢复主人；释放新精灵时设置装备与 ownerUUID。',
 'owner 仅 hasUUID 时赋值，没有旧名称 fallback；生产已完成标记与计时一起恢复，防止把所有 timer 一概认作应清瞬态。释放先添加实体后才设置 tame/owner。',
 '保留任务是否已领取等事实标记，并明确计时器是否属于持久业务过程；新载体归属应在对外可见前完成初始化。',
 'owner 缺失时不主动清已有值，复用读对象可能残留；release 未检查 addFreshEntity 成功就置 hasPixie=false，存在先清后验风险。',
 '瓶/屋两个近似 NBT 实现合并本族；普通精灵外观读取不另计。')

add('i','ice-cocoon-loot-or-concrete-content',('TileEntityMyrmexCocoon','load'),
 [('TileEntityMyrmexCocoon','saveAdditional'),('TileEntityMyrmexCocoon','getItems')],
 '蚁茧容器实体世界读档。',
 'LootTable/seed 或实际 Items 列表。',
 '先创建固定大小空容器；仅 tryLoadLootTable 不成功时导入实际 Items。',
 '恢复逻辑按“未展开的战利品表”和“已生成真实栈”二选一，避免两种表示同时导入而重复发物。saveAdditional 也按 trySaveLootTable 分支配对。',
 '旧任务载体迁移区分尚未兑现的奖励定义与已拥有的实体栈，不能把二者叠加兑现。',
 '依赖原生 tryLoadLootTable/ContainerHelper，未知物品和损坏表的具体 fallback 不在本类。不是蚁巢声望迁移。',
 '不把 load 和 save 两支计为两项；与主账 MyrmexHive 玩家声望链持久对象不同。')

add('i','ice-dragonforge-processing-resume',('TileEntityDragonforge','load'),
 [('TileEntityDragonforge','saveAdditional'),('TileEntityDragonforge','tick')],
 '龙锻炉世界载入后，tick 从 cookTime 和真实输入继续处理。',
 'Items，CookTime；writer 把 cookTime 转 short 后 putInt。',
 '重建库存并加载物品，恢复加工进度；龙焰临时计数不在此 writer。',
 '业务过程 cookTime 保存，但 lastDragonFlameTimer 在重载后不随之恢复；tick 在缺输入/不满足条件时清零或衰减进度。保存发生 short 窄化而读为 int。',
 '区分可持续业务进度与临时刺激源；进度恢复后重新校验当前输入，而不复活旧攻击/免疫计时。',
 'short 转换可能截断大值；load 不作范围校验，super 数据 writer 配对也需由引擎确认。',
 '仅此加工恢复一项；普通 Lectern/Podium 的同型容器 load 不作为新模板数。')

add('i','ice-world-feature-spacing-history',('IafWorldData','load'),
 [('IafWorldData','get'),('IafWorldData','check',55),('IafWorldData','save')],
 '维度 SavedData 工厂加载历史位置，危险结构生成 check 消费。',
 'FeatureType 分类的 id+position 列表。',
 '枚举分类遍历读 NBT，向 LAST_GENERATED 静态 map 追加；保存重新写分类列表。',
 '历史不是临时缓存：check 用记录位置限制后续生成距离。但加载不清 static map，跨维度/重复 load 可合并陈旧记录；check 循环覆盖 canGenerate 而非累计所有距离结果。',
 '持久世界事实与运行期 cache 分离，加载应清理或按维度隔离；重复读档幂等性和判定聚合都要核查。',
 '此项是世界持久状态，距玩家任务进度较远，列低优先级；不研究建筑设计，也未运行世界生成。',
 '与 DragonPos UUID 召回索引不是同对象/控制流；每 FeatureType 或每位置不能各计。')

add('i','ice-bestiary-additive-page-progress',('EnumBestiaryPages','addPage'),
 [('EnumBestiaryPages','possiblePages'),('EnumBestiaryPages','containedPages'),('ItemBestiary','inventoryTick'),('ItemBestiary','onCraftedBy')],
 '工作台研究/解锁调用 addPage；库存 tick 为无 tag 的旧书建立介绍页。',
 '物品 NBT Pages int[]，书原有其他键。',
 '复制已有页索引列表，仅未包含时追加；再写回同一个 tag。',
 '这是书上实际已解锁内容进度，addPage 不覆盖其他 tag。inventoryTick 只在整个 tag 为 null 才补介绍页；有 tag 但无 Pages 时不会补。containedPages 直接按索引取 ALL_PAGES，非法索引可抛异常。',
 '旧任务标记采用增量合并而非替换整份标签，区分缺整个容器与缺子键两种旧档形态；验证外来整数索引。',
 '枚举 ordinal 作为持久身份会受枚举重排影响；不是稳定 ID 迁移，也不能复制为任务奖励来源。',
 '初始化/查缺/追加构成一本书恢复链，逐页/各种书页不另计。')

add('i','ice-stone-statue-selective-snapshot',('EntityStoneStatue','readAdditionalSaveData'),
 [('EntityStoneStatue','buildStatueEntity'),('EntityStoneStatue','addAdditionalSaveData'),('ItemStoneStatue','useOn')],
 '石像实体世界读档或石像物品 useOn 导入 IAFStoneStatueNBT。',
 'StatueEntityType、StatueEntityTag、形体尺寸/scale、CrackAmount。',
 '恢复被封存实体表现及快照；创建快照时对 Player 显式不 saveWithoutId。',
 '与号角恢复活龙不同，石像保留被封实体 tag 但只创建石像包装；玩家快照被特意排除。writer CrackAmount 为 int 而 reader 为 byte，存在数值窄化。ItemStoneStatue.useOn 先读内层，再在服务端读整个外层 stack tag，可能用缺省覆盖前次字段。',
 '迁移载体明确白名单对象并防止把整份玩家数据塞入替代物品；检验嵌套层级和两次读覆盖顺序。',
 '不声称可以复原玩家或原生实体；这是快照边界反例，内外层格式兼容需实测而本任务禁止启动。',
 'entity snapshot/reader/item importer 合并一项；与号角存在序列化容器共同模式，协调按包装对象与选择性排除差异判重。')

add('s','sophisticated-uuid-content-world-restoration',('ItemContentsStorage','readStorageContents'),
 [('ItemContentsStorage','get'),('ItemContentsStorage','load'),('ItemContentsStorage','writeStorageContents'),('WoodStorageBlockBase','setPlacedBy'),('LegacyStorageBlockDataMigration','normalizeStorageContents'),('LegacyStorageBlockDataMigration','normalizeBlockEntityTag'),('LegacyStorageBlockDataMigration','normalizeStorageWrapperTag'),('LegacyStorageBlockDataMigration','normalizeContentsNbt'),('LegacyStorageBlockDataMigration','normalizeInventory')],
 'SavedData 工厂读 UUID 内容库；木容器放置按 STORAGE_UUID 恢复后移除该世界记录。',
 '旧 shulkerBoxContents 或新 storageContents 列表，每条 uuid+contents。',
 '旧键存在则优先选旧列表；规范化嵌套库存，再存入 UUID map，writer 统一新键。',
 '加载会调用 LegacyStorageBlockDataMigration 对嵌套 storageWrapper/contents 中库存与升级库存归一；底层 LegacyItemStackMigration 在 SophisticatedCore，不在本批重复研究。setPlacedBy 仅非 linked endpoint 恢复内容，loadAdditional 后才 removeStorageContents。',
 '旧键与新键冲突时定义明确优先级并保留诊断；载体恢复成功后一次性移除来源，防止重复兑换库存。',
 'UUID 缺失 Objects.requireNonNull 可使整个加载失败；外部 Core 规范化细节未列为新证据。remove 早于后续容量/初始化完成，没有事务回滚。',
 '与主账 StackStorageWrapper.loadSlotNumbers 的容量元数据提升有支持重叠，主项限 SavedData 外层旧列表+UUID 消费；若主协调已收整条 stash 恢复应整项合并。')

add('s','sophisticated-orphan-double-chest-salvage',('ChestBlockEntity','loadAdditional'),
 [('ChestBlockEntity','dropSecondPartContents')],
 '单箱读到超过单箱上限的库存，且不在升级过程时触发半箱内容回收。',
 '已恢复 inventory slots、当前 SINGLE 方块状态和 isBeingUpgraded。',
 '将超出单箱槽位的栈复制并清槽，排队掉落；缩小存储并删除失效槽设置。',
 'linked storage 在 dropSecondPartContents 中直接返回，避免缩小共享数据。普通库存先从原 handler 清出，再以 TickTask 延后掉落，最终刷新升级包装与外观侧。',
 '布局/容量变化应显式回收溢出而非截断；升级中的中间状态需 guard，避免误判损坏而发物。',
 '任务排队前已清槽，崩溃窗口可能丢物；无 level/server 时也可能清槽而不发物。仅静态验证。',
 'load 判定和 dropSecondPartContents 为同链一项；不按每个溢出槽计。')

add('s','sophisticated-live-tier-snapshot-replacement',('StorageTierUpgradeItem','upgradeStorageBlock'),
 [('StorageTierUpgradeItem','tryUpgradeStorage',101),('StorageTierUpgradeItem','upgradeStorage',144),('StorageTierUpgradeItem','upgradeDoubleChest')],
 '服务端升级物品校验权限/数量，通过具体 tier definition 升级已存在模组容器。',
 '旧 BE.saveAdditional 全部数据、新方块状态及目标 inventory/upgrade 容量。',
 '先新建 BE 并 load 快照，标记升级、关菜单，再替换世界 BE；按 linked/普通路径调整容量。',
 '新对象在旧对象移除之前完成 NBT 导入，isBeingUpgraded 避免 Chest load 的溢出回收；双箱主/从决定哪一半扩双倍容量，整个双箱仍复用 upgradeStorageBlock。',
 '替代任务物品/玩家数据恢复可先构建并验证目标，再清源；明确迁移中间状态防止正常清理误触发。',
 '世界替换与 linked 容量更新不原子，后者失败会在旧 BE 已移除后抛异常；没有事务回滚。',
 '单箱/双箱及所有 tier/颜色/材质同一迁移实现合并一项；主账 canonical reader 仅被支持调用，不重复建议它。')

add('s','sophisticated-vanilla-container-import',('StorageTierUpgradeItem','upgradeStorage',316),
 [('StorageTierUpgradeItem','upgradeStorage',275),('StorageTierUpgradeItem','setStorageItemsNameAndWoodType'),('StorageTierUpgradeItem','replaceBlockAndBlockEntity')],
 'vanilla tier definition 在玩家有 canOpen 权限时把原版容器转模组容器。',
 '原版容器逐槽 ItemStack、customName、目标 woodType 与新 blockstate。',
 '只导入明确挑选的物品/名称/木类型；相邻双箱分别转换后 join。',
 '这条不复制整个旧 BE NBT，而是显式导出 be.getContainerSize 的每槽，再向新容器赋值；与模组容器升级的原始快照迁移有不同保留边界。',
 'Clone 永久进度优先选择允许字段导入，避免复制整份 ForgeData；真实物品栈与显示属性分别迁移。',
 '它只承诺容器接口能读到的栈和名称，不保留任意旧 BE 自定义数据；双箱另一半缺失时允许先前转换保留，无整体回滚。',
 '原版箱/桶/潜影盒与染色注册变体不拆数；底层 setStorageItems... 仅支持。')

add('s','sophisticated-limited-barrel-policy-repair',('LimitedBarrelBlockEntity','loadAdditional'),
 [('LimitedBarrelBlockEntity','setFixedSettings')],
 '限槽桶服务端/无 level 读档后按实际容量重建固定槽策略。',
 'storageWrapper 恢复的 inventory 槽数、display selected slots、noSort slots。',
 '两种策略集合大小不等于实际槽数时，重选0..N槽。',
 '实际 no-sort 持久策略与容量耦合，加载后执行修复；只比较集合 size 而非成员内容，大小相同但含越界槽不会修复。客户端有 level 时不改。',
 '恢复永久配置后检查与当前容量/角色规则的约束，不把所有旧设置原样带入；判断应比较实际成员而不只数量。',
 'display 是界面策略，单独不计；本项相关点限真实库存 no-sort 规则，离任务迁移较远，列低优先级建议。',
 '两个 settings category 修复算同一项；若主账已覆盖整条 LimitedBarrel 读后修复，需合并。')

add('s','sophisticated-crafting-tier-component-preservation',('StorageTierUpgradeRecipe','assemble'),
 [('StorageTierUpgradeRecipe','matches'),('StorageTierUpgradeRecipe','canUpgrade'),('StorageTierUpgradeRecipe','isPrimaryOrUnlinked'),('StorageTierUpgradeShapelessRecipe','assemble'),('DoubleChestTierUpgradeRecipe','assemble')],
 '合成升级旧容器物品；matches 验证 endpoint 角色，assemble 保留原组件。',
 '原 storage item 的完整 components、新配方输出与容量缺省。',
 '非 primary/非 unlinked 返回空栈；原 components 复制到升级输出，再按新 tier 调整槽数。',
 '角色检查同时在 matches 和 assemble，但只有 matches 的 canUpgrade 会核对服务端 manager 里的真实 primary 身份。物品有 STORAGE_UUID 时才重写容量。DoubleChest 只是乘2模板，shapeless 是同实现包装，全部合并。',
 '替换物品保住 Count/组件后再更新目标特有容量；不要只信载体上的可伪造角色标志，提交入口也应重新核实权威身份。',
 'applyComponents 是广泛复制，可能携带不应迁移的暂态组件；本批不重复 credit 主账 StackStorageWrapper 容量提升 reader。',
 'shaped/shapeless/single/double 全部本族一次；双倍容量模板不单独计数。')

add('s','sophisticated-vanilla-shulker-capability-import',('ShulkerBoxFromVanillaShapelessRecipe','assemble'),
 [('ShulkerBoxFromVanillaShapelessRecipe','matches'),('ShulkerBoxFromVanillaShapelessRecipe','getVanillaShulkerBox')],
 '将原版潜影盒物品在合成中转为模组容器；通过物品 ItemHandler capability 读取内部物品。',
 '原版潜影盒物品的 capability 库存、配方新输出；不是已经放置的 BE。',
 '有 capability 时为目标确保 contents UUID，遍历非空栈，复制并插入目标 handler；无 capability 仍返回配方输出。',
 '与物品 tier 配方整份 applyComponents 不同，本项通过 capability 枚举实际栈，只复制内容；与世界 BE 转换也不同，插入策略可重新排列槽。insertItem 返回的未插入余量未检查，因此不能认为转换必然无损。',
 '旧任务载体转换需验证源能力存在、目标容量足够且实际接受所有数量；只有全部接收才消耗输入，否则保留可恢复余量。',
 '没有复制 customName/其他源组件；capability 缺失或目标拒收时可能产出空/不完整容器，且方法没有回滚。Core 的 ensureContentsUuid 内部实现不作为本批独立信用。',
 '一次 capability 库存导入为一项；不按颜色/每槽计。与第27项世界逐槽导入共享意图但载体、API、槽位策略与失败语义不同，请 Kepler 最终语义去重。')

add('w','waystones-player-unlock-reference-pruning',('PersistentPlayerWaystoneData','getWaystones'),
 [('PersistentPlayerWaystoneData','getWaystonesData'),('PersistentPlayerWaystoneData','getActivatedWaystonesData'),('PersistentPlayerWaystoneData','activateWaystone'),('PersistentPlayerWaystoneData','isWaystoneActivated'),('PlayerWaystoneManager','activateWaystone'),('PlayerWaystoneManager','getPlayerWaystoneData',551),('WaystoneProxy','getBackingWaystone')],
 '服务端 PlayerWaystoneManager 选择 persistent backend 后列出玩家解锁传送点。',
 'Balm 玩家持久数据根内 WaystonesData.Waystones 的字符串 UUID 列表。',
 'UUID 转代理并查世界 manager；无效引用直接从原 NBT 列表删除，合法点进入结果。',
 'getWaystonesData 与 getActivatedWaystonesData 会把 getCompound/getList 得到的容器写回父 tag，因而列表 iterator.remove 直接改持久玩家数据。公开 activate 先判重且只记录普通 WAYSTONE，底层 activate 自身不判重。',
 '旧任务依赖暂时未载入时不要把“当前查不到”当成永久无效直接删进度；明确根容器的别名和缺省类型修复副作用。',
 'UUID.fromString 损坏条目未隔离，可能中断整个列表；Balm.getPersistentData 的死亡 Clone 行为不在此仓源码中，不能声称已验证死亡保留。冷却时间键不是本项永久进度白名单。',
 '读/写/判重/代理解析同一玩家解锁家族一次；排序、每个传送点和两个冷却键不另计。')

add('w','waystones-world-schema-origin-upgrade',('WaystoneManager','read'),
 [('WaystoneManager','save'),('WaystoneManager','get'),('Waystone','read',168),('Waystone','write',199),('WaystoneBlockEntityBase','load'),('WaystoneBlockEntityBase','onLoad'),('WaystoneBlockEntityBase','loadBackingWaystone'),('Waystone','isOwner')],
 '主世界 SavedData 工厂读 Waystones；方块 BE onLoad 再按 UUID 连接该世界对象。',
 'WaystoneUid/World/BlockPos/Name/IsGlobal，可选 OwnerUid/Type/Origin，旧 WasGenerated。',
 '旧 WasGenerated 转 WILDERNESS/UNKNOWN，合法新 Origin 覆盖；Type 缺省普通 waystone；清理无名 sharestone。',
 'Waystone.read 对非法 Origin 名称保留旧 boolean 推导结果，但 UUID 和维度 ResourceLocation 无同等异常隔离。manager 为修复 #1133 主动跳过无名 sharestone；BE 未找到 backing UUID 时会初始化新端点，并更新位置/维度。',
 '旧字段升级定义新旧优先级和枚举 fallback；区分不可逆清理与临时依赖缺失，新造身份可能令旧玩家引用失联。',
 'OwnerUid 缺省 null，而 isOwner 对无主对象返回 true，兼容默认改变权限边界。没有整表逐条隔离，坏 UUID 可使 SavedData 读失败。',
 'world schema reader、manager 清理、BE UUID 重连统一一族；每个 Type/Origin/上下半块不拆数。')

add('w','waystones-bound-carrier-uuid-and-quantity',('BoundScrollItem','getWaystoneAttunedTo'),
 [('BoundScrollItem','setWaystoneAttunedTo'),('BoundScrollItem','useOn'),('BoundScrollItem','finishUsingItem'),('AbstractAttunedShardItem','getWaystoneAttunedTo'),('AbstractAttunedShardItem','setWaystoneAttunedTo'),('PlayerWaystoneManager','tryTeleportToWaystone'),('PlayerWaystoneManager','tryTeleport')],
 '绑定卷轴/碎片从物品 tag 恢复目标 UUID；卷轴绑定时拆一件，使用时交给传送消费者。',
 'WaystonesBoundTo 或 AttunedToWaystone 的 NBT int[] UUID，原栈数量和其他 tag。',
 '符合类型才产生 WaystoneProxy；缺失为 null。绑定一件时保留原栈或 split(1)，多余绑定输出优先放库存，失败掉落。',
 'setWaystoneAttunedTo 原地改指定键而非 setTag 覆盖整份；null 只移除绑定键。finishUsingItem 不直接删除栈，真正消费发生在 tryTeleport 的事件/资格检查之后，但仍在 doTeleport 之前。',
 '替换任务载体按实际件数拆栈并保留其他 tag；把成功确认与消耗点放在同一完整链审查，不能看到 finishUsingItem 返回原栈便判定不消耗。',
 'int[] 类型检查不保证 UUID 数组长度正确；reader 可返回无效代理。距离检查未先比较维度；tryTeleport 先扣物品/经验再执行移动，不提供失败回滚保证。',
 '卷轴和碎片只换键名，明确合并；传送引擎、API 包装、网络消息不再单独计。')

add('w','waystones-warp-plate-attunement-receipt',('WarpPlateBlockEntity','load'),
 [('WarpPlateBlockEntity','saveAdditional'),('WarpPlateBlockEntity','initializeInventory'),('WarpPlateBlockEntity','serverTick'),('WarpPlateBlockEntity','trySelectRecipe'),('WarpPlateBlockEntity','getTargetAttunementStack')],
 '传送板 BE 读档后，serverTick 继续调谐/选择目标；初始化配方填入首次材料。',
 'Items、ReadyForAttunement、CompletedFirstAttunement、LastAttunementSlot。',
 '恢复已支付物品和首次调谐事实、轮询游标；attunementTicks 与实体站立等待表不序列化。',
 '初始化配方缺失时 completedFirstAttunement 置 true 避免继续当首次未完成；serverTick 完成后绑定产物、扣四个外槽、置完成事实。getTargetAttunementStack 用恢复游标轮询，但即使随机选择也推进游标。',
 '长期已完成/已领取事实与短期等待计时分开，迁移不要因遗漏计时器重复发首次材料或奖励；恢复后重验当前配方。',
 'load 未清已有 items；LastAttunementSlot 未钳制，负值可能产生负索引。serverTick 含 Minecraft.getInstance 客户端访问；中心数量>1 分支通常被 trySelectRecipe 阻止，不能据此宣称服务端必崩。未运行上游。',
 '调谐库存、首次事实与轮询游标同一板生命周期一次；绑定 shard reader 仅引用第33项的同族语义，不另为配方品种计数。')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def select(alias,spec):
    file,method,*line=spec
    rows=[r for r in INDEX if r['repo']==ALIASES[alias] and r['path'].endswith('/'+file+'.java') and r['method']==method and (not line or r['start_line']==line[0])]
    if len(rows)!=1:raise ValueError((alias,spec,[(r['path'],r['start_line']) for r in rows]))
    return rows[0]
def field(alias, filename, fieldname):
    # Only used for supporting codec closures; never a new review/count.
    import sys
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(BASE))
    import extract
    template=next(r for r in INDEX if r['repo']==ALIASES[alias] and r['path'].endswith('/'+filename+'.java'))
    raw=(ROOT/template['original_file']).read_bytes()
    nodes=[n for n in extract.walk(extract.PARSER.parse(raw).root_node) if n.type=='field_declaration' and any(c.type=='variable_declarator' and raw[c.child_by_field_name('name').start_byte:c.child_by_field_name('name').end_byte].decode()==fieldname for c in n.named_children)]
    assert len(nodes)==1,(filename,fieldname)
    n=nodes[0];text=raw[n.start_byte:n.end_byte].decode()
    return dict(template,start_line=n.start_point.row+1,end_line=n.end_point.row+1,method=fieldname+' [complete supporting field declaration]',context=text,method_sha256=sha(text.encode()),structural_fingerprint=extract.norm(n,raw),candidate_id=sha((template['repo']+template['revision']+template['path']+str(n.start_byte)).encode())[:20],parse_has_error=n.has_error,evidence_kind='supporting_codec_field_not_separate_credit')
def package():
    pins={p['repo']:p for p in json.loads((BASE/'source-pins.json').read_text())}
    manifests={}; outputs=[]
    def evidence(r):
        pin=pins[r['repo']]; key=(r['repo'],r['path'])
        if key not in manifests:
            original=ROOT/r['original_file'];raw=original.read_bytes(); assert sha(raw)==r['file_sha256']
            tree=json.loads((ROOT/pin['metadata_dir']/'tree.json').read_text())
            blob=next(v for v in tree['tree'] if v['path']==r['path'])
            gitsha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert gitsha==blob['sha']
            dest=BASE/'sources'/r['repo'].replace('/','__')/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            manifests[key]=dict(repo=r['repo'],commit=r['revision'],root_tree=pin['root_tree'],path=r['path'],source=str(dest.relative_to(ROOT)),sourceSha256=sha(raw),blob=gitsha,size=len(raw),verified_against_official_tree=True)
        m=manifests[key]
        return dict(r,private_file=m['source'],source=m['source'],source_local=m['source'],sourceSha256=m['sourceSha256'],source_sha256=m['sourceSha256'],blob=m['blob'],git_tree=pin['root_tree'],source_url_or_coordinate='https://github.com/'+r['repo']+'/blob/'+r['revision']+'/'+r['path']+'#L'+str(r['start_line'])+'-L'+str(r['end_line']))
    for number,item in enumerate(reviews,1):
        p=select(item['alias'],item['primary']);es=[evidence(p)]+[evidence(select(item['alias'],s)) for s in item['support']]
        if number==1:es.append(evidence(field('a','AccessoriesHolderImpl','CONTAINERS_KEY')))
        if number==11:
            es.extend(evidence(field('f','PaintRollerContents',name)) for name in ['CODEC','STREAM_CODEC'])
        rec={k:v for k,v in item.items() if k not in ['alias','primary','support']}
        rec.update(id='halley-migration-%02d'%number,candidate_id=p['candidate_id'],status='helper_reviewed_pending_coordinator',credit=0,accepted=False,review_scope='Static full-method/chain review; not game-tested; no upstream code executed',evidence=es,supporting_candidates=[r['candidate_id'] for r in es[1:]],preservation=item['observation'],application_limit=item['application']+' 限制：'+item['limits'])
        rec.update(repo=p['repo'],revision=p['revision'],commit=p['revision'],path=p['path'],start=p['start_line'],end=p['end_line'],line=p['start_line'],end_line=p['end_line'],name=p['method'],source=es[0]['source'],source_local=es[0]['source'],sourceSha256=p['file_sha256'],source_sha256=p['file_sha256'],text=p['context'],excerpt=p['context'],excerptSha256=p['method_sha256'],normalizedSha256=p['structural_fingerprint'],source_blob=es[0]['blob'],git_tree=es[0]['git_tree'],url=es[0]['source_url_or_coordinate'])
        outputs.append(rec)
    (DOC/'reviewed-suggestions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in outputs))
    (DOC/'batch-001.json').write_text(json.dumps(dict(helper='halley-migration',target=30,reviewed_chain_records=len(outputs),accepted=0,credit=0,novelty_not_certified=True,counting_note='Raw reviewed chains include prior/parallel overlaps. Use reconciliation.json; never import this array as new credit automatically.',records=outputs),ensure_ascii=False,indent=2)+'\n')
    (BASE/'source-manifest.json').write_text(json.dumps(list(manifests.values()),ensure_ascii=False,indent=2)+'\n')
    print('Packaged',len(outputs),'reviewed chains including overlaps; credit0;',len(manifests),'whole files')
if __name__=='__main__':package()
