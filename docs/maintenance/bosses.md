# 六位 Boss 对照表（bosses）

> 只列**可验证事实**：实体 ID、生成配置、召唤信物、掉落表、任务书里的攻略页 ID 与主线讨伐任务 ID。
> **不重写攻略正文、不推测刷新坐标**（生成是生物群系随机刷新，代码与配置里都没有固定坐标）。
> 数据来源：`data/dynasty/forge/biome_modifier/*`、`data/dynasty/worldgen/biome/*.json` 的 `spawners`、
> `data/dynasty/dimension/*.json`、`entity/DynastyEntities.java`、`block/RitualAltarBlock.java`、
> `DynastyBossDrops.java`、`data/dynasty/loot_tables/entities/*`、`tools/art/boss_quest_guides.py`、
> `modpack/config/ftbquests/quests/chapters/*.snbt`。

## 1. 总表

| Boss | 实体 ID | 生成维度（依据） | 召唤信物 | 掉落表位置 | 攻略页 ID | 主线讨伐任务 ID |
| --- | --- | --- | --- | --- | --- | --- |
| 龙帝 | `dynasty:dragon_emperor` | **天朝·龙庭**（`spawn_boss_celestial.json` → `#dynasty:celestial`，权重 1） | `dynasty:dragon_emperor_seal` 龙帝玉玺 | JSON：`loot_tables/entities/dragon_emperor.json`；另见代码 `DynastyBossDrops.java:37-41` | `1000000000020000` | `1000000000000191`（`dynasty_story_08`） |
| 叛将 | `dynasty:rebel_general` | **主世界**（`spawn_overworld_boss.json` → `#minecraft:is_overworld`，权重 1）+ **地府**（`spawn_boss_underworld.json`，权重 3）+ **东海龙宫**（`spawn_elite_palace.json`，权重 2） | `dynasty:rebel_head` 叛将首级 | JSON：`loot_tables/entities/rebel_general.json`；代码：`DynastyBossDrops.java:47-51` | `1000000000020001` | `100000000000014b`（`dynasty_story_03`） |
| 宦官首脑 | `dynasty:eunuch_mastermind` | **天朝·龙庭**（`spawn_elite_celestial.json` → `#dynasty:celestial`，权重 2） | `dynasty:eunuch_token` 内廷令牌 | JSON：`loot_tables/entities/eunuch_mastermind.json`；代码：`DynastyBossDrops.java:52-56` | `1000000000020002` | `100000000000014f`（`dynasty_story_04`） |
| 不死始皇 | `dynasty:undead_first_emperor` | **地府**（`spawn_boss_underworld.json` → `#dynasty:underworld`，权重 1） | `dynasty:emperor_bone` 帝骸骨 | JSON：`loot_tables/entities/undead_first_emperor.json`；代码：`DynastyBossDrops.java:42-46` | `1000000000020003` | `1000000000000152`（`dynasty_story_05`） |
| 九霄天将 | `dynasty:nine_heaven_general` | **九霄天界**（`spawn_boss_jiuxiao.json` → `#dynasty:jiuxiao`，权重 1） | `dynasty:sky_token` 天将令 | **无 JSON 实体掉落表**（`loot_tables/entities/` 下没有该文件）；掉落写在 `DynastyBossDrops.java:62-66` | `1000000000020004` | `10000000000001c5`（`dynasty_story_06`） |
| 东海龙王 | `dynasty:dragon_king` | **东海龙宫**（`spawn_boss_dragon_palace.json` → `#dynasty:dragon_palace`，权重 1） | `dynasty:sea_token` 龙宫玉印 | **无 JSON 实体掉落表**；掉落写在 `DynastyBossDrops.java:67-72` | `1000000000020005` | `10000000000001d9`（`dynasty_story_07`） |

## 2. 维度 ↔ 生物群系 ↔ 生成配置（可核对链条）

| 维度 | 维度 ID | 包含生物群系（`dimension/*.json` 的 `biome_source`） | 该维度里配了哪些 Boss |
| --- | --- | --- | --- |
| 天朝·龙庭 | `dynasty:celestial_dynasty` | `celestial_sea` / `celestial_plains` / `jade_forest` / `dragon_ridge` | 龙帝（权重 1）、宦官首脑（权重 2） |
| 地府 | `dynasty:underworld` | `underworld_wastes` / `soul_river` | 不死始皇（权重 1）、叛将（权重 3） |
| 九霄天界 | `dynasty:jiuxiao` | `jiuxiao_cloud_sea` / `jiuxiao_skyland` | 九霄天将（权重 1） |
| 东海龙宫 | `dynasty:dragon_palace` | `dragon_palace_deep` / `dragon_palace_hall` | 东海龙王（权重 1）、叛将（权重 2） |

