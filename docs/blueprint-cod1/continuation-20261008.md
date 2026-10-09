# cod1 续作 · 2026-10-08

基线：`main` 的 `8d5850e94eac1d6d5ffc5f71cb39f0b20ee26939`。交付分支：`cod1-continuation-20261008`。
输入：用户本轮提供的 `cod1_new(6).txt`。保留主分支现有整合包、其他 cod 分支已合并功能、原有实体 ID 和镇渊帝君最终 Boss 身份。

## 已有进度与本轮边界

当前目录和源码一致：**0 DONE / 30 PARTIAL / 64 NOT_STARTED**。30 只基础怪已注册并有实现；15 精英、12 Boss、25 神器、12 神影仍未完成。输入所述“尚未启动的21只基础怪”已经落后于源码，不应重新注册或重建它们。逐项实现类、模型、动画、贴图、技能、落点、奖励与验收缺口继续见 [现有任务表](remaining-20261007.md)。

青龙偃月刀保持现有第一/第三人称、关羽神影、青龙和多人世界视觉实现。本轮检查了 ImperialWeaponRenderer、ImperialRenderState 与 HouyiAvatarRenderer 的阶段分离、近裁剪/相机相关分支和状态恢复；没有删除神影、缩小模型或关闭效果。

实际客户端验证被当前环境的显示套接字限制阻塞：Xvfb 启动报 `Cannot establish any listening sockets`，因此没有产生本轮单机或双客户端通过证据。构建/服务器测试不能替代此门槛，也不能使用历史截图判定最新构建通过。本轮未跨过该验收门槛新增后续精英、Boss、神器或神影。

## 已复现并修复：死士引信被眩晕打断

旧 Powder.tick 只在失去近距离视线、时间不连续或读档时重置引信。外部 `interruptAttack` 已经取消 DETONATE，但近距离目标仍在时，眩晕期间继续累加 NearTicks，并保留 tryStart 预留的 DETONATE 冷却。补充的真实服务器实体测试在旧逻辑上失败：`Stunned ticks cannot advance the new fuse`。

修复在现有行为中完成：

- 记录已点燃的动作；动作被取消后，清除未消耗的引信计数与对应冷却。
- 眩晕期间不累计引信，恢复后重新计满三秒；不清除其他技能冷却，不缩短眩晕。
- 同时覆盖一 tick 眩晕在下一次行为 tick 前已到期的边界。
- 复用原攻击时钟、同步、死亡和掉落路径，不新增系统或实体。

新增两项回归：`stunningLitPowderFuseRequiresFreshThreeSecondsWithoutSpentCooldown`、`oneTickInterruptionCannotLeavePowderFuseCooldownReserved`。这证明当前可复现的缺陷，不冒称已找回历史间歇失败日志或证明两者必为同一原因。

## 验证记录

- 未修改正式逻辑的基线构建通过。
- 基线 dynasty_army：168 项完成，167 通过，1 项失败：`twoPlayersCanBreakCageAndFiniteBindingLeavesOtherEffectsIntact`。
- 单独复现：新增引信测试在旧逻辑上失败；同轮单独树根牢笼测试通过。保留失败证据，没有删测试或放宽断言。
- 两次修复后完整回归、一轮经 Gradle 启动的小范围回归均以 137 退出，环境同时记录 OOM kill；这些运行全部保留为未通过。随后停止重跑完整集合，以不驻留 Gradle 的独立 JVM（768 MiB 堆）验证相关测试。
- 修复后的独立 JVM 验证：**9/9 通过，进程退出 0**。包括新增 10 tick / 1 tick 中断两项、原有正常三秒/离开重置/砂砾隔离/点燃后离开重置/读档重置/尸体延迟爆炸六项，以及现有牢笼双玩家服务端测试。
- 这些是实际服务器实体测试；牢笼测试使用服务器玩家夹具，不是真实双客户端。全部 170 项的修复后完整回归仍被资源限制中断，不宣称通过。基线牢笼在整批中的失败未根治，保留诊断与待复核项。
- 修复后独立 `build`：**BUILD SUCCESSFUL，退出 0**。

完整回归重跑入口（170 项，不能把此前中断记录当作通过）：使用 Java 17、已有依赖缓存、仓库原有服务器测试 init 脚本。低内存设置由临时 init 文件作用在实际 JavaExec 任务上：

```sh
python3 tools/art/make_local_repo.py
mkdir -p build
cat > build/cod1-memory.init.gradle <<'GRADLE'
allprojects { p -> afterEvaluate {
    p.tasks.configureEach { task -> if (task.name == 'runGameTestServer') {
        task.doFirst {
            task.jvmArgs = task.jvmArgs.findAll { !it.startsWith('-Xmx') }
            task.maxHeapSize = '1024m'
        }
    } }
} }
GRADLE
bash gradlew --offline --no-daemon --max-workers=1 \
  -Dorg.gradle.java.home=/usr/lib/jvm/java-17-openjdk-amd64 \
  -Dorg.gradle.jvmargs='-Xmx512m -XX:ActiveProcessorCount=2' \
  -I tools/maintenance/pr_repair_qa.init.gradle \
  -I build/cod1-memory.init.gradle \
  -PrepairRun=cod1-20261008-final -PrepairNamespaces=dynasty_army \
  build runGameTestServer
```

`org.gradle.java.home` 的命令行覆盖仅用于此 Linux 环境，没有修改用户 macOS 配置。专用服务器测试使用已有脚本中的缓存元数据和跳过客户端资源下载设置。没有部署至用户游戏实例或合并 main。

小范围验证只通过临时独立 sourceSet 包装器调用仓库现有测试方法，原断言完整保留；仅为受资源限制的定向验证，包装器没有进入交付 JAR。原始新测试也在正常 `dynasty_army` 的全量集合中。

完整日志保存在 `evidence/continuation-20261008-*.txt`，保留基线失败、旧逻辑复现及资源中断记录。

## 给下一轮的原文任务文件

按输入的“每项最新构建单机和双人均通过才允许 DONE”标准，本轮没有完整内容条目可以删除。因此 `cod1_new(6).txt` 原文逐字保留；实现过的基础怪继续从现有代码收尾，不重复制作。部分缺陷修复不等同于整只怪或整个 cod1 已完成。
