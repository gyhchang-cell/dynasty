"""Locally authored static evidence assembler. Never imports/executes upstream code."""
from pathlib import Path
import hashlib, json, re, datetime
ROOT = Path(__file__).resolve().parents[5]
# Resolve the repository from this script's fixed authorized location.
assert (ROOT / 'docs/cod4/audit-20261022/sweep-receipt-research/protocol.json').exists(), ROOT
TOOL = ROOT / 'tools/cod4/sweep-receipt-research/helpers/combat-spectrum'
OUT = ROOT / 'docs/cod4/audit-20261022/sweep-receipt-research/helpers/combat-spectrum'
manifest = json.loads((OUT/'source-manifest.json').read_text())
M = {x['repo']:x for x in manifest}
B = 'ZsoltMolnarrr/BetterCombat'; S = 'DaFuqs/Spectrum'
BP = 'common/src/main/java/net/bettercombat/'; SP = 'src/main/java/de/dafuqs/spectrum/'
specs=[]
def add(key, repo, path, line, observation, application, limits, supports=(), decision='proposed_eligible', chain=None):
    specs.append(dict(key=key,repo=repo,path=(BP if repo==B else SP)+path,line=line,observation=observation,application=application,limits=limits,support_specs=supports,decision=decision,chain=chain or key))
