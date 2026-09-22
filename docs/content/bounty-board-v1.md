# 悬赏告示板与委托系统 v1（bounty-board-v1）

可选日常委托系统：独立的悬赏告示板方块 + 专用界面 + 三种目标 + 每日轮换 + 服务端权威判定。
MC 1.20.1 / Forge 47.4.10。开工前已确认**仓库里没有既有悬赏系统**（全库 grep `悬赏/bounty/委托` 无命中），
因此按独立系统实现，未与 FTB 主线任务耦合。

## 1. 使用方式

1. 合成**悬赏告示板**（3×3：木板×6 + 纸×2 + 墨囊×1，木板用原版 `#minecraft:planks` 标签，产出 1 个）。
   首次拿到木板会点亮配方（原版 `recipe_unlocked` 进度，见 §4）。
2. 放下后**右键**打开界面（服务端建立会话，有效期 60 秒；方块被拆或走远会失效）。
3. 界面左侧是**今天发布的 6 条**委托，右侧是选中委托的详情（目标、进度、奖励预览）与四个按钮：
   **接取 / 放弃 / 提交 / 领取奖励**。状态前缀标出 `[可接] [进行中] [可领取] [已完成] [未满足条件]`。
4. 每人同时最多 **3 个**已接委托；所有告示板共享同一个人的记录，换一块板不会多接。
5. 界面文字全部走翻译键（`dynasty.bounty.*`），补一条不会给界面塞原始键名；长描述会自动折行且限制行数。

### 三种委托的实际规则

| 类型 | 完成方式 | 关键约束 |
| --- | --- | --- |
| **收购** | 点「提交」时校验并扣除物品 | 只从**主背包 + 快捷栏**（`Inventory.items` 36 格）取；盔甲、副手、Curios 饰品、外部容器不动。**先算后扣**：不够就整笔拒绝，不会扣一半 |
| **讨伐** | **接取之后**亲手击杀指定生物 | 只认本人击杀或**可追溯到本人的投射物**；环境死亡、其他玩家、来源不明一律不计；**宠物/驯服生物击杀不计入**（说明与实现一致，已写进委托描述） |
| **考察** | **接取之后**亲自进入指定维度 | 已是项目里**已有维度**（不新增）；考察检查每 40 tick 跑一次**只遍历在线玩家**，不扫世界；接取时已在该维度 → 下一次检查（约 2 秒）完成，界面描述同步说明 |

界面支持的反馈：满额（`最多同时接 3 个`）、条件未满足、材料不足、背包空间不足（奖励**保留**不丢地上）、
重复接取、重复提交、重复领奖、会话失效。

## 2. 委托列表（18 条，全部数据驱动）

**收购 10**（只数主背包；奖励为少量绿宝石 + 经验）

| ID | 目标 | 数量 | 权重 | 奖励 |
| --- | --- | --- | --- | --- |
| `dynasty:acquire_wheat` | 小麦 | 16 | 12 | 3 绿宝石 + 2 经验 |
| `dynasty:acquire_carrot` | 胡萝卜 | 16 | 12 | 3 绿宝石 + 2 经验 |
| `dynasty:acquire_potato` | 马铃薯 | 16 | 12 | 3 绿宝石 + 2 经验 |
| `dynasty:acquire_brown_mushroom` | 棕色蘑菇 | 12 | 10 | 3 绿宝石 + 2 经验 |
| `dynasty:acquire_string` | 线 | 16 | 10 | 3 绿宝石 + 2 经验 |
| `dynasty:acquire_leather` | 皮革 | 8 | 8 | 4 绿宝石 + 3 经验 |
| `dynasty:acquire_paper` | 纸 | 16 | 8 | 2 绿宝石 + 2 经验 |
| `dynasty:acquire_bamboo` | 竹子 | 16 | 8 | 2 绿宝石 + 2 经验 |
| `dynasty:acquire_cobblestone` | 圆石 | 32 | 12 | 3 绿宝石 + 2 经验 |
| `dynasty:acquire_logs` | 任意原木（`#minecraft:logs`） | 32 | 12 | 3 绿宝石 + 2 经验 |

**讨伐 4**（只用普通原版敌对生物，本轮不含 Boss）

| ID | 目标 | 数量 | 权重 | 奖励 |
| --- | --- | --- | --- | --- |
| `dynasty:hunt_zombie` | 僵尸 | 8 | 12 | 4 绿宝石 + 4 经验 + 面包×4 |
| `dynasty:hunt_skeleton` | 骷髅 | 8 | 12 | 4 绿宝石 + 4 经验 + 箭×8 |
| `dynasty:hunt_spider` | 蜘蛛 | 6 | 10 | 3 绿宝石 + 4 经验 |
| `dynasty:hunt_creeper` | 苦力怕 | 4 | 8 | 5 绿宝石 + 5 经验 + 火把×8 |

