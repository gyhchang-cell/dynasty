"""Package manually read ecology methods and frozen local evidence; no upstream execution."""
import json
from collections import Counter, defaultdict
from evidence import AM, TF, ROOT, DOCS, dump, method as m, span, record, sha, verify_records


def am(name, signature, role):
    return m('am', AM+name+'.java', signature, role)


def tf(name, signature, role):
    return m('tf', TF+name+'.java', signature, role)


events = am('event/ServerEvents', 'public static void onServerTick(', '实际 Forge LevelTick 入口；未筛 phase/维度，完整方法保留')
data = 'world/AMWorldData'
whale = 'world/BeachedCachalotWhaleSpawner'
records = []
records.append(record('EA-0001', 'am', 'weather-clocked-beached-encounter-with-bounded-placement',
    am(whale, 'public void tick()', '雷暴时消耗 delay 并递增失败概率'),
    [events, am(whale, 'public BeachedCachalotWhaleSpawner(', '加载状态和首次初始化'),
     am(whale, 'private boolean attemptSpawnWhale()', '玩家/随机门与实际实体加入'),
     am(whale, 'private BlockPos func_221244_a(', '十次有界地表位置/biome 候选'),
     am(whale, 'private boolean func_226559_a_(', '2x3x2 支撑形状及流体空位'),
     am(data, 'public static AMWorldData get(', 'SavedData 来源与世界绑定'),
     am(data, 'public static AMWorldData load(', '读入键'),
     am(data, 'public CompoundTag save(', '写出键'),
     am('world/AMWorldRegistry', 'public static boolean testBiome(', 'biome 配置异常时拒绝'),
     span('am', AM+'config/AMConfig.java',226,235,'开关/间隔默认值，非独立实现'),
     span('am', AM+'entity/AMEntityRegistry.java',87,87,'实际实体类型 WATER_CREATURE 注册，非独立实现'),
     am('AlexsMobs', 'public AlexsMobs()', '实际事件及 registry 注册')],
    ['每到 timer 门且雷暴才消耗1200 delay，doMobSpawning 再筛机会；失败概率累加而不是只改普通 biome 权重。',
     '随机玩家、1/5 门、最多10处地表搜索、距离平方>225及无流体/支撑形状后，create/finalizeSpawn(SPAWNER)/addFreshEntity；不能称 vanilla NATURAL 出生。',
     '这是源码中真实玩法入口，不走本方法内的 vanilla global/local cap 检查。'],
    ['将稀有遭遇的机会时钟、天气等待、位置失败与实体实际加入分别记录，可解释等待窗口是否产生机会。',
     '生态可达性研究应区别普通出生与独立遭遇来源，不能把后者回填前者的 NATURAL 验收。'],
    ['不建议现在引入独立 spawner 或绕开 cap；1000门槛未满。',
     'attemptSpawnWhale 在没有玩家时返回true；addFreshEntity 返回值被忽略，所以方法true不严格等价出生成功。',
     'load 使用 BeachedCachalot...，save 使用 beachedCachalot...，键大小写不一致；不能称可靠跨重启持久化。',
     'onServerTick 未筛 Phase.END/Overworld，timer 在非雷暴也会减且可负；不能照抄1200为真实唯一服务端tick周期。',
     'UUID写入不构成该方法的在世唯一性检查；未证明适用 Dynasty 或当前整合包。Citadel匹配器不在本项新增信用中。'],
    {'unit':'整条鲸遭遇链仅1项', 'different_from':['EA-0002: 种子区块选择+普通出生predicate','EA-0003: 结构出生表替换'],
     'merged_zero_credit':['timer/delay/chance/UUID/accessor/biome helper/collision search/constructor/event registration']}))

