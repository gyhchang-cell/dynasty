# Halley batch-050 → Kepler

1条待审建议、1条已排除同族风险，均credit0、accepted=false。固定官方Globox1997/LevelZ commit `ed2ddf84a4a6177ef15ac4fb2188074a597ccf63`、tree `bec1bfc239b3ff4e342605099fcbdf489a36426e`；属性为MC1.21.1/mod2.0.12。完整源码/方法行范围及SHA256、Git blob、摘录hash/归一hash保留在tools对应批次与本目录JSON，文档核对0解析/哈希错误。

玩家profile一整链：当前技能ID校验、缺项补0、超限退款、显式Clone五项、数据包重载与临时属性重建。数字ID没有旧别名表，不能保证ID重排兼容；map复制为共享引用。默认死亡保留100%，resetCurrentXp清当前经验；上游自带百分比死亡政策仅作观察，不能移植为新增惩罚。所有字段/限制类别/技能数/支持方法只属一链。

经验球完整reader/writer/旧Value+Count→clumpedMap/merge/pickup已读，但注明Clumps启发且近原生经验球家族，先排除，不给新建议。excluded_records保存完整证据，不能误计。

未执行上游、构建、测试、游戏、GUI；不碰主账、生产、待办、原存档。十小时最低实际工作量及剩余范围继续保留，尚未完成。
