# Exact sweep pair launcher — offline handoff

2026-10-29。仅新增 `tools/cod4/sweep-native-acceptance/launch_pair.py`、本目录 Python 校验及专属 launcher 证据目录。driver、prep、watchdog、生产/共享 Jar、世界、旧 readiness 和主待办均未修改。已读取 Herschel `driver/preparation-boundary-delta02.json`：P2 准备边界闭环，P1 独立最终 readiness/controller 集成由本 launcher 提供待审源码；这不是运行审批或原生验收。

## 入口及审批契约

从仓库运行 `python3 tools/cod4/sweep-native-acceptance/launch_pair.py sweep01`：默认 check，完整只读核对，缺 ready 输出 `INPUTS_CHECKED_NO_READY_NOT_LAUNCHABLE`。`--mode plan` 将相同检查和完整 snapshot 写到 stdout；launcher 不自行保存/改写 snapshot 或创建审批。协调可以另存 stdout 作为 review 输入。本次完整结果在 `docs/cod4/audit-20261022/sweep-native-acceptance/launcher/sweep01-plan-not-ready01.json`，SHA 见 delivery01。

唯一实际启动入口是显式 `--mode run`。它首先要求该固定 run 根已有独立 `reviewed-launch-ready.json`；缺失立即拒绝，早于元数据 helper 加载、平台查询、marker 或 watchdog。源码无 ready writer。本轮没有创建任何真实或临时 ready 文件、没有执行真实 run。

协调完成 launcher/watchdog 及最终 snapshot 独立 review 后，自行提供 ready：`status` 必须为 `READY_FOR_ONE_BOUNDED_SWEEP_RUN`，`run` 精确匹配，`one_attempt_only` 必须为布尔 true，`snapshot_sha256` 等于本工具 canonical JSON 摘要，`reviewer` 非空；`review_report` 是仓库相对路径且位于 sweep 专属证据目录，`review_report_sha256` 绑定其原字节。该 report 应承载本次 launcher/最终输入/单次运行审查，不能把只做 P2 的 preparation report 当作运行审批。现有 receipt/status 不能自动推导授权。

run 会先 snapshot/ready 核对，读取 awake display 与 ps（不唤醒/解锁/操作屏幕），再完整复读 snapshot、ready、环境、display、ps；验证即将 source-load 的 watchdog 字节与最终 SHA 一致。随后仅以 CREATE_NEW+fsync 创建 `execution-started.json`，绑定 readySHA/snapshotSHA，调用现有 `pair_watchdog.run_owned_pair`。任何后续失败均消耗本次 marker，绝不覆盖或自动重试。没有 shell、detach、existing-PID attachment、世界创建/复制或编译命令。

## 精确绑定范围

