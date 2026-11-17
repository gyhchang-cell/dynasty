# Halley → Kepler：第018批，credit0

固定官方 ForestryMC/ForestryMC `72e15b0f08daa25d8293cf28b5d5e1da200f9161`，来源复用第015批。三条待审核建议：

1. 背包base36槽与持久mode/整数UID → 实际拾取、补给和箱体交互。单槽修改保留未知Slots键，整包markDirty重新编码会丢弃当前容量外旧槽；UID缺失在构造时补写，UID不是玩家身份。
2. 茧Caterpillar/Age/CATMAT/isSolid重载 → 普通茧孵化或固体茧采集 → 实体/物品产物。缺Caterpillar与空Caterpillar默认个体不同；固体块没有普通孵化tick。共享第016染色体codec仅支持，不追加计数。
3. 果荚UID/MT/SP重载 → 生长与真实产品。未知UID回cocoa且重写会覆盖原UID；genome未持久化，但当前FruitProviderPod产物忽略genome，不能据此声称已证明产品改变。

JSON含完整方法/固定commit/tree/blob/source SHA256、全文范围与摘录/结构哈希、逐项具体观察/应用/限制/去重风险。180方法、13字段和1静态初始化共194节点只是支持证据，不能作为194条实现。39文件证据；静态文档核对parse/hash错误0，只读主账1072行，主摘录无机械碰撞，语义仍待主责。

未运行编译、测试、游戏、服务器、GameTest或上游代码；无GUI/屏幕操作，不改生产/主账/待办/原存档。十小时与全部剩余研究仍未完成，继续后续批次。
