COD4-1 / COD4-11 只读自然生态验收

在仓库根运行：
python3 tools/cod4/ecology-acceptance/prepare.py
python3 tools/cod4/ecology-acceptance/audit_sources.py
python3 tools/cod4/ecology-acceptance/run_verified.py normal-run3

每次用新label，拒绝覆盖旧运行。正常Forge DedicatedServer自动使用种子20261023、normal地形、真实结构生成，完成有限扫描后保存退出。测试世界与缓存位于独占.work；不改正式Java/assets/TODO。首次独立缓存APFS克隆与编译可能需较长时间。run_verified创建独立本地测试世界的eula.txt，不复用玩家存档。

本次归档结果：docs/cod4/audit-20261022/ecology-acceptance/report.txt、result.json、normal-run2-observations.json、normal-run2-receipt.json。normal-run1为较小locate半径1的初测；normal-run2扩大为4，其余生成机制相同。最终summary固定读取normal-run2，不会把后续未审核运行冒充已验收结果。

当前为无玩家的昼间有限样本。原生SpawnPlacements回调通过只证明对应入口条件，不等同于自然刷出、自然击杀或自然材料到手。30物种、10材料是独立分母；本次不宣称生态清单完成。未创建新建筑，也未用手放结构/改biome/生成命令替代自然生成。