def b(p,*lines): return (B,BP+p,list(lines))
def s(p,*lines): return (S,SP+p,list(lines))
Q=s('events/listeners/EventQueue.java',18,25,52,68)
POS=s('events/listeners/BlockPosEventQueue.java',17)
OWNER=s('api/block/PlayerOwned.java',12,27,32,40,46)
CCA=s('cca/SpectrumComponentInitializers.java',11)
# One network attack chain; packet codec, hand resolution and redirects carry no extra credit.
add('BC01',B,'network/ServerNetwork.java',53,
'C2S接收先选择玩家当前ServerWorld与攻击手，再executeSync；任务内按该world的实体数字ID逐个解析目标、调用vanilla交互包或player.attack，末尾撤销临时属性并复原combo。跨执行边界没有要求gameTime仍相等。',
'借鉴将输入接收与实际服务端攻击执行分层；方天仅在真实成功伤害后记录来源/目标快照，再以有限年龄交给END消费。临时战斗状态应有可靠清理路径。',
'这不是成功伤害回执；包没有产生刻、UUID、维度或唯一请求号。selectedSlot差异仅打印日志；executeSync不保证必延后一个tick。手与world在调度前捕获；true || rangeCheck绕过范围分支；disconnect早退及异常可能跳过临时属性清理。',
[b('network/Packets.java'),b('logic/PlayerAttackHelper.java',49,85,108,169,177),b('mixin/PlayerEntityMixin.java',165,189)])
add('BC02',B,'mixin/client/MinecraftClientInject.java',222,
'客户端startUpswing捕获主手stack引用并启动至少1 tick倒数；pre_Tick先检查取消再递减，到0才performAttack，重新取当前攻击手和目标并发C2S。ATTACK_HIT在本地发包后触发，甚至没有命中目标时也会触发。',
'借鉴显式区分起手、等待、取消、发包与权威命中；给方天请求与成功回执不同状态，不把动画/客户端hit事件当作成功证据。',
'客户端预测不提供服务端成功证明。cancelWeaponSwing清stack和使用冷却但未清upswingTicks；静态调用顺序显示取消后仍可能倒数到performAttack，实际效果未运行验证。不能照搬取消语义。',
[b('mixin/client/MinecraftClientInject.java',269,276,286,332,361,430),b('logic/PlayerAttackHelper.java',49)])
add('SP01',S,'blocks/redstone/RedstoneTransceiverBlockEntity.java',84,
'无线红石发送者缓存输入，在serverTick只在改变时emit；接收队列按2*floor距离延迟，tick倒数到0后下一次tick触发。消费者再检查当前接收模式及频道，写功率并通知邻居。',
'借鉴事件携带语义来源信息、投递时复查接收资格；方天同样应在短窗口内重新核对来源/目标/世界，而非要求同一刻。',
'延迟是队列调用次数，不是绝对时刻TTL；没有独立事件ID/UUID。triggerEvent没有重复canAccept的isRemoved检查。通用EventQueue先回调后remove，异常或回调重入会影响一次消费。',
[Q,s('events/listeners/WirelessRedstoneSignalEventQueue.java',18),s('blocks/redstone/RedstoneTransceiverBlockEntity.java',35,76,103),s('blocks/redstone/RedstoneTransceiverBlock.java',79,84,122)])
add('SP02',S,'blocks/energy/CrystalApothecaryBlockEntity.java',254,
'BLOCK_CHANGED事件经BlockPosEventQueue延迟；消费时重新读取事件位置的当前方块，仍为可采晶簇才求掉落、尝试入库。确实使用掉落后移除晶簇，满库存则暂停；setStack解除暂停并扫描现存晶簇。',
'借鉴消费前重查目标当前状态，用实际成功入库结果驱动终结，区分事件出现与可提交结果。方天应保留真实伤害成功位并一次取走。',
'只保存位置，没有方块代次；另一个可采晶簇替换同位置仍能通过。相同位置不同Entry不去重；移除方块仅间接抑制重复。owner是消费时按UUID全服查询，不检查同维度。',
[Q,POS,OWNER,s('blocks/energy/CrystalApothecaryBlockEntity.java',43,51,225,249,313)])
add('SP03',S,'blocks/energy/CrystalApothecaryBlockEntity.java',74,
'独立的卸载补偿路径从NBT LastWorldTime恢复；首次tick在差值>1200时估算未加载期间晶簇产出，然后将补偿标记清为-1。计算扫描当前允许晶簇和库存容量，避免每个后续tick再次补偿同一时间段。',
'借鉴生命周期记录与一次结算标记分开；明确区分正常队列消费、重载恢复、已补偿状态。方天短回执宜明确是否跨卸载保留。',
'这是估算的长时离线产出，不是真实伤害事件或短TTL；使用当前地形估算过去。不能据此为旧回执补造成功结果；与SP02同方块但触发、持久化标记和算法不同，仅建议额外1处。',
[s('blocks/energy/CrystalApothecaryBlockEntity.java',51,164,189,206)])
add('SP04',S,'blocks/chests/BlackHoleChestBlockEntity.java',265,
'黑洞箱使用同一个ItemAndExperience队列族收集实体；每80 tick扫描补发实体事件，距离决定延迟。消费时复查箱体未被阻挡，XP分支检查存活及储存资格后入账并remove；物品分支复查存活、拾取许可和过滤，按实际插入余量修改或discard原物品。',
'借鉴延后消费时再次核验目标有效性，反馈与实际提交量对应；重复到达的引用应因目标已移除或余量为零失效。',
'Item与XP及两种包装只合计1处。捕获实体引用，无UUID/维度快照、无消费时距离复核；队列本身不对同实体的多Entry去重。移除实体和修改余量是业务终结，非显式一次性回执令牌。',
[Q,s('events/listeners/ItemEntityEventQueue.java',18),s('events/listeners/ExperienceOrbEventQueue.java',18),s('events/listeners/ItemAndExperienceEventQueue.java',21,37,50),s('blocks/chests/BlackHoleChestBlockEntity.java',59,66,183,253)])
add('SP05',S,'blocks/deeper_down/HummingstoneBlockEntity.java',33,
'Hummingstone保存GameEvent.Message并按距离延迟，serverTick消费；HUM到达调用startHumming并可再传播，HYMN到达调用onHymn，后者验证当前位置仍为Hummingstone再破坏、掉落共鸣物。入队HUM且队列>20时发出HYMN。',
'借鉴事件类型决定状态转移，消费时检查当前对象；队列积压阈值与终结动作必须分开，不把积压当成功伤害。',
'>20是升级事件条件而非容量上限。Entry不作语义去重，保存来源实体引用，没有短TTL或UUID/维度复核；传播有随机再发，不适合作一次性回执实现。',
[Q,s('blocks/deeper_down/HummingstoneEventQueue.java',19),s('blocks/deeper_down/HummingstoneBlockEntity.java',23,28),s('blocks/deeper_down/HummingstoneBlock.java',78,104,112,120,128,145,164,187)])
add('SP06',S,'blocks/pastel_network/network/PastelTransmission.java',69,
'真实Pastel物品传输从发送库存事务提取，路径长度*vertexTime入SchedulerMap；END_SERVER_TICK经网络manager调用tick倒数。到达时只找当前图中且区块已加载的目标，按实际插入量提交，剩余物品散落并调整underway计数。NBT连同网络UUID、World键及剩余延迟恢复。',
'借鉴任务保存来源上下文、载荷与剩余工作，投递时重新解析目标，并在成功、部分成功、失效三种结局收口；回执消费应先明确唯一提交边界。',
'传输不是伤害回执；长时持久化不能照作短TTL。调度/计数在提取事务commit前发生；SchedulerMap回调后remove，异常不等于可靠一次消费。旧网络并入时该方法未迁移在途队列；World恢复缺少空值处理。',
[s('helpers/SchedulerMap.java',46),s('blocks/pastel_network/network/PastelTransmission.java',25,32,48,65,99,116),s('blocks/pastel_network/network/PastelTransmissionLogic.java',71,113,169),s('blocks/pastel_network/network/ServerPastelNetwork.java',86,268,354,411,416,434),s('blocks/pastel_network/network/ServerPastelNetworkManager.java',64),s('registries/SpectrumEventListeners.java')])
add('SP07',S,'blocks/redstone/RedstoneTimerBlock.java',71,
'定时器调度回调翻转POWERED再预约下一次；玩家修改时clearNextTicks清旧预约，再从当前位置当前方块状态启动新周期。updatePowered用isTicking避免重复预约。',
'借鉴重配置时显式撤销旧任务及防重复预约；方天持有者/武器上下文变化应有明确旧回执失效规则。',
'周期器不是成功回执。scheduledTick用旧state求下一次延迟，不能按直觉当作新状态时长；无UUID、目标或短TTL。各档时间及两种电平合计一处。',
[s('blocks/redstone/RedstoneTimerBlock.java',32,60,84,97)])
add('SP08',S,'blocks/redstone/RedstoneCalculatorBlock.java',67,
'比较当前计算值与缓存输出，只有需要改变且未isTicking时预约2 tick；消费时update重新采集输入并计算，仅当结果改变才更新缓存/邻居。',
'借鉴排队只表达需要复核，提交值在执行时再核验；方天必须明确哪些字段应保持攻击瞬间快照，哪些条件需要消费时复查。',
'这是有意合并输入的红石计算，不能用最新攻击覆盖旧成功回执。算术模式不分别计；onUse切模式调用update时传旧state，存在暂用旧模式的静态风险。',
[s('blocks/redstone/RedstoneCalculatorBlock.java',46,71,94,106)])
add('SP09',S,'blocks/redstone/BlockDetectorBlock.java',44,
'指定朝向邻居与参照方块匹配时schedule2，isQueued限制重复；scheduledTick先触发上升电平再排2 tick下降，替换方块时补邻居通知，onBlockAdded处理已有TRIGGERED状态。',
'借鉴把触发边沿、等待和脉冲终结明确为两阶段，统一处理替换时清理。',
'消费时不复查最初匹配条件，是边沿记录而非当前条件。相同位置同类型替换的实例代次没有记录；不是伤害成功证据。',
[s('blocks/redstone/BlockDetectorBlock.java',17,37,55,78,90)])
add('SP10',S,'blocks/redstone/BlockPlacerBlock.java',108,
'红石上升沿预约4 tick并置TRIGGERED；回调从当前库存选槽，消费时按BE ownerUUID查在线玩家，并经claims许可尝试BlockItem.place，仅isAccepted后处理创造模式的物品递减。',
'借鉴延迟任务执行前重新解析持有者和权限；方天消费须同时核对攻击者快照与目标，而不能仅凭保存的对象引用。',
'未复核仍通电；使用当前库存而非入队快照。tryPlace的放置音效和事件位于try内、但不受place.isAccepted分支保护，不能当成功回执；owner解析不检查同维度。',
[OWNER,s('blocks/redstone/BlockPlacerBlock.java',46,63,96,113,126),s('blocks/redstone/BlockPlacerBlockEntity.java',35,40,46,52)])
add('SP11',S,'blocks/present/PresentBlock.java',141,
'潜行开礼物保存openerUUID并置OPENING、预约20 tick；每次回调递增BE openingTicks，达到6后按当前物品执行拆包行为并移除方块，进度归因通过UUID查当前在线玩家。',
'借鉴多步任务携带行为发起人，并在终结后让对象失效；方天应把发起人快照、进度、已消费标记分开。',
'终结移除后仍无条件scheduleBlockTick，依赖游戏方块调度规则避免再回调；无独立任务代次。重复使用可覆盖opener；UUID全服解析不校验维度。所有拆包物品行为不额外计数。',
[OWNER,s('blocks/present/PresentBlock.java',101,171),s('blocks/present/PresentBlockEntity.java',49,68,85,103,126)])
add('SP12',S,'blocks/decoration/EtherealPlatformBlock.java',51,
'踩踏把本格age设5，邻格age4并预约2 tick；回调先沿EXTEND传播并清该位，再以10/4 tick逐步衰减age。传播仅当新age严格大于邻格已有age才改写和预约。',
'借鉴状态版本/单调推进条件抑制旧任务反复传播；短回执也应有明确可消费状态和终结状态。',
'age是阶段值，不能当worldTime TTL；以位置/方块类型为身份，无攻击来源或成功位。不同邻方向、age及EXTEND状态仅合计一处。',
[s('blocks/decoration/EtherealPlatformBlock.java',35,80)])
add('SP13',S,'blocks/decay/DecayAwayBlock.java',40,
'放置后4 tick启动清除波，扫描可治愈或可移除的相邻衰变方块，转成清除波并预约8 tick；自身最后转换为按当前世界维度效果选择的正常方块。',
'借鉴执行时读取实际世界上下文，先传播任务再终结当前任务对象；维度相关行为不可只保存裸坐标。',
'这是方块清理调度，没有实体UUID或短TTL。维度效果决定替换产物，不等于生产维度与消费维度一致性校验；不同维度产物与转换表不单独计。',
[s('blocks/decay/DecayAwayBlock.java',27,61,103)])
add('SP14',S,'blocks/boom/ThreatConfluxBlock.java',127,
'放置50 tick后从NOT_ARMED变ARMED；实体接触改FUSED并预约20 tick；FUSED回调取当前BE物品与在线owner，先removeBlock再执行ModularExplosion。手持芯片可把状态改NOT_ARMED。',
'借鉴消费时核对阶段并先封闭可重入的任务载体；方天应先原子取走合格回执，再做二次横扫与反馈。',
'拆除状态不取消旧预约，因此旧回调可再次把NOT_ARMED武装；没有任务generation。爆炸内部部分声效在damage前，不能当成功伤害；owner无同维度复核。',
[OWNER,s('blocks/PlacedItemBlockEntity.java',29,36,48,53,58),s('blocks/boom/ThreatConfluxBlock.java',72,98,108,145),s('explosion/ModularExplosionDefinition.java',152),s('explosion/ModularExplosion.java',31)])
add('SP15',S,'blocks/CrackedEndPortalFrameBlock.java',221,
'含爆炸属性的裂隙末地框架放入时预约40 tick；回调重新读取当前eye.hasExplosions，按随机结果爆炸/拆传送门/破框架或冒烟，之后仍预约10 tick。',
'借鉴消费前复核当前载荷资格，并区分终结、继续与失效；移除资格后应考虑取消后续预约。',
'不满足hasExplosions时也会继续预约；没有显式清队列或TTL。终结后仍排队，依赖方块类型的调度保护。概率分支不是独立实现。',
[s('blocks/CrackedEndPortalFrameBlock.java',66,202)])
add('SP16',S,'blocks/chests/HeartboundChestBlockEntity.java',151,
'非owner开箱时按player UUID确认身份，并记录world.getTime；告警在后续scheduled tick继续更新，lastAccess>0且lastAccess+20>now时保持15信号。它允许正常时间前进时跨tick消费有效窗口。',
'直接借鉴年龄窗口取代r.tick==now，但方天应加入0<=now-producedTick的下界，并明确最大允许年龄和一次消费。',
'正常时间下覆盖年龄0..19，不是恰好20；tick0被>0哨兵排除，时间倒退会误当有效。NBT保存时间却不保存维度。持续告警可多次查询，不能冒充一次消费回执。',
[s('blocks/chests/HeartboundChestBlockEntity.java',51,80,86,108,139),s('blocks/chests/HeartboundChestBlock.java',33,50,73,88),s('blocks/chests/SpectrumChestBlock.java',95),s('blocks/chests/SpectrumChestBlockEntity.java',137)])
add('SP17',S,'blocks/idols/IdolBlock.java',106,
'Idol在使用、踩踏或投射物命中入口检查!COOLDOWN且trigger返回true，才设冷却并schedule40；回调清COOLDOWN。以具体FirestarterIdol为真实玩法落点，trigger扫描六面尝试点火。',
'借鉴先判断业务结果再推进短时状态，并集中到单一入口封闭重复触发；方天仍须以真实伤害成功为准。',
'Firestarter.trigger最终无条件true，因此冷却/反馈并不证明点火成功；这只是计划与重入抑制。所有Idol子类/触发入口不重复计数。',
[s('blocks/idols/IdolBlock.java',48,63,69,81),s('blocks/idols/FirestarterIdolBlock.java',65,97)])
add('SP18',S,'blocks/block_flooder/BlockFlooderBlock.java',158,
'扩散方块的第一阶段根据ownerUUID查询玩家、权限、半径和库存来计算targetBlockState并缓存，随机2..6 tick后第二阶段替换目标并从owner库存扣物品；新邻任务继承source和ownerUUID。',
'借鉴多阶段任务显式保存来源UUID/原点，识别计划和提交之间需要再次校验的条件。',
'最终阶段先改世界，再取owner且未判空，未重查权限和库存；owner下线可能导致部分提交。targetBlockState不写入NBT，重载会重新计算。是反例，不可照搬为可靠交易或成功回执。',
[s('blocks/block_flooder/BlockFlooderBlock.java',53,72,184),s('blocks/block_flooder/BlockFlooderBlockEntity.java',41,51,63,74,78)])
add('SP19',S,'cca/MiscPlayerDataComponent.java',205,
'SoothingBouquet消费设置等待50、睡眠窗口120和来源SleepAlteringItem；玩家tick递减，到等待0才调用sleep，窗口0时failSleep。reset先清三个计数再可选处罚；玩家damage入口notifyHit可提前中断。组件注册NEVER_COPY。',
'借鉴显式等待/执行窗口/取消三段生命周期，失效先清状态再副作用；玩家重生应有清理策略。',
'damage注入位于调用damage入口而非成功返回，amount>0不等于实际伤害。sleep调用结果未检查；同tick可递减窗口，数字不等于精确墙钟TTL。来源Optional在处罚后清，异常有残留风险。',
[CCA,s('items/tools/SoothingBouquetItem.java',34,55,76),s('cca/MiscPlayerDataComponent.java',59,65,233,248,254,268,274,279,291),s('mixin/PlayerEntityMixin.java',76)])
add('SP20',S,'cca/MiscPlayerDataComponent.java',166,
'格挡damage修改钩子识别ParryingSword使用时长；bluff设15 tick反击窗口，perfect另置布尔令牌。后续attack钩子consumePerfectCounter先清布尔再给伤害乘1.5；倒数到1的tick清窗口并消费残余令牌。以LightGreatsword为具体落点。',
'借鉴成功资格与一次性消费分开、返回令牌前清除状态；短窗口配合明确的来源/武器/目标绑定更适合方天。',
'布尔令牌没有目标UUID、武器代次、维度或产生刻。hasForcedCrits会把parryTicks直接清0，此路径不触发倒数到1清理；是否所有中断路径均消费需运行验证。格挡钩子不是攻击成功回执。',
[CCA,s('cca/MiscPlayerDataComponent.java',158,162,175,179),s('mixin/LivingEntityMixin.java',304,324,335),s('mixin/PlayerEntityMixin.java',133,147,155),s('items/tools/ParryingSwordItem.java',53,64,69,77,83,87,91),s('items/tools/LightGreatswordItem.java',26)])
add('SP21',S,'status_effects/FrenzyStatusEffect.java',53,
'击杀钩子把worldTime记到LastKill组件并调用Frenzy.onKill；持续效果消费该时间，lastKill>=0且diff<200视为近期击杀，离开窗口且diff%200==0时衰减属性。固定属性UUID替换旧modifier；玩家组件NEVER_COPY。',
'借鉴记录业务事件的产生刻、后续在窗口内查询；方天需要再加年龄非负与一次消费，而不是照搬整除周期。',
'缺少diff>=0，时间倒退可能被接受；衰减命中整除刻，跳过该刻不会补做。记录的是onKilledOther入口，不是普通伤害成功。实体与玩家的两个钩子仅作同链辅助，不双计。',
[CCA,s('cca/LastKillComponent.java',26,33,39,44),s('mixin/EntityMixin.java',26),s('mixin/PlayerEntityMixin.java',65),s('status_effects/FrenzyStatusEffect.java',69,73,91)])
add('SP22',S,'entity/entity/LightShardBaseEntity.java',69,
'GlassAmpoule真实使用召唤LightShard：先25 age减速阶段再追踪；目标缓存实体与UUID，选目标要求同world、视线/距离，isValidTarget排owner/队友并检查存活移除等。age>maxAge时discard，碰撞再次验证目标后攻击并移除。',
'借鉴延迟后重新校验目标存活/身份和世界边界，并给任务有限寿命；方天应持久保存目标UUID和维度并重新解析。',
'已缓存目标的isValidTarget没有同world检查；UUID写NBT但read后没有按UUID恢复targetEntity，可能重新选目标。discard后tick未立即return；damage返回值被忽略且声效无条件，不能当成功回执。LightMine等派生不额外计。',
[s('entity/entity/LightShardBaseEntity.java',45,130,143,155,183,201,236,285,291,304),s('entity/entity/LightShardEntity.java',26,32,36),s('items/magic_items/ampoules/BaseGlassAmpouleItem.java',18,31),s('items/magic_items/ampoules/GlassAmpouleItem.java',24)])
add('SP23',S,'entity/entity/InkProjectileEntity.java',122,
'Paintbrush付墨后服务端spawn带owner的投射物；MagicProjectile在后续tick查询碰撞，过滤PVP资格并有age>=200丢弃。Ink实体命中只有damage返回true才触发附魔回调、onHit和击中玩家包，失败则反弹并在极慢时discard。',
'借鉴真实damage结果控制后继反馈，失败保留/终结分支明确；成功回执生产位置应位于权威damage结果之后。',
'不是END回执队列，无持有者/目标UUID快照。染色发生在damage前，不是伤害成功反馈；onHit内和调用者都discard，不能把两次discard当两次消费。MagicProjectile还手动递增age，200是字段阈值并非保证200实际tick。',
[s('entity/entity/InkProjectileEntity.java',57,179,219,265),s('entity/entity/MagicProjectileEntity.java',33,109,130),s('items/magic_items/PaintbrushItem.java',197)])
add('SP24',S,'entity/entity/DraconicTwinswordEntity.java',448,
'抛掷双剑在物品NBT保存投射物UUID并预留槽；后续交互只允许owner，按UUID从该玩家库存找回原stack，解除预留再discard。remove也按同UUID尝试解除预留；穿透集合限制同一实体重复进入命中流程。',
'借鉴将异步任务绑定明确源物品/任务UUID，消费或销毁时清预留；方天回执应有来源动作标识并只允许一次结算。',
'findThrownStack只检查NBT UUID，不检查物品类型；物品被移出owner库存时无法解除。无短TTL，age方法为空；实体引用集合未持久化。onEntityHit的声效/穿透推进在damage成功分支之外，不能作为真实伤害回执。',
[s('items/tools/DraconicTwinswordItem.java',52,76,182,187,191),s('entity/entity/DraconicTwinswordEntity.java',60,168,297,349,386,429),s('entity/entity/BidentBaseEntity.java',29,41,45,50)])
add('SP25',S,'blocks/decay/DecayBlock.java',127,
'邻方块变动且可转换时对本格预约40..239 tick低优先级任务；消费时randomTick与trySpreadToRandomNeighboringBlock重新读取邻格、claims、硬度和转换资格，setBlockState实际成功才播放放置音。以FadingBlock为具体转换玩法。',
'借鉴入队筛选与消费时再次校验分离，以及以实际状态变更结果决定反馈；方天成功位不能在入队阶段预判。',
'本格调度并不绑定最初触发的邻格，执行可能随机影响其他方向；没有目标UUID或短TTL。衰变种类和转换表仅算同族一处。',
[s('blocks/decay/DecayBlock.java',94,110,135,146,157),s('blocks/decay/FadingBlock.java',18,39)])
add('SP26',S,'blocks/lava_sponge/WetLavaSpongeBlock.java',28,
'湿熔岩海绵在添加时启动按ultrawarm维度决定的随机延迟；scheduledTick先预约下一次，再检查DO_FIRE_TICK并对可放火的当前目标尝试点火。',
'借鉴持续任务的维度上下文与终止条件必须显式设计；回执不应采用无上限自预约。',
'普通环境点火周期与短回执关联弱，列辅助零信用；关闭DO_FIRE_TICK仍保留预约。不是来源/目标身份校验，维度参数只用于频率。',
[s('blocks/lava_sponge/WetLavaSpongeBlock.java',19,44)],decision='auxiliary_zero_credit')
# Honest exclusions: not used to inflate independent implementation count.
add('AX01',B,'client/ClientNetwork.java',15,'S2C动画通过client.execute按当前client.world数字实体ID寻找玩家，执行stop/start动画；声音也延后到client线程。','用于区分视觉投递与权威成功回执，相关包只能作辅助观察。','纯动画/声效，非独立战斗回执玩法；无UUID/维度/TTL，零信用。',[b('mixin/client/AbstractClientPlayerEntityMixin.java',124,293)],decision='auxiliary_zero_credit')
add('AX02',S,'events/listeners/EventQueue.java',25,'通用队列复制keyset后递减，delay=0时回调然后remove。','SP01/02/04/05的共享调度上下文；注意delay+1与回调重入边界。','没有独立玩法，且已作为具体消费者链辅助，不能再单计。',[Q,POS],decision='excluded_shared_chain')
add('AX03',S,'helpers/SchedulerMap.java',46,'通用倒数调度器对Freezable条件跳过，回调后iterator.remove。','仅以SP06真实Pastel载荷证明相关性。','通用调度器不能独立新增credit，与SP06同链。',decision='excluded_shared_chain')
add('AX04',S,'blocks/redstone/RedstoneGravityBlock.java',43,'回调检查UNSTABLE并传播或坠落；propagate改邻格但schedule的位置是当前pos。','提示调度位置与更新位置须逐项核对。','本次未追全vanilla FallingBlock的生产/调度入口；不把局部方法当已完成独立链。',decision='excluded_incomplete_chain')
add('AX05',S,'blocks/redstone/DetectorBlock.java',83,'抽象Detector定期调用updateState再预约下一次。','候选入口；需要具体子类的完整生产及状态提交链。','本次没有完成具体updateState实现审查；抽象模板零信用。',decision='excluded_incomplete_chain')
add('AX06',S,'blocks/jade_vines/JadeVineBulbBlock.java',44,'邻更新发现支撑无效预约1 tick，消费时再次canPlaceAt，不可放才break。','可作延迟重检的普通示例。','与普通植物支撑坍塌模板高度同构，未作跨主账语义去重；保守零信用。',[s('blocks/jade_vines/JadeVineBulbBlock.java',36,66)],decision='excluded_template')
add('AX07',S,'items/trinkets/AshenCircletItem.java',34,'物品NBT记录lastStart，max(0,lastStart-now+3000)作为冷却；授予抗火后设置时间。','可对照长冷却与事件有效期的区别。','普通长冷却不当短回执研究credit；未追全PrimordialFire组件调用链。',[s('items/trinkets/AshenCircletItem.java',44,50,59)],decision='auxiliary_zero_credit')
add('AX08',S,'cca/azure_dike/DefaultAzureDikeComponent.java',110,'护盾吸收时重置recharge delay，serverTick倒数到0才补充并同步；组件可NBT保存和重生复制。','仅作战斗后延迟恢复的候选对照。','普通充能冷却，未完成装备配置/伤害混入调用链，因此零信用。',[s('cca/azure_dike/DefaultAzureDikeComponent.java',55,75,90,100,124)],decision='excluded_incomplete_chain')
add('AX09',S,'entity/entity/LightMineEntity.java',110,'LightMine复用LightShardBase的age和target生命周期，再增加地雷行为。','与SP22归于同一基础追踪/TTL链。','派生物不因名称/伤害载荷变化新增credit；独立地雷状态链未另作完整审查。',decision='excluded_shared_chain')
add('AX10',S,'items/tools/NightfallsBladeItem.java',72,'postHit立即处理状态效果；其它时间字段用于效果表现。','关键词命中不等于回执队列。','没有该方法的延后消费/调度生命周期，排除。',decision='excluded_out_of_scope')

