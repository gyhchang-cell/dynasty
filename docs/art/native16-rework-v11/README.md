# Dynasty 原生 16×16 重绘 v11

基于当前项目文件和完成记录，对未满意的 v10 样张重做，并新增三件饰品候选。**4 个方块 ID + 3 个物品 ID，共 13 张 PNG、3 份必要引用 JSON；全部原生 16×16。** 当前状态：候选内部引用完整，尚未覆盖 `src`，没有同步到任何实例。

打开 [review.html](review.html) 查看原尺寸、最近邻放大、前后对比、3×3 铺贴、原版相邻效果与真实模型的离线 UV 预览。

## 参考依据

实际解析并逐页查看 **600 个真实方块 ID 的代表面**，全局 ID 和像素哈希均去重：原版 80、愚者 198、乌托邦探险之旅 170、登神者 31、锻造之旅 91、涟漪之篇 30。包含原版及 28 个模组命名空间。每个样本能追溯到本机 JAR、blockstate、模型父链、实际面绑定、PNG 和 SHA-256。

排除同图复用的形状变体、蜡化别名和染色家族；不把动画帧或同一方块的多面计成多个方块。另研究愚者和登神者中的 **40 件饰品**，不算入上述 600。整合包是安装来源，素材作者是相应模组；没有声称整合包内所有风格都适合 Dynasty，也未解析实例资源包覆盖顺序。

- [600 个方块参考图册](research/reference-gallery.html) / [完整来源](research/reference-600-audit.json) / [观察记录](research/README.md)
- [40 件饰品研究](accessory-research/README.md) / [来源](accessory-research/reference-sources.json)

参考只用于理解材质、色块、轮廓与密度。新图由 `build_art.py` 中的 16×16 字符网格和整像素色簇独立绘制；没有读入参考图重绘、换色、缩小、锐化或马赛克处理。研究联系表含他人图像，仅供本次本地对照，不是 Dynasty 原创资源；可用资源 ZIP 内没有第三方参考图。

## 完成对象与证据

ID 均带 `dynasty:` 前缀。下表中的纹理路径相对 `src/main/resources/assets/dynasty/`；候选对应路径在 `candidate/assets/dynasty/`。原件备份与 SHA 见 [baseline-resources.json](baseline-resources.json)，所有候选的精确目标路径见 [candidate-manifest.json](candidate-manifest.json)。

| ID | 当前源纹理 / 尺寸 | 现有记录与重做依据 | v11 处理 |
|---|---|---|---|
| `marble_block` | `textures/block/marble_block.png`，16×16 | v9 已交付；现图灰白碎斑密集；v10 样张未获认可 | 6 色浅灰白石，低对比短层理和成簇晶面，减弱重复斜纹 |
| `jade_ore` | `textures/block/jade_ore.png`，16×16 | v9 已交付；原矿物亮点分散，v10 大矿簇偏像嵌宝石 | 10 色，连续石底上 5 组不规则矿簇，尺寸和间距有变化 |
| `dragon_crystal_ore` | `textures/block/dragon_crystal_ore.png`，16×16 | v9 已交付；原图矿物小且暗；v10 规则大颗粒 | 9 色，4 组紫晶碎面，改变方向和长度，收窄高亮 |
| `jade_mending_forge` | `textures/block/jade_mending_forge.png`，16×16 | v9 已交付且已有 3 长方体模型；同图贴各面、lit 共用外观 | 区分作业顶面、前指示槽、侧面、底面；顶面和正面各有激活版本，4–9 色 |
| `bronze_mirror` | `textures/item/bronze_mirror.png`，32×32 | 老生成器同心圆盘；未找到专属完成记录，认可状态不确定 | 16×16，10 色，铜框与灰绿镜面、短镜钮；独立候选 |
| `jade_pendant` | `textures/item/jade_pendant.png`，32×32 | 老生成器绳加圆盘，孔洞原为实色；未找到专属完成记录 | 16×16，9 色，垂玉剪影、红系绳、真实透明孔；独立候选 |
| `storm_charm` | `textures/item/storm_charm.png`，32×32 | 通用 tablet 矩形和王字形笔划；未找到专属完成记录 | 16×16，8 色，窄符体、系结、成簇雷纹与少量朱色；独立候选 |

