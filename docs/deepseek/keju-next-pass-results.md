# 科举下一轮改动结果（答题界面 / 一次性会话 / 严格可重载题库）

本轮只动**科举答题界面、科举会话与题库加载校验**，没有新建第二套考试系统。
范围白名单内共 6 个文件被修改、15 个文件新增；奖励与存档语义**逐项对照过，保持原样**。

* 开工前先复核了 `DynastyKeju`、`KejuScreen`、`ClientKeju`、两个科举包、`questions.json`（3 档 / 45 题 / 0·400·1600 / 12·25·45）、`tools/art/verify_keju.py`
  与旧报告，确认这些内容**已存在**，本轮不重复实现。
* 未改 `DynastyNetwork.java`（注册表）、`Dynasty.java`、`DynastyUsables.java`、`command/DynastyCommands.java`、
  `DynastyMerit/Stats/Advancements/SlotProgression`、`structure/`、`worldgen/`、`bounty/`、`puzzle/`、
  任何 `assets/**/lang/`、贴图、模型、配方、战利品、任务书或全局生成器；题库 JSON 一字未改。
* 未运行 `exportModpack` / `exportMod` / `syncToHMCL`，未覆盖 jar、未同步启动器、未 git add/commit/push。

## 1. 实际改动文件

### 修改（6）

| 文件 | 改动 |
| --- | --- |
| `src/main/java/com/dynasty/DynastyKeju.java` | 会话化改造：题库改由 `KejuReloadListener` + `KejuBankCache` 提供、`/reload` 生效；出题走 `KejuSessionRegistry.open`（快照 + 令牌）；`handleAnswer` 先验证再消费；奖励代码逐行保留 |
| `src/main/java/com/dynasty/client/KejuScreen.java` | 重写为可阅读试卷面板：按字体宽度换行、选项高度随内容增长、滚轮 + 滚动条、鼠标/数字键/方向键/Tab/Enter、明确的「确认作答」按钮、一次界面只发一个包 |
| `src/main/java/com/dynasty/client/ClientKeju.java` | 打开前校验题干与选项数（非法包直接忽略并记日志，不静默修补） |
| `src/main/java/com/dynasty/network/OpenKejuPacket.java` | 方向校验（只收 PLAY_TO_CLIENT）、`readUtf` 按题库同源上限拒绝超长字段、补测试用访问器；字段仍是 1 int + 4 string |
| `src/main/java/com/dynasty/network/AnswerKejuPacket.java` | 方向校验（只收 PLAY_TO_SERVER）、从上下文取真实发送者后再 `enqueueWork`、补访问器；字段仍是 2 int |
| `tools/art/verify_keju.py` | 判定收紧（类型 / 空白 / 布尔 / 严格递增 / 首档为 0 / 长度与数量上限）；新增 `--bank` 便于用临时题库测试；核对 Java 常量与网络长度上限同源 |

### 新增

`src/main/java/com/dynasty/keju/`（纯逻辑与 MC 胶水分开）：

* `KejuRules.java` — 题库契约的唯一来源：档位 / 题目 / 选项 / 答案的解析与严格校验，上限常量（每档 10..200、最多 8 档、总 800、题干 200 字、选项 100 字）、`tierFor`、兜底题库自检。**不修正任何坏数据**。
* `KejuSession.java` — 一次性会话快照（令牌、玩家、档位与奖励、题目、答案、开题时间）。
* `KejuSessionRegistry.java` — 每玩家一个会话；`submit` 先验证再消费（NO_SESSION / WRONG_TOKEN / ILLEGAL_CHOICE / ACCEPTED）。
* `KejuCooldown.java` — 30 秒档位功名冷却，时钟注入（可测边界），`pruneExpired` 只清过期。
* `KejuServerState.java` — 按服务器实例（身份比较）持有会话与冷却；换实例即换槽位，关闭即清空。
* `KejuBankCache.java` — 现役题库；只有整份合法才替换，失败保留旧库。
* `KejuNet.java` — 线协议契约：方向常量 + 长度上限（引用 `KejuRules` 常量）。
* `KejuReloadListener.java` — 数据包重载监听（`SimplePreparableReloadListener`）：工作线程读取+校验，主线程决定是否替换。
* `KejuEvents.java` — 科举自己的订阅类：`AddReloadListenerEvent`（挂题库监听）、`ServerStoppingEvent`（清会话与缓存）、`PlayerLoggedOutEvent`（丢会话 + 只清过期冷却）。
* `KejuLayout.java` — 界面纯几何（面板/可视区/滚动/命中换算），与 `KejuScreen` 共用同一份公式，因此可在无客户端环境断言布局不越界。

