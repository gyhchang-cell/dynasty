# Dynasty 内容审计报告（只读审计 · 2026-09-20）

> 审计对象：`/Users/a15356015027/Desktop/dynasty` 的**当前工作区状态**（含未提交改动）。
> 本报告只做记录与建议：**未改动任何 Java / 贴图 / 模型 / 配方 / 任务配置 / 构建脚本 / jar**，
> 未删除文件、未安装依赖、未操作存档、未提交或推送。唯一新增文件是本报告。
> 未运行任何会生成/覆盖项目文件的脚本；分析用的临时脚本写在 `/tmp`，只读项目文件。

## 0. 方法与证据基线

* 读了 `docs/开发约定.md`（含 **2026-09-20 生效的「任务大重制 v2」** 规范）；项目内**没有** AGENTS.md / CLAUDE.md / .clinerules。
* 交叉核对的实际数据源：`data/dynasty/recipes`（414 条）、`loot_tables/{blocks,chests,entities}`、
  `forge/biome_modifier/*`、`worldgen/biome/*.json` 的 `spawners`、`worldgen/placed_feature/*`、
  `advancements/*`、`tags/{items,blocks}`、`modpack/config/ftbquests/quests/chapters/*.snbt`（7041 行）、
  `docs/quests-remaster/book.json`、以及 Java 的 `DynastyBossDrops` / `DynastyBossCombat` / `DynastyWeaponGifts` /
  `block/RitualAltarBlock` / `entity/DynastyBoss*` / `entity/DynastyEntities` / `client/DynastyBlockInfo` 等。
* 原版行为基线：用本地 ForgeGradle 缓存里的 **1.20.1 patch 后源码**
  （`~/.gradle/caches/forge_gradle/.../forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar`）核对
  `NaturalSpawner` / `SpawnPlacements` / `PotionItem` / `MipmapGenerator`，不靠记忆。
* 全量可达性检查：把「配方 + 宝箱/实体掉落表 + Boss 掉落 switch + 任务奖励 + 成就 + 代码授予」当来源，
  从野生来源做传递闭包，对 460 个物品模型逐个判定是否可达；同时做配方环检测。
* **并行开发提示（仅记录，未覆盖）**：工作区存在大量未跟踪/未提交文件（任务重制 v2、`tools/art/quest_story.py`、
  `tools/art/boss_quest_guides.py`、`gen_tab_icon.py`、`verify_tab.py` 等），`docs/开发约定.md` 的 v2 规范
  日期就是审计当天，说明有另一个会话正在维护任务书与 Boss 攻略。本轮我未写入这些文件。
  读取过程中有 3 个文件（`entity/DynastyBossMechanics.java`、`entity/DynastyBossMechanicDriver.java`、
  `tools/art/quest_story.py`）被文件读取器判为「内容已更新」，我改用 shell 复核：mtime 仍是 9-13 / 9-19，
  未见本轮被其它进程改写（记录在此，供后续判断）。

---

## 1. 已确认问题

### 1.1 阻塞主线

**未发现**「主线要求、却只能创造获取」的物品，也**未发现配方循环依赖**。核查方式与证据见 §3.1：
27 个主线目标全部可达；全库 0 条配方环。唯一相近的风险是「一次性授予武器丢失后无补救」，但它只影响
**可选**毕业路线（不在主线里），列在 1.2 第 2 条。

### 1.2 功能错误

**（1）Boss 阶段表里的「破绽倍率」从未生效，终阶段实际仍是 ×2.5**

* 涉及内容：龙帝 / 不死始皇 / 九霄天将 / 东海龙王的**终阶段破防窗口**。
* 玩家影响：表里写着终阶段破绽 ×3.0，玩家实际只拿到 ×2.5（输出窗口偏小，战斗体感比设计更肉）。
* 证据：
  * `src/main/java/com/dynasty/entity/DynastyBossMechanicDriver.java:50-51` —— `Phase` 记录里带 `weakMultiplier`；
    表项 `:75-78`（龙帝 2.5 / 3.0）、`:84-86`（始皇 2.5 / 3.0）、`:93-96`（天将 2.5 / 3.0）、`:102-105`（龙王 2.5 / 3.0）。
  * `:197-206` 的 `enterPhase()` 只把 `shieldTicks / shieldHits / shieldCut` 传给
    `DynastyBossMechanics.shield(...)`（`entity/DynastyBossMechanics.java:88`）——**没有**任何一处读取 `weakMultiplier`。
  * 真正破盾走的是硬编码：`DynastyBossCombat.java:59`
    `DynastyBossMechanics.breakShield(mob, bossBarOf(mob), 140, 2.5D);`（窗口固定 140 tick、倍率固定 2.5）。
