# 关键材料来源索引（materials）

> 范围：主线与高级装备真正用到的关键材料。**只列已核实来源**，每条给出证据文件；
> 「没有配方」不等于拿不到 —— 本表把挖掘、宝箱、生物掉落、首杀奖励、任务奖励、货币兑换都查了。
> 证据来源：`data/dynasty/recipes/*`、`data/dynasty/loot_tables/{blocks,chests,entities}/*`、
> `data/dynasty/forge/biome_modifier/*`、`data/dynasty/worldgen/placed_feature/*`、
> `data/minecraft/tags/blocks/*`、`DynastyBossDrops.java`、`DynastyBossCombat.java`（首杀）、
> `modpack/config/ftbquests/quests/chapters/*.snbt`（任务奖励，经 `docs/quests-remaster/book.json` 统计）。

## 1. 挖掘类（唯一两条“要下矿”的材料）

| 材料 | ID | 挖掘来源（已核实） | 工具等级 | 其它来源 |
| --- | --- | --- | --- | --- |
| 玉 | `dynasty:jade` | 主世界**玉矿 / 深层玉矿**：`placed_feature/jade_ore.json`（Y −60…60，每区块 6 次）；方块掉落表 `loot_tables/blocks/jade_ore.json`、`deepslate_jade_ore.json` | `data/minecraft/tags/blocks/needs_stone_tool.json`（**石镐**即可） | 熔炼矿石（`recipes/jade_from_ore.json`、`jade_from_deepslate_ore.json`）；玉块拆解（`jade_from_block.json`）；6 张宝箱表；麒麟掉落（上限 2，概率 0.8）+ 首杀麒麟 |
| 龙晶 | `dynasty:dragon_crystal` | 主世界**龙晶矿**：`placed_feature/dragon_crystal_ore.json`（Y −60…−5，每区块 2 次） | `needs_iron_tool.json`（**铁镐**即可） | 熔炼（`dragon_crystal_from_ore.json`）；帝陵/帝王陵/法阵宝箱；龙帝/凤凰/始皇掉落表；代码掉落：龙帝 4、始皇 2、天将 3、龙王 4 |

* 两个矿的**生物群系**都是 `#minecraft:is_overworld`（`forge/biome_modifier/jade_ore.json`、`dragon_crystal_ore.json`）。
  ⚠ 游戏内说明里写的「龙晶矿在天朝·龙庭地下」与数据不符，见 `docs/audit/deepseek-content-audit.md` §1.3。

## 2. 冶材与货币

| 材料 | ID | 已核实来源 |
| --- | --- | --- |
| 青铜锭 | `dynasty:bronze_ingot` | 合成 `recipes/bronze_ingot_alloy.json`（铜锭×3 + 铁锭×1 → ×4）；拆青铜块 `bronze_ingot_from_block.json`；宝箱（兵营/宫殿遗迹）；掉落：叛将（上限 3，0.8）、兵马俑（上限 1，0.15）等（实体表 imperial_soldier / rebel_soldier / royal_guard / terracotta_warrior 均含） |
| 银锭 | `dynasty:silver_ingot` | **无配方**：宝箱（兵营、神庙）＋ 掉落：宦官首脑（上限 3，0.8）、刺客（上限 1，0.2） |
| 铜钱 | `dynasty:copper_coin` | **任务奖励主力**（book.json 统计：488 个任务发放）；宝箱（兵营、烽火台）；掉落（弓手、大臣、叛军）；兑换（银钱 → 铜钱 `coin_down_copper.json`） |
| 银钱 | `dynasty:silver_coin` | 合成 `coin_up_silver_coin.json`（铜钱×9）；拆金币 `coin_down_silver.json`；宝箱（宫殿遗迹）；掉落（刺客） |
| 金钱 | `dynasty:gold_coin` | 合成 `coin_up_gold_coin.json`（银钱×9）；拆玉钱 `coin_down_gold.json`；宝箱（宫廷/宫殿遗迹）；掉落（宦官、年兽、叛将、禁军；龙王上限 16，0.8）；任务奖励 106 处 |
| 玉钱 | `dynasty:jade_coin` | 合成 `coin_up_jade_coin.json`（金钱×9）；拆龙钱 `coin_down_jade.json`；宝箱（宫廷/帝王陵/帝陵/法阵）；掉落（九尾狐、始皇） |
| 龙泉钱 | `dynasty:dragon_coin` | 合成 `coin_up_dragon_coin.json`（玉钱×9）；宝箱（帝王陵）；掉落表（龙帝、始皇） |

## 3. 玉块与“无矿”材料

| 材料 | ID | 已核实来源 |
| --- | --- | --- |
| 玉块 | `dynasty:jade_block` | 合成 `coin_up_jade_block.json`（玉×9）；方块掉落表 `blocks/jade_block.json` |
| 朱砂 | `dynasty:cinnabar` | **无矿、无配方**：只在宝箱里 —— `chests/temple.json`、`ritual_circle.json`、`imperial_tomb.json`（与任务书 HINTS「当前没有可挖的朱砂矿」一致） |
| 符纸 | `dynasty:talisman_paper` | 合成 `talisman_paper.json`（纸 + 朱砂）；宝箱（帝陵/宫殿遗迹/法阵）；掉落（刺客、宦官首脑） |
| 徽墨 | `dynasty:ink_stick` | 合成 `ink_stick.json`（煤炭×2 + 朱砂）；宝箱（宫廷、烽火台） |
| 竹简 | `dynasty:bamboo_slip` | 合成 `bamboo_slip.json`（竹子×2 + 线） |
| 兵器图纸 | `dynasty:blueprint` | 合成 `blueprint.json`（纸 + 徽墨 + 竹简）；7 张宝箱表；掉落：禁军（上限 1，0.25） |
| 精钢 | `dynasty:refined_steel` | 合成 `refined_steel.json`（铁锭×3 + 朱砂 → ×2）；宝箱（兵营、神庙）；掉落：年兽（上限 2，0.8）+ 首杀年兽 |

