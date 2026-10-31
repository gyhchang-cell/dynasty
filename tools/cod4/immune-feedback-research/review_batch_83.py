"""Cached attacker-power refusal differs from target immunity and positive hit feedback."""
from ledger import B,O,record,verify
import json
r='DaedalusGame/EmbersRekindled';p='src/main/java/teamroots/embers/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='embers-native-cached-attacker-power-denial-and-deferred-boolean-consumption'
record(k,r,[w('item/ItemClockworkAxe.java'),f('EventManager.java',538,568),w('util/EmberInventoryUtil.java'),w('api/event/EmberRemoveEvent.java'),f('RegistryManager.java',383,383),f('Embers.java',64,73)],
 '实际注册clockwork axe实现IEmberChargedTool；Forge EventManager.onEntityDamaged从DamageSource.trueSource取Player并读当前mainhand，非创造且hasEmber false即cancel。hasEmber读取stack NBT poweredOn；原生onUpdate每5 tick查询库存/手持/可选Baubles的live总ember，>5才powerOn。未取消且amount>0的正向路径点火并服务器发EmberBurstFX，标didUse；后续onUpdate读单boolean只消耗一次5 ember并在live总量<5时关power。removeEmber先post折扣事件，按副手→主手→Baubles→库存收取，不返回欠额或事务成功值。',
 '最终拒伤是攻击者当前装备的缓存能量资格1，非Boss防御。没有检查direct source与发射时武器，因此不能从此取消推断目标免疫。5 tick缓存、>5开启与<5关闭边界不对称；同次更新前多个成功hit都写didUse=true，不能称逐次命中原子付费。拒绝分支没有专门文字/嗡声/网络回执；EmberBurst是正向hit反馈不代表拒绝。本次不将正向包/renderer作为已完整验收链，亦不拆工具变体、折扣或库存扫描计数。',
 'Boss拒控必须由目标控制政策产生明确reason；不能把攻击方支付不足或普通伤害cancel映射灰字。节流记账应与最终拒绝事件语义及权威目标绑定，不借用延迟boolean消费或装备刷新缓存。',
 '固定源码，完整axe/能量聚合收取/event方法及实际事件注册已读。只读，无游戏/生产改动；未验证延迟箭、跨tick资源并发或实际FX像素。普通玩家不新增灰字要求。','native_attacker_resource_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'embers-batch83-cached-attacker-resource-qualification','credited_chains':[k],'rationale':'当前攻击者装备缓存资格→最终hurt取消→后续boolean收取的独立结算位点1；非单纯source常量、目标消耗盾或装备换壳，正向粒子/工具变体/聚合包装0。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
