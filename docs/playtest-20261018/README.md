# 2026-10-18 完整模组组合隔离实测

本次复用了现有 Dynasty 的 83 个模组，在独立临时目录创建测试世界并实际进入客户端。没有操作玩家存档或关闭玩家世界，测试客户端已经退出。这里记录的是本轮覆盖范围，不代表所有玩法全部通过。

## 修复

- 21 组同材料但不同产物的配方冲突：修改 28 个配方文件，为相撞配方补上可区分的材料。风翎弓的锻造材料改为天羽，避免与神臂弓被同一配方输入覆盖。具体前后材料见 recipe-fixes.json。
- 将四张已有实体贴图明确加入方块图集，修复引用它们的模型出现紫色缺失贴图；招魂符改用现有原始物品贴图加载器。没有重画图片。
- 补齐披鳞执金吾刷怪蛋及药水类型的漏译名称。
- 同步任务配方说明，迁移风翎弓对应的一个备料检测材料；保留其任务身份与奖励。
- 修正任务校验脚本误把 QA 辅助 jar 选成正式模组的问题。
- 更新可找到的对应配方生成器，避免再次生成时覆盖修复。狐尾符、踏云佩、凤羽符未找到独立配方生成条目，其 JSON 为本次修复源。

## 实际验证

- 原生 RecipeManager 读取 595 个王朝配方，检查材料是否有效。
- 544 个普通合成配方逐个填入原生合成容器，检查匹配、产物以及实际选中配方；锻造配方也检查实际选择的产物。最终未发现产物被其他配方覆盖。
- 扫描 816 个王朝物品的烘焙模型和显示名称，最终缺失物品模型、漏译名称均为 0。特殊实体渲染器不因缺省粒子贴图而误判。
- 完整模组组合中实际显示生命 27/36，保留 OverflowingBars 心形显示；实际打开天将令 JEI 来源页与生物罗盘界面。
- 57 项任务回归检查、2 项配方冲突回归检查通过；正式安装包任务校验通过。
- 14 个发布文件中，39 张已认可武器贴图的哈希全部保持一致。

证据：native/audit.txt、native/COMPLETE.txt、full-client.log、recipe-tests.txt、deployed-quest-check.txt、approved-textures-preserved.json。

截图：
- native/screenshots/full-pack-health.png
- native/screenshots/full-pack-sky-token.png
- native/screenshots/full-pack-creature-compass.png
- native/screenshots/item-and-block-fixtures.png

模型对照页中的两个“空气”条目是无对应物品注册的世界方块，不能据此判定世界方块缺图。没有把所有世界方块逐个放置验收。state.png 是早期测试辅助包缺元数据时的诊断截图，不是最终验收图；辅助包元数据已修正。

## 同步与未验项

已备份并更新 8 份模组 jar、6 份整合包导出文件、5 份现存启动器任务配置。仅窄范围写入本次资源和任务内容；部署记录见 deployment.json、extra-profile-sync.json 和 ../quests-journey-v3/launcher-sync-round19.json。玩家 options、声音、亮度和存档未改。测试辅助模组未发布。正式游戏需重启加载新文件。

当前任务书 20 章、1255 项；其中比上次多出的 2 项是并行 Cod2 工作，保留但不归入本轮新增成果。

仍有 AllTheLeaks 对 EMF 的适配类加载错误（IterationContext 类不存在），本次没有修改第三方 jar；该错误未阻止进入测试世界。未完成每个 Boss、所有结构导航、全部任务链和长时间生存流程验收，不能称为“所有东西无 bug”。
