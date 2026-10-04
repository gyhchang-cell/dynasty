# 当前方块资源清单 · native16-review-v10

基于 `before/` 的固定初始快照：**45 个注册方块 ID、34 张 Dynasty 方块 PNG、19 张引用的原版 PNG**。当前 34 张 Dynasty 图全部 16×16、全不透明，均与 v9 manifest 哈希一致。v9 已交付不能写成“尚未完成”或“占位”。

本清单覆盖 blockstates 的所有模型分支、父模型继承、纹理变量与实际注册的方块物品。详细解析、SHA-256、颜色/透明像素及原版动画元数据见 [inventory.json](inventory.json)。没有修改源资源。

## 状态与范围

- 首批评审候选：`marble_block`、`jade_ore`、`jade_mending_forge`；均未接入。
- 扩展评审候选：`dragon_crystal_ore`；未接入。
- `palace_bricks` 为用户确认的 7 色样稿，明确保留。其余默认保留，不把没有专属 PNG 当作未完成证据。
- 已认可饰品、金合欢展示架与其他成品保留；本清单没有重绘或声称全面审计盔甲图标及穿戴 UV。
- 新祭坛未收到最终 ID、UV 与尺寸，未制作候选、未注册或接入；既有 `altar` / `ritual_altar` 保留。
- 未修改模型几何、碰撞、功能、公共注册代码、建筑、存档、实例、模组或导出列表；尚未游戏内实测。

## 注册 ID → 实际贴图

表中的 `dynasty:block/x` 对应 `src/main/resources/assets/dynasty/textures/block/x.png`；`minecraft:block/x` 对应原版 `assets/minecraft/textures/block/x.png`。完整路径、尺寸和颜色数在下方 PNG 表及 JSON 中。

