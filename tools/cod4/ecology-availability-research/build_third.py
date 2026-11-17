"""Environment-gated natural selection; one mechanism, no parameter/species credit."""
import json
from evidence import CS, DOCS, dump, method as m, span, record, verify_records


def cs(name, signature, role):
    return m('cs',CS+name+'.java',signature,role)


r=record('EA-0008','cs','functional-native-spawner-data-preserves-native-failure-and-checks-offset-habitat',
    cs('mixin/MixinMobSpawning','private static void checkFunctionalSpawnerData(', '实际NaturalSpawner RETURN注入只做原返回值AND环境条件'),
    [span('cs',CS+'mixin/MixinMobSpawning.java',16,22,'完整注入descriptor与RETURN/cancellable注解'),
     cs('ColdSweat','public ColdSweat()', 'mod constructor注册biome serializer'),
     span('cs',CS+'core/init/BiomeCodecInit.java',13,20,'add_spawns codec完整注册字段'),
     cs('data/biome_modifier/AddSpawnsBiomeModifier','public void modify(', '实际CREATURE表去旧实体条目并装入带函数的数据'),
     cs('data/codec/util/FunctionalSpawnerData','public FunctionalSpawnerData(', 'SpawnerData携带predicate'),
     cs('data/codec/util/FunctionalSpawnerData','public boolean canSpawn(', '传递原生context和pos'),
     cs('data/codec/requirement/LocationRequirement','public boolean test(Level level, BlockPos origin)', '偏移后对实际结构piece/biome/dimension等检查'),
     cs('data/codec/util/NegatableList','public boolean test(Predicate<T> test)', '要求/排除的实际短路语义'),
     cs('data/codec/requirement/BlockRequirement','public boolean test(Level level, BlockPos pos, BlockState state)', '支撑/状态/NBT/block检查'),
     cs('data/codec/requirement/BlockRequirement','public boolean test(Level level, BlockPos pos)', '加载门及state读取'),
     cs('data/codec/requirement/BlockRequirement','public boolean test(BlockState state)', '块状态适配'),
     cs('data/codec/requirement/BlockRequirement','public boolean test(FluidState state)', '流体状态适配'),
     cs('data/codec/requirement/BlockRequirement','public <S extends StateHolder<?, S>> boolean test(', '完整StateRequirement比较'),
     cs('data/codec/requirement/FluidRequirement','public boolean test(Level pLevel, BlockPos pPos)', '流体读取加载门'),
     cs('data/codec/requirement/FluidRequirement','public boolean test(FluidState state)', '流体/源水/状态比较'),
     cs('data/codec/util/IntegerBounds','public boolean test(int value)', '坐标/光范围适配'),
     cs('data/codec/util/WorldTempBounds','public boolean test(double value)', '温度边界适配'),
     cs('util/world/WorldHelper','public static ServerLevel getServerLevel(', '结构查询绑定同dimension服务端世界'),
     cs('util/world/WorldHelper','public static double getRoughTemperatureAt(Level level, BlockPos pos)', '默认rough temperature读取'),
     cs('util/world/WorldHelper','public static double getRoughTemperatureAt(Level level, BlockPos pos, int flags)', '实际分段缓存/游戏时间时效，支持证据不另计'),
     span('cs',CS+'config/ConfigSettings.java',662,677,'实际ENTITY_SPAWN_BIOMES配置读取lambda，完整声明'),
     cs('data/codec/configuration/SpawnBiomeData','public static SpawnBiomeData fromToml(', '已有山羊/变色龙配置入口'),
     cs('data/codec/configuration/SpawnBiomeData','public NegatableList<LocationRequirement> location()', '配置location传递')],
    ['带函数的SpawnerData随biome ADD写入；NaturalSpawner.canSpawnMobAt返回时只在原boolean AND location上再筛。原返回false不会被翻成true，也不主动创造机会或增加cap。',
     'LocationRequirement先移动x/y/z offset，再检查范围、biome、dimension、结构getStructureWithPieceAt与INVALID_START、光/块/流体/温度；自定义predicate有值时直接返回并跳过其余条件。',
     '这里实际AddSpawnsBiomeModifier固定写CREATURE，虽然SpawnBiomeData另存category；不能仅看schema推断消费的是配置category。',
     '配置的要求/排除不是可凭名字推断的集合运算：NegatableList在requireAll且全部满足时直接返回true，后续exclusions未执行。'],
    ['生态观测应保留原生返回结果及独立环境条件，不能为使稀有生物出现反向覆盖原生失败。',
     '场景条件必须核对实际piece而非只有结构名；body检查用的偏移位置、加载状态与短路顺序需要完整证据。',
     '数据模型的字段不代表消费者实际使用，研究category/cap共存需追到写入出生表的位置。'],
    ['这是单条真实模组自然出生功能链；通用NegatableList/温度缓存只作支持，绝不单独计生态案例。',
     '未执行或验证Mixin启动配置、SRG映射和本整合包运行兼容；不把Java注入源码存在说成已生效。',
     'BlockRequirement/FluidRequirement在未加载坐标返回true；block replaceable仅检查Optional是否存在而未使用其布尔值；NBT条件但无BlockEntity可放行。不能称条件全部严格。',
     'rough temperature按8块segment缓存；默认flags=0可复用1000/(1+randomTickSpeed/20)游戏ticks，而非注释的固定10秒实时值。未审完全部温度modifier与NBT表达式，这些子系统不新增信用、不声称测量真值。',
     '位置dimension tag分支检查dimensionTypeRegistration与tag.location，不能概括为任意dimension tag完全符合预期。',
     '原生cap之前已经拒绝时本链无最终生成机会；它不是解决runtime04全局CREATURE关闭的已证方案。'],
    {'unit':'带环境函数的数据写表→原生consumer→位置检查整链仅1项',
     'different_from':['EA-0007: registry placement predicate；本项让每条SpawnerData绑定位置条件并在原生选择返回时只作AND','EA-0003: 本项用piece条件筛选原数据而非替换结构出生表'],
     'merged_zero_credit':['变色龙/山羊条目、温度/流体/光/结构字段、各范围或NBT表达式、通用缓存']})
previous=[]
for name in ['batch-001.json','batch-002.json']:
    previous.extend(json.loads((DOCS/name).read_text())['records'])
dump('batch-003.json',{'status':'SOURCE_REVIEWED_PROPOSED_NOT_ACCEPTED','target':1000,
    'reviewed_proposed_in_batch':1,'cumulative_reviewed_proposed':len(previous)+1,
    'accepted':0,'gate_met':False,'records':[r], 'cross_batch_integrity':verify_records(previous+[r])})
print('Packaged batch003:1 new; cumulative8 proposed,0accepted')
