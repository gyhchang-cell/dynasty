"""Package two complete gameplay mechanisms from pinned cached text; never execute upstream."""
from evidence import *
T=AM+'entity/EntityTerrapin.java'; B=AM+'block/BlockTerrapinEgg.java'; E=AM+'tileentity/TileEntityTerrapinEgg.java'
S=AM+'entity/EntitySkreecher.java'
def m(p,s,r):return method('am',p,s,r)
def s(p,a,b,r,kind='supporting_range'):return span('am',p,a,b,r,kind)
primary=m(B,'public void randomTick(', '完整卵块随机tick：habitat/time gate、HATCH阶段、removeBlock后取亲本BE、幼体加入')
chain=[m(T,'protected void registerGoals()', '实际MateGoal和LayEggGoal注册'),
 s(T,589,625,'完整MateGoal：成功交配保存partnerData到孕体字段并设置HasEgg；无直接幼体'),
 s(T,627,674,'完整LayEggGoal：空地habitat目标、离水到达才setBlock，亲本写BE、清孕态'),
 s(T,60,87,'完整相关synched/实例字段；partnerData为普通内存字段'),
 m(T,'public void addAdditionalSaveData(', '孕态/自身表型/桶来源NBT写入；无partnerData'),
 m(T,'public void readAdditionalSaveData(', '对应恢复，无partnerData恢复'),
 m(T,'public void tick()', '完整实体tick：水陆导航/游泳计时与运动状态；不单计AI'),
 m(T,'public boolean shouldLeaveWater()', '有卵即建议离水'),m(T,'public boolean shouldEnterWater()', '无离水需求才考虑回水'),
 m(T,'private void switchNavigator(', '实际水陆导航切换'),
 s(AM+'entity/ai/AnimalAILeaveWater.java',15,81,'完整离水goal；概率入口、8次候选与无水邻域筛选'),
 m(T,'public boolean isFood(', '真实繁殖食物tag条件，tag内容未审'),
 m(T,'public InteractionResult mobInteract(', '拿繁殖食物交互就setPersistenceRequired，再委托桶/父类'),
 m(T,'public boolean requiresCustomPersistence()', '桶来源/命名保留条件'),m(T,'public boolean removeWhenFarAway(', '距离移除返回桶来源/命名的否定'),
 m(T,'public void saveToBucketTag(', '完整桶NBT保存，自身additionalData包含HasEgg但不含partnerData'),
 m(T,'public void loadFromBucketTag(', '桶恢复实际入口'),
 m(T,'public void setFromBucket(', '孵化后主动设桶来源的真实setter'),
 m(T,'public SpawnGroupData finalizeSpawn(', '普通spawn表型初始化；卵孵化方法没有调用本finalize'),
 m(T,'public AgeableMob getBreedOffspring(', '通用后代工厂存在，但实际MateGoal覆写不调用'),
 m(T,'public boolean hasEgg()', '孕态读'),m(T,'private void setHasEgg(', '孕态写'),
 s(T,330,384,'完整表型getter/setter与ordinal clamp；不按表型类别计数'),
 m(B,'public BlockTerrapinEgg()', 'randomTicks启用与初始HATCH0/EGGS1'),
 m(B,'public static boolean hasProperHabitat(', '脚下habitat委托'),m(B,'public static boolean isProperHabitat(', 'SAND或CROCODILE_SPAWNS tag'),
 m(B,'private boolean canGrow(', '时间窗口或1/15随机条件；不是固定孵化墙钟'),
 m(B,'public void onRemove(', 'EGGS<=1才super，不能不读引擎就断言所有移除都丢BE'),
 m(B,'public BlockEntity newBlockEntity(', '实际创建亲本数据BE'),
 m(E,'public TileEntityTerrapinEgg(', '实际BlockEntityType绑定'),
 m(E,'public void addAttributesToOffspring(', '完整双亲赋值与mutation；nextInt2令case2不可达'),
 m(E,'public void load(', '双亲NBT读取'),m(E,'protected void saveAdditional(', '双亲NBT写入'),
 s(E,72,115,'完整ParentData构造/合并比较/序列化；只保存表型不保存亲本UUID'),
 m(B,'public List<ItemStack> getDrops(', 'silk touch实际把亲本写入BlockEntityTag，返回单个物品'),
 m(B,'public boolean canBeReplaced(', '同卵物品叠加至4的入口'),m(B,'public BlockState getStateForPlacement(', '叠卵状态路径没有亲本canMerge调用'),
 m(B,'public void stepOn(', '踩踏入口'),m(B,'public void fallOn(', '坠落入口'),
 m(B,'private void tryTrample(', '实际服务器随机移除'),m(B,'private boolean canTrample(', '排除同种和蝙蝠；玩家或mobGriefing'),
 m(B,'private void removeOneEgg(', '减少EGGS或destroyBlock'),m(B,'public void playerDestroy(', '玩家破坏实际调用removeOneEgg'),
 s(AM+'block/AMBlockRegistry.java',37,37,'实际卵块注册'),s(AM+'tileentity/AMTileEntityRegistry.java',19,19,'实际卵BE绑定'),
 s(AM+'entity/AMEntityRegistry.java',118,118,'实际实体注册WATER_AMBIENT，非CREATURE替换建议'),
 m(AM+'AlexsMobs.java','public AlexsMobs()', '实际entity/block/BE注册调用入口')]
