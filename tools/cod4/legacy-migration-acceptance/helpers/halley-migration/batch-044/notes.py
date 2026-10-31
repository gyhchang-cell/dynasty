add('sereneseasons-dimension-season-clock-saveddata-range-recovery-and-transient-sync-baseline',
 pick('/season/SeasonSavedData.java','load save')+whole('/season/SeasonHandler.java')+whole('/season/SeasonTime.java')+
 pick('/command/CommandSetSeason.java','register setSeason')+pick('/core/SereneSeasons.java','init addHandlers')+whole('/init/ModAPI.java')+whole('/api/season/SeasonHelper.java')+
 whole('/network/SyncSeasonCyclePacket.java')+whole('/season/SeasonHandlerClient.java')+
 pick('/init/ModFertility.java','populate isCrop isCropFertile populateSeasonCrops populateSeasonSeeds')+whole('/season/SeasonalCropGrowthHandler.java')+pick('/config/SeasonsConfig.java','load isDimensionWhitelisted'),
 '官方Glitchfiend/SereneSeasons固定61df18c2029d50e1294e7fc8d61824bbd6facb75，gradle.properties MC1.20.1。DimensionDataStorage.computeIfAbsent(SeasonSavedData::load,defaultSupplier,"seasons")真实世界存档读取；服务端START tick更新，世界季节用于作物肥力及生长/骨粉限制。',
 '唯一持久计数SeasonCycleTicks int；VERSION=0常量未写未读，不能称版本迁移。当前配置dayDuration*subSeasonDuration*12决定cycle，读取对值clamp到[0,cycle]，未记录旧周期配置/旧日长。缺数字键原生getInt缺省0；新文件supplier按startingSubSeason 0随机、1..12指定起始季节。',
 'save只把SeasonCycleTicks写传入NBT；load创建新对象而非保留未知payload。不存在数据文件走supplier并setDirty，存在文件缺键走load的0而非起始季节配置；负数夹0，超过周期夹到包含上界cycle（getSubSeason经模数表示首季，下次tick positiveModulo归一）。缩短周期不按原季节比例换算，进度会截断。',
 'onLevelTick只server START及白名单维度；先更新lastDayTimes基线，再检查doSeasonCycle和无在线玩家暂停，避免暂停时长累积。difference非0才取存档，(int)difference加现值并positiveModulo，setDirty；时间指令/睡觉跳时可能推进或回退周期，int窄化和乘法溢出未防护。lastDayTimes/updateTicks/prevServerSeasonCycleTicks均静态内存map，未持久、未读到卸载清理。sendSeasonUpdate首次用当前值初始化prev，不制造历史季节变化事件；实际作物通过SeasonHelper→SeasonHandler→SeasonTime读取恢复后的季节，非纯渲染样例。',
 '可借鉴把世界持久真值与同步/变更检测缓存分开，缺文件与缺字段采用不同而明确的恢复路径，并在载入边界校验数值范围。Dynasty永久任务需保留历史资格/未知键及原Count/tag，不能按季节本例用clamp截断任务进度；也不把世界计时器或静态cache加入Player Clone白名单。',
 '没有旧ID重映射或Player Clone，建议仅实际世界持久读取范围，Kepler可按范围排除。save接受原NBT不主动删除未知键，但load不存原NBT且新对象后续原生保存是否保留未知键未展开，不能保证未知payload存续。配置允许Integer.MAX_VALUE但duration乘法无checked overflow；原生SavedData读写原子性/GlitchCore事件与网络调度未展开，无运行验证。SyncSeasonCyclePacket.handle有packet.dimension==player当前维度检查，但未在本方法检查方向；不要推断已证明服务端拒绝伪造。客户端END tick即使服务端暂停仍推算，依赖更新矫正，不作权威进度。',
 'SavedData/save/load/tick/command/SeasonTime/fertility/packet为同一世界季节时钟链合1。四季/12子季/跨平台移植/配置键/事件消费者不拆信用。与其他世界时钟族有架构风险，需Kepler按对象与实际范围复核；本地credit0、accepted=false。')
