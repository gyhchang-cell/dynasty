被动生态观测器（私有QA，默认关闭）

本轮只编译；没有启动Minecraft客户端/服务器，没有修改正式源码或世界。
observer-compile.init.gradle只注册compileCod4EcologyObserver，不接入任何run任务。
因此该class尚未注入运行中的游戏，也不能算运行验收通过。

后续确有必要运行时，由私有QA会话负责人显式接入本源码，并同时提供：
  ecology.bounded.observe=true
  ecology.bounded.output=<父目录存在、该子目录尚不存在的新证据目录>
不能向原live-run1追加新数据，不能改原游戏存档，不自动续跑。

记录内容：
- 原生SpawnState的活动区块/CREATURE数量；按类别原生最大数量计算全局cap。
- 每200tick保存快照和真实玩家主背包空槽/内容。
- 只读原生LocalMobCapCalculator里已有的逐玩家CREATURE计数；反射仅按字段类型读取，
  不调用canSpawn、不填充或修改附近玩家缓存。失败会明确observed=false及原因。
  这些计数不证明某区块附近实际有哪些玩家，也不能单凭计数宣布该区块local gate开放。
- 周期快照仍明确actual_spawn_attempt_observed=false。
  “当前gameTime整除400”只是派生标记，不能当真实自然选种机会或入世证明。
- SpawnPlacementCheck仅在NATURAL、CREATURE且有NaturalSpawner实际调用栈时计入
  每200tick窗口的检查次数，按维度/物种/原版结果/LOWEST处事件结果分别统计；
  每窗口最多20条详细样本。事件不代表所有更早gate通过，更不代表已经成功出生。
- FinalizeSpawn声明NATURAL后仅fresh EntityJoin并有NaturalSpawner调用栈才纳入
  已观察自然来源集合；读盘加入和无栈的声明不计自然来源通过。
- 灯油实际LivingDrops的原ItemEntity UUID、位置、Owner/PickupDelay/age、玩家背包；
  原生尝试拾取/实际PickupEvent/到期/离开Level分开记录。
  LOWEST事件观测不是后续所有监听器的最终状态；离开Level不等于到期。

观测器不会生成/删除/攻击/移动实体，不提供物品，不清包，不改概率/cap/时间/天气，
不调用调试刷怪入口，不反射调用选种或cap方法，不生成/加载新场景。
不会自动启动或停止任何游戏进程。4600tick或300秒预算耗尽后停止周期采样，
写bounded-stop-request.txt，由外部私有会话控制器负责正常保存/停止。
预算标记不等于已强制终止，后续运行必须接入该控制器且禁止无限重试。

旧EcologyLiveAcceptance的自动传送、攻击目标、MONSTER清理、补食/武器等夹具
保持原文件字节不变；不能未经审查直接与本观察器组合后声称最小方案已经实现。
完整下一轮方案仍需每个目标位置实际local gate/更早选种失败链等观测，
目前本工具补齐已有逐玩家计数与部分真实选中后检查，不冒充全链路观测。
