"""Text-only study of a gameplay population lifecycle, plus an incomplete placement lead."""
from evidence import *
B=MW+'server/entity/foliaath/EntityBabyFoliaath.java'
A=MW+'server/entity/foliaath/EntityFoliaath.java'
I=MW+'server/item/ItemFoliaathSeed.java'
def m(p,s,r):return method('mw',p,s,r)
def s(p,a,b,r):return span('mw',p,a,b,r)
chain=[m(I,'public InteractionResult useOn(', '真实种子物品输入入口；服务器权限与原clickedPos上方出生'),
 m(I,'public Entity spawnCreature(', 'MOB_SUMMONED finalize→checkSpawnRules→add，忽略add结果仍返回entity'),
 m(B,'public boolean checkSpawnRules(', '实际身体无液体/碰撞检查与grass/dirt/leaves下方支持'),
 m(B,'protected void registerGoals()', '实际eat animation goal注册'),
 m(B,'public List<ItemEntity> getMeatsNearby(', '真实0.4径ItemEntity+tag/foodProperties判定'),
 m(B,'private boolean arePlayersCarryingMeat(', '持肉玩家只影响activate，没有直接喂食信用'),
 m(B,'public void addAdditionalSaveData(', '只额外保存tickGrowth'),
 m(B,'public void readAdditionalSaveData(', '只额外恢复tickGrowth'),
 m(B,'public boolean requiresCustomPersistence()', '幼苗true；不等于任何移除原因免疫'),
 m(B,'protected void defineSynchedData(', 'growth0/infanttrue/hungryfalse/eatingempty实际初始态'),
 m(B,'public int getGrowth()', '状态读'),m(B,'public void setGrowth(', '状态写'),m(B,'public void incrementGrowth()', '实际成长+1'),
 m(B,'public boolean getInfant()', '幼态读'),m(B,'public void setInfant(', '幼态写'),
 m(B,'public boolean getHungry()', '饥饿读'),m(B,'public void setHungry(', '饥饿写'),
 m(B,'public void setEating(', '消耗后动画stack存储'),m(B,'public ItemStack getEating()', '客户端粒子stack读，不计实际输入'),
 m(A,'public EntityFoliaath(', '实际新成体构造，无幼苗全部数据转移'),
 m(A,'protected void defineSynchedData(', '成体CAN_DESPAWN默认true'),
 m(A,'public boolean requiresCustomPersistence()', '成体!CAN_DESPAWN决定个体持久性'),
 m(A,'public void setCanDespawn(', '成熟设false实际消费'),
 m(A,'public void addAdditionalSaveData(', 'canDespawn额外NBT写'),m(A,'public void readAdditionalSaveData(', 'canDespawn额外NBT读'),
 m(MW+'server/entity/MowzieEntity.java','public void checkDespawn()', '完整实际父清理顺序：EventHooks/Peaceful先于个体持久性距离分支'),
 m(MW+'server/entity/MowzieLLibraryEntity.java','public void tick()', '实际动画tick推进，外部AnimationHandler调用不执行'),
 m(MW+'server/entity/MowzieLLibraryEntity.java','public Animation getAnimation()', '实际动画状态读'),
 m(MW+'server/entity/MowzieLLibraryEntity.java','public void setAnimation(', '结束时重置animationTick'),
 s(MW+'server/ai/animation/AnimationBabyFoliaathEatAI.java',1,11,'完整实际goal薄包装，支持0'),
 m(MW+'server/ai/animation/SimpleAnimationAI.java','protected boolean test(', '动画身份决定goal匹配'),
 m(MW+'server/ai/animation/AnimationAI.java','public boolean canUse()', '实际AI开始匹配'),
 m(MW+'server/ai/animation/AnimationAI.java','public boolean canContinueToUse()', '实际按animation duration继续'),
 m(MW+'server/ai/animation/AnimationAI.java','public void stop()', '实际发NO_ANIMATION reset'),
 s(MW+'server/item/ItemHandler.java',35,35,'真实seed物品注册'),
 s(MW+'server/entity/EntityHandler.java',42,43,'两生命周期实体类型均MONSTER；非自然出生证明'),
 m(MW+'MMCommon.java','public MMCommon(', '真实modBus注册ItemHandler/EntityHandler')]
