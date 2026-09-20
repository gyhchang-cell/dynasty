# 基础料理与说明 v1（basic-foods-v1）

本批次新增 **6 种基础料理**（只给饥饿与饱和度，无状态效果、无永久属性）与 **3 组翻译键说明**
（料理用途 / Boss 信物用途 / 维度传送门目的地与回程提醒）。MC 1.20.1 / Forge 47.4.10。

## 1. 新内容一览

| 中文名 | 注册 ID | 饥饿恢复 | saturationMod | 堆叠 | 容器行为 |
| --- | --- | --- | --- | --- | --- |
| 炙肉串 | `dynasty:grilled_meat_skewer` | 8（4 个鸡腿） | 0.6 | 64 | 无 |
| 麦香饼 | `dynasty:wheat_cake` | 5（2.5 个鸡腿） | 0.5 | 64 | 无 |
| 蜜汁烤肉 | `dynasty:honey_roast` | 10（5 个鸡腿） | 0.7 | 64 | 无 |
| 田园炖菜 | `dynasty:countryside_stew` | 8（4 个鸡腿） | 0.6 | **1** | 食用后返还 1 个碗（`BowlFoodItem`） |
| 菌菇鱼汤 | `dynasty:mushroom_fish_soup` | 10（5 个鸡腿） | 0.6 | **1** | 食用后返还 1 个碗（`BowlFoodItem`） |
| 南瓜甜饼 | `dynasty:pumpkin_sweet_cake` | 6（3 个鸡腿） | 0.5 | 64 | 无 |

* 数值含义：饥饿恢复按「半个鸡腿 = 1 点」计；`saturationMod` 是 `FoodProperties.Builder.saturationMod`
  的系数（**不是**最终回复的饱和度数值）。
* 注册位置：`src/main/java/com/dynasty/DynastyBasicFoods.java`（新类，只含这 6 件）。
  4 件用 `food()`（普通 `Item`），2 种汤用 `stew()`（`BowlFoodItem` + `stacksTo(1)`）。

## 2. 配方（全部 `minecraft:crafting_shapeless`）

| 配方文件 | 材料（按 ingredients 顺序） | 产量 |
| --- | --- | --- |
| `recipes/grilled_meat_skewer.json` | 熟猪排 + 熟鸡肉 | 炙肉串 ×2 |
| `recipes/wheat_cake.json` | 小麦 + 小麦 + 鸡蛋（**两个独立配料槽**，共消耗 2 个小麦） | 麦香饼 ×2 |
| `recipes/honey_roast.json` | 熟猪排 + 蜂蜜瓶 | 蜜汁烤肉 ×1 |
| `recipes/countryside_stew.json` | 胡萝卜 + 马铃薯 + 棕色蘑菇 + 碗 | 田园炖菜 ×1 |
| `recipes/mushroom_fish_soup.json` | 熟鳕鱼 + 棕色蘑菇 + 碗 | 菌菇鱼汤 ×1 |
| `recipes/pumpkin_sweet_cake.json` | 南瓜 + 小麦 + 糖 | 南瓜甜饼 ×2 |

全部只使用原版材料，没有加稀有材料、状态效果或额外奖励。

**容器行为（代码依据，未实测）**

* 蜜汁烤肉：原版 `Items.HONEY_BOTTLE` 注册时带 `craftRemainder(GLASS_BOTTLE)`，而
  `Recipe.getRemainingItems()`（1.20.1 默认实现，Shapeless 沿用）会对带 `craftRemainder` 的原料返还一件。
  因此 **合成后返还 1 个玻璃瓶**，配方里**没有**再写一份瓶子（写两份会变成双份返还）。
* 两种汤：`BowlFoodItem#finishUsingItem` 在非创造模式返回 `new ItemStack(Items.BOWL)`，
  即**食用后返还 1 个碗**；合成时碗作为原料被正常消耗（碗没有 `craftRemainder`）。

## 3. 配方解锁进度（沿用原版机制）

仓库内**没有**任何 `recipe_unlocked` 用法（全库 grep 为 0，`tools/art/verify_*.py` 也不涉及），
所以按原版标准做法为 6 个配方各加一个解锁进度：

```
data/dynasty/advancements/recipes/<id>.json
  parent: minecraft:recipes/root
  criteria: has_the_recipe（minecraft:recipe_unlocked） + has_<主材料>（minecraft:inventory_changed）
  rewards:  { recipes: [dynasty:<id>] }
```