r15=record('EA-0015','am','paired-parent-state-carried-through-habitat-egg-block-incubation-and-persistent-hatchlings',primary,chain,
 observation=[
 '真实注册MateGoal覆写breed：只把配偶表型复制到孕体partnerData、HasEgg=true、清love/设双方6000年龄、发统计/XP；没有当场新建幼体。有卵触发shouldLeaveWater，实际离水goal有水/概率/目标条件，最多8候选，并非立刻必达岸边。',
 '完整LayEggGoal以16搜索范围父类择点，isValidTarget只验证above空和SAND或CROCODILE_SPAWNS基底。离水且到达后设置卵块；random.nextInt(1)+3实际总是3枚；setBlock返回未查，之后无论是否取得BE都清HasEgg并设loveTime600。digTime只有字段及stop置0，本tick没有挖掘等待门槛，不能宣称真正等待一段dig时间。',
 '孕体add/readAdditionalSaveData保存HasEgg和自身表型，却没有partnerData；同样save/load桶tag仅转这些字段。重载或装桶恢复怀卵后partnerData可能为空，产卵fallback使parent2=parent1，不能声称配对遗传随所有转存持久化。卵BE有双亲load/save支持，但产卵直接赋parent字段未显式setChanged，不保证全部后续变更落盘。',
 '卵块构造启用randomTicks；随机tick需habitat与日时0.65<time<0.69或1/15，HATCH0→1→2后才移除并按EGGS新建幼体。时间窗口只是每次随机tick内的gate，不是固定天数/必达孵化率；调用removeBlock早于getBlockEntity。自定义onRemove仅EGGS<=1时super，因此这里只报告顺序及引擎关联依赖，不断言默认3卵必然失去亲本BE。',
 '双亲都在时实际addAttributesToOffspring对type/shell/skin独立二选一，颜色用整型平均；15%mutation切OVERLAY但nextInt(2)使skinColor的case2不可达。整个遗传算法合为此生命周期支持，绝不按品种/颜色/排列拆项；未声称生物学颜色混合正确或天然稀有率。',
 '幼体create无null防护，年龄-24000，setFromBucket(true)，moveTo后addFreshEntity返回忽略；没有finalizeSpawn、collision/spawnrules或NaturalSpawner cap准入调用。桶来源实际进入requiresCustomPersistence和removeWhenFarAway条件，故繁殖幼体具有距离保留支持；这不是全局cap豁免、不死或成功加入证明。先remove卵再add意味着不能仅以卵消失确认后代存在。',
 '踩踏/坠落/玩家破坏可减少卵数；silk touch仅返回单个卵物品，并把可用亲本写BlockEntityTag。叠卵placement只改EGGS，所读完整block没有调用ParentData.canMerge；原生BlockItem如何处理BlockEntityTag未审，不宣称混合亲本叠卵或silk物品重放完全正确。'],
 application=['生态可达性要分别核实配对成功、孕态延续、离水择址成功、卵块提交、亲本数据仍在、实际后代加入及距离保留；每一级反馈不能代替下一阶段事实。',
 '借鉴跨实体→BlockEntity→幼体交接的证据门槛，尤其孕体/桶转存的配偶信息、先删后加失败、随机tick和取消破坏；1000前不制作修复或改cap/category/概率。'],
 limits=['此处1整机制，包含环境孵化与亲本转存；普通爬行动物同模板卵不再另计，getter/颜色/注册支持均0额外信用。',
 '通用BreedGoal/MoveToBlockGoal/LandRandomPos/BlockItem/Level.removeBlock完整原生消费者未展开，无父类调度与BE移除顺序运行结论。',
 '食物tag和CROCODILE_SPAWNS资源实际内容、自然出生表与野外亲本可达性未闭合；只认可实际玩法繁殖链，不宣称自然场景或建筑信用。',
 '无游戏/编译/测试/上游代码执行；遗传与孵化仅源代码路径观察，没有已出生数、存活或材料验收。'],
 dedup='双亲数据从孕体普通字段交给真实卵BE，再受基底/随机tick孵化并给幼体桶来源距离保留，为一个跨载体繁殖机制；EA14为宿主高阶效果到期寄生，EA13是自体成长替换，EA10为既有同种NBT巢存取。差异依靠实际状态载体/调用链，不依赖物种ID或颜色。与候选Triops通用Frogspawn路径不共享本BE亲本载体，候选仍0；所有通用爬行卵模板不得再包装。')