- ROOT 固定 `/Users/a15356015027/Desktop/dynasty`，BASE 固定 `build/cod4-sweep-native-20261029`；run 仅 `sweep[0-9]{2,25}`，所有目标须为 canonical 直接子路径。执行中的 launcher 源路径与初始源 SHA 也要一致。所有目录 manifest 拒绝 descendant symlink/special file，缺目录 None 与空目录 {} 分开。
- 不信任 plan 自报路径：固定 host/peer、两 OUT、bridge、run12 自有 source-world 与 host/saves/sweep-world、两 UUID/用户名逐项重建；完整 source-world/copy manifest 相同且与 prepared 一致。host 不得有别的 save；peer 不得有 save。输出必须为空，bridge 仅 plan.json，实例顶层不得含未准备条目。
- final plan/rootmarker/prepared 原字节 SHA、四来源 receipt/四源 Jar/两端四复制 Jar、两端完整 mods/config/defaultconfigs/resourcepacks/options、四生产源 manifest 以及固定共享 baselineSHA 全绑定。既有 marker、watchdog日志或 consumed bridge 均拒绝。
- driver 当前和 `build/.../driver-frozen01` source/resources 须等于 reobf01 `frozen_inputs`，实际 SRG Jar 每个 class/resource SHA 要相同。QA02 当前及编译冻结完整 Java 方法源文件 SHA 核对，QA03 包内所有11class SHA 对 reobf03；生产 FangtianSweep 当前/冻结源对原离线编译收据；quiet20 Jar 对固定 compile20，current quiet Java 对其 source verification 收据。未重新编译、不改变 source 或 Jar。
- tools SHA 包含 launcher、自有顶层 Python、watchdog/prep、生态元数据构造与导入的 prepare_inputs/watchdog/lint、QA/driver/quiet 源资源和构建 init。加载元数据构造时只执行已读源 `.py`，不使用预载 tool module 或缓存 pyc；暂替换所需3个生态 import 后恢复 sys.modules。所有 helper CLI 均有 main guard；没有调用其 run/prepare。其原始 ecology flags 只作输入并在再生 argv 中全部剔除。
- 双端 argv 重新走既有 installed metadata constructor，再换角色/UUID并添加精确开关，必须与 prepared argv 全元素完全相等。固定 Java、BootstrapLauncher、native forgeclient、gameDir、assetsDir、两 UUID；所有 property 必须独立且仅在 JVM 参数段，sweep/ecology 恰好六项 sweep+三项 false ecology，无额外开关。拒绝晚置 property、未知 JVM property/option、agent/@argfile/property file 类注入与重复角色参数。`JAVA_TOOL_OPTIONS/_JAVA_OPTIONS/JDK_JAVA_OPTIONS/CLASSPATH` 只要存在（包括空值）即拒绝。
- installed metadata、Java executable/release/完整 lib tree、实际 classpath/module path Jar、完整 installed libraries tree、完整 extracted native tree、assets index 字节/路径 SHA 绑定。所有 launch 路径须 canonical；不执行 java -version 等命令。不对整个 installed assets objects 声称冻结；专业资源不写入。

## 生命周期边界

run 的 CoreGraphics 调用仅查询 main display Active/Asleep；不能读取时失败关闭。ps 是全机 Java 游戏排他检查；Minecraft/Forge/Fabric/Quilt/GameTest/服务器及未知 Java 均拒绝，不限本仓库，只有可明确识别且不含游戏入口的 Gradle launcher/daemon 可放行。只读检查任何已有 PID，不向它们发送信号。

实际两个 foreground Popen、独立新 process group 和 stdout/stderr 私有日志均在已有 watchdog 内创建；launcher 不另写第二套进程管理。预算 startup240/absolute900/save60/TERM15/poll0.25，callback 失效由外部 watchdog 收回自己新建的 JVM。正常退出/强制信号、连接 marker、exit0 都不等于 save 或游戏通过；Herschel 既有 direct-child leader 退出后遗留后代的 caveat 仍保留，本 launcher 不改旧 watchdog 或承诺一般进程树清理。

## 离线证据与未验范围

`launch-checks/check_launcher.py` 15项 Python 测试通过，Popen 全程被拒绝替身覆盖。覆盖真实 prepared 双端 argv、profile/property 覆盖、3false生态限制、agent/argfile、继承环境、canonical/symlink/manifest、重复 JSON、Gradle/真实与未知 Java 分类、缺 ready 先拒绝、stale ready、默认 check、输入竞态/睡眠拒绝，以及 mock controller 单次 CREATE_NEW marker。没有实际进程、display 或 ps 查询；没有临时 ready 文件。只在 TemporaryDirectory 写 synthetic manifest/marker，并非真实 run。首次一项 fixture 因 macOS /var→/private/var 别名失败，改测试临时根 resolve 后通过，没有放宽 canonical launcher。

实际 sweep01 只读全量 plan/check 通过（receipt819c22...、plan5493e06...、marker0da3d4...），完整 plan-not-ready 保存逐路径 SHA，未写 run 根。准备与源 driver SHA 未变，无新 prep 改动需求。集中运行仍须协调最终独立审查 ready/argv/platform、唯一 run、原生 age1/负控/raw分析/双视角像素/自然保存证据；overall/gameplay acceptance 均未完成，不改主待办。
