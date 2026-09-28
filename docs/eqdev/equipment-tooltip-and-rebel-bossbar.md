# 装备悬停说明重构 + 叛将血条/生成修复（本轮交付）

范围：只动「装备说明展示的客户端类」与「RebelGeneral 的血条 + 必要的局部生成修复」，
外加独立新增的辅助类、测试与本文档。武器渲染、流派成长、任务与引导书、贴图/模型、
装备数值与饰品效果、结构生成器都**没有**改动。最终集成时已把共享语言键合并，
并修正持续追踪但暂时不可见的玩家不应被遗忘的问题。

## 1. 实际改动文件清单

**修改（4）**

| 文件 | 改动 |
| --- | --- |
| `src/main/java/com/dynasty/client/DynastyTooltips.java` | 重写展示流程：默认最多 3 行自定义说明、Shift 展开详情；删掉重复的攻击力/护甲/韧性/耐久行与内部实现说明；只追加不清空；套装只留「套装详情见图鉴」 |
| `src/main/java/com/dynasty/client/DynastyItemInfo.java` | 新增 `lines(stack, includeGeneric)` 重载：盔甲不再取「通用护甲说明」（与套装行重复），真实的用法/图鉴文案保留 |
| `src/main/java/com/dynasty/DynastyTrinketTips.java` | 饰品 `Charm.appendHoverText`：默认前 3 行（属性），效果与命中触发改到 Shift 后；Shift 判定用 `DistExecutor` 包住，服务器不会加载客户端类 |
| `src/main/java/com/dynasty/entity/DynastyBosses.java` | **只改 RebelGeneral 那一段**：血条改成按玩家订阅；`customServerAiStep` 里接订阅管理器；新增 `die()` 摘条；新增 `checkSpawnRules` 自然生成落点校验 |

**新增**

| 文件 | 作用 |
| --- | --- |
| `src/main/java/com/dynasty/DynastyTooltipBudget.java` | 共享的「默认几行」预算（服务器安全，不含客户端引用） |
| `src/main/java/com/dynasty/client/DynastyTooltipText.java` | 悬停文案 + 纯算术：翻译键优先（缺键回退内置中英）、按运算类型折叠属性修饰符、套装减伤按真实 90% 上限 |
| `src/main/java/com/dynasty/client/DynastyTooltipGate.java` | 唯一触碰 GLFW 的 Shift 状态（客户端专用） |
| `src/main/java/com/dynasty/entity/BossBarVisibility.java` | 血条可见性的**纯判定**（无 MC 引用，可单测） |
| `src/main/java/com/dynasty/entity/DynastyBossBarSubscriptions.java` | 按玩家逐个订阅血条的 MC 胶水：登记候选、错峰判定、跨维度/退出/死亡清理 |
| `src/main/java/com/dynasty/entity/DynastySpawnPlacement.java` | 生成落点校验：自然生成严格（可站立面 + 身体无碰撞），其它入口放行 |
| `src/main/java/com/dynasty/entity/RebelGeneralBossBarGameTests.java` | GameTest：跟踪范围≠可见、退订/清空安全、自然生成拒绝「埋进方块/贴天花板」 |
| `tools/eqdev/EqDevLogicTest.java` | 生产类直调的逻辑测试（血条判定 / 生成分档 / 数值折叠） |
| `tools/eqdev/test_source_contracts.py` | 结构性契约（血条按玩家订阅、无全局开关、只追加不清空、客户端类不进服务器、文案键齐全） |
| `tools/eqdev/run_eqdev_tests.sh` | 一条命令跑上面两项 |
| `docs/eqdev/tooltip-lang-additions.json` | 已合并的新语言键片段（7 键 × 中英） |
| `docs/eqdev/equipment-tooltip-and-rebel-bossbar.md` | 本文档 |

## 2. 新旧行为差异

### 2.1 悬停说明