pup = 'entity/EntityDevilsHolePupfish'
records.append(record('EA-0002', 'am', 'seeded-single-habitat-chunk-search-with-persisted-give-up',
    am(data, 'public void tickPupfish()', '十次计数节奏与有界墙钟放弃状态'),
    [events,
     am(data, 'private void searchForPupfishChunk()', 'seed+尝试号选坐标，读取噪声水柱'),
     am(data, 'public int getWaterHeight(', '噪声柱水体高度读取'),
     am(data, 'public boolean isInPupfishChunk(', '已选择区块的XZ闭区间'),
     am(data, 'public static AMWorldData get(', '实际世界数据入口'),
     am(data, 'public static AMWorldData load(', '位置/放弃标记读取'),
     am(data, 'public CompoundTag save(', '位置/放弃标记保存'),
     am(pup, 'public static boolean canPupfishSpawn(', '实际 placement predicate'),
     am(pup, 'private static boolean isPupfishChunk(', 'predicate读 SavedData'),
     am(pup, 'private static boolean isInCave(', '水柱上方不见天、低于海平面'),
     am(pup, 'public boolean checkSpawnRules(', '实例随机门'),
     am('entity/AMEntityRegistry', 'public static boolean rollSpawn(', 'SPAWNER例外及rolls解释'),
     span('am', AM+'entity/AMEntityRegistry.java',126,126,'WATER_AMBIENT实体类型'),
     span('am', AM+'entity/AMEntityRegistry.java',225,225,'IN_WATER placement实际绑定'),
     span('am', AM+'world/AMWorldRegistry.java',268,270,'biome出生表注入支持范围；全文件保留'),
     span('am', AM+'config/AMConfig.java',253,254,'restrict开关/搜索距离默认值')],
    ['NoiseBasedChunkGenerator下以level seed+尝试号抽XZ，水高度严格31<height<63时存唯一ChunkPos；每10次计数机会搜索，整数minutes>5后放弃。',
     'spawn predicate将已保存区块、水体和洞穴水柱相交；SPAWNER可绕过此predicate，其余正常出生仍须原生cap和后续事件。',
     'NoPupfishChunk随SavedData保存，耗时放弃可把后续启动也带入没有入口的状态。'],
    ['研究稀有生态的候选栖地是否确定存在，须检查选择算法、生成器兼容、搜索终止及存档状态，不能只看非空biome标签。',
     '把“栖地未选出/搜索已终止”和“cap先挡住”作为不同诊断状态，不进行更多随机挂机。'],
    ['wall clock不是游戏tick；LevelTick未筛phase/维度，不声称每10真实tick或6分钟精确时限。',
     'restrictPupfishSpawns只控制搜索，当前canPupfishSpawn未检查它；关开关不等价解除位置限制。',
     '选择器仅查噪声水高度，不证明选中区块同时有允许biome、合适洞顶、已加载或真实出生。',
     '搜索失败/特殊非噪声生成器与普通cap阻挡均需独立观测；不建议照搬永久放弃策略。',
     '本项聚焦真实predicate可达性，不将缓存缺失的Forge biome modifier JSON宣称已核验；注册注入片段是支持证据，不等于完整部署验收。'],
    {'unit':'搜索、存档、区块predicate及随机门合并1项', 'different_from':['EA-0001: 天气时钟直接生成实体'],
     'merged_zero_credit':['多个方法、一个物种的注入/placement/存档字段和搜索参数']}))

records.append(record('EA-0003', 'tf', 'structure-start-piece-index-and-conquest-spawn-table-selection',
    tf('events/EntityEvents', 'public static void gatherPotentialSpawns(', '有效start/组件索引/征服状态选择'),
    [tf('events/EntityEvents','private void setup()', '真实事件监听注册'),
     tf('events/EntityEvents','private void structureSpecialSpawns(', 'PotentialSpawns消费并替换出生表'),
     tf('events/EntityEvents','private static int getSpawnListIndexAt(', '包含位置的组件取最高索引'),
     tf('world/components/structures/util/ConfigurableSpawns','default WeightedList<MobSpawnSettings.SpawnerData> getSpawnableList(', '按category路由'),
     tf('world/components/structures/util/ConfigurableSpawns','default WeightedList<MobSpawnSettings.SpawnerData> getSpawnableMonsterList(', '标签索引查表'),
     tf('world/components/structures/util/ControlledSpawns','public WeightedList<MobSpawnSettings.SpawnerData> getForLabel(', '未定义索引返回空表'),
     tf('world/components/structures/util/ControlledSpawningStructure','public ControlledSpawningConfig getConfig()', '实例持有的结构配置')],
    ['通过实际StructureManager startsForStructure获取实现ControlledSpawns的start；无效start跳过。MONSTER再筛已征服、位置validator与包含坐标的piece索引。',
     '事件消费者只在收集到非空结构表时清除旧表并加新表；返回空表不会清空biome默认表。',
     '非MONSTER分支先返回分类表，不受后面的conquered/piece/validator条件控制；默认ConfigurableSpawns只映射AMBIENT/WATER_CREATURE。'],
    ['结构场景的可达性应核对真实start、piece和位置，再核对species表；空tag或仅名称相似不能替代该链。',
     '审查“禁用出生”需追踪消费者是否真的接受空结果；在证据里分开候选表和最终原生出生。'],
    ['固定来源是较新NeoForge/WeightedList API，不能声称可直接用于本项目Forge1.20.1。',
     '非MONSTER分支只有chunk所引用start和isValid筛选，不能夸称全部分类均做精确bbox检查。',
     '被征服返回空并不保证完全无怪，原biome表可能保留；多start先返回次序也是限制。',
     '本项不声称具体结构资源已自然生成、不绕开global/local cap；完整结构配置与征服保存链后续只能作为支持，不另包装成重复信用。'],
    {'unit':'事件入口、选择器、索引和空结果消费者共1项', 'different_from':['EA-0001: 天气独立spawner','EA-0002: 世界唯一栖地区块'],
     'merged_zero_credit':['每座暮色结构、每个出生表成员、monster/ambient/water分支和配置getter']}))

