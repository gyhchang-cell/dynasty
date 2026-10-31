import json,pathlib
R=[]
def add(f,m,o,a,l,start=None):
 d=dict(repo='iron431/irons-spells-n-spellbooks',file='/'+f+'.java',method=m,observation=o,application=a,limits=l)
 if start:d['start']=start
 R.append(d)
add('IMagicSummon','shouldIgnoreDamage','非绕过无敌伤害、配置不许打自己召唤且来源非空时才委托isFriendlyFireBetween；其他不忽略。','保护开关、伤害标签和真正来源实体共同决定输入免伤，不能代替攻击输出许可。','仅研究召唤实体受伤路径；不导入该模组配置或改变本项目伤害标签。')
add('IMagicSummon','isAlliedHelper','owner为空false；对象为另一魔法召唤或OwnableEntity时取其owner，判同owner或otherOwner.isAlliedTo(otherOwner)。','关系谓词接收者和实参必须核对，自己与自己比较不能证明两个不同owner结盟。','源码确实写自比较；没有运行该版本，不能扩大声称所有外部宠物一定被错误结盟。')
add('IMagicSummon','onDeathHelper','LivingEntity召唤物死亡时，仅服务端且开启死亡消息并且召唤者为ServerPlayer，向那个玩家发送召唤物战斗死亡消息。','战斗通知也应由真实归属定向到玩家，避免最近旁观客户端收到另一人的私有反馈。','消息归属是相关召唤玩法实现；不把消息格式/翻译或一般日志基础设施计数。')
add('IMagicSummon','onRemovedHelper','客户端退出；DISCARDED时给主人提示，原因shouldDestroy才同时移除召唤管理和到期追踪；区块卸载强制杀死代码已注释。','卸载与销毁不同，清理归属索引和租约计时不能用任何离开世界事件一概删除。','只收现行单参版本；Deprecated按药效层数追踪的重载不算现行独立实现。',68)
add('GenericProtectOwnerTargetGoal','canUse','owner必须Living；扫描正在以主人或同主人魔法召唤为target且有视线的Mob，选离主人最近者直接赋target；失败递减强度，间隔分支另按受伤时间与强度设置。','主动护主应以正在攻击己方为条件，不能把附近所有非盟友旁观者当威胁。','间隔变量分支赋值需完整读，不能按字段注释推定实际每100tick检查；不导入其强度机制。')
add('GenericCopyOwnerTargetGoal','canUse','只允许Mob主人且主人target非空，要求父canAttack并排除由该主人直接召出的IMagicSummon。','复制owner目标依然应复核许可；直接同owner召唤排除不能涵盖所有旁观非Enemy对象。','与一般owner最近攻击时间戳不同；这里仅Mob主人，玩家主动攻击入口在另一goal。')
add('GenericCopyOwnerTargetGoal','start','重新读取当前owner的target，赋Mob.target并把同一对象写入Brain ATTACK_TARGET有效200tick，最后调用父start。','目标有普通字段与Brain双存储；只清普通字段可能不能撤销持久攻击意图。','canUse到start间owner变化未在此复核；记录局部窗口，不据此直接认定可复现崩溃。')
add('GenericOwnerHurtByTargetGoal','canUse','取主人最近袭击者，先排null及袭击者isAlliedTo召唤物，再要求新时间戳、父canAttack并排同主人召唤。','护主报复包含显式反向盟友检查；报复路径也不能绕过项目Enemy许可。','相对已研究Ars目标goal新增supplier主人及显式反向盟友门；只计该完整组合，不拆每个条件。')
add('GenericOwnerHurtByTargetGoal','start','赋缓存袭击者为target，同时Brain记200tick；若此时主人仍Living则更新时间戳，再父start。','报复开始时须同步攻击记忆；撤销或换归属应考虑历史记忆和时间戳。','与copy目标start共享Brain写入，但新增独立受击去重状态；主动攻击start无Brain不重复收录。')
add('GenericHurtByTargetGoal','canUse','自身受击目标先排空/盟友，新受击时间戳才继续，玩家且全局愤怒规则时拒绝，再执行注入toIgnoreDamage和可无视视线/隐身的canAttack。','通用受击goal可注入owner排除；旁观玩家经旧受击记录被选中仍需独立目标门。','忽略谓词与攻击目标许可不同；不得引入全局PVP/愤怒配置改动。')
add('GenericHurtByTargetGoal','start','先核当前袭击者非空，赋target及200tickBrain记忆，更新targetMob/时间戳/300不可见记忆，可呼叫同类支援后父start。','报复会传播给其他实体，并存在多层缓存，审核须追到群体传播源。','原生样板有移植成分；本条贡献在Brain目标记忆与本模组注入忽略策略的联动。')
add('GenericHurtByTargetGoal','alertOthers','范围按followDistance及上下10格找同class非旁观Mob，排自身/已有target；Tamable需同owner且候选非盟友，排指定class后写袭击者target。','同种类不等于同归属；此处owner限定只针对TamableAnimal，魔法召唤归属要另核。','不把alertOther单行setter另计；是否产生跨owner实害取决于实体isAlliedTo具体实现。')
add('SummonedZombie','registerGoals','完整替换注册：近战/跟随/游走观察；target优先护主受击、主人攻击、复制Mob主人、自己受击支援、主动保护，没有NearestPlayerGoal。','复用敌对原生实体时，重建目标goal可避免继承的最近玩家选敌继续运行。','SummonedSkeleton/PolarBear相同target列表不重复计；不建议为本项目重写全部野生AI。')
add('SummonedZombie','hurt','非绕过无敌且起身动画中或shouldIgnoreDamage命中即false，否则父受伤。','召唤出现窗口免伤是条件式受击限制，应与到期/战斗目标权限分开。','相同Skeleton版本不计；起身保护是该模组机制，不新增本项目动画或免伤。')
add('SummonedZombie','doHurtTarget','将自身、目标和RaiseDead带getSummoner归属的伤害源交Utils.doMeleeAttack。','伤害归属与目标过滤不同；要继续跟入真实近战工具，不能看到owner参数就判不误伤。','其他召唤仅换SpellRegistry常量的同模板不计；尚未凭此断言最后工具是否友伤过滤。')
add('SummonedZombie','onUnSummon','仅服务端播消散粒子后setRemoved(DISCARDED)，由移除回调管理归属/到期追踪。','主动解召应触发销毁型移除链，区别于区块卸载暂离。','其他种类完全相同解除代码不计；粒子参数没有独立玩法贡献。')
add('SummonedHorse','mobInteract','已是载具先交父交互，否则只有pPlayer与summoner同实例才骑乘，旁人调用makeMad，返回双端成功。','可见召唤物不等于旁观者可控制；交互授权必须绑定服务端真实owner。','PolarBear同骑乘结构只有无makeMad差异，未重复计数；本项目不新增骑乘控制。')
add('SummonedHorse','readAdditionalSaveData','父读档后以OwnerHelper.deserializeOwner恢复原生Horse ownerUUID。','召唤管理器和原生可驯服实体可能同时有owner存储，重载应核对两者一致。','本方法只恢复原生owner字段；不能据此证明全局SummonManager归属也恢复。')
add('SummonedHorse','addAdditionalSaveData','父存档后以OwnerHelper.serializeOwner保存getOwnerUUID。','存档入口应保存稳定UUID而非易变entityId；需和读档及管理器索引一起验证。','与Ars直接NBT UUID不同，具体序列格式由OwnerHelper决定，须继续追源。')
add('SummonedPolarBear','getControllingPassenger','首位乘客为Mob则返回，若不是重新取首位并允许Player，否则null；这里不校验summoner。','上车许可与持续控制许可是两道入口；控制器自身可接受任何已上车实体。','不能据此推定旁观者能实际登乘，已有mobInteract仍限定owner。')
R=[r for r in R if r['method'] not in ['getControllingPassenger','readAdditionalSaveData','addAdditionalSaveData']]
pathlib.Path(__file__).with_name('batch07.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
