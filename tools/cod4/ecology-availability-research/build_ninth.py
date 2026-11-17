"""Package a real parasitic brood lifecycle; text only, never run upstream Java."""
from evidence import *
H=AM+'entity/EntityTarantulaHawk.java'; E=AM+'effect/EffectDebilitatingSting.java'
def m(p,s,r):return method('am',p,s,r)
def s(p,a,b,r):return span('am',p,a,b,r)
chain=[m(H,'protected void registerGoals()', '真实BreedGoal/AIMelee/AIBury及spider目标注册'),
 m(H,'public void spawnChildFromBreeding(', '交配成功只设bredBuryFlag/年龄/love/stat/XP，无直接子实体'),
 m(H,'public AgeableMob getBreedOffspring(', '直接后代接口返回null，不能以交配统计视作出生'),
 m(H,'public boolean isFood(', '驯服后breedable tag才是食物'),
 m(H,'public InteractionResult mobInteract(', '实际喂食驯服/父类交互入口，全部方法支持但command不计额外'),
 s(H,716,818,'完整AIMelee内部类：bred flag决定sting amplifier、实际addEffect和拖载、stop清flag'),
 s(H,916,981,'完整AIBury内部类：沙地搜索、drag/dig、有限200tick下沉与stop边界'),
 m(H,'private BlockPos genSandPos(', '最多15随机沙候选；上界255非世界高度访问器'),
 m(H,'private Vec3 getOrbitVec(', '实际环绕候选及isEmptyBlock判定'),
 m(H,'public Vec3 getBlockGrounding(', '拖载前落地候选辅助'),
 m(H,'private BlockPos getCrowGround(', '实际向下查solid/fluid，硬编码-64'),
 m(H,'public boolean isTargetBlocked(', '射线遮挡辅助'),
 span('am',H,303,431,'完整实体tick；attackProgress驱动命中、拖载恢复分支','complete_method'),
 m(H,'public void addAdditionalSaveData(', 'BreedFlag/飞行/挖掘等状态序列化支持'),
 m(H,'public void readAdditionalSaveData(', '实际恢复BreedFlag；不能推断目标/倒计时完整恢复'),
 m(H,'public SpawnGroupData finalizeSpawn(', '实际幼体finalize可设nether状态再super'),
 m(H,'private static boolean isBiomeNether(', 'finalize实际biome tag条件'),
 m(H,'public boolean isDragging()', '真实drag状态读'),m(H,'public void setDragging(', '真实drag状态写'),
 m(H,'public boolean isDigging()', '真实dig状态读'),m(H,'public void setDigging(', '真实dig状态写'),
 m(E,'public boolean isDurationEffectTick(', '效果单例lastDuration记下duration并要求>0'),
 m(E,'public boolean isEntityInsideOpaqueBlock(', '实际眼部薄AABB/窒息shape相交，并非普通脚部方块'),
 m(E,'protected EffectDebilitatingSting()', '实际属性modifier初始化'),
 m(E,'public void addAttributeModifiers(', '仅arthropod启用属性modifier'),
 m(E,'public void removeAttributeModifiers(', '仅移除modifier，未在本方法恢复noPhysics/noGravity'),
 m(AM+'event/ServerEvents.java','public void onEntityDespawnAttempt(', '高阶sting真实AllowDespawn事件DENY；不是全局cap钩子'),
 s(AM+'effect/AMEffectRegistry.java',36,36,'真实DEBILITATING_STING RegistryObject'),
 s(AM+'entity/AMEntityRegistry.java',94,94,'后代EntityType注册CREATURE；不推断豁免cap'),
 s(H,69,69,'STING_DURATION2400默认常量，非已证精确墙钟时间'),
 m(AM+'misc/AMBlockPos.java','public static final BlockPos fromVec3(', '眼部helper委托'),
 m(AM+'misc/AMBlockPos.java','public static final BlockPos fromCoords(', '坐标用int截断，负坐标非floor'),
 m(AM+'message/MessageTarantulaHawkSting.java','public static void handle(', '按runtime entity id应用默认amplifier0的反馈，不等于server高阶brood事实'),
 m(AM+'AlexsMobs.java','public AlexsMobs()', '实际注册effect/entity和ServerEvents')]