`tools/keju/`：`run_keju_tests.sh`（一条命令跑全部）、`KejuQaTests.java`（106 项生产类直调测试）、
`test_verify_keju.py`（32 项临时坏题库压正式校验器）、`test_frozen_files.py`（冻结文件哈希对照）、
`frozen_baseline.json`（开工时基线）、`keju-qa.init.gradle`（只导出 Gradle classpath，供 javac 直跑，不改 `build.gradle`）。

## 2. 三项改进的落点

### A. 可阅读、可操作的考试界面（`KejuScreen` + `KejuLayout`）

* 面板：深色描边 + 米色纸面 + 居中标题（复用已有翻译键 `screen.dynasty.keju`），全部用 `GuiGraphics` 绘制，**没有新增 PNG / 背景大图 / 粒子**。
* 排版：题干与每个选项都用 `font.split(...)` 按**实际字体宽度**换行；选项卡片高度 = 行数 × 9 + 8，随内容增长；面板宽度按窗口逻辑尺寸在 200..420 之间取值，面板绝不越出窗口（极小窗口退让为整屏）。
* 溢出：内容超过可视区时用 `enableScissor` 裁剪 + 滚轮滚动（`mouseScrolled`），右侧画细滚动条；**没有截断文字，也没有缩小字号**；键盘切换会把目标选项滚进可视区。
* 操作：鼠标点击选中；数字键 1/2/3（含小键盘）选中；↑↓ 与 Tab/Shift+Tab 循环；Enter（含小键盘）提交；底部固定一行提示随状态变化。
* 提交：有明确的「确认作答」按钮，未选择时 `active=false`；`submitted` 标志保证**同一次界面最多发一个答案包**（连点无效）；提交后立即关闭，**没有结果回包，界面不假装知道对错**，判分反馈仍由服务端聊天给出。
* Esc 由父类处理：只关闭界面，不判错、不发奖励；`isPauseScreen()` 仍为 `false`；试卷右键与 `/dynasty keju` 入口未动。
* 纯几何在 `KejuLayout` 里，`KejuScreen` 与它共用同一份公式（面板 / 可视区 / 内容高度 / 选项偏移 / 滚动夹取 / 命中换算），因此可以在无客户端环境断言布局。

### B. 服务端一次性答题会话（`KejuSession` + `KejuSessionRegistry` + `KejuServerState`）

* 会话快照含**服务端生成的令牌、玩家 UUID、档位与奖励、题目与正确答案、开题时间**；客户端只提交令牌与 1..3 选项，包里没有任何身份 / 答案 / 奖励字段。
* 令牌由每服务器实例的计数器发放（起始随机、递增、永不为 0），**与题目下标无关**（旧实现 `tierIndex * 1000 + index` 同题会重用）。
* 先验证再消费：无会话 → `NO_SESSION`；令牌不匹配 → `WRONG_TOKEN`（**不消费**，题目仍有效）；选项不在 1..3 → `ILLEGAL_CHOICE`（**不消费**）；只有令牌与选项都合法才消费并判分。答错一样结束本次题目。
* 重新开题替换旧会话（旧令牌立刻失效且不影响新题）；登出丢弃会话并只清理**已过期**的冷却（30 秒内保留，断线重连绕不过去）；服务器关闭清空该实例的会话、冷却与题库缓存。
* 管理员 `/dynasty answer <1-3>` 与外部接口 `openExam(ServerPlayer)` / `pending(Player)` / `handleAnswer(ServerPlayer,int,int)` 保持不变。
* 两个 handler 都核对方向（Open 只收 `PLAY_TO_CLIENT`，Answer 只收 `PLAY_TO_SERVER`），发送者一律取 `context.getSender()`，不信任包内身份；非法包安全拒绝。
* 没有加入倒计时、每日次数、费用、地点限制或竞赛等新玩法；答题时长限制维持现状（无限制）。

