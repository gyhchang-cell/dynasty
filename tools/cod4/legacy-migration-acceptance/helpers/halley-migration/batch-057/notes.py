# -*- coding: utf-8 -*-
mob=pick('item/misc/ItemMob.java','capture hasEntityData getEntityData setEntityData createCapturedEntity createCapturedEntityFromNBT onItemUse spawnCapturedEntity')
trim=whole('tile/TileEntityFishTrimmingTable.java')+whole('inventory/container/ContainerFishTrimmingTable.java')+pick('network/serverbound/MessageButcherFish.java','process')
add('betweenlands-legacy-crab-missing-trim-payload-backfill-and-actual-butchery',
pick('entity/mobs/EntitySiltCrab.java','readEntityFromNBT')+pick('entity/mobs/EntitySiltCrab.java','writeEntityToNBT entityInit onInitialSpawn randomizeSiltCrabProperties getPartFromLootTable setItem1 setItem2 setItem3 getItem1 getItem2 getItem3')+pick('entity/mobs/EntityBubblerCrab.java','randomizeSiltCrabProperties')+mob+trim,
'旧SiltCrab/BubblerCrab实体NBT被世界或捕获物品createCapturedEntity读取，三个旧产物字段全无时服务端补抽；真实拆解台C2S chop恢复实体产物并落到物理输出槽。',
'item1/item2/item3各完整ItemStack compound；旧格式三个tag都null；当前loot table RNG；捕获物品Entity compound以及拆解台Items列表。',
'当前格式保存已经确定的三项可拆解产物；明确旧无字段时随机回填。Silt/Bubbler仅换表/同继承链合1，不是每槽或物种一个实现。',
'readEntityFromNBT先super，对每个实际NBTBase仅instanceof NBTTagCompound才new ItemStack，否则EMPTY；随后仅当服务端且三个原始tag都==null才randomize。因此一个合法字段+两缺失、一个错型字段+两缺失、三个空compound都不触发旧回填；不把缺失/空/错型混同。writer总是写三个compound，故world对象重存后有字段的空槽也不再补抽。randomize用真实loot table三个getPartFromLootTable调用，WorldServer生成列表仅取第一项，空表/空列表EMPTY；每项不是新的迁移信用。Bubbler override只换三个表，为同族。真正消费getSlotResult按输入item识别，getInputEntity每次通过ItemMob.createCapturedEntity从Entity NBT创建新对象，再读对应Item1/2/3；chop循环1..4逐槽调用，最后清源slot0/磨损斧。包装createCapturedEntityFromNBT设置新UUID/位置/速度但未把解码补出的字段写回原捕获item；据可见链，旧捕获载荷每次重建可再次进入随机补抽、各输出槽也可来自不同临时解码，不能称旧物品已幂等升级。正常新captured item maxStackSize1保留entity完整writeToNBTOptional；maxStackSize>1路径只保id，不宣称泛化全部生物物品完整payload。MessageButcherFish仅确认当前openContainer类型调用chop；Container.canInteractWith距离/同tile有独立方法但此process未显式调用，权限框架外部未展开。',
'旧任务物品缺字段升级应先明确全缺/部分缺/错型优先级；需把一次补得的永久产物/奖励写回唯一新格式，避免每次只读重建又随机补发。区分“对实体保存幂等”和“对捕获载荷保存幂等”，迁移不能只跑read而不落地目标。',
'原生EntityList/ItemStack内部没有逐行研究或运行，故动态RNG和源NBT是否被native隐式改写不作已复现保证；结论限定可见模组包装无显式writeback。未审loot资源表具体取值，也不把三个表/三个输出/两个crab当数量。真实产物被读到chop物理槽而非纯纹理变体。',
'同一旧crab载荷回填+捕获解码+拆解消费者合1。与056蟹笼区域捕获预算及053旧critter registry改名是不同数据转换对象，ItemMob/拆解台支持重用0；若Kepler已有同回填链应去重，不自动接受。')

