"""Read-only source-evidence packaging; never execute upstream code."""
from evidence import *
W=MW+'server/world/feature/structure/'
D=MW+'datagen/'
C=MW+'server/config/ConfigHandler.java'
def m(p,s,r):return method('mw',p,s,r)
def s(p,a,b,r):return span('mw',p,a,b,r)
P=W+'WroughtnautChamberPieces.java'
_,plines=source('mw',P)
chain=[
 m(W+'WroughtnautChamberStructure.java','public WroughtnautChamberStructure(', '实际配置绑定，父类高度和避水关闭'),
 m(W+'WroughtnautChamberStructure.java','public void generatePieces(', '实际chunk中点/海床高度→有界搜索→旋转偏移→piece添加'),
 m(W+'WroughtnautChamberStructure.java','public GenerationStep.Decoration step()', '类声明地下步骤；与settings实际指定须区分'),
 m(W+'WroughtnautChamberStructure.java','public StructureType<?> type()', '实际结构codec type返回'),
 m(W+'MowzieStructure.java','public MowzieStructure(Structure.StructureSettings settings, ConfigHandler.GenerationConfig config, Set<Holder<Biome>> allowedBiomes, boolean doCheckHeight,', '完整父构造绑定配置/biome集合/三个flags'),
 m(W+'MowzieStructure.java','public Optional<GenerationStub> findGenerationPoint(', '真实自然Structure生成入口，检验后生成stub'),
 m(W+'MowzieStructure.java','public boolean checkLocation(GenerationContext context)', '父入口委托'),
 m(W+'MowzieStructure.java','protected boolean checkLocation(', '完整父级biome/enable/height/water守卫；avoidStructures参数未消费'),
 m(P,'public static void start(', '实际addPiece，不依据模板名推断实体'),
 s(P,1,len(plines),'完整模板Piece类/读写Rot/placement settings；handleDataMarker为空'),
 m(D+'StructureHandler.java','public static void bootstrap(', 'datagen实际构造WroughtnautChamberStructure'),
 m(D+'StructureHandler.java','private static Structure.StructureSettings structure(TagKey<Biome> biomeTag, Map<', '实际结构settings参数路径'),
 m(D+'StructureHandler.java','private static Structure.StructureSettings structure(TagKey<Biome> biomeTag, TerrainAdjustment', '实际settings使用SURFACE_STRUCTURES，不把子类step当最终部署证据'),
 m(D+'StructureHandler.java','private static HolderSet<Biome> biomes(', '实际结构settings biome tag引用'),
 m(D+'StructureSetHandler.java','public static void bootstrap(', '实际RandomSpread15/5 triangular+salt，无村庄exclusion应用于wrought'),
 s(D+'RegistryDataGenerator.java',13,16,'BUILDER将structure及structure_set bootstrap绑定'),
 m(D+'RegistryDataGenerator.java','public RegistryDataGenerator(', '实际DatapackBuiltinEntriesProvider'),
 m(D+'DataGenerators.java','public static void gatherData(', '实际datagen事件注册provider'),
 s(D+'DataGenerators.java',13,16,'实际mod事件subscriber注解，非运行过datagen声明'),
 m(D+'MMBiomeTags.java','protected void addTags(', 'HAS_MOWZIE_STRUCTURE纳入IS_OVERWORLD tag的生成代码，不等同已部署非空JSON'),
 m(W+'StructureTypeHandler.java','public static void addBiomeSpawns(', '配置匹配通过ADD填充FERROUS_WROUGHTNAUT_BIOMES集合'),
 m(MW+'server/world/MobSpawnBiomeModifier.java','public void modify(', 'ADD时实际调用结构biome集合填充'),
 m(MW+'server/world/MobSpawnBiomeModifier.java','public static MapCodec<MobSpawnBiomeModifier> makeCodec()', '实际modifier codec factory'),
 s(W+'StructureTypeHandler.java',20,24,'结构type和template piece type实际字段'),
 m(W+'StructureTypeHandler.java','private static <T extends Structure> DeferredHolder<StructureType<?>, StructureType<T>> registerStructureType(', 'type实际DeferredRegister'),
 m(W+'StructureTypeHandler.java','private static DeferredHolder<StructurePieceType, StructurePieceType> registerStructurePieceType(', 'piece实际DeferredRegister'),
 m(MW+'MMCommon.java','public MMCommon(', '实际modBus注册structure type/piece和biome codec'),
 m(MW+'server/world/BiomeChecker.java','public BiomeChecker(', '实际config编译'),
 m(MW+'server/world/BiomeChecker.java','public boolean isBiomeInConfig(', '完整biome条件调用'),
 m(MW+'server/world/BiomeChecker.java','private BiomeCombo(', '实际组合编译，非法或空可变成null'),
 m(MW+'server/world/BiomeChecker.java','private boolean acceptsBiome(', '组合内部null跳过，非任意配置fail-safe'),
 m(C,'GenerationConfig(final ModConfigSpec.Builder builder,', '完整世代配置，距离注释已弃用但负值仍作enable gate'),
 s(C,357,364,'Wroughtnaut实际配置高度20..50、biome列表和距离默认字段；参数不独立计数')]