chain16=[m(S,'protected void registerGoals()', '玩家target注册与FollowTargetGoal/避warden实际注册'),
 s(S,489,520,'完整FollowTargetGoal；活目标/cooldown入口、水平2.5内开始clap'),
 m(S,'public void setClapping(', '停止clap时清clapTick，但不复位one-attempt latch'),
 m(S,'public void angerAllNearbyWardens()', '已有warden按视线增怒，无新建'),m(S,'private List<Warden> getNearbyWardens()', '实际35水平、向下至-64/上至cling决定高度AABB，不是全维度去重'),
 m(S,'public void addAdditionalSaveData(', 'SummonedWarden保存的是attempt latch，不是加入成功'),m(S,'public void readAdditionalSaveData(', '实际恢复attempt latch/cooldown/cling；clapTick不保存'),
 m(S,'public boolean hurt(', '先清cling/clap并设cooldown，再super.hurt，拒伤也可能打断'),
 s(S,57,72,'字段：hasAttemptedWardenSpawning/clapTick普通实例状态'),
 m(S,'public boolean checkSpawnRules(', 'skreecher自身roll条件非warden加入准入'),
 m(S,'public static boolean checkSkreecherSpawnRules(', 'skreecher自身Sculk/黑暗/非和平，非结构start验证'),
 m(S,'private float calculateDistanceToCeiling()', 'tick实际天花板距离委托'),m(S,'public BlockPos getCeilingOf(', '向上至maxBuildHeight支撑面搜索'),
 m(S,'private void switchNavigator(', '实际clinging导航切换'),m(S,'protected PathNavigation createScreecherNavigation(', '完整自定义空中路径稳定目标判断'),
 s(S,458,487,'完整自定义MoveController，运动不另计'),
 s(S,313,319,'cling状态读写'),s(S,321,323,'clap状态读'),s(S,332,342,'jump状态与坐标helper'),s(S,386,392,'ceiling距离状态读写'),
 s(AM+'entity/ai/EntityAINearestTarget3D.java',11,28,'完整3Dtarget helper与父类委托；实际玩家搜索盒由registerGoals覆写'),
 m(AM+'entity/AMEntityRegistry.java','public static boolean rollSpawn(', '实际概率helper，SPAWNER bypass only'),
 s(AM+'entity/AMEntityRegistry.java',137,137,'SKREECHER实际EntityType CREATURE；不能凭extends Monster推cap类别'),
 s(AM+'entity/AMEntityRegistry.java',235,235,'实际placement注册'),s(AM+'misc/AMTagRegistry.java',230,230,'实际warden允许biome tag键；内容未读'),
 s(AM+'config/AMConfig.java',228,228,'功能静态默认true非运行期配置事实'),
 m(AM+'AlexsMobs.java','public AlexsMobs()', '实际注册入口')]