| 场景 | 旧行为 | 新行为 |
| --- | --- | --- |
| 默认（不按 Shift） | 名字下插一行简介；非装备只显示「按住 Shift」；**盔甲无论按不按 Shift 都全量展开** | 追加**最多 3 行**自定义说明；有更多内容时才补「按住 Shift 查看详情」 |
| 按住 Shift | 追加攻击力 / 护甲 / 韧性 / 耐久 / 套装加成 —— 与原版属性块**重复** | 展开触发条件与准确数值，且**不重复**默认行，也不重复原版属性 |
| 盔甲默认块 | 「套装名 · 部位」+「特殊效果：护甲/韧性/抗击退」+「套装效果：四件总减伤/总生命」+「当前已穿 X/4（**每秒自动刷新，换装 / 过维度都不会丢**）」+ 耐久 | 「§6将军铠 §7套装 · 每件减伤 §6+16% §7· 生命上限 §6+150」+「§8套装详情见图鉴」（套装不再长篇展开，套装逻辑未动） |
| 盔甲 Shift 详情 | 无（默认已经全给了） | 「穿满四件：总减伤 +64%（上限 90%）· 总生命 +600」+「当前已穿 2/4：实际减伤 +32% · 生命 +300」+「四件合计：护甲 +N · 韧性 +N」 |
| 兵器 | 简介行写「兵器 · 攻击力 26（Shift 看机制）」，Shift 再重复攻击力 | 只保留真实的「特攻 +N」（若有），攻击力/耐久交给原版显示 |
| 饰品 | 属性 / 效果 / 命中触发**全部常显** | 默认前 3 行（属性），效果与命中触发在 Shift 后 |
| tooltip 结构 | 往索引 1 插行（会打乱原版与其它模组的顺序） | 只在末尾**追加**，从不清空整份列表；附魔、耐久、其它模组的提示都不受影响 |

顺带修正一处**显示与结算不一致**：旧代码把四件套总减伤上限写成 `0.92`，而玩法结算
`DynastyBalance.setDamageReduction` 用的是 `0.90`；现在悬停按真实的 0.90 显示（只改显示，未改数值）。

### 2.2 叛将血条

| 场景 | 旧行为 | 新行为 |
| --- | --- | --- |
| 玩家进入实体跟踪范围 | `startSeenByPlayer` 直接 `bossEvent.addPlayer` → 14 区块（≈224 格）内**立刻**给血条 | 只登记候选，**不给条**；等可见性判定 |
| 隔着山体 / 在地下 / 刚进维度 | 照样弹血条 | 从没见过又没交战 → **不显示** |
| 同维度、视线通畅、≤40 格 | 显示 | 显示 |
| 交战中（Boss 锁定该玩家 / 双方刚互相攻击过） | 显示 | ≤48 格内保持显示 |
| 战斗中短暂被遮挡 | 一直显示 | 曾见过 + 100 tick 宽限内保持，过后且没交战才收起（不闪烁） |
| 走远 / 跨维度 / 死亡 / 实体移除 / 玩家退出 | 主要靠原版兜底 | 全部显式清理：跨维度立刻收起、死亡与移除 `clear()`、退出走 `stopSeenByPlayer`；记录 600 tick 无交互过期 |
| 多个叛将 | 每只都在 224 格内塞一根条 → 屏幕堆叠 | 只有「看得见或真在打」的玩家才会看到 |
| 全局开关 | —— | **不使用** `ServerBossEvent#setVisible`，每个玩家独立订阅 |
| 性能 | —— | 每 10 tick 一次、按实体 id 错峰、只遍历**跟踪自己的玩家**（不扫世界、不扫生物） |

### 2.3 叛将生成落点

| 场景 | 旧行为 | 新行为 |
| --- | --- | --- |
| 自然生成 / 区块生成 | 没有落点校验，可能生成在实心方块里、贴天花板卡住 | 校验「脚下有可站立面」+「2.2 格身体碰撞箱无碰撞」，不合格直接拒绝 |
| 刷怪蛋 / 命令 / 召唤 / 刷怪笼 / 结构守卫 | 照常 | **照常放行**（不因为坏生成把入口全砍掉）；未改动任何 biome modifier 或结构生成器 |
| 存档里已有的叛将 | —— | 不删除、不传送、不改位置（只影响新的生成判定） |

