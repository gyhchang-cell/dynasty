"""Static fixed-source mechanism and incomplete-candidate packaging only."""
from evidence import *
E=AM+'entity/EntityElephant.java'
S=AM+'event/ServerEvents.java'
def m(p,s,r):return method('am',p,s,r)
def s(p,a,b,r):return span('am',p,a,b,r)
r=record('EA-0011','am','trader-finalization-attached-encounter-with-rider-synchronized-expiry',
 m(S,'public void onEntityFinalizeSpawn(', '完整实际Forge FinalizeSpawn subscriber：trader附件出生分支与其他无额外信用分支'),
 [m(AM+'AlexsMobs.java','public AlexsMobs()', '实际MinecraftForge EVENT_BUS注册ServerEvents'),
  m(E,'public boolean canSpawnWithTraderHere()', '实际加载/障碍/4格上方空气谓词'),
  m(E,'protected EntityElephant(', '创建时初始化inventory'),m(E,'private void initElephantInventory()', '完整inventory初始化/内容搬运'),
  m(E,'protected void defineSynchedData()', 'Trader/Chested初始false'),m(E,'public void setTrader(', '实际trader状态写'),
  m(E,'public boolean isTrader()', '实际状态读'),m(E,'public void setChested(', '实际chest状态写'),
  m(E,'public void addElephantLoot(', '实际loot调用；loot资源内容非本项范围'),
  m(E,'public void tick()', '完整tick；仅server非tame trader调用tryDespawn；tame分支会卸下passengers'),
  m(E,'private boolean canDespawn()', '非tame且trader'),m(E,'private void tryDespawn()', '读取当前trader乘客剩余时间，否则自身计时；到零clear内容并DISCARDED'),
  m(E,'public AbstractVillager getControllingVillager()', '遍历实际passengers，未以原始trader UUID配对'),
  m(E,'public void addAdditionalSaveData(', 'Trader/Tamed/DespawnDelay与inventory实际NBT写'),
  m(E,'public void readAdditionalSaveData(', '实际NBT恢复；不凭字段存在推断每次落盘'),
  s(E,133,133,'默认despawnDelay47999，仅默认参数支持'),
  s(AM+'config/AMConfig.java',210,211,'概率/biome开关默认值支持'),
  s(AM+'entity/AMEntityRegistry.java',65,65,'实际注册CREATURE，不等于原生自然cap豁免')],
 observation=[
 '真实注册ServerEvents的@SubscribeEvent FinalizeSpawn入口，只认WanderingTrader、正配置概率、随机条件与可选温度>=1；只在getChunkNow非空时创建象，再核查isLoaded/checkSpawnObstruction/上4格空气，设置trader/chested并addFreshEntity、强制骑乘、填loot。未核查event spawn reason，不是仅NATURAL事件。',
 '此入口没有create null保护、addFreshEntity/startRiding结果判定或原trader UUID/已附象幂等标志；后续trader是否真的加入/未被取消未核验，故event/finalize回调不等于一对有效活体已出生。loot填充也不能代替加入成功。',
 '完整tick中server且非tame trader才调用tryDespawn；有实际WanderingTrader乘客且其delay>0时先同步delay再减1，否则自身delay递减。到零卸leash、clear inventory、DISCARDED当前AbstractVillager乘客及象，不走die战利品逻辑；不能当玩家击杀或drop。',
 '与商人绑定依靠当前passengers而非保存的原trader UUID；异常换乘的其他AbstractVillager也会在expiry被discard。不宣称严格identity绑定。tame会停止该自定义清理，完整tick驯服分支还主动卸乘客。',
 '存档写回Trader/Tamed/DespawnDelay及Items，read恢复这些字段；实际交易物loot资源内容未审。read else分支逐项重复初始化，但initElephantInventory会复制旧容器内容；不据此宣称物品丢失，也不从字段存在推断每次状态变更必落盘。'],
 application=[
 '后续生态分析区分原生分类抽取与其他游戏事件附带遭遇；记录来源事件、实际加入和乘客绑定结果，再跟踪临时种群退出；当前生产不新增商人附属spawn或绕cap。',
 '可借鉴附属实体跟随主遭遇剩余寿命、驯服退出临时回收的状态划分；需使用明确identity、成功提交、正确清理原因和库存证据，不照搬原实现的缺陷。'],
 limits=[
 '只研究真实模组event consumer与附属种群生命周期；vanilla WanderingTraderSpawner→Forge FinalizeSpawn触发内部未全文审，不能承诺固定周期、来源仅自然或本世界可达。',
 '概率不是出生成功率；chunk与obstruction只是调用前条件，无入世/存活运行证据。未读当前版本NaturalSpawner实体计数内部，不声称真正解除CREATURE cap。',
 '未执行/编译；未验证库存loot资源、taming全部外部导航/物品来源或其他模组cancel优先级；当前完整handler里其他物种AI分支均0额外信用。',
 'expiry同步取决于实际riderDelay与tick执行，不把默认47999直接说成统一的实际世界期限或严格有界次数。'],
 dedup='相较EA1天气自带调度和EA4/5/6/9 worldgen seeding，本项入口是另一原生实体的finalize事件，衍生实体通过实际乘客的剩余寿命同步退出，tame改变退出状态；相较EA10巢内队列不含储存/重建。整个事件/条件/乘客/计时/NBT/cleanup合1项，同类trader附件/换动物ID不再计。')
