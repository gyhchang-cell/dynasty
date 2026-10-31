"""Package text-only colony-lifecycle reading; never import or execute upstream Java."""
from evidence import *
T=AM+'tileentity/TileEntityLeafcutterAnthill.java'
E=AM+'entity/EntityLeafcutterAnt.java'
B=AM+'block/BlockLeafcutterAnthill.java'
def m(path,sig,role): return method('am',path,sig,role)
def s(path,a,b,role): return span('am',path,a,b,role)
chain=[
 m(E,'protected void registerGoals()', '实际注册ReturnToHiveGoal，非未被调用的示意代码'),
 s(E,636,744,'完整ReturnToHiveGoal内部类：查找/继续/停止/开始/逐步靠近/真实tryEnterHive入口'),
 span('am',E,258,344,'完整实体tick；服务器递减stayOut计数并周期核验hive','complete_method'),
 m(E,'private boolean isHiveValid()', '缓存hive必须仍为实际anthill block entity'),
 m(E,'public boolean hasHive()', 'hive缓存存在性'),
 m(T,'public void tryEnterHive(EntityLeafcutterAnt p_226961_1_', '双参入巢委托真实三参入口'),
 m(T,'public void tryEnterHive(EntityLeafcutterAnt p_226962_1_', '活实体转队列、局域补充条件、DISCARDED原实体'),
 m(T,'private int getAntsInAreaCount(', '在巢队列和32格AABB活蚁共同计数，非全局cap'),
 m(T,'public boolean hasQueen()', '队列wrapper queen标记决定有无queen'),
 m(T,'public static void serverTick(', '实际服务端block entity ticker入口'),
 m(B,'public <T extends BlockEntity> BlockEntityTicker<T> getTicker(', '仅服务端且类型匹配的ticker绑定'),
 m(B,'public BlockEntity newBlockEntity(', 'block创建实际anthill block entity'),
 m(T,'public TileEntityLeafcutterAnthill(', '实际block entity type绑定'),
 m(T,'private boolean addAntToWorld(', '出口支撑判定/序列化重建/实际addFreshEntity布尔返回'),
 m(T,'public static Entity loadEntityAndExecute(', 'NBT重建consumer/乘客处理；出巢前已去Passengers'),
 m(T,'private static Optional<Entity> loadEntity(', '重建RuntimeException转empty，队列可保留'),
 m(T,'public static Optional<Entity> loadEntityUnchecked(', '创建已注册EntityLeafcutterAnt并load，非字符串ID猜测'),
 m(T,'public void load(CompoundTag nbt)', '恢复队列/timer/Queen wrapper'),
 m(T,'public ListTag getAnts()', '序列化队列去UUID但未写wrapper Queen'),
 m(T,'public void saveAdditional(', '实际保存队列及LeafFeedings'),
 m(T,'public void setChanged()', 'override只有被调用才检查火灾；入/出巢方法未显式调用'),
 m(T,'public boolean isNearFire()', '27块附近fire判断，仅支持setChanged边界'),
 m(T,'public void growFungus()', '入巢有叶时调用的完整fungus副作用'),
 m(T,'private boolean isUnfilledChamber(', 'fungus内部条件'),
 s(T,408,421,'完整Ant内部类：移除UUID，保存内部计时及queen字段'),
 m(E,'public void readAdditionalSaveData(', '实体内Queen/Leaf/倒计时/hive还原，与wrapper Queen分开'),
 m(E,'public void addAdditionalSaveData(', '实体内Queen仍会写入EntityData，不宣称蚁后身份整体消失'),
 m(E,'public boolean hasLeaf()', '叶状态实际entitydata读'),
 m(E,'public void setLeaf(boolean leaf)', '出巢清叶实际写'),
 m(E,'public boolean isQueen()', '实体Queen实际entitydata读'),
 m(E,'public void setQueen(boolean queen)', '实体load设置Queen及属性'),
 m(E,'public void setStayOutOfHiveCountdown(', '蚁后出巢后400tick禁止返回'),
 s(AM+'tileentity/AMTileEntityRegistry.java',14,16,'block entity DeferredRegister/type supplier'),
 s(AM+'block/AMBlockRegistry.java',32,33,'实际block和chamber字段'),
 m(AM+'block/AMBlockRegistry.java','public static RegistryObject<Block> registerBlockAndItem(String name, Supplier<Block> block){','注册委托'),
 m(AM+'block/AMBlockRegistry.java','public static RegistryObject<Block> registerBlockAndItem(String name, Supplier<Block> block, Item.Properties','真实block/item注册'),
 s(AM+'misc/AMPointOfInterestRegistry.java',16,22,'实际anthill POI字段及DeferredRegister'),
 m(AM+'misc/AMPointOfInterestRegistry.java','private static Set<BlockState> getBlockStates(', '实际方块状态绑定POI'),
 s(AM+'entity/AMEntityRegistry.java',89,89,'活蚁注册为CREATURE；不推断原生cap豁免'),
 m(AM+'AlexsMobs.java','public AlexsMobs()', 'mod bus实际注册entity/block/BE/POI'),
 s(AM+'config/AMConfig.java',230,232,'局域增殖和队列阈值默认值，只是支持不是独立机制')]