r16=record('EA-0016','am','ai-alarm-triggered-local-encounter-with-persisted-single-attempt-latch',
 m(S,'public void tick()', '完整实体tick：clap累计、局部warden检查、先消耗attempt再尝试TRIGGERED加入与终止条件'),chain16,
 observation=[
 '实际注册玩家target（本覆写搜索盒水平16、Y硬编码-64..320）和FollowTargetGoal；有活目标且clingCooldown<=0才可启动，水平距离<2.5使clapping=true。clap期间每8tick怒化附近已有warden、ENTITY_ROAR反馈，但这些都不是新生warden证据。',
 'tick在clapTick>=100且未attempt且配置允许时，先将hasAttemptedWardenSpawning=true，再向下找UP sturdy面至Y>-64结束。然后只有server、局部getNearbyWardens为空、biome holder命中SKREECHERS_CAN_SPAWN_WARDENS才create/finalize(TRIGGERED)/设置attacktarget和anger/addFreshEntity。地面/biome/局部已存在阻止均已消耗本实体attempt，没有自动重试。',
 '实际局部warden搜索盒水平±35，Y参数从自身+(cling?5:25)到-64，不是球半径或全维度唯一约束；未读AABB原生构造，不把书写Y倒序直接当成空盒或bug实证。多个召唤者仍可能各有attempt，附近查询只见当时可查询到的实体，不保证跨tick/卸载全局去重。',
 'create无null防护、向下搜索遇-64可结束而未证明sturdy，出生只moveTo地面上方，无完整bbox/collision或原生warden trySpawnAt/SHRIEKER逻辑；addFreshEntity返回未查。所以SummonedWarden标签是attempt latch而非spawn成功收据，也不能把鸣叫或延迟达到100作为已出现事实。',
 'SummonedWarden实际NBT读写，clapTick和clapping额外NBT未保存；setClapping(false)会清tick却不清attempt。hurt在super是否接受伤害之前就清cling/clap并设200+随机cooldown；clap连续状态可被拒伤也打断。clap末尾server检查目标存活、LOS、隐身/盲和水平>20停止，但本tick尝试出生在该检查之前，因此不是先验证全部目标条件再commit。',
 '注册类型实际CREATURE，尽管类extends Monster；自身placement要求非和平/黑暗/SCULK、rollSpawn单独生效，而warden是TRIGGERED直接加入路径。本链未调用NaturalSpawner全球/局部cap，不得以本直接加入设计证明原项目自然CREATURE gate已打开或建议换类别。'],
 application=['稀有遭遇的可用性要区分有界延迟、attempt锁、环境拒绝、已存在抑制、实际加入及存档状态；保存变量名称不能替代spawn成功证据。',
 '可借鉴追踪锁在检查前或成功后提交、何时取消、重载是否重试及局部去重空间边界。此处仅研究真实AI触发遭遇，不制作本项目召唤器或调整生态cap。'],
 limits=['只作为AI触发生态遭遇1链，非被动生物cap共存解决方案、非自然结构生成/建筑或已生成warden实证。',
 '未审原生Warden.finalizeSpawn/EntityType.create/ServerLevel.addFreshEntity/AABB消费者全链及实际biome tag资源，因此不保证原生warden规则全部生效或野外交集非空。',
 'clap计数在tick中的增长不是已证100个连续真实墙钟tick；原生AI调度/卸载暂停/重载后相位不能由本类 alone 保证。',
 '未编译/运行/游戏/服务器/GUI，不执行上游代码；已接收代码只供语义借鉴，1000门槛未达。'],
 dedup='独立机制为真实AI持续报警后、局部已有个体抑制、持久化单次尝试消耗的跨物种遭遇；EA1是天气/world计时遭遇并有周期概率回写，EA14是宿主效果繁殖后代，EA11是交易者附属同步寿命，EA9是结构postProcess队列。不能把相同clap计数/声音/怒化/出生拆分或按warden种类包装。')
rows=[r15,r16]
dump('batch-010.json',{'status':'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED','records':rows,
 'proposed_credit':2,'accepted_credit':0,'integrity':verify_records(rows),
 'review_routing':{'EA-0014':'coordinator accepted; do not assign Carson duplicate review','EA-0015':'pending independent review','EA-0016':'pending independent review'},
 'new_runtime_credit':0})
# Real complete reading excluded from credit because the useful storage-release pattern overlaps EA10.
C=AM+'entity/EntityCatfish.java'
e=s('am',1,1,'unused') if False else span('am',C,60,704,'完整类已读；排除计数，不作为新机制')
dump('semantic-exclusions-004.json',{'status':'READ_COMPLETE_BUT_NO_NEW_CREDIT','records':[dict(
 id='EX-CATFISH-STORAGE',**e,proposed_credit=0,accepted_credit=0,
 observation=['实际TargetFoodGoal成功swallow后discard猎物，仅addAdditionalSaveData而非完整save；spit新建实体后readAdditionalSaveData并覆写health，成功add才清存储。',
 '因此不是原UUID完整回放，也不是严格击杀；状态占据保留+成功加入后移出与EA10巢存取核心相近。本次不靠换猎物/容器另计。'],
 application=['保留掠食可能移除但未击杀的生态证据边界；需区分活体、储存内容、重新创建，不按death/killed冒充。'],
 limits=['未审原生add/readAdditionalSaveData完整基类字段，不声称全部附加数据已复原','食物tag内容/自然巨大体型biome未闭合','仅0信用排除记录，不新增候选或有效机制'])]})
print('EA15/16 pending:',[len(r['chain']) for r in rows],'; Catfish excluded0')
