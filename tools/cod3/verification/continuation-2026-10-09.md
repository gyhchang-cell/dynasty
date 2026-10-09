# cod3 对话续做验证 · 2026-10-09

基线 `08c95b34b077d49183664f28d62e39308db69b17`；Minecraft 1.20.1、Forge 47.4.10、Java 17.0.20.1。所有服务器测试使用独立 `build/` 世界目录。

| 检查 | 结果 | 覆盖 |
| --- | --- | --- |
| 强制完整 Java 编译 | PASS | `--no-build-cache --rerun-tasks compileJava`；检查 class 含新增 InfusionRequest 协议声明 |
| Gradle build | PASS | Java、资源、jar、reobfJar；12 秒 |
| dynasty_cod3 GameTest | 26/26 PASS | 原有十九项及新增七项对话测试；实际进入测试批次、通过、保存全部世界并退出 0 |
| cod3 资源检查 | PASS | 160 目录项、15 骨架、165 动画状态、45 地标、6 Boss 安全绑定；所有新增中英对话词条 |
| 中英词条检查 | PASS | 708 物品模型、7 效果及结构/群系/维度 |
| 原文保真检查 | PASS | 1508→1507 行，唯一差异为删除 C3-NPC-002 原行；无替换、插入或重排 |

实际测试日志关键输出：

```text
Running test batch 'defaultBatch:1' (26 tests)...
========= 26 GAME TESTS COMPLETE ======================
All 26 required tests passed :)
ThreadedAnvilChunkStorage: All dimensions are saved
Game test server shutting down
BUILD SUCCESSFUL in 1m 29s
```

验证先执行强制完整编译，再运行：

```sh
./gradlew --offline --no-daemon --max-workers=2 \
  -Dorg.gradle.java.home=<JDK17> \
  '-Dorg.gradle.jvmargs=-Xmx768m -XX:ActiveProcessorCount=2' \
  -I tools/maintenance/pr_repair_qa.init.gradle -I tools/cod3/qa.init.gradle \
  -Pcod3TestHeap=1024m -Pcod3TestRun=build/cod3-dialogue-gametest-final-20261009 \
  -Pcod3Namespaces=dynasty_cod3 runGameTestServer
```

环境构建补充：依赖使用整合包已有的 GeckoLib/Curios/JEI 本地仓库。ForgeGradle 的工具解析以及本机 Gradle 对 Forge mergetool API 的下载失败，使用官方同版本 `installertools:1.4.4:fatjar` 和 `mergetool:1.1.5:api` 的隔离缓存完成；未修改工程依赖版本，未提交本机路径。

保留失败经过：前两次运行未进入测试，因协议表缺少 17 号包而模组构造失败；第二次增量编译仍加载旧 class。强制完整编译后确认声明进入 class，随后实际运行全部二十六项测试。前两次虽显示 Gradle BUILD SUCCESSFUL，均不算 GameTest 通过。最终日志中的 Forge 更新检查和 Mojang 公钥联网失败未阻断测试批次或正常保存。

本轮未运行真实双客户端、图形/FBO、GUI 缩放、F3+T 或全模组测试矩阵，不将这些项目记为完成。完整世界剧情、角色功能和任务文件中其余十二项继续保留。
