# Halley → Kepler：第019批，credit0

官方MCA Reborn：CurseForge Source链接指向 Luke100000/minecraft-comes-alive。固定1.20.1 `4d824551b30654e5792e19e84f3933e3e3d90ea2`；GitHub fork=true是官方续作谱系，不将原MCA/移植另计。两条完整持久玩法建议，信用仍0：

- 玩家mca_player_UUID持久对象，含entityData/初次定制/inbox/lastSeenVillage；读到登录、数据请求、实际取信和世界更新。普通get固定主世界，getIfPresent直接取传入世界；缺entityData随机模板与空compound不同；取信remove后未dirty，后续周期dirty不等于保证消费事务。
- 家谱MCA-FamilyTree旧关系枚举升级：固定哨兵UUID缺失时，先载完整图，再依partner.isPlayer顺序修正三个状态分支。枚举越界fallback不能解决旧序号仍合法但语义错。真实婚姻/生育gate读取恢复结果；节点save不写reader接受的profession，坏UUID项未逐项隔离。

142完整方法+18字段只是支持证据，不能当160条参考；26文件；全部固定tree/blob/source与方法/归一化哈希、全文行范围、具体观察应用限制和语义去重风险已附。文档AST/source核对错误0，主账快照1080行、主摘录无机械匹配仍不代表语义接受。两对象共享编辑/关系支持方法，去重矩阵明确不加支持信用。

采集脚本复制时曾错误保留第015选源文件名，重复取Forestry；已纠正并把重复取值排除019 manifest/inventory，详情tools同批acquisition-correction.json。没有把重复下载或任何候选算信用。MCA当前477可用源码文件和2921方法索引只为未审库存。

仅研究，无编译/测试/游戏/屏幕/原存档/生产/主账/待办操作。下一批继续同固定MCA的真实实体转换/墓碑载荷恢复，十小时与全部剩余研究尚未完成。