**考察 4**（前置是**已核实存在**的「进入该维度」成就文件，不是猜的 ID）

| ID | 维度 | 权重 | 前置 | 奖励 |
| --- | --- | --- | --- | --- |
| `dynasty:explore_celestial` | `dynasty:celestial_dynasty` | 8 | `dynasty:entered_celestial` | 4 绿宝石 + 4 经验 |
| `dynasty:explore_underworld` | `dynasty:underworld` | 8 | `dynasty:entered_underworld` | 4 绿宝石 + 4 经验 |
| `dynasty:explore_jiuxiao` | `dynasty:jiuxiao` | 6 | `dynasty:entered_jiuxiao` | 5 绿宝石 + 5 经验 |
| `dynasty:explore_dragon_palace` | `dynasty:dragon_palace` | 6 | `dynasty:entered_dragon_palace` | 5 绿宝石 + 5 经验 |

奖励纪律：只用**适量绿宝石 / 普通补给 / 少量经验**；不奖励 Boss 信物、毕业装备、永久属性、饰品槽。
`BountyRules.isForbiddenReward` 会在加载时拦截 `*_token` / `*seal*` / `rebel_head` / `emperor_bone` /
`xuantian_jade` / 毕业武器等，加载器会把这类定义**记日志并跳过**。

防「低成本套利」：告示板**只发不收**，绿宝石不能从告示板换回材料；一次发布同一条委托只会出现一次（每天 6 条里
每条实例只有一份），奖励量级（2–5 绿宝石）明显低于材料的正常劳作成本，且同一实例**每名玩家只能领奖一次**。


## 3. 数据格式示例

目录：`src/main/resources/data/dynasty/bounty_offers/<名字>.json`（**数据包可覆盖**，改完 `/reload` 即生效）。

```json
{
  "id": "dynasty:acquire_logs",
  "type": "acquire",              // acquire / hunt / explore
  "target_kind": "item",          // item / entity / dimension（与 type 必须匹配）
  "target": "#minecraft:logs",    // 物品 ID、实体 ID、维度 ID；物品支持 #标签
  "amount": 32,                   // 目标数量（1..512）
  "weight": 12,                   // 每日抽取权重（1..100）
  "title": "dynasty.bounty.acquire_logs.title",
  "description": "dynasty.bounty.acquire_logs.desc",
  "reward": { "emeralds": 3, "experience": 2, "items": [ { "item": "minecraft:bread", "count": 4 } ] }
}
```

可选字段 `prerequisite`（成就 ID，例如 `dynasty:entered_jiuxiao`）：不满足时该条在界面显示 `[未满足条件]`
且无法接取；加载时会核对成就文件是否存在。

**加载与容错**：`BountyOffers` 是 `SimplePreparableReloadListener`，逐条校验
（type 与 target_kind 匹配、amount、weight、奖励范围与禁用物品、标题/描述必须是 `dynasty.bounty.` 开头）。
坏定义只打印 `[bounty] 跳过一条委托定义 → <文件>：<原因>` 并跳过，**不会让服务器起不来**。
重载只替换定义池，**不动玩家存档**：已接委托的目标/数量/奖励是接取时写进存档的快照，重载后不会变。

## 4. 每日发布与刷新

* 每游戏日发布 **6 条**，日界取自**主世界** `getDayTime()/24000`（睡觉跨日会正常刷新）。
* 抽取是**决定论**的：按委托 ID 排序后用「日数」播种做加权不放回抽样 → 同一世界同一天，
  任何玩家、任何重启、任何重载，拿到的 6 条完全一致。
* 每人每条的**发布实例 ID** = `日:槽位:委托ID`；「每个发布实例每名玩家最多领奖一次」靠它记录。
* **跨日**：已接委托不消失，目标与奖励保持接取时的快照，可以跨天完成与领奖。
* **放弃**：删除该次记录（进度一起丢弃），不发奖励；如果今天这条还在发布列表里，可以重新接取，
  但讨伐数量从 0 重新数（不继承）。
* **时间倒退**：状态机保留「已见最高日」水位，`effectiveDay = max(真实日, 水位)`，倒退时**不重新发布**旧日期实例，
  旧日期的已领记录仍然拦着，所以倒退时间拿不到重复奖励。
* **记录清理**：已领记录按天保存，只保留最近 16 天（`KEEP_DAYS`）。旧日期永不重发，清理不会重新打开领奖机会。

## 5. 存档与多人

