player=pick('/mixin/MixinPlayer.java','onReadAdditionalSaveData onAddAdditionalSaveData getClimateClemencyGranted setClimateClemencyGranted')
add('toughasnails-climate-clemency-grant-history-selective-respawn-copy',
 pick('/mixin/MixinServerPlayer.java','onRestoreFrom')+player+whole('/mixin/MixinServerLevel.java')+pick('/temperature/TemperatureHandler.java','onPlayerTick removeHeatExhaustion tryAddHeatExhaustion')+pick('/config/TemperatureConfig.java','load'),
 '官方ToughAsNails5be2dc22f6747e29880398551d2624a897c0e862，branch1.21，MC1.21。Player原生NBT尾部保存一次领取标志；ServerPlayer.restoreFrom尾部按配置只复制已领资格，ServerLevel.addPlayer入口据此决定发放Climate Clemency效果。',
 '根climateClemencyGranted boolean缺省false，MixinPlayer新实例false。climateClemencyRespawning默认false，climateClemencyDuration默认6000；flag是历史已授予资格，效果本体和剩余时长属于别的对象。',
 'onRestoreFrom在!climateClemencyRespawning时把旧玩家flag值复制到新玩家，忽略native restoreFrom boolean参数（未区分死亡/返回末地）；配置true时不复制，目标新实例false允许重新发放。原NBT reader先温度→口渴→flag，前面异常会使flag赋值未执行；flag不校验类型，getBoolean缺省。',
 'onAddPlayer要求enableTemperature、duration>0、未领取且非creative；先setGranted(true)再addEffect，未检查addEffect返回成功，因此标志语义为尝试发放而非效果确认。温度tick在效果存在时把level设NEUTRAL，资格flag本身不持续免疫；宽限过后历史flag仍true。临时temperatureData/thirstData没有在该restoreFrom注入被复制，不能从这一个hook断言原生其他路径绝无迁移。',
 '可借鉴以显式永久历史字段白名单复制，防止死亡重复发首次奖励，并把领取历史与临时效果/剩余时长分离。Dynasty需审定功名/官阶/忠诚/任务标志的复制政策，对死亡/末地返回分别定义；不复制整份ForgeData、免疫、姿态、反击计时器，也不新增死亡惩罚。',
 '上游flag先提交且addEffect返回未查，不是两阶段事务；同实例缺键可把true改false，类型坏或reader前置异常没有隔离；未保留未知键原payload。原生restoreFrom与mixin实际生效、跨模组注入顺序未执行验证。资格名称含clemency不能当永久免疫许可。静态配置读完整，配置框架验证依赖未展开。',
 '永久已授予历史+配置选择性respawn copy合1。get/set、NBT、addPlayer发放、效果消费者、两种配置不拆计。与其他首次登录标志/Clone白名单实现广义相近，Kepler须比具体控制流；credit0。')
add('toughasnails-player-survival-stats-load-gates-disabled-normalization-and-runtime-consumption',
 pick('/temperature/TemperatureData.java','readAdditionalSaveData addAdditionalSaveData')+whole('/temperature/TemperatureData.java')+whole('/thirst/ThirstData.java')+
 pick('/mixin/MixinPlayer.java','onReadAdditionalSaveData onAddAdditionalSaveData onCauseFoodExhaustion onTick getTemperatureData getThirstData')+
 pick('/mixin/MixinServerPlayer.java','onDoTick onRestoreFrom')+whole('/temperature/TemperatureHandler.java')+pick('/thirst/ThirstHandler.java','onPlayerTick onChangeDimension syncThirst onItemUseFinish')+
 pick('/api/temperature/TemperatureHelper.java','getTemperatureData getTemperatureAtPos getPercentHyperthermic isFullyHyperthermic getTicksRequiredForHyperthermia getTicksHyperthermic')+whole('/temperature/TemperatureHelperImpl.java')+whole('/temperature/BuiltInTemperatureModifier.java')+whole('/api/temperature/TemperatureLevel.java')+whole('/api/thirst/ThirstHelper.java')+whole('/thirst/ThirstHelperImpl.java')+whole('/init/ModApi.java')+
 pick('/core/ToughAsNails.java','init addHandlers'),
 '同一Player原生NBT read/add尾部真实持久读取温度与口渴，两套近似read/write启用门闸合并1族；MixinPlayer.tick尾部真实服务端玩法消费，ServerPlayer.doTick同步派生显示缓存。',
 '温度根temperatureLevel/targetTemperatureLevel为enum ordinal，changeDelayTicks/hyperthermiaTicks/extremityDelayTicks/dryTicks；口渴thirstLevel/thirstTickTimer/thirstHydrationLevel/thirstExhaustionLevel。只以首键contains(type99 numeric)判断整组存在，其他键缺省0。新对象温度NEUTRAL/targetNEUTRAL，口渴20/hydration2。',
 'writer启用时写当前值，禁用时明确写neutral/20/hydration2及0计时，覆盖已有游戏状态。reader仅有首键时处理：启用温度直接TemperatureLevel.values()[ordinal]、无范围或异常保护，读target/change/hyper/extremity但漏读writer写的dryTicks；禁用分支设全部默认并dry0。口渴启用读全4字段但setters无clamp，禁用归默认。缺首键完全不触及现对象，通常新实例默认但同实例可能旧值残留。',
 '真实tick温度递减delay/累积干燥，按环境modifiers追目标，达到hyperthermia阈值140且40tick周期伤害；口渴按exhaustion阈值先耗hydration再thirst，thirst<=0累计80tick依难度伤害，和平模式可回补。lastTemperature/lastThirst/nearby thermoregulators用于同步或环境缓存，不在该NBT中；并不属于永久进度。onRestoreFrom仅climateflag，存盘保留并不等于死亡保留。',
 '借鉴区分缺整组、缺子字段、功能关闭三种恢复策略，并检查writer/reader字段对称性和enum边界；永久进度应白名单保留，临时生存/伤害计时与派生缓存应按其独立规则处理。Dynasty不能复制这些温度/口渴计时器到死亡后的进度迁移，也不能用禁用功能写默认的策略清除旧任务未知数据。',
 '无旧别名/版本标志/未知payloadstash，ordinal重排不兼容且越界会异常；disabled writer主动覆盖旧值不可逆，dryTicks缺读是静态可见不对称，不称已运行复现。原生food/exhaustion bridge、插件modifiers、网络调度、原生Player保存顺序未全展开，未测试任何伤害/重生。TemperatureHelperImpl全方法作为支持上下文，普通modifier/getter不独立计数。',
 '温度与口渴共享同式首键门闸/配置归一read-write，不按字段或近似对象拆成多项；完整消费者是该族支持。与ColdSweat/既有需求模组相近，应Kepler做语义去重。本族是实际玩家持久读取而非永久Clone方案，credit0。')
