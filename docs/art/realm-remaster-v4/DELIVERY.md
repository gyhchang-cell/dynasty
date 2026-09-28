# 山河与百炼 · 2026-09-24

## 当前交付状态

源码、资源、任务和项目内整合包已更新并构建通过。
产物：`build/libs/dynasty-1.4.0.jar`，已同步 `modpack/mods/dynasty-1.4.0.jar`。
实际实例 `/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝` 仍在运行，
部署保护已中止安装；本轮没有修改实例里的模组或用户存档。

游戏完全退出后，运行 `python3 tools/art/deploy_growth_update.py`。
脚本验证当前实例、备份被替换文件、校验 SHA256，只替换模组和任务配置，不触碰 saves/options。
备份及逐文件回执在 `build/deployment-backups/growth-<时间>`。

## 内容

- 修正 hallBody 高度参数误用、天空建筑重复叠加世界高度，以及局部特征越界导致的半栋建筑；整栋写入前检查范围。
- 统一楼梯坡向与净空，打开平台栏杆出口；九霄星坛从 26×26 扩至 42×42，增加藏书廊、水庭、钟亭及工作台设施。
- 降低建筑密度，皇宫、书院、关隘可在主世界指定群系生成。
- 新增 8 个原创地表/岩层方块，四个维度的基础石头和表土使用本模组方块；保留基岩、原有地形起伏算法及其他生成装饰，不宣称整个世界生成器已重写。
- 修正 Traveler's Titles 的维度翻译键；统一自然指南针、探险者指南针名称。实际 PinIn 匹配器验证全拼/首字母搜索。
- 饰品每条属性单独一行；流派加成饰品移至独立区域，无主路线前置连线。
- 新增北辰破阵枪、承影剑、风翎弓、雷符杖：被动机制、8 条保留 NBT 的进化配方、任务和书中配方均接入。
- 13 件兵器图像（9 件旧图重制、4 件新增）及 12 张拉弓帧；保留先前已重制的流派精品素材。弓左右手模型方向有数学回归测试。
- 6 张新角色纹理；Boss/精英加入塔盾、翼刃、悬浮面具、魂袍、分节龙尾/鱼尾等轮廓。常规士兵仍为人形，不宣称全部实体都已重新雕塑。

## 验证

- `./gradlew runGameTestServer --offline`：59/59，包括四维度实际区块地层、楼梯/建筑、被动武器与进化 NBT。
- `./gradlew --offline -I tools/art/runtime-qa/runtime-qa.init.gradle runClient`：100 张真实 Minecraft 离屏模型帧；资源重载/VBO 重建通过，无 GL 错误。
- 隔离 book-qa 客户端：熊掌生命和攻击分行、书中进化页通过。
- `test_realm_art.py`：39 个独立资源的来源、尺寸、颜色类型及四把弓双手指向通过。
- `test_quest_story.py`：29 项通过；613 任务、35 章节，488 个已发布任务身份保留，无前置环。
- worldgen、feature_order、entities、lang、curios、keju、schools、ftbquests、modpack 依赖检查通过。
- `./gradlew build --offline`、`git diff --check` 通过。

## 存档兼容边界

建筑及地层生成只影响新生成的区块。旧区块中已经存在的高柱、半栋建筑不自动拆除或重建。
旧星坛保留原有存储边界，不向相邻区块强行扩建。
无须删除任务进度或重建世界。

效果页 `gallery.html` 的建筑/角色图来自真实客户端离屏渲染，不是世界内截图；地块图为贴图平铺预览。
原创图像生成记录见 `assets.json`、`weapons.json`、`skins.json`，由内置图像生成工具制作，再机械缩放/映射至现有 UV。