add('SP27',S,'entity/entity/PreservationTurretEntity.java',531,
'炮塔通过实体GameEventHandler和Vibrations.Ticker接收延后振动；accepts检查炮塔存活、AI启用、同world、边界及来源目标资格。accept到达后把来源设为target并开启炮塔；攻击Goal等待openProgress==1，后续每次攻击又检查target和canSee，后者包含同world、距离和射线条件。',
'借鉴从事件候选到延后目标再到执行的多层复核，尤其世界一致性应在执行时再次检查；方天回执可以允许跨刻，但不能放宽身份/维度条件。',
'底层振动排程属于vanilla API，未下载其实现，不声称已审查底层精确时延。accept没有重复全部accepts资格；射击damage返回值被忽略、两处音效无条件，不能作为成功回执。振动listener持久化代码被注释；事件感知与Goal仅合计1条。',
[s('entity/entity/PreservationTurretEntity.java',70,118,128,158,176,182,377,399,453,471,476,481,520)])
add('SP28',S,'entity/entity/FloatBlockEntity.java',319,
'FloatBlock在放置/邻更新后排2 tick，执行时检查重力方向是否可通行才spawn实体；实体首tick尝试移除原格，后续碰撞尝试放回方块。放不下时dropAsItem先检查isRemoved再discard，再掉落和反馈，形成终结时的一次性保护。',
'借鉴终结副作用前先把任务标记为已移除，以阻止重复掉落；消费时检查当前位置可替换和可放置，区分任务创建与真正提交。',
'首tick原格不匹配时实际未按注释discard；同方块类型替换不能区分代次。tick未调用super.tick也未递增age，age>100超高界清理不能直接当可靠TTL。不是实体攻击回执；未将其伤害/AnvilCrusher子链另计。',
[s('blocks/gravity/FloatBlock.java',24,29,35,39,59),s('entity/entity/FloatBlockEntity.java',53,70,104,161,211,221,245)])
add('AX11',S,'helpers/BuildingHelper.java',69,'Queue仅用于同一次调用中的BFS连接方块搜索，visitedPositions防重复。','作为关键词误报记录，不能把Queue出现当跨tick任务。','即时算法，无延后消费/TTL生命周期；零信用。',decision='excluded_out_of_scope')
add('AX12',S,'blocks/lava_sponge/LavaSpongeBlock.java',28,'熔岩吸收使用BFS queue，在单次update里移除流体，深度和数量限制循环。','区分同步工作队列与跨tick回执队列。','同步遍历而非延后任务；不因队列数据结构新增credit。',[s('blocks/lava_sponge/LavaSpongeBlock.java',21)],decision='excluded_out_of_scope')
add('AX13',S,'entity/entity/MiningProjectileEntity.java',71,'投射物保存stack.copy，在方块命中时执行挖掘并discard，继承MagicProjectile的寿命。','SP23共享投射物基类的派生候选。','AoEHelper与MoonstoneStrike实际执行链未追全；共享TTL包装不可重计。',[s('entity/entity/MiningProjectileEntity.java',39,64)],decision='excluded_incomplete_chain')
add('AX14',S,'entity/entity/BidentMirrorImageEntity.java',59,'镜像戟碰撞后调用LightShardEntity.summonBarrage。','记录SP22的上游入口，不重复计算追踪和寿命。','派生调用包装，不是新的LightShard生命周期；零信用。',[s('entity/entity/BidentMirrorImageEntity.java',35,48),s('entity/entity/LightSpearEntity.java',27,38)],decision='excluded_shared_chain')
add('AX15',S,'cca/OnPrimordialFireComponent.java',108,'燃烧组件保存剩余ticks，serverTick伤害并扣除1或水中3；putOut清零并同步。','可辅助区分持续伤害状态与一次成功伤害回执。','持续状态效果不当一次消费队列计数；KindlingCough完整生产者入口未追全，未额外计。',[s('cca/OnPrimordialFireComponent.java',62,69,77,83,97),s('entity/entity/KindlingCoughEntity.java',25,32,56,72)],decision='excluded_incomplete_chain')

