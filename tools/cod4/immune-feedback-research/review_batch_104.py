"""Native capture escape budget and repair-carrier-dependent armor admission."""
from ledger import B,O,record,verify
import json
keys=[]
def project(r,p):
 def f(s,a,b):return p+s,a,b
 def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
 return f,w
r='team-abnormals/upgrade-aquatic';f,w=project(r,'src/main/java/com/teamabnormals/upgrade_aquatic/')
k='upgradeaquatic-native-prehurt-stun-budget-releases-captive-without-health-success';keys.append(k)
record(k,r,[w('common/entity/monster/Thrasher.java'),w('common/entity/monster/GreatThrasher.java'),w('common/entity/ai/goal/thrasher/ThrasherGrabGoal.java'),w('common/entity/ai/goal/thrasher/ThrasherThrashGoal.java'),w('core/UpgradeAquatic.java'),w('core/registry/UAPlayableEndimations.java'),f('core/registry/UAEntityTypes.java',27,44),f('client/model/ThrasherModel.java',76,98)],
 '固定214a42，UpgradeAquatic注册UAEntityTypes，Thrasher注册Grab/Thrash两真实Goal。Grab先canPerformAttack再沿视向rayTrace判block，非block调用startRiding(force=true)不读结果并清target；Thrash在非stun且有乘客时启动，设置2或3次脱困hit预算并播55tick动画。hurt在super之前对<=8格Living来源按amount/难度概率扣HITS_TILL_STUN；synced字段更新回调tickCount>10且预算0设置40..69tick stun。原生tick server有stun即ejectPassengers并递减，Grab/Thrash和MoveController同时拒stun资格。',
 '完整家族计1：以伤害尝试强度概率消费的脱困预算，区别Endergetic累计实际HP损失并加跨抓取者重抓窗口。即使super.hurt返回false，预算和前置受击动画已可发生，不能据其断言真实掉血。setStunned回调无server guard，client也可随机取时长，本类不等于权威TCP时序已验；NoAI使tick中的释放/减时跳过。Thrash每5tick声与hurt不读成败；每ticksetShiftKeyDown(false)只阻当前输入状态，非所有挂载事件禁令。预算未存NBT，StunnedTicks有存；重新每轮Thrash重设预算。Great仅阈值/尺寸差异0。',
 'Boss拒控结果应由server明确裁决后播放，不能拿受击动画、局部hit预算变动或客户端随机stun当免疫语义。控制释放/动作锁与文字反馈各自核对真实边界，普通体质不追加灰字。',
 'Thrasher整篇及两Goal、Great全文已读；setupAnim全文只含尾鳍/头姿态，未见stunAnimation消费，不能声称眩晕躯体可辨。Blueprint NetworkUtil/EntityUtil底层未读，外部辅助0；本条只证明本模组原生裁决与物理释放，不声称其网络动画/射线精确实现或视觉通过。','native_capture_escape_attempt_budget')
r='DrZhark/mocreaturesdev';f,w=project(r,'src/drzhark/mocreatures/')
k='mocreatures-native-repair-rock-presence-opens-armored-core-before-damage-settlement';keys.append(k)
record(k,r,[f('entity/monster/MoCEntityGolem.java',55,111),f('entity/monster/MoCEntityGolem.java',114,251),f('entity/monster/MoCEntityGolem.java',259,326),f('entity/monster/MoCEntityGolem.java',478,575),f('entity/monster/MoCEntityGolem.java',669,747),f('entity/monster/MoCEntityGolem.java',773,828),f('entity/monster/MoCEntityGolem.java',935,958),f('entity/item/MoCEntityThrowableRock.java',151,330),f('entity/item/MoCEntityThrowableRock.java',366,375),f('MoCreatures.java',387,467),f('MoCreatures.java',503,524),f('MoCreatures.java',1357,1360),f('network/MoCServerPacketHandler.java',541,562),f('client/network/MoCClientPacketHandler.java',32,259)],
 '固定旧版6d3be813，@Init load→AddEntities真实注册Golem/TRock。构造23块身体槽，server onLivingUpdate激活/补缺，acquireRock生成behavior2随行石，Rock.native onEntityUpdate接近master后receiveRock回血+填缺槽。最终attackEntityFrom在非dying且非state1：胸口四块未全缺、openChest false时仅随机破身体块/播阻挡声、设仇恨，return true不走父HP伤害；openChest以缺任意槽且2格AABB内任意TRock为true，未核石头owner或behavior，故外来石也可开准入。通过后伤害cap5才super。',
 '计1：真实世界修复载体接近反而开放核心伤害的空间准入，并非把有限盾资源换实体名。被挡返回true仍无parentHP变化；部分破槽可能drop物品/声音，不能称纹丝不动。state4直接false，state1也可returntrue但不伤，这两通用phase仅支持0。破块随机偏末端、槽4不可破，任意块缺失非仅胸口决定openChest前置。saveGolemCube发送实体id+slot/value到当前维度全部客户端，收包按当前world同ID/class再写槽，不验slot范围/UUID/维度代际，只有IOException catch。',
 'Boss灰字必须来自实际控制拒绝语义，不能从true/false或未掉HP机械映射；目标定位包应含一致身份/维度并校验索引或枚举，观察者范围及缺失实体处理不能依赖旧式裸ID。此例身体槽/石头构建不移植为新资产。',
 '完整引用各关键方法已读，包括修复原生tick和接收全文方法；非整篇1280行Golem全文，generateBlock/translateOre材质映射不当新研究。原旧版整数伤害/dataWatcher/Packet250 API不可直接搬到本项目；网络线程/模型实际提交/声音听感未运行未验。本条研究最终gameplay准入及拒伤回执，S2C包装0，不制作身体模型。','native_repair_carrier_spatial_admission')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch104-captive-attempt-escape-and-repair-carrier-core','credited_chains':keys,'rationale':'Capture escape uses pre-parent incoming-hit attempt budget, not actual HP loss/regrab timer. Golem core admission observes nearby physical repair carriers and missing body topology, not a simple phase bit/resource shield reskin. All Goal/packet/geometry wrappers zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
