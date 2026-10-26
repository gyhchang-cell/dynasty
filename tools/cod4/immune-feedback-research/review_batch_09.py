from ledger import record,verify
p='Xplat/src/main/java/vazkii/botania/';f=p+'common/entity/GaiaGuardianEntity.java'
record('botania-gaia-trueplayer-authority-and-phase-timer','VazkiiMods/Botania',[(f,435,470),(f,359,375),(f,392,413),(f,202,283),(f,568,588),(f,745,892),(p+'common/helper/PlayerHelper.java',40,58),(p+'common/helper/VecHelper.java',23,25)],
 '完整hurt/actuallyHurt/getDamageAfterArmorAbsorb→source.owner必须Player→PlayerHelper.isTruePlayer完整类/名称过滤→专有INVUL_TIME必须为0→cap32再super。完整spawn主方法设置160tick/health1、aiStep原生逐tick生产/递减无敌计时、save读回与同步getter/setter已读；玩家范围辅助读到实际查询。本条研究Boss攻击者资格与阶段计时权威，不按玩家数、阶段、helper或平台拆分。',
 'source.getEntity而非directEntity用于准入，玩家投射物可通过owner准入；非玩家/假玩家或计时非零直接false，不表示所有减伤都是免疫。isTruePlayer只是可配置fakePlayerClass及名称正则过滤，不是证明真人输入（自动化玩家仍不能称真人2人）。召唤与低血召怪期计时不同于原版invulnerableTime；accepted actuallyHurt设置原版至少20tick并安排移动/4tick后传送。hurt拒绝分支没有独立免疫浮字、音效或每目标文字节流。aiStep回血直接setHealth不同于heal覆写门控。',
 'Boss语义需携带真正拒绝原因，不能把非玩家攻击、阶段无敌、32伤害上限和普通体质合成一类。研究玩家身份/来源归属与零血差拒绝的边界；不由此引入新真人验证或普通玩家灰字门槛。',
 '完整读受伤决定方法、专用计时主要生产方法及所列助手；spawn/checkPylons/checkArena的建筑判定内部、完整战斗攻击/召怪/粒子渲染未逐链认证，不计这些辅助功能。原版super伤害与同步止于平台契约；未运行、未判断Boss画面。','immunity_rejection_semantics')
verify()
