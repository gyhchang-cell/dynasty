# 本地验证 · 2026-10-10

macOS、Apple M4 Max、Java 17、Minecraft 1.20.1、Forge 47.4.10、GeckoLib 4.8.4。测试使用隔离的 `build/` 世界，未打开玩家存档。

## 已通过

- `python3 tools/cod3/verify_assets.py`：160 项目录、15 骨架、165 动画状态、45 地标、六种安全 Boss 绑定；新增对白词条完整。
- 38/38 `dynasty_cod3` 专用服 GameTest，最终日志 `build/cod3-20261010/acceptance-verified.log`。
- 189/189 `dynasty,dynasty_cod3` 扩展专用服回归，包括帝陵两版本兼容性与大型工坊实际生成；日志 `build/cod3-20261010/full-regression-verified.log`。
- 完整 Forge 发布构建通过，使用独立输出 `build/cod3-20261010/isolated-build`；最终日志 `build/cod3-20261010/build-final.log`。可安装产物为 `build/cod3-20261010/dynasty-1.4.0-cod3-local.jar`，已确认包含新增运行类、金环定义与语言资源且不包含渲染 QA harness。
- 191/191 OpenGL/FBO 检查：40 VFX 两档、25 奇景、15 NPC 正侧面、八工作台空/满界面、30 地标，以及五件真实烘焙物品模型的两档残影。结果 `build/cod3-20261010/render-verified/results/PASS.txt`，日志没有三处已修复物品的 missing texture。
- `git diff --check`、原文仅删除断言、原文件与仓库镜像一致。

## 复现

本机命令共用以下参数；其他机器使用自己的 JDK17 路径：

```sh
./gradlew --offline --max-workers=2 \
  -Dorg.gradle.java.home=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home \
  -I tools/maintenance/pr_repair_qa.init.gradle -I tools/cod3/qa.init.gradle \
  -Pcod3TestRun=build/cod3-acceptance-20261010-verified runGameTestServer

./gradlew --offline --max-workers=2 \
  -Dorg.gradle.java.home=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home \
  -I tools/maintenance/pr_repair_qa.init.gradle -I tools/cod3/render-qa.init.gradle \
  -Pcod3RenderQaRun=build/cod3-20261010/render-verified runClient

./gradlew --offline --max-workers=2 \
  -Dorg.gradle.java.home=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home \
  -I tools/maintenance/pr_repair_qa.init.gradle build
```

共享 checkout 中最后两条命令追加 `-I tools/cod3/isolated-build.init.gradle -Pcod3IsolatedBuild=build/cod3-20261010/isolated-build --no-build-cache`。扩展回归使用 `-Pcod3Namespaces=dynasty,dynasty_cod3 -Pcod3TestHeap=3g -Pcod3TestRun=build/cod3-full-regression-20261010-verified`。各命令串行执行，避免输出目录争用。

`pr_repair_qa.init.gradle` 使用本机已缓存的 assets 与 metadata；渲染 harness 不进入发布 jar。没有改动包编号、字段布局和镇渊最终 Boss 流程。

测试覆盖保存恢复、多个菜单/玩家、实际服务器伤害范围与真实商人库存。客户端检查生产几何、资源及 GL 状态恢复，不能替代双客户端人工矩阵。未完成范围见 [续做记录](../../../docs/cod3/continuation-2026-10-10.md)。

源码及产物 SHA-256、检查计数见 [机器可读凭据](../../../docs/cod3/verification-20261010.json)。