r=record('EA-0013','mw','planted-population-hunger-plateau-growth-and-persistent-adult-replacement',
 m(B,'public void tick()', '完整幼苗服务端喂食/20tick成长/三饥饿平台/2400替换实体生命周期'),chain,
 observation=[
 '真实ItemHandler seed注册和useOn→spawnCreature调用：客户端直接SUCCESS，服务器需mayUseItemAt，但实际坐标始终clickedPos上1而非relative(facing)；MOB_SUMMONED finalize后checkSpawnRules检验碰撞/无液体/grass,dirt,leaves，再调用addFreshEntity。忽略add结果仍返回entity，所以useOn可能消费种子而未入世，SUCCESS也不代表出生。',
 '完整幼苗tick仅在server hungry且NO_ANIMATION时扫描近处ItemEntity，肉tag并foodProperties非空才split1；有实际物品后incrementGrowth、hungry=false并动画反馈。玩家持肉只影响张口activate，不能替代真实掉落物消耗。',
 '服务端非hungry时每tickCount%20==0成长+1，growth<600设置infant并清hungry；growth恰好600/1200/1800设置hungry，使成长等待肉；growth恰好2400创建新成体、复制位置、setCanDespawn(false)、addFreshEntity，然后无条件discard幼苗。三个阈值和替换均用==，未证明跳过阈值/异常存档时具备自纠正。',
 '成熟替换没有finalizeSpawn/checkSpawnRules/出生成功结果保护；幼苗discard不等于死亡或击杀，成人是新entity，源码只复制位置和设置持久性，不保留幼苗UUID/名字等全部状态。不能凭幼苗消失或反馈证明成体已加入。',
 '幼苗额外NBT只写tickGrowth；hungry/infant/eating没有本类额外保存，靠tick相等平台条件/初始值重算，重载时细粒度相位与动画未证完全恢复。成体canDespawn序列化存在，其requiresCustomPersistence返回!flag。父checkDespawn先执行EventHooks及Peaceful条件，再决定距离分支是否跳过，非不死或全部原因不清理。'],
 application=[
 '生态证据应把可种植后备种群与NATURAL抽取分开，逐项记录真实食物消耗、时间平台、旧实体退出和新实体实际入世，不能以客户端动画或返回SUCCESS代替事实。',
 '借鉴成长阶段、饥饿门及成熟后保留玩家培育个体的生命周期划分；真正实施前须验证原子交接/状态继承/重载及cap计数，1000前不制作新繁殖或改类别。'],
 limits=[
 '这是实际模组玩家种植/喂食种群生命周期参考，不能证明野外出生、种子自然掉落来源、物品tag实际部署非空或生态缺口已解决。两类型MONSTER并不说明其count/周期可与CREATURE互换。',
 'AnimationHandler/LLibrary网络内部未全文审，goal配对/本地动画推进仅支持调用边界，不声称客户端渲染、精确进食时长运行成功。',
 '外部vanilla/NeoForge生存/加入/存档/cap消费未执行；持久性不是免疫PEACEFUL/event/伤害。未验证默认难度下EventHooks具体结果。',
 '源码是固定NeoForge版本，不直接推成本项目Forge API可编译。未执行下载代码/编译/游戏/测试，未研究建筑资产或生产改动。'],
 dedup='与EA10巢内保存同类实体延时重建不同，本项玩家种植后消耗掉落肉、离散生长饥饿平台、成熟替换不同entity type并改变个体持久性。与EA11临时trader同步寿命退出相反；与EA9结构生成固定cohort不同。成体持久性setter/序列化/动画包装全部支持0，不按种子/幼苗/成体/3平台拆项；未来其他同模板成长植物合并。')
dump('batch-008.json',{'status':'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED','records':[r],
 'proposed_credit':1,'accepted_credit':0,'integrity':verify_records([r]),'no_natural_birth_or_runtime_credit':True})
