"""Pinned full native game methods: conservative affix family and Boss decisions."""
from ledger import B,O,record,verify
import json
keys=[]
def w(r,f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
def add(k,r,refs,c,o,l):
 for f,a,z in refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
 record(k,r,refs,c,o,l,'本地固定Git tree/blob源+SHA；完整关键方法逐段观察，仅静态不证明画面/声音/TCP，不改正式Java/资产/TODO、不启游戏。通用框架、同链wrapper、实体/来源常量变体0额外，普通阴阳无灰字要求。','native_control_damage_arbitration');keys.append(k)
r='Shadows-of-Fire/Apotheosis';p='src/main/java/dev/shadowsoffire/apotheosis/'
add('apotheosis-native-equipped-affix-source-reduction-not-immune',r,[(p+'Apotheosis.java',174,178),(p+'AdventureEvents.java',173,194),(p+'affix/AffixHelper.java',136,172),(p+'affix/AffixInstance.java',45,69),(p+'affix/AffixInstance.java',178,180),w(r,p+'affix/effect/DamageReductionAffix.java'),(p+'affix/Affix.java',229,231),(p+'data/AffixProvider.java',515,572),(p+'data/AffixProvider.java',1008,1012)],
 '实际AdventureEvents注册→原生LivingIncomingDamage LOW先应用entity attachment reductions，随后所有EquipmentSlot逐个gems+affixes→AffixHelper读取真实AFFIXES/RARITY组件并验证bound/canApplyTo→AffixInstance派发DamageReductionAffix完整onHurt；实际datagen六种装备词缀定义值范围和类目→source既非BYPASS_INVULNERABILITY亦非BYPASS_ENCHANTMENTS且匹配type才amount*(1-level)，else基类原样返回。',
 '一个装备词缀来源匹配减伤门1，不把physical/magic/explosion/fall/projectile/lightning或稀有度变体拆数。默认生成值都<1，复合乘法仍不构成Boss拒控，不能以说明tooltip灰色误当受击灰字。外部physical predicate/StepFunction和CachedObjectSource内部不在本条独立计数；reload注释说明cached可能unbound，native onDamage用getAffixes.values没有streamAffixes额外isValid过滤，不保证所有reload顺序安全。没有取消事件/明确拒控或声光S2C。datagen定义是实际Java配置，未取得原始生成JSON/启动证明，不冒称运行已载入。',
 'Boss语义必须独立于部分减伤；灰字生产不能简单套所有0伤或装备防御分支。')
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';v=p+'common/entities/boss/Vizier.java';s=p+'common/entities/hostile/SkullLord.java'
add('goety-vizier-native-intro-and-post-hit-window-final-refusal',r,[(p+'common/entities/ModEntityType.java',1517,1520),(p+'common/items/ModItems.java',114,114),w(r,p+'common/items/DarkScrollItem.java'),(v,80,115),(v,115,281),(v,365,372),(v,447,473),(v,543,598),(v,609,638),(v,642,645),(v,738,751),w(r,p+'client/render/VizierRenderer.java'),w(r,p+'client/render/layer/VizierAuraLayer.java'),(p+'init/ClientInitEvents.java',762,762)],
 '真实DarkScroll.finishUsingItem server结构检查→创建已注册Vizier/finalize/makeInvulnerable40→真实entity tick递减CONFUSED；native hurt intro>0(除FELL_OUT_OF_WORLD)/moddedInvul>0/己方Irk源拒绝；actuallyHurt cap后调用super并有来源entity才设BossInvulnerabilityTime；真实tick递减，NBT存取；intro时原生entityEvent5、客户端handle再递减。',
 '以Vizier native final gate+窗口寿命/回放整链1，intro/来源常量/半伤/cap不拆。intro可放行FELL_OUT_OF_WORLD但后面的moddedInvul不含此例外；spellcasting只减半不是免疫。hurt在拒绝后才可能召minion，但调用super仍可能false。原生tick客户端也递减CONFUSED，event5再次减，且还有entityData INT同步，静态只指出存在多更新来源，不推断实机漂移数。30/10tick混乱/愤怒声粒子是intro，不是每次拒伤回执。isPowered仅spellcasting→aura，不等于intro拒绝态或moddedInvul；不能用护罩存在声称免疫显示对应。BossBar intro隐藏，无gray文字，AI正常其余tick仍运行。',
 '窗口权威与显示时钟分离；声光应由实际Boss控制拒绝语义生产，不能从intro/施法护罩猜。')
add('goety-skulllord-native-live-partner-immunity-and-link-feedback',r,[(p+'common/entities/ModEntityType.java',1548,1556),(s,137,144),(s,220,398),(s,400,426),(s,579,601),(s,611,642),(s,652,658),(s,773,800),(s,510,537),(p+'utils/EntityFinder.java',81,102),w(r,p+'client/render/SkullLordRenderer.java'),(p+'init/ClientInitEvents.java',768,768)],
 '真实SkullLord finalizeSpawn创建BoneLord并绑定UUID+clientId→server native tick存活partner则FLAGS invulnerable true/event4，缺失或dead则false/event5并再生预算；原生hurt先读isInvulnerable直接false，否则计hitTimes再super；真实renderer按旗标选脆弱/普通texture并按两实体插值位置绘制连接四边形。',
 '独立由活体partner生命周期决定的最终Boss拒伤1，flag setter/event wrapper/纹理/连接几何0额外。server EntityFinder跨server levels查UUID，client只本level intid+BoneLord类型，不核对同步UUID；未证实跨维度正确锚定/ID代际，新追踪初始也未实机。每server tick可broadcast4/5，非状态变化沿限流，不能拿5tick bossBar.update当免疫节流。缺partner tick先置false后搜已有partner，重连那tick不自动再改true。native onRemoved会清partner；活partner时正常AI仍可移动/攻击。连接使用entityCutoutNoCull且alpha1，非柔和半透明；当前相机与连接方向共线crossnormalize可能退化，仅静态边界。无每拒控灰字/嗡声，不能以图层存在称观感通过。',
 '目标身份与两实体链接必须在收包/生命周期层校验，只有Boss明确拒控才播灰字；同一状态重复广播不是“不刷屏”。')
add('goety-skulllord-native-cobweb-movement-multiplier-refusal',r,[(p+'common/entities/ModEntityType.java',1548,1551),(s,539,545)],
 '已注册真实SkullLord实体覆盖原生makeStuckInBlock(BlockState,Vec3)：COBWEB时不调用super，其余block状态才交原生受困倍率处理；这是世界接触产生的原生控制应用位点，不依MobEffect/hurt返回值。',
 '一个直接物理受困入口的最终拒绝1；与活体partner伤害旗标无依赖，即使Boss当前可伤仍拒蛛网倍率。不把恒false的causeFallDamage或另一实体相同method换名追加；仅COBWEB过滤，不宣称全部泥/冰/移动减速免疫。没有取消此前motion或强制静止，没有type9/灰字/声音。原生block调用框架外部0，不伪造运行接触或TCP结果。',
 'Boss控制免疫必须在实际施加控制入口返回明确拒绝；普通伤害false不能覆盖这种无伤害控制路径。')
f=O/'semantic-dedup.json';x=json.loads(f.read_text());x['groups'].append({'family':'apotheosis-goety-batch41','credited_chains':keys,'rationale':'Apotheosis六种来源/全部稀有度装备减伤合1；Vizier原生拒伤窗口1；SkullLord活体partner伤害拒绝1；独立原生蛛网受困施加门1。动画/渲染wrapper、常量/实体名换壳0。'});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');verify()
