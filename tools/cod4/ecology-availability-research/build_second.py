"""Second manually reviewed mechanism batch; source/text packaging only."""
from evidence import IAF, MW, DOCS, dump, method as m, span, record, verify_records
import json


def iaf(name, signature, role):
    return m('iaf', IAF+name+'.java', signature, role)


def mw(name, signature, role):
    return m('mw', MW+name+'.java', signature, role)


def worldgen_entry():
    return [
        iaf('IceAndFire','public IceAndFire()', 'Feature注册及配置注册事件入口'),
        iaf('IceAndFire','public static void onServerAboutToStart(', '启动时向实际biome注入feature'),
        iaf('IceAndFire','private static void reloadSources(', 'noise biome source补充处理'),
        iaf('world/IafWorldRegistry','public static void registerConfiguredFeatures()', 'configured/placed feature实际注册'),
        iaf('world/IafWorldRegistry','public static void addFeatures(', '条件biome注入与防重复generation settings集合'),
        iaf('world/IafWorldRegistry','private static boolean safelyTestBiome(', 'biome异常转false'),
        iaf('world/IafWorldRegistry','public static boolean isFarEnoughFromSpawn(', '世界出生点水平距离门'),
        span('iaf', IAF+'world/IafWorldRegistry.java',147,177,'实际具体Feature supplier绑定；支持字段范围，不拆信用'),
        span('iaf', IAF+'world/IafWorldRegistry.java',197,207,'表面/洞穴placed feature lambda及过滤器绑定')]


def danger():
    return [
        iaf('world/IafWorldRegistry','public static boolean isFarEnoughFromDangerousGen(final ServerLevelAccessor level, final BlockPos position, final String id) {', 'SURFACE默认分区'),
        iaf('world/IafWorldRegistry','public static boolean isFarEnoughFromDangerousGen(final ServerLevelAccessor level, final BlockPos position, final String id, final IafWorldData.FeatureType type)', '调用世界数据距离检查'),
        iaf('world/IafWorldData','public static IafWorldData get(', '实际维度storage绑定'),
        iaf('world/IafWorldData','public boolean check(final TypedFeature feature', 'typed feature适配'),
        iaf('world/IafWorldData','public boolean check(final FeatureType type', '检查并写回按类型记录的最近坐标'),
        iaf('world/IafWorldData','public IafWorldData load(', '距离记录读入'),
        iaf('world/IafWorldData','public @NotNull CompoundTag save(', '距离记录保存')]


records=[]
records.append(record('EA-0004','iaf','natural-hydra-habitat-feature-with-shared-dangerous-site-spacing',
    iaf('world/gen/WorldGenHydraCave','public boolean place(', '自然地表巢穴生成、真实栖地和实体创建'),
    worldgen_entry()+danger()+[
        iaf('world/gen/WorldGenHydraCave','private boolean isTouchingAir(', '巢内可用空间检查'),
        iaf('world/gen/WorldGenHydraCave','public IafWorldData.FeatureType getFeatureType()', 'SURFACE分区')],
    ['biome配置允许且generateHydraCaves启用时注入SURFACE_STRUCTURES，place再筛随机率、世界出生点距离和危险地点间距。',
     '四角下方空块早退后构筑自然巢穴，内部装饰/战利品写入后创建Hydra并限制活动半径；实际sink为worldIn.addFreshEntity。',
     '共享IafWorldData按FeatureType记录(id,pos)，这是场景争用/分区的真实实现；它是一个实现链，不能把每种危险生物拆开当共享间距机制的新信用。'],
    ['自然结构依赖需同时追踪biome注入、placement、地形门和实际entity加入；仅有场景名字或predicate阳性不足。',
     '研究结构互斥是否缩小可达空间时，记录距离状态写入时机以及失败尝试是否也修改它。'],
    ['固定源码用旧StructureFeature/Random等API，不是本项目Forge1.20.1已验证实现。',
     'check中canGenerate每轮被覆盖，返回值只代表最后遍历项，不能声称检查所有历史点均满足间距。',
     'check无论通过与否都会写入位置，后续四角地形失败也已消费记录；不是成功生成后才提交。',
     'LAST_GENERATED为static，虽get绑定当前维度storage，不能据此宣称隔离各世界/维度；load还向static列表append。',
     'addFreshEntity返回值忽略，place true不严格证明实体已加入；未以当前世界运行验证，不建议改本项目生成方式。'],
    {'unit':'Hydra栖地、地形门、共享间距和实体sink合并1项',
     'different_from':['EA-0001: 运行中天气时钟','EA-0002: 不建场景的唯一栖地区块','EA-0003: 已有结构内出生表'],
     'merged_zero_credit':['所有颜色/变种、getter、共享危险间距各调用者、装饰方块/战利品条目']}))

