"""Natural structure population lifecycle, not architectural reference credit."""
import json
from evidence import MW,DOCS,dump,method as m,span,record,verify_records


def mw(name,sig,role):
    return m('mw',MW+name+'.java',sig,role)


p='server/world/feature/structure/'
g=p+'UmvuthanaGroveStructure'
pieces=p+'UmvuthanaGrovePieces'
minion='server/entity/umvuthana/EntityUmvuthanaMinion'
chain=[
    mw('datagen/StructureSetHandler','public static void bootstrap(', '自然random-spread set及村庄排除区'),
    mw('datagen/StructureHandler','public static void bootstrap(', '对应自然结构配置'),
    span('mw',MW+'datagen/RegistryDataGenerator.java',13,20,'两类bootstrap实际挂到RegistrySetBuilder'),
    mw('server/world/MobSpawnBiomeModifier','public void modify(', 'ADD阶段构建结构可用biome集合'),
    mw(p+'StructureTypeHandler','public static void addBiomeSpawns(', '结构配置biome实际消费'),
    mw(p+'MowzieStructure','public Optional<GenerationStub> findGenerationPoint(', '生成入口先检查位置再构建pieces'),
    mw(p+'MowzieStructure','public boolean checkLocation(GenerationContext context)', '实例配置适配'),
    mw(p+'MowzieStructure','protected boolean checkLocation(', 'biome、地表最低高度及水体门'),
    mw(g,'public UmvuthanaGroveStructure(', '结构实例绑定群落generation config与biome集合'),
    mw(g,'public void generatePieces(', '先拒绝水面中心；实际加入Firepit及有限其余piece'),
    mw(g,'private static BlockPos posToSurface(', '依照真实地表高度定位'),
    mw(g,'private static boolean startPlatform(', '平台构建适配'),
    mw(pieces,'public static StructurePiece addPlatform(', '可选平台/扩展碰撞排除'),
    mw(pieces,'public FirepitPiece(StructureTemplateManager manager, Rotation rotation, BlockPos pos)', '实际生成的Firepit子类'),
    mw(pieces,'public BlockPos findGround(', 'piece坐标变换后查MOTION_BLOCKING_NO_LEAVES'),
    mw(minion,'public SpawnGroupData finalizeSpawn(', '初始化交易状态并调用父初始化'),
    mw('server/entity/umvuthana/EntityUmvuthana','public SpawnGroupData finalizeSpawn(', '父初始化按原因配置武器/面具'),
    mw(minion,'public boolean requiresCustomPersistence()', '场景种群总是要求自定义持久化'),
    mw(minion,'public void addAdditionalSaveData(', 'HomePos/HomeDist及交易状态存档'),
    mw(minion,'public void readAdditionalSaveData(', '读取home并restrictTo恢复'),
    mw('server/entity/MowzieEntity','public void checkDespawn()', '持久化种群跳过距离despawn分支')]
r=record('EA-0009','mw','natural-structure-firepit-bounded-cohort-with-persistent-home-lifecycle',
    mw(pieces,'public void postProcess(WorldGenLevel worldIn,', 'Firepit后处理：有限重试、STRUCTURE初始化、实体加入和home限制'),chain,
    ['自然structure_set→结构biome/水体/高度门→generatePieces明确add FirepitPiece；其postProcess每次抽5–9目标，每个最多20位置重试。',
     '在旋转后的piece坐标上查地表，要求y>0、实例checkSpawnRules和无碰撞，才finalizeSpawn(STRUCTURE)、restrictTo(center,25)、addFreshEntity。',
     'Minion.requiresCustomPersistence恒true；自身home与交易状态序列化，MowzieEntity.checkDespawn只在非持久化时做距离移除。',
     '研究重点是结构群落的出生来源、数量预算、重试、定居/持久化生命周期，共有自然结构/栖地/生物三层，不能仅按生物数量或piece数量计参考。'],
    ['稀有定居者与普通自然池共存研究，应追溯实体来源、home存档、持久化语义和对应版本原生计数器，而非把已加载实体总数直接当cap数。',
     '一次性结构植入应有实际加入确认及重入边界证据；仅一次for循环上限不等于整个结构生命周期的一次性上限。',
     '普通NATURAL与STRUCTURE生成分开验收；本项目六种拒绝CHUNK_GENERATION，不能拿另一来源替代其实际自然出生。'],
    ['源码postProcess没有布尔seeded/UUID集合，也未以传入chunk bbox筛选每个植入位置；只能报告重入风险，不能在无运行证据下宣称已重复出生。',
     'addFreshEntity返回值忽略且随后break，所以5–9是目标/尝试上限，不是严格成功群落数。',
     '原生cap常排除requiresCustomPersistence，但本来源较新NeoForge；未核验该版本的全套计数修改，也不声称这是Dynasty可采用的cap修复。',
     '结构生成数据代码已读；模板NBT、打包资源与实际世界部署未核验。Firepit后处理本身不以marker存在为前提，但能否被实际执行仍需运行期证据。',
     '不研究/制作营地建筑设计、不下载或复制模型/贴图/模板；只复制Java文本于研究目录。',
     'generation config里avoidStructures参数在MowzieStructure.checkLocation体中未使用，不能把字段存在当额外避让已经实现。'],
    {'unit':'自然营地群落seed、home保存与持久化合并1项',
     'different_from':['EA-0005: feature内部随造地植入，未有structure piece后处理/home交易存档','EA-0007: 同仓库共用biome/placement predicate；该群落用专门STRUCTURE入口与持久化生命周期'],
     'merged_zero_credit':['每个minion、5–9数量、20重试、平台变体、所有模板piece、home字段、共用biome matcher']})
old=[]
for i in range(1,4):old.extend(json.loads((DOCS/f'batch-{i:03}.json').read_text())['records'])
dump('batch-004.json', {'status':'SOURCE_REVIEWED_PROPOSED_NOT_ACCEPTED','target':1000,
    'reviewed_proposed_in_batch':1,'cumulative_reviewed_proposed':len(old)+1,'accepted':0,'gate_met':False,
    'records':[r],'cross_batch_integrity':verify_records(old+[r])})
print('Packaged batch004:1 new; cumulative9 proposed,0accepted')
