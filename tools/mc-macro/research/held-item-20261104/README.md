# 持剑识别修复，2026-11-04，1.10.2/build 32

用户报告持剑检测十分钟仍提示没有，要求修复并同步桌面、处理输入权限。未取得当时的录像与运行日志，不能声称下面复现的问题是其十分钟故障的唯一根因。

## 本轮修复

- 纠正 1.10.1 中错误加入的 `mouseReady` 近战门槛：本地 Java 源码及字节码确认它来自 `!ignoreFirstMove`，表示恢复后的首次鼠标移动，不等于游戏是否捕获鼠标。`active` 本身已含真实捕获、菜单、存活保护。修改前，静止剑/斧/空手的四例新测试均失败；修改后通过。锚和搭路的相机准备逻辑未改。
- 主手身份与可运行状态分开：按 selected 实际槽位判断，缺少 combat、过期、菜单、失焦或权限缺失不再笼统提示没有剑。
- 26.1 普通持剑连点使用已有现代读数，避免等待已被现代分支停止的 1.8.9 读数组件。仍只允许剑与真实左键新按压；剑斗开启时连点让出控制。
- 已连接后持续超过一秒无新包会释放读数会话，让已有服务重试；首包超时保留，非零启动退出和启动异常及时提示；回调按会话隔离。
- 连接检测暂停自动输入，支持现代路径，15 秒内显示最近主手、槽号、物品 ID、版本、连接和权限。历史主手标注年龄且只展示，不用于授权攻击。修复现代分支提前返回而永远跳过检测计时的问题。
- 显式维护参数 `--request-input-permissions` 使用正常系统许可申请；`--permission-report` 让应用自身报告授权状态。仅维护启动会定时刷新，不读写 TCC 数据库，不增加无关权限，不自动开启剑斗。

## 验证

战斗 103/103；主手 41/41；现代读数组件本机回环 UDP 集成 24/24；疾跑 21/21；物品/物理输入 102/102；旧核心回归通过。两条错误理解 mouseReady 的历史断言已换为真实 inactive 与静止持剑测试，不声称原错误断言仍应通过。

主手测试含九个快捷栏槽、错误和过期拒绝，以及 12000 个样本覆盖的 **600 秒模拟时间**，不是十分钟游戏实测。UDP 测试注入模拟启动器，未附加用户游戏；覆盖鉴权、重复序号、缺失/无效读数、连接后断流、重连会话及迟到回调。

完整构建、签名、桌面安装后八个包文件一致性通过。未操作用户游戏、未发送攻击、未修改原存档。未完成真实持剑场景验收，不能宣称已验证所有现场问题。

测试入口：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/held-item-20261104/validate.sh`。
测试与构建日志：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/candidates/held-item-1102`。
修改前源码：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/held-item-fix-1102-before`。

## 安装与权限

已同步并正常打开 `/Users/a15356015027/Desktop/mcPvPmax.app`：1.10.2/build 32，哈希 `c5caa7b20d8e4246ad56235d34d5fec755ebc82802dfb586e5a01ebc7e64ff52`。旧版完整保存在 `/Users/a15356015027/Desktop/dynasty/tools/mc-macro/.build/backups/desktop-1102-20261104-185630/mcPvPmax-1.10.1.app`，dist/ZIP 未替换。

安装记录：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/held-item-20261104/install.json`。
权限快照：`/Users/a15356015027/Desktop/dynasty/tools/mc-macro/research/held-item-20261104/permission-check.json`。
应用自身实时维护报告：`/Users/a15356015027/Library/Application Support/mcPvPmax/permissions.json`。

**安装后首份报告辅助功能、输入监控、输入监听、录屏都为 false，剑斗关闭。** 已正常申请并打开系统设置，但当前代理的 osascript 被拒绝辅助访问，不能代点，等待用户完成授权；不能写“权限已上好”。密码/Touch ID 只能用户本人确认。

**仍采用原 Java 读数组件，不是纯视觉版。** 本轮不扩大其兼容版本和实战成功范围，先前纯视觉目标尚未完成。