主材料分别是：熟猪排 / 小麦 / 蜂蜜瓶 / 棕色蘑菇 / 熟鳕鱼 / 南瓜 —— 玩家**拿到主材料就会点亮配方**。
（这 6 个文件只有 criteria 与 rewards，没有 title/description，属原版配方进度的常见形态；
不会与 `gen_advancements.py` 生成的带标题成就冲突。）

## 4. 显示与创造栏

* 创造栏：加在现有「王朝」页的美食段落（`DynastyTabs.java`，6 行 `output.accept`）。
* 词条：中英名 6 条 + 说明键 15 条（见第 6 节），`zh_cn.json` / `en_us.json` 现在各 **621 键**（键集合完全一致）。

### 临时贴图（重要，不是新美术）

以下 6 件**复用 Minecraft 原版贴图**做临时模型，`models/item/<id>.json` 里 `layer0` 指向原版命名空间，
**没有复制、没有修改原版贴图文件，也没有生成任何新图片**：

| 料理 | 临时引用的原版贴图 |
| --- | --- |
| 炙肉串 | `minecraft:item/cooked_mutton` |
| 麦香饼 | `minecraft:item/bread` |
| 蜜汁烤肉 | `minecraft:item/cooked_porkchop` |
| 田园炖菜 | `minecraft:item/beetroot_soup` |
| 菌菇鱼汤 | `minecraft:item/mushroom_stew` |
| 南瓜甜饼 | `minecraft:item/pumpkin_pie` |

这 6 张贴图是**占位**，请勿当成新美术资产；后续替换为专属贴图时只需改 `models/item/*.json` 的 `layer0`。


## 5. 玩家说明（全部走翻译键）

新增类 `src/main/java/com/dynasty/client/DynastyInfoKeys.java`：只放「物品路径 → 翻译键」的对应表，
Java 里**没有一句成段中文**；文案全在 `lang/zh_cn.json`、`lang/en_us.json`。
展示沿用项目现有 tooltip 机制：`DynastyItemInfo.lines()` 末尾追加这些键的行，再由 `DynastyTooltips`
（`ItemTooltipEvent`）渲染 —— 没有新图鉴系统，也没有改任务配置。

| 键 | 内容（中文） | 作用对象 |
| --- | --- | --- |
| `dynasty.info.food.grill` 等 6 条 | 「食用：恢复 X 点饥饿值（Y 个鸡腿）。」 | 6 种料理各一条（X 与 Java 注册一致） |
| `dynasty.info.food.stew_hint` | 「汤羹：最多堆叠 1，食用后返还 1 个碗。」 | 田园炖菜、菌菇鱼汤 |
| `dynasty.info.food.honey_bottle_hint` | 「合成时按原版蜂蜜瓶机制返还 1 个玻璃瓶，配方不会额外再给瓶子。」 | 蜜汁烤肉 |
| `dynasty.info.token.altar` | 「Boss 信物：用于法阵·祭坛召唤对应 Boss。」 | 6 种信物（龙帝玉玺 / 叛将首级 / 内廷令牌 / 帝骸骨 / 天将令 / 龙宫玉印） |
| `dynasty.info.token.guide` | 「召唤条件详见任务书中的 Boss 图鉴。」 | 同上 6 种信物 |
| `dynasty.info.portal.<portal>` 4 条 | 「F 传送门：放下后右键前往「目的地」……」（天朝·龙庭 / 地府 / 九霄天界 / 东海龙宫；龙宫提示备好水下呼吸） | 4 座传送门 |
| `dynasty.info.portal.return_hint` | 「回程：目的地不会自动生成回程门——合成一次给 2 座，请带一座过去，或随身带归乡符。」 | 4 座传送门 |

* 文案只写**已有机制**：不写「永久增强」「神级料理」之类不存在的效果；不声称目的地会自动生成回程门
  （代码里 `DynastyPortalBlock` 只做落点安全检查，不造回程门）。
* 信物键只加在**代码确认过的 6 个信物**上（`RitualAltarBlock` 的 `TOKEN_TO_BOSS` 映射）。
* 已有相同文案不会重复显示：`DynastyInfoKeys` 会跳过与上一条完全相同的行，也会跳过不存在的翻译键
  （所以装老词条包不会看到原始键名）。
