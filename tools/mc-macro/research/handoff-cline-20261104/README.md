# macPvpS / mcPvPmax 接手检查，2026-11-04

## 后续桌面同步（2026-11-04 11:09，本机时间）

用户随后明确要求同步到桌面已有应用。复核候选及源码校验值、重跑离线测试后，仅将 `/Users/a15356015027/Desktop/mcPvPmax.app` 更新为 **1.10.1/build 31**，可执行文件 SHA-256 为 `b841ce415b53ac3eb3df2286d2a61e870c628dc15d94b6f07d3de6f79284130a`。整个包的 8 个文件条目与候选一致，签名校验通过。未启动应用、未自动攻击、未改系统权限或原存档；本轮无游戏实测，不把同步测试安装当成新的实战成功基线。

旧桌面版本完整保存在 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/desktop-sync-1101-20261104-110951/mcPvPmax-1.10.0.app`。项目 `dist` 和 ZIP 未替换。安装记录：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/handoff-cline-20261104/desktop-sync-latest.json`。

**本次桌面版本仍含 Java 内部读数组件，不是纯视觉版；纯视觉原型未集成。** 下文“桌面未改变”及 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/handoff-cline-20261104/artifact-sha256.json` 中的旧桌面哈希是同步前的历史检查证据，当前桌面状态以本节和安装记录为准。

## 当前用户要求与边界

用户要延续既有功能、开关开启后按主手剑/斧自动出手，手动瞄准；参考高水平玩家录像，并明确本轮不调用服务器或游戏 API。截图中的旧要求还允许空手、禁止拿方块/食物/锚等时自动攻击。

**最新限制优先于历史“本机只读 Java 允许”记录。现有应用不满足纯视觉限制。** 未使用游戏实例、未输入攻击、未操作存档、未改权限、未发布或覆盖桌面成功版。本轮不能声称已完成用户的完整软件要求。

项目实际路径：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro`。它位于 Dynasty 大仓库内；只处理本目录，不处理无关的 cod1–6 文件。已有修改和未跟踪文件均保留，未 reset、clean、stash、提交或推送。

## 版本与现有实现

- 桌面 `/Users/a15356015027/Desktop/mcPvPmax.app` 与 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/dist/mcPvPmax.app` 均为 1.10.0/build 30；可执行文件 SHA-256 都为 `246264c33f76c9f3e6fe720ff5932ac92d073f4288ced118f35af40aea4d1b56`。
- 源码和候选已经是 1.10.1/build 31，包含独立开关、剑/斧/空手支持、武器变化取消、盾斧能力检查、攻击恢复确认和受击跳跃相关策略；不能把这些尚未正式发布的修改当成桌面版已具有的功能。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/Sources/ModernTelemetry.swift` 使用 `jdk.attach` 附加组件；`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/modern/src/local/mcmacro/ModernAgent.java` 导入 `net.minecraft`，读取准星实体、交互距离、恢复进度、受击、盾、落地和游戏键位。只读不等于不用游戏 API。
- `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/Sources/AnchorIntegration.swift` 的读数组件并不只由剑斗启动。因此未来只替换剑斗控制器仍不足以保证整个应用不附加 Java。
- 已有 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/Sources/F3Capture.swift` 可复用 ScreenCaptureKit/Vision 思路，但它目前解析坐标和朝向，不是剑/斧、盾、目标或攻击指示器检测器。

## 本轮修复与证据

修改前按文件保存的基线在 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/cline-audit-20261104/baseline`，不要用 Git HEAD 冒充本轮基线，战斗文件在接手前就未跟踪。

原战斗测试 98 项中 97 通过。失败来自旧测试把槽位 1 当作非武器，但真实样本槽位 1 是现在支持的空手。修正测试为显式手持石头，并增加空手仍允许的断言，没有删除空手功能。

新回归在保存的旧控制器上复现四项失败：未捕获鼠标仍可启用、捕获中断不取消、攻击绑定改变仍可出手、暴击准备时捕获中断未释放。

只在 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/Sources/Combat.swift` 增加 `mouseReady` 检查和逐次确认攻击键仍为左键；未调整冷却、距离、跳跃或盾斧时机。新增断言位于 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/Tests/Combat/main.swift`。

