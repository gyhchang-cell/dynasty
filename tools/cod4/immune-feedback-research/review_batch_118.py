"""Main review of four independent Herschel008 sites; research only, no game code."""
import json,hashlib
from ledger import B,O,record,verify
h=O/'helpers/herschel-immune/batch-008.json';draft=json.loads(h.read_text());decisions=[];added=[]
r='ZsoltMolnarrr/SpellEngine';p='common/src/main/java/net/spell_engine/'
def f(s,a,z):return p+s,a,z
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
shared=[f('internals/impact/SpellImpacts.java',200,887),f('internals/delivery/SpellDelivery.java',127,301),f('internals/SpellTriggers.java',166,173),f('internals/SpellTriggers.java',255,291),w('utils/WorldScheduler.java'),w('mixin/ServerWorldMixin.java'),w('fx/ModelEffectHelper.java'),w('utils/SoundHelper.java'),f('fx/ParticleHelper.java',35,45),f('fx/ParticleHelper.java',102,158)]
def add(helper,key,repo,refs,chain,obs,lesson,limits,cat):
 record(key,repo,refs,chain,obs,lesson,limits,cat);added.append(key);decisions.append({'helper_id':helper,'main_id':key,'research_credit':1,'decision':'promoted after main full containing methods/call chain and semantic review'})
add('herschel-008-04','spellengine-native-shield-contact-receipt-before-durability-and-player-source-filter',r,[w('mixin/entity/LivingEntityEvents.java'),f('SpellEngineMod.java',77,106),f('internals/SpellTriggers.java',106,125),f('internals/SpellTriggers.java',223,233),f('internals/SpellTriggers.java',255,291)],
 '声明的原生LivingEntity.damage→damageShield WrapOperation在original.call之前派发实体格挡事件和玩家格挡事件；SpellEngineMod.init注册SpellTriggers，玩家监听交onShieldBlock，仅source.getAttacker非null才进入服务端fireTriggers，先消费stash后尝试passive即时或排队执行。',
 '计1：原生盾接触点生产的明确格挡回执及玩家消费来源资格。不是damage RETURN为false的推测，不是shield耐久结算成功回执；两个事件包装不另计。传给Args的是durabilityAmount，不是上下文damageAmount。环境来源仍可能派ENTITY事件，但玩家onShieldBlock会提前return；fireTriggers另有客户端早退。与已有EVASION生产/源对象关联、stash尝试扣层和玩家spell额度门语义独立。',
 'Boss应在明确拒控分支生产专用原因回执；尝试、接触、扣耐久、实际伤害分别命名，避免拿无HP变化生成IMMUNE。',
 '全文LivingEntityEvents和init/onShieldBlock/fireTriggers已读；未核查当前原版damage字节码、Mixin启用清单或实际装载，不把注释first当跨版本保证。没有证明配置有SHIELD_BLOCK技能，更无TCP/画面。下游stash与限额沿用已有研究不重计。','native_explicit_contact_receipt_with_source_qualified_consumer')
add('herschel-008-11','spellengine-harmful-velocity-resistance-suppresses-reset-and-positive-impact-receipt',r,shared,
 '真实SpellDelivery.DIRECT→performImpacts→完整performImpact，在通用可攻击/关系/概率/目标条件后，VELOCITY按LOOK或ORIGIN构造水平基向量加世界Y并按法强确定性缩放。HARMFUL且Living才乘1-knockbackResistance；最终lengthSquared>0才PRE、可选清旧速度、addVelocity、velocityModified和success。success尾部声光/模型并排到世界tick TAIL的POST。',
 '计1：敌对位移的最终抗性门在清旧速度等副作用之前。全抗性得到零冲量时不PRE/不reset/不写速度/不success，HELPFUL绕过属性门，非Living不读属性。与Ars strength>0击退同有抗性乘算，但本点新增reset_velocity被抗性同时抑制、帮助性位移分流及显式成功反馈边界，作为完整原生法术位移策略合计1；不把向量几何/同步标志/FX包装拆条。没有Boss tag或状态分类检查，免状态不等于免该位移。',
 '拒控应在清速度、换目标等副作用前决定；不要因状态被拒就假定直接速度也被拒。成功回执只在实际允许分支生成。',
 'performImpact全文275–887、performImpacts、deliver、世界调度和反馈发送完整方法已读。没有外部具体法术配置/原生运行/最终客户端运动证据，不声称移动实测。网络/模型渲染沿用已有研究，不增信用。','native_hostile_velocity_final_resistance_before_reset_and_receipt')