## 3. 已执行的测试与真实结果

```bash
# 1) 编译
./gradlew --offline compileJava
  → BUILD SUCCESSFUL（只剩项目里既有的 ResourceLocation(String,String) 过期告警）

# 2) 本轮测试：Python 契约 + Java 逻辑，一条命令
bash tools/eqdev/run_eqdev_tests.sh
  == 1/2 Python 结构性契约 ==
  通过 26 项，失败 0 项
  ✅ 结构性契约（血条订阅 / 悬停展示 / 文案键）全部符合本轮约定
  == 2/2 Java 逻辑测试（生产类直调） ==
  通过 27 项，失败 0 项
  ✅ 叛将血条判定 / 生成落点 / 悬停数值折叠 逻辑测试全部通过
```

**Java 逻辑测试的实际断言（摘要）**

* 血条：初次隔山体/地下 → 不显示；同维度视线通畅 ≤40 格 → 显示；看得见但 >40 格 → 不显示；
  交战 45 格 → 显示、49 格 → 不显示；曾见过 + 宽限内（99 tick）被遮挡 → 保持显示、宽限刚过（101 tick）→ 收起；
  交战中长时间遮挡 → 仍保持；未交战走远 → 收起；
  **两位玩家同距离时按「是否可见 / 是否交战」分别判定**（看得见的给条、隔墙的不给）。
* 生成：`NATURAL / CHUNK_GENERATION` 走严格校验；`SPAWN_EGG / COMMAND / MOB_SUMMONED / STRUCTURE / SPAWNER / DISPENSER` 放行；空输入安全返回 false。
* 数值折叠：加法 4+6=10；`(0+5)×1.2×1.5=9`（并断言 ≠ 朴素相加 5.7）；两个总乘连乘 =2.25；两个基础乘先相加再乘 =13；
  未知运算类型按加法处理不丢数值；套装减伤 16%×4=64%、28%×4→90%（真实上限）；
  实穿件数 2×25%=50%、4×33%→90%、件数夹在 0..4；百分比/数字格式（16% / 5.5% / 90% / 16 / 16.5）。

**Python 契约检查钉住的真实结构性事实（摘要）**

* `RebelGeneral.startSeenByPlayer` 只登记候选、**不再**出现 `bossEvent.addPlayer`；`stopSeenByPlayer` 会退订；
  `die()` 与 `remove()` 都 `clear()`；整个 `DynastyBosses.java` 里**没有** `setVisible(`；
  订阅管理器里有节流（`if (--this.cooldown > 0)`）、跨维度收起、过期清理，且不含 `getEntitiesOfClass` / 世界遍历。
* `DynastyTooltips` 只追加（`tip.addAll`），**没有** `.clear()`；不再出现「攻击力：/ 护甲：/ 韧性：/ 耐久：」与 `appendStats` / `appendArmorStats`；
  不再出现「每秒自动刷新 / 换维度不会丢 / refreshed every second」与「套装效果：」长篇；默认与 Shift 两个视图分开；事件类带 `value = Dist.CLIENT`。
* `DynastyTrinketTips` 用 `DistExecutor.unsafeCallWhenOn(Dist.CLIENT, ...)` 取 Shift 与提示；GLFW 只出现在客户端类里。
* 文案：`DynastyTooltipText` 里用到的 7 个键与 `docs/eqdev/tooltip-lang-additions.json` 完全一致；
  `zh_cn.json` / `en_us.json` **未被提前写入**这些键。

## 4. 未完成 / 待合并事项