r=record('EA-0012','mw','natural-underground-chamber-bounded-noise-column-floor-wall-orientation-search',
 m(W+'WroughtnautChamberStructure.java','public static Pair<BlockPos, Rotation> tryWroughtChamber(', '完整自然洞室地形判定核心：64列、上下高度、有地板才沿四向检验4高墙并返回旋转'),
 chain,
 observation=[
 'datagen StructureSetHandler将wrought chamber绑定RandomSpread15/5 TRIANGULAR/salt23217347；StructureHandler使用实际tag/settings构造对应class；真实findGenerationPoint先父级checkLocation再generatePieces，非未引用的几何helper。generated JSON、template二进制和运行期自然start未验证，不能从这条入口源码推成实际世界已生成。',
 '构造传false,false,true，父级不应用通用地表高度/避水检查，但仍消费enable和实际allowedBiome集合。generatePieces取chunk中点/OCEAN_FLOOR_WG高度，把本机制的高度范围交给tryWroughtChamber。父级avoidStructures参数没有实际使用，不能说第三flag落实避让。',
 '核心固定dx,dz从-8到<8步2，共最多64列。heightMax=-65或高于surface时取surface，heightMin=-65改-64；逐列向下直到第一个非solid层，再向下到solid floor。源码注释称air，实际!isSolid没有水体/空气判定，不能以洞穴空气名义验收。',
 '有地板后按水平四方向最多8步找墙，每步最多观察4块连续solid；若前三块solid会向上移动checkWallPos，下一水平步沿用抬高后的Y，故不是始终固定地板高度的简单平面射线。找到后返回墙脚位置与按方向确定的Rotation，首个成功立即结束，无随机选择或全局最优证明。',
 'generatePieces按返回rotation旋转(0,0,-9)偏移，再调用start→addPiece。模板piece保存Rot、rotation/no mirror、忽略structure blocks，handleDataMarker空；不能仅看Wroughtnaut名字或注释称chest就宣称铁守卫/箱子实际被生成。',
 '类step返回UNDERGROUND_STRUCTURES，但StructureHandler实际StructureSettings写SURFACE_STRUCTURES；没有读native调度消费不能把前者当已证明最终生成阶段。generationDistance非负只作enable守卫；实际spacing在set写15/5，不能说配置距离任意变更必改变间距。'],
 application=[
 '后续结构可达性需要把structure_set候选、真实biome集合、噪声列条件、楼板/墙体、旋转锚点和实际模板完整性分层记录；候选或tag存在不能替代真实场景。',
 '可借鉴有界地形搜索及从地形方向推导锚点的方法，不复制模板/建筑、不新增内容、不调整本项目cap/概率；把非solid、水和实际空气严格区分。'],
 limits=[
 '一项仅自然地下洞室地形选择整机制参考，无建筑造型/模板数量/实体出生/实际世界结构可达性信用。模板NBT和generated datapack deployment不在缓存审阅范围。',
 '来源为固定较新NeoForge版本，与本项目Forge1.20.1不能直接假设API/原生调度兼容。isSolid/getBaseColumn/模板原生实现作为调用边界，不宣称复制可直接运行。',
 '高度min硬编码-64而非heightAccessor最小值；没有检查每个目标体积/全模板碰撞、fluid、内部通行/灯光，也没保证能找到符合条件的地形。',
 'biome ADD modifier JSON部署仍未闭合；仅记录真实Java接线，不能保证集合启动后非空。与EA7共用biome匹配/registry支持不另计。',
 '同类Frostmaw模板换名/旋转不另计；未运行上游或datagen/游戏/编译/测试。'],
 dedup='独立性在地下噪声列→非solid层→solid floor→四向4高墙→orientation选择这套实际被Structure调用的自然地形决策，非模板换名。EA9是地表firepit实际postProcess局域cohort，并未研究此地下选址；EA4 Hydra四角地表/共享间距、EA5海岛支撑向下、EA6海床水点、EA3已有结构表消费均不同。共享父级/biome/注册/serialization全部支持0，不拆分64列/四方向/任意参数。')
dump('batch-007.json',{'status':'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED','records':[r],
 'proposed_credit':1,'accepted_credit':0,'integrity':verify_records([r]),
 'runtime_structure_or_mob_credit':0,'source_scope':'terrain-selection implementation only; template deployment not inferred'})
# Addenda supplement immutable proposals and independent receipts; no additional credit.
r7=json.loads((DOCS/'independent-reviews/coordinator-EA0007.json').read_text())
r8=json.loads((DOCS/'independent-reviews/coordinator-EA0008.json').read_text())
dump('review-addenda-002.json',{'status':'COORDINATOR_LIMITS_RECONCILED_ZERO_EXTRA_CREDIT',
 'EA-0007':{'receipt':'independent-reviews/coordinator-EA0007.json','receipt_sha256':sha((DOCS/'independent-reviews/coordinator-EA0007.json').read_bytes()),
 'limits':['UMVUTHANA_CRANE placement注册但不在SPAWN_CONFIGS；null config跳过全部configured分支returntrue，不能概括全部注册实体消费全部条件。','ResourceLocation.tryParse结果传getOptional无显式null guard；missing holder跳过不证明任意非法名称fail-safe。'],
 'verification_correction':r7['verification_correction']},
 'EA-0008':{'receipt':'independent-reviews/coordinator-EA0008.json','receipt_sha256':sha((DOCS/'independent-reviews/coordinator-EA0008.json').read_bytes()),
 'limits':['custom predicate present时用原origin直接返回，offset及全部标准条件不执行。','modifier对每条同entity先删CREATURE旧项再加；schema category不等于实际消费类别。','保留NegatableList requireAll跳过exclusion、未加载fail-open、replaceable/NBT和缓存温度边界。'],
 'semantic_distinction':'registry-wide replacement predicate EA7 vs per-SpawnerData闭包 AND native RETURN EA8，非普通字段/helper另计'},
 'original_batches_unchanged':True,'additional_credits':0})
print('Packaged EA-0012,',len(r['chain']),'ranges; one proposal, zero accepted')