v9 是已交付资源，不能称为“未做占位”。本轮是经用户要求再次改善风格。三个饰品保留原图；没有因缺少确认记录就推定用户从未认可。

## 精确引用与状态

- 汉白玉、玉矿、龙晶矿：沿用已有 blockstate → cube_all 方块模型 → 同名纹理；方块物品继续继承方块模型，不需要新增注册或引用文件。
- 修补炉：候选 `models/block/jade_mending_forge.json` 只改纹理表与面引用。3 个元素坐标、默认 UV、父级等字段与备份完全一致。北为正面；南、东、西为侧面；down 为底面；仅最上台面 up 使用工作面，底座与中柱 up 仍用底材。
- 新增 `models/block/jade_mending_forge_active.json` 继承待机模型，只覆盖 `front`、`top` 两个纹理键。候选 blockstate 保留 4 朝向 × lit 两状态的 8 分支，只将 lit=true 指向 active。物品仍用待机模型。
- 饰品：已有 `models/item/<id>.json` 均为 `item/generated`，`layer0="dynasty:item/<id>"`。只替换同路径 PNG 即可，无模型或 Curios 配置改动。
- **关联材质**：`herbal_basin` 现有模型共用 `marble_block`。若启用候选包，其白石部分会同时改变；玉边、孔洞、几何与行为保持现状，已附离线对比。
- 全部静态，无新增 `.mcmeta`。激活态只改正面 6 像素、顶面 4 像素。现有代码 lit 的 40 tick 与方块光等级 10 未改；亮色不是自发光渲染已验证的证据。

## 检查与范围

[verification.json](verification.json)：13 张 PNG 全为 16×16；方块不透明，饰品仅 0/255 alpha 且四边至少留 1 像素；4–10 个可见颜色；所有具体模型/纹理引用解析通过；修补炉几何和 UV 一致、8 状态正确。备份的 12 个原文件与当前源文件哈希一致。参考原图与候选无完全相同像素哈希；这只是机械检查，不是原创性证明。

[scope-verification.json](scope-verification.json)：启动时记录的 5063 个既有文件复核，5062 个哈希未变（含原已修改的 JAR）。收尾时公共代码 `DynastyContent.java` 出现另一操作新增的镇渊祭仪与实体注册；另有 ritual Java 目录与掉落表新文件。本任务只读观察，未写入、回退或覆盖。既有贴图与模型基线未变。原资源清单保留在 [source-inventory](source-inventory/README.md)：45 个既有方块 ID、34 张 Dynasty PNG、19 张原版依赖；不冒充已审计另一任务刚新增的内容。

已检查 1×、最近邻放大、3×3 铺贴、原版石砖相邻与修补炉六面离线投影。**未启动游戏，尚未游戏内实测**；离线模型图不验证实际光照、碰撞或交互。

已认可宫砖、万钧戒、灵纹佩、金乌箭囊、展示架及其他成品保留；未重画盔甲。新祭坛缺少最终 ID/UV/尺寸，本轮未制作或注册。其余建筑材料保留在清单中，未在本轮批量替换。

## 文件使用

`dynasty-native16-v11-REVIEW-ONLY.zip` 是可选资源包，需项目已有 Dynasty 模组提供 ID、几何父模型与物品定义；兼容项目 Minecraft 1.20.1 的资源包格式 15。包中只有 Dynasty 候选资源和 pack.mcmeta，共 17 个文件。此任务没有自动安装资源包或复制到实例。

项目内复现：依次运行本目录 `build_art.py`、`qa/render_forge.py`、`preview_art.py`、`verify_candidates.py`；脚本依赖本机项目、Minecraft 构建缓存与 Pillow，离开项目的导出副本不作为独立构建环境。参考审计脚本另外依赖本机整合包 JAR。
