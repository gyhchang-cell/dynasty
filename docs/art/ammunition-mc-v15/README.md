# 遗漏物品补齐：5种弹药与生物罗盘

2026-10-18，继续用户授权重做现有差贴图，保护精致旧图。复查v14保留范围后发现5种弹药均借用minecraft:item/arrow，生物罗盘借用minecraft:item/compass_16。读取ExpansionWeapons.SpecialArrow与CreatureCompass真实用途后，分别设计粗重钢矢、轻型连弩矢、细长破甲尖、绿色毒刃、叉形铜导雷头，以及爪印追踪罗盘。只更换这6件物品图标及其模型引用；没有修改箭实体、伤害、效果、射击、注册ID、配方或追踪界面。

内置image_gen逐件生成，提示为prompt-prefix.txt加selection.json的subject，参考../accessories-mc-v11/references/style-target.png；沿用该目录真实1000件物品研究记录。原PNG保存在sources与originals-6.zip。before含6个原模型及从Minecraft client.jar提取的实际旧图，选择文件记录原模型哈希，发布前确认目标未被并行修改。

已查看原稿总览、前后差异和32px库存尺寸预览，5种弹药用粗细/箭头/尾翼区分，保留生物罗盘已有追踪功能。运行只裁透明边并补2px；没有缩成16px、量化或有损压缩。this-round-6.png与comparison.png均非游戏截图。

构建、原生资源检查、JAR核对与导出同步结果以本目录后续日志和JSON为准。此次不启动客户端、不关闭既有游戏、不修改存档、声音亮度，不推送GitHub。未以美术完成替代任务清单内玩法/真人验收，相关提示词保留。

最终验证：build/reobfJar成功（27秒）；377件累计原稿源RGBA、模型、图集与发行JAR核对755项匹配，errors为空。Minecraft原生无窗口解码/挤出/UV/面染色检查377张、650726面通过。既有贴图本轮全部哈希保持不变。三个原有导出包内嵌本体与构建JAR一致，74个文件官方哈希及依赖检查通过，FTB内嵌8个、补装0。已同步11处本地游戏/导出文件，未启动图形游戏。完整日志及published/installed/validation JSON均在本目录。
