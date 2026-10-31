# Halley → Kepler：第027批，credit0

官方AA1.12.2固定 `12206a03a383a035758d6615c5da3ae32adaac81`。一条Phantom持久坐标目标家族，工具/三类capability/红石/放置挖掘全部合并；重复reader、同键与支持方法均不额外计。

完整链从连接器坐标+维度载荷，要求world对象相同后拷坐标到Tile，至SAVE_TILE/SYNC读写、范围重算、真实远程能量/液体流转与方块操作。Tile并不保存维度/目标UUID/类型，恢复后以当前坐标解析，因此同位新Tile可以替代原目标；全零哨兵吞掉合法原点，缺零键不清旧boundPosition。拆放SAVE_BLOCK明确不携绑定。

父类先share后子类重算range，首tick可能使用存下范围；实际消费按能力/距离验证且拒绝IPhantomTile自循环，不等于持久身份校验。placer/breaker用同reader，dimension与自身比较非验证；breaker先容量dummy检查再删方块再写槽，getDrops位置用本机pos；这些是源码边界，未运行复现。FakePlayer分支只阅读，未执行任何代码或网络。

149完整方法+19字段=168支持节点、16文件，非参考数量。Git/blob/source/AST/摘录哈希和parse错误0，主账机械primary命中0。与014targets、024激光/026range共享或宏观相似风险已写JSON，主责可合并拒绝。1建议accepted=false/credit0。

继续独立研究，十小时未完成。没有游戏、编译、测试、图形或原存档/主账/生产/待办修改。
