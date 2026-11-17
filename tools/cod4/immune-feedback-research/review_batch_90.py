"""Scylla native accumulated parry refusal and actual empty particle consumer, one site."""
from ledger import B,O,record,verify
import json
r='lender544/new1.20.1';p='src/main/java/com/github/L_Ender/cataclysm/';s=p+'entity/InternalAnimationMonster/IABossMonsters/Scylla/Scylla_Entity.java'
def w(q):
 rel=p+q;return rel,1,len((B/'sources'/r.replace('/','__')/rel).read_text().splitlines())
k='cataclysm-scylla-native-success-fed-parry-threshold-refusal-and-empty-flash-consumer'
record(k,r,[(s,114,114),(s,141,144),(s,164,357),(s,377,431),(s,451,463),(s,560,571),(s,598,604),(s,771,777),(s,871,907),(s,2006,2034),(s,2251,2429),(p+'init/ModEntities.java',647,651),(p+'ClientProxy.java',96,96),w('entity/InternalAnimationMonster/AI/InternalStateGoal.java'),w('client/particle/ParryParticle.java'),w('client/particle/Options/ParryParticleOptions.java')],
 '真实SCYLLA实体注册，registerGoals挂HorizontalSwingGoal与parry state19。hurt对非bypass来源、非NoAI且source position正面，CanParryState须state1/2且attackTicks>35、3>51、4>50。累计parryCount>=18则直接置25/播原版铁门声/广播byte11并returnfalse；低于18则概率(count+1)*5且cooldown<=0成功同样处理。已在state19且tick2..10也可拒伤发事件。只有super.hurt返回true的正面攻击才增加count，projectile+2、其他+1。swing tick看到count>=25停止→stop切state19；其15tick goal结束count清0、cooldown100。tick倒计时。',
 '独立原生成功受击历史→累积概率/保证拒伤与事件生产1，不按phase/箭与近战/既有同链方法拆分。最大count保证分支不查cooldown，state19短窗口也不查；不能称全局冷却防刷。实际客户端handle11→parryParticle按当前实体姿态快照生成12个PARRY；注册ParryFactory，lifetime9..11/落地移除。然而完整ParryParticle.render覆写里super.render和全部trail提交均注释，方法实际无绘制语句，不能据事件/粒子生成声称闪光可见！原生声播放在拒绝前，颜色整数未归一也不是本次视觉通过依据。state21/22/sleep静默拒伤并已有phase family0，非全部Boss控制免疫。',
 '必须检验最终消费者确实提交文字/微光，不能把广播成功或粒子对象存在当画面。Boss免控事件节流应覆盖保证分支和连续状态窗口，并以目标拒绝事实为准，避免单一概率分支有cooldown却声称不刷屏。',
 '完整hurt/资格/consumer/particle/options、对应goal小方法及swing完整类、注册和实际tick已读；aiStep巨大完整方法本次输出有截断，不以其未读部分为通过依据。空render为该固定上游源码静态事实，不是本项目产品bug结论。无游戏/像素/听验/正式修复；资产仍专业对话。','native_history_conditioned_refusal_receipt')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'scylla-accumulated-parry-final-refusal','credited_chains':[k],'rationale':'Success-fed threshold/probability plus action/continuous-window receipt policy differs from static frontal shield. Byte11/wrappers/particle variants/empty rendering zero extra. Other seven inspected Boss hurt policies merged/support zero.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
