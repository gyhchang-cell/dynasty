# 天子剑、青龙偃月刀：第一版专属特效

- 天子剑：渐显方形帝印、旋转双金龙、三层金色挥剑弧、命中敕令印记。
- 青龙偃月刀：肩后游龙、手边小盘龙、三层青色斩击与龙影、命中龙影及爪痕。
- 龙形由连续发光带构成，含龙角、龙须、发光眼睛、背鳍及爪；不是粒子圆圈，也不是实体生物。
- 常驻大造型在肩后，挥砍主体偏下。手边小龙是视角/手侧定位的视觉环绕，不绑定物品模型的骨骼。
- 新效果仅影响视觉，不增加伤害、推力、破坏方块或技能。龙渊剑保持无自定义粒子。
- 命中由服务端通知附近 48 格的客户端；只处理这两把武器的直接近战伤害。最多保留 32 个命中效果，每个 24 tick；最多渲染最近 12 名持有者。
- 换维度/退出清理缓存，隐身与旁观玩家不显示持有光环。网络版本更新为 3，联机服务端和客户端需使用相同版本。

## 验证

- 离线构建成功。
- 6 个 GameTest 全部通过：原有 4 个弓测试，新增武器白名单/不改变伤害、命中数据往返测试。
- 242 个几何动画采样通过有限值检查，单武器三个阶段合计最多 675 条线段。
- `preview.png` 从游戏使用的同一几何类导出，用于看形状与配色，并非游戏截图。尚未在游戏世界实测视角、联机观感或帧率。

## 预览重建

在仓库根目录执行：

```sh
mkdir -p build/imperial-preview
javac -d build/imperial-preview src/main/java/com/dynasty/client/ImperialWeaponGeometry.java tools/art/ImperialWeaponPreview.java
java -cp build/imperial-preview ImperialWeaponPreview docs/art/imperial-weapons-v1/preview.svg
magick -font /System/Library/Fonts/Supplemental/Arial.ttf -background none docs/art/imperial-weapons-v1/preview.svg docs/art/imperial-weapons-v1/preview.png
```
