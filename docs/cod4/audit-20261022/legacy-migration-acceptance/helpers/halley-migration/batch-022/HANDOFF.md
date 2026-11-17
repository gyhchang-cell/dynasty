# Halley → Kepler：第022批，credit0

官方 MCA Reborn 固定 commit `4d824551b30654e5792e19e84f3933e3e3d90ea2`，三条待审对象家族；未新增下载信用。

- Reaper 持久召唤任务：旧position直接坐标回退为spawnPosition与下方fire；新格式writer写totems列表，reader却getCompound后传会强转NbtList的工具方法，静态类型不相容。完整读到仪式触发、VillageManager保存/重载、取消与最终Boss.spawn；生成返回null仍完成移任务。该子任务旧格式语义独立于021父容器，重复风险明确留主责判。
- CivilRegistry：真实死亡/婚姻历史写JSON Text列表，主世界按村庄int ID存文件，实际书页请求、恢复与绘制完整串联。村庄管理器本身按维度，各维度可同ID时历史键未带维度；坏entry缺隔离。页/网络只是支持。
- VillagerTracker：真实外置UUID→GlobalPos持久注册表→追踪物品→指南针/距离。set只put不dirty，remove才dirty且未找到外部调用；死亡更新最后位置，换绑/查无目标未清旧position。bounded map仅支持，不作泛用缓存计数；是否按派生缓存排除由主责。

99完整方法+17字段只为116支持节点，26文件，固定Git tree/blob/source和全文摘录/归一化hash已核对，错误0；无主摘录机械匹配仍需语义审阅。与019—021共享支持/批内矩阵已附，三个建议credit0、accepted=false。

未运行上游、编译、测试或游戏，未动屏幕/原存档/主账/生产/待办。继续下一选源实际研究；十小时和剩余范围未完成。