def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(repo,path):
    p=ROOT/M[repo]['source_root']/path
    raw=p.read_bytes()
    expected=next(v['sha256'] for v in M[repo]['files'] if v['path']==path)
    assert sha(raw)==expected,(repo,path)
    return p,raw,raw.decode().splitlines(keepends=True)
# Ignore Java comments/strings while finding a method's balanced closing brace.
def method_end(lines,start):
    text=''.join(lines[start-1:]); mode='code'; depth=0; begun=False; i=0; line=start
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ''
        if mode=='line':
            if c=='\n':mode='code'
        elif mode=='block':
            if c=='*' and n=='/':mode='code';i+=1
        elif mode in ('string','char'):
            if c=='\\':i+=1
            elif c==('"' if mode=='string' else "'"):mode='code'
        else:
            if c=='/' and n=='/': mode='line';i+=1
            elif c=='/' and n=='*': mode='block';i+=1
            elif c=='"':mode='string'
            elif c=="'":mode='char'
            elif c=='{':depth+=1;begun=True
            elif c=='}':
                depth-=1
                if begun and depth==0:return line
        if c=='\n':line+=1
        i+=1
    raise AssertionError(('unterminated',start))

def evidence(repo,path,start=None):
    p,raw,lines=read(repo,path)
    a=start or 1; z=method_end(lines,a) if start else len(lines)
    if start:
        assert re.search(r'\b(public|protected|private|default|static)\b',lines[a-1]),(path,a,lines[a-1])
        assert '(' in lines[a-1],(path,a,lines[a-1])
    excerpt=''.join(lines[a-1:z])
    return dict(repo=repo,revision=M[repo]['revision'],path=path,source_local=str(p.relative_to(ROOT)),source_sha256=sha(raw),line=a,end_line=z,excerpt=excerpt,snippet_sha256=sha(excerpt.encode()),url=f"https://github.com/{repo}/blob/{M[repo]['revision']}/{path}#L{a}-L{z}",scope='complete_method' if start else 'whole_file_context_zero_credit',method_signature=lines[a-1].strip() if start else None,preceding_context=(dict(line=max(1,a-12),end_line=a-1,excerpt=''.join(lines[max(0,a-13):a-1])) if start and a>1 else None))