r=record('EA-0014','am','parasitic-brood-effect-expiry-with-host-despawn-denial-and-delayed-offspring',
 m(E,'public void applyEffectTick(', '完整寄生生命周期终点：节肢宿主高阶sting最后效果tick才新建BREEDING幼体'),chain,
 observation=[
 '真实BreedGoal注册且spawnChildFromBreeding覆写不直接出生：设bredBuryFlag、双方age6000/resetLove并给统计/XP；getBreedOffspring返回null。bred flag由AIMelee实际攻击时转成sting amplifier1，普通sting为0。交配反馈、统计、XP均不是幼体出生证据。',
 '完整AIMelee tick先对目标hurt（结果不查），bred flag且目标低血会heal，然后addEffect（结果不查），2400duration用于arthropod。满足麻痹/驯服及bred条件时可强制骑乘拖载；AIBury另最多15次选sand、dig<200下沉最多3格。沙地/埋葬不是Effect最终出生代码的条件，不能宣称所有幼体必须成功埋葬才出生。',
 '实际注册ServerEvents.onEntityDespawnAttempt在有DEBILITATING_STING且amplifier>0时DENY。只是AllowDespawn条件，不是NaturalSpawner global/local cap豁免，不保证其他伤害/和平模式/外部移除不生效；可能保留宿主时长须另查原生消费者。',
 'isDurationEffectTick把当前duration存到效果实例lastDuration。applyEffectTick对arthropod可设置noPhysics/noGravity，下落/禁跳；当lastDuration==1才hurt(amplifier+1)*30；amplifier>0则从宿主处向上找空块至Y256，创建baby、服务端finalize(BREEDING)/addFreshEntity，之后清noGravity/noPhysics。没有验证宿主伤害成功/死亡、沙地或亲本UUID，不能把这次hurt当严格KILLED或把出生绑定某对亲本。',
 '幼体create无null保护、add返回忽略，无位置checkSpawnRules/noCollision；向上空块搜索不是幼体完整bbox安全检查，硬编码256也非世界max高度。清理效果提前结束时，本removeAttributeModifiers只有属性super移除，未见恢复noPhysics/noGravity；最终tick恢复逻辑不自动证明所有取消路径清理完整。',
 'BreedFlag有额外NBT读写，但目标引用、AI内部sandPos/digTime和lastDuration不是本类所读额外字段，因此不保证卸载重载后整条寄生周期相位保持。消息handler按运行期entity id再应用默认amplifier0效果，不能替代server amplifier1/实际后代加入证据。'],
 application=[
 '生态研究需区分配对/奖励、宿主effect状态、宿主暂留、到期发起幼体加入、实际后代存活；被保留的宿主和繁殖统计都不能算已获得新种群。',
 '可借鉴把延迟后代状态绑定在真实宿主生命过程的设计问题，审查暂留与清理、成功提交、取消/重载及亲本归属；1000前不制作寄生/生成器或改cap/类别。'],
 limits=[
 '固定Forge源码只作真实玩法生命周期参考；未审native MobEffectInstance→duration/apply的完整调度，不从共享lastDuration字段就断言已发生跨宿主串用，也不保证其线程/重入安全。',
 '通用vanilla BreedGoal、父mobInteract配对启动与实际breedable食物tag成员未展开，按真实注册/覆写调用边界处理；不证明自然野外亲本可得或玩家材料闭环。',
 '只全文读取相关AI/效果/注册/consumer；MoveControl/导航、完整Forge AllowDespawn原生消费顺序、出生cancel/cap计数未运行验证，不能宣称解决本项目global cap关闭。',
 '这一整链至多1项，战斗伤害、客户端消息、注册/getter/埋葬参数均0额外信用；不把常见sting伤害另算生态机制。',
 '未启动游戏/服务器/GUI，未编译或执行上游，无任何运行出生/击杀/材料信用。'],
 dedup='实际独立语义是交配flag转宿主高阶effect、AllowDespawn暂留宿主、effect寿命末端从宿主位置产生不同种后代；EA13的种植自体growth平台成熟替换、EA10的同种巢内NBT储存释放、EA11的乘客寿命同步退场均不同。全部生殖入口/AI搬运/host effect/清理/后代sink合1链，不按amplifier/猎物/沙地/方法拆分。')
dump('batch-009.json',{'status':'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED','records':[r],
 'proposed_credit':1,'accepted_credit':0,'integrity':verify_records([r]),'new_runtime_credit':0,
 'identity_and_timing_scope':'host effect lifecycle source only; no claim native cap opening or confirmed parent/offspring persistence'})
# Additional reading of a different archive pin cannot silently replace the original pinned tree.
base=ROOT/'tools/cod4/immune-feedback-research/sources/TeamTwilight__twilightforest'
meta=json.loads((base/'source.json').read_text())
paths=['src/data/java/twilightforest/datagen/data/worldgen/TFStructureSetGenerator.java',
       'src/main/java/twilightforest/world/components/structures/placements/LandmarkGridPlacement.java']
dump('candidate-C005-archive-addendum.json',{'status':'FULL_METHOD_READ_BUT_GIT_TREE_ASSOCIATION_INCOMPLETE_ZERO_CREDIT',
 'candidate_id':'EA-C005','repo':meta['repo'],'revision':meta['commit'],
 'cached_metadata':str((base/'source.json').relative_to(ROOT)),
 'cached_metadata_sha256':sha((base/'source.json').read_bytes()),'archive_sha256':meta['archive_sha256'],
 'read_files':[{'path':p,'source_local':str((base/p).relative_to(ROOT)),'source_sha256':sha((base/p).read_bytes()),
                'line':1,'end_line':len((base/p).read_text().splitlines()),'excerpt':(base/p).read_text(),
                'url':f"https://github.com/{meta['repo']}/blob/{meta['commit']}/{p}"} for p in paths],
 'observation':'另一固定archive确有完整TFStructureSetGenerator.bootstrap消费者：6种锁类型格心和多个forceCenters实际配置。已全文读取；但commit9911不同于原candidate285f且无tree.json，不能拿另一版本资源闭合旧pin或冒充Git tree验证。',
 'application':'将来需补此固定commit Git tree及余链完整审查，或在原固定树找到相应资源；不得覆盖旧sources元数据。',
 'limits':['未查远端/未重试失败服务','archive元数据文件hash不替代已要求Git tree/blob/commit链','未审本版本其余全链，不信用接枝'],
 'proposed_credit':0,'accepted_credit':0,'does_not_overwrite_existing_pinned_source':True})
print('EA-0014 one new pending mechanism;',len(r['chain']),'supporting ranges; C005 archive lead still zero')
