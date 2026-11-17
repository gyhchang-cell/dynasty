# -*- coding: utf-8 -*-
framework=pick('capability/base/EntityCapabilityHandler.java','registerEntityCapability registerCapabilities registerCapability onAttachCapabilities onPlayerClone getEntityCapabilities')+pick('capability/base/EntityCapability.java','setEntity init getEntityCapability isPersistent clonePersistentData')+pick('registries/CapabilityRegistry.java','preInit')+pick('registries/Registries.java','preInit')+pick('common/TheBetweenlands.java','preInit registerEventHandlers')
add('betweenlands-equipment-physical-stacks-amulet-slot-entitlement-and-gem-mirror-clone-lifecycle',
pick('capability/equipment/EquipmentEntityCapability.java','readFromNBT')+whole('capability/equipment/EquipmentEntityCapability.java')+whole('capability/equipment/EnumEquipmentInventory.java')+whole('inventory/InventoryEquipment.java')+whole('inventory/InventoryEquipmentAmulets.java')+whole('capability/equipment/EquipmentHelper.java')+whole('handler/ItemEquipmentHandler.java')+whole('capability/circlegem/CircleGemEntityCapability.java')+whole('capability/circlegem/CircleGem.java')+pick('capability/circlegem/CircleGemType.java','fromName fromID getRelation')+pick('capability/circlegem/CircleGemHelper.java','setGem getGem getGems handleAttack getActiveItem getMultipleProcStrength applyProc')+pick('item/equipment/ItemAmulet.java','onEquip onUnequip onEquipmentTick createStack canEquip canDrop')+whole('item/misc/ItemAmuletSlot.java')+pick('handler/AttackDamageHandler.java','onEntityAttacked')+framework,
'实体equipment能力读NBT重建分类物理库存；Clone统一入口仅在非死亡或keepInventory真时复制；宝石能力采用相同条件并行读写。',
'amuletSlots int；inventories[{id,items[{slot,stack}]}]完整ItemStack；同护符衍生的gems[{gem,type}]；old/new玩家、wasDeath、旧世界keepInventory。',
'重建固定最大槽位物理列表，清缓存IInventory；恢复可选开放护符槽数。死亡keepInventory=false不复制两个组件；真实掉落事件清库存。宝石镜像不另建议信用。',
'Equipment reader先inventories.clear并为三种固定Enum id新建空最大数组，缺amuletSlots保持构造默认1，复用对象缺键则保留旧数。分类id不能识别跳过；slot仅检查<数组size，负slot仍可set越界，重复slot后写覆盖；不检查Item合法类别/数量/有效解锁槽，未知栈依赖原生ItemStack读取。writer扫描最大物理列表，包含当前未开放的隐藏槽；InventoryEquipmentAmulets.getSizeInventory只返回min(amuletSlots,3)，因此持久内容与当前可访问容量不同。ItemAmuletSlot.addAmuletSlot消费工具耐久增加同组件amuletSlots，creative可超过3；set无markDirty。整体Clone条件把这个已购买容量与可掉落装备一起处理，说明永久解锁和物品载荷不分离会影响死亡边界。onDeathDrops仅server且!keepInventory，遍历可访问槽，对IEquippable先onUnequip，再canDrop；即使canDrop=false continue，最终inv.clear仍清物理列表，不能把不可掉落理解为死亡保留。装备helper复制栈、模拟接收、调用onEquip再实际插入；指定slot重载已有一次非模拟插入再通用insert，未证明原子。ItemAmulet.onEquip添加BOTH gem，onUnequip删除第一个匹配类型，onEquipmentTick空；装备read直接恢复数组，不重放onEquip，独立gem能力NBT保持战斗状态。CircleGem reader名字未知回NONE、combat ordinal只上界无下界，负数异常；getter返回unmodifiable list但add不去重。AttackDamageHandler实际读取恢复的RING_OF_POWER库存和CircleGemHelper伤害关系，因此不是GUI槽缓存。',
'为Clone分别列出经审定的永久容量/历史和真实装备归属，不把整能力包一并复制；恢复派生状态要明确是否重放onEquip，防重复叠加/丢战斗能力。原Count/tag完整栈、隐藏槽和溢出策略需一起审查，死亡掉落与保留不可同时重复发物。',
'仅作为上游语义研究，不改变本项目keepInventory、死亡惩罚或增加slots机制。物理装备/宝石镜像没有按三个inventory或三色拆计；外部Forge与原生ItemStack/InvWrapper不在本仓，未执行或证明跨事件时序。getEntity声明EntityPlayer但isApplicable接受EntityLivingBase，为其他实体泛型使用有潜在边界；不能声称全实体安全。',
'护符实际栈、已购买槽数、圆宝石镜像同装备生命周期合为1建议。与Accessories/Curios/ToolBelt已收家族主题相近，具体购买容量与条件Clone/隐藏槽/parallel gem serialization需Kepler最终审查；不把支持cap框架算新实现。')

