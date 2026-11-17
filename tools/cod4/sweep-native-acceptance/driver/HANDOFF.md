# Sweep stage driver final offline handoff — 2026-10-29

状态：独立默认关闭 driver 已完成离线编译、JDK 协议边界检查及 prepare_pair 参数核查。没有执行 prep，没有复制存档/实例或启动游戏。原生 chat/C2S、同会话完整矩阵及像素验收仍待主协调集中完成；任何 COMPLETE / age1 candidate 都不是整项验收通过。

## 冻结输入与构建

精确入口：`src/com/dynasty/sweepdriver/SweepStageDriver.java`，SHA256 `efe11885531929beb011690c13c92f90decf2897ba03a31a158899f42c8216a6`。仅三个 class：主类、`$Schedule`、`$RawImport`。资源为独立 modId `dynastysweepdriver` 的 `META-INF/mods.toml` 与 format15 `pack.mcmeta`，无新 Mixin。

完整冻结路径、资源/工具/类 SHA 见 `docs/cod4/audit-20261022/sweep-native-acceptance/driver/final-delivery01.json`。离线官方映射输出：`tools/cod4/sweep-native-acceptance/driver/.work/20261029-014903-564284/classes/`。本轮未重新编译未改的 Java，也未重复 QA02、护卫或盔甲回归。

协调已生成独立 SRG01：`build/cod4-sweep-native-20261029/driver-build01/libs/dynasty-sweep-stage-driver-1.0.jar`，SHA256 `ce7c33149a47b722df76a4d3ac5652e281fb67c86da77e2f2392b947db7dca19`；对应 `coordinator-reobf01.json`，源与资源同本次冻结。该收据不是独立运行验收。若需另构建，`qa.init.gradle` 的 `reobfSweepStageDriverJar` 要求绝对私有 `dynasty.sweepdriver.build`、`baseline`、`qaClasses`、`sources` 四个 build 属性；QA 官方类路径见 compile01，不要将官方映射 class 直接覆盖 SRG Jar。

## 与协调 prepare_pair.py 的契约

已只读逐项核对 `tools/cod4/sweep-native-acceptance/prepare_pair.py`，未导入或执行其 prepare。其 fresh `sweepNN` 标签满足 driver ID 限制（driver 最长30字符；实际标签须遵守此上限）。它在 `build/cod4-sweep-native-20261029/<run>` 创建 host/peer、host-evidence/peer-evidence、bridge；driver 检查实际 gameDir、SweepQA.OUT、所有 realpath 均在同一个带标记的私有根内。桥接仅适用于同机共享文件系统上的两个独立 JVM。

双方均设置：`dynasty.sweepqa.enabled=true`、`dynasty.sweepqa.instance=<role instance>`、`dynasty.sweepqa.output=<role evidence>`；driver 设置 `dynasty.sweepdriver.enabled=true`、`dynasty.sweepdriver.role=host|peer`、`dynasty.sweepdriver.bridge=<root/bridge>`。默认未显式启用时不驱动客户端。

plan 的 run/private_root/host_instance/peer_instance/host_output/peer_output/host_uuid/peer_uuid/saved_world/bootstrap_existing_world/qa_sha256/driver_sha256/production_sha256 全部匹配；根 marker 绑定原始 plan 字节 SHA。计划及 ModList 实际 QA、driver、私有 production Jar SHA 必须一致，旧角色会话文件拒绝复用。各阶段绑定 index/case/run/plan/角色 session，保留不可重用的 command-index。

原始已停的自有 run12 checkpoint：`build/cod4-mob-network-20261023/run-12/host/saves/mob-qa-1793198631800`。prep 仅计划复制此世界至 host/saves/sweep-world，bootstrap 只 loadLevel，不新建世界。名字/离线 UUID：host `Cod4MobHost` → `6c3ab68c-2707-3e49-bca5-7e82a37ca29f`；peer `Cod4MobPeer` → `ca2fb277-2f95-3b5d-a212-139f545d2321`。两者 playerdata 文件在原 checkpoint 均存在（只读哈希收据）。prep 替换原 launcher 的 --username/--uuid，game_directory 原本即 role instance；不要使用 launch_once 返回的旧 EcologyQA identity 字段代替最终 argv/plan UUID。

