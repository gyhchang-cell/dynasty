# 翻译键补充记录（translation-changes）

> 本轮（2026-09-20）只做「补已确认缺失的键」。**未覆盖、未删除、未排序、未格式化任何已有词条**。
> 改动文件只有两个：
> `src/main/resources/assets/dynasty/lang/zh_cn.json`、`src/main/resources/assets/dynasty/lang/en_us.json`
> （各 +8 键，592 → 600 键；git diff 为纯新增 + 1 行逗号调整）。
> 规则来源：`docs/开发约定.md` §3「新增物品/方块/实体/维度/成就，必须同时补齐：注册 → 模型 → 贴图 → 语言（中英）」。

## 1. 核对方法

用只读脚本（`/tmp` 内一次性脚本，未写入项目）把「注册代码 + 实际引用」与两份 lang 逐类对照：

| 类别 | 注册/引用来源 | 数量 | 结果 |
| --- | --- | --- | --- |
| 物品（非方块） | `assets/dynasty/models/item/*.json` | 457 | 全部有 `item.dynasty.*` ✅ |
| 方块物品 | 同上（`models/item/*.json` 里指向 `block/` 的那批） | 23 | 用 `block.dynasty.*` 命名 ✅（`verify_lang.py` 双查，约定如此） |
| 弓的状态模型 | `houyi_bow_pulling_0/1/2` | 3 | **不是物品**，不需要词条 ✅ |
| 方块 | `assets/dynasty/blockstates/*.json` | 21 | 全部有 `block.dynasty.*` ✅ |
| 实体 | `ENTITIES.register("…")` | 21 | 全部有 `entity.dynasty.*` ✅ |
| 效果 | `EFFECTS.register("…")` | 7（另有 2 个历史键共 9） | ✅ |
| 附魔 | `ENCHANTMENTS.register("…")` | 3 | ✅ |
| 药水 | `POTIONS.register("…")` + 3 种药水物品 | 6 种 | `potion.dynasty.*` 6 条 + `item.dynasty.{dynasty,splash,lingering}_potion.effect.*` 18 条 ✅ |
| 成就 | `data/dynasty/advancements/*.json` 的 `translate` | 30 个文件 | 60 条 `.title/.description` 全齐 ✅ |
| 界面标题 | `Component.translatable("screen.…")` | 3 | ✅ |
| 创造栏 | `itemGroup.dynasty.dynasty` | 1 | ✅ |
| 伤害类型 | `data/dynasty/damage_type/*.json` 的 `message_id` | 2 | **`solar_judgment` 缺键** → 已补 |
| 维度 | `data/dynasty/dimension/*.json` | 4 | **`jiuxiao` / `dragon_palace` 缺键** → 已补 |
| 生物群系 | `data/dynasty/worldgen/biome/*.json` | 10 | **4 个缺键** → 已补 |
| Curios 槽位 | `data/dynasty/curios/slots/*.json` | 10 | 全部由 Curios 本体提供中英词条（已验证 `curios-forge-5.14.1` 的 `lang/zh_cn.json` 含全部 10 个 `curios.identifier.*`）✅ 不要重复添加 |
| 音效字幕 | `assets/dynasty/sounds.json` | 不存在 | 无字幕键需求 ✅ |
| 按键绑定 / 容器菜单 / 自定义属性 | `KeyMapping` / `AbstractContainerMenu` / 自定义 `Attribute` 注册 | 0 | 都不存在，无需键 ✅ |
| 任务书引用 | `modpack/config/ftbquests/**/*.snbt` 里 449 个 `dynasty:*` id | 449 | 全部能落到 item/block/entity/advancement/dimension/biome/tag 上，无遗漏 ✅ |

## 2. 新增键（共 8 键 × 2 语言 = 16 条）