复测结果：战斗 105/105、疾跑 21/21、物品/物理输入 102/102，既有搭路/输入核心测试通过。它们是离线策略测试，不是本轮游戏实测。旧搭路功能未扩大验收范围。

隔离应用 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/cline-audit-20261104/app/mcPvPmax.app` 构建成功，签名校验通过；仍包含旧 Java 读数组件，不是纯视觉成品，不应推荐用户当作纯视觉版本运行。桌面与 dist 哈希未改变。

## 纯视觉候选，尚未集成

目录 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/visual-melee-20261104`。

新增 Foundation-only 的观测协议与离线决策器：连续画面确认、武器/槽位变化、未知目标或距离暂停、画面过期/乱序拒绝、开关与菜单/失焦保护、分别使用当前武器画面恢复进度，以及出手后恢复画面确认与超时关闭。

**没有画面检测器、没有系统点击、没有 UI/热键接入、没有纯视觉受击跳跃/暴击实现。** 测试使用合成观测，不证明目标/距离/盾识别准确，不证明游戏伤害、速度或胜率。置信度门槛未在实际画面数据上标定。

最终候选策略测试 102/102 通过，包含未知/不可触及距离拒绝、延迟反馈不能掩盖超时、反复轮询旧帧不重复出手且不阻断下一张新帧，以及非法时钟后显式重新开启的恢复检查。

全量复测命令：

```bash
bash '/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/handoff-cline-20261104/validate.sh'
```

日志保存到 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/cline-audit-20261104`。构建使用原脚本及隔离输出环境变量，不启动应用。

## 视频研究范围

已网上核对作者原始页面：Intel Edits《How to Actually Get Good at Minecraft PvP》（视频 ID `G_-FqCxdnAE`）；Swight《How To DOMINATE Minecraft Shield PvP》（`mLZ5vtzO93Y`）。本地还保存了 Nevoy《The Ultimate Axe PvP Guide》（`PdoGB23Q5Ic`），本轮未完成其连续帧观看。

沿用本地视频及已有 AVFoundation 解码工具。元数据/AVFoundation 的总时长和 nominalFrameRate 存在不一致：接口报告 30 fps 和约两倍时长，但两个选段分别 0.8 秒实际解出 48 个按 1/60 秒间隔递增的帧。因此不据 nominalFrameRate 把动作当作二倍慢放，不对整个容器时间轴作未经核验的结论。

- Swight：查看章节抽样图和 103.0000–103.7833 秒连续 48 帧。画面可见斧头挥动、对手举盾形态随后消失；不能仅凭盾消失区分破盾与主动放盾，不能由此宣称获得真实按键或服务端命中时间。
- Intel Edits：查看章节抽样图，解码 899.6000–900.3833 秒 48 帧。可靠显示并查看了前 12 帧及概览，可见带按键叠层的连击接近演示。其余页在工具中多次显示媒体省略，不能把“读取成功”冒充完成全部逐帧观察。
- 不声称看完所有录像，不声称这些作者是经排名证实的世界最强，不把剪辑示范或按键叠层直接当作当前客户端的精确时序依据。

帧页及原始选段帧位于 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/cline-audit-20261104` 中的 `shield-sequence`、`sword-sequence`。

## 下一步明确缺口

1. 在候选内实现并离线评估画面检测：所选槽位、剑/斧/空手/其他、攻击恢复指示器、菜单及准星目标；必须有不确定/拒绝状态，不能把皮肤颜色或模型大小直接当作精确距离。
2. 取得当前游戏版本、材质包和 GUI 缩放的代表性截图与短录屏，建立正反样本；不自动切用户游戏前台采集。
3. 明确纯视觉构建的应用范围：战斗路径必须不启动两套旧读数组件；其他依赖内部状态的功能不能暗中继续读取，也不能静默删掉而宣称无退步。
4. 加入“仅观察、不点击”模式检查识别表现，再接系统输入与开关；覆盖关闭、菜单、换槽、失焦、重连和异常释放。
5. 完成真实同场景对比后才讨论发布，保留旧应用。纯视觉跳跃重置与暴击需要额外可靠的运动/受击证据；未实现前不得宣传。