contexts={}; rows=[]
for spec in specs:
    row=evidence(spec['repo'],spec['path'],spec['line'])
    row.update(candidate_id='combat-spectrum-'+spec['key'].lower(),helper_id=spec['key'],status='helper_reviewed_pending_coordinator',decision=spec['decision'],observation=spec['observation'],application=spec['application'],limits=spec['limits'],independent_chain_key=spec['chain'],proposed_credit=int(spec['decision']=='proposed_eligible'),master_credit=0,credit=0,source_root=M[spec['repo']]['source_root'],source_metadata=str((OUT/'source-manifest.json').relative_to(ROOT)),external_runtime_tested=False,upstream_code_executed=False,review_basis='人工静态阅读全文方法/指定调用链；摘录与SHA由本地自编脚本组装，不代表运行验证。',support_evidence=[])
    for repo,path,starts in spec['support_specs']:
        for start in starts or [None]:
            ident=f"{repo}:{path}:{start or 'full'}"
            if ident not in contexts:contexts[ident]=evidence(repo,path,start)
            row['support_evidence'].append(ident)
    row['structural_fingerprint']=sha(re.sub(r'\s+','',row['excerpt']).encode())
    rows.append(row)
assert len({r['candidate_id'] for r in rows})==len(rows)
assert len({r['independent_chain_key'] for r in rows if r['proposed_credit']})==sum(r['proposed_credit'] for r in rows)
# Ledger scan is read-only and does not promote any helper row to accepted.
ledger_audit=[]
for name in ['protocol.json','accepted.jsonl','reviewed.jsonl','candidates.jsonl','progress.json']:
    p=OUT.parents[1]/name
    raw=p.read_bytes(); matches=[]
    if name.endswith('jsonl'):
        for n,line in enumerate(raw.decode().splitlines(),1):
            if not line.strip():continue
            obj=json.loads(line)
            if obj.get('repo') in (B,S):matches.append(dict(line=n,candidate_id=obj.get('candidate_id'),repo=obj.get('repo'),path=obj.get('path'),revision=obj.get('revision')))
    ledger_audit.append(dict(path=str(p.relative_to(ROOT)),sha256_at_scan=sha(raw),same_repo_rows=matches,read_only=True))
