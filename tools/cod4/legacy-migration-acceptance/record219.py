import json
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()));files=['/DistributorBlockEntity.java','/InserterBlockEntity.java','/BlockInserter.java','/BlockDistributor.java'];s=[c['candidate_id'] for c in cs if any(c['path'].endswith(f) for f in files)]
a=accepted('30c571593b00e5e11e29','divinerpg-single-cargo-inserter-round-robin-distributor-state','完整4类：单格Inserter与派生Distributor存档/轮转输出/移除回收，shared转移support合为一个owner','item ItemStack compound含原components/count、split_order byte方向ordinal，cooldown默认6非持久','parseOptional恢复货物，分配器按上次方向依次N/E/S/W/D查目标向下投递；成功剩余空才认提交，否则恢复原库存，拆块dropContents后remove BE清载荷','非原版5格lootable hopper原样复刻：单货物档+持久轮转游标与分配器相邻目标筛选实际consumer，相关父子合1而不按reader再拆。setBlockState派生调用oldSet跳过FACING属性避免分配器缺属性。对迁移借鉴物品完整载荷及运行游标语义区别，临时cooldown重建不能泛拷全部字段。','split_order未校验Direction.values范围，负/越界byte可抛；缺item不清已有内存，parseOptional失败为空无隔离旧载荷。方向和cooldown变更不显式dirty，只有removeItem正数setChanged；setItem本身不dirty。insertStack先模拟，目标空时execute余量未查且直接EMPTY可能丢物；回滚依赖目标操作遵约无原子保障。该转移核心部分沿用hopper思路只作支持0，不额外算一种新算法。额外cap注册/外部管道放入和底层Container drops未全部展开，无运行或全保物保证。',s)
rows=[a]
for i in ['5010f58c8d64d2550465','c223f7770d59e4227ad5']:
 rows.append(dict(candidate_id=i,status='duplicate',family='divinerpg-robbin-legacy-mouth-item-and-entity-hut-envelope-recovery',reason='本轮完整reader/writer类读后跨family检索确认已在095整条鸟/窝/巢托管链全文审阅，不因该support reader未作primary而再计，原095包含第二槽生成新鸟丢旧载荷边界。'))
record(219,rows)
