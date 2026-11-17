真实原生CREATURE门槛回执：私有QA编译阶段，尚未运行

最初仅由 native-gate-compile.init.gradle 编译；后续 tools/cod4/ecology-native-acceptance/ 已增加私有helper Jar/reobf与显式bootstrap/正常保存停止控制器，仍未启动游戏。
没有装入生产Jar，没有自动注册事件，没有把Mixin配置接到生产mod。
现有bounded-src/EcologyOpportunityObserver.java保持字节不变。

与既有被动observer不同，本工具观察实际原生调用，而非周期快照推断：
- NaturalSpawner.spawnForChunk真实传入spawnFriendlies/persistentPhase标志，且实际Overworld，记录该chunk机会。
- SpawnState.canSpawnForCategory(CREATURE,同chunk)原生RETURN；只读其现有类别计数/活动区块数计算原版cap作上下文。
- LocalMobCapCalculator.canSpawn(CREATURE,同chunk)原生RETURN。仅实际调用才记录；未调用明确为未观察，不能冒充local gate开放。
- ThreadLocal嵌套栈与唯一scope_id/parent_scope_id限定同一实际调用；类别回执匹配SpawnState对象，local回执另匹配只读取得的原生LocalMobCapCalculator对象身份与ChunkPos。
- 字段身份读取失败、多次/异对象local回执、END仍未配对的scope显式记异常，不能自动算作完整机会；重入不覆盖外层scope。
- 不自行调用canSpawn/getPlayersNear或debug spawn，不多抽RNG，不改返回值，不改cap、世界、实体、时间、概率、位置。
- 原生类别门槛通过仍不等于目标物种被选中，更不等于成功自然出生。

未完成的运行接入前提：
1 Herschel已对初版做独立只读复核并提出边界问题，后续已加固，修订版及私有bootstrap仍待复核/运行。helper Jar/reobf已离线构建；公共API已正常重映射，method以安装1.20.1 SRG的固定名字/descriptor绑定。
2 私有bootstrap明确且仅一次MinecraftForge.EVENT_BUS.register(NativeCreatureGateObserver.class)，并装入native-creature-gates.mixins.json。
3 显式ecology.nativegate.observe=true及ecology.nativegate.output=<父目录存在且叶目录尚不存在的新路径>；默认关闭。
4 与既有被动出生/掉落/库存observer按独立新目录组合，不向历史live-run1追加记录。
5 外部控制器必须执行一次有界会话/正常保存停止。观测器在逐行写入前检查32000行/300秒准入，并在4600 ServerTick检查；阈值触发仅写bounded-stop-request.txt。同步I/O仍可能阻塞，因此不能宣称硬墙钟保证；bootstrap正常停止控制器与独立外部进程watchdog都仍必要。
   同一JVM第二次ServerStarted明确拒绝，避免复用stopped/ticks旧状态；每个运行必须新私有JVM。
6 原始世界只读，沿static-creature-gaps/minimum-next-run.txt真实门槛/原生正常攻击释放计数竞争者/真实背包腾位方案，不调cap或生成目标；未获原生选种或掉落保持PENDING，不无限挂机。
7 编译通过不验证Mixin在完整包实际注入、事件注册、真实local/global gate、六种出生、灯油同UUID拾取；这些均未完成。
