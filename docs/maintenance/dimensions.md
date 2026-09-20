# 维度与传送门清单（dimensions）

> 只写**代码/配置能验证的事实**；玩家该带什么、该做什么，另用「建议」段单独列出（来自本项目的任务书文案
> `tools/art/quest_story.py` 的 HINTS 与 Boss 攻略页），**不把建议混进机制说明**。
> 来源：`data/dynasty/dimension/*`、`data/dynasty/dimension_type/*`、`data/dynasty/recipes/*`、
> `block/DynastyPortalBlock.java`、`DynastyBlocks.java`、`DynastyNetherLock.java`、`TalismanCharmItem.java`。

## 1. 总表

| 维度 | 维度 ID | 维度类型文件 | 传送门方块 | 进入方式 | 回程方式 |
| --- | --- | --- | --- | --- | --- |
| 天朝·龙庭 | `dynasty:celestial_dynasty` | `dimension_type/celestial_dynasty.json`（有天光、固定时间 6000、环境光 0.55、384 高） | **天朝传送门** `dynasty:jade_portal`（`DynastyBlocks.java:92-94` → `CELESTIAL_DYNASTY`） | 放下方块 → 右键 | ① 在对面再放一座门右键回来；② 用**归乡符** `dynasty:return_talisman` |
| 地府 | `dynasty:underworld` | `dimension_type/underworld.json`（无天光、环境光 0.08、384 高） | **地府传送门** `dynasty:underworld_portal`（`DynastyBlocks.java:116-120` → `UNDERWORLD`） | 放下方块 → 右键 | 同上；另：**原版地狱门被禁用**（见 §3） |
| 九霄天界 | `dynasty:jiuxiao` | `dimension_type/jiuxiao.json`（有天光、固定时间 6000、环境光 0.35） | **九霄传送门** `dynasty:cloud_portal`（`DynastyBlocks.java:100-104` → `JIUXIAO`） | 放下方块 → 右键 | 同上 |
| 东海龙宫 | `dynasty:dragon_palace` | `dimension_type/dragon_palace.json`（无天光、固定夜晚 18000、环境光 0.18） | **龙宫传送门** `dynasty:dragon_gate`（`DynastyBlocks.java:106-110` → `DRAGON_PALACE`） | 放下方块 → 右键 | 同上（注意水下呼吸，见 §4） |

* 四个维度的 `coordinate_scale` 都是 **1.0**、`min_y = -64`、`height = 384`（`dimension_type/*.json`）。
* 每个维度用的生物群系见 `docs/maintenance/bosses.md` §2（那里有 `dimension/*.json` 的 `biome_source` 列表）。

## 2. 门怎么用（代码保证的机制）

* **门是方块物品**，放下后右键触发传送（`DynastyPortalBlock.use()`，`:49-64`）：
  如果当前维度**就是**该门的目标维度 → 传送回**主世界**；否则传送到目标维度。
  所以「一座门 = 双向开关」。
* **落点安全**：`findArrival()`（`:76-85`）从 `maxBuildHeight-3` 向下扫「脚下实心、身体两格空、不在液体里」的位置；
  找不到就在最高处铺一层 3×3 圆石平台（`:117-128`）。这是为了防止「出生在基岩层/岩浆里」的旧问题。
* **门方块本身不可破坏**：`portalProps()` = `strength(-1.0F, 3600000.0F).noCollission().lightLevel(15)`
  （`DynastyBlocks.java:86-90`），即基岩级硬度 + 发光 15。**放下去就拿不回来了**（要再放门得再合成）。
* **配方各给 2 座**（下表），这是「一座留家里、一座带过去」玩法的前提。

| 传送门 | 配方（`data/dynasty/recipes/*`） | 产出 |
| --- | --- | --- |
| 天朝传送门 `jade_portal` | 3×3：玉石块×8 + 中间龙晶×1（shaped，键 J=jade_block、C=dragon_crystal） | ×2 |
| 地府传送门 `underworld_portal` | 同上摆法，中间换成**朱砂** | ×2 |
| 九霄传送门 `cloud_portal` | 玉石块×4 + 龙晶×1 + 凤凰羽×1（shapeless） | ×2 |
| 龙宫传送门 `dragon_gate` | 玉石块×4 + 龙晶×1 + 龙鳞×2（shapeless） | ×2 |