prep 删除 launcher 全部旧 `-Decology.*` 参数，再只注入 `ecology.nativeqa.enabled=false`、`ecology.nativegate.observe=false`、`ecology.bounded.observe=false`，不继承旧 driveScenes/openCopiedWorld/restoreSavedQaFlight。compile20 Jar 仍包含三处 common 观察 Mixin 与 QuietWindowMixin；false 开关关闭生态 observer/scene/lifecycle 工作，并非移除了 common 注入。QuietWindowMixin 提供已存在的隐藏窗口初始化；driver 自身只断言 invisible/unfocused，不操作窗口。metadata format15 已核对。原生启动时是否无 warning 仍需运行证据，LoadingErrorScreen 不自动绕过。

prep 本身不限制 run 字符总长至30；协调使用正常短 `sweepNN` 即满足本次协议，超长标签会被 driver 拒绝。不要覆盖旧 prepared root。driver Jar 被 prep 绑定到 coordinator-reobf01 收据；若换 SRG build，协调应同步其收据和 prep 绑定，不能悄悄换 Jar。

## 自动阶段及验收边界

复用了原 fullpack 的 port → 双端实际渲染 → command → server system ready → client ready → 输入 → ack → COMPLETE 协议思想。旧 MobNetworkAcceptance 会自动新建世界并运行自己的矩阵，因此不同时加载；没有修改它或生态旧 helper。新 driver 只桥接既有 sweep QA03 原生命令。

1. host 打开已复制世界，发布私有 LAN；peer 原生 TCP 加入。检查两个非 FakePlayer、预期 UUID、peer 的实际 socket 地址、SURVIVAL 与实际 render 帧。
2. peer 通过 `ClientPacketListener.sendCommand("sweepqa arm ...")` 的原生聊天入口发送命令；服务器原 QA 创建自有 fixture。host 等原文件稳定并发 system ready nonce，两端收到真实 system chat 后才推进。
3. 原 fixture 字节 SHA 校验复制到 peer OUT，校验角色/实体/原生武器/距离/完整冷却。host 经原生本地 chat `sweepqa-watch` 开观察；peer 经 `sweepqa-client` 进入既有 QA 的真实 MultiPlayerGameMode.attack C2S，driver 不直接调用 attack、receipt 或生产 cue。
4. 两端完成实际40 clienttick窗口且 CaseLog 关闭；host 还需攻击后20个成对原生 END 周期。随后原生命令 dump / clear，等 SERVER log 关闭，再将原始 server-events 字节复制给 peer。
5. 两种视角分别最多6次真实成功攻击寻找实际 age1（不改时钟、不制造延迟/伤害/回执）；选出 candidate 后才做3种负控×2视角。最多18案例，6次仍无 age1 则明确失败退出。负控必须实际进入攻击，不能靠空探针判绿。
6. result-index 带 case/view/mode/calibration 和文件 SHA，overall_acceptance 始终 false。该轻量分类仅筛候选，不替代 analyze.py 全检查。协调对 peer OUT 的最终正例执行 `analyze.py OUTPUT CASE --mode success --view first|third`，负例补 `--calibration SAME_VIEW_POSITIVE_CASE`（具体 CLI 以 analyze.py --help/源码为准）。必须复核真实血量/一次消费/年龄/拥有者/维度/旧 mesh_weapon 包与生命周期、原月牙同帧共存、原生像素文件和遮挡/形状/组合；不能以 nonzero 像素关闭待办。host 为独立旁观记录，不伪装成攻击者正例分析。

## 有界退出与未完成范围

阶段60秒/1000 callback ticks、bootstrap240秒/6000 ticks、总900秒；完成/异常均清自有 QA fixture，peer 正常 stop，host 等 peer 完成（或10秒）再 stop。外部可用 bridge/external-stop-request.txt 请求正常退出；JVM/渲染线程挂死仍须协调自己的有界双进程 watchdog。现有 coordinator pair_watchdog.py 已接此 marker；其 Python-only 检查不是游戏退出/存档证明。driver 不自行创建/杀外部进程。

若旧 checkpoint 弹实验确认或其它未处理界面，driver 不模拟点击绕过，超时应保留证据。驱动 init 在所有权绑定前失败会写 FAIL（能写时）并停止动作，外部 controller 负责收回自己启动的 JVM。集中 run 仍须核查最终 launcher 参数、实际隐藏窗口、连接身份、正常退出/保存，以及 fresh 同会话 positive calibration。当前未完成上述任何运行验收；不改主清单。

离线证据：真实 Forge/QA 官方映射 javac PASS；纯 JDK 执行36种有界计划、耗尽边界与原始字节/SHA 拒绝覆盖检查共2286断言，确认未加载 Minecraft/Forge。仅证明离线协议，不证明原生聊天、C2S、图形或服务器行为。原 QA02、metadata03、旧失败及 SRG 收据保留；未写生产、共享 Jar 或专业资产。