* 最小修复建议（二选一，都不需要动画/贴图）：
  * 让 `shield()` 接收 `weakTicks/weakMultiplier` 并写进 `persistentData`，`DynastyBossCombat` 读它；
  * 或先把表里的 `3.0D` 改成 `2.5D` 并在表头注释里写明「破绽倍率当前是全局固定值」，消除「表声明 ≠ 实现」。

**（2）一次性授予的毕业武器丢失后没有任何补救路径（后羿弓 / 朱雀羽扇 会被永久锁死）**

* 涉及内容：射日弓（白天杀凤凰授予）、御赐金锏（官阶 12）、尚方宝剑（官阶 17）、七星宝刀（五种 Boss）。
* 玩家影响：**后羿弓**配方需要 `sunbow`、**朱雀羽扇**配方需要 `supreme_sword`；这两件一旦被丢/烧掉，
  该玩家再也不可能做出对应毕业武器。任务书里确实写了「不要随意丢弃」，但没有找回手段。
* 证据：
  * `DynastyWeaponGifts.java:39-46`（官阶）、`:56-66`（白天凤凰 → sunbow）、`:82-101`（`grant()`：**先置 flag 再发物品**，
    flag=`dynasty_gift_<weapon>` 存 `persistentData`，之后永不再发；背包满时掉落在地上）。
  * `data/dynasty/recipes/houyi_bow.json`（材料含 `dynasty:sunbow`）、`data/dynasty/recipes/zhuque_fan.json`（含 `dynasty:supreme_sword`）；
    这两件武器**没有**任何配方、掉落表或任务奖励来源（任务书里只作为「持有检测」出现，从不作为奖励发放）。
* 最小修复建议：给这四件武器加一条「丢失找回」路径（例如按 flag 缺失才重发、或加一条消耗材料的合成/祭坛找回配方），
  或把 `grant()` 的 flag 写在「物品真正进入背包/掉落物存在」之后并允许重生补发。

### 1.3 文案或显示问题

**（1）龙晶矿的「在哪里 / 用什么镐」说明与数据完全对不上**

* 涉及内容：`client/DynastyBlockInfo.java` 的方块使用说明（玩家按提示查看的那段）。
* 玩家影响：会跑去「天朝·龙庭」找龙晶矿（实际只在**主世界**），并以为必须先做玉镐（实际铁镐即可），
  而主线第 4 章恰恰要求先拿到龙晶才能开门 —— 属于会直接误导主线的文案。
* 证据：
  * 文案：`src/main/java/com/dynasty/client/DynastyBlockInfo.java:44-46`
    `"§d龙晶矿§r：天朝·龙庭地下生成，要用玉镐 / 龙晶镐才挖得动。"`
  * 生成：`data/dynasty/forge/biome_modifier/dragon_crystal_ore.json:3` → `"biomes": "#minecraft:is_overworld"`；
    `data/dynasty/worldgen/placed_feature/dragon_crystal_ore.json:16-19` → Y `-60`…`-5`。
  * 工具：`data/minecraft/tags/blocks/needs_iron_tool.json:4` → `dynasty:dragon_crystal_ore`（**铁**级即可）。
  * 对照：任务书 `tools/art/quest_story.py` 的 HINTS 写的才是对的（「主世界 Y=-60 至 -5 的深层…先用铁镐采集」）。
* 最小修复建议：把该行改成「主世界 Y −60~−5 的深层生成，铁镐即可；天朝龙庭不生成」。

**（2）玉矿的 Y 区间说明与数据不符**

* 证据：文案 `DynastyBlockInfo.java:41-43`「主世界 y≤30 挖到」；数据
  `worldgen/placed_feature/jade_ore.json:16-19` → 梯形分布 Y `-60`…`60`（每区块 6 次）。
* 玩家影响：玩家会以为只有浅层有，实际上深层同样有（主线第 2 章大量需要玉）。
* 最小修复建议：改成「主世界地下各深度（−60~60）都会生成，深板岩层是深层变种」。