add('herschel-008-12','spellengine-damage-ignored-native-result-still-feedback-and-offset-knockback',r,shared,
 '同一真实DIRECT调用链的DAMAGE分支先PRE、caster.onAttacking，再调用target.damage但不消费boolean。Living恢复knockback multiplier与旧timeUntilRegen，并在context.hasOffset时额外takeKnockback；随后无条件success=true，消费共享success尾部目标粒子/声/模型及targetWasAlive且玩家caster的延迟POST。',
 '计1：独立DAMAGE结算生产的正向回执不依据原生接纳，且拒伤后仍尝试offset位移。区别旧账STATUS的Boss分类门、PRE内部applyDamage重查和AOE最后目标覆盖：此处是单个DAMAGE动作自身丢失hurt结果。不能把success/POST/音效推成HP变化，更不能从damage=false推断免疫原因。takeKnockback仍可能被原生抗性阻止，不能说实际推动。targetWasAlive是动作前取样。恢复timeUntilRegen不在finally；异常后方法可返回已置success，亦不是原生接纳凭据。',
 '正式Boss免疫包必须来自已知拒控理由，不以通用攻击成功FX反推。伤害接纳和控制副作用接纳分别记录；保留尝试FX时不要将它标成命中或免疫。',
 '全文执行和实际目标FX发送、声音/模型helper、POST消费者与世界tick调度已读。没有配置具体攻击技能或实际服务端运行；不报伤害利用已复现，不重复已有FX锚定/TTL研究。','native_damage_result_ignored_with_independent_side_effect_and_feedback')
r='DrZhark/mocreaturesdev';p='src/drzhark/mocreatures/'
refs=[f('entity/passive/MoCEntityTurtle.java',26,46),f('entity/passive/MoCEntityTurtle.java',93,115),f('entity/passive/MoCEntityTurtle.java',127,189),f('entity/passive/MoCEntityTurtle.java',215,307),f('entity/passive/MoCEntityTurtle.java',328,358),f('entity/passive/MoCEntityTurtle.java',462,475),f('entity/MoCEntityAnimal.java',306,333),f('entity/MoCEntityAnimal.java',1863,1885),f('MoCreatures.java',388,399),f('MoCreatures.java',405,405),f('MoCreatures.java',513,519)]
add('herschel-008-14','mocreatures-turtle-threat-los-shell-denial-with-refused-hit-opening-roll',r,refs,
 '实际load→AddEntities注册Turtle，原生server onLivingUpdate在非倒置/未驯服时getBoogey(4)，所选目标有LOS则首次hiss并设hiding watcher22；失去该目标/LOS清hiding。原生attackEntityFrom hiding恒false，其中1/10先flipflop清hiding+倒置watcher23，本击仍拒伤。非hiding调用父伤害后1/3翻倒，不看父bool。',
 '计1：由外部威胁LOS主动入壳、拒绝命中概率解除自身防御并倒置的最终接纳状态机。与Undergarden pot第一次正伤必揭露、200tick/导航/所有玩家LOS才回隐不同：Turtle入壳不由伤害触发且无该CD；当前拒伤并不保证仍受保护，父false也可改变后续姿态。getBoogey遍历覆盖返回最后一个合格实体，不是最近，include排同class并按体宽或高>=0.5。hiss只入壳首次，非每次拒伤回执。',
 'Boss拒控通知应快照本次明确原因，不能等状态变化后再查当前是否免疫；状态进入声音不等于逐击拒控提示。防刷要与防御状态机独立。',
 '完整关键生命周期/交互/伤害方法和父伤害/原生注册已读。attackEntityFrom无服务端guard，两个watcher setter客户端guard已注释，不声称仅服务端抽签；NBT仅保存倒置/名称显示，hiding未保存。未读模型或运行，无画面结论，无灰字。','native_threat_qualified_defense_with_refused_hit_probabilistic_release')
for hid,why in [('herschel-008-10','全文PoisonEffectMixin已读。伤害上限health-1及25tick周期是非致死改写，未形成明确拒控/拒伤原因回执；资源仅转录，作为支持0，不以周期包装凑数。'),('herschel-008-13','原生形态/变形/注册及attackEntityFrom全文已读。狼形按归属玩家当前持物覆写正伤害（空手不改），没有明确拒控/免疫或独立反馈；保留为伤害改写支持0，五金工具不能拆数。'),('herschel-008-15','本轮尚未完成主岗全文原生链复核，继续pending0，不能信用helper建议。')]:decisions.append({'helper_id':hid,'research_credit':0,'decision':why})
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'batch118-main-reviewed-helper008-contact-velocity-result-shell','credited_chains':added,'rationale':'Four distinct final game behavior sites. Shared complete performImpact evidence is not itself counted; only source-qualified shield contact, hostile velocity side-effect admission, DAMAGE false-positive feedback, and threat shell denial transition. Poison/werewolf positive amount rewrites support0; MPS pending0.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
(O/'HERSCHEL-008-REVIEW-PARTIAL.json').write_text(json.dumps({'helper_draft_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),'draft_rows':len(draft['rows']),'draft_not_final_delivery':True,'main_count_before':355,'new_credit':len(added),'decisions':decisions,'untouched_support_rows':'01/02/03/05/06/07/08/09 retain0, no repeated full-review claim','production_changed':False,'game_started':False},ensure_ascii=False,indent=2)+'\n')
verify()