## 4. 丝织与杂项

| 材料 | ID | 已核实来源 |
| --- | --- | --- |
| 生丝 | `dynasty:raw_silk` | 合成 `raw_silk.json`（线×3） |
| 丝绸 | `dynasty:silk` | 合成 `silk.json`（生丝×3）；宝箱（宫殿遗迹）；掉落：九尾狐（上限 3，0.8）+ 首杀九尾狐 |
| 织锦 | `dynasty:brocade` | 合成 `brocade.json`（丝绸×2 + 金锭）；宝箱（宫廷、神庙、烽火台） |
| 蟠桃 | `dynasty:immortal_peach` | 合成 `immortal_peach.json`（金苹果 + 玉） |
| 桃酥 | `dynasty:peach_bun` | 合成 `peach_bun.json`（小麦 + 糖 + 蜂蜜瓶） |

## 5. 六种 Boss 信物（复战 + 高阶装备）

| 信物 | ID | 来源（两条都成立） |
| --- | --- | --- |
| 叛将首级 | `dynasty:rebel_head` | 击杀叛将（上限 1，概率 1.0）＋ 首杀叛将奖励（+240 功名） |
| 内廷令牌 | `dynasty:eunuch_token` | 击杀宦官首脑（1.0）＋ 首杀奖励（+240） |
| 帝骸骨 | `dynasty:emperor_bone` | 击杀**不死始皇**（1.0，另有首杀 +300）；龙帝也有 0.7 概率；另见 3 张宝箱表（宫廷/帝王陵/帝陵） |
| 龙帝玉玺 | `dynasty:dragon_emperor_seal` | 击杀龙帝（1.0）＋ 首杀奖励（+400） |
| 天将令 | `dynasty:sky_token` | 击杀九霄天将（1.0）＋ 首杀奖励（+300） |
| 龙宫玉印 | `dynasty:sea_token` | 击杀东海龙王（1.0）＋ 首杀奖励（+320） |

* 信物的**其它用途**：法阵·祭坛复战（`RitualAltarBlock.bossFor`）、高阶配方
  （`dragon_emperor_seal` 被 25 条配方引用，见 `docs/audit/deepseek-content-audit.md` §3.1）。

## 6. 神兽材料与终盘材料

| 材料 | ID | 已核实来源 |
| --- | --- | --- |
| 龙鳞 | `dynasty:dragon_scale` | **无配方**：龙王掉落（上限 4，1.0）、凤凰掉落（上限 2，1.0）+ 首杀凤凰；实体掉落表（龙帝/年兽/始皇）；宝箱（帝王陵） |
| 凤凰羽 | `dynasty:phoenix_feather` | **无配方**：`loot_tables/entities/phoenix.json`（凤凰掉落）。凤凰刷新在 `celestial_sea` / `dragon_palace_deep` / `jiuxiao_cloud_sea`（群系 `spawners`） |
| 麒麟角 | `dynasty:qilin_horn` | **无配方**：`loot_tables/entities/qilin.json`。麒麟刷新在 `celestial_plains` / `dragon_palace_hall` / `dragon_ridge` / `jade_forest` / `jiuxiao_skyland` |
| 狐尾 | `dynasty:fox_tail` | **无配方**：`loot_tables/entities/nine_tailed_fox.json`。九尾狐刷新在 `jade_forest` / `soul_river` / `underworld_wastes` |
| 玄天玉 | `dynasty:xuantian_jade` | 合成 `xuantian_jade.json`（帝骸骨 + 玉×2 + 龙晶）；天将 0.5 概率直接掉 |
| 帝骸骨 | 见 §5 | — |

## 7. 待确认

1. **宝箱概率/权重未审计**：本表只核实「该材料出现在哪张表里」，**没有核对每张表的权重与 roll 次数**
   （例如朱砂在神庙表里的权重是 8、rolls 是 4，实际期望产量未算）。想调平衡请看
   `data/dynasty/loot_tables/chests/*.json` 的 `rolls` 与 `weight`。
2. **矿物实际分布密度未实测**：`placed_feature` 只给出「每区块 6 次 / Y −60…60」这类参数，
   我没在游戏里统计真实产出速度。
3. **`dynasty:silver_ingot` / `cinnabar` / `dragon_scale` / `phoenix_feather` / `qilin_horn` / `fox_tail` 没有配方**——
   这是**事实**不是缺陷（来源是宝箱与掉落），但如果以后有人只查配方就会误判「拿不到」。
4. 任务奖励数量按 `book.json` 统计（铜钱 488 处、金钱 106 处），**未逐条核对奖励池平衡**。
5. 我列过候选 id `dynasty:talisman`，它在模组里**不存在**（有效的是 `talisman_paper`），已从表里剔除。