**（3）法阵·祭坛的失败提示只列了 4 种信物，漏掉天将令与龙宫玉印**

* 证据：提示串 `block/RitualAltarBlock.java:83-85`
  「…手持 Boss 信物（龙帝玉玺 / 叛将首级 / 内廷令牌 / 帝骸骨）才能唤醒。」
  而真实可用的映射是 6 种：`:48-56`（另含 `sky_token` → 九霄天将、`sea_token` → 东海龙王）。
* 玩家影响：拿着天将令/龙宫玉印的玩家看到这条提示会以为「我这信物不能用」。
* 最小修复建议：补齐 6 种，或提示改成「手持任意 Boss 信物（悬停可看）」不再列举。

**（4）Boss 首杀提示里的物品名与词条不一致（3 处）**

* 证据：
  * `DynastyBossCombat.java:96` "天界令牌到手" → 物品词条是 `item.dynasty.sky_token = 天将令`
    （`lang/zh_cn.json`；任务书章节里也叫「天将令」）。
  * `:98` "龙宫令牌到手" → 物品是 `sea_token = 龙宫玉印`。
  * `:103` `FIRST_KILL.put("phoenix", new FirstKill(120, "dragon_scale", 2, "凤凰羽落：龙鳞系材料"))`
    —— 提示写「凤凰羽落」，实际发的是**龙鳞**（凤凰羽来自实体掉落表 `loot_tables/entities/phoenix.json:9`，
    和首杀奖励是两回事）。
* 玩家影响：玩家按提示在背包里找「天界令牌 / 龙宫令牌 / 凤凰羽」找不到，会以为掉落坏了。
* 最小修复建议：三处 note 文案与词条对齐（或改成「战利品：天将令」这类不会误解的写法）。


---

## 2. 已核实澄清（排查过、结论「不是问题」，避免下一轮重复怀疑）

1. **药水词条不是「过期键」**：原版 `PotionItem.getName()` 用的键是 `getDescriptionId() + ".effect."`
   （patch 后源码 `net/minecraft/world/item/PotionItem.java:119`），即 `item.dynasty.dynasty_potion.effect.<effect>`，
   与 `lang/*.json` 里现存的 27 个键一致。仓库里 `validate_all.py` 打印的「232 个过期键」是误报。
2. **`dynasty:dynasty_potion` 不是「来源未核实」**：`DynastyBrewing.java:21-64` 用 Forge `PotionBrewEvent.Pre`
   实现酿造（粗制药水 + 龙晶/玉/符纸/龙鳞/朱砂 → 6 种王朝药水，荧石粉 → 天命）。
   `docs/quests-remaster/source-audit.json` 把它列为 `optional_unverified`，只是因为酿造没有 JSON 配方文件。
3. **`verify_loot.py` 报「palace_ruin 没被结构引用」是误报**：该表由代码结构使用 ——
   `worldgen/DynastyFeatures.java:169`、`worldgen/DynastyBuildings.java:153/203/256/307`、
   `worldgen/DynastyBuildings3.java:90/121/145/160/181/200/226/255/276/…`。
   我另做的引用核对：8 张宝箱表**全部**被引用，0 张孤儿；loot / recipe / advancement / 任务目标与奖励里的
   `dynasty:` 引用 **0 条悬空**。
4. **`validate_all.py` 报 `models/item/crimson_pillar.json → block/crimson_pillar` 是误报**：
   该 item 模型就是 `{"parent":"dynasty:block/crimson_pillar"}`，block 模型存在，贴图引用 0 缺失。
5. **凤凰 / 麒麟 / 九尾狐 / 大臣 都有生成配置**（我最初怀疑「没有生成」，已证伪）：
   `data/dynasty/worldgen/biome/*.json` 的 `spawners` 里写死了 ——
   `phoenix`：`celestial_sea` / `dragon_palace_deep` / `jiuxiao_cloud_sea`（monster）；
   `qilin`：`celestial_plains` / `dragon_palace_hall` / `dragon_ridge` / `jade_forest` / `jiuxiao_skyland`（creature）；
   `nine_tailed_fox`：`jade_forest` / `soul_river` / `underworld_wastes`；
   `minister`：`celestial_plains` / `dragon_palace_hall` / `jade_forest` / `jiuxiao_skyland`。
   凤凰羽来自 `loot_tables/entities/phoenix.json:9`，所以主线第 6 章的九霄门（需凤凰羽）**不阻塞**。
   （凤凰被配在「海」生物群系里，属观感/设定取向，不是数据错误。）
