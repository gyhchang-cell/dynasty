# 本轮构建与部署

2026-09-21：离线 build 成功。26 项独立 Forge GameTest 全过，45 帧真实客户端离屏渲染通过；5 项罗盘汉化测试、18 项任务回归、世界生成/特征顺序/战利品引用检查通过。未打开用户存档。

已更新两处，SHA-256 均为：

`fa7efcef4c4c24f1e205052f9c7a4008054f714a2cbdd368d6a91cc8546a573e`

- `/Users/a15356015027/Desktop/dynasty/modpack/mods/dynasty-1.4.0.jar`
- `/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/mods/dynasty-1.4.0.jar`

实例根据本次 20:59 启动日志和实际目录核实，非此前废纸篓里的旧实例。其探索罗盘 `translateStructureNames = true`，第二章任务文件与项目当前版本逐字一致，所以没有重复覆盖任务配置。两个原版罗盘模组未改动。

旧项目包和旧实例包备份目录：`/Users/a15356015027/Desktop/dynasty/build/backups/architecture-v3-Oo6rOi/`。使用新文件替换目录项，没有原地写坏运行中 Java 持有的旧 JAR。

完全退出游戏再启动当前实例，才加载新代码和资源。旧世界已生成建筑不会被替换，新建筑请在新区域或独立测试世界查看。没有改任何存档、没有提交或上传 GitHub，也没有重打旧导入 ZIP；不要重新导入旧 ZIP 期待包含本轮内容。
