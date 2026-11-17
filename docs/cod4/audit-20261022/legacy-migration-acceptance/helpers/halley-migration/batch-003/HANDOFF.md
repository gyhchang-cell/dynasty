# Halley → Kepler：第三批，6 条研究建议，credit 0

已完整阅读并整理六条真实玩法持久化链；不是六条已接纳新增。包含 101 个去重完整方法节点、30 个证据文件。412 个下载文件、4077 个索引节点不计研究 credit。没有构建、测试、游戏、上游代码执行、生产变更、主账写入或原存档操作。

固定官方来源（commit → Git tree → blob 与本地 SHA256）：

- Daripher/Passive-Skill-Tree，branch 1.20.1，commit bd5a5bc3b63655b9302084f418038628323f36de，tree 7fce3d0e9f851120dcf3bf8a87e0c98b1af28759。
- SilentChaos512/ScalingHealth，branch 1.20，commit 34486f65db9bb791fde8fe6ef43f5664c19990d6。精确 tree、每个 blob/文件 SHA256 见 tools 对应 batch-003/source-manifest.json。

主入口为 batch-003.json 或 reviewed-suggestions.jsonl。每条带完整方法正文、上下界、固定 URL、文件/摘录/规范化 SHA256、Git blob、具体观察/应用/限制/重复风险；同链支持只放 evidence。方法起点包含 annotation，摘录按 AST 起止字节，不含首行缩进。

| 研究链 | 实际语义与限制 |
|---|---|
| 技能树版本/失效技能退点、Clone、效果重建 | 全列表退点，入世界 learn(false) 避免首次学习物品再次发放；TreeReset 写出却未读回；旧 ID 映射并未实现 |
| ScalingHealth 自有双能力 Clone | 先复制后按死亡限定执行心数/难度变换；不复制 AFK 等临时字段；反射 valid 非可移植范式，reader 绕过限幅 setter |
| 怪物持久状态与非持久 processed | 读盘保留 blight/difficulty，但随后重新随机计算难度；固定 UUID 避免简单属性叠加，不能称原样恢复 |
| 宠物永久累计生命与延迟重应用 | 不重放付费互动，仅重建累计量属性；互动无 owner 检查，缺 capability 仍可能消耗；与怪物条高重复风险 |
| 物品类型化奖励嵌套重建 | 真实制作→标签→换装属性消费；未知嵌套子项可能使整组失败；升级把两类奖励写到一类但留另一类的静态风险 |
| 武器毒性效果与有限/无限次数 | -1 无限，归零同时删效果与次数；制作新 ItemStack 丢原栈数据，攻击事件不是最终伤害成功回执 |

静态文件证据核对见 document-integrity.json：提交树/blob/字节/AST 范围与哈希无差异。与当时主账 878 行的匹配保留在 semantic-duplication-notes.json。怪物与宠物 primary 是短 reader，规范化命中多个 Botania 标量读取方法；没有通过更换 primary 藏掉碰撞。具体命中正文已阅读，仍由 Kepler 看整个玩法 owner/consumer 判断；怪物/宠物彼此也允许合并。不能由“规范化碰撞是通用 reader”直接推出新增资格。

考试期间本批仅进行了源码阅读、文档生成与离线文件证据核对，没有运行编译/测试。用户现已明确解除考试禁测，但当前分工仍只研究；图形/游戏/真实 TCP 必须由主协调集中安排，本岗不自行启动。不需要游戏来完成此研究交付。

主账只读观察为 677/1000（最新 progress 文件）；不得把本批直接加到该计数。至少 10 小时持续研究要求尚未达到，接下来继续独立选源，不因交付本批结束目标。
