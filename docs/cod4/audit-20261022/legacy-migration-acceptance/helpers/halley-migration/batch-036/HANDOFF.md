# Halley → Kepler：第036批排除证据，0建议、credit0

官方 NaturesAura 94a21a6c2c0cd73f581369f72d7190edb960c5ef：EntityMoverMinecart 搬运灵气，非收纳实体。完整读取22方法/3文件，只是排除支持节点，不能作为22或1条有效参考。

扩展 serializeNBT/deserializeNBT 存 active/last_pos/offsets，但本仓库未证明常规原生实体落盘和 restoreFrom 调用这些覆写，尚未展开对应原生版本。不宣称必然丢档；结论是接线未证实。轨道会 create→restoreFrom→addDuringTeleport；运输先drain后store并故意损耗，destroy只掉新空矿车。3轨道变体不拆计。

完整Git树/blob/源SHA审计见document-integrity.json；22完整方法AST摘录与规范hash审计见exclusion-document-integrity.json，均错误0。excluded-candidates.json保留可复核全文，reviewed-suggestions.jsonl为空，不导入主账信用。保留原选源记录并在此明确修正预期。

继续037宠物资格/死亡恢复及新来源Requiem、identity。十小时工作量未完成，无生产主账待办原档修改、无游戏编译测试GUI。