6. **「没有 SpawnPlacements 注册」不等于刷不出来**：Forge 给 `SpawnPlacements` 打了补丁 ——
   未注册时 `getPlacementType()` 返回 `NO_RESTRICTIONS`、`checkSpawnRules()` 返回 true
   （patch 后源码 `net/minecraft/world/entity/SpawnPlacements.java:53-56`、`:63-67`）。
   所以本模组生物都能自然生成；副作用见 §4 待核实项 a。
7. **四个门的「一次合成两座」与说明一致**：`recipes/jade_portal|underworld_portal|cloud_portal|dragon_gate.json`
   的 `result.count` 都是 2；材料也与游戏内说明一致（天朝门 3×3 玉块+龙晶、地府门同摆法+朱砂、
   九霄门 玉块×4+龙晶+凤凰羽、龙门 玉块×4+龙晶+龙鳞×2）。
8. **6 个 `minecraft:impossible` 成就都有代码颁发**（这条若缺，主线会整章完不成，故重点核对）：
   `entered_celestial` / `entered_underworld` → `DynastyWorldEvents.java:57/59`；
   `entered_jiuxiao` / `entered_dragon_palace` → `:61/63`（维度名映射与任务文案一致）；
   `slay_sky_general` → `entity/DynastyBosses.java:594`、`slay_dragon_king` → `:776`，
   两者都要求 `source.getEntity() instanceof ServerPlayer`，符合「亲自击败」的判定。
   `slay_emperor` / `slay_dragon_emperor` 用原版 `player_killed_entity` 触发器，无需代码。
9. **弓的蓄力动画是通的**：`houyi_bow.json` 的 overrides 用 `dynasty:pulling` / `dynasty:pull`
   （`models/item/houyi_bow.json:3946/3953/3960`），客户端在同一处注册了这两个属性
   （`client/DynastyClientEvents.java:28-35`），三张蓄力贴图与模型都在。
10. **资源完整性基本干净**：详见 §3.3（词条 / 贴图引用 / blockstate / parent / 盔甲层 / 实体贴图 全部 0 缺失）。
    唯一「看起来缺词条」的 3 个 `houyi_bow_pulling_*` 是弓的状态模型（不是物品），不需要词条。

---

## 3. 逐项检查结果与证据

### 3.1 生存获取链（配方 / 掉落 / 战利品 / 交易 / 任务奖励 / 代码）

* **物品全量对齐**：`assets/dynasty/models/item` 共 460 个模型（其中 3 个是弓的蓄力状态模型），
  与 Java 注册项一一对齐 —— **0 个注册物品缺模型**。
* **交易：本模组没有**。全库 grep `Trade / Merchant / Villager` 命中 0，也没有 trade JSON，
  所以获取来源只认下面 7 类：配方、宝箱战利品表、实体掉落表、Boss 掉落 switch、首杀奖励、
  任务奖励、成就与代码授予（`DynastyWeaponGifts` / `DynastyFestivals` / `DynastyRankPerks`）。
* **全量扫描**：460 个物品里 **33 个**在本轮扫描中没有任何「配方 / 宝箱 / 实体掉落 / 任务奖励 / 成就」来源，
  逐个落实后结论如下（都不是问题）：
  | 类别 | 数量 | 落实结果 |
  | --- | --- | --- |
  | `*_spawn_egg` 刷怪蛋 | 17 | 创造专属；主线不要求（`DynastyTabs` 只展示，无来源） ✔ 设计如此 |
  | `dynasty_emblem` | 1 | 创造栏封面，`docs/开发约定.md:152-157` 明确「不进列表、玩家拿不到」 ✔ |
  | `dynasty_potion` / `_splash_` / `_lingering_` | 3 | 酿造获得（`DynastyBrewing.java:21-64`） ✔ |
  | `houyi_bow_pulling_0/1/2` | 3 | 弓的状态模型，不是物品 ✔ |
  | `gilded_mace` / `supreme_sword` / `seven_star_saber` / `sunbow` | 4 | 代码条件授予（`DynastyWeaponGifts.java:39-66`；调用点 `DynastyWorldEvents.java:71/128`） ✔ |
  | `houyi_bow` / `zhuque_fan` | 2 | 有配方，材料依赖上面两件授予品 ✔（软锁风险见 §1.2-2） |