| 方块 ID | 实际 PNG 资源引用 | 完成记录 / 处理判断 |
|---|---|---|
| `dynasty:altar` | `dynasty:block/altar` | v9 已交付。**并行任务边界，保留**。现有 v9 祭坛资源保留；另一个任务负责龙口遗迹与召唤祭坛，不推断其新 ID 或 UV。 |
| `dynasty:bounty_board` | `minecraft:block/bookshelf` | 告示板完成记录；复用原版。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:bronze_block` | `dynasty:block/bronze_block` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:celestial_stone` | `dynasty:block/celestial_stone` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:chime_bell` | `dynasty:block/chime_bell` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:cloud_portal` | `dynasty:block/cloud_portal` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:cloud_stone` | `dynasty:block/cloud_stone` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:clue_tablet` | `minecraft:block/chiseled_stone_bricks` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:crimson_pillar` | `dynasty:block/crimson_pillar_side`<br>`dynasty:block/crimson_pillar_top` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:deepslate_jade_ore` | `dynasty:block/deepslate_jade_ore` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:dragon_crystal_ore` | `dynasty:block/dragon_crystal_ore` | v9 已交付。**扩展候选，未接入**。v9 已交付。紫系矿物 23/256 像素、最亮紫 1 像素，候选扩展提升小图辨识；保留现有 PNG。 |
| `dynasty:dragon_gate` | `dynasty:block/dragon_gate` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:dragon_throne` | `dynasty:block/dragon_throne` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:echo_bell` | `minecraft:block/gold_block` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:element_lamp` | `minecraft:block/brown_mushroom_block`<br>`minecraft:block/glowstone`<br>`minecraft:block/magma`<br>`minecraft:block/prismarine_bricks`<br>`minecraft:block/redstone_lamp`<br>`minecraft:block/redstone_lamp_on`<br>`minecraft:block/sea_lantern`<br>`minecraft:block/shroomlight` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:ember_brazier` | `dynasty:block/bronze_block`<br>`minecraft:block/coal_block` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:essence_condenser` | `dynasty:block/essence_condenser`<br>`minecraft:block/amethyst_block` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:herbal_basin` | `dynasty:block/jade_block`<br>`dynasty:block/marble_block` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:hide_stretcher` | `dynasty:block/crimson_pillar_side`<br>`minecraft:block/brown_terracotta` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:imperial_lantern` | `dynasty:block/imperial_lantern` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:incense_burner` | `dynasty:block/incense_burner` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:jade_block` | `dynasty:block/jade_block` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:jade_mending_forge` | `dynasty:block/jade_mending_forge` | v9 已交付。**首样候选，未接入**。v9 已交付且已有异形模型。现有 3 个元素共用一张石料面，候选按现有 UV 区分作业顶面、侧面与正面；不改几何、碰撞或功能。 |
| `dynasty:jade_ore` | `dynasty:block/jade_ore` | v9 已交付。**首样候选，未接入**。v9 已交付。浅玉色亮点较少且分散，候选改善矿簇轮廓与基底关系；保留现有 PNG。 |
| `dynasty:jade_portal` | `dynasty:block/jade_portal` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:jade_soil` | `dynasty:block/jade_soil` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:lapidary_bench` | `dynasty:block/crimson_pillar_side`<br>`dynasty:block/jade_block`<br>`dynasty:block/palace_bricks` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:marble_block` | `dynasty:block/marble_block` | v9 已交付。**首样候选，未接入**。v9 已交付。灰阶碎斑较多，候选用更连贯的大色簇与克制石纹；保留现有 PNG。 |
| `dynasty:marrow_vat` | `dynasty:block/marrow_vat` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:palace_bricks` | `dynasty:block/palace_bricks` | v9 已交付。**已认可，保留**。v9 release-notes 明确写明玩家确认的 7 色样稿；保持原文件与哈希。 |
| `dynasty:pearl_sand` | `dynasty:block/pearl_sand` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:plaque` | `dynasty:block/plaque` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:ritual_altar` | `dynasty:block/ritual_altar` | v9 已交付。**并行任务边界，保留**。现有 v9 召唤祭坛资源保留；另一个任务负责相关 3D 模型，未收到新祭坛最终 ID、UV、尺寸，既不做候选也不接入。 |
| `dynasty:ruin_controller` | `minecraft:block/gilded_blackstone` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:ruin_gate` | `minecraft:block/polished_deepslate` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:ruin_shell` | `dynasty:block/palace_bricks` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:screen` | `dynasty:block/screen` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:spirit_soil` | `dynasty:block/spirit_soil` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:star_dial` | `minecraft:block/daylight_detector_top`<br>`minecraft:block/lodestone_side`<br>`minecraft:block/lodestone_top` | 机关完成记录；复用原版/宫砖。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:star_soil` | `dynasty:block/star_soil` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:taiko_drum` | `dynasty:block/taiko_drum` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:tidal_stone` | `dynasty:block/tidal_stone` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:underworld_portal` | `dynasty:block/underworld_portal` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:underworld_stone` | `dynasty:block/underworld_stone` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |
| `dynasty:vitality_shrine` | `dynasty:block/crimson_pillar_side`<br>`dynasty:block/jade_block`<br>`dynasty:block/vitality_shrine` | v9 已交付。**保留**。保留当前资源。已有交付或有效引用；缺少逐项用户确认不能推断为未完成，不为凑数量重绘。 |

## PNG 尺寸、颜色与完成证据

下面是固定基线中实际引用的 PNG。颜色数为所有可见像素的不同 RGB 数；原版动画条带按整张 PNG 统计，不误报为高清方块。

