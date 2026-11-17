"""Persist incomplete research as zero-credit candidates, never as completed references."""
from evidence import AM, IAF, TF, dump, method as m, record, verify_records


def methods(key, prefix, name, specs):
    return [m(key,prefix+name+'.java',sig,role) for sig,role in specs]


anthill=methods('am',AM,'world/FeatureLeafcutterAnthill',[
    ('public boolean place(', '已全文读：自然feature入口与初始蚁群入巢')])[0]
ants=methods('am',AM,'tileentity/TileEntityLeafcutterAnthill',[
    ('public void tryEnterHive(EntityLeafcutterAnt p_226962_1_, boolean p_226962_2_, int p_226962_3_)', '实体序列化入巢并移除'),
    ('private boolean addAntToWorld(', '出口遮挡与实际addFreshEntity返回值'),
    ('private void tickAnts()', '时间达到后仅成功加入才删除队列项'),
    ('public static void serverTick(', 'block entity tick入口'),
    ('public void load(CompoundTag nbt)', '巢内群落读入'),
    ('public ListTag getAnts()', '巢内群落写出数据'),
    ('public void saveAdditional(', '写入block entity NBT')])
c1=record('EA-C001','am','candidate-natural-anthill-inhabitant-storage-and-confirmed-release',anthill,ants,
    ['自然place创建蚁丘并生成3–5个入巢实体，首个queen；tryEnterHive将实体NBT存入群落，实际世界实体被DISCARDED。',
     'tickAnts达到占用时限后尝试出巢；addAntToWorld返回真实level.addFreshEntity值，成功才iterator.remove，遮挡失败会保留。'],
    ['自然结构内持有的生态群落不等于当前已加载动物；实体生命周期与cap计数必须区分巢内NBT和世界实体。'],
    ['候选0信用：尚缺已部署configured/placed feature、biome modifier JSON及Block ticker绑定的核读，不能称入口链完整。',
     'getAnts未写wrapper Queen但load读取它；不能直接采用该存档格式，不把问题包装成另一个案例。',
     '释放移除UUID，不能把入巢前后UUID视作同一实体的原始自然回执。'],
    {'unit':'生成→入巢→保存→有界占用→成功释放合并一个待研究机制','distinctness_pending':True},status='candidate')
c1['next_required']=['只读取得固定树内已缺失配置，失败不重试','读BlockLeafcutterAnthill.getTicker与registry/feature链','检查已有其它研究本协议内是否同一群落机制']

grave=m('iaf',IAF+'world/structure/GraveyardStructure.java','public static @NotNull Optional<PieceGenerator<JigsawConfiguration>> createPiecesGenerator(', '已全文读：旋转四角低点与jigsaw起始位置')
c2=record('EA-C002','iaf','candidate-graveyard-jigsaw-natural-scene-entry',grave,
    methods('iaf',IAF,'world/IafWorldRegistry',[
        ('public static void registerStructureConfiguredFeatures()', '结构set/候选biome配置'),
        ('public static Holder<ConfiguredStructureFeature<?, ?>> registerConfiguredStructureFeature(', '结构配置holder')]),
    ['generateGraveyards开关后以随机旋转采样四角高度，取最低点+1，替换context为实际graveyard pool并JigsawPlacement.addPieces。',
     '真实专用结构类型比“ghost_sites只有古战场”更明确，但当前记录尚未闭合资源/自然生成配置交集。'],
    ['学习如何为场景身份保留专属结构与自然配置链，不拿任何废墟别名替代荒村/义庄/鬼市的范围。'],
    ['候选0信用：Pool.replaceContext、实际template pool/biome tag资源尚未完整核读；不称已自然生成。',
     'Rotation使用ThreadLocalRandom，不能声称仅固定世界seed就完全复现旋转。',
     '不制作建筑、不复制模板，不把三个同组jigsaw结构当三个研究信用。'],
    {'unit':'graveyard完整自然结构链待审','same_template_siblings_excluded':['gorgon_temple','mausoleum']},status='candidate')
c2['next_required']=['核读Pool.replaceContext与固定资源引用','验证非空biome集合/structure set/pool自然链','保留旧版本API限制']

avoid='world/components/placements/AvoidLandmarkModifier'
c3=record('EA-C003','tf','candidate-landmark-reference-clearance-for-natural-decoration-coexistence',
    m('tf',TF+avoid+'.java','public Stream<BlockPos> getPositions(', '已全文读：根据chunk真实结构引用抑制自然装饰'),
    methods('tf',TF,avoid,[
        ('private boolean structureTypeBlocksFeaturePlacement(', '查询start chunk及valid start'),
        ('private boolean allowedInsideStructure(', '结构显式允许集'),
        ('private boolean clearFromStructureZone(', '表层/地下/植被占用相交'),
        ('private boolean placementIsBlocked(', 'bbox/piece或中心半径两种净空'),
        ('private static DataResult<AvoidLandmarkModifier> validate(', '不能完全没有占用标记')]),
    ['按当前chunk结构reference查询start，有效且没有允许重叠时才做净空筛选；半径<=0走piece距离，否则走XZ方形范围。',
     '空stream抑制该候选装饰；没有valid start不会据名字删除生态位置。'],
    ['研究自然场景与植被/地下生态共存应定位实际引用及空间，而非全biome全禁；不建议改现有项目参数。'],
    ['候选0信用：还没核读实际使用本modifier的自然placed feature资源，以及BoundingBoxUtils.greatestAxalDistance；不能把仅codec注册当已生效玩法。',
     'UtilityPiece.allowFeatures是局部例外；surface/underground/vegetation是同一机制分支，不拆成3条。',
     '它针对feature placement，不直接释放被动cap，也不保证自然动物出生。'],
    {'unit':'结构净空过滤链待审','different_from':['EA-0003针对已有结构中的生物出生表，不是装饰placement']},status='candidate')
c3['next_required']=['定位固定自然placed feature具体绑定','读完整距离helper及注册消费链','与结构grid exclusion机制区分，不能包装同一过滤链重复计数']

dump('candidates-001.json', {'status':'INCOMPLETE_ZERO_CREDIT','candidates':3,'proposed_credit':0,'accepted_credit':0,
    'records':[c1,c2,c3],'integrity':verify_records([c1,c2,c3])})
print('Saved3 explicit incomplete candidates,0credit')
