# 罗盘中的王朝地点汉化

## 原因与修复

直接检查已安装版本 `ExplorersCompass-1.20.1-1.4.0-forge.jar` 的
`StructureUtils.getPrettyStructureName`：它用 `Util.makeDescriptionId("structure", id)`
查找语言词条；查不到时自动把注册名改成首字母大写英文，例如 `Palace`、`Academy`。
之前只有物品、维度和群系译名，缺少全部六个 `structure.dynasty.*`，因此不是找不到建筑，
而是找到后没有中文名。

| 建筑注册名 | 罗盘显示名 |
| --- | --- |
| `dynasty:palace` | 皇家宫殿 |
| `dynasty:academy` | 国子监 |
| `dynasty:imperial_tomb` | 帝陵 |
| `dynasty:great_wall_gate` | 长城关隘 |
| `dynasty:star_altar` | 九霄星坛 |
| `dynasty:stone_grove` | 幽冥石林 |

六个建筑分组与建筑使用相同注册名，亦使用相同中文名。罗盘列表、搜索结果与定位提示
共用上游方法，不需要篡改其 JAR 或增加强制依赖。

一并将已有十个群系、四个维度的中英名字纳入同一张受验证的表；原有名字保持不变。
自然罗盘的 `BiomeUtils.getBiomeName` 与两个罗盘的 `getDimensionName` 查词规则也已检查。

## 维护与验证

源表：`tools/art/gen_dynasty3_json.py` 的 `WORLDGEN_NAMES`。
单独刷新地点语言，不触碰贴图、模型、配方：

```sh
python3 -c 'import sys; sys.path.insert(0, "tools/art"); from gen_dynasty3_json import merge_worldgen_lang; merge_worldgen_lang()'
python3 tools/art/verify_compass_localization.py
python3 tools/art/test_compass_localization.py
```

验证会读取实际两个罗盘 JAR 的反编译结果；检查所有 `structure` / `structure_set` /
`biome` / `dimension` 注册文件的名字，中文未翻译、漏名字或新增结构忘记写源表都会失败。
常规 `verify_lang.py` 也已接入地点覆盖检查。

客户端须选简体中文，并保持探索者罗盘的 `translateStructureNames = true`（上游默认即为 true）。
这里只核验了资源和上游读取逻辑；须更新实际实例中的王朝 JAR、重启后再确认列表显示。
帝陵译名不代表固定 Boss 刷新点，不更改建筑生成或 Boss 生成规则。
