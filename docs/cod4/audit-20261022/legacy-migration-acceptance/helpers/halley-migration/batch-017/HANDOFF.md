# Halley → Kepler：第017批，credit0

固定官方 ForestryMC/ForestryMC mc-1.12 commit `72e15b0f08daa25d8293cf28b5d5e1da200f9161`，复用第015批来源；本批无新下载。两条完整玩法持久语义建议，均待主责核查去重，非已接受信用。

- 旧电路UID替代表 → CircuitBoard NBT → 农场sockets重载 → onLoad/setFarmLogic → 实际种苗消费。一条链合并四个旧别名与所有方向/板型。未知layout时默认返回值未赋值，未知电路UID重写会丢失；manual标志看似重置已追到实际no-op setter，不报告假bug。空读写CircuitLibrary明确排除。
- TradeStation世界存档与TileTrader本地fallback库存 → 真实订单付款/货物消费。一条链合并owner/virtual/库存/邮费；世界站缺失时新站未见从fallback恢复，且订单先投回信再修改存量。与第016批邮件支持链高度重叠，仅交易订单/双持久库存语义供主责判定，若同家族则合并。

完整方法与字段上下文均附固定tree/blob/source哈希、AST全文范围、摘录/归一化哈希及源URL。153个完整方法和23个字段只是支持证据，不能作为153或176条参考。28文件证据；静态文档核对parse/hash错误0；只读主账1069行，主摘录指纹未碰撞，不等于语义已通过。没有运行编译、测试、游戏或上游代码，未改主账/生产/待办/原存档，无屏幕操作。

继续后续独立语义研究；十小时与全部剩余范围尚未完成。