r=record('EA-0010','am','anthill-live-entity-to-stored-colony-and-commit-on-add-release',
 m(T,'private void tickAnts()', '有界遍历stored colony；超过最短占巢且非queen才出巢，只有实际add成功才移出'),chain,
 observation=[
 '实际registerGoals注册ReturnToHiveGoal：已有叶/queen且禁止返回计数到期，优先现存hive，否则每次查找受cooldown约束、POI半径100选最近；靠近且脚下正是hive才调用tryEnterHive。目标选择不检查容量，容量只在入巢判定，因此不保证满巢时必然换巢。',
 '入巢先检查ants.size<colonySize，保存实体NBT，必要时根据feedings、queen和在巢+32格AABB计数补一条空NBT新蚁，再把入巢实体加入队列并DISCARDED；这是活体转储存态，不是死亡或玩家击杀。补充与原蚁合入可能使队列超过阈值，不宣称硬人口上限。',
 '实际BlockLeafcutterAnthill.getTicker仅服务端/type匹配调用serverTick→tickAnts。每个队列项计时，ticksInHive严格大于minOccupationTicks且wrapper非queen才尝试出巢。阻塞出口或load失败/addFreshEntity=false均保留该项，下次tick再尝试；只有add成功iterator.remove。无全局尝试总次数或最终超时，不能称有限重试。',
 '出巢移除Passengers/Leash/UUID，创建已注册活蚁并load，叶标记清除，移动到巢顶；新UUID使巢前后不能用同UUID作为同一活体证据。声音/gameEvent先于实际add，故看到出巢反馈并不证明实际加入。',
 '保存/读回支持Ants/EntityData/占巢timer与LeafFeedings，但getAnts未保存load所读wrapper Queen。实体自身EntityData的Queen另有写回，故仅指出队列角色标记丢失，不能说queen实体必变worker。入巢、tick递增和成功出巢无显式setChanged，不能保证每次晚变更必落盘。'],
 application=[
 '后续生态证据应区分活实体、巢内保存种群和真正新出生；原实体DISCARDED及UUID重建不计死亡/击杀，声音/事件不替代实际加入结果。',
 '学习局部巢内+附近活体一起限量、阻塞时保留储存项与成功加入后提交移除的生命周期原则；不复制代码、不直接给本项目新增spawner或修改cap。'],
 limits=[
 '只认可已注册巢的玩法储存/释放机制；自然蚁丘configured/placed feature及biome modifier JSON缓存内容缺失，EA-C001的自然部署可达性交集仍未闭合、0信用。不从此项声称自然巢已在世界生成。',
 '未读取本版本NaturalSpawner计数调用链，不断言巢内NBT必然排除cap或释放必然绕过所有Forge事件；CREATURE注册仅事实。',
 '未验证运行期POI可达性/寻路活锁/容量公平性；vanilla导航、Forge addFreshEntity内部作为外部调用，不把实际加入返回推成同UUID长期存活。',
 '触火/踩踏/玩家喂食releaseQueens及anteater emergency支路不作为新案例或本项完整验收范围；fungus副作用完整方法作为支持不另计。',
 '固定Forge源码只作语义研究，未执行、编译或启动；wrapper Queen遗漏、无显式dirty、软容量边界均保留。'],
 dedup='与EA1天气直生、EA2独占栖息chunk、EA3结构表、EA4/5/6/9世界生成cohort、EA7/8谓词交集不同：此项是活体转巢内储存、逐tick延时重建且实际加入成功才提交移除。全部POI/AI/BE/NBT/局部增殖/注册支持合为1项；EA-C001重叠储存链由此覆盖，不可再以自然巢部署闭环把同一链重复计数。')
dump('batch-005.json',{'status':'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED','records':[r],
 'integrity':verify_records([r]),'credits_proposed':1,'credits_accepted':0,
 'candidate_overlap':{'EA-C001':'storage/release lifecycle covered here; natural worldgen deployment remains incomplete and zero credit; do not count same chain twice'},
 'no_game_compile_test_or_production_change':True})
dump('review-addenda-001.json',{'status':'LIMITS_ONLY_ZERO_EXTRA_CREDIT','batch_001_immutable':True,
 'EA-0001':{'receipt':'independent-reviews/coordinator-EA0001.json',
 'limits':['AMWorldData.get reads dataMap.get(overworld), writes dataMap.put(world); crossdimension cache reliability not inferred.','Retain load/save beachedCachalot key-case mismatch, null player true and ignored addFreshEntity result.'],
 'source':m(AM+'world/AMWorldData.java','public static AMWorldData get(', '完整方法证明key不对称')},
 'EA-0002':{'receipt':'independent-reviews/coordinator-EA0002.json',
 'limits':['tickPupfish/search directly mutate fields without explicit setDirty; initial get marking dirty does not prove every late mutation reaches disk. Serialization support only.','Retain restrict=false predicate restriction, unproven biome/cave intersection, wallclock/phase/crossdimension boundaries.'],
 'source':[m(AM+'world/AMWorldData.java','public void tickPupfish()', '直接field变更无显式dirty'),m(AM+'world/AMWorldData.java','private void searchForPupfishChunk()', '直接选chunk/attempt++无显式dirty')]},
 'EA-0003':{'receipt':'independent-reviews/coordinator-EA0003.json',
 'limits':['Conquest/piece/validator guards apply only MONSTER; non-MONSTER early return.','Empty table preserves original biome candidates.','Pinned newer NeoForge source is not direct Forge1.20.1 compatibility.','One table-selection mechanism, no actual generated-structure reachability credit.']}})
print('Packaged EA-0010: ONE proposed mechanism;',len(r['chain']),'supporting ranges, zero extra range credit')
