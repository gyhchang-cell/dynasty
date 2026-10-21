# 长城残影：独立远景旗影

运行资源为 `assets/dynasty/scenic/great_wall_echo_flags.json`。仅保留完整建筑的三组原旗杆、横杆、挂接线和静态旗布，共 92 个方块、290 个外露面。使用原有完整 11 项 palette，所有索引及原木轴向保持一致。

外露面由这 92 个方块重新求邻接生成，增加了完整建筑中被遮挡的三个旗杆底面和西旗底端的一个南面。没有筛选完整建筑的旧面表。

三个旗的原位置、朝向和尺寸保持一致。沿用完整模型的 `size=[64,24,32]`、`centerPivot=[32,0,16]`、`anchor=[34,0,1]`、`front=-Z` 和 `groundBlockY=0`。变换为 `world = groundCenter + rotation(local - [32,0,16])`。旗杆底端原来分别位于建筑平台的 Y6、Y15、Y7，远景也保留这些高度。不要单独居中旗帜、降到 Y0 或重新缩放。

## 生成与检查

在仓库根目录执行：

```sh
python3 tools/art/cod3/scenic_great_wall_echo.py
python3 tools/art/cod3/scenic_great_wall_echo.py --check
/Users/a15356015027/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/art/cod3/scenic_great_wall_echo.py --review
```

扩展后的默认命令仅导出远旗并检查；`--check` 写入本目录的 `checks.json`；`--review` 仅重建本目录的七张远旗预览和 `preview.json`，需 NumPy、Pillow 及本地原版材质 JAR。上述命令均不运行 Java、不写存档。

完整 NBT、完整 JSON、原有完整建筑预览及 `BUILDING_READY.json` 均冻结。旧 README 中的生成命令属于完整建筑历史交付。其原始脚本逐字归档为本目录 `full-building-source.py`，SHA256 与旧 `BUILDING_READY.json` 的脚本指纹一致；该历史文件不应作为当前生成入口。当前扩展脚本及独立资源指纹见上一级 `LOD_HANDOFF.json`。

## 验证范围

`checks.json` 共 54 项离线检查通过，包括完整建筑兼容性和十项远旗检查。七张最终预览均已实际查看：正面、背面、斜视、底面、灰模、黑色剪影和 80 米地面视角。预览直接使用远旗 JSON 的面及原版材质；保持完整建筑的世界取景框，没有给每面旗单独放大；没有雾、动画或音效。正背面中东旗接近侧视，是原有 +Z 旗布方向的正常结果。

这些是软件预览，尚未完成原生游戏验证。本交付仅完成远旗资产。运行时加载、远近切换、透明深度、裁剪、事件生命周期和原生验收由主线处理；保留现有任务清单。切换时应避免同时叠画完整建筑中的旗布与独立远旗。沿用完整建筑保守渲染边界可保持一致；独立旗影的支点相对顶点 AABB 为 `[-22,6,-10]` 至 `[23,23,10]`，运行时仍需应用同一旋转。

沿用本建筑已记录的 100 张参考图及原设计；本次只是同一建筑的几何子集，未新增建筑，也不重复计作新的一百张参考。