* 另有 `data/dynasty/worldgen/biome/*.json` 里各群系自带的 `spawners` 列表（例如 `celestial_sea` 的 monster 列表里有
  `dynasty:phoenix`、`dragon_palace_hall` 的 monster 列表里有 `dynasty:merfolk`），这些是**群系原生刷新**，
  与 `forge/biome_modifier` 的追加刷新是两条并行的配置来源。
* 本模组**没有注册 `SpawnPlacements`**（全库 grep 为 0）。Forge 对未注册类型返回 `NO_RESTRICTIONS` +
  `checkSpawnRules = true`（patch 后源码 `SpawnPlacements.java:53-56`、`:63-67`），所以这些 Boss 能自然刷新；
  副作用（和平难度是否仍刷新）见「待确认」。

## 3. 召唤（复战）机制：代码事实与影响范围

* **信物 → Boss 映射**（`block/RitualAltarBlock.java:43-57`）：
  `dragon_emperor_seal→龙帝`、`rebel_head→叛将`、`eunuch_token→宦官首脑`、`emperor_bone→不死始皇`、
  `sky_token→九霄天将`、`sea_token→东海龙王`。表里 6 行与之一一对应。
* **成型条件**：祭坛同高度周围 3×3 环（8 格）里 ≥4 块玉石块（`countJade()`，`:59-72`，`REQUIRED_JADE = 4`，`dy=0`）。
* **消耗**：召唤成功消耗 1 个信物；创造模式（`instabuild`）不消耗（`:104-106`）。
* **唯一性限制**：以玩家为中心 80 格内已有**同种存活** Boss 时拒绝召唤，且不消耗信物（`:93-99`）。
* **召唤后**：Boss 获得 200 tick（10 秒）抗性提升 II（`:109-110`）。
* **首杀保证信物**：除掉落表外，`DynastyBossCombat.FIRST_KILL`（`:91-102`）在**玩家击杀**时再补发 1 个信物
  （每人每种一次），所以「打不到信物」不会卡死复战。
* 祭坛本体配方：`data/dynasty/recipes/ritual_altar.json`（玉石块×4 + 龙晶×1，无序）。

## 4. 任务书链接（攻略 ↔ 主线）

* 攻略页由 `tools/art/boss_quest_guides.py` 生成到 `dynasty_boss_guides.snbt`：6 个 Boss 页 + 1 个「法阵·祭坛」教学页
  （页 ID `1000000000020000`…`1000000000020005`，教学页 `1000000000020006`）。
* 双向链接（生成器 `add_guides()` 写入，自检 `validate_links()` 断言目标存在）：
  攻略页首行「← 返回主线讨伐 · X」指向主线击杀任务；主线击杀 / 击杀成就 / 信物任务首行「点击查看 · X 攻略」指回攻略页。
  抽查：`dynasty_story_08.snbt:34/48/62` → `1000000000020000`（龙帝）；`dynasty_boss_guides.snbt:12` 页首行 → `1000000000000191`。
* 攻略页 `rewards: []`、无前置，**不阻塞主线**（`boss_quest_guides.py:108-111` 有断言）。

## 5. 待确认

1. **刷新坐标一律不提供**：生成方式是生物群系随机刷新（`forge:add_spawns` + 群系 `spawners`），
   配置里没有坐标或结构绑定；本表不推测「哪个建筑必刷」。
2. **和平难度是否仍会刷出这些 Boss 待实测**：因为模组没有 `SpawnPlacements` 注册，
   `Monster.checkMonsterSpawnRules` 里的「`PEACEFUL` 不刷新」判定对它们不生效（Forge 补丁行为）。
   和平难度下玩家受伤判定另有限制，但**是否仍会生成**需要实机确认。
3. **九霄天将 / 东海龙王没有 JSON 实体掉落表**：掉落完全由 `DynastyBossDrops` 的代码分支给出；
   如果后续有人用数据包方式改掉落，这两只会不受影响（记录为事实，不代表有问题）。
4. Boss 血量 / 护甲 / 阶段数值不在本表：阶段阈值与破盾次数见 `entity/DynastyBossMechanicDriver.java:74-138`，
   攻略页里的数字与之一致（已核对），但本表不复述。