add('betweenlands-captured-anadia-durable-freshness-nested-reward-and-smoking-state-conversion',
pick('entity/mobs/EntityAnadia.java','readEntityFromNBT')+pick('entity/mobs/EntityAnadia.java','writeEntityToNBT entityInit setFishSize getFishSize setHeadType setBodyType setTailType setFishColour getFishColour setHeadItem setBodyItem setTailItem getHeadItem getBodyItem getTailItem setIsTreasureFish setTreasureUnlocked getTreasureUnlocked getHeadType getBodyType getTailType getHealthMods getSpeedMods getStrengthMods getStaminaMods get')+whole('item/misc/ItemMobAnadia.java')+mob+pick('item/tools/ItemNet.java','register itemInteractionForEntity')+pick('registries/RecipeRegistry.java','registerSmokingRackRecipes checkAndConvertNBTStack')+whole('recipe/misc/SmokingRackRecipe.java')+pick('tile/TileEntitySmokingRack.java','update canSmokeSlots updateCuringModifier updateFuelState consumeFuel smokeItem readFromNBT writeToNBT loadFromNbt saveToNbt')+trim,
'玩家网捕获Anadia写完整Entity并标绝对过期世界tick；存档/物品读取还原体型、部位产物和宝物标志；物品tick过期、放生、真实拆解、熏制依据嵌套载荷分支。',
'Entity内head/body/tail type与ItemStack、fishSize、fishColour、isTreasureFish/isTreasureUnlocked；物品专有rottingTime LONG；世界totalTime；熏架Items及各进度。',
'捕获鱼的具体嵌套产物/永久形态和绝对保鲜期限被携带；熏制复制外层stack后改嵌套活性及生肉产物，不是仅换色外观，仍同鱼载荷链1建议。',
'Entity reader缺byte为0进enum.get，越界（含负）映射UNKNOWN，未提供旧ordinal别名；fishSize缺float为0，setter无有限/非负钳制且更新size/移动速度/最大生命再setHealth(max)，所以不是无副作用解码；上游行为只观察不用于本项目回血。三个产物仅compound new ItemStack否则EMPTY，未如旧crab补抽，treasure布尔直接恢复，未保存钓鱼短时stamina/escape计数。网捕获要求EntityAnadia nettableTimer>0（静态注册已读）；先capture/移除实体/生成物品，再onCapturedByPlayer设置Entity.rottingTime=current+24000。isRotten只在fishColour!=0且有rottingTime时比较绝对世界tick，缺deadline视未腐坏、错型hasKey存在会getLong默认0；onUpdate到期把非0非1 colour变1，server给玩家smell，但该timer不纳入Clone永久白名单。重建实体只读EntityAnadia已知字段，rottingTime不是entity writer字段，放生再捕获会由callback重新给期限，不能把物品专有未知key认为经实体roundtrip必保留。真实拆解按deadline决定产物或ANADIA_REMAINS；熏制前canSmokeSlots拒0已熏或1腐鱼。注册配方output=stack.copy，修改fishColour0；三个嵌套raw meat通过checkAndConvertNBTStack变新smoked stack并保Count，未复制该子栈Damage/tag/能力；非raw保持旧stack。外层其余payload保留，rottingTime未删除但colour0使其不生效。smokeItem输出copy并扣源一件；同一嵌套payload类型转换与持久消费者合1。',
'迁移旧任务册或子容器时要分别列出外层Count/tag与嵌套ItemStack保留规则，不用“copy外层”暗示内层无损。依赖世界时间的到期键应有缺值/错型与换世界语义；纯reader调用setter可能改生命等行为，Clone白名单恢复应避免连带状态改变。',
'这是有真实物品产出/保鲜/禁止放生意义的状态，不因字段名colour就当视觉例；也不把各部位或枚举值独立计数。未运行捕获/熏架/腐坏，native ItemStack.copy及NBT未展开；钓鱼全部AI不在审阅范围。宝物flag仅此载荷观察，不声称未读宝物领奖链已安全一次消费。上游生命/负面气味/食物损耗不实施到本项目。',
'同一captured Anadia载荷读写、deadline和nested smoking conversion合1，ItemMob与拆解台跨057两项支持重复0；与蟹旧格式回填不同在绝对期限及嵌套子栈替换，但最后需Kepler审同对象/同链范围，不能据方法数量自动计数。')

add('excluded-betweenlands-last-killed-capability-only-audio-imitation-consumer',
whole('capability/lastkilled/LastKilledCapability.java')+pick('capability/base/EntityCapability.java','isPersistent clonePersistentData')+pick('tile/TileEntitySimulacrum.java','playImitationSound'),
'击杀事件写玩家lastKilled registry key；cap保存/跟踪，Simulacrum客户端读后播放模仿声音。','lastKilled STRING或缺失null。','完整持久与消费者已找到，但当前相关消费是环境音效，排除0，不包装永久任务历史。',
'onLivingDeath取EntityDamageSource.trueSource并写被杀实体registry key，reader需STRING否则clear null，未知有效格式ID未核registry；基类!wasDead才Clone，这个类未override，死亡不保留。playImitationSound近16格临时create实体后反射声音/playSound/setDead，没有任务奖励/解锁/持久物品。故有kill+Clone+NBT也不足以作为本任务永久进度参考。nextInt20使r<=19覆盖剩余分支、death sound分支不可达仅旁证不计实现。',
'用具体玩法消费者区分永久进度与氛围缓存，不把所有序列化玩家cap都加白名单。','未运行反射/客户端音频，也不启动图形；代码只作为排除证据。','音频状态1排除0；不拆reader、tracking、Clone、sound调用计数量。')

add('excluded-betweenlands-inventory-legacy-support-heading-is-live-inventory-api',
pick('tile/TileEntityGrubHub.java','getInventoryStackLimit getSlotsForFace canInsertItem canExtractItem removeStackFromSlot isItemValidForSlot readFromNBT writeToNBT')+pick('tile/TileEntityWaterFilter.java','getInventoryStackLimit getSlotsForFace canInsertItem canExtractItem removeStackFromSlot isItemValidForSlot readFromNBT writeToNBT'),
'检索到INVENTORY LEGACY SUPPORT注释；全文读两类确认含义。','side/slot/ItemStack实时库存接口。','该注释不是旧档格式迁移，不把标题或两个同构接口块当候选。',
'注释下方法仅枚举各面槽/插拔/有效物品判定，removeStackFromSlot固定EMPTY；没有NBT旧键/版本转换。两类真实NBT读写则super库存+tank，另有各自生产行为，但本项未以该标题声称已审独立旧格式升级。','关键词仅定位，结合完整方法和持久输入才能判迁移。','两类生产流虽已全文阅读，这里只交接口标题排除；未将tank通用支持加为新建议。','两个近似库存API块合1排除，字段名/机器名不能重复凑数。')
