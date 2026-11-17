"""Two manually observed Redstone Arsenal native chains; helpers and constants merged."""
from ledger import B,O,record,verify
import json
r='CoFH/RedstoneArsenal';p='src/main/java/cofh/redstonearsenal/';keys=[]
def w(f):return f,1,len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
def add(k,refs,c,o,l):
 for f,a,z in refs:assert 1<=a<=z<=len((B/'sources'/r.replace('/','__')/f).read_text().splitlines())
 record(k,r,refs,c,o,l,'固定f6dc8b5245649479286b9210214177a87e4d2038，本地Git tree/blob固定及文件SHA；静态源码观察，不运行游戏/上游、不改正式源码/资产/TODO。CoFH基础energy/原生事件分发内部未全读，不按基础设施额外计数；无观感或TCP通过主张。','native_damage_refusal_and_receipt');keys.append(k)
add('redstonearsenal-native-charge-shield-refusal-with-break-cue-and-self-hud',[(p+'RedstoneArsenal.java',39,116),w(p+'common/event/RSAEvents.java'),w(p+'util/FluxShieldingHelper.java'),w(p+'common/capability/FluxShieldedEnergyItemWrapper.java'),w(p+'common/capability/IFluxShieldedItem.java'),w(p+'common/capability/CapabilityFluxShielding.java'),w(p+'common/network/PacketHandler.java'),w(p+'common/network/packet/client/FluxShieldingPacket.java'),w(p+'common/network/data/client/FluxShieldingPayload.java'),w(p+'client/renderer/FluxShieldingOverlay.java'),(p+'client/event/RSAClientSetupEvents.java',71,75),(p+'client/event/RSAClientEvents.java',69,79),(p+'init/registries/ModItems.java',81,85)],
 '实际FluxArmor注册cap→原生LivingAttack<=500/非creative spectator/非同时BYPASS_ARMOR和EFFECTS→findShieldedItem只扫描armor且charges>0→已有invulnerableTime则取消，否则成功useCharge设10tick并取消；LivingHurt另成功charge则减500。charge使用gameTime+600写NBT并抽能→shield-break音及target AABB中心红尘→仅自身ServerPlayer S2C charge计数→客户端更新静态charges/HUD；真实8tick本地重算也更新HUD。',
 '护盾拒绝、资源生命周期、受击声光/自HUD同链合并1，不把包/绘制wrapper或4件装备拆分。只要发现有可用charge且原invulnerableTime>0便取消，不消费/不声光；charge用尽后即使10tick尚在find不到也不走此门。LivingHurt减500是部分/完全扣减，不能冒充Boss拒控。Curios循环注释不可当支持。useCharge创意抽能simulate参数来自外部Utils，未读内部不保证所有资源结算。世界gameTime写NBT无维度代际校验。仅自身HUD不是目标头顶灰字；packet仅两个int，无范围夹取/世界清理/目标UUID。最大值下降或充值时missing差变小触发recharge声，不等于拒绝声；本地8tick和包都写static，静态不能证明所有变化先后。Overlay随hideGui/survivalElements隐藏，右侧高度避让；无实机结论。',
 'Boss文字、微光、嗡声应从明确拒控生产点并受同一逐目标节流；普通伤害CD静默取消/自身护盾HUD不能替代。跨世界目标生命周期与收到包时边界需明确。')
add('redstonearsenal-native-trident-plunge-hit-dependent-fall-refusal',[(p+'common/event/RSAEvents.java',55,83),(p+'common/event/RSAEvents.java',85,98),(p+'common/item/FluxTridentItem.java',220,259)],
 '真实LivingFall Player+实际手持FluxTrident+autoSpinAttack→完整plungeAttack：fallDistance>max、empowered且useEnergy成功；client粒子后直接true，server枚举范围实体hurt OR为hit并按hit播放TRIDENT_RETURN或HIT_GROUND→事件按true停止spin并cancel，否则设倍率.4。FlyableFall同调用但不重复计数，真实主手换走清spin。',
 '一个独立条件摔落最终结算门1。服务端至少一目标hurt true才完全取消；没有目标/全false则.4减伤，hurt false只参与hit聚合不能识别Boss拒控。client只要前门通过就true，而server实际命中决定，不把client动画当权威成功。雷暴引雷与临时雷抗在最终hit前可执行；未取消不等于无附带效果。声音不是目标免疫回执，stopSpin只作用玩家当前spin不冻结Boss。外部useEnergy/empowered实现未补全，明确不宣称能量事务完整性；就本地native final gate观察。',
 '真正的免疫语义要在被拒绝控制的裁决点生产，不能从聚合hurt bool或粒子/音效推断；客户端预测与服务端结果应分开。')
f=O/'semantic-dedup.json';x=json.loads(f.read_text());x['groups'].append({'family':'redstonearsenal-native-batch40','credited_chains':keys,'rationale':'护盾attack/hurt/charge/packet/selfHUD同家族合并1；原生旋转三叉戟摔落前置独立1；常量、音色、4装备、包装与客户端重复入口0额外。'});f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');verify()
