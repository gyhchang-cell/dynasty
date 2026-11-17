# Halley → Kepler：第025批，credit0

官方 Ellpeck/ActuallyAdditions 1.12.2，commit `12206a03a383a035758d6615c5da3ae32adaac81`，复用023固定源/Git tree/blob。仅一条巨箱库存升级家族，两个入口与全部规格合并，不按支持方法计数。

- 实体箱升级先复制物品，再移除源Tile、换方块、扣道具，最后检查新Tile/容量再回灌；没有先确认目标成功。small→medium以基类isInstance检查，可匹配large子类，目标容量更小；超槽不保留。只拷库存，非完整旧Tile元数据。
- 保箱器携带路径完整追到掉落物Items→真实注册保NBT升级配方→放置回灌→Container实际取出。跳过keeper位置导致后续索引前移；放置循环不以目标容量限界。配方直接setTagCompound输入NBT引用，无显式深拷贝；有序/无序/大小/配方多实例全部同族。Data的SAVE_BLOCK读取不再load Items，所以不会由该共享调用再次覆盖刚恢复的root.Items。
- LootTable生成前先置null、来源移除和失败窗口仅作源码观察，未运行复现。借鉴应先保留源Count/tag/未知载荷，验证目标和容量后再提交，不全量Clone持久数据。

99完整方法+8字段共107支持节点、22文件，非107参考。Git/source/AST/摘录hash与parse错误0；只读主账1123行快照机械primary命中0。与024背包共享codec和槽操作不额外计数，主责可据语义进一步合并或拒绝。accepted=false/credit0。

没有游戏、编译、测试、上游执行、屏幕操作或主账/生产/待办/原存档修改。十小时与剩余范围仍继续，后续拟保留玩家接口UUID持久绑定和刷怪笼身份载荷链，实际审完再决定有效建议数量。
