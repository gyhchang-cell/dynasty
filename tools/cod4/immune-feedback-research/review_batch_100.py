"""Three native Lycanites control policies; no per-effect/packet wrapper credits."""
from ledger import B,O,record,verify
import json
r='Lycanite/LycanitesMobs';p='src/main/java/com/lycanitesmobs/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def resource(s):
 t='src/main/resources/assets/'+s
 return t,1,len((B/'sources'/r.replace('/','__')/t).read_text().splitlines())
common=[f('core/info/CreatureInfo.java',139,326)]
k='lycanites-native-mounted-rider-inherits-final-effect-denials-via-tick-cleanse'
record(k,r,[w('core/entity/EntityCreatureRideable.java'),w('freshwatermobs/entity/EntityIoray.java'),w('core/info/ElementInfo.java'),f('core/entity/EntityCreatureBase.java',2926,2948),f('core/entity/EntityCreatureBase.java',3751,3760),resource('freshwatermobs/creatures/ioray.json'),resource('lycanitesmobs/elements/acid.json')]+common,
 '实际ioray JSON class/mountable及CreatureInfo反射注册、acid element数据核对。原生Rideable.onLivingUpdate先super，控制乘客存在且活体→riderEffects；再复制骑手activeEffects数组逐个用坐骑this.isPotionApplicable判定，坐骑拒绝的效果从骑手移除。Base.isPotionApplicable遍历元素，ElementInfo拒本元素debuff/immunities中的registryId。Ioray专门riderEffects续水肺105ticks并清paralysis/penetration；酸元素debuff也含penetration。下骑onDismounted仅续水肺100ticks，不保留清负面租期。',
 '计1：坐骑免疫策略投射给另一实体骑手的持续净化，区别直接装备tag admission、单体自清或Fear强制载具租期。复制array避免遍历中删除；active effect可能先应用再被下一tick清，不能声称施加时拒绝或全程零影响。此段未限制server-only，两端调用可能不同步；hasRiderTarget client读TARGET bit/server读实际乘客。riderEffects与通用净化同链只计1，两个效果名和水肺常量均0。',
 'Boss“此次控制未生效”需要最终施加前拒绝，不能将事后净化复用成拒控灰字理由；普通玩家骑乘净化不增加灰字要求。',
 'Rideable/Ioray/ElementInfo全文及实际注册解析完整关键方法已读。注册配置及原生tick链静态核对，不声称native加载运行、两端截图或水肺观感。','native_cross_entity_control_immunity_projection')
k2='lycanites-native-melee-temporary-knockback-resistance-restore-skipped-on-failed-hit'
record(k2,r,[w('shadowmobs/entity/EntityWraamon.java'),w('core/entity/ai/EntityAIAttackMelee.java'),f('core/entity/EntityCreatureBase.java',2532,2556),f('core/entity/EntityCreatureBase.java',2671,2727),resource('shadowmobs/creatures/wraamon.json')]+common,
 '实际wraamon JSON→反射注册，initEntityAI装原生meleeGoal。Goal.updateTask范围/攻击冷却触发host.attackMelee。Wraamon先保存目标KNOCKBACK_RESISTANCE.getAttributeValue()并setBaseValue(1)，再super.attackMelee；父方法挡格不可攻击或attackEntityAsMob失败立即false。只有父返回true才恢复target baseValue为保存值；attackEntityAsMob有alive/target/LOS gate，穿透与普通伤害分段且返回第二段结果。',
 '计1：一次攻击期间目标属性临时拒击退及恢复条件的独立结算位点，区别Goety单次event stamp清除。父false时无finally，目标baseValue可残留1；保存的是总attributeValue而恢复到base，并非原base，带modifier时亦非精确回滚。穿透首段可能已成功而第二段false，不能据最终false认定完全未受伤或Boss免控；未实机验证该源缺陷。粒子/伤害段/Goal包装不另计。',
 '避免用临时改目标属性模拟Boss免控；拒绝反馈只由明确控制准入产生。若必须临时修改，保存原base并覆盖所有返回路径恢复，不能用hurt布尔决定清理。',
 '完整Wraamon、meleeGoal、父attackMelee及attackEntityAsMob已读；CreatureInfo完整注册方法复用。原版属性聚合/目标hurt内部依赖未独立计数；无正式修改。','native_scoped_knockback_rejection_cleanup')
k3='lycanites-native-instability-final-boss-exclusion-and-independent-client-impulse'
record(k3,r,[w('PotionEffects.java'),w('core/network/MessageEntityVelocity.java'),w('core/network/PacketHandler.java'),w('shadowmobs/entity/EntityWraamon.java'),w('core/info/ElementInfo.java'),f('core/entity/EntityCreatureBase.java',2532,2556),f('core/entity/EntityCreatureBase.java',3323,3327),f('LycanitesMobs.java',145,177),resource('shadowmobs/creatures/wraamon.json'),resource('lycanitesmobs/elements/chaos.json')]+common,
 '原生wraamon chaos元素成功melee→Base.applyDebuffs→ElementInfo.debuffEntity加instability，实际Potion注册与LivingUpdate bus。执行时server且非IGroupBoss、非creative/spectator、活动instability、10%随机才实际加三轴随机速度。玩家先发原版SPacketEntityVelocity当前速度，再另取三次随机值构造自定义MessageEntityVelocity，仅发该玩家；收包按当前世界entityID解析后motion +=短整型/8000。',
 '计1：最终控制执行处Boss排除与原生玩家额外冲量交付完整一链，不按序列化、clamp轴、random常量拆数。客户端额外三轴冲量与server使用不同随机采样，不能把双包当同一向量精确同步。构造每轴clamp±3.9/量化short；onMessage未enqueue、无player/world/entity null检查、无UUID维度/事件去重。Boss可能持有effect但此执行完全跳过，无明确免控文字或拒绝包；不把伤害拒绝和移动拒绝等同。',
 'Boss拒控应在最终执行门发送明确语义，效果存在不代表控制有效；S2C必须携带同一次服务端决定而非客户端重新随机决定，校验当前维度/目标身份并在客户端线程提交。普通体质不新增文字。',
 'PotionEffects及MessageEntityVelocity/PacketHandler全文已读，Wraamon原生能力和JSON关系已核。vanilla SPacket内部不扩计；没有截图或网络实测，不声称上游实际崩溃或错位已复现。','native_final_control_refusal_and_motion_receipt')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'lycanites-batch100-cross-rider-cleanse-scoped-knockback-final-instability','credited_chains':[k,k2,k3],'rationale':'Cross-entity immunity projection via post-admission cleanse; one-hit temporary attribute mutation and all-return cleanup; final Boss-control skip plus native motion receipt are separate policies. Within each whole producer/consumer chain wrappers, statuses and entity skins are zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
