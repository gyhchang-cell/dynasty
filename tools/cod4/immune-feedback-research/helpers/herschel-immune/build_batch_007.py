"""Local-only helper receipt builder. No upstream execution or master-ledger writes."""
from pathlib import Path
import json,hashlib,re,shutil,importlib.util
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'
LOCAL=ROOT/'tools/cod4/immune-feedback-research/helpers/herschel-immune'
MASTER=ROOT/'docs/cod4/audit-20261022/immune-feedback-research'
I='iron431__irons-spells-n-spellbooks';A='baileyholl__Ars-Nouveau';S='ZsoltMolnarrr__SpellEngine'
BASE={I:ROOT/'tools/cod4/immune-feedback-research/sources'/I,A:ROOT/'tools/cod4/armor-acceptance/.work/research-sources'/A,S:ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources'/S}
# Authored lexical reader from another helper is read-only support, not research credit.
spec=importlib.util.spec_from_file_location('reader',ROOT/'tools/cod4/immune-feedback-research/helpers/halley-immune/inspect_methods.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
sha=lambda x:hashlib.sha256(x).hexdigest()
meta={k:json.loads((v/'source.json').read_text()) for k,v in BASE.items()}
verified={};rows=[]
before={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()}
def evidence(repo,name,method,qualifier=None):
 ps=list(BASE[repo].rglob(name+'.java'));assert len(ps)==1,(name,len(ps));p=ps[0];rel=p.relative_to(BASE[repo]).as_posix();data=p.read_bytes();lines=data.decode().splitlines(keepends=True)
 starts=[i for i,l in enumerate(lines,1) if re.match(r'\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:public|private|protected|default|static)\s',l) and re.search(r'\b'+re.escape(method)+r'\s*\(',l) and (qualifier is None or qualifier in ''.join(lines[i-1:i+8]).split('{',1)[0]) and not l.strip().endswith(';')]
 if method=='__complete_file__':starts=[1]
 assert len(starts)==1,(name,method,qualifier,starts)
 start=starts[0];end=len(lines) if method=='__complete_file__' else reader.end_method(lines,start);excerpt=''.join(lines[start-1:end]);pin=meta[repo];commit=pin.get('commit',pin.get('sha'));blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if repo in (A,S):
  tree=json.loads((BASE[repo]/'tree.json').read_text());assert tree['sha']==commit;assert next(x['sha'] for x in tree['tree'] if x['path']==rel)==blob
  proof='pinned Git tree blob SHA1'
 else:
  entry=next(x for x in pin['files'] if x['path']==rel);assert entry['sha256']==sha(data);proof='pinned archive source.json SHA256 inventory'
  if 'git_blob_sha1' in entry:assert entry['git_blob_sha1']==blob;proof='pinned source inventory SHA256 and Git blob SHA1'
 dest=LOCAL/'sources-batch007'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'unit':'complete_support_resource' if method=='__complete_file__' else 'complete_method','source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-007-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与001–006及当前主账按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
def span(repo,name,start,end,label):
 ref=ev(repo,name,'__complete_file__');lines=ref['excerpt'].splitlines(keepends=True);excerpt=''.join(lines[start-1:end]);ref.update(method=label,lines=[start,end],excerpt=excerpt,excerpt_sha256=sha(excerpt.encode()),normalized_excerpt_sha256=sha(re.sub(r'\s+','',excerpt).encode()));ref['url']=ref['url'].split('#')[0]+f'#L{start}-L{end}';ref['resource_scope']='complete nested declaration or complete registration statement; not a counted method';return ref


add('iron-poison-marked-once-native-long-cast-interruption-refusal',
 'PoisonMobEffect.applyEffectTick HEAD的实际Mixin对ServerPlayer记tickCount；MagicData.popMarkedPoison以当前tick-标记<=1认定一次毒伤并立刻清零。原生onLivingIncomingDamage仅在casting/canBeInterrupted/remaining>0、伤害不在LONG_CAST_IGNORE且pop返回false时cancelCast。canBeInterrupted要求LONG并未戴CONCENTRATION_AMULET；标签datagen含燃烧/凋零/摔落等及可选NeoForge毒伤。',
 '控制拒绝需区分来源标签、装备与一次性事件标记；仅用时间邻近匹配会把第一次相关incoming当毒伤，不是DamageSource对象级关联。免打断不等于免伤。',
 '静态无运行；Poison applyEffectTick标记在HEAD，不证明本次确产生伤害；标签门短路时不pop，可能留下窗口。默认timestamp=0，pop只检查差<=1未排负值。仅服务端玩家有标记，Boss/普通Mob不套用同一语义。Mixin资源未新取/未运行，Java链已固定。',
 '原生PoisonMobEffect.applyEffectTick→MobEffectMixin.markPoisoned→MagicData.timestamp→原生LivingIncomingDamageEvent→ServerPlayerEvents.onLivingIncomingDamage→popMarkedPoison拒绝中断或Utils.serverSideCancelCast→既有OnCastFinished明确cancelled回执',
 ev(I,'MagicData','popMarkedPoison'),ev(I,'MobEffectMixin','__complete_file__'),ev(I,'MagicData','markPoisoned'),ev(I,'ServerPlayerEvents','onLivingIncomingDamage'),ev(I,'AbstractSpell','canBeInterrupted'),ev(I,'DamageTypeTagGenerator','addTags'),ev(I,'Utils','serverSideCancelCast','boolean triggerCooldown'),ev(I,'CancelCastPacket','cancelCast'),ev(I,'AbstractSpell','onServerCastComplete'),
 dedup='001 incoming全文的冰墓/火戒分支与005反制取消回执为共享支持；新决策是LONG_CAST_IGNORE/护符/一次性毒伤标记拒绝中断，不把既有packet或每种来源再计。')
entityMixin='src/main/java/com/hollingsworth/arsnouveau/common/mixin/EntityMixin'
add('ars-soaked-native-positive-fire-tick-denial-versus-fire-damage-immunity',
 '已注册ConjureWater.onResolveEntity立即clearFire，再在Living且durationMultiplier>0时赋SOAKED。EntityMixin原生setRemainingFireTicks HEAD仅当Living且isWet（SOAKED或Bubble乘客）且新ticks>0时clearFire并cancel；原生isInWaterOrRain RETURN也把湿目标置true。不是LivingIncomingDamage取消，对直接火伤并未在此拒绝。',
 '具体点燃状态写入门可明确表示拒绝点燃，不能把“未着火”泛化成火伤免疫；控制状态来源和伤害来源需分别记录。',
 '只读Java未验证Mixin运行/资源启用。SoakedEffect有applyEffectTick清火，但未覆写shouldApplyEffectTickThisTick，故不据该方法存在声称持续tick必调用；真正已找到的是原生fire-ticks写入门和立即clearFire。保护只在状态/乘骑存在时判定，无另加持久免疫。',
 'APIRegistry注册EffectConjureWater→SpellResolver/EffectConjureWater.onResolveEntity→IPotionEffect.applyPotion→注册SOAKED；原生Entity.setRemainingFireTicks→EntityMixin.isWet取消正ticks；原生isInWaterOrRain读取同门',
 ev(A,entityMixin,'ars_nouveau$setSecondsOnFire'),ev(A,entityMixin,'isWet'),ev(A,entityMixin,'ars_nouveau$isInWaterOrRain'),ev(A,'EffectConjureWater','onResolveEntity'),ev(A,'IPotionEffect','__complete_file__'),ev(A,'SoakedEffect','__complete_file__'),span(A,'ModPotions',51,51,'SOAKED_registration'),span(A,'APIRegistry',94,94,'ConjureWater_registration'),ev(A,'SpellResolver','onResolveEffect'),ev(A,'SpellResolver','resolveAllEffects'),
 dedup='与Iron fireward incoming取消伤害不同：这里明确只拒绝原生点燃状态写入，并改变wet查询；与Bubble乘骑捕获同门共享但不是重复乘骑解除/redirect。')
add('ars-soaked-observer-effect-sync-with-local-player-exclusion-and-lossy-amplifier',
 'PotionEffectTagProvider实际TO_SYNC仅加入SOAKED。onPotionAdd服务端在Wixie时长修正后发entity int/effect registry ID/duration；Remove与Expired共用-1发同包。PotionSyncPacket客户端查当前mc.level整数ID且Living、并排除本地proxy player；正时长addEffect构造固定amplifier0且不显粒子/图标，其他值remove。Networking确注册S2C。',
 '面向旁观者的控制状态反馈要区分本地玩家已有原生同步与远端副本；接收实体及状态注册表校验有用，但有状态包不代表原伤害接纳，丢失amplifier不能当全量状态一致。',
 '无TCP/实机。只有事件通知，不把事件名Added猜成最终原生接受点；包不带UUID/维度/代际/序号，目标未跟踪时无缓存重试，后来进入视距的初始状态未在此补发。tag datagen已读且有实际登记，不声称已运行生成资源。',
 'ConjureWater实际SOAKED生产→MobEffectEvent.Added/Remove/Expired→EventHandler→Networking.sendToNearbyClient按区块tracking→注册PotionSyncPacket→当前世界实体查找/本地玩家排除→add/removeEffect→Soaked/native wet门',
 ev(A,'PotionSyncPacket','onClientReceived'),ev(A,'PotionSyncPacket','__complete_file__'),ev(A,'EventHandler','onPotionAdd'),ev(A,'EventHandler','onPotionRemove'),ev(A,'EventHandler','onPotionExpire'),ev(A,'EventHandler','syncPotionRemoval'),ev(A,'PotionEffectTagProvider','addTags'),span(A,'ModDatagen',42,42,'PotionEffectTagProvider_registration'),ev(A,'EffectConjureWater','onResolveEntity'),ev(A,'Networking','register'),ev(A,'Networking','handle'),ev(A,'Networking','handleClient'),ev(A,'Networking','sendToNearbyClient','BlockPos pos'),
 dedup='不是泛型codec计数：实际SOAKED远端状态副本策略、LocalPlayer排除和增删负时长约定合1；与上一条原生点燃拒绝为独立客户端归属/生命周期点。')
add('spellengine-stashed-combat-charge-consumed-on-attempt-with-deferred-effect-replacement',
 'SpellStashHelper.link由服务器starting注册，针对真实STASH_EFFECT配置把触发器绑到StatusEffect；SpellDelivery实际给目标addStatusEffect。原生combat→fireTriggers先useStashes，复制activeEffects，以本次调用Map按实例累计剩余amp，通过触发门后performImpacts却忽略bool，TRANSFER无arrow也照后续消费；非零consume写Diff，最后统一applyChanges。delayConsume将delay=1，排到world tick TAIL的immediateTasks，届时按effect type重查当前instance但用旧计算newAmplifier，未核验是否同一代效果。',
 '控制反馈消耗预算要定义尝试还是接纳；延迟扣层不能用旧预算覆盖后来刷新的同类型状态。每次调用局部预算不等于同tick全局封顶。',
 '只有静态框架原生链，未装载具体外部STASH法术配置/未运行；不声称任一Boss实际用了此机制。既有evaluateTrigger cap仍可限制一部分重入，所以不能把delay直接称无限触发。WorldScheduler delay=0在下次TAIL处理不是保证完整下一tick。',
 'SpellEngineMod.init→SpellStashHelper.init→serverStarting link→StatusEffectSpellStash；SpellDelivery STASH_EFFECT→效果持有；原生LivingEntityHealthImpacting→CombatEvents→SpellTriggers.init/onDamageIncoming/fireTriggers→useStashes→StatusEffectUtil.applyChanges→WorldScheduler/ServerWorldMixin TAIL→processRemoval',
 ev(S,'SpellStashHelper','useStashes'),ev(S,'SpellStashHelper','init'),ev(S,'SpellStashHelper','link'),ev(S,'SpellStash','__complete_file__'),ev(S,'StatusEffectSpellStash','__complete_file__'),ev(S,'SpellEngineMod','init'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'LivingEntityHealthImpacting','damage_ApplyDamage_entity'),ev(S,'SpellTriggers','init'),ev(S,'SpellTriggers','onDamageIncoming'),ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellTriggers','evaluateTrigger'),ev(S,'StatusEffectUtil','__complete_file__'),ev(S,'WorldScheduler','__complete_file__'),ev(S,'ServerWorldMixin','__complete_file__'),
 dedup='004 cap/chance算法全文仅支持。此处为实际存储法术效果栈、尝试后消费、延迟重查同type覆盖边界，独立于一般被动触发配额；全部同链消费包装1条，不拆每种trigger。')
add('spellengine-teleport-minimum-displacement-explicit-fizzle-before-cost-callback',
 'performImpact TELEPORT解析FORWARD安全候选或BEHIND_TARGET坐标。配置minimum_distance>0且实体/起点存在时，目标为空或直线位移未达平方阈值会在目标实体当前位置发专门fizzle particles/model/sound并return false，没走depart/teleport/arrive。fizzle粒子调用includeSourceEntity=false，仅把payload sourceEntityId写0（sourceType仍ENTITY）；最终sender仍显式向tracked ServerPlayer本人及tracking集合发送，不能把该参数名误读成排除本人。声音另走world.playSound(null,目标坐标)。成功路径却调用void teleport后直接success=true。deliver完成回调传delivered||forceSuccess；performSpell completion仅success后ReleaseFx/SpellCost.consume。',
 '这是有明确拒绝生产点的语义反馈，能区分“目的地/距离失败”和泛型hurt失败；反馈锚在实际被传送实体，原因和完成回调应一起核查。',
 '静态未运行；BEHIND_TARGET自目标更早return false不发fizzle，minimum_distance=0缺dest也无此提示。不能宣称所有失败均免CD/消耗：AREA分支forceSuccess=true、其他impact可成功，且imposeAttemptCooldown已在delivery前执行。void teleport返回不证明最终原生位置接受。',
 'performSpell→SpellDelivery.resolveAndDeliver/deliver DIRECT→SpellImpacts.performImpacts/performImpact TELEPORT→min-distance fizzle false→聚合/DeliveryCompletion→success门的ReleaseFx+cost；模型/粒子/SoundHelper为既有反馈消费者支持',
 ev(S,'SpellImpacts','performImpact'),ev(S,'SpellDelivery','resolveAndDeliver'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'SpellImpacts','performImpacts','boolean additionalTargetLookup'),ev(S,'SpellExecution','performSpell'),ev(S,'SpellCooldowns','imposeAttemptCooldown'),ev(S,'TargetHelper','findTeleportDestination'),ev(S,'TargetHelper','isSafeWithClearance'),ev(S,'TargetHelper','isSafeTeleportDestination'),ev(S,'ParticleHelper','sendBatches','Entity trackedEntity, List<ParticleGroup> effects, boolean includeSourceEntity'),ev(S,'ParticleHelper','sendBatches','@Nullable Entity trackedEntity'),ev(S,'ModelEffectHelper','spawn','LivingEntity contextEntity'),ev(S,'SoundHelper','playSound','Entity entity'),ev(S,'SoundHelper','playSoundEvent','float volume'),
 dedup='004/005共享performImpact完整体不代表新计相同分支：本条仅新增minimum_distance显式fizzle/回调边界；与003Iron被取消传送仍先发FX为不同原生否决策略。不按FX种类或FORWARD/BEHIND拆数。')
add('ars-sensitive-glow-target-color-receipt-gates-existing-status-and-native-team-precedence',
 '已注册EffectLight实际对非自身或Sensitive目标applyConfigPotion(GLOWING)，仅hasEffect(GLOWING)&&Sensitive才发PacketUpdateGlowColor（仍会为已有glowing发，不证明本次添加接纳）。S2C以整数entityID/color发区块tracking；接收把非0颜色写目标client persistentData，0删除。EntityMixin.getTeamColor只在原生颜色=16777215且isCurrentlyGlowing时读取，负值用本地ticks rainbow，否则用原色。',
 '具体状态反馈应依实际目标有该状态再生产，但已有状态不能证明本次成功；原生队伍颜色优先、0清除哨兵与颜色取值域需区分，避免目标着色错归。',
 '不是拒控文字实现/未运行；缺UUID、维度、目标未加载重试与初始跟踪补色。该NBT只在client包中写，搜索glow_color未见效果移除时自动清；重新发0才显式删。Mixin启用资源本地缺，无运行承诺。原始RGB黑0会走删除而非黑色，不能声称所有颜色等价可见。',
 'APIRegistry注册EffectLight→SpellResolver→EffectLight.onResolveEntity→IPotionEffect→hasEffect→Networking S2C注册/区块tracking→PacketUpdateGlowColor.onClientReceived→Entity.getTeamColor RETURN mixin取target persistentData',
 ev(A,'PacketUpdateGlowColor','onClientReceived'),ev(A,'PacketUpdateGlowColor','__complete_file__'),ev(A,'EffectLight','onResolveEntity'),ev(A,'IPotionEffect','__complete_file__'),ev(A,entityMixin,'ars_nouveau$getTeamColor'),ev(A,'Networking','register'),ev(A,'Networking','sendToNearbyClient','BlockPos pos'),span(A,'APIRegistry',55,55,'EffectLight_registration'),ev(A,'APIRegistry','registerSpell'),ev(A,'SpellResolver','onResolveEffect'),ev(A,'SpellResolver','resolveAllEffects'),
 dedup='独立实际目标颜色回执/原生team优先策略，不拆几何/modelFX模板；与旧hud颜色常量不同。不是按药水或颜色数量凑参考，主岗可按与战斗文字的实际相关性降支持。')
add('spellengine-passive-delay-target-snapshot-world-change-support',
 'fireTriggers的passive.fire_delay>0在触发当场选targetResult并排到旧player.world的scheduler；闭包执行时改用player.getWorld且仍用捕获的targetResult，不在此重新找目标。performSpell先检查spectator/法术source/attempt，短路可能拒绝后续；delivery.delay>0又另有caster/target removed检查，二者不是同一时序。',
 '延迟反馈若把旧目标快照与当前新世界混用，应验证世界和代际；仅静态可见风险，不推定已跨维攻击成功。',
 '本条没有新增具体Boss拒绝门/明确反馈生产，支持0。与既有004触发器和005目标生命周期背景合并；不将scheduler通用设施计信用。',
 '原生CombatEvent→SpellTriggers.fireTriggers选目标→WorldScheduler→旧world TAIL运行闭包→当前player.world performSpell/attempt→SpellDelivery.resolveAndDeliver',
 ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellTriggers','init'),ev(S,'SpellExecution','performSpell'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'WorldScheduler','__complete_file__'),ev(S,'ServerWorldMixin','__complete_file__'),status='support_only_not_effective',dedup='通用延迟目标生命周期只支持0；不与既有触发配额或具体feedback TTL重复计。')
add('iron-gust-direct-motion-before-status-acceptance-and-single-pulse-support',
 'GustSpell真实生成GustCollider并主动gust.tick。AbstractConeProjectile服务端dealDamageActive只执行一轮、碰撞实体Set去重后置false；GustCollider仅owner非空/目标Living/范围/非友伤时直接加速度并hurtMarked，再addAIRBORNE忽略结果。getOwner在tickCount>=1直接null；尾部实体外观存留到>8tick。Airborne碰墙速度满足阈值先发fall声再hurt，忽略bool且return false。',
 '控制位移写入在状态之前，不能以状态拒绝证明没被推动；音效也不是伤害成功回执。',
 '同001 Ars Snare/Gravity直接motion旁路家族，支持0；不是新免疫门。没有实机计时，不能据getOwner阈值假定第一次原生tick必有owner。说明主动tick/计数门不代表已验证实际移动。',
 '注册GUST→GustSpell.onCast主动tick→AbstractConeProjectile单轮碰撞Set→GustCollider.onHitEntity motion→AIRBORNE；原生effect tick碰墙声/伤害',
 ev(I,'GustCollider','onHitEntity'),ev(I,'GustSpell','onCast'),ev(I,'AbstractConeProjectile','tick'),ev(I,'AbstractConeProjectile','getSubEntityCollisions'),ev(I,'GustCollider','getOwner'),ev(I,'GustCollider','tick'),ev(I,'AirborneEffect','applyEffectTick'),ev(I,'AirborneEffect','shouldApplyEffectTickThisTick'),span(I,'MobEffectRegistry',42,42,'AIRBORNE_registration'),span(I,'SpellRegistry',123,123,'GUST_registration'),status='support_only_not_effective',dedup='直接motion与status成功分离已计家族；新脉冲门不是单独拒控/反馈策略，支持0不补数量。')
add('iron-scapegoat-taunt-selector-not-hit-rejection-support',
 'ScapegoatSpell生成诱饵后Utils.performTaunt在近球体选目标，tauntPredicate混合Enemy XOR/taunter Enemy和allied/Neutral愤怒；最终只对Mob先发愤怒粒子再setTarget。没有读取setTarget接纳结果，临时诱饵自身15秒倒计时归零清退。',
 '目标改变意图与目标接受分开；这种清仇恨/嘲讽无实际伤害拒绝不扩成免疫样本。',
 '依006主审对真实隐身清仇恨的范围决定，本条同样支持0。没有修改守卫或转移其旧账信用。',
 'SCAPEGOAT注册→ScapegoatSpell.onCast→Utils.tauntPredicate/performTaunt→Mob.setTarget；ScapegoatEntity.tick→poofAndDiscard',
 ev(I,'Utils','performTaunt','List<Entity> targets'),ev(I,'Utils','performTaunt','Predicate<Entity> selector'),ev(I,'Utils','tauntPredicate'),ev(I,'ScapegoatSpell','onCast'),ev(I,'ScapegoatEntity','__complete_file__'),ev(I,'ScapegoatEntity','poofAndDiscard'),span(I,'SpellRegistry',135,135,'SCAPEGOAT_registration'),status='support_only_not_effective',dedup='与006-02隐身/其他纯仇恨控制一致降支持0；不计为Boss免伤回执。')
add('iron-sacrifice-owner-recheck-and-direct-killed-removal-support',
 'Sacrifice预选仅自有IMagicSummon，onCast重取TargetEntityCastData并再次UUID比summoner，随后先范围爆破再remove(KILLED)，不走目标hurt。实际DeadKingBoss.sacrificialMarkHandler为ominous召唤物随机加Mark；Mark在LivingDeathEvent服务器回调爆破并remove。爆破目标伤害applyDamage返回未读，声光/摄像震动无条件。',
 '直接移除与伤害拒绝不同，预选成功文字不是最终接纳；存在先爆破后移除的实际源不应伪称已处理全部免疫。',
 '已有Ars Disintegration直接remove绕hurt家族，支持0；无客户端/AI/死亡事件顺序运行验证。没有测试重入或声明必然double explosion，也未制作/改变camera。',
 '注册SACRIFICE→checkPreCastConditions→onCast所属复核→doSacrificeExplosion→remove；SetSummonOwnerEvent→DeadKingBoss.sacrificialMarkHandler→Mark→LivingDeathEvent→onLivingDeath',
 ev(I,'SacrificeSpell','onCast'),ev(I,'SacrificeSpell','checkPreCastConditions'),ev(I,'SacrificeSpell','doSacrificeExplosion'),ev(I,'SacrificialMarkEffect','onLivingDeath'),ev(I,'DeadKingBoss','sacrificialMarkHandler'),span(I,'SpellRegistry',98,98,'SACRIFICE_registration'),span(I,'MobEffectRegistry',76,76,'SACRIFICIAL_MARK_registration'),status='support_only_not_effective',dedup='同直接remove绕hurt家族支持0，不凭来源武器/标记死亡变体再计；旧预选回执包也不重新计。')
rows[4]['decision_focus']={'lines':[640,655],'counting_rule':'The complete performImpact containing method is shared support with 004/005; the proposed independent site is only the minimum_distance fizzle decision, not another count for that entire method. Pending primary review; zero helper credit.'}
supplements=[]
assert len(rows)<=30
for repo in BASE:
 d=LOCAL/'sources-batch007'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo in (A,S):shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for n in ('001','002','003','004','005','006') for r in json.loads((OUT/f'batch-{n}.json').read_text())['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
assert not overlaps,overlaps
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert len(primary)==len(set(primary))
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-007','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'max_units':30,'rows':rows,'support_for_prior_batches':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'候选不等于信用；主岗需最终相关性/语义去重。本批不按模板补到30。代码均固定本地源码审阅；本批外部请求0；既有005/006注册来源及TLS失败记录保留，未重试；真实隐身/通用AOE/直接移除同族主动降支持0。无游戏/正式代码修改。'}
(OUT/'batch-007.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-007.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars/SpellEngine pinned Git tree/blob；Iron pinned archive source.json SHA256 inventory，无相同commit树，不冒称blob已独立核验。'},ensure_ascii=False,indent=2)+'\n')
allrefs=[v for r in rows+supplements for v in r['source_refs']]
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'supplement_units':len(supplements),'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(r['unit']=='complete_method' for r in allrefs),'complete_support_resource_references':sum(r['unit']=='complete_support_resource' for r in allrefs),'batch_sha256':sha((OUT/'batch-007.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':0,'todo_modified':False}
(OUT/'receipt-007.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
