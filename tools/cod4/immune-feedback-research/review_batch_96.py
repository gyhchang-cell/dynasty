"""Native accumulated budget and exposed sub-body qualification. No asset copying."""
from ledger import B,O,record,verify
import json
keys=[]
r='Lycanite/LycanitesMobs';p='src/main/java/com/lycanitesmobs/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
k='lycanites-native-success-fed-per-second-refusal-with-next-tick-health-rollback';keys.append(k)
record(k,r,[f('core/entity/EntityCreatureBase.java',1436,1493),f('core/entity/EntityCreatureBase.java',1509,1682),f('core/entity/EntityCreatureBase.java',2740,2777),f('core/entity/EntityCreatureBase.java',2781,2800),f('core/entity/EntityCreatureBase.java',3721,3750),f('core/entity/EntityCreatureBase.java',1221,1245),f('demonmobs/entity/EntityAsmodeus.java',83,101),f('core/info/CreatureInfo.java',139,326),('src/main/resources/assets/demonmobs/creatures/asmodeus.json',1,len((B/'sources'/r.replace('/','__')/'src/main/resources/assets/demonmobs/creatures/asmodeus.json').read_text().splitlines()))],
 '实际Asmodeus JSON enabled/boss/class→CreatureInfo.loadFromJSON反射实体类/registerModEntity，native constructor设置damageMax25和damageLimit40，rare子种也设置。EntityCreatureBase.attackEntityFrom先server/无敌/type/实体门，再乘modifier、减defense并限制单击，super true才onDamage累加damageTakenThisSec。isEntityInvulnerable达到limit拒后续伤。完整onLivingUpdate在super前比较healthLastTick与现HP，超过limit则整次恢复旧HP，每20 updateTick服务端清累计，末尾updateTick++。',
 '计1：原生成功事件累计的秒级准入预算和下一tick健康回滚属于同完整伤害政策。与仅单击clamp、相邻帧iframe、Minister总staff预算不同。累计的是传super的damage而非测得HP损失，后续减免会造成差异；本次跨越40阈值仍可先接纳，下一次才拒。单tickHP损失>40恢复全部旧HP而非clamp剩余额，也可能误恢复其他直接setHealth损失；未检查致死后复活可行，不作此主张。20tick是实体updateTick时钟，非真实秒/统一world-time。',
 'Boss拒控应从明确控制拒绝路径产生一次语义回执；成功伤害累计预算不是控制免疫。伤害数字、事后HP变化和拒绝时机不可混用。',
 '完整关键hurt/defense/onDamage/isInvulnerable/onLivingUpdate及配置加载/注册方法已读；CreatureInfo从loadFromJSON到register全部读过。来源CRLF原字节保留Git hash。未读取全部extra行为、实际启动/画面/双端，无灰字/嗡声实现声称。Asmodeus活体小兵阶段盾与既有Goety partner家族不重复计。','native_success_accumulated_damage_budget')
r='team-abnormals/endergetic';p='src/main/java/com/teamabnormals/endergetic/'
k='endergetic-native-exposed-egg-sack-route-bypasses-body-arrow-refusal';keys.append(k)
record(k,r,[w('common/entity/eetle/BroodEggSack.java'),f('common/entity/eetle/BroodEetle.java',120,181),f('common/entity/eetle/BroodEetle.java',195,351),f('common/entity/eetle/BroodEetle.java',489,505),f('common/entity/eetle/BroodEetle.java',559,581),f('common/entity/eetle/BroodEetle.java',720,743),w('common/entity/eetle/ai/brood/BroodEetleLaunchEggsGoal.java'),f('core/registry/EEEntityTypes.java',50,52),f('client/model/eetle/BroodEetleModel.java',113,201)],
 '实际BROOD_EETLE/BROOD_EGG_SACK registry和已注册LaunchEggsGoal，原生start设置同步firingCannon，tick驱动eggCannon及15tick eggMouth max，stop清firing。完整Brood tick维护独立sack实体、双方id与位置，缺失自动重建。sack.hurt只server且parent存活且mouth完全open或lastStage时允许，附加节肢伤害→parent.attackEntityFromEggSack直接super.hurt，成功才附魔回调、WET_GRASS_PLACE声、15 egg block粒子。普通body.hurt直接arrow false，其他非特例仅5%/10%，弱点路线绕过body override。',
 '独立计1：动画窗口实际决定另一个受击入口能否绕过身体拒箭，非单纯代理转发，不按body/sack/粒子/注册拆数。sack在server tick要求parent.getEggSack==this，非当前关联的孤儿discard；持久化仅整数id无UUID/维度代际保障。模型setupAnim用同getEggMouthProgress开四片口，逻辑用isMaxed不是肉眼半开；只有成功伤害请求声粒子，关闭窗口false无免疫文字。',
 'Boss某一受击部位拒绝并不代表所有入口拒伤或免控；控制接入要统一原生最终拒控语义，成功受击和拒绝提示不能共享单个hurt=false推断。',
 '完整sack类、parent完整tick/关键hurt/数据/getter、完整LaunchEggsGoal及模型setupAnim/renderToBuffer均已读。Blueprint Endimator内部未读，仅按其isMaxed/tick调用边界描述；实际renderer注册/几何可辨识未验，普通粒子API不代表画面通过。lastStage消费者确认存在，具体全部其他goal不额外信用。','native_exposed_secondary_damage_route')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch96-success-budget-and-exposed-secondary-route','credited_chains':keys,'rationale':'Entity-local success accumulator with subsequent refusal and tick rollback is one policy. Exposed secondary hurt entry bypassing normal body arrow refusal differs from generic proxy forwarding. Registration, data keys, animation pieces and particles zero extra.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
