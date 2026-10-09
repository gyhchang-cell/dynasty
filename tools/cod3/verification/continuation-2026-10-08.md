# cod3 续做验证 · 2026-10-08

基线 `2d8e34f32af2c6deba7e9dc687e10bd1fed4e64d`；Java 17.0.20、Forge 47.4.10、Minecraft 1.20.1。使用独立检出、独立 Gradle 缓存和独立测试世界。

| 检查 | 结果 | 覆盖 |
| --- | --- | --- |
| 完整 Java 重新编译 | PASS | 显式禁止增量编译并强制执行，确认包含当前 BossSequenceRunner 源码 |
| Gradle build | PASS | Java、资源、jar、reobfJar |
| dynasty_cod3 专用服 GameTest | 19/19 PASS | 原有 11 项与新增 8 项，包含实体 NBT 恢复、序列定义序列化、异常存档、晚加入快照选择、准确结束 tick、死亡白名单、遗留物持久化；亦复跑工坊、死亡、秘密及既有安全回归 |
| cod3 资源检查 | PASS | 160 目录项、15 骨架、165 动画状态、45 地标模型、6 Boss 绑定 |
| 中英词条检查 | PASS | 692 物品模型、7 模组效果与结构/群系/维度词条 |
| 原文删减检查 | PASS | 1524 行变为 1508 行，仅删除 16 行；十条已完成索引 + 完成的祭坛预警小节和 LootableRemains 建议条目；未改写剩余行 |
| git diff --check（排除原文副本） | PASS | 代码与说明文档空白检查；原文副本保留上传文件自带的尾部空行，另以逐字删除校验验证 |

新增测试类：`Cod3SequenceGameTests`。成功运行日志关键输出：

```text
========= 19 GAME TESTS COMPLETE ======================
All 19 required tests passed :)
BUILD SUCCESSFUL in 2m 55s
```

保留失败经过：首次测试 18/19，发现隐身状态不随原版实体 NBT 自动保存；修复后两个运行仍加载了旧编译类并重复失败。强制非增量编译后确认新字段进入 class。随后 3 GiB 测试进程在准备世界时以 137 退出，没有执行测试，不计为通过。最终改为 1 GiB 专用服堆、768 MiB Gradle 堆，在新世界完整运行 19 项并正常保存关闭，退出 0。没有删除失败断言、减少用例或将中断记作通过。

最终运行命令（`GRADLE_USER_HOME` 为独立已填充缓存）：

```sh
bash gradlew --offline --no-daemon --no-build-cache --max-workers=1 \
  -Dorg.gradle.java.home=/usr/lib/jvm/java-17-openjdk-amd64 \
  '-Dorg.gradle.jvmargs=-Xmx768m -XX:ActiveProcessorCount=2' \
  -I tools/maintenance/pr_repair_qa.init.gradle -I tools/cod3/qa.init.gradle \
  -Pcod3TestHeap=1024m -Pcod3TestRun=build/cod3-sequence-lowmem-20261008 \
  -Pcod3Namespaces=dynasty_cod3 runGameTestServer
```

真实双客户端、玩家死亡重连、GUI 全缩放、F3+T、第一/第三人称效果和性能测试本轮未执行，不以服务端测试代替。此前 FBO 渲染记录仅作为已有几何原语的历史证据，本轮未宣称重新完成图形验收。其余未完成范围与删除证据见 `docs/cod3/continuation-2026-10-08.md`。
