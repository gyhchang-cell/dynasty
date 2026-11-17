"""Native over-limit refusal is not ordinary damage capping nor Boss control immunity."""
from ledger import B,O,record,verify
import json
r='Aizistral-Studios/Enigmatic-Legacy';p='src/main/java/com/aizistral/enigmaticlegacy/';k='enigmatic-cube-native-overlimit-whole-damage-refusal-and-targeted-recoil'
def w(f):
 f=p+f
 return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
record(k,r,[(p+'handlers/EnigmaticEventHandler.java',1997,2012),(p+'items/TheCube.java',66,90),(p+'items/TheCube.java',158,164),(p+'handlers/SuperpositionHandler.java',277,280),(p+'handlers/SuperpositionHandler.java',1322,1324),(p+'config/EtheriumConfigHandler.java',133,144),w('packets/clients/PacketPlayerMotion.java'),(p+'registries/EnigmaticItems.java',378,380),(p+'registries/EnigmaticItems.java',526,526),(p+'EnigmaticLegacy.java',200,244),(p+'EnigmaticLegacy.java',350,350)],
 '实际TheCube装备注册/主Forge handler→LOW native LivingHurtEvent仅ServerPlayer且source.entity非null→当前event.amount>getDamageLimit(佩戴CursedRing?150:100)且实际Curios装备Cube→整次setCanceled/ITEM_BREAK声→directLiving时从攻击者/玩家位置归一化计算recoil→EtheriumConfig.knockBack写server velocity，若ServerPlayer则定向PacketPlayerMotion→enqueueWork对本地player setDeltaMovement。',
 '一个单次伤害阈值整次拒绝的最终生产点1，两个阈值/破碎声/S2C motion wrapper合并。不是把伤害cap到100/150，是>而非>=，100或150恰边界仍伤；环境无source.entity不走这个拒绝（Cube其他来源列表另有既有家族），不能写作所有巨伤/所有Boss招式免疫。LOW读已被先前listener修改后的event.amount，不保证最原始量。getter先于hasCurio执行，未装备也读诅咒身份。播放破碎声并没有在此破坏装备/扣资源；不据声音名推装备碎裂。无per-target冷却、序号或一次事件ID。',
 '拒伤/阈值超限与控制免疫应分不同语义，Boss灰字不能监听任意hurt取消。原版声音可用作既有反馈资源，但选择仍需按最终拒控语义；定向motion包不能作为改变他人Camera的范例。',
 '固定a0294f119a0a84a4627b008bc90fe31808dbf596，完整核心方法、native注册、实体归属与S2C receiver已读。PacketPlayerMotion无client player null/finite/维度/代际检查，默认registerMessage没方向约束；本条不冒称攻击者一定实际位移/无网络风险。TheCube其异步传送不属于本条，不以未展开部分加数；无游戏、正式源码、资产、TODO改动。','native_final_damage_refusal')
f=O/'semantic-dedup.json';d=json.loads(f.read_text());d['groups'].append({'family':'enigmatic-cube-native-threshold-batch64','credited_chains':[k],'rationale':'与Cube既有source列表/impact反弹不同的LOW LivingHurt超阈值整次取消；不是同链wrapper/换source常量；两个curse阈值不拆。定向受击motion仅随拒绝回执链引用0额外。'});f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