add('toughasnails-thermoregulator-persisted-fuel-budget-and-recomputed-spatial-influence',
 pick('/block/entity/ThermoregulatorBlockEntity.java','loadAdditional saveAdditional')+whole('/block/entity/ThermoregulatorBlockEntity.java')+
 pick('/block/ThermoregulatorBlock.java','newBlockEntity getTicker onRemove onPlace neighborChanged checkPoweredState')+whole('/temperature/AreaFill.java')+
 pick('/temperature/TemperatureHelperImpl.java','thermoregulatorModifier modifyTemperatureByThermoregulators')+
 pick('/temperature/TemperatureHandler.java','onPlayerTick')+pick('/init/ModBlockEntities.java','registerBlockEntities register'),
 '真实注册的THERMOREGULATOR BE原生loadAdditional/saveAdditional→服务端ticker消费已存燃料预算并恢复局部空间影响。机器库存/燃料真值与可再计算区域缓存一条链。',
 'CoolingTimeRemaining/HeatingTimeRemaining/FillTimer int，FilledBlocks列表由NbtUtils.writeBlockPos产生int-array，items两槽经带registry HolderLookup的ContainerHelper。root位置信息仅BlockPos，不带dimension，属于该BE所在世界。',
 'load super后重建两槽库存、loadAllItems并读计时无范围校验；重建filledBlocks但nbt.getList("FilledBlocks",TAG_COMPOUND)随后list.getIntArray(i)，与writer的BlockPos intarray列表类型不一致，可能丢整个缓存列表，需依原生getList类型语义确认。元素arr.length!=3跳过。writer写计时/缓存/库存，未见原未知NBT保存。',
 'ticker禁用时clear区域并关blockstate效果后return，不递减燃料；启用先递减正预算，耗尽且槽非空时给1600tick并shrink1；不同槽决定heating/cooling。每fillTimer%20==0通知20范围玩家、清cache后从出风口AreaFill半径16重算confined可通行空间；dirty仅changed时，因此逐tick预算递减不一定立即标dirty。实际playerModifier查附近BE.getEffectAtPos→冷热/中和影响温度；缓存丢失通常等下一fill周期重建，不能据此称无损恢复。',
 '可借鉴永久真值与可再计算派生空间cache分层，缓存旧格式坏时重算、库存与已付燃料预算独立保留。Dynasty任务/官阶不是空间cache，不能用重算或空列表覆盖真实永久资格；若旧ID损坏需保存原栈/Count/tag等，不直接照搬本例skip策略。',
 '原生ContainerHelper栈codec/未知物品fallback未展开，不能声称Count/components无损。FilledBlocks列表类型疑点只是静态不对称；getList外部源码不在本仓，未做运行复现。getEffectAtPos/AreaFill只是support；fuel校验入口在canPlaceItem，ticker对直接写入的非空槽不再验证tag；modifyTemperatureByThermoregulators强制castBE类型风险。ThermoregulatorBlock CODEC字段指WaterPurifierBlock构造器，静态可见另有接线疑点，不据此宣布运行正常。无旧ID/Player Clone。',
 '两槽冷热/三种effect/空间fill/getters/容器/跨loader合1，不能把1600tick项或NBT字段拆计。不同于普通炉子之处是持久燃料预算与按世界障碍可重算的空间影响；仍有通用BE/炉子类重叠风险，由Kepler决定保留/合并，credit0。')
