# 帝兵特效第二版：立体鳞甲龙与剑印

本版针对第一版龙像圆环、命中方框粗糙的问题调整：

- 龙改为缓存的立体曲面模型，每条 2,750 个面；保留游戏像素世界适合的低多边形轮廓，但不再以粗光线表示龙身。
- S 形收腰龙身、凸起鳞甲、腹部节纹、四条分关节的腿与弯钩爪。
- 龙头有长吻、张开的上下颚、獠牙、发光眼、眉骨、鼻孔、分叉鹿角、鬃毛、长须与颔下须。
- 天子剑双龙分立两侧、向内护卫帝印，轻微摆动，不再头尾相接旋转成圆环。
- 右上角命中特效取消方框、“敕”字和八根短线，改为细长金色剑印、护手和两侧云纹。
- 青龙刀共用新的立体龙；金色与青玉色材质独立。挥砍节奏与伤害逻辑未改。
- 独立半透明曲面渲染，深度测试与由远及近排序；剑光保留发光效果。最多渲染附近 6 名持有者和 16 个命中效果，全局曲面上限 120,000。

## 检查

离线构建、6 个功能 GameTest 通过；242 个动画采样通过几何有限值检查。预览由当前游戏几何直接导出，不是游戏截图。尚未进游戏确认遮挡、光影兼容和帧率。

```sh
mkdir -p build/imperial-preview
javac -d build/imperial-preview src/main/java/com/dynasty/client/ImperialWeaponGeometry.java src/main/java/com/dynasty/client/ImperialDragonMesh.java tools/art/ImperialWeaponPreview.java
java -cp build/imperial-preview ImperialWeaponPreview docs/art/imperial-weapons-v2/preview.svg
magick -font /System/Library/Fonts/Supplemental/Arial.ttf -background none docs/art/imperial-weapons-v2/preview.svg docs/art/imperial-weapons-v2/preview.png
```