### C. 严格、可重载的题库（`KejuRules` + `KejuBankCache` + `KejuReloadListener` + `KejuEvents`）

* 统一判定（Java 加载器 = Python 校验器 = 网络长度上限，脚本会直接读 Java 常量核对）：档位 id 非空唯一、中英名非空、
  门槛为非负整数且**严格递增**（第一档必须 0）、奖励为正整数、每档 10..200 题、题库 ≤ 8 档 / ≤ 800 题、
  题干与三个选项均为非空字符串（拒绝空白串）、选项互不重复、题干全库不重复、
  答案必须是**真正的整数 1..3**（布尔 / 字符串 / 小数一律拒绝）、题干 ≤ 200 字、选项 ≤ 100 字。
* **不再静默修正**：答案越界不再被改成 1，四个选项不再被截成三个，门槛乱序不再被重排；任何一条不合法都让**整份新题库不生效**。
* 报错带路径 + 档位（含 id）+ 题目 / 选项位置 + 原因，例如
  `data/dynasty/keju/questions.json：档位 #1（id=metropolitan） 题目 #0：correct 越界：4，必须 1..3`。
* 校验失败保留上一份有效题库；首次加载没有有效题库（含文件缺失）时回落到现有 **7 题**内置兜底并打日志；损坏 JSON / 缺文件都不会抛到玩法层。
* `/reload` 走 Forge 服务端数据重载事件（科举自己的 `KejuEvents`，未碰主类与悬赏监听器）：重载成功后**新开题用新题库**，
  **已打开的题目按开题快照判分并发放原档位奖励**，重载失败不破坏进行中的会话、不重置冷却。

## 3. 奖励与存档冻结对照（开工 / 收尾各一次）

* 档位、门槛、奖励：`questions.json` 哈希与开工时一致（3 档 / 15+15+15 题 / 0·400·1600 / 12·25·45），本轮未改该文件。
* 每次合法答对仍然是：龙威 + 疾风 + 天命（各 `20 * 180` tick、等级参数 `0`）+ 一本可书写书；
  冷却仍然只限制**档位功名**（`KejuRules.REWARD_COOLDOWN_MS == 30_000L`），效果与书不受冷却影响 —— 见 `DynastyKeju.java` 第 130-146 行
  （`DRAGON_MIGHT / SWIFT_WIND / MANDATE_OF_HEAVEN / WRITABLE_BOOK / addMerit / DynastyMerit.onEvent(player,"keju") / DynastyAdvancements.awardForEvent(player,"keju")`）。
* 首次 +30 功名仍是 `DynastyMerit.onEvent(player, "keju")` 的一次性事件（`dynasty_merit_evt_keju` 存档标志），**未删除、未重复发放**；`dynasty:exam_passed` 与既有任务 / 饰品槽联动未改。
* 没有新增跨存档的考试成绩、每日记录、称号或奖励领取表，没有迁移玩家存档。
* 机器证据（`python3 tools/keju/test_frozen_files.py`，与开工基线比对）：

```
冻结文件核对：10 个未变，0 个变化，0 个丢失
冻结文件自检：通过 ✅（奖励 / 存档 / 官阶 / 网络注册表 / 题库均为开工时内容）
```

  基线覆盖 `questions.json`、`DynastyMerit`、`DynastyStats`、`DynastyAdvancements`、`DynastySlotProgression`、
  `DynastyNetwork`、`DynastyUsables`、`command/DynastyCommands`、`Dynasty.java`、`build.gradle`。
  （注：`git diff --stat` 里 `DynastyNetwork.java` 有 6 行插入，那是**并行代理**的悬赏改动、早于本轮开工；与开工基线对照可确认本轮没有动它。）