meta=dict(helper='combat-spectrum',target_independent_implementations=80,reviewed_proposed_eligible=sum(r['proposed_credit'] for r in rows),gap_to_80=80-sum(r['proposed_credit'] for r in rows),master_credit_added=0,final_count_owner='Carson',completed_required_1000=False,official_repositories_confirmed=[dict(repo=x['repo'],url=x['official_url'],revision=x['revision'],fork=x['fork']) for x in manifest],upstream_code_executed=False,game_started=False,server_started=False,build_started=False,production_modified=False,ledger_write=False,reviewed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),count_rule='仅每个独立玩法链建议1；同链包装、分支、变种、通用工具、未完成链和未读候选为0。Carson须最终跨仓语义去重。',ledger_read_snapshot=ledger_audit)
for name,obj in [('batch-001.json',dict(metadata=meta,records=[r for r in rows if r['proposed_credit']])),('reviewed-zero-credit.json',dict(metadata=meta,records=[r for r in rows if not r['proposed_credit']])),('evidence-contexts.json',dict(evidence=contexts)),('verification.json',dict(metadata=meta,records_checked=len(rows),support_excerpts_checked=len(contexts),all_manifest_hashes_match=True,exact_source_excerpts=True))]:
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(proposed=meta['reviewed_proposed_eligible'],gap=meta['gap_to_80'],zero_credit=len(rows)-meta['reviewed_proposed_eligible'],contexts=len(contexts)),ensure_ascii=False))
