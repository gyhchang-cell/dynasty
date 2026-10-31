"""One native captive-identity refusal and chance-based unconditional release chain."""
from ledger import B,O,record,verify
import json
r='DrZhark/mocreaturesdev';p='src/drzhark/mocreatures/'
def f(s,a,b):return p+s,a,b
k='mocreatures-native-captive-only-damage-refusal-and-release-before-parent-result'
record(k,r,[f('entity/passive/MoCEntityCrocodile.java',31,88),f('entity/passive/MoCEntityCrocodile.java',150,338),f('entity/passive/MoCEntityCrocodile.java',383,446),f('entity/passive/MoCEntityCrocodile.java',483,520),f('entity/passive/MoCEntityCrocodile.java',568,595),f('entity/MoCEntityAnimal.java',1863,1885),f('MoCreatures.java',387,467),f('MoCreatures.java',503,524)],
 '固定6d3be813原生注册Crocodile，attackEntity近距且attackTime<=0对未骑乘目标1/3挂载并设置dataWatcher24 caughtPrey；原生onLivingUpdate有捕获者时清攻击目标、陆地拖水/间歇伤害、水中翻滚伤害。最终attackEntityFrom只在source.getEntity恰等于riddenByEntity时进行10次中9次false直接拒伤；其余1次先unMount再调用父attackEntityFrom。unMount恢复活目标deathTime0、mountEntity(null)、清caughtPrey，死亡路径也调用。',
 '计1：当前实际被抓受害者身份限定的最终伤害拒绝与随机即时脱控，而非一般Boss不受玩家伤害/坐骑友伤常量。抓取方收到被抓者攻击时可在父伤害最终拒绝之前释放；伤害成功不是释放前提，未抓的其他来源不进入90%门。区别Thrasher多次打击预算→stun→tick释放，以及Glider实际HP损失→重抓冷却。本门无明确server检查，无自有灰字、微光、嗡声、每目标提示节流。父Animal另有用户名归属拒绝，不把它再计一条。',
 '控制/伤害/释放必须分开返回语义；Boss灰字只为明确被拒的控制生成，禁止把被抓者受击免伤、父hurt失败或释放成功共用一个immune布尔。回执去重不能抹掉真实不同结算。',
 '关键完整native方法全文已读，非整篇Croc或基类全文；updateRiderPosition仅作锚定支持0，未制作/复用模型。原旧版mount/dataWatcher实现未运行；原生EntityAnimal AI调度由继承契约调用，不声称其上游完整源码也已读。普通阴阳体质无灰字要求，存档/客户端视觉未验。','native_captive_identity_damage_gate')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'mocreatures-batch105-captive-identity-refusal-release-before-hp','credited_chains':[k],'rationale':'Final refusal depends on actual currently captive attacker identity; alternative random branch releases before parent acceptance. Separate from a multi-hit escape budget or generic rider friendly fire. Capture/mount/position/animation wrappers zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