* 传送门原有说明（`DynastyBlockInfo`）讲的是合成与基本用法，新加的两条补的是**目的地 + 回程准备**，
  两者不完全重复；如果你觉得罗嗦，删掉 `DynastyInfoKeys.KEYS` 里对应的 entry 即可。
* 料理 tooltip 的第一行仍是项目原有的通用简介（`DynastyItemInfo.category` 返回「王朝物品……」），
  本批**没有**改动那个方法，以免影响其它已有食物的显示；新增的食用说明追加在它下面。

## 6. 修改文件清单

**新增**

```
src/main/java/com/dynasty/DynastyBasicFoods.java                     6 件料理注册
src/main/java/com/dynasty/client/DynastyInfoKeys.java                翻译键说明表
src/main/resources/assets/dynasty/models/item/{grilled_meat_skewer,wheat_cake,honey_roast,
    countryside_stew,mushroom_fish_soup,pumpkin_sweet_cake}.json     临时贴图模型 ×6
src/main/resources/data/dynasty/recipes/<同 6 个 id>.json            无序配方 ×6
src/main/resources/data/dynasty/advancements/recipes/<同 6 个 id>.json 配方解锁进度 ×6
docs/content/basic-foods-v1.md                                       本文件
```

**小幅增补（每处只加必要行）**

```
src/main/java/com/dynasty/DynastyContent.java         +1 行：注册 DynastyBasicFoods.ITEMS
src/main/java/com/dynasty/DynastyTabs.java            +6 行：把 6 件料理放进现有美食段落
src/main/java/com/dynasty/client/DynastyItemInfo.java +6 行：追加翻译键说明（不影响其它物品）
src/main/resources/assets/dynasty/lang/zh_cn.json     +21 键（6 名称 + 15 说明）
src/main/resources/assets/dynasty/lang/en_us.json     +21 键（同上）
```

**没有改动**：主线任务与奖励、Boss、武器、饰品效果、世界生成、建筑、现有平衡数值；
没有改 `modpack/mods/dynasty-1.4.0.jar`（发布 jar 未动，等统一打包）；没有生成或重绘图片。

## 7. 验证结果

| 项目 | 命令 | 结果 |
| --- | --- | --- |
| 离线编译 | `./gradlew compileJava --offline --rerun-tasks` | **BUILD SUCCESSFUL**；日志中 error/failed 计数 0；`build/classes/.../DynastyBasicFoods.class`、`DynastyInfoKeys.class` 已生成 |
| 资源/词条/配方自检 | `python3 tools/maintenance/check_all.py` | 资源 512 文件（模型 491、外部贴图引用 6）0 错误；语言 621/621 键 0 错误；配方 420 文件 0 错误；汇总 934 文件 · 0 错误 0 警告 0 跳过 |
| 项目词条自检 | `python3 tools/art/verify_lang.py` | 新增 6 件**没有**被点名；报告里 6 条 `houyi_bow_pulling_0/1/2 缺词条` 是**本批之前就存在**的（那是弓的状态模型、不是物品） |
| 项目装备自检 | `python3 tools/art/verify_gear.py` | 新增内容未被点名；报告里 8 条「饰品贴图不是 32×32」是**本批之前就存在**的 |
| 数值/配方/词条一致性 | `/tmp/validate_foods.py`（临时只读脚本，未入库） | 6 件：注册值与设计要求一致、配方材料与产量一致、模型引用一致、词条与解锁进度齐全 ✅ |

### 未实测（没有进游戏验证，不能声称已在游戏中通过）

* 吃下 6 种料理后的**实际饥饿 / 饱和度回复**（只有 Java 注册值作为依据）。
* 两种汤**食用后返还碗**、蜜汁烤肉**合成后返还玻璃瓶**（依据是原版 `BowlFoodItem` 与
  `craftRemainder` + `Recipe.getRemainingItems()` 的实现，**未在游戏里试过**）。
* 配方书里**解锁提示是否按预期点亮**（依据是原版 `recipe_unlocked` + `inventory_changed`）。
* tooltip 的**实际排版 / 换行效果**（键齐全、代码路径正确，但没在客户端里看过）。
* 六张贴图只是临时引用原版贴图，**观感未评估**。
