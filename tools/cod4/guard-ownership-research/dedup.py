"""Conservative semantic-family exclusions after reading complete implementations."""
import json,pathlib
R=pathlib.Path(__file__).resolve().parent;D=R.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research'
c=json.loads((R/'.work/candidates.json').read_text());out=[]
def reject(repo,file,method,reason,start=None):
 hits=[x for x in c if x['repo']==repo and x['path'].endswith('/'+file+'.java') and x['name']==method and (start is None or x['start']==start)]
 for r in hits:out.append({k:r[k] for k in ['id','repo','commit','path','start','end','name','url','excerptSha256']}|{'accepted':False,'reason':reason})
A='baileyholl/Ars-Nouveau';G='Polarice3/Goety-2'
reject(A,'FamOwnerHurtByTargetGoal','canAttack','与已接受FamOwnerHurtTargetGoal.canAttack同一ownerUUID排除+父canAttack模板，变量/类角色端口不另计。')
for method in ['readAdditionalSaveData','getOwnerFromID','addAdditionalSaveData']:
 reject(A,'EntityAllyVex',method,'与已接受SummonSkeleton同方法的owner/NBT模板语义相同；新实体种类和字段拼写不增加有效位点。')
for file in ['SummonWolf','SummonSkeleton','EntityAllyVex']:
 for method in ['getTicksLeft','setTicksLeft','setOwnerID','getOwnerUUID']:
  reject(A,file,method,'纯寿命/owner字段访问器或Optional包装，不以getter/setter凑数。')
reject(G,'ServantFollowOwnerGoal','start','与已接受Ars FollowSummonerGoal.start同一重算清零/保存并置零水寻路代价模板，未计。')
reject(G,'ServantFollowOwnerGoal','stop','与已有停止导航/恢复水代价模板近似，增加清owner缓存不足再作为独立控制流贡献计数。')
reject(G,'Minion','canContinueToUse','VexCharge持续条件与已接受Ars AllyVex相同，hasWanted/charging/存活，端口不另计。',188)
reject(G,'IOwned','copyTrueOwner','IOwnedBlock重载与IOwned成对复制UUID/clientID近似；接口端口不另计。',77)
for method in ['isGrudgedTowardsTag','isGrudgedTowardsType','isAllyWithType']:
 reject(G,'IOwned',method,'在线owner查询/离线UUID保存关系的参数类别变体；已接受实体关系版本，未重复计数。')
for file in ['SummonTargetGoal','ServantNaturalAttackGoal']:
 reject(G,file,file,'构造器参数转发/重载默认值不作为独立研究位点；只接受有策略控制流的goal方法。')
reject(G,'WitchServant','registerGoals','与已接受WarlockServant注册同一shootTarget活体缓存匿名goal，时间常量和类名替换不另计。')
reject(G,'WitchServant','targetSelectGoal','与WarlockServant相同HurtBy+SummonTarget注册模板，普通goal挂载并无独立过滤贡献。')
reject(G,'WarlockServant','targetSelectGoal','只注册HurtByTargetGoal和已研究SummonTargetGoal，未增加新的过滤控制流，不另计。')
reject(G,'WitchServant','mobInteract','与已接受WarlockServant同一货币交易owner/ally授权和owner专属装备控制流，实体类型端口不另计。')
I='AlexModGuy/Ice_and_Fire';M='AlexModGuy/AlexsMobs';S='iron431/irons-spells-n-spellbooks'
reject(I,'AmphithereAIHurtByTarget','setEntityAttackTarget','类有注册，但本静态方法未override原生alertOther，未找到调用点；不计作实际生效目标过滤实现。')
reject(I,'HippogryphAIAttackMelee','canUse','未在固定源码实体注册中找到引用，此版本近战使用其他goal；不能把未启用疑似反转条件凑入实际游戏参考。')
for method in ['canUse','start']:
 reject(I,'MyrmexAISummonerHurtByTarget',method,'与同模组SummonerHurtTarget同一时间戳+实体shouldAttackEntity委托策略，仅受击/主动攻击记录端口，不重复。')
for file in ['TameableAIFollowOwnerWater','FlyingAIFollowOwner']:
 for method in ['start','stop','tryToTeleportNearEntity','tryToTeleportToLocation']:
  reject(M,file,method,'与已有主人跟随的水代价保存/导航停止或随机附近传送模板同构；物种与变量名称替换不再计。')
reject(M,'FlyingAIFollowOwner','isInCombat','与已接受Water版本同一主人距离30+活target规则，只计一次。')
reject(M,'TameableAIFollowOwner','isInCombat','与Water/Flying同一主人距离30+活target规则，只计一次。')
reject(M,'EntityCrow','isAlliedTo','与已接受EntityCapuchinMonkey完整owner/其他Tamable/主人团队模板相同。')
for file in ['SummonedSkeleton','SummonedPolarBear','SummonedVex','SummonedHorse']:
 for method in ['onUnSummon','setSummoner','isAlliedTo','doHurtTarget']:
  reject(S,file,method,'与已读SummonedZombie或IMagicSummon共用解除/设置owner/盟友/伤害委托模板，只换实体或法术常量不计。')