* **可达性闭合**：以「野生来源 + 全部配方」做传递闭包，34 项落在闭包外（就是上表这批）；
  把代码授予与酿造计入后 **= 0**。**配方环检测：0 条**（含 `#tag` 展开）。
* **配方 → 掉落 → 任务** 的引用完整性：loot / recipe / advancement / 任务目标与奖励里的 `dynasty:` 引用
  **0 条悬空**；8 张宝箱表 0 张孤儿（详见 §2.3）。
* **主线 27 个目标逐个核对**（`tools/art/quest_story.py` 第 1~8 章）：**全部可达**。

  | 主线目标 | 实际来源（证据） |
  | --- | --- |
  | `mu_mao` `shi_ge` `tong_dao` `tie_jian` | 合成（`data/dynasty/recipes/*.json`），材料为木/铜/铁 |
  | `bronze_ingot` | `recipes/bronze_ingot_alloy.json`（铜锭×3 + 铁锭×1 → ×4） |
  | `cinnabar` | **无矿**：只在宝箱里 —— `chests/temple.json`（×2 权重 8）、`ritual_circle.json`、`imperial_tomb.json`、`palace_ruin.json`、`watchtower.json`；与 `quest_story.py` HINTS 的说明一致 |
  | `ink_stick` `bamboo_slip` `blueprint` | 合成（煤炭/朱砂/竹子/纸） |
  | `jade` | 主世界玉矿（`placed_feature/jade_ore.json`，Y −60~60，需石镐） |
  | `exam_paper` `tiger_tally` | 合成 |
  | `rebel_head` | 首杀叛将**必掉**（`DynastyBossDrops.java:48` chance 1.0）+ 首杀奖励（`DynastyBossCombat.java:99-100`） |
  | `talisman_paper` `return_talisman` | 合成（纸+墨囊 / 符纸+末影珍珠） |
  | `dragon_crystal` | 主世界深层矿（Y −60~−5）+ 帝陵宝箱 + Boss 掉落 |
  | `jade_portal` `underworld_portal` `cloud_portal` `dragon_gate` | 合成，各给 **2 座**（材料见 §2.7） |
  | `eunuch_token` `emperor_bone` `sky_token` `sea_token` `dragon_emperor_seal` | 对应 Boss 首杀必掉 + 首杀奖励 |
  | `xuantian_jade` | `recipes/xuantian_jade.json`（帝骸骨 + 玉×2 + 龙晶）——与第 5 章「先斩始皇、再炼玄天玉」的顺序一致 |
  | 维度与成就 | 门的目标维度：`jade_portal→celestial_dynasty`（`DynastyBlocks.java:92-94`）、`underworld_portal→underworld`（`:116-120`）、`cloud_portal→jiuxiao`（`:100-104`）、`dragon_gate→dragon_palace`（`:106-110`）；`entered_*` 成就由 `DynastyWorldEvents.java:54-65` 授予 |
* **正常复杂链记录**（不是问题，供后续改内容时参照）：
  * **信物链**：自然生成 → 首杀必给信物 → 法阵·祭坛可反复召唤 → 25 条终盘配方引用 `dragon_emperor_seal`
    （`dragon_slayer` / `tianzi_sword` / `edict_of_dragon` / 混元·太乙·紫微·鸿蒙四套甲 / 玄天钺…）。
    由于龙帝是主线终点，这条链**只在主线之后**使用，任务书第 8 章也明确写了「不要为打龙帝先做依赖玉玺的装备」。
  * **授予链**：官阶 12 → 御赐金锏；官阶 17 → 尚方宝剑 →（+朱雀羽+凤凰羽+图纸）朱雀羽扇；
    击败 5 种不同 Boss → 七星宝刀；**白天**杀凤凰 → 射日弓 →（+天狼弓+凤凰羽+图纸）后羿弓。
  * **玉石链**：玉矿 → 玉 → 玉块 → 四个门 / 法阵·祭坛 / 玉系装备与大量饰品（属性表见 `docs/饰品与任务重制.md`）。
