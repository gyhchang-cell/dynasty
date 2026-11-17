"""Native elemental hurt sound receipt, not a generic packet credit."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/';f='common/network/server/SPlayWorldSoundPacket.java';n=len((B/'sources'/r.replace('/','__')/(p+f)).read_text().splitlines());k='goety-native-elemental-hurt-world-sound-broadcast-current-world-consumer'
record(k,r,[(p+'common/events/ModEvents.java',163,164),(p+'common/events/ModEvents.java',1089,1154),(p+'utils/ModDamageSource.java',212,225),(p+'common/network/ModNetwork.java',36,40),(p+'common/network/ModNetwork.java',75,75),(p+'common/network/ModNetwork.java',125,127),(p+f,1,n),(p+'client/ClientProxy.java',28,32)],
 'FORGE已注册ModEvents原生LivingHurt的shock/hellfire分支→服务器目标blockPos及对应声效SPlayWorldSoundPacket→已注册SimpleChannel→PacketDistributor.ALL→enqueueWork→ClientProxy当前Minecraft.level instanceof ClientLevel→本地NEUTRAL声。',
 '按实际战斗声接收边界整链1，不将泛用send/decode/helper各算。包只带BlockPos/resourceLocation/volume/pitch，无世界key、目标ID或事件nonce，ALL会发往非目标维度玩家；接收只要求当前ClientLevel，未校验维度/距离/有限数值/存活目标，可能在另一维度同坐标播声（静态路径风险，未动态复现）。使用方LivingHurt阶段先播声和粒子，再处理火免疫减半/火保，后续其他监听器仍可取消，因此不是最终HP变化确认，更不是控制免疫。shock/hellfire只是来源和音色常量，合计1。无本链逐目标时间节流；高频伤害可重复派送。中性声类别而非伤害者个体类别，声源出生坐标非跟随目标。声音是否听见还受距离/音量设置，未听音。',
 'Boss灰字与嗡声回执必须由最终拒控生产、携带目标与世界身份并限速；只在有客户端世界就播声不足以避免跨维度污染，不能借原生受伤声证明IMMUNE。优先原版声音但仍须真实听音验收。',
 '完整关键事件/包/consumer已读，固定提交hash。原生Forge事件即本链生产入口；元素攻击具体每种来源/原版sound引擎内部未单独研究，辅助0。无游戏/正式代码/资产/待办改动。','combat_feedback_receiver_world_validation')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'goety-elemental-world-sound-batch53','credited_chains':[k],'rationale':'真实LivingHurt声回执→ALL→当前世界消费的完整游戏实现1；不是按通用包函数计数，两元素合并。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
