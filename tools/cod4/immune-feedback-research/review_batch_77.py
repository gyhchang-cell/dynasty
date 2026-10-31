"""Native teleport-qualified immunity; no per-phase/packet/particle extra credits."""
from ledger import B,O,record,verify
import json
r='BobMowzie/MowziesMobs-Public';p='src/main/java/com/bobmowzie/mowziesmobs/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='mowzie-native-crane-teleport-qualified-invulnerability-versus-ignition'
record(k,r,[w('server/entity/umvuthana/EntityUmvuthanaCrane.java'),f('server/entity/umvuthana/EntityUmvuthana.java',632,667),f('server/entity/umvuthana/EntityUmvuthana.java',722,724),f('server/entity/umvuthana/EntityUmvuthana.java',956,1053),w('server/entity/umvuthana/MaskType.java'),f('server/entity/EntityHandler.java',59,59),f('server/ServerEventHandler.java',148,188),w('server/capability/AbilityData.java'),f('server/ability/AbilityHandler.java',71,81),f('server/ability/Ability.java',58,65),f('server/ability/Ability.java',78,98),f('server/ability/Ability.java',108,124),f('server/ability/Ability.java',129,143),f('server/ability/Ability.java',179,181),f('server/ability/Ability.java',215,218),w('server/message/MessageUseAbility.java'),f('server/message/NetworkHandler.java',29,52)],
 '实际注册Crane factory→registerGoals安装TeleportToSafeSpotGoal，active且治疗目标过近/尚未尝试时找50候选位置，碰撞/区块/邻近Boss等逐渐放宽。start先标hasTriedOrSucceededTeleport=true再sendAbilityMessage；server查实例canUse→activateAbility.tryAbility/start，再tracking+self S2C当前entityId+ability index；client当前world Living直接索引能力表激活。EntityTick.Post→AbilityData.tick→Ability.tickUsing，传送技能startup7/active7/recovery13但section切换按ticksInSection>duration；active逐步teleport且endSection落最终点。原生isInvulnerableTo在inactive或Teleport能力ticksInUse<=16或标记false时拒伤，FELL_OUT_OF_WORLD及timeUntilDeath==0保留例外。',
 '一个传送过程具有明确受击与点燃不同例外的最终免伤位点1，非同名Boss/三个阶段/光效拆数。igniteForTicks相同条件直接return但没有void/timeUntilDeath例外；因此受击资格和点燃资格不可共用一种失败回执。FAITH mask.canBlock=false，不误归FURY方向盾。findTeleportLocation失败到第4次可置true，且本类该标记初值true、所见所有赋值也仅true：不能声称false分支已有原生进入来源。start先置true而ability.canUse可失败，不能据寻路启动推断真实传送。技能声音仅ticks2/16，粒子ticks4/5/18，没有每次拒伤声/灰字；是技能状态启动反馈。',
 'Boss拒控灰字必须在真实被拒的控制生产点生成，不能把传送状态声或hurt(false)误当每次Boss免控确认。不同控制类型可有不同例外；包校验目标身份/能力类型/索引/过期，不能裸索引当前实体表。',
 '固定版本，完整Crane类、完整Teleport技能及关键native producer/ability lifecycle/receiver方法已读；native普通受击由super继续处理，未读Minecraft该版本全hurt内部，不声称客户端画面复现。没有Boss灰字原生实现，不把普通实体自动纳入本项目灰字要求。不制作粒子资产/模型。false标记无生产点及新追踪重同步未确认，保留限制。','native_phase_qualified_damage_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'mowzie-batch77-teleport-qualified-refusal','credited_chains':[k],'rationale':'同一传送期最终拒伤/点燃策略合并1；技能S2C与已读其他Mowzie能力复用0，不因动画阶段/粒子/实体名追加。不同于方向弱点窗，资格由原生能力生命周期并有死亡期限例外。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