| # | 键 | zh_cn | en_us | 命名依据（证据） |
| --- | --- | --- | --- | --- |
| 1 | `death.attack.dynasty.solar_judgment` | `%1$s 被烈阳审判灼尽了` | `%1$s was scorched by the solar judgment` | 伤害类型 `data/dynasty/damage_type/solar_judgment.json` 的 `message_id = dynasty.solar_judgment`；同目录 `qinglong_descent` 已有 `death.attack…` 与 `…player` 两条，说明键格式为 `death.attack.<message_id>[.player]`；该伤害由 `DynastyBowRitual.java:56-58`（`SOLAR_DAMAGE`）使用。措辞按 id 语义（solar judgement）+ 火焰粒子（`ParticleTypes.FLAME`）取「烈阳审判」 |
| 2 | `death.attack.dynasty.solar_judgment.player` | `%1$s 被 %2$s 引来的烈阳审判灼尽了` | `%1$s was scorched by %2$s's solar judgment` | 同上；句式和既有 `qinglong_descent.player` 保持一致（`%1$s` 受害者、`%2$s` 击杀者） |
| 3 | `dimension.dynasty.jiuxiao` | `九霄天界` | `Nine-Heaven Realm` | 同伴键 `dimension.dynasty.celestial_dynasty = 天朝·龙庭` / `…underworld = 地府`；中文名取自成就 `advancements.dynasty.entered_jiuxiao.description`「穿过云门进入**九霄天界**」；英文取自同键的 `Enter the nine-heaven realm` |
| 4 | `dimension.dynasty.dragon_palace` | `东海龙宫` | `Dragon Palace` | 中文取自 `advancements.dynasty.entered_dragon_palace.description`「穿过龙门进入**东海龙宫**」；英文沿用既有译名（`block.dynasty.dragon_gate = Dragon Palace Portal`、`entered_dragon_palace.title = Into the Dragon Palace`） |
| 5 | `biome.dynasty.jiuxiao_skyland` | `九霄仙岛` | `Nine-Heaven Skyland` | 中文见 `docs/更新日志-1.4.0.md:1301`「两个群系：**九霄仙岛**（jiuxiao_skyland）、**云海**（jiuxiao_cloud_sea）」；英文按同伴键风格（`celestial_plains = Celestial Plains`）与 #3 的 Nine-Heaven 统一 |
| 6 | `biome.dynasty.jiuxiao_cloud_sea` | `云海` | `Cloud Sea` | 同上（同一条更新日志）；英文对照既有 `celestial_sea = Celestial Sea` |
| 7 | `biome.dynasty.dragon_palace_hall` | `龙宫正殿` | `Dragon Palace Hall` | 中文见 `docs/更新日志-1.4.0.md:2170`「两个群系：**龙宫正殿**（dragon_palace_hall）、**深渊**（dragon_palace_deep）」 |
| 8 | `biome.dynasty.dragon_palace_deep` | `深渊` | `Abyss` | 同上；英文对照既有 `item.dynasty.abyss_pearl = Abyss Pearl` |

## 3. 明确「查过但不需要补」的项（避免下一轮重复怀疑）

* `item.dynasty.{altar,bronze_block,…,jade_ore,…}` 等 23 条**看起来缺**，其实是方块物品 —— 它们的名字走
  `block.dynasty.*`，21 个方块键齐全。这是 `verify_lang.py` 的既定规则（`item.` / `block.` 双查）。
* `houyi_bow_pulling_0/1/2` 是 `models/item` 下的**状态模型**（由 `houyi_bow.json` 的 `overrides` 引用），
  不是注册物品，不需要词条。
* `death.attack.adv.<id>`：原版不存在这种「击杀方式」键（1.20.1 `DamageSource` 只用
  `death.attack.<msgId>` 与 `death.attack.<msgId>.player` 两条），所以没有新增。
* `curios.identifier.{back,belt,body,bracelet,charm,hands,head,necklace,ring}`：由 Curios 本体提供；
  本模组只覆盖了 `curios.identifier.curio = 万能饰品`。

## 4. 待确认（本轮**没有**动，需要作者确认后再做）

1. **大量玩家可见文本是硬编码中文**（不是翻译键），英文玩家会看到中文，例如：
   `DynastyBossCombat.java` 的 `§6[首杀]`、`block/RitualAltarBlock.java:83-91` 的法阵提示、
   `client/DynastyBlockInfo.java` / `client/DynastyItemUsage.java` 的用法说明、`client/GuideScreen.java` 的图鉴正文、
   `DynastyTrinketTips` 的悬浮说明。要本地化必须改 Java（改成 `Component.translatable`），
   **超出本轮「只补翻译键」的范围**，故只记录。
2. **`dimension.dynasty.*` 的读取方未在本仓库内找到**（Java / 任务书 / 配置里都没有引用）。
   我按同伴键的命名惯例补了 jiuxiao / dragon_palace 两条，但**用途待确认**：
   如果实际没有任何模组读取这个键，这两条是冗余的（无害）。
3. **`solar_judgment` 的死亡文案是我按 id 语义拟的**（游戏内此前会显示原始键名）。
   若作者对该招式有正式中文名（例如「射日真火」之类），以作者命名为准，替换这两条即可。
4. 图鉴/用法说明里对**玉矿 y≤30、龙晶矿「天朝·龙庭地下生成 / 需玉镐」**的描述与数据不符
   （详见 `docs/audit/deepseek-content-audit.md` §1.3）。这属于文案纠正，本轮未改（不在允许范围内）。
