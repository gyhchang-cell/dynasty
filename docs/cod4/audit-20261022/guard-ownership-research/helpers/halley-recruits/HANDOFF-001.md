# Halley → Herschel：recruits 归属/守卫研究 001

完成 **30 处完整方法的逐项研究建议**，不是仅交几个家族或下载清单。每条均有独立控制流观察、适用点、限制和本批区分理由；**全部 credit=0、research_credit=0、accepted=false**，由 Herschel 最终跨仓库语义去重、决定晋级。附加 96 个完整支持方法均不计数。

来源仅官方 [talhanation/recruits](https://github.com/talhanation/recruits)，固定 [commit e95f883c19fdef4a14ff200484bb5837d7d56fdf](https://github.com/talhanation/recruits/commit/e95f883c19fdef4a14ff200484bb5837d7d56fdf)，root tree `5e772c95fba1f1b39551c8e9a3db038de41b4938`。完整递归树未截断，已按 Git 对象格式重建并核对 102 个树对象；57 个取得文件均核对原始 SHA256、Git blob SHA1 和固定树路径。

源码声明 Minecraft 1.20.1 / Forge 47.4.10；`gradle.properties` 的 mod_version 为 1.10.7，`mods.toml` 为 1.15.2，**不假定二者构成一致发行版本**。固定 commit 是本批唯一版本身份。

## 交付与复核

- [batch-001.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/guard-ownership-research/helpers/halley-recruits/batch-001.json)：与主账兼容的列表，完整包含 repo/commit/path/start/end/name/source/sourceSha256/text/excerptSha256/normalizedSha256/url/observation/application/limits。额外标记独立贡献、重复风险、credit0和待主协调去重状态。
- [supporting-methods-001.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/guard-ownership-research/helpers/halley-recruits/supporting-methods-001.json)：实际读到的调用者、策略子方法、注册、发射工厂、条约、网络sender校验等全文，只作同链辅助。
- [source-verification-001.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/guard-ownership-research/helpers/halley-recruits/source-verification-001.json)：commit/tree/blob、本地路径及全部取得文件哈希、版本声明差异、TLS与解析边界。
- [batch-verification-001.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/guard-ownership-research/helpers/halley-recruits/batch-verification-001.json)：组装时主账 927 条，只记录该清单哈希而不备份清单；批内和与该快照的精确标准化重复均 0。精确去重不等于最终语义去重。

候选索引里有 1053 个方法节点，**绝不代表 1053 处已研究或有效参考**。只有本批列出的 30 个方法有独立撰写的三项观察；96 个支持方法不计，其他节点未晋级。owner/UUID getters、简单转发、编解码、一般网络限流、弹道数学及平台/实体换名均不以数量计入本批。

## 30 个实际方法位点

下表范围包含 AST 识别到的方法注解和完整方法体；全文、哈希、固定 URL 均在批次 JSON。

| # | 文件 / 方法 | 行范围 | 本条研究的独立边界 |
| --- | --- | --- | --- |
| 1 | RecruitEvents.canAttackRecruit | 551–584 | owner、team友伤、保护leader、group、任务信使多层身份排除 |
| 2 | RecruitEvents.canAttackPlayer | 539–549 | owner/保护玩家与创造旁观模式硬拒绝 |
| 3 | RecruitEvents.canAttackAnimal | 525–537 | 自身坐骑、首乘客策略转换及保护UUID自比较反例 |
| 4 | RecruitEvents.canHarmTeam | 610–625 | 队伍、外交盟友、未过期条约共同许可；缺队伍放行 |
| 5 | RecruitEvents.onLivingAttack | 457–472 | 服务端伤害事件重新验证，区别于初始选敌 |
| 6 | RecruitEvents.onProjectileImpact | 283–367 | 实际命中者/坐骑乘客/箭owner与穿透箭状态 |
| 7 | RecruitEvents.onLivingHurt | 402–427 | 火枪兼容伤害再检、cancel后仍传播报警的副作用顺序 |
| 8 | RecruitEvents.alertTeam | 430–440 | 空target的同Team单位收到直接仇恨传播 |
| 9 | AbstractRecruitEntity.shouldAttack | 2061–2069 | 中立/激进/被动状态下的正面候选规则 |
| 10 | AbstractRecruitEntity.searchForTargetsSync | 327–342 | 合法候选池→距离排序→最近十者随机选择 |
| 11 | AbstractRecruitEntity.tick | 242–305 | 已有target死亡、深水、视线失效及错峰重搜 |
| 12 | AbstractRecruitEntity.hire | 1403–1460 | 归属建立、取消事件、旧目标和导航清理 |
| 13 | AbstractRecruitEntity.disband | 947–981 | 归属解除、驻防/组/队伍撤销与取消边界 |
| 14 | AbstractRecruitEntity.assignToPlayer | 2227–2244 | 转交多步状态与离线owner/取消/失败一致性 |
| 15 | AbstractRecruitEntity.updateTeam | 2109–2144 | 在线owner团队变化的四路同步及延迟重试 |
| 16 | AbstractRecruitEntity.isEffectedByCommand | 1311–1322 | owned/存活/listen/garrison/owner/group指挥资格 |
| 17 | AbstractRecruitEntity.setAggroState | 1056–1069 | 攻击模式转换清目标及解除位置模式 |
| 18 | AbstractRecruitEntity.setFollowState | 1085–1131 | 跟随/驻守/保护模式互斥，守位锚点建立 |
| 19 | AbstractRecruitEntity.reactToHit | 1498–1526 | 最近攻击者替换与向保护leader升级的仇恨 |
| 20 | AbstractRecruitEntity.doHurtTarget | 1528–1551 | 最终hurt、先点火、成功副作用与恒true返回值 |
| 21 | MessageAssignRecruitToPlayer.canAssign | 57–81 | 转交角色权限、驻防限制、leader只能转给自己 |
| 22 | RecruitHurtByTargetGoal.alertOthers | 54–83 | 同类且同owner的复仇传播及接收者空目标/排除类 |
| 23 | RecruitMeleeAttackGoal.canAttackHoldPos | 132–142 | 目标到守位点距离平方<400的空间许可 |
| 24 | RecruitMeleeAttackGoal.canContinueToUse | 58–76 | 途中失去视线清target，持续状态复核 |
| 25 | RecruitMeleeAttackGoal.tick | 100–130 | 有视线时追击/挥击分流及坐骑目标转换调用 |
| 26 | RecruitProtectEntityGoal.tick | 55–85 | 非owner保护对象的缓存、死亡清理、周期重绑与跟随 |
| 27 | RecruitRangedCrossbowAttackGoal.tick | 105–252 | 弩延迟状态机最终SHOOT再检，战略坐标火力另一分支 |
| 28 | CommandEvents.onAttackCommand | 352–390 | 批量sender授权后只用首单位过滤目标池的风险 |
| 29 | BowmanEntity.performRangedAttack | 141–196 | 实际箭对象产生、source传递路径与坐骑改瞄 |
| 30 | RecruitDefendVillageFromPlayerGoal.canUse | 26–46 | 村民信誉额外玩家选敌入口与旧缓存目标保留 |

## 完整调用链与主要结论

1. **归属和指挥**：Main 的 Mod/公共 setup 注册事件和消息 → NetworkSecurity 在服务端线程使用 context sender → MessageAttack / MessageAssignRecruitToPlayer → 游戏资格方法 → hire/disband/assignToPlayer/updateTeam。不能用客户端 payload playerUuid 证明归属；本版本 MessageAttack 实际使用 sender UUID。入队成功辅助方法会清旧 target。
2. **自然选敌**：AbstractRecruitEntity 构造器配置 `TargetingConditions.selector(this::shouldAttack)` → 服务端 tick → searchForTargetsSync → shouldAttack → neutral/aggressive子规则与canAttack → RecruitEvents按目标类型分派 → owner/team/外交/条约。源码的 `validTargets` 是批量攻击命令中的集合，未把它当成一个额外“validTarget方法”凑数。
3. **其他实际目标入口**：已注册的 owner复仇、被保护者复仇、同主报警、同队报警、村庄信誉goal均可能直接setTarget。setTarget只加深水过滤和补给时钟，不补owner/Enemy/passive检查。owner复仇的若干goal与已有模板接近，因此只作支持，不另计。
4. **移动与攻击**：守位锚点半径、近战goal持续资格和近战tick分别影响是否持续行动、追击还是挥击；最终AttackUtil可能将目标换为坐骑。弩SHOOT会重验原实体；战略火力没有实体目标；弓实际发射方法自身未重验归属。
5. **最终边界**：实际弹射物碰撞再查owner/命中实体/首乘客，LivingAttack事件再次查canAttack；但近战doHurtTarget先FireAspect点火后hurt，hurt失败仍恒return true并消耗/加经验。因此“伤害事件取消”不等于“没有仇恨、导航、点火和成功回执副作用”。

对 Dynasty 最有用的是“所有真实选敌入口、持续目标、最终攻击及副作用统一服从既有 Enemy 规则”，而不是移植 recruits 的 PvP/外交玩法。这个仓库无队伍时伤害默认放行，激进模式会纳入普通玩家，村庄信誉也会产生玩家目标，均不适合直接采纳。

另外两处名字容易误导：`isAttackingOwnerOrSelf` 实际读目标的 lastHurtByMob，不能凭名字当作“目标刚攻击主人”；`canAttackAnimal` 在 protectUUID 非空时与自身UUID值自比较，会挡所有Animal。本批保留真实源码观察，不冒充实机缺陷复现。

## 运行与范围

没有启动游戏/服务器，没有运行上游 Java、Gradle或下载脚本。只运行本人编写的下载、文本、AST与哈希校验工具；TLS始终开启证书校验。AbstractRecruitEntity 的 raw 请求一次TLS EOF后，改用一次GitHub blob API成功并验证blob，原错误留档，没有循环重试。

解析器对 `RecruitHurtByTargetGoal` 的类型注解varargs声明有兼容报警；该辅助setAlertOthers正文人工读过，未作为AST入选方法。30个主方法与96个支持方法节点均无解析错误，已逐字校验来源摘录。没有声称运行/编译通过。

只写 tools/docs 的 `guard-ownership-research/helpers/halley-recruits/`。主账、生产、模型、动画、待办均未修改；没有备份清单、删除游戏内容或自动给主账credit。
