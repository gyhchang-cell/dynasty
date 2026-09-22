# 三件文房物品 · 生成与装配记录

本轮使用内置 imagegen，每个物品单独生成，实际透明 PNG 原稿在 `sources/`。不是让 DeepSeek 画图，不使用代码拼接仿制插画。

共用规格：单个 Minecraft 物品图标；透明背景；精致但清晰的像素簇与阶梯状轮廓；主体尽量占满画布但不能裁断；无场景、无水印、无外部投影、无说明文字。

## exam_paper / 科举试卷

Chinese imperial examination scroll 科举试卷. Rolled ivory paper at top and bottom with a slightly unfurled broad cream page, several short ink marks as calligraphy, one small vermilion official seal and dark-red tie, subtle antique gold end caps. Crisp polished pixel-art clusters, limited cream/gold/vermilion palette, readable silhouette at inventory scale, not photorealistic. Front three-quarter view filling 90–94% of square canvas height and 75% width, centered. Genuinely transparent background, clean alpha edges. One self-contained sprite, not a spritesheet; avoid noisy tiny marks and blurred glow.

## ink_stick / 徽墨

Premium Chinese Huizhou ink stick 徽墨, a thick short ebony-black octagonal ink cake shown diagonal bottom-left to top-right in a shallow three-quarter view, elegant raised antique gold curling dragon and cloud motif on its wide face, bevel edge in cool charcoal blue, two gold end borders. Clear broad silhouette, strong gold-versus-black contrast, black face remains visible. Refined pixel-art with crisp clusters and restrained highlights. Single object nearly fills square icon (92% extent) without clipping. Must read as a solid ink block, different from a scroll or coin. No brush, paper, box or scene.

## bamboo_slip / 竹简

Chinese bamboo manuscript 竹简, partially unrolled broad fan of seven warm honey-green bamboo slips connected by two dark brown silk cords, right edge curling back as a compact roll to show dimension. Sparse short dark ink markings on each slat; one tiny jade cord fastening at bottom, no large dangling decoration. Crisp pixel art with confident stepped outlines, legible at small scale, honey gold and moss green palette, shaded bevel edges, distinct silhouette. Object occupies 92% of canvas without clipping. Clearly bamboo writing tablets, not a book, paper scroll or coin.

## 游戏贴图装配

沿用 `tools/art/PackRemasterAssets.java item`：裁透明边、等比缩放到最长边 120 像素，居中装配为 128×128 RGBA；不改变图像主体设计。`before/` 保存旧图，`after/` 是最终接入图。

在项目根目录对每个名字执行，例如：

```sh
java tools/art/PackRemasterAssets.java item docs/art/architecture-remaster-v3/items/sources/exam_paper.png src/main/resources/assets/dynasty/textures/item/exam_paper.png
```

三件均保留原注册名、物品模型与功能。新贴图最长边均为 120/128；试卷 106×120，徽墨 120×120，竹简 120×103。
