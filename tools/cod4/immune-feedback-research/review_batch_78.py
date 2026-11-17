"""Actual pre-explosion denial and its native audiovisual receipt, one credit."""
from ledger import B,O,record,verify
import json
r='DaedalusGame/EmbersRekindled';p='src/main/java/teamroots/embers/'
def f(s,a,b):return p+s,a,b
def w(s):
 rel=p+s
 return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='embers-native-whole-explosion-absorption-mercy-window-and-fixed-coordinate-receipt'
record(k,r,[w('item/bauble/ItemExplosionCharm.java'),w('item/bauble/BaublesUtil.java'),w('compat/BaublesIntegration.java'),f('Embers.java',64,73),f('proxy/CommonProxy.java',42,48),f('RegistryManager.java',544,547),f('ConfigManager.java',92,94),w('network/PacketHandler.java'),w('network/message/MessageExplosionCharmFX.java'),f('particle/ParticleUtil.java',35,37),f('particle/ParticleUtil.java',55,57),f('proxy/ClientProxy.java',134,139),f('proxy/ClientProxy.java',174,179),w('particle/ParticleGlow.java'),w('particle/ParticleSmoke.java'),w('particle/ParticleRenderer.java'),f('EventManager.java',505,525),f('EventManager.java',769,788)],
 '实际preInit初始化网络并注册物品；Baubles开关且依赖已加载时registerAll实例化ExplosionCharm，其constructor把this注册ForgeBus。原生ExplosionEvent.Start服务端取爆点固定±5整数AABB内entities，Baubles CHARM实际slot6同item且!cooldown或mercy，播放absorb声、sendToAll爆点及实体半高固定位置包、cancel整个爆炸；第一次另recharge声并设100tick CD/5tick mercy。ServerTick.START对WeakHashMap每实体递减。实际CLIENT注册包→onMessage先capture当前world、schedule40次glow/smoke→ClientProxy按设置采样→ParticleRenderer排队，原生ClientTick更新/RenderWorldLast绘制。',
 '一个在爆炸计算前取消整个world事件并发吸收回执的独立实现1，不是单受害者LivingDamage拒伤。固定扫描盒并非爆炸真实半径/视线判定；没有break或isCanceled检查，多名合格佩戴者可各发包、各进CD。5tick宽限期内重复爆炸仍发absorb声和粒子，CD只限制重新激活不限制提示频率；两个WeakHashMap按entity对象隔离且不删到0/负数条目，非世界时间deadline/持久化。sendToAll无维度/range，六double无UUID/目标ID/finite/时序，任务前捕获world无null/换world验证。粒子飞向包内静态半高位置，不随实体移动。glow实际寿命入参*0.5并初速度*2，另随机加age；烟用完整寿命。renderer按renderThroughBlocks(false)分normal/additive，shouldDisableDepth(true)在此renderer不被读取；不能因那个方法名就称穿墙。',
 'Boss反馈应在原生拒控判定后明确生产一次，并把实体资格CD与文字音效节流分开；按真实目标身份/维度/期限校验，过期或换世界不复用旧world，避免向全服无条件广播固定坐标。吸收整次world事件和目标免控语义不同，不把取消爆炸直接移植成Boss免疫。',
 '固定版本，事件producer/冷却tick/实际S2C编解码消费者/粒子实际绘制和nativehook完整方法已读，注册大容器只引用直接接入位置，其余物品注册不计研究。粒子集合未见world unload清空，不声称永不残留；未运行上游/游戏，不证明画面和声资源适合本项目。无资产制作，Baubles可选功能条件记录，不扩普通玩家灰字。','native_whole_explosion_refusal_receipt')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'embers-batch78-whole-explosion-absorption','credited_chains':[k],'rationale':'原生world Explosion.Start整次拒绝、entity弱引用CD+mercy及真实S2C固定吸收回执合并1；glow/smoke/codec/两个声音/slot包装0额外；不同于单目标来源标签无伤。'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
