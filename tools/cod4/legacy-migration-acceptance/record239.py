import json
from review_batch import accepted,record,O
cs=list(map(json.loads,(O/'candidates.jsonl').read_text().splitlines()))
rows=[]
def support(suffix,root):return [r['candidate_id'] for r in cs if r['repo']=='AlexModGuy/AlexsMobs' and r['path'].endswith('/'+suffix) and r['candidate_id']!=root]
root='7fcda62379ac0e38324a'
rows.append(accepted(root,'alexsmobs-rescued-whale-permanent-once-reward-versus-unpersisted-recipient','鲸鱼add/read完整方法及完整aiStep390–742，字段/constructor/REWARD_PLAYER_PREDICATE声明、getMouthVec/getVec已读；搁浅眼部重新入水找50格最近非lastHurt玩家，水中距离<10发放。','GivenReward boolean缺省false保存once资格；rewardPlayer仅内存Player引用无UUID存档，rewardTime字段未用于此消费。DespawnDelay numeric类型存在才覆盖47999默认。','实际服务端spawn 2–3 AMBERGRIS，随后hasRewardedPlayer=true并清rewardPlayer；后续reward消费要求!hasRewardedPlayer。','独立永久一次奖励回执与待领奖人区别实现1，不把Albino/Beached/战斗字段拆分。与其它已计喂鱼累计奖励不同触发/对象/once消费，非同代码换键。对本修复 once flag必须长期保留、接收者未保存可能让已达条件奖励丢失提供具体边界。','addFreshEntity未核成功即写once，非发放事务；两端写once但spawn服务器；不保存recipient所以reload不能保证未领者恢复，未运行。只指定完整方法和字段，非整个970行全部已审；原生animal持久桥共享0信用。',support('EntityCachalotWhale.java',root)))
root='5024aa78c8fc0c385ce4'
rows.append(accepted(root,'alexsmobs-bison-earned-grazing-count-to-fur-regrowth-receipt','EntityBison564行全文；server吃草动画tick30且下方GRASS_BLOCK才feedings++并替换DIRT；tick累计>=5且sheared才归零恢复毛。','Sheared bool和Feedings int明确持久化，缺省false/0；ChargeCooldown也写磁盘但实际是战斗timer非永久进度；SnowPerm物品交互为支持。','readyForShearing非baby且未剪；shear先set剪过/归零再spawn2–3 BISON_FUR，Forge onSheared组列表归零/置剪过。','真实多次世界资源消费累计余额→再生→剪取回执一链1；区别原版sheep直接一次草重生与已计Grizzly定时产毛、Turtle苔藓水平，非仅键名变化。field两状态必须按同owner恢复，否则reload免费恢复或漏掉已赚进度。','reader未clamp负/过大Feedings；吃草setBlock bool未确认便加余额；regrow分支无serverguard；剪取先清资格无产物交付确认。Snowy/permSnow为外观支持不另计，临时charge保存不等于可复制玩家永久字段。静态未运行未改正式。',support('EntityBison.java',root)))
record(239,rows)
