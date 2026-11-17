# COD4 真实双客户端网络验收

仅测试辅助模组，不进入正式模组。使用固定的已验证私有 Dynasty JAR、GeckoLib、Curios 和辅助模组，共四个 JAR；不是完整整合包声明。新建两个独立实例，host 原生 publishServer 发布随机 LAN 端口，peer 使用独立离线 UUID 经本机 TCP 登录。host 为正常集成服务器的本地连接，peer 强制检查真实 InetSocketAddress。两个客户端均实际渲染；没有 FakePlayer。

服务器夹具提供装备、物品和效果，不能当作生存获取或两名真人游玩。0–23：八状态逐项施加、刷新、解除；24–31：天罡白天阴气免疫、地煞夜间阳气免疫及摘帽、重新佩戴、昼夜变化；32–38：独立层数、上限、阴阳中和、雷印三次消耗；39–42：两人盔甲、背包饰品不生效、真实 Curios 项链槽归属转移；43：peer 客户端 MultiPlayerGameMode.useItem 原生 C2S 与持续使用，服务端等待完成后核对丹药扣一、阳气归属；44：清理；45–48：近距离基线、peer离开100格（同时超出32格广播范围/低视距）、重新进入跟踪、最终清理。

每个阶段保留服务端快照和两端客户端快照。每个客户端核对自己的完整原生效果列表与服务端的层数、时长（网络等待容差100tick），记录其他实体效果列表；对两个实体均核对实际客户端 Cod3VfxRenderer ACTIVE 中尚有效的状态序列和层数及装备/Curios槽。读取现有渲染队列，不伪造视觉包。截图来自各自真实 framebuffer。客户端等待同步最多400tick，再输出具体 mismatch；不能仅靠构建成功当联机通过。

编译：`JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home ./gradlew --offline --project-cache-dir build/cod4-network-20261022/project-cache -I tools/cod4/network-acceptance/qa.init.gradle networkAcceptanceJar reobfNetworkAcceptanceJar`

运行：`python3 tools/cod4/network-acceptance/run.py run-01`。每次必须使用新 run 编号。驱动等待其他 COD4 全包 GPU 客户端退出后才启动（主代理后续已明确允许与其短FTB定位QA并行），失败只终止自己创建的进程组。保留失败运行，不覆盖。

范围限制：当前未精确测量31/32/33格临界边界；已测100格离开和重新进入。未覆盖全部状态的真实战斗来源输入、真人音效主观判断、全部盔甲特效、完整整合包或生存流程。只有第43阶段是原生客户端发起交互；其余主要是服务端夹具与真实网络同步。

已完成：`docs/cod4/audit-20261022/network-acceptance/report.json`，权威运行 `run-03`，49服务端快照、98客户端快照、54实际世界截图，双方exit0。`run-01`保留夹具昼夜时序失败；`run-02`49网络状态通过但早期地形加载画面不计世界渲染全验收。源及JAR哈希见prepared.json与各运行manifest/result。