records.append(record('EA-0005','iaf','natural-island-support-column-and-clear-space-cohort-seeding',
    iaf('world/gen/WorldGenSirenIsland','public boolean place(', '逐层落底的小岛与空间可用时植入有限生物群'),
    worldgen_entry()+[
        iaf('world/gen/WorldGenSirenIsland','private int getRadius(', '岛层半径函数'),
        iaf('world/gen/WorldGenSirenIsland','private BlockState getStone(', '生成实际支撑块'),
        iaf('world/gen/WorldGenSirenIsland','private void spawnSiren(', '空间点上的实际实体sink'),
        iaf('world/gen/WorldGenSirenIsland','public IafWorldData.FeatureType getFeatureType()', '类声明为SURFACE，调用显式OCEAN')]+danger(),
    ['天然feature在随机门/出生点间距/OCEAN危险分区后，以非遮挡地形逐层向下生成支撑；实际Sirens仅在2x2上方空位且随机筛选成功时加入。',
     '每次生成先抽1–3个目标上限，在布置过程中限制实际spawn调用次数；生成返回true不保证循环产生任何合适空位或实体加入成功。',
     '与EA-0004的四角地面门/封闭巢穴单体不同，本项是向下寻支撑与可用小平台条件驱动的群落植入，不以物种ID差别计数。'],
    ['场景生态验收应分开“自然场景生成”和“场景内生物实际植入”，不能因结构存在就假定稀有目标必在。',
     '记录共享间距分区、实际空间筛选及群落上限；计数应在实体加入确认后，而不是尝试前。'],
    ['共享危险间距实现已在EA-0004审读，仅作支持，不额外计信用；同类其它岛模板不再计。',
     'sirens在spawn前递增且sink返回值忽略；1–3只是尝试上限，不是保证出生数量。',
     '主while到minBuildHeight，底部支撑while却到y>=0；这是一处高度边界限制，不能声称完整支持负高度世界。',
     'getRadius在layer>up分支不再用MAX_ISLAND_RADIUS上限；不能称所有层半径<=10。',
     '这里研究自然生成算法，不制作/复制小岛建筑，不计1000建筑参考、不改变任何资产。'],
    {'unit':'逐层落底/空位判断/群落seed合并1项',
     'different_from':['EA-0004: 实心地面四角门+巢穴单体；共享间距部分不重计'],
     'merged_zero_credit':['石材随机变体、外观、每只Siren、地形层数、相同配置注册链']}))

records.append(record('EA-0006','iaf','ocean-floor-offset-feature-entity-add-with-false-feature-return',
    iaf('world/feature/SpawnSeaSerpent','public boolean place(', '海底基准随机高度、水体门与实际实体sink'),
    worldgen_entry()+[iaf('entity/EntitySeaSerpent','public void onWorldSpawn(', '自然feature调用的初始化，变种不另计')],
    ['先从origin偏8,8查WORLD_SURFACE_WG，再从该位置又偏8,8查OCEAN_FLOOR_WG，随后在海底附近抽XZ与0–29的Y偏移，只有水体中才create/addFreshEntity。',
     '无论是否执行实体加入，Feature.place都返回false；不能把feature布置计数false反推没有自然实体副作用。',
     '这与搁浅鲸天气tick及Siren岛造地植入不同，是依赖双高度图/水下3D采样的无场景方块生成入口。'],
    ['自然生态证据要在实际实体加入点确认UUID/provenance；feature返回值、回调计数或结构成功数量不足以代替。',
     '水生位置研究必须展开全部坐标变换和高度图基准，不能把名为ocean的biome直接当作最终水位满足。'],
    ['不将onWorldSpawn的7颜色/ancient分支另计；同样random->spawn的其它species模板不计。',
     'onWorldSpawn只是该feature初始化，代码没有finalizeSpawn(NATURAL)，不冒称本项目原生NATURAL回执。',
     'addFreshEntity返回忽略，false Feature return与出生有无均需独立证据；未推断实际异常或当前世界必有此怪。',
     '同一feature在新生成区块才有机会，与运行中满CREATURE cap的诊断不是同一个分母，不建议为验收搬用此路。'],
    {'unit':'海底采样到实体sink与返回语义合并1项',
     'different_from':['EA-0001: 雷暴时钟+地表10次搜索','EA-0005: 新建自然岛屿空间植入'],
     'merged_zero_credit':['蛇变种、属性、概率数字和共享registry/helper方法']}))