| PNG 路径 | 尺寸 / 可见 RGB 色数 | 动画 / 透明 / v9 证据 |
|---|---|---|
| `src/main/resources/assets/dynasty/textures/block/altar.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/bronze_block.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/celestial_stone.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/chime_bell.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/cloud_portal.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/cloud_stone.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/crimson_pillar_side.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/crimson_pillar_top.png` | 16×16 / 6 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/deepslate_jade_ore.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/dragon_crystal_ore.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/dragon_gate.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/dragon_throne.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/essence_condenser.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/imperial_lantern.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/incense_burner.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/jade_block.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/jade_mending_forge.png` | 16×16 / 6 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/jade_ore.png` | 16×16 / 10 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/jade_portal.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/jade_soil.png` | 16×16 / 6 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/marble_block.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/marrow_vat.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/palace_bricks.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/pearl_sand.png` | 16×16 / 6 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/plaque.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/ritual_altar.png` | 16×16 / 10 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/screen.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/spirit_soil.png` | 16×16 / 6 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/star_soil.png` | 16×16 / 6 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/taiko_drum.png` | 16×16 / 9 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/tidal_stone.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/underworld_portal.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/underworld_stone.png` | 16×16 / 8 色 | 不透明；静态；v9 SHA-256 一致 |
| `src/main/resources/assets/dynasty/textures/block/vitality_shrine.png` | 16×16 / 7 色 | 不透明；静态；v9 SHA-256 一致 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/amethyst_block.png` | 16×16 / 7 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/bookshelf.png` | 16×16 / 29 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/brown_mushroom_block.png` | 16×16 / 4 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/brown_terracotta.png` | 16×16 / 47 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/chiseled_stone_bricks.png` | 16×16 / 7 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/coal_block.png` | 16×16 / 5 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/daylight_detector_top.png` | 16×16 / 9 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/gilded_blackstone.png` | 16×16 / 10 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/glowstone.png` | 16×16 / 8 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/gold_block.png` | 16×16 / 9 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/lodestone_side.png` | 16×16 / 8 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/lodestone_top.png` | 16×16 / 5 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/magma.png` | 16×48 / 10 色 | 不透明；原版动画，帧 16×16，网格 3 帧；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/polished_deepslate.png` | 16×16 / 7 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/prismarine_bricks.png` | 16×16 / 8 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/redstone_lamp.png` | 16×16 / 8 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/redstone_lamp_on.png` | 16×16 / 6 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/sea_lantern.png` | 16×80 / 717 色 | 不透明；原版动画，帧 16×16，网格 5 帧；原版依赖，不属于 v9 重绘清单 |
| `minecraft 1.20.1 client-extra.jar!/assets/minecraft/textures/block/shroomlight.png` | 16×16 / 8 色 | 不透明；静态；原版依赖，不属于 v9 重绘清单 |

## 引用核对与例外

- 45 个 blockstates ID 全部在 `DynastyBlocks.java` 或 `puzzle/PuzzleBlocks.java` 找到注册；父模型、面纹理与 `#变量` 已递归解析。
- `crimson_pillar` 使用端面/侧面与横柱模型；`ruin_shell` 继承 `dynasty:block/palace_bricks`，无需新增 PNG。
- `star_dial` 方块的物品 ID 是 **`puzzle_star_dial`**。同名 `models/item/star_dial.json` 属于饰品，不能作为方块物品引用。`before/` 未包含别名物品模型，本清单只读 `src/main/resources/assets/dynasty/models/item/puzzle_star_dial.json`，其 parent 为 `dynasty:block/star_dial`。
- `ruin_controller` 没有注册 BlockItem；磁盘有同名 item 模型不代表存在同名可获得物品。
- 原版父模型、PNG 与 `.mcmeta` 只读项目构建使用的 Minecraft 1.20.1 `client-extra.jar`；未复制其素材、未打开游戏实例或存档。当前实例的资源包覆盖不在本清单范围。
- 解析模型（含父链与物品）102 个；缺失模型/PNG 或无法解析的纹理变量 0 个。注册/状态差异：0。本清单未发现必须修正的引用。原版 cube/cube_all/cube_column 父模板的空纹理槽由具体子模型赋值，已单独记录，不误报为缺失。

## 依据

- `docs/开发约定.md`
- `docs/art/STYLE-CONTRACT.md`
- `docs/art/vanilla-v9/release-notes.md`、`manifest.json`
- `docs/art/vanilla-v8-references/README.md`、`vanilla-materials-v7/release-notes.md`（仅作历史，不能覆盖 v9 事实）
- `docs/content/ruin-puzzles-v1.md`、`ruin-puzzles-natural-v2.md`、`bounty-board-v1.md`
- `src/main/java/com/dynasty/DynastyBlocks.java`、`src/main/java/com/dynasty/puzzle/PuzzleBlocks.java`
