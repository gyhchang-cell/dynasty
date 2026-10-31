"""Wind robe native fall-denial and entity-bound wind lifecycle; one family."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
def w(f):return p+f,1,len((B/'sources'/r.replace('/','__')/(p+f)).read_text().splitlines())
k='goety-wind-robe-native-budget-gated-fall-refusal-and-entity-wind-lifecycle'
record(k,r,[(p+'common/events/RobeEvents.java',40,43),(p+'common/events/RobeEvents.java',442,447),(p+'common/items/ModItems.java',246,247),w('common/items/curios/WindyRobeItem.java'),(p+'utils/SEHelper.java',76,90),(p+'utils/SEHelper.java',179,185),(p+'utils/SEHelper.java',309,328),(p+'utils/CuriosFinder.java',42,63),(p+'utils/CuriosFinder.java',380,382),(p+'utils/TotemFinder.java',86,113),(p+'api/items/magic/ITotem.java',39,41),(p+'api/items/magic/ISoulContainer.java',62,68),(p+'config/ItemConfig.java',239,240),(p+'utils/ServerParticleUtil.java',286,307),(p+'utils/ServerParticleUtil.java',345,351),w('client/particles/WindParticleOption.java'),w('client/particles/WindParticle.java'),w('client/particles/WindTrailParticle.java'),(p+'client/particles/ModParticleTypes.java',452,458),(p+'init/ClientSideInit.java',141,141)],
 '已注册Wind/Storm robe→FORGE原生LivingFall检查Curios实穿与灵魂余额后取消落地伤害；独立原生inventoryTick下降条件触发每20tick尝试扣魂/减速及服务器目标ID WindParticleOption→已注册provider→当前世界查owner、跟随绕身→年龄/目标消失移除→CUSTOM透明trail采样绘制。',
 '整条预算拒伤/状态反馈/锚定生命周期一族1，不按袍名、trail helper或圈粒子拆。落地回调只检查余额不消耗，空中按周期扣费且受SoulLossEvent/discount影响；不可据落地cancel反推每次扣费。creative只在inventoryTick有旁路，落地余额检查没有creative旁路。风是符合下降条件时持续产生，并非落地被拒绝的一次性回执。实际Totem优先Curios再副手覆盖，否则前十库存槽首个；余额读取NBT/激活cap。包只有owner数值ID，无UUID/维度代际；owner缺失的关联风移除，ID复用不验证类型/UUID，出生寿命0转随机20–39tick。trail64历史点/4采样，tick记录位置，透明CUSTOM共享buffer.endBatch和禁cull不能静态证明遮挡或清晰度。代码注明Cataclysm来源，后续同源trail不得重复信用。',
 'Boss灰字须由最终拒控明确产生，持续状态环绕不能代替拒控确认；S2C需目标身份/维度生命周期，按目标节流与对象上限分开。普通阴阳体质不增灰字。',
 '固定Goety-2源码提交及逐文件hash；观察完整关键方法。通用Curios库/vanilla粒子派送内部为辅助0，SoulLossEvent监听器未全读，不声称实际扣费数；Storm lightning旁支不计且未完成收包链。未运行游戏、未改正式源码/资产/待办。','native_damage_denial_and_target_feedback')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'goety-wind-robe-batch52','credited_chains':[k],'rationale':'落地余额门+另行空中扣费+实体风反馈整链1。Cataclysm同源trail不得另计。LichEvents伤害LICH_IMMUNE标签未找到原生填充，仍0，不凭存在分支算有效实现。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
