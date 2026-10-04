# 王朝剩余贴图 v15 · 评审版

打开 `review.html` 查看 340 件物品的原稿、原尺寸新稿与最近邻放大对比，以及 23 套盔甲的穿戴 UV 预览和告示板的 3×3 铺贴。

本轮完成：339 件经资源清单确认仍待制作的物品，另对已认可方向的玄铁胸甲精修；23 套盔甲共 92 张物品栏图标及 46 张标准 64×32 穿戴贴图；原先临时复用书架纹理的告示板 5 张原生 16×16 面贴图。独立资源包含 391 张 PNG 和 29 个必要模型贴图引用 JSON，其中 28 个随新武器轮廓重建手持边缘，另一个是告示板六面引用。所有物品图标沿用现有资源规范，以原生 32×32 整数像素直接绘制；盔甲穿戴贴图保持标准 UV，不把图标直接用作穿戴贴图。

其他任务有完成记录的 130 张物品、34 张方块贴图保持原样。`zhuque_fan`、`juling_axe`、`bawang_spear` 的来源仍不确定，保留原稿。先前本对话制作的铜镜、玉佩、雷纹护符与方块样稿没有重画。并行的龙口、召唤祭坛、真元资源、模型和代码未写入此候选资源包。

## 文件

- `review.html`：全部前后对比、原尺寸、新稿放大、盔甲穿戴预览、告示板 3×3 铺贴。
- `Dynasty-v15-candidate-resource-pack.zip`：Minecraft 1.20.1 的独立候选资源包，仅包含本轮新资源与引用；在王朝模组上方启用可供玩家自行评审。
- `resource-inventory.csv`：476 张原有物品贴图、方块纹理的分类与证据。
- `delivery-manifest.json`、`verification.json`、`resource-references.json`：逐文件路径、SHA256、模型引用和静态验证。
- `source-backup/`：本轮所涉及原资源的逐文件备份。
- `items-core/`、`items-equipment/`、`items-accessories/`、`armor-a/`、`armor-b/`、`blocks-bounty/`：各批候选的生成记录与细分预览。

检查通过：340 个目标 ID 与清单完全对应，391 张 PNG 尺寸和透明通道正确，没有重复候选图；340 个物品模型与告示板模型的纹理都能解析；28 个更新的手持模型与新透明轮廓逐边吻合。原有 476 张物品源图保持原哈希；已确认的 130 件旧成品和 34 张方块图保持原哈希。其他并行任务在其目录的修改被保留，不做回滚。

状态：**391 张 PNG 与 29 个资源 JSON 已接入项目 `src/main/resources`，`./gradlew --offline build` 成功，新 `build/libs/dynasty-1.4.0.jar` 内 420/420 个资源哈希匹配。项目 `modpack/mods/dynasty-1.4.0.jar` 已备份并更新，420/420 个资源哈希一致；尚未同步游戏实例或游戏内实测。** 所有本轮贴图均为静态颜色，没有 `.mcmeta` 动画，也没有真实发光渲染。离线穿戴图遵循现有几何与 UV，但不能替代游戏内最终观感检查。

接入回执：`source-install-receipt.json`；本轮覆盖前备份：`deployment-backup/`。
项目发布 JAR 回执：`modpack-install-receipt.json`。