* 采用 **SavedData**（挂在主世界 DataStorage，ID `dynasty_bounty`），按**玩家 UUID** 存一份纯文本行状态。
  选它的理由：需求要求「按 UUID / 重启保留 / 死亡重生保留 / 区分不同世界」——SavedData 天然按存档隔离，
  不挂在实体上（死亡重生无影响），且专用服务器不需要加载任何客户端类。
* 行格式（前缀 `bounty-v1`）：`bounty-v1|lastDay|publicationDay`、`PUB|...`（当天发布快照）、
  `ACC|instanceId|...|progress|done|submitted`（已接委托）、`CLM|day|instanceId`（已领记录）；
  **坏行跳过**（单行解析失败不影响其他数据，也不阻止服务器启动）。
* 不同玩家各自一份状态、互不覆盖；不同存档/世界各自一份 SavedData。
* **不做**任何 FTB 写入，不借用 FTB 任务 ID，不改现有进度。

## 6. 服务端权威与防刷

* 客户端只发**操作意图**（`BountyActionPacket(action, instanceId)`），数量、进度、奖励全部服务端重算。
* 每次操作都重新校验：会话存在且未过期（60 秒）、**方块还在**、玩家在 6 格内、实例属于当天发布、
  状态合法（未满 3、未重复接、未领过、类型匹配）。
* 重复点击/重复包：接取→`ALREADY_ACCEPTED`；提交→`ALREADY_DONE`（**不再扣材料**，`consumedOnSubmit`
  是一次性的，读一次即清零）；领奖→`ALREADY_CLAIMED`。
* 关闭界面后发包：会话仍在 60 秒窗口内会正常处理；过期或走远 → 提示「请先右键告示板再操作」，**不扣不发**。
* 提交事务边界：**先算（当前可提交数量）→ 判定 → 记录状态 → 再扣物品**；若下游扣除数与预期不符，
  回滚状态并提示「物品已退回」。**边界说明**：这是同 tick 内「先判后扣」，没有跨存档事务，
  服务器在扣物品与写盘之间硬崩（极小概率）时可能出现「材料已扣、状态未落盘」的一格误差——
  不声称绝对事务安全。
* 奖励发放前检查**背包空位**（按奖励叠数计），不足时返回 `NO_SPACE` 并**保留可领取状态**，不丢地上。

## 7. 修改文件

**新增（独立包 `com.dynasty.bounty`，纯逻辑与 MC 胶水分开）**

```
src/main/java/com/dynasty/bounty/BountyModel.java         纯数据模型（Type/TargetKind/Stack/Reward/Offer/Instance）
src/main/java/com/dynasty/bounty/BountyStateMachine.java  纯状态机 + 存档行格式（javac 可直接测）
src/main/java/com/dynasty/bounty/BountyRules.java         纯规则：日界、决定论抽取、定义校验、空间判定
src/main/java/com/dynasty/bounty/BountyOffers.java        数据包加载（逐条校验 + 记日志跳过）
src/main/java/com/dynasty/bounty/BountyBoardData.java     SavedData（世界级、按 UUID）
src/main/java/com/dynasty/bounty/BountyView.java          服务端→客户端界面数据
src/main/java/com/dynasty/bounty/BountyBoardBlock.java    告示板方块
src/main/java/com/dynasty/bounty/BountyService.java       会话/发布/接取/放弃/提交/领奖/击杀与考察钩子
src/main/java/com/dynasty/network/BountyBoardPacket.java  S2C 界面数据
src/main/java/com/dynasty/network/BountyActionPacket.java C2S 操作意图
src/main/java/com/dynasty/client/ClientBounty.java        客户端持有界面数据
src/main/java/com/dynasty/client/BountyBoardScreen.java   代码绘制界面（GUI 缩放自适应、长文本折行）
src/main/resources/assets/dynasty/blockstates/bounty_board.json
src/main/resources/assets/dynasty/models/block/bounty_board.json
src/main/resources/assets/dynasty/models/item/bounty_board.json
src/main/resources/data/dynasty/recipes/bounty_board.json
src/main/resources/data/dynasty/advancements/recipes/bounty_board.json
src/main/resources/data/dynasty/bounty_offers/*.json      18 条委托定义
tools/bounty/BountyRulesTest.java                         36 条断言的纯逻辑测试（javac 直接跑）
tools/bounty/verify_offers.py                             数据包/资源/词条自检
docs/content/bounty-board-v1.md                           本文件
```

**小幅增补（只加必要注册/词条）**

