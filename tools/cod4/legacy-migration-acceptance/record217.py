import json
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()))
s=[c['candidate_id'] for c in cs if c['path'].endswith('/Sorcerer.java')]
a=accepted('13e5a8c107653d3c4254','goety-sorcerer-legacy-level-alias-health-init-and-spell-entitlement','完整Sorcerer576行，含读写/等级派生属性/出生升级及实际选法和释放消费者','优先SorcererLevel，否则Level老字段；HasSpawned boolean控制读入是否补满生命，SorcererSpellTicks辅助临时状态','setSorcererLevel clamp1..5→同步LEVEL/经验奖励8倍等级/可选maxHealth设置；升级来自raid/assault，实际SpellGoal按级别min/max过滤及法杖/威力等级','一条实际schema alias到不同法术权限的实体等级进度owner，19法术及旧新键/属性/冷却不拆数。writer只写新SorcererLevel，旧Level支持fallback，有目标优先级而非纯静态映射表。归一化等级和临时充能/动作/数组CD分别审，不照抄永久玩家白名单。','contains未要求具体int类型：错误类型新字段会压住合法旧Level读成0后clamp1；HasSpawned缺省false会heal而非只复制Health，且boolean未赋给字段，tick才true。level1时不还原先前高等级health基值；配置关闭不处理原属性。保存castingTime但不存选中的spell、warmup、cooldown数组，恢复不是完整施法续跑。raid条件easy在前使高阶else-if可能不可达，仅静态观察。spell具体实现/父类库存/通用Mob底层未全链展开，当前条只覆盖明确alias与已读等级实际消费者，无原生运行声明。',s)
record(217,[a])
