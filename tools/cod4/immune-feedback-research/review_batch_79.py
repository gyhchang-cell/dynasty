"""Actual Ender Ground final teleport denial, not another spell-name credit."""
from ledger import B,O,record,verify
import json
r='Polarice3/Goety-2';p='src/main/java/com/Polarice3/Goety/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='goety-native-ender-ground-final-teleport-denial-command-exceptions'
record(k,r,[f('common/effects/GoetyEffects.java',163,164),f('common/effects/brew/BrewEffects.java',107,107),f('common/effects/brew/BrewEffects.java',220,230),f('common/effects/brew/BrewEffects.java',250,252),w('common/effects/brew/PotionBrewEffect.java'),f('common/blocks/entities/BrewCauldronBlockEntity.java',756,845),f('utils/BrewUtils.java',210,232),f('common/items/brew/BrewItem.java',44,83),f('common/items/brew/BrewItem.java',119,121),f('common/items/ModItems.java',169,172),f('common/events/PotionEvents.java',97,98),f('common/events/PotionEvents.java',823,831),f('mixin/LivingEntityMixin.java',100,105),('src/main/resources/goety.mixins.json',1,len((B/'sources'/r.replace('/','__')/'src/main/resources/goety.mixins.json').read_text().splitlines())),w('common/magic/spells/void_spells/BanishSpell.java')],
 '实际ENDER_GROUND注册GoetyBaseEffect；珍珠对应PotionBrewEffect，getBrew完整方法把该wrapper转成MobEffectInstance并setCustomEffects写CustomPotionEffects；真实BrewItem.use→finishUsingItem服务端addEffect，返回未检查。已启用LivingEntityMixin在原生randomTeleport HEAD有状态直接return false；实际Forge PotionEvents.enderTeleport又取消非TeleportCommand/SpreadPlayersCommand的EntityTeleportEvent。实际Banish.conditionsMet先发EnderEntity事件会被该subscriber否决；若直接进入touchResult则每次尝试先stopRiding，再randomTeleport由Mixin拒绝。',
 '一个对原生移动操作的最终拒绝位点1，两个入口同一EnderGround控制策略合并；不同于既有Applicable能否挂入状态、Banish施法前目标资格、Wight传送成功后藏身免伤，不是把相同spell换名计数。事件入口命令有例外，而randomTeleport Mixin本身没有命令/伤害/来源例外；不能据事件白名单推断任何底层调用都获准。原生Banish成功才播teleport声音和gameEvent，拒绝无明确灰字或嗡声。单独看touchResult全失败仍可能已解骑乘；正常conditionsMet会先拒绝，不能未经原生序列验证宣称实际已经发生副作用。',
 'Boss控制拒绝应在具体原生位点出明确原因，预检和执行期都要一致，但一次尝试不重复产文字。判定拒绝要发生在stopRiding/速度/位置等副作用之前；不拿传送成功声或无伤结果替代真正免控回执。',
 '固定提交，两个最终gate、完整Banish/药水原生使用方法及getBrew和序列化方法全文已读；大注册容器仅直接注册位置作为支持0，未把全酿造任务/取得过程宣称已验。BrewItem.finishUsingItem与wrapper为本链上下文，不额外信用；未运行游戏/原生Minecraft传送内部/像素和声音，不证明管理员命令所有底层实现。普通体质不新增灰字。','native_teleport_control_refusal')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'goety-batch79-enderground-final-operation','credited_chains':[k],'rationale':'状态最终取消原生传送的独立操作位点；事件与Mixin两入口合并1，原已研究Applicable状态拒绝和Banish施法前资格不重记，附属酿造/包装0。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