add('betweenlands-food-specific-diet-memory-always-clone-with-feedback-cache-excluded',
pick('capability/foodsickness/FoodSicknessEntityCapability.java','readFromNBT')+whole('capability/foodsickness/FoodSicknessEntityCapability.java')+whole('capability/foodsickness/FoodSickness.java')+whole('handler/FoodSicknessHandler.java')+framework,
'已注册food_sickness能力磁盘读；PlayerEvent.Clone中isPersistent恒true，无论真实死亡或非死亡都通过NBT重建。',
'HatredMap[{Food注册字符串,Level整数}]；lastSickness枚举和客户端lastUsedItem等反馈缓存为非持久字段。',
'新HashMap替换旧饮食厌恶记忆，已注册食物按名字恢复level；未知食物跳过；仅writer列出的记忆跨Clone，lastSickness不随之复制。',
'writer保存每个Item注册名及Level，reader先新建map，再Item.getByNameOrId解析，非null才写入，重复Food后写覆盖；缺/错型list为空。reader不校验是food/IFoodSicknessItem，不钳制level；日常increase按最终阈值180钳制但不能推断加载也被钳制。getSicknessForHatred按50/110/180上界分档，>=180回SICK，负数回FINE。真实onUseItemTick只在服务端且duration<=1、开启规则/维度/食物可得病时读取记忆：SICK减少食物/衰败恢复量，其余根据本食物历史减少别的食物厌恶，最终加5并同步反馈。这个事件在即将结束tick执行而非明确消费成功回执，不证明被别的模组取消使用后不会记账。lastSickness只用于消息变化比较，写NBT没有它；默认FINE，Clone/重登后反馈门槛重置，而持久饮食历史保留。统一clonePersistentData写到新compound再调用新reader，没有引用共享map，也没复制实体hurtTime等临时字段。',
'经批准的长期历史集合应单独writer白名单并用稳定注册身份恢复，短期反馈去重缓存不因同对象而带过Clone。先确认原设计是要保留还是重置，不能把“死亡全清”或“所有键全拷”套给所有组件。',
'上游保留饮食厌恶是有意负面历史，不得在Dynasty新增此惩罚；本项适用是字段分类和reader语义。未知Food无隔离、无旧别名、无范围约束；原生getByNameOrId兼容数字ID的外部实现未展开。同步与服务端食用时序未实测，不声称当前游戏行为验收。',
'所有食物键、阈值、消息支持与Clone同一记忆家族一次；与Diet/SoLCarrot共享长期饮食主题，FoodSickness惩罚记忆和alwaysClone具体对象请Kepler跨账去重，credit0。')

add('betweenlands-player-carried-entity-passenger-save-and-deferred-login-materialization',
pick('capability/playermounts/PlayerMountsEntityCapability.java','readFromNBT')+whole('capability/playermounts/PlayerMountsEntityCapability.java')+framework,
'玩家能力序列化收集骑在玩家身上的BL实体；读档排队原始compound；PlayerLoggedInEvent服务端生成实体并重新骑玩家。',
'PlayerPassengers COMPOUND list，实际原子写出的IEntityBL实体NBT；queuedPassengers为载入后的待实例化列表。',
'恢复物理乘客实体而非只缓存ID；断线期间取消特定dismount，保证玩家存档还能捕获乘客。',
'writer检查player.isBeingRidden，只遍历直接getPassengers且instanceof IEntityBL，用writeToNBTAtomically成功的完整NBT入列表；不保存全部模组实体或仅存会话entityId。reader每次clear queue，typed list的每个compound原引用入queue；本层不校验entity id/owner/UUID/维度。onPlayerJoin逐个AnvilChunkLoader.readWorldEntity(nbt,player.world,true)，非null强制startRiding(player,true)。未清queue、未依据spawn/riding成功结果逐条确认，因此重复login回调可重试相同载荷，不能称幂等一次消费。保存writer完全忽略queuedPassengers，若重新写盘发生在还未实例化的窗口，未见保留待恢复载荷的fallback。onMountEvent当玩家MP.hasDisconnected且BL rider时取消dismount，防原生断线移除先于玩家保存。组件未覆盖isPersistent，使用基类!wasDead；不能把登录恢复当作真实死亡后永久带宠物。',
'旧物品/进度依赖实例化时，可保留原始待恢复载荷到依赖就绪，再逐条成功确认消费；中途再保存必须同时保留未恢复队列，防尚未生成的数据被writer遗漏。稳定UUID/归属和重复恢复防护要在重建边界补齐。',
'外部AnvilChunkLoader可生成嵌套实体的具体规则未展开，未证明UUID冲突或原区块重复实体处理；startRiding返回值不检查。只研究玩家携带实体持久化，不复制短暂战斗计时/无条件死亡保留。没有上游运行或原档操作。',
'登录恢复queue、断线dismount保护和writer同一玩家乘客生命周期一家族；支持capClone/注册不另计。与Identity/Requiem实体重建主题相近，具体玩家携带乘客而非身份变身需Kepler最终去重。')

