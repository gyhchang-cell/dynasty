# cod1 续作 · 2026-10-09

基线：`main` 的 `08c95b34b077d49183664f28d62e39308db69b17`。交付分支：`cod1-continuation-20261009`。输入为用户提供的 cod1 续作任务文件；返还文件固定命名为 `cod1.txt`。

## 本轮结果

青龙偃月刀的最新代码已通过 **56 个单机视角 + 两个真实 TCP 客户端各 14 个场景**。保留已有近裁剪与相机进入神像体积时的渲染保护，没有重复改写 Renderer，没有删除神影、缩小模型、关闭特效或放宽黑屏阈值。截图分辨率均为 1600×1000。

双客户端场景包括 A 单独持刀、B 单独持刀、双方持刀、第一/第三人称、进入神像骨盆/胸部、服务器青龙视觉包、资源重载、Fancy/Fabulous。两端报告记录同一 holder/target UUID，均观察到两个真实玩家。截图中的神像、装备纹理与效果继续显示，天空也可在相机进入模型后看到。

当前内容状态仍为 **0 DONE / 30 PARTIAL / 64 NOT_STARTED**。30 只基础怪已有实现，不能依据旧提示词重新注册其中 21 只。15 精英、12 Boss、25 神器、12 神影未在本轮新增；镇渊帝君与现有维度保持原身份。关刀专项通过不等于每只怪、每个 Boss 或整个整合包验收完成。

## 实际修复

- 基线正式运行时在 FML 注册网络消息时崩溃：`Dynasty packet is missing from frozen wire schema: 17`。InfusionRequest 已注册却未进入冻结的协议表。补齐 `17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1`，不修改已有消息编号、方向或负载。协议回归读取 Forge 实际缓存的握手表，并拒绝遗漏 17 的旧表。
- 蝙蝠局部数量上限测试立即查询刚创建的实体，实体区段尚未在空间查询中可见。改为先等原来的三个真实活体夹具全部可见，再检查原有三只上限；没有改变正式出生限制。
- 树根牢笼测试在整批运行中曾在第一次测试攻击前从 12HP 降到 5HP；补上夹具场地侧墙，隔离邻近战斗干扰，保留原伤害、双玩家破笼、有限束缚与其他效果保留断言。没有确认具体邻场攻击来源，也没有修改正式牢笼耐久。隔离后组合回归及最终 cod1 回归均显示测试攻击前 12HP。
- 现有关刀 QA init 脚本增加可选 `guandaoPrepareOnly`：导出实际 JavaExec 启动参数，释放 Gradle 缓存锁后启动独立 JVM。默认运行方式不变，QA 类没有打进交付 JAR。

## 验证与边界

- 最终 `build` 与 `dynasty_army`：**170/170 required tests passed，退出 0，BUILD SUCCESSFUL**。覆盖当前 30 只基础怪的现有服务器测试及上一轮新增的死士引信中断回归。
- 单机：`solo-PASS.txt`，56/56，进程退出 0。
- 实际双客户端：`host-PASS.txt`、`peer-PASS.txt`，各 14/14，两个进程退出 0。服务器实际视觉包到达两端的检查保留。
- 组合 `dynasty_cod2,dynasty_army` 最后一轮尝试为 **198/200**；墓室驻军与中层飞颅的实体 UUID 查询等待超时。驻军测试的尝试性时序修改未能解决问题，已撤回；相关测试和正式生产逻辑保留。这些失败没有被改成跳过或通过。
- 现有 `tools/art/test_quest_story.py` 为 28 通过、1 错误；Boss 双向链接测试解析说明字符串时出现 JSONDecodeError。本轮没有把它计为通过。
- 首次单机运行与 Gradle/服务器回归并行时被 OOM 杀死，仅捕获 17 帧，明确不算通过。最终单机、双客户端和服务器回归顺序运行。
- 使用真实 Minecraft/Forge 开发客户端、GeckoLib 与 Mesa llvmpipe；Xvfb 通过 TCP 显示套接字运行。音频资源未完整下载，日志保留资源与离线认证警告。本轮不宣称完整整合包音频、所有外部 mod 组合、用户 GPU 或每只怪的联机生命周期已经通过。

最终 JAR SHA-256：`364793cfcd2204df71a0064b6f99bd0f848801b4511b5d25380b01846498363c`。客户端验证使用同一生产源码的已编译类；之后的最终 build 没有再改正式生产逻辑。

## 证据与复跑

[证据目录](evidence/continuation-20261009) 保留三个 PASS 报告、170 项完整服务器日志、基线启动失败、198/200 组合失败、OOM 中断、完整客户端日志、84 帧联系表和四张原始 PNG。`frame-sha256.json` 记录全部原始帧摘要。联系表是缩略 JPEG；PASS 中的像素比例在生成联系表之前直接取自实际原始 framebuffer。原始阈值为单机黑像素比例 ≤0.96、内部视角暗像素比例 ≤0.65、双客户端暗像素比例 ≤0.65。

服务器复跑使用现有脚本和独立的新工作目录：

```sh
bash gradlew --no-daemon --max-workers=2 \
  -Dorg.gradle.jvmargs='-Xmx768m -XX:ActiveProcessorCount=2' \
  -I tools/maintenance/pr_repair_qa.init.gradle \
  -PrepairRun=cod1-fresh-run -PrepairNamespaces=dynasty_army -PrepairHeap=1400m \
  build runGameTestServer
```

关刀复跑使用 `tools/art/guandao-qa/guandao-qa.init.gradle`。单机加 `-PguandaoRegression`；双人使用同一个新输出目录，分别启动 host 与 `-PguandaoPeer`。`-PguandaoPrepareOnly` 将精确 JVM 参数、主类、classpath、工作目录及 MOD_CLASSES 导出到 `build/guandao-world-qa/launch.json`；独立 JVM 必须保留这些字段。单机不要算作真实双人；必须同时获得 host 与 peer 的 PASS，并检查实际截图。

## 返回的剩余任务

`cod1.txt` 移除已经通过的关刀验证前置待办，并校正过时的“21 只未启动”状态。所有 94 项内容的设计和未完成验收继续保留；前 9 只优先补真实世界入口、任务/掉落用途、活动战斗重连及服务器重启、逐项单机与双客户端验收。上一轮确认的引信中断缺陷已经有服务器回归，不能冒称找回了所有历史间歇失败日志，也不能由此直接把死士整项标为 DONE。