```
src/main/java/com/dynasty/DynastyBlocks.java          +1 个方块注册（BOUNTY_BOARD）
src/main/java/com/dynasty/DynastyTabs.java            +1 行（创造栏美食段）
src/main/java/com/dynasty/network/DynastyNetwork.java +2 个消息注册（沿用现有通道）
src/main/resources/assets/dynasty/lang/zh_cn.json     +72 键（方块名 / 界面 / 消息 / 18×标题与描述）→ 693 键
src/main/resources/assets/dynasty/lang/en_us.json     +72 键（同上）→ 693 键
```

**没有改动**：FTB 主线任务与奖励、Boss 战斗、永久饰品槽、毕业装备、建筑生成、世界生成；
未新增依赖、未动 `modpack/mods` 里的发布 jar、未生成任何图片。

### 临时贴图

告示板方块临时复用原版贴图 `minecraft:block/bookshelf`（`models/block/bounty_board.json` 的 `all`），
**没有复制或修改原版贴图文件，也没有生成新美术**；界面用代码绘制矩形与文字，不需要背景图。


## 8. 构建与测试结果（实际执行）

```bash
$ ./gradlew compileJava --offline            # 新增类与注册全部编译
BUILD SUCCESSFUL      （日志里 error/失败 计数 0；build/classes/com/dynasty/bounty/*.class 全部生成）

$ javac -cp build/classes/java/main -d /tmp/bounty_test tools/bounty/BountyRulesTest.java
$ java  -cp build/classes/java/main:/tmp/bounty_test BountyRulesTest
通过 36 项，失败 0 项
✅ 悬赏委托核心逻辑测试全部通过        （退出码 0）

$ python3 tools/bounty/verify_offers.py
委托定义 18 条：收购 10 / 讨伐 4 / 考察 4
数据包自检：通过 ✅                     （退出码 0）

$ python3 tools/maintenance/check_all.py     # 上一批的资源/词条/配方自检
检查文件 938 个 · 确认错误 0 · 警告 0 · 跳过 0

$ python3 tools/art/verify_ftbquests.py      # 任务书未被影响
任务书自检：通过 ✅
```

覆盖的约束（`tools/bounty/BountyRulesTest.java`，均为实际断言）：
接取满额 · 接取前击杀不计数 · 目标不符不计数 · 放弃后重新接取（进度清零、不发奖励） ·
跨日保留（快照与进度） · 时间倒退（水位不降、不重发、不能重复领） · 重复领奖被拒 ·
重复提交被拒且不再消耗 · 材料不足零消耗 · 奖励空间不足（保留可领状态） · 两名玩家隔离 ·
存档往返（水位/发布/进度/已领/快照） · 数据包重载后快照不变 · 考察目标维度判定 ·
每日发布决定论（同天一致、异天变化） · 定义校验（合法通过、数量/权重非法拒绝、禁用奖励拒绝）。

## 9. 已知限制与未实测项

**未实测（编译与纯逻辑测试不能代替）**

* **界面交互没有实际打开过**：布局、按钮可用态、长文本折行、GUI 缩放（小窗口 / 大 GUI Scale）都只是代码层保证。
* **多人真机行为未测**：两名玩家同时开板、同时提交、同时领奖的时序（逻辑上服务端串行处理，但没有联机验证）。
* **击杀归属只做了代码级覆盖**：宠物击杀、TNT / 岩浆等间接伤害、命令杀怪等边界没有实机跑过。
* **`/reload` 实机重载**、**睡觉跨日**、**服务器重启后继续领奖**、**死亡重生后保留**目前只有代码/单元级证据。
* **没有使用独立测试存档跑服务器**：本轮只做离线编译与纯逻辑测试，没有启动服务器或客户端。

**实现边界（有意限定）**

* 讨伐只用**普通原版敌对生物**（僵尸 / 骷髅 / 蜘蛛 / 苦力怕），不含 Boss，也不含本模组的精英怪。
* 考察只覆盖项目**已有的 4 个维度**，前置用已核实的 `dynasty:entered_*` 成就，不猜 ID。
* 收购只支持**物品或物品标签**，不支持 NBT 过滤（`target` 写 `#tag` 时按物品标签匹配）。
* 每日固定 6 条且**全服一致**（同一世界同一天所有玩家一样），没有「按玩家进度换池」的机制。
* 已领记录只保留最近 16 天；日水位保证旧日期不会重发，清理不会重新打开领奖机会，
  但**超过 16 天的历史领奖明细不再保留**（只影响审计，不影响判定）。
* 界面没有分页 / 搜索：一次只显示当天 6 条；若把发布条数调大，列表会变长且不滚动。
* 没有把委托接进 FTB 任务书或图鉴（需求要求不动主线），也没有加音效。

**与既有系统的关系**：本系统完全独立，不改主线任务、Boss、饰品槽、毕业装备与建筑生成，
也不构成任何现有内容的新门槛（不做委托照样能推进主线）。
