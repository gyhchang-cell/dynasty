# 2026-09-23：杀怪成长与图鉴改版

## 本轮实现

- `DynastyTooltips` 从 `DynastyBalance` 读取每件减伤/生命，加在原版韧性行后。盔甲不再重复展示套装与用途；饰品去掉“常驻”，专属流派增伤以短蓝字显示。
- `DynastySchoolProgression` 只在敌对生物死亡时奖励熟练度。同一实体结算一次；旧玩家阶数与进度保留。现有招式保留，但不是升级或初战任务的门槛。
- `DynastyWeaponProgression` 的物品 NBT 保存等级、历练与路线。射箭时保存兵器快照与 UUID，击杀奖励回到实际发射的弓，避免换手把经验给错兵器。
- `gen_growth_book.py` 生成 12 个原版 smithing_transform 配方；锻造继承原物品 NBT，包括等级、历练、名称与附魔。原来的工作台配方仍可用，但不继承旧物品 NBT。
- `quest_growth.py` 在保留旧 ID/奖励的前提下重写流派说明，并添加 24 个进化材料/成品节点。`quest_atlas.py` 不再输出任何 backdrop 装饰图，仅保留真实前置连线、标题与可点击导航。
- 原 Dynasty 引导书通过可选反射桥打开 `dynasty:imperial_codex` Patchouli 书。8 个分类，439 个条目；装备套装规则移入书中。未安装 Patchouli 时保留原界面回退。
- 新增 Patchouli、Equipment Compare、Lootr；固定 Forge 1.20.1 版本及 SHA-512，登记于 `qol_mods.json`。Equipment Compare 在 Modrinth 导出标为仅客户端。

## 生成与验证

```sh
python3 tools/art/gen_schools.py
python3 tools/art/gen_growth_book.py
python3 tools/art/gen_ftbquests.py
python3 -m unittest discover -s tools/art -p test_quest_story.py
python3 -m unittest discover -s tools/art -p test_schools.py
./gradlew runGameTestServer build --offline
python3 tools/art/make_modpack.py
python3 tools/art/verify_modpack.py modpack/mods
```

本轮结果：54 项服务器 GameTest、29 项任务回归、6 项流派资源测试、26 项源代码契约检查通过。装备/Curios/语言/任务前置和模组依赖检查通过。

实际客户端 QA：`tools/art/book-qa/book-qa.init.gradle`，在 `build/book-qa/client` 内创建全新的平坦测试世界，不接触玩家存档。成功打开原生 Patchouli 书、8 分类/439 条目、成长与进化页；实际装备悬浮确认韧性后紧跟蓝字减伤和生命、无重复，全部饰品无“常驻”。截图在本目录。三模组整合包仅做依赖校验，尚未在全部第三方模组同时启用时做完整游玩回归。

## 部署

已核对最新游戏日志的 `--gameDir`，仅更新 `/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝`：本体 jar、3 个新模组、生成的 FTB 任务配置。jar 文件数 78 → 81；Forge UI 总模组数还包含嵌套模块，需重启后查看。

备份与逐文件 SHA-256 收据：`build/deployment-backups/growth-20260923-211655/receipt.json`。未改存档、玩家任务进度、启动器账户或按键设置。源码、整合包和该实例的本体 jar SHA-256 一致。

回退时先退出游戏；按收据恢复有 `before` 的文件，将本次新安装的三个 jar 移至备份目录即可。不要删除整合包目录，也不要用全目录覆盖玩家存档。
