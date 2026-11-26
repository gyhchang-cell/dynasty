# 五套旧护腿显示胸纹的静态证据

在默认 Forge 1.20.1 / 47.4.10 路径下，护腿渲染单独读取 LEGS 槽的物品。匹配护腿的装备槽后，它启用内层模型的躯干与双腿，从对应材质取第 2 层贴图。胸槽为空不妨碍这条分支绘制。实证路径为 `HumanoidArmorLayer.java` 的 43–68、81–97、129–135、161–172 行。躯干前面由 `HumanoidModel.java` 第 64 行的 8×12×4 方块定义。

五套现有第 2 层的躯干正面 `[20,20,28,32)` 均有 96/96 全不透明像素。旧生成器把第 1 层胸纹和第 2 层胸纹都画在 `[21,23,27,29)`。五套该区域各有 36 像素与自身第 1 层逐 RGBA 相同，且全部不透明。其上部 `[21,23,27,27)` 有 24 像素超过此前核定的腰部边界。配对比较和生成器证据一起确认，护腿层确实携带胸纹，结论不依赖宽衣或内衬的视觉猜测。

| 护腿 ID | 第 2 层相对路径 |
|---|---|
| `dynasty:bronze_leggings` | `textures/models/armor/bronze_layer_2.png` |
| `dynasty:general_leggings` | `textures/models/armor/general_layer_2.png` |
| `dynasty:jade_leggings` | `textures/models/armor/jade_layer_2.png` |
| `dynasty:sky_leggings` | `textures/models/armor/sky_layer_2.png` |
| `dynasty:xuantian_leggings` | `textures/models/armor/xuantian_layer_2.png` |

坐标使用从左上起算的半开区间。坐标证据 JSON 保存了 10 张项目图集、物品注册与默认渲染源码的 SHA-256。对照页展示原图裁片及整数放大。

后续修复不能只清上半胸纹。胸纹的最后两行落在候选腰区 `[21,27,27,29)`，也要检查是否还保留了原胸纹形状。实机应分别单穿护腿、单穿胸甲和穿整套，确认胸纹只随胸甲出现、腰带只在护腿槽保留原有腰部身份，以及侧背过渡。当前仅验默认静态路径。资源包覆盖和实际画面仍待验证。制作门槛未通过。