dump('batch-001.json', {'protocol':'PROTOCOL.md','status':'SOURCE_REVIEWED_PROPOSED_NOT_ACCEPTED',
    'target':1000,'reviewed_proposed':len(records),'accepted':0,'gate_met':False,
    'records':records,'integrity':verify_records(records)})

b = ROOT/'docs/cod4/audit-20261022/ecology-native-acceptance/inputs-01/runtime-04'
outcome = json.loads((b/'outcome.json').read_text())
frozen = []
for name, expected in outcome['evidence_sha256'].items():
    p = b/('native-gates/native-gates.jsonl' if name == 'native-gates.jsonl' else name)
    actual = sha(p.read_bytes())
    assert actual == expected, (p, actual, expected)
    frozen.append({'path':str(p.relative_to(ROOT)), 'sha256':actual, 'matches_outcome_receipt':True})
rows = [json.loads(s) for s in (b/'native-gates/native-gates.jsonl').read_text().splitlines() if s.strip()]
scopes = defaultdict(list)
for row in rows:
    if 'scope_id' in row: scopes[row['scope_id']].append(row)
returns = [r for r in rows if r['kind']=='actual_native_creature_category_return']
assert len(scopes)==283 and all(len(v)==3 for v in scopes.values())
assert len(returns)==283 and all(r['actual_category_return'] is False and r['local_evaluation_observed'] is False for r in returns)
periods = sorted({r['overworld_game_time'] for r in returns})
assert periods == outcome['native_periods']
static_paths = ['source-audit.json','static-creature-gaps/report.txt','static-creature-gaps/verification.json',
                'static-creature-gaps/source-manifest.json','static-creature-gaps/species-reachability.json',
                'static-creature-gaps/cap-snapshots.json','static-creature-gaps/lantern-oil-evidence.json']
staticbase = ROOT/'docs/cod4/audit-20261022/ecology-acceptance'
for name in static_paths:
    p=staticbase/name
    frozen.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),
                   'use':'baseline/support only; 0 reference credit'})
sourceaudit=json.loads((staticbase/'source-audit.json').read_text())
dump('baseline-001.json', {'status':'READ_ONLY_EXISTING_EVIDENCE_NO_NEW_ACCEPTANCE',
    'runtime_outcome':{'path':str((b/'outcome.json').relative_to(ROOT)),'sha256':sha((b/'outcome.json').read_bytes()),'record':outcome},
    'raw_gate_independent_read':{'rows':len(rows),'event_counts':dict(Counter(r['kind'] for r in rows)),
        'complete_scopes':len(scopes),'category_open':0,'category_closed':283,'local':'NOT_EVALUATED',
        'periods':periods,'creature_count_range':[min(r['native_count_read'] for r in returns),max(r['native_count_read'] for r in returns)],
        'actual_caps':sorted({r['computed_vanilla_cap'] for r in returns})},
    'structure_tags':sourceaudit['structure_tags'], 'known_gap':sourceaudit['known_gap'],
    'evidence':frozen,'research_credit':0,
    'boundaries':['24/30 births and9/10 materials unchanged','37death candidates !=37strictkills; strict0 != no actual death',
       'native save log observed and exit0; watchdog native_save_verified=false is retained',
       'six registered species static predicate intersection not proven empty; callback true != native birth',
       'no abandoned village/mortuary/ghost market acceptance inferred from battlefield aliases']})

dump('network-limit-001.json', {'operation':'one browser open of cached fixed official repo identity',
    'url':'https://github.com/AlexModGuy/AlexsMobs/tree/09755dade2cfbdf14839e026d3af446f9d3ff843',
    'result':'Failed to fetch restricted URL / Internal Error','retries':0,
    'action':'preserve local results; no network retry/fallback download; cached pinned Git-tree identities explicitly labelled',
    'unfetched_resources':['AM Forge modifier JSON and anthill configured/placed feature JSON'],
    'credit_from_failed_request':0})
print('Packaged batch001:',len(records),'reviewed proposed, accepted0; raw native283 closed, local not evaluated.')
