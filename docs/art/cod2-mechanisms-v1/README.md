# 2026-10-11 Cod2机关续作

已完成并从外部cod2.txt删除三条独立要求：冲压巨锤、传送带、上升气流。完整地牢、Boss与整份Cod2仍未完成。

| 条目 | 实际变化 | 验收 |
|---|---|---|
| crusher_hammer | 原创厚锤头与承压底座；原房间WARNING/ACTIVE/RECOVERY驱动竖向动画；可见头与伤害AABB共享尺寸；光照采样随锤头高度 | 实际同一循环生命20→16→16；预警无伤害；高处目标无误伤；最终四向与重载实绘 |
| conveyor_belt | 原创粗框、分段履带和方向标；FACING旋转；推动真实站立实体及掉落物；排除浮空目标、保留更快运动和纵向物理 | 原生掉落物在七段履带上自行移动，逐tick轨迹、有限速度、物品数量1；无瞬移 |
| updraft_vent | 注册受保护风口；粗阶梯Cuboid；有限4格高区域，每两tick加0.24竖向速度，封顶0.33，水平保持 | 使用原生重力的掉落物实际上升；区域外无力；位置不被力函数直接改写 |

交付4份Java原生block model JSON、4张实际16×16 PNG、4份java_block格式bbmodel和3套四朝向blockstates。动态锤头由BlockEntityRenderer与服务端状态快照驱动；这些方块使用Java方块格式，不生成无用途的geo/animation文件。贴图含白最多4纯色、一格白边、2×2色区，所有面UV采有效纯色色岛。

制作前比例、部件及动作在[PLAN.md](PLAN.md)。正面/45°/90°/背面/纯黑剪影已检查；`*-review.png`是导出几何的软件复核，实际游戏证据在[native四向接触表](native-four-views.png)及`native/`原始截图。

Java17离线build成功，76项Cod2原生服务端测试全部通过。真实Forge客户端一次跑整批；随后修正测试相机/单循环夹具，以及实际发现的锤头光照问题，分别补验。共3次实际客户端启动：run1失败证据保留，run2完整功能18图/19记录通过，head-light1只补最终锤头四向及重载5图/6记录。没有重复运行已经通过的76项服务端测试。两个通过快照的全部运行资源相同，唯一变化的生产类是锤头Renderer；已验证的服务端物理字节未变。

详细SHA、JAR核对、真实轨迹和删除原文见[DELIVERY_20261011.json](DELIVERY_20261011.json)。最终本体在`build/cod2-mechanisms-build/libs/dynasty-1.4.0.jar`；11项运行资源与源文件逐字节相同，QA类不进正式JAR。失败的初次组合日志在客户端QA漏导入处停止；修正后完整build日志明确成功。

不改现有Block/BE框架、并行任务的战斗/任务/AI和碰撞；本批只修正本聊天机关作用区域并添加独立风口。两个既有精英动画已被并行工作更新，本批未修改或回滚，当前SHA记录于[parallel-preservation.json](parallel-preservation.json)。没有推送GitHub。

未验收整座千机城/隐仙观、缺失命名Boss、多人通关或TPS；蒸汽与火焰的组合条目仍保留。清单删除账本现在累计10处，可用原始备份减去账本逐字节重建当前文本。