dump('batch-006.json',{'status':'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED','records':[r],
 'integrity':verify_records([r]),'credits_proposed':1,'credits_accepted':0,'no_game_compile_test_or_production_change':True})
T=AM+'entity/EntityTriops.java'; B=AM+'block/BlockTriopsEggs.java'
c=record('EA-C004','am','triops-pair-lock-surface-egg-and-hatch-lifecycle-incomplete-native-scheduler',
 m(T,'public InteractionResult mobInteract(', '实际玩家输入喂食入口，食物tag内容缺失'),
 [m(T,'protected void registerGoals()', '配对与产卵实际goal注册'),
  s(T,361,475,'完整BreedGoal和LayEggGoal内部类，含配对保留/停止/产卵边界'),
  m(T,'public boolean isSearchingForMate()', '真实活体/水/fed/cooldown条件'),
  span('am',T,229,253,'完整实体tick；breeding cooldown递减，未发现baby age递增','complete_method'),
  m(T,'public void addAdditionalSaveData(', '配对状态NBT保存'),m(T,'public void readAdditionalSaveData(', '配对状态NBT恢复'),
  m(T,'public boolean requiresCustomPersistence()', 'baby/fromBucket/fedCarrot个体持久性谓词'),
  m(T,'public boolean removeWhenFarAway(', '距离despawn决定'),m(T,'public void setBabyAge(', '实际synched age写'),
  m(B,'public BlockTriopsEggs()', 'FrogspawnBlock父类实际继承'),
  m(B,'public void tick(BlockState blockState,', '孵化先destroyBlock再尝试2/3幼体且忽略加入结果'),
  s(AM+'block/AMBlockRegistry.java',50,50,'卵方块实际注册'),m(AM+'AlexsMobs.java','public AlexsMobs()', '实际mod bus block/entity注册')],
 observation=['已全文阅读EntityTriops与BlockTriopsEggs；配对canUse会给partner.breedWith=本体，但stop仅清fed与设置cooldown，所读完整类未发现清breedWith；不把心形广播当产卵成功。',
 'LayEggGoal最多10次XZ候选，从当前位置上10格向下找水面空气，靠近后先pregnant=false再setBlockAndUpdate，忽略setBlock结果。',
 '卵tick先破坏自身，再create2/3幼体setPersistenceRequired/babyAge=-12000且addFreshEntity结果忽略。所读完整实体类没有babyAge自增，故不能推断长大后会恢复距离清理；不过原生父类内部未完整读取，不宣称运行期永不长大。'],
 application=['为研究种群增殖与cap共存保留完整生产/消耗顺序；必须补齐父类调度/生存条件和实际食物tag后再判断整链可达，不用方法数量充数。'],
 limits=['FrogspawnBlock实际onPlace孵化调度与canSurvive父类源码未核闭；TRIOPS_BREEDABLES实际非空部署内容未核闭。candidate0，未独立提案。','食物/配对/egg/幼体整个机制最多1项，不能按各支路或孵化个体数拆信用。'],
 dedup='暂存不计；与EA10巢内实体保存后释放不同，是喂食配对生成卵/孵化新个体。未来与其他卵类同义模板合并。',status='candidate')
dump('candidates-002.json',{'status':'INCOMPLETE_ZERO_CREDIT','records':[c],'integrity':verify_records([c]),'proposed_credit':0,'accepted_credit':0})
print('EA-0011 one proposed; EA-C004 incomplete zero credit')