reject(G,'EnchanterMoveToTargetGoal','canUse','固定源码中未找到注册/构造调用，暂仅辅助观察，未计实际游戏实现。')
for file in ['EntityKangaroo','EntityKomodoDragon','EntityMimicOctopus','EntityTarantulaHawk']:
 reject(M,file,'isAlliedTo','与已接受EntityCapuchinMonkey同一驯服owner/其他Tamable/主人团队模板，精确或变量端口不计。')
reject(M,'EntityKomodoDragon','hurt','与已读宠物受击解除坐姿/非玩家非箭减伤模板近似，仅分母数值不同不计。')
reject(M,'EntityMimicOctopus','getGuardianLaser','与已读Cockatrice.getTargetedEntity同一同步ID+客户端缓存/服务端getTarget模板，移除失明前置不足新增位点。')
reject(M,'EntityMimicOctopus','onSyncedDataUpdated','与Cockatrice目标同步ID变化时清计时/缓存模板同构，不再计。')
for method in ['doHurtTarget','isAlliedTo','setTarget','getTrueOwner']:
 reject(G,'AbstractSpiderServant',method,'与已接受Owned/Summoned/IOwned主体归属、守区目标、普通附魔近战模板同构，不按蜘蛛端口计数。')
reject(G,'BlackWolf','mobSense','BlackBeast隐身感知的精简端口，无独立新目标策略，不另计。')
reject(G,'PhantomServant','setTarget','纯父setTarget转发，没有新增过滤或状态行为，不计。')
for method in ['setMeleeAttacking','tick','mobInteract']:
 reject(G,'BlackguardServant',method,'与已读RoyalGuard近战时钟/驻留动画/主人修复模板同构，不按护卫种类重复。')
reject(G,'HoglinServant','getControllingPassenger','与BearServant控制乘客许可同构，仅类名端口不计。')
reject(G,'HoglinServant','mobInteract','与BearServant主人喂养/上下骑乘完整模板近似，仅食品与分支嵌套变化不计。')
reject(G,'GuardianServant','getActiveAttackTarget','与已接受Cockatrice/MimicOctopus目标ID客户端缓存模板同构，不计端口。')
reject(G,'GuardianServant','mobInteract','BearServant主人喂鱼治疗的子集，颗粒/声音不增加目标策略，不计。')
reject(G,'ServantSpawnEggItem','use','与已接受useOn相同蹲下非hostile随从设主逻辑，液体与通用权限基础设施不作为另一归属实现。')
reject(G,'ServantUtil','convertSkeletons','与convertZombies相同先检查转换许可再赋主/finalize/寿命模板，换亚型列表不计。')
reject(G,'RaiderServant','setCommandPosEntity','与setCommandPosEntityOrder相同leader/following/父转发控制流，仅提示文案不同。')
for method in ['tick','canUse']:
 reject(G,'RogueguardServant',method,'与已接受ImperialGuard对应逃跑/射击goal全方法同构，类名/动画常量端口不计。')
for method in ['doHurtTarget','tick','getTargets']:
 reject(G,'VanguardServant',method,'与Piker普通附魔近战、长矛AOE及前向活体扫描模板近似，动画/盟友调用差异不增加独立参考。')
reject(G,'BoneSpiderServant','tick','攻击锁移动modifier为已读stayingMode速度锁模板，非新的目标策略，不计。',122)

# Full-read port exclusions from batches20–38; these never earn accepted credit.
reject('Electroblob77/Wizardry','SummonSpiritHorse','cast','与SummonSpiritWolf.cast同一UUID单实例替换、落点与赋主流程，仅鞍具和属性类别变化不计。')
reject('Electroblob77/Wizardry','EntityLightningWraith','updateTask','与EntityIceWraith.updateTask同一远近战预热/爆发/CD状态机，只换法术常量。')
for method in ['cast','createMinion','addMinionExtras']:
 for f in ['SummonSkeletonLegion','SummonSkeleton','SummonWitherSkeleton','SummonZombie','SummonShadowWraith','SummonSnowGolem']:
  reject('Electroblob77/Wizardry',f,method,'已全文阅读此类；召唤工厂亚型或装备常量变体，没有新的主人/选敌策略，辅助不计。')
reject('klikli-dev/occultism','ChimeraFamiliarEntity','canUse','已全文读ranged相关Goal，但注册处注释禁用，不能算实际生效路径。',530)
for method in ['readAdditionalSaveData','addAdditionalSaveData','setTicksLeft','getTicksLeft','setOwnerID','getOwnerUUID']:
 reject('Alexthw46/Ars-Elemental','EntitySummonBee',method,'已读继承式召唤owner/寿命存取端口，与Ars已有模板同构，不按物种再计。')
reject('AlexModGuy/AlexsMobs','EntityGrizzlyBear','tickRidden','与已接受EntityElephant.tickRidden完全相同；同源码标准化哈希重复已拒绝。')
reject('AlexModGuy/AlexsMobs','EntityGrizzlyBear','onGetItem','与EntityGorilla.onGetItem同样记录食物投掷者等待进食驯服，仅蜂蜜条件/字段不同。')
for f in ['EntityFlutter','EntityMudskipper','EntityWarpedToad','EntityGrizzlyBear','EntityCrocodile']:
 reject('AlexModGuy/AlexsMobs',f,'isAlliedTo','与已接受CapuchinMonkey同一owner/其他Tamable/主人团队模板，不重复物种端口。')