1. **语言键已合并**：`docs/eqdev/tooltip-lang-additions.json` 的 7 个键已并进
   `src/main/resources/assets/dynasty/lang/{zh_cn,en_us}.json`，并修正英文“减伤”的译文。
2. **GameTest 已执行**：`./gradlew --offline runGameTestServer jar` 通过，52 项必需测试全部通过；
   `RebelGeneralBossBarGameTests` 的 2 项包含在内。新 JAR 已同步到 `modpack/mods/dynasty-1.4.0.jar`。
3. **没有实机验收**：
   * 悬停的实际排版、长句折行、Shift 展开手感没在客户端里看过（只断言了两个视图的内容差异）；
   * 血条的「两位玩家不同距离 / 隔墙 / 交战 / 离开范围 / 跨维度 / 死亡」只覆盖**判定逻辑**与**结构性契约**，
     没有在真实双人服务器里跑过；
   * 生成落点只覆盖纯逻辑分档 + GameTest 代码（未执行），没有统计真实世界的生成位置。
4. **另外 4 个 Boss 仍是旧逻辑**（龙帝 / 宦官首脑 / 九天将军 / 龙王）：本轮按要求只改叛将，
   它们依旧「进跟踪范围就显示血条」。接入方式见 §5（每个约 5 行改动）。
5. **刷怪频率与生物群系不在本轮范围**：`data/dynasty/forge/biome_modifier/spawn_*.json`
   （主世界权重 1、冥界权重 3、龙宫权重 2）没有改动。若实测觉得刷得太勤或仍出现在洞穴深处，
   那属于刷怪表调参，需要主代理决策，我没有擅自改数据。

## 5. 给另一位开发者的接手说明

* **别改这两个类的语义**：`client/DynastyTooltips`（默认 ≤3 行 + Shift 展开、只追加）与
  `client/DynastyTooltipText`（翻译键优先、缺键回退）。要加新装备说明，请加一个 `DynastyTooltipText.Text`
  常量，并把键补进 `docs/eqdev/tooltip-lang-additions.json`。
* **默认行数**：`DynastyTooltipBudget.BRIEF_LIMIT`（当前 3）是装备与饰品共用的预算，改一处两边同时生效。
* **`DynastySchoolWeapons.appendHoverText` 我没有动**（属你的范围）。它现在仍是无条件追加；
  建议同样按「默认 ≤3 行 + Shift 详情」展示，避免与套装行、属性行重复 —— Shift 判定可直接复用
  `client/DynastyTooltipGate`（记得用 `DistExecutor` 包一层，保证专用服务器不加载客户端类）。
* **给其它 Boss 做逐玩家血条**（每个 Boss 约 5 行）：
  1. 字段 + 构造：`private final DynastyBossBarSubscriptions barSubscriptions;` 并在构造函数里
     `new DynastyBossBarSubscriptions(this, this.bossEvent)`；
  2. `startSeenByPlayer` → `barSubscriptions.startSeenByPlayer(player)`；
  3. `stopSeenByPlayer` → `barSubscriptions.stopSeenByPlayer(player)`；
  4. `remove(...)` 与 `die(...)` → `barSubscriptions.clear()`；
  5. `customServerAiStep()` 开头加 `barSubscriptions.tick();`。
  阈值（显示 40 格 / 保持 48 格 / 宽限 100 tick / 每 10 tick 判定）都在 `BossBarVisibility` 里。
* **结构守卫**：本轮没有改 `structure/`。以后若在建筑里生成叛将并希望校验落点，直接调用
  `DynastySpawnPlacement.hasStandingSpace(level, pos, box)` 自己判；不要改成 `NATURAL` 去借用严格校验。
* **共享文件**：`assets/**/lang/`、任务书 SNBT 与生成器、配方、模型/贴图、`DynastyBalance`、
  `DynastyArmorMaterials`、`DynastyTrinkets`、`DynastySchool*` 都没有被我改动；
  `DynastyBosses.java` 的改动集中在 RebelGeneral 那一段（可用 `git diff` 复核）。