* 背包满时的书本奖励**保持原样**：`player.getInventory().add(...)` 的返回值没有被检查，因此放不下时书不会进背包；
  原版在这情况下是否掉地/丢失本轮**没有核实**。按任务要求未改成待领取 / 邮寄 / 补发系统，留待主代理决定（见 §6）。

## 4. 测试命令与结果（都是本轮真实执行）

```bash
bash tools/keju/run_keju_tests.sh        # 一条命令跑完下面四步
  == 1/4 编译源码 ==                     ./gradlew --offline compileJava → 通过
  == 2/4 Java 测试（生产类直调） ==       通过 106 项，失败 0 项
  == 3/4 Python：正式校验器 + 临时坏题库 == 通过 32 项，失败 0 项
  == 4/4 冻结文件核对 ==                 10 个未变，0 个变化，0 个丢失
  ✅ 科举测试全部通过

python3 tools/art/verify_keju.py
  科举题库：档位 3 个，题目 45 条，Java 兜底 7 条
  科举题库自检：通过 ✅（选项 3 个 / 答案整数 1..3 / 无重复题干 / 门槛严格递增且首档为 0 / 每档 10..200 题 / 题干 ≤ 200 字 / 选项 ≤ 100 字）
```

* `tools/keju/KejuQaTests.java` 直接调用生产类（`KejuRules` / `KejuSessionRegistry` / `KejuCooldown` / `KejuServerState` / `KejuBankCache` / `KejuNet` / 两个网络包 / `KejuLayout`），
  classpath 由 `tools/keju/keju-qa.init.gradle` 从 Gradle 导出（未改 `build.gradle`，未加依赖）。
* 覆盖：题库上限与整库形状、档位字段（错类型 / 空白 / 重复 id / 门槛乱序或相等 / 首档非 0 / 奖励非正）、
  题目与选项（第 4 个选项 / 选项不足 / 选项重复 / 空与空白题干 / 题干非字符串 / 题干全库重复 / 题干 201 字 / 选项 101 字 / 接近上限仍通过）、
  答案（0 / 4 / true / "1" / 1.5 / 缺失）且断言**坏题库整份不生效**、缓存（装入 / 失败保留旧库 / 兜底 / 清空 / 兜底 7 题自检）、
  会话（合法一次生效、重复提交无二次、旧令牌与错玩家与非法选项都不消费、重开替换、答错也结束、登出与清空、重载后旧会话按快照判分、新会话用新库）、
  冷却（注入时钟：29.999 秒不可领 / 30.000 秒可领、剩余时间、登出只清过期、断线重连仍要等满、清理不过期不丢、清空）、
  服务器槽位（同实例复用、换实例隔离、关闭清空、关闭别的实例不误清）、
  界面几何（下方表格）、网络（方向拒绝、长度上限拒绝、两个包编解码往返、越界选项不在解码期被修正）。
* `tools/keju/test_verify_keju.py` 用**临时题库**（临时目录，不碰正式题库）压 `tools/art/verify_keju.py`：
  合法库通过、缺文件、损坏 JSON、根节点非对象、tiers 空、每档 < 10 题、单档 > 200 题、档位 > 8、第 4 个选项、选项重复、
  答案 0/4/true/"1"/1.5/缺失、门槛倒序与相等、首档非 0、minMerit 是字符串或布尔、奖励为 0、id 重复或为空、中文名空白、
  空题干 / 空白题干 / 题干非字符串 / 题干重复 / 题干超长 / 选项超长 —— 全部要求**退出码 1 + 报出原因 + 无 traceback**。
* 界面几何实测（窗口逻辑尺寸 → 面板 / 可视区 / 文字宽 / 长内容滚动上限；`8 行题干 + 5/4/6 行选项`）：

```
窗口 1280×720  → 面板 420×688 可视区 611 文字宽 386 长内容滚动上限 0
窗口  640×360  → 面板 420×328 可视区 251 文字宽 386 长内容滚动上限 2
窗口  426×240  → 面板 394×208 可视区 131 文字宽 360 长内容滚动上限 122
窗口  320×180  → 面板 288×148 可视区  83 文字宽 254 长内容滚动上限 170
窗口  214×120  → 面板 200×96  可视区  31 文字宽 166 长内容滚动上限 222
窗口  200×110  → 面板 200×96  可视区  31 文字宽 166 长内容滚动上限 222
窗口  150×90   → 面板 150×90  可视区  25 文字宽 116 长内容滚动上限 228
```