# Fully read algorithm, still zero credit without actual natural placement data binding.
L=TF+'world/components/structures/placements/LandmarkGridPlacement.java'
G=TF+'util/landmarks/LegacyLandmarkPlacements.java'
def tm(p,s,r):return method('tf',p,s,r)
c=record('EA-C005','tf','landmark-center-grid-and-seeded-variety-placement-awaiting-resource-binding',
 tm(L,'protected boolean isPlacementChunk(', '真实StructurePlacement覆写入口，但实际structure_set资源引用缺失'),
 [tm(L,'public LandmarkGridPlacement(', '实际codec构造参数'),
  tm(L,'public static LandmarkGridPlacement forceStructureForCenters()', '无landmark lock时仅格心筛选，不证明任何结构一定生成'),
  tm(L,'public StructurePlacementType<?> type()', '真实注册type返回'),
  span('tf',TF+'init/TFStructurePlacementTypes.java',14,22,'完整类型注册字段及registerPlacer，注册不等于datapack消费'),
  tm(G,'public static boolean chunkHasLandmarkCenter(', 'chunk与计算得到的格心所在chunk相等'),
  tm(G,'public static BlockPos getNearestCenterXZ(int chunkX, int chunkZ) {', '无高度重载委托'),
  tm(G,'public static BlockPos getNearestCenterXZ(int chunkX, int chunkZ, int height)', '完整坐标哈希格心/负坐标偏置'),
  tm(G,'public static ResourceKey<Structure> pickVarietyLandmark(', '区域指定lich/naga，其他使用overworld seed加权variety'),
  span('tf',G,35,46,'完整VARIETY_LANDMARKS初始化；表项/权重合一支持不拆信用'),
  tm(TF+'util/WorldUtil.java','public static long getOverworldSeed()', '直接要求当前server存在并取overworld seed；未使用传入placement state seed')],
 observation=['已全文阅读LandmarkGridPlacement、AvoidLandmarkGridPlacement、LegacyLandmarkPlacements及实际getOverworldSeed；当前选定Java缓存未找到自然structure_set构造或部署JSON实际引用landmark_grid，因此不计信用。',
 '候选算法先筛格心，再可选pickVarietyLandmark使用ResourceKey对象==匹配lock。getNearestCenterXZ哈希只依赖坐标，选种类另使用全局当前server的overworld seed，不是state seed；不能无条件推断离线或多世界隔离可用。',
 'variety方法特殊区域固定两lich/two naga位置，其他权重抽选；这只决定候选，不证明biome/有效start/piece/场景完整。'],
 application=['后续补固定实际structure_set资源绑定再评估整机制；将自然候选格、类型选择、biome/有效start的可达性分层。'],
 limits=['candidate0；不以codec注册、格心数量或模板/结构ID当独立案例。','与EA-C003装饰避让相关但边界不同，本项是结构候选格；共同helper即使将来闭合也不能重复计。','尚未审核本版本ResourceKey实例interning保证，因此对象==仅原代码事实，不宣称所有等价key稳定匹配。'],
 dedup='自然候选格+区域强制类型+加权variety整链至多1项，不分格心/seedhelper/多种结构。当前未闭合部署仍0。',status='candidate')
dump('candidates-003.json',{'status':'INCOMPLETE_ZERO_CREDIT','records':[c],'integrity':verify_records([c]),'proposed_credit':0,'accepted_credit':0})
review=json.loads((DOCS/'independent-reviews/coordinator-EA0009.json').read_text())
dump('review-addenda-003.json',{'status':'EA0009_INDEPENDENT_REVIEW_LIMITS_ZERO_EXTRA_CREDIT','id':'EA-0009',
 'receipt':'independent-reviews/coordinator-EA0009.json','receipt_sha256':sha((DOCS/'independent-reviews/coordinator-EA0009.json').read_bytes()),
 'observed_chain':review['observed_chain'],'limits':review['limits'],
 'explicit_boundary':'custom persistence only skips distance branch; EventHooks/PEACEFUL processed first. 5–9 targets != successful adds. No seeded/bbox guard is reentry risk only; datagen/template not deployed/read, zero building credit.',
 'source_support':m(MW+'server/entity/MowzieEntity.java','public void checkDespawn()', '完整父方法顺序证据'),
 'original_batches_unchanged':True,'additional_credit':0})
print('EA-0013 one proposal;',len(r['chain']),'ranges; EA-C005 incomplete zero credit')
