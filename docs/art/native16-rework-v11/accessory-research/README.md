# 饰品只读审计与 40 件实图参考

本目录是研究材料，不是接入资源。所有现有 `src`、模型、Java、注册、实例、存档均未修改。读取本机真实模组 JAR 中 40 个不同物品贴图，来自 **愚者 / The Fool 0.2.2**（Goety 2.5.36.1）与 **登神者：天阶咏叹 v1.5**（Artifacts 9.5.16、Relics 0.8.0.13）。这里的 40 件**不计入 500 个方块参考数量**。未下载其他作者素材；未将参考贴图重新着色当成原创。

## 原始记录与保护边界

已读 `docs/art/STYLE-CONTRACT.md`、`journey-polish-v4/DELIVERY.md`、`journey-polish-v4/assets.json`、`accessory-refining-v3/DELIVERY.md`、`school-accessories-v2/DELIVERY.md`，并核对实际 PNG、模型、注册代码、Curios 标签和美术记录。

风格约定明确保护已认可的万钧戒、灵文佩（实际语言键名：灵纹佩）、金乌箭囊。v4 交付记录仍说明其是独立资源包试样，不能将 `src` 中同名旧图的尺寸当成认可样张。展示架也不在本轮饰品范围。龙骨戒存在 v7 完成记录；山岳镯存在 v2 完成记录；凤凰指环和明月佩为 128×128 美术，未列入本轮三件优先候选。

## 三件适合独立候选的现有 ID

| ID | 现有贴图与尺寸 | 模型/插槽 | 当前证据与建议 |
|---|---|---|---|
| `dynasty:bronze_mirror` 铜镜 | `src/main/resources/assets/dynasty/textures/item/bronze_mirror.png`，32×32，10种RGBA含透明 | `models/item/bronze_mirror.json` → `item/generated` / `dynasty:item/bronze_mirror`；charm | 现图同心圆+八向小点，旧生成器 `gen_items_more_craft.py:73–84` 对应。重画成铜框、克制镜面与小型镜钮，保持圆镜的读法。 |
| `dynasty:jade_pendant` 玉佩 | `src/main/resources/assets/dynasty/textures/item/jade_pendant.png`，32×32，9种RGBA含透明 | `models/item/jade_pendant.json` → `item/generated` / `dynasty:item/jade_pendant`；necklace | 现图是直绳和圆盘同心环，所谓孔洞实际不透明，旧生成器 `gen_items_trinkets.py:17–25` 对应。重画为有系绳与透空小孔的垂玉，使它与圆镜剪影不同。 |
| `dynasty:storm_charm` 雷纹护符 | `src/main/resources/assets/dynasty/textures/item/storm_charm.png`，32×32，6种RGBA含透明 | `models/item/storm_charm.json` → `item/generated` / `dynasty:item/storm_charm`；charm | 现图多层规则矩形与王字形笔划，`gen_dynasty3.py:522` 使用通用 `tablet` 形。候选改为窄长符体、顶端系结和少量成簇折线雷纹。 |

三件均为二值 alpha（0/255）。在既有专属美术完成记录中未找到三件，不能由此推定用户从未认可，因此只建议独立候选，不擅自覆盖。全部可原生 16×16 设计；没有采用 32×32 的必要。

真实用途：铜镜每600 tick净化一个负面效果；玉佩额外8%减伤；雷纹护符常驻抗性I、**下雨或雷雨**额外力量II与速度I。依据 `DynastyTrinkets.java:800 / :695 / :927`，没有修改功能。铜镜的 `DynastyItemUsage` 旧文案仍写装饰/礼物，但不以该旧文案取代当前实际代码。

## 实际看过的 40 件参考所得

- Goety 的吊坠、戒指和 Artifacts 的项链普遍将 16×16 中最可读的面积留给轮廓和一颗主体宝石。孔洞是真透明；轮廓不是处处等厚的黑边。许多图只用5–15种可见颜色。
- 镜面、骨、铜、玉用相邻色簇定体积。高亮常是1–3像素连续短段，并不遍布四周。为新铜镜选择不对称的少量高亮，避免当前完整同心亮圈。
- 1×时，Goety戒指以斜向环孔和偏置宝石读出“戒指”；Artifacts的吊坠以宽链+下方重心读出“项链”。不能把三件新饰品都变成一种圆盘。
- Artifacts 的 shock_pendant / thorn_pendant 使用相似链形但不同核心形状；可借鉴“结构明确+一点强调色”的组织规律，不复制链条像素或其专属图案。
- Relics 的若干图同样原生16像素，但第一帧就有22–105种可见RGBA色，体积高光更密。它们适合研究动态重点、环孔和剪影，却不作为本轮 Vanilla 普通饰品的色阶密度目标。
- 40件全部二值alpha；可见颜色中位数11。新增候选应保持0/255透明、整像素边缘、约8–12主要色。不给整件外缘添加半透明光晕。
- Relics 的10件有动画条带，仅取其已创作的首个16×16帧进行静态轮廓比较；未将每个动画帧算作一个物品。动画本身不构成“真实发光”证据。

## 文件与验证

- `reference-contact-1.png`、`reference-contact-2.png`：40件逐件原尺寸和最近邻6×对照，已实际查看。
- `reference-native-1x.png`：全部40件1×检查，已实际查看。
- `current-candidates.png`：现有三件及备用汲生戒原尺寸/最近邻放大，已实际查看。汲生戒未列入优先三件。
- `reference-sources.json`：逐件 JAR 来源、包名、SHA-256、内部路径、尺寸、动画元数据、模型定义与颜色/透明统计。
- `candidate-audit.json`：三件 Dynasty 原始哈希、模型关系、真实用途、完成记录与建议。
- `inspect_accessories.py`：只读 JAR 研究/联系表脚本；第三方原始16像素帧留在项目 `work/native16-v11/accessories/`，不会被加入候选资源包。

上述来源是各整合包内含模组的资产，并不声称已经解析该实例启用的资源包覆盖顺序，更不声称游戏内实测。未启动客户端。
