"""Undergarden native first-hit rearm, difficulty denial and ordered combat result policy."""
from ledger import B,O,record,verify
import json
r='Quek04/The-Undergarden';p='src/main/java/quek/undergarden/'
def f(s,a,b):return p+s,a,b
def w(s):return f(s,1,len((B/'sources'/r.replace('/','__')/(p+s)).read_text().splitlines()))
def res(s):return s,1,len((B/'sources'/r.replace('/','__')/s).read_text().splitlines())
common=[w('Undergarden.java'),f('registry/UGEntityTypes.java',106,139)]
keys=[]
def add(k,refs,chain,obs,lesson,limits,cat):
 record(k,r,common+refs,chain,obs,lesson,limits,cat);keys.append(k)
add('undergarden-native-first-positive-hit-refusal-with-los-and-idle-qualified-rearm',[
 f('registry/UGEntityTypes.java',88,88),w('entity/animal/MysteriousPot.java')],
 '原生注册MysteriousPot并自身registerGoals装HideAgainGoal；hurtServer非bypass且未active且amount>0时按directsource方位取整90度转向、jump、active同步true、hideCooldown200并false。active或bypass走原生superhurt；weapon BREAKS_DECORATED_POTS可使amount翻倍。tick减cooldown；HideAgainGoal须cooldown<=0&&active&&navigationdone，16范围combat玩家为空或所有玩家无LOS才start snap到blockPos且active=false重新装填。ACTIVE同步更新refreshDimensions，未active时immobile和可碰撞。',
 '有效计1的是可重复装填的最终伤害接纳策略：第一次正amount命中消耗隐藏状态而拒伤，随后暴露，冷却+导航+目标LOS资格再隐藏。与Frostmaw仅direct arrow恒拒+苏醒、Iron尸体幂等复活替换实体不同，不因awake同词合并；转向四方向/维度/同步包装不拆。hideCooldown未保存，save只active；重载不能声称保持200租期。非正amount未active仍super，不把所有隐藏hurt都称免疫。无灰字或拒控声。',
 '拒绝理由应在实际接纳门生成；触发姿态动作仍可能此次无伤，冷却到期不等于可再触发，还要实测状态资格。Boss字不应靠hurt=false猜测。',
 '完整实体含Goal/储存/同步和实际注册已读；未读取像素/模型，原生Jump可视性未验，不把此策略直接抄入产品。','native_state_consumption_rearm_refusal')
add('undergarden-native-peaceful-difficulty-denial-with-creative-bypass-and-persistence-policy',[
 f('registry/UGEntityTypes.java',92,92),w('entity/monster/boss/ForgottenGuardian.java'),res('src/generated/resources/data/minecraft/tags/entity_type/deflects_projectiles.json')],
 '真实ForgottenGuardian注册和完整实体：hurtServer在ServerLevel difficulty PEACEFUL且非source.isCreativePlayer且非BYPASSES_INVULNERABILITY时直接false，否则super。checkDespawn仅EventHooks.checkMobDespawn成功早退，其他只noActionTime=0；原生ambient/look/immobile有各自难度政策，不以实体无动作猜拒绝。它另行deflection按实际DEFLECTS_PROJECTILES tag返回自有声音+原生REVERSE，canBeAffected恒false，均已完整读。',
 '仅difficulty×creative/bypass最终拒伤producer计1；类内portal/effects/流体/击退静态免疫、tag项、deflection音色/原版REVERSE及普通攻击byte4均作同源支持0，绝不把攻击动画/音效当免疫反馈。register.notInPeaceful不代替hurt门；当前类checkDespawn覆盖已见，但未读当前版本EntityType与EventHooks，不能声称和平必定可以自然生成或永不被其他插件删除。',
 'Boss拒控需独立于难度/creative来源的伤害豁免；服务端明确最终条件并决定回执类型，不能仅复用伤害false作Boss控制结论。',
 '完整252行实体、注册和实际生成tag已读；没有游戏/真实声画/默认世界生成验证。该参考不扩展本项目普通体质灰字要求。','native_difficulty_qualified_refusal')
add('undergarden-native-ordered-hit-effects-first-success-feedback-versus-ammo-refund',[
 f('registry/UGEntityTypes.java',51,51),f('registry/UGItems.java',77,77),f('registry/UGItems.java',140,140),f('registry/UGItems.java',214,215),f('registry/UGItems.java',232,243),f('registry/UGItems.java',256,258),f('registry/UGDataComponents.java',20,20),w('item/tool/SlingshotItem.java'),w('component/SlingshotAmmo.java'),w('registry/custom/UGSlingshotAmmoSettings.java'),w('registry/custom/UGHitEffects.java'),w('entity/projectile/slingshot/SlingshotProjectile.java'),w('entity/projectile/slingshot/effect/HitEffect.java'),w('entity/projectile/slingshot/effect/entity/AddMobEffectHitEffect.java'),w('entity/projectile/slingshot/effect/entity/VelocityBasedDamageHitEffect.java'),w('entity/projectile/slingshot/effect/entity/HealHitEffect.java'),w('entity/projectile/slingshot/effect/entity/EquipItemHitEffect.java'),w('entity/projectile/slingshot/effect/block/PlaceBlockHitEffect.java'),res('src/generated/resources/data/undergarden/tags/entity_type/immune_to_gooey_effect.json')],
 '真实物品component注册DEPTHROCK_PEBBLE/GOO_BALL/GRONGLET；Slingshot原生use→releaseUsing服务器创建带ammoStack投射物，消耗弹药与耐久。onHitEntity或最终block碰撞→finishHit按ammo.hitEffects顺序apply，首个true即break并可播放hitSound/broadcast byte3碎裂；全部false时owner非creative玩家且dropAsItem才spawnItem，最后discard。Pebble的apply直接返回hurtServer结果；Goo先PlaceBlock、再非immuneEntities的AddEffect、再Scintling Heal。实际immune_to_gooey只有scintling，因此它绕过Goo状态进入Heal。',
 '整条“原生命中策略结果→停止后续效果/成功碎裂声vs失败退款”独立家族1。AddMobEffectHitEffect忽略living.addEffect返回值仍true，故目标原生canBeAffected拒绝也可能成功碎裂，不是明确IMMUNE；Heal忽略最终血量变化也true；Place忽略setBlock返回bool。Pebble hurt=false可能免疫/帧保护等，不把退款称Boss免控。只有Gronglet dropAsItem默认true，Goo/Pebble默认false，不能声称所有失败都会退款；Gronglet装备和放块非战斗功能辅助0。codec/弹药类别/粒子/音色/效果包装不多计。',
 '应从Boss最终控制决策携带明确reason，不通过通用效果bool或是否播放碎裂声反推免疫；链中一次成功会遮住后续效果，验收必须追完整选择顺序和目标资格。',
 '完整Item/Projectile/component/各调用的关键HitEffect及实际默认component/tag/registry已读；ExplodeHitEffect主体未读，本条不计或声称BLISTERBERRY爆炸拒伤。底层网络component/原版粒子未运行，不证明灰字或两端画面。','native_combat_result_feedback_arbitration')
d=json.loads((O/'semantic-dedup.json').read_text());d['groups'].append({'family':'undergarden-batch93-final-native-policies','credited_chains':keys,'rationale':'Repeatable first-hit state consumption with LOS-qualified rearm differs from permanent arrow rejection or corpse replacement. Difficulty/creative qualified final damage gate independent; ordered real combat effect settlement controls sound/break vs refund one family. Portal/static effect lists/reverse and codecs/wrappers zero extra. No old asset/guard credit.'});(O/'semantic-dedup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');verify()