add('betweenlands-coordinate-bound-paid-blessing-persistence-and-consumption-before-real-death',
pick('capability/blessing/BlessingEntityCapability.java','readFromNBT')+whole('capability/blessing/BlessingEntityCapability.java')+pick('tile/TileEntitySimulacrum.java','update isActive updateEffects getClosestActiveTile onLivingDeathFirst')+pick('handler/PlayerRespawnHandler.java','getSpawnPointNearPos')+framework,
'附近激活BLESSING塑像服务端消耗供品设置玩家blessing坐标/维度；能力读档恢复；最高优先级LivingDeathEvent检查后取消死亡并消费资格。',
'x/y/z INT三元组、dimension整数；BLessing能力默认location=null；一次供品资格与塑像坐标。',
'完整坐标类型才恢复blessed；缺任一坐标明确清location。资格在同维度濒死事件消费，阻止本次真死亡，非无条件Clone永久进度。',
'writer仅location非null写xyz，总写dimension；基类Clone默认!wasDead，真实死亡不自动复制。reader只检查三坐标INT，缺一置null；不检查dimension注册、目标塑像存在或仍激活。updateEffects的BLESSING每4worldtick查4格内非spectator且尚未绑定当前位置玩家，再查玩家2.5格已加载区块的SPIRIT_FRUIT供台；server随机1/40扣1供品并cap.setBlessed维度/塑像pos。onPlayerTick同维度持续给205tick blessed药效，不核当前塑像或距离。最高优先级death handler在同维度且location非null先取消事件并半血，归零经验并掉1/3经验；有一半概率寻找原位置附近有效出生点，阻塞只提示也不撤销救命，最后触发成就并clearBlessed。未检查保存坐标处现在仍是原塑像，故不能宣称源对象存活校验；清资格发生在副作用末尾，异常中断没有事务回滚证明。坐标清除后若writeToNBT复用旧compound不会主动remove xyz，但统一Clone/磁盘能力writer传新compound，因此不能把复用风险说成已证当前永不清除bug。',
'区分“跨磁盘保存的已支付一次资格”与“跨死亡永久历史”，并把来源坐标/维度、依赖有效性及消费边界明确审定。Clone白名单不应续复制已消费保护或临时药效；迁移时保持原设计，不把一次资格当无限永久权限。',
'上游经验损失/半血/复活机制是明确现有设计，本研究绝不引入Dynasty死亡惩罚或回血。主事件被取消后没有实际Clone不是永久复制成功证明。外部PlayerUtil.teleport、Potion原生持久化和事件取消顺序未展开，未运行游戏或验收救命行为。供台具体储物底层只用于定位供品，未另算实现。',
'塑像供品绑定、能力读写、持续效果、濒死消费合为1；支持坐标查询/出生点算法0额外信用。与Anthropophagy付费tether主题类似，但明确坐标维度限定、事件取消而非真实死亡后Clone，须Kepler最终判断是否独立，credit0。')

add('excluded-betweenlands-playerpersisted-respawn-routing-flag-is-not-permanent-history',
pick('handler/PlayerRespawnHandler.java','onPlayerDeath')+whole('handler/PlayerRespawnHandler.java'),
'死亡写PlayerPersisted标志，respawn读取决定路由。','thebetweenlands.respawn_in_bl与last portal坐标。','作为临时路由字段分类反例支持，不提交永久进度候选。',
'onPlayerDeath每次重新计算床是否有效/配置并写入原生PERSISTED_NBT_TAG，onRespawn读取或EndConquered决定是否传BL，必要时用lastPortal寻找出生点。标志没有在onRespawn显式清除，但下次死亡重算；并非功名/任务历史，不能因为放在PlayerPersisted就自动认为全部子键永远应复制。',
'为永久白名单按业务意图逐键评估，不把PlayerPersisted或ForgeData整根克隆当作已完成分类。',
'外部Teleporter实际迁移/原生Clone持久根规则未展开，未把路由当新版安全兼容实现。',
'排除临时死亡路由；出生点算法只是祝福支持，不新增信用。')