## 3. 另外三条「代码保证」的相关机制

1. **原版地狱门被关掉**（`DynastyNetherLock.java`）：点火生成门被取消（`:34-42`，`BlockEvent.PortalSpawnEvent`），
   任何「前往原版地狱」的维度旅行也会被拦下并提示改用**地府传送门**（`:45+`，`EntityTravelToDimensionEvent`）。
   代码注释说明地狱材料改在地府维度获取。
2. **进入维度会发成就**：`DynastyWorldEvents.java:54-65` 按维度路径发 `entered_celestial` /
   `entered_underworld` / `entered_jiuxiao` / `entered_dragon_palace`（任务书据此自动判定，见主线第 4~7 章）。
3. **归乡符**（`charm("return_talisman")`，`TalismanCharmItem.java:191-205`）：
   右键消耗 1 张（创造模式不消耗，`:76-78`）→ 传送到**主世界出生点**附近的安全落点（复用同一个 `findArrival`），
   重置坠落距离，并**移除所有负面效果**。它不是回「床」。
   配方：符纸 + 末影珍珠（`recipes/return_talisman.json`；文案见 `quest_story.py` HINTS）。

## 4. 建议玩家做的准备（来自项目自己的文案，**不是机制**）

* 天朝：`quest_story.py` HINTS → 「合成一次得到两座门。放下第一座并右键前往天朝；把第二座带过去，
  在安全位置放下作为回程门。**对面不会自动生成门**。」
* 地府：HINTS → 「一次合成两座，右键方块往返地府。带第二座门、归乡符、照明和搭路方块，先建立安全据点再探索。」
* 九霄：HINTS → 「凤凰羽来自凤凰的掉落。一次得到两座门，带好回程物品与缓降手段，九霄的高差比地面更危险。」
* 龙宫：HINTS → 「进入龙宫前先准备水下呼吸药水或已获得的水下饰品；不要入水后才找材料。」
  （维度类型是「无天光 + 固定夜晚」，`ambient_light: 0.18`。）
* Boss 攻略页（`dynasty_boss_guides.snbt`）同样按维度给了准备清单；这些是**建议**，代码不会强制。

## 5. 相关配置位置（要改东西时看这些）

| 内容 | 位置 |
| --- | --- |
| 维度定义 | `src/main/resources/data/dynasty/dimension/{celestial_dynasty,underworld,jiuxiao,dragon_palace}.json` |
| 维度类型（天光/时间/高度） | `src/main/resources/data/dynasty/dimension_type/*.json` |
| 地形（噪声设置、地表规则） | `src/main/resources/data/dynasty/worldgen/noise_settings/*.json` |
| 群系 | `src/main/resources/data/dynasty/worldgen/biome/*.json` |
| 门方块与传送逻辑 | `DynastyBlocks.java`（注册）、`block/DynastyPortalBlock.java`（行为） |
| 门配方 | `src/main/resources/data/dynasty/recipes/{jade_portal,underworld_portal,cloud_portal,dragon_gate}.json` |
| 维度进入成就 | `DynastyWorldEvents.java:54-65`、`data/dynasty/advancements/entered_*.json` |
| 关掉原版地狱门 | `DynastyNetherLock.java` |

## 6. 待确认

1. **其他模组的传送方式**（跨维度指令、其他模组的门）是否能进入这四个维度：代码里没有拦截，
   但**没有实测**；`DynastyNetherLock` 只拦「去原版地狱」。
2. **落点平台是否会在水下维度造出奇怪结构**：`buildLanding()` 在找不到可站立点时铺圆石，
   龙宫（水下）情况下的实际观感**未实测**。
3. **门不可破坏是否符合预期**（`strength(-1)`）：这意味着玩家无法回收已放置的门。
   如果作者本意是「可回收」，那需要改方块属性——本批次只记录事实，未改动。
4. 九霄 / 龙宫的进入是否还需要别的准备（如缓降、防水），属**玩法建议**，不在机制事实内。