for f in ['EntityGorilla','EntityGrizzlyBear','EntityWarpedToad','EntityCrocodile']:
 reject('AlexModGuy/AlexsMobs',f,'hurt','与已读宠物解除坐姿/非玩家非箭减伤模板同构，没有新的归属目标门。')
reject('AlexModGuy/AlexsMobs','EntityCrocodile','mobInteract','与已接受Gorilla主人forcedSit翻转+公开肉食治疗同构，食品数值不足新增信用。')
reject('AlexModGuy/AlexsMobs','EntityWarpedToad','mobInteract','与已读Mudskipper/SugarGlider喂养随机驯服、公共治疗和主人三态命令核心同构，缺少收纳等独立控制分支。')
for method in ['canUse','canContinueToUse','tick']:
 reject(G,'MudGolem',''+method,'全文读的农田/泥土搬运Goal，未贡献本次召唤归属选敌语义，辅助不计。')
reject(G,'Squall','hurtTarget','与已接受RedstoneGolem hurtTarget同一实际附魔近战模板。')
reject(G,'GraveGolem','hurtTarget','与RedstoneGolem附魔近战相同，附加伤害比例数值不足新实现。')
reject(G,'Prisoner','followGoal','RaiderServant.followGoal删去训练分支的语义子集，不另计。')
reject(G,'PhantomServant','canContinueToUse','原生幻翼俯冲存活/非创造/猫恐惧完整移植，没有新的受控身份策略。',524)
reject(G,'PhantomServant','tick','原生幻翼俯冲碰撞攻击与重置阶段模板；只研究其守区/选敌改动，端口不计。',559)
reject(G,'PhantomServant','stop','与已接受AttackStrategy.stop同样守区回boundPos/否则高度重置。',365)
reject('AlexModGuy/AlexsMobs','CrocodileAIMelee','checkAndPerformAttack','与原生近战距离门/重置冷却/挥手/doHurtTarget同构，非新的守卫策略。')
reject('AlexModGuy/AlexsMobs','CrocodileAIMelee','canContinueToUse','与该类canUse同样父资格+空乘客门，仅持续阶段端口不另计。')

# Additional full-read exclusions, batches39–49. Exact accepted repeats stay credited only at their first site.
reject('mrsterner/GuardVillagers','HeroHurtTargetGoal','canStart','原版ownerHurtTarget时间戳与canTrack模板，已读多处相同流程，辅助不计。')
reject('mrsterner/GuardVillagers','RangedBowAttackPassiveGoal','tick','整体原生弓AI模板，仅巡逻横移分支不足新增归属控制策略。')
reject('talhanation/recruits','RecruitDefendVillageFromPlayerGoal','canUse','与GuardVillagers村民信誉选玩家完整模板同构，只换信誉阈值与名字，不计。')
reject('talhanation/recruits','BowmanEntity','performRangedAttack','弓原生弹道/附魔/损耗模板，坐骑替换并入Recruits弩完整链。')
reject('Polarice3/Goety-2','ReprobateCarry','canHitEntity','与已接受SpellHurtingProjectile相同owner当前target短路/同盟/Enemy/ownerStack模板，端口不计。')
reject('Polarice3/Goety-2','PoisonQuill','canHitEntity','完整穿透命中onHitEntity已研究；过滤仅相同ownerStack模板加pierceID，不拆同链增加信用。')
reject('AlexModGuy/DomesticationInnovation','FrogMixin','isValidAttackTarget','与AxolotlMixin同完整owner最近攻击/受击及同盟排除算法，只换格式，未重复。')
reject('AlexModGuy/DomesticationInnovation','AxolotlMixin','di_customServerAiStep','与Frog入口同owner受击复制，Frog新增Brain缓存链计一次，精简端口支持不计。')
reject('AlexModGuy/DomesticationInnovation','FrogAttackablesSensorMixin','di_isHuntTarget','与Axolotl传感器同一重写模板；错误Axolotl类型分支仅反例支持，不凑一个物种信用。')
reject('AlexModGuy/DomesticationInnovation','PanicGoalMixin','di_canContinueToUse','与di_canUse完全相同的改造宠物禁止Panic条件，持续阶段端口不另计。')
for f in ['FrogMixin','AxolotlMixin','RabbitMixin','FoxMixin']:
 reject('AlexModGuy/DomesticationInnovation',f,'getTameOwner','UUID当前level查玩家与try/catch经典解析模板，纯接口适配不另计。')
for m in ['getOwnerOf','getOwnerUUIDOf','setOwnerUUIDOf','hasSameOwnerAs']:
 reject('AlexModGuy/DomesticationInnovation','TameableUtils',m,'两套宠物接口的薄适配/双向转发；完整hasSameOwnerAsOneWay已计，包装不另计。')

(D/'semantic-exclusions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Explicit reviewed exclusions',len(out))