handler='server/world/spawn/SpawnHandler'
records.append(record('EA-0007','mw','shared-natural-spawn-intersection-of-biome-dimension-sky-substrate-and-structure-set',
    mw('server/entity/MowzieEntity','public static boolean spawnPredicate(', '真实注册的共有spawn predicate完整条件链'),
    [mw('MMCommon','public MMCommon(', '模块/placement listener注册入口'),
     mw(handler,'public static void registerSpawnPlacementTypes(', '所有实际绑定共享predicate，合并计数'),
     mw('server/world/MobSpawnBiomeModifier','public void modify(', 'ADD阶段消费biome helper'),
     mw('server/world/MobSpawnBiomeModifier','public static MapCodec<MobSpawnBiomeModifier> makeCodec()', '实际serializer codec'),
     mw(handler,'public static void addBiomeSpawns(', '正权重/biome筛选后注入类别表'),
     mw(handler,'private static void registerEntityWorldSpawn(', 'SpawnerData实际写入'),
     mw('server/world/BiomeChecker','public BiomeChecker(', '解析tag/名单数据'),
     mw('server/world/BiomeChecker','public boolean isBiomeInConfig(', '白名单先于黑名单，组合OR'),
     mw('server/world/BiomeChecker','private BiomeCombo(', '单个组合解析'),
     mw('server/world/BiomeChecker','private boolean acceptsBiome(', '组合内tag/ID的AND及否定'),
     mw('server/entity/MowzieEntity','private static boolean isBlockTagAllowed(', '地块tag匹配'),
     mw('server/config/ConfigHandler','SpawnConfig(final ModConfigSpec.Builder builder,', '可配置范围和默认维度'),
     span('mw',MW+handler+'.java',33,50,'MM_SPAWN完整lambda：下方支撑/禁止基岩屏障与身体两块空位', 'complete_initializer'),
     span('mw',MW+handler+'.java',52,60,'entity到SpawnConfig实际表'),
     span('mw',MW+'server/world/BiomeModifiersHandler.java',10,14,'serializer注册支持字段')],
    ['同一共有predicate供多个真实模组生物使用，按一种机制计：额外随机、维度、上下高度、暗度、地块ID或tag、见天/不见天、避开structure_set相交。',
     'biome名单是白名单先判true、然后黑名单、再各组合OR；组合内条件AND。placement另要求下面可运动阻挡且身体/头部符合原生空位。',
     '出生表中Lantern用AMBIENT，其他多为MONSTER；配置spawnRate是选种权重而非额外随机概率，extraRarity另在predicate消费。'],
    ['静态可达性要展开跨层AND/OR与优先级，尤其矛盾的见天/不见天、地块tag和结构排除；不能按每行参数或每个物种声称独立参考。',
     '区分注册类别/自然表/placement/额外rarity，记录原生global/local是否先到达；研究类别策略并不授权更改本项目category。'],
    ['源码仅检查ServerLevelAccessor后，稍后无条件cast ServerLevel；WorldGenRegion路径可能失败，不能称它覆盖所有生成原因都安全。',
     'dimension检查只在world instanceof ServerLevel且非SPAWNER时执行；不把predicate概括成所有路径严格维度绑定。',
     'invalid/missing avoid structure_set跳过；这是候选placement范围，不是已生成valid start或精确bbox验证。',
     '额外rarity用rand.nextDouble()>值，0值的注释与极端随机等0的严格比较有差别，不写成数学上绝无成功。',
     '本地cache未含生成的biome modifier JSON，已核验Java入口/codec链，不声称本轮验证安装后资源或自然出生。NeoForge API与本项目不同。'],
    {'unit':'共用生态predicate、biome注入和placement合并1项',
     'different_from':['EA-0002: 世界唯一栖地区块而非多条件可配置predicate','EA-0003: 有效start/组件替换表；这里用候选structure_set避让'],
     'merged_zero_credit':['7个物种、名单成员、tag组合数、参数行、共享函数与客户端外观']}))

previous=json.loads((DOCS/'batch-001.json').read_text())['records']
integrity=verify_records(previous+records)
dump('batch-002.json', {'status':'SOURCE_REVIEWED_PROPOSED_NOT_ACCEPTED','target':1000,
    'reviewed_proposed_in_batch':len(records),'cumulative_reviewed_proposed':len(previous+records),
    'accepted':0,'gate_met':False,'records':records,'cross_batch_integrity':integrity})
print('Packaged batch002:',len(records),'new; cumulative',len(previous+records),'proposed,0accepted')