## 5. 没有验收的部分（不要当成已完成）

* **界面没有实机验收**：本轮**没有启动客户端、没有任何真实界面图**。换行后的观感、字号是否舒服、滚动条位置、按钮手感、
  鼠标连点与 Esc 关闭等只在**逻辑层与几何层**用测试断言（`KejuLayout` + 键鼠分支），没有在游戏里看过一眼。
  要真机确认请在 `build` 下的独立测试世界开一次试卷（不要打开用户已有世界）。
* **没有跑 GameTest / 独立测试世界**：没有执行 `runGameTestServer`（避免与并行代理抢 Gradle），
  因此 `/reload` 端到端、`AddReloadListenerEvent` 是否被 FML 发现并挂载、`PlayerLoggedOutEvent`、`ServerStoppingEvent`
  只有代码层依据（`@Mod.EventBusSubscriber(modid = Dynasty.MODID)` 与 `bounty/BountyService` 是同一包层级、同一注解的既有模式）与单元测试；
  服务器启动日志里的"科举题库已装载：N 档 / M 题"尚未实际观察过。
* **多人同时答题、断线重连、服务器重启后的冷却**未实测：冷却表是内存态，进程重启会清空（与原实现一致，本轮未改成持久化）。
* 书本奖励在背包满时的原版行为未核实（见 §3）。

## 6. 白名单之外发现的问题与建议（本轮**没有**顺手改）

1. `DynastyNetwork.java` 里两个科举包仍未声明方向（本轮只能在各自 handler 里核对 `context.getDirection()`）。
   最小补丁建议：改用带方向的注册重载
   `registerMessage(index, type, encoder, decoder, handler, NetworkDirection.PLAY_TO_CLIENT / PLAY_TO_SERVER)`。
   该文件已有并行改动，本轮按白名单不动。
2. 主代理若要把提示本地化：建议新增（本轮未改任何 lang 文件）
   `screen.dynasty.keju.confirm`、`screen.dynasty.keju.hint.select`、`screen.dynasty.keju.hint.ready`、`screen.dynasty.keju.hint.submitted`
   与服务端消息 `keju.msg.expired / keju.msg.stale / keju.msg.bad_choice / keju.msg.correct / keju.msg.wrong / keju.msg.cooldown`。
   当前界面新提示沿用本模块既有中文直写风格（复用 `screen.dynasty.keju` 作标题）。
3. `DynastyKeju.grant` 里书本奖励没有检查 `Inventory.add` 的返回值（§3 记录）。若决定改成待领取 / 掉地，建议放在科举自己的文件里做，避免动奖励系统。
4. `tools/art/verify_keju.py` 现在支持 `--bank <path>`：如果导出流程以后要校验追加题库，可以直接传参；默认行为与判定口径不变（只收紧）。
5. `tools/keju/keju-qa.init.gradle` 会往 `build/keju-qa-classpath.txt` 写一个临时文件（`build/` 已被 git 忽略），不进入产物。
6. `build.gradle` 的 `exportModpack` 里 `verify_keju.py` 的失败只被 `catch` 成一行 lifecycle 日志（不会中断导出）。
   本轮沿用该语义（没有改 `build.gradle`）；若希望题库自检真正拦住打包，请主代理把这段改成失败即抛。

## 7. 待主代理补做

* 在独立测试世界实机看一次界面（窗口 1280×720、小窗口、高 GUI 缩放、超长中文题干）并留真实截图。
* 跑一次 `/reload` 观察日志与"新题用新库、旧题按快照判分"的实机表现；跑一次登出 / 关服确认会话与冷却清理。
* 决定背包满时书本奖励的处理方式（保持现状 / 待领取）。
* 决定是否给两个科举包在注册表里补方向声明（§6.1）。
