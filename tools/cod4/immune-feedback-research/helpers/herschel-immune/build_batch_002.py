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
 starts=[i for i,l in enumerate(lines,1) if re.match(r'\s*(?:public|private|protected|default|static)\s',l) and re.search(r'\b'+re.escape(method)+r'\s*\(',l) and (qualifier is None or qualifier in l) and not l.strip().endswith(';')]
 assert len(starts)==1,(name,method,qualifier,starts)
 start=starts[0];end=reader.end_method(lines,start);excerpt=''.join(lines[start-1:end]);pin=meta[repo];commit=pin.get('commit',pin.get('sha'));blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if repo in (A,S):
  tree=json.loads((BASE[repo]/'tree.json').read_text());assert tree['sha']==commit;assert next(x['sha'] for x in tree['tree'] if x['path']==rel)==blob
  proof='pinned Git tree blob SHA1'
 else:
  entry=next(x for x in pin['files'] if x['path']==rel);assert entry['sha256']==sha(data);proof='pinned archive source.json SHA256 inventory'
  if 'git_blob_sha1' in entry:assert entry['git_blob_sha1']==blob;proof='pinned source inventory SHA256 and Git blob SHA1'
 dest=LOCAL/'sources-batch002'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-002-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与上一批按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
add('spellengine-player-protection-charge-and-source-receipt',
 'PlayerProtectionEffectMixin在Player原生isInvulnerableTo HEAD调用tryProtect。遍历active effects，缺registry key跳过；匹配注册保护和damage tag才扣amplifier；按新amp<0选择onRemove或onDecrement粒子/声，然后applyChanges并true。原生返回invulnerable true。',
 '实际拒伤分支有明确消耗和音效依据；来源tag不匹配不是被保护，不应产生免疫提示。',
 'API仅Player Mixin调用，不证明Boss适用；遍历命中首个即返回，多保护不全部消费；减层后重加效果返回值未检查。',
 'Player.isInvulnerableTo→Protection.tryProtect→ParticleHelper/SoundHelper→StatusEffectUtil.applyChanges→原生true',
 ev(S,'PlayerProtectionEffectMixin','isInvulnerable_SpellEngine'),ev(S,'Protection','tryProtect'),ev(S,'StatusEffectUtil','applyChanges'),ev(S,'StatusEffectUtil','processRemoval'),ev(S,'StatusEffectUtil','copyWithNewAmplifier'),ev(S,'SoundHelper','playSoundEvent','float volume'),ev(S,'ParticleHelper','sendBatches','@Nullable Entity trackedEntity'),
 dedup='首批仅支持入口、缺方法体而信用0。本批同提交本地补全保护决策/消耗，禁止将首批入口再独立晋级。Evasion/Shroud不在本链。')
add('spellengine-control-policy-intersection-and-reason-priority',
 'fromEffects读取ActionImpairing.actionsAllowed，忽略null；所有jump/move/player attack/item/cast/mobAI允许位分别AND。原因取枚举最大ordinal。没有limiter则ANY。',
 '组合控制不能由最后一个效果覆盖；UI最高优先原因可能不是当前这项动作的唯一拒绝原因。',
 '这是通用游戏效果决策，不证明Boss可被施加；依赖StatusEffect Mixin实现ActionImpairing；常量STUN/SILENCE等不拆条目。',
 'StatusEffectActionImpairing存策略→LivingEntity.updateEntityActionsAllowed→fromEffects→各原生拒绝入口',
 ev(S,'EntityActionsAllowed','fromEffects'),ev(S,'StatusEffectActionImpairing','actionsAllowed'),ev(S,'StatusEffectActionImpairing','setAllowedEntityActions'),ev(S,'LivingEntityActionImpairing','updateEntityActionsAllowed'),ev(S,'LivingEntityActionImpairing','tickStatusEffects_HEAD_SpellEngine'))
add('spellengine-final-input-and-active-item-control-gates',
 '原生jump在HEAD取消；isImmobile受限返回true；tickActiveItemStack先clearActiveItem再取消；Player.attack HEAD受限取消。客户端tickMovement在Input.tick后清前后/左右输入，tick尾更新策略。',
 '阻输入、终止正在用物品、原生行动门应覆盖实际路径，输入归零不是拒绝所有外部motion；缓存更新时序需要辨明。',
 '这些共享同一动作策略合并一条；客户端路径不等于服务端对非法C2S全面拒绝；没有实际运行Mixins。',
 'effect changed→cached actionsAllowed→jump/isImmobile/item/player attack；ClientPlayer input override',
 ev(S,'LivingEntityActionImpairing','jump_HEAD_Spell_Engine'),ev(S,'LivingEntityActionImpairing','isImmobile_HEAD_SpellEngine'),ev(S,'LivingEntityActionImpairing','tickActiveItemStack_HEAD_SpellEngine'),ev(S,'PlayerEntityActionImpairing','attack_HEAD_SpellEngine'),ev(S,'ClientPlayerActionImpairing','tickMovement_ModifyInput_SpellEngine_ActionImpairing'),ev(S,'ClientPlayerActionImpairing','tick_TAIL_SpellEngine_ActionImpairing'),ev(S,'EntityActionsAllowed','isImpaired','Common action'))
add('spellengine-error-reason-vs-attempt-debounce',
 'isImpaired Player最终重载仅客户端/showError/不允许时把reason交HudMessages。castAttemptError用attemptDisplayed挡重复，成功或失败都先置标记，再看是否失败/配置；仅MISSING_ITEM/ON_COOLDOWN能生成消息。actionImpaired未读该标记，直接error。',
 '控制拒绝提示与施法失败是不同生产来源；不能以一个去重标志声称所有免疫消息都限流。',
 '只HUD红字不是目标灰色浮字；actions reason按枚举优先，与当前动作原因不一定一一对应；部分失败类型不产生消息。',
 'MinecraftClient.doAttack/doItemUse→isImpaired(showError)→actionImpaired；施法Attempt→castAttemptError',
 ev(S,'EntityActionsAllowed','isImpaired','boolean showError'),ev(S,'HudMessages','castAttemptError'),ev(S,'HudMessages','actionImpaired'),ev(S,'MinecraftClientActionImpairing','doAttack_HEAD_SpellEngine_ActionImpair'),ev(S,'MinecraftClientActionImpairing','doItemUse_HEAD_SpellEngine_ActionImpair'))
add('spellengine-hud-error-single-slot-lifetime-and-release-reset',
 'HudMessages.error最终重载覆盖currentMessage，默认20tick/10fade；tick在duration<=0清空，否则--；useKey松开才重置attemptDisplayed。连续actionImpaired可每tick替换消息并重置寿命。',
 '单槽覆盖/寿命和尝试去重是三种语义，不应把20tick寿命当每目标节流。',
 '无目标UUID/维度key，HudMessages是静态singleton；本批未查实际绘制器，不声称10fade已视觉验证；无Boss免疫权威语义。',
 'actionImpaired/error→MessageState→HudMessages.tick→currentMessage清理；键释放→attemptDisplayed reset',
 ev(S,'HudMessages','error','Text text, int duration'),ev(S,'HudMessages','error','public void error(String message, int duration'),ev(S,'HudMessages','tick'),
 dedup='与前一条同HUD类但此条仅独立生命周期/覆盖机制，不重复消息资格生产；最终可由主岗合并，信用0。')
add('spellengine-client-cast-prediction-reconciles-denial',
 'startSpellCast排spectator/null/same spell和CAST_SPELL受限，再attempt；通过发送CastRequest并建立非instant预测。tick若死亡/换item/CD/受控取消；服务端声明曾匹配后消失则结束；未确认>20tick丢预测，非charged超时也结束。',
 '客户端开始展示不等于服务端允许；确认超时不能反推Boss免疫，只能结束预测。',
 '未补齐服务端SpellCastInteractor/SpellCasting.attempt，不计为服务器安全验证或免疫生产；这里只研究客户端反馈撤销生命周期。',
 'ClientCastController.startSpellCast→CastRequest+predictedProcess→tick声明对账→cancel/endPrediction',
 ev(S,'ClientCastController','startSpellCast'),ev(S,'ClientCastController','tick'),ev(S,'ClientCastController','cancelSpellCast'),ev(S,'ClientCastController','endPrediction'))
add('spellengine-target-stream-dedup-not-hit-receipt',
 'streamTargets只clientResolved形状，snapshot等lastSent则不发，变化则更新后发TargetStream。snapshotFor对服务端解析形状发EMPTY。',
 '客户端目标状态去重不等于命中/拒绝事件去重，不可用于宣称Boss免疫回执已收到。',
 '纯施法瞄准复制，离战斗文字/拒绝反馈较远；本批降支持，不拿协议状态充研究有效数。',
 'tick→streamTargets→TargetSnapshot比较→C2S TargetStream',ev(S,'ClientCastController','streamTargets'),ev(S,'ClientCastController','snapshotFor'),status='support_only_not_effective')
add('spellengine-mob-ai-disabled-return-value-counterexample',
 'isAiDisabled HEAD在USE_AI受限时setReturnValue(false)再cancel，实际返回语义为AI未禁用；与fromEffects canUseAI=false的意图相反。',
 '最终原生返回值必须按被注入方法语义核对，不能靠Mixin命名认定拒控已工作。',
 '未启动外部代码，静态反例；不推荐计入有效AI拒绝实现。',
 'effect→fromEffects→isImpaired(Mob)→Mob.isAiDisabled注入返回false',ev(S,'MobEntityActionImpairing','isAiDisabled_HEAD_SpellEngine'),ev(S,'EntityActionsAllowed','isImpaired','Mob action'),status='support_only_not_effective')
add('ars-bubble-capture-final-tag-sleep-and-reboard-filter',
 'EffectBubble生成实体后tryCapturing；未爆/空乘客且canHit才startRiding并以实际乘客列表确认。canHit排已下船UUID、睡眠Player、BUBBLE_BLACKLIST和已在Bubble中的实体；datagen将Boss纳入黑名单。',
 '真正控制结果应读上载结果；Boss、睡眠玩家、重复上载分别属于不同资格拒绝。',
 'canHit不调用super Projectile筛选；没有owner/盟友过滤；tick近邻路径与tryCapturing并非完全同门。',
 'EffectBubble.onResolveEntity→Bubble.tryCapturing→canHitEntity→startRiding→实际passenger确认',ev(A,'EffectBubble','onResolveEntity'),ev(A,'EffectBubble','createBubble'),ev(A,'BubbleEntity','tryCapturing'),ev(A,'BubbleEntity','canHitEntity'),ev(A,'BubbleEntity','getDismountLocationForPassenger'),ev(A,'EntityTagProvider','addTags'))
add('ars-bubble-pop-tick-lifecycle-not-unified-rejection',
 'pop仅服务端且HAS_POPPED尚false时置同步标记并播泡泡声。tick读取已爆则poppingTicks++，服务端age>maxAge调用pop；空乘客时直接找canHit实体、临时清boardingCooldown再上载；poppingTicks>5才discard。',
 '爆裂反馈、控制释放和延迟移除并非同一时刻；寿终期间所有控制入口需要统一拒绝门。',
 'tick捕获没有再查HAS_POPPED，tryCapturing有该检查；临时boardCD仅失败才恢复。hasPopped字段与同步HAS_POPPED不是同一变量。无运行证明。',
 'Bubble.tick→pop同步/声→延迟discard；同tick空乘客自动捕获路径',ev(A,'BubbleEntity','pop'),ev(A,'BubbleEntity','tick'))
add('ars-bubble-unwired-static-event-hooks-not-proven',
 'onAttacked可取消空泡/物品/自身乘客攻击，活体乘客则player.attack转发；entityHurt可加泡伤再pop，使用普通hasPopped字段；preEntityRemoval设置同步HAS_POPPED。',
 '静态方法存在不等于已注册原生事件；应核查调用注册再宣称实际受伤反馈。',
 '固定Java缓存全量搜索只有这些声明，未找到外部调用；没有SubscribeEvent注解。本批仅支持，不能称原生事件机制已工作。',
 '静态事件形参入口→乘客攻击/加伤/pop；注册链未证实',ev(A,'BubbleEntity','onAttacked'),ev(A,'BubbleEntity','entityHurt'),ev(A,'BubbleEntity','preEntityRemoval'),status='support_only_not_effective')
add('ars-disintegration-removal-bypasses-damage-immunity',
 '服务端每60tick找5格MONSTER或白名单活体但排Player，再排DISINTEGRATION_BLACKLIST；直接remove DISCARD，removed后poof，按经验产宝石；只有有经验产出才didWorkOnce设置耗源。',
 '直接移除不会走hurt免疫/伤害文字路径；拒伤门不能覆盖所有处置。玩家例外与Boss标签要另核。',
 '默认disintegration黑名单datagen为空，不能宣称默认所有Boss受保护；视觉粒子不代表普通伤害。',
 'Ritual.tick→候选资格/blacklist→Entity.remove→removed检查→poof/XP gems/source flag',ev(A,'RitualDisintegration','tick'),ev(A,'EntityTagProvider','addTags'))
add('iron-rapier-native-dodge-with-collision-fallback',
 '服务器且攻击者非null非bypass先排shouldIgnoreDamage，再40%侧闪；performSidestep按近距绕目标/远距横移，findFreePosition再窒息检查；堵塞时退回原位仍粒子/teleport/声，hurt仍false。',
 '真正拒伤分支可能没有可见位移，不能以目标没动认定闪避失败；也不能由传送效果证明Boss免疫。',
 '无闪避CD；首批Evasion/Shroud不同具体实体native hurt生产，不复用其粒子包装信用。',
 'SummonedRapier.hurt→friendly ignore或随机dodge→performSidestep→false；否则父hurt',ev(I,'SummonedRapierEntity','hurt'),ev(I,'SummonedRapierEntity','performSidestep'))
add('iron-summoned-weapon-final-owner-damage-config',
 'SummonedWeapon.hurt非bypass且shouldIgnoreDamage拒绝；该策略只有CAN_ATTACK_OWN_SUMMONS=false且来源有entity才做friendlyfire。否则允许父hurt。',
 '玩家可选友伤策略不等同Boss免疫；最终拒绝点应保留bypass能力，来源无entity并不被同样拒绝。',
 '调用既有DamageSources.isFriendlyFireBetween，仅支持复用，不把映射函数再次计数；所有武器子类共享此策略合并。',
 'SummonedWeapon.hurt→IMagicSummon.shouldIgnoreDamage→friendlyfire→false/super',ev(I,'SummonedWeaponEntity','hurt'),ev(I,'IMagicSummon','shouldIgnoreDamage'))
add('iron-voidtentacle-bypass-only-damage-and-antimagic',
 'VoidTentacle.hurt仅BYPASSES_INVULNERABILITY允许super，其余false；isPickable=false但仍有最终伤害门。tick最多300age存在，<280每20tick攻击；onAntiMagic烟粒子后discard。',
 '不可选中与真正拒伤不同；常规伤害免疫仍保留特殊销毁入口，反魔法移除不等于一次成功HP伤害。',
 '不把静态false的isPickable包装独立计数；dealDamage附加失明只是伤害成功条件，不额外拆条。',
 'hurt→bypass gate；tick寿命/AI damage；AntiMagic→onAntiMagic→discard',ev(I,'VoidTentacle','hurt'),ev(I,'VoidTentacle','tick'),ev(I,'VoidTentacle','onAntiMagic'),ev(I,'VoidTentacle','dealDamage'))
add('iron-portal-control-tag-cooldown-before-teleport',
 '候选排CANT_USE_PORTAL/载具/旁观并需pickable或projectile。canUsePortal排passenger/PartEntity/连接缺失/目标UUID cooldown。先给目的portal登记10tick冷却，再检查连接坐标、同维传送或跨维目标Level。',
 '拒绝传送原因包括资格、连接和冷却，不能归结Boss免控；成功声可能先于跨维dim有效性检查，不能作权威成功回执。',
 '属于控制资格与结果观察，不是免疫字；冷却按portal+entity双键，processDelay对范围内对象+1可能抵消tick-1；不称已实测时序。',
 'Portal.tick cooldown-1→checkEntities delay+1→canUsePortal→add cooldown→connected position→teleport/FX',ev(I,'PortalEntity','checkForEntitiesToTeleport'),ev(I,'PortalEntity','tick'),ev(I,'PortalManager','canUsePortal','UUID portalId'),ev(I,'PortalManager','addPortalCooldown'),ev(I,'PortalManager','addDirectPortalCooldown'),ev(I,'PortalManager','processCooldownTick'),ev(I,'PortalManager','processDelayCooldown'))
add('iron-portal-per-entity-loop-window-abort',
 'handleLoopTracking首次UUID记gameTick与1，后续++loopCount>5且距首次<=20tick触发：若循环者是owner用genericKill封装Float.MAX_VALUE，NaN则HP0；丢portal。超过窗口则移除该UUID记录。',
 '按实体的有限时间重复控制检测可比目标反馈去重，但过载处置与免疫拒绝不同。',
 '只同维分支调用；不是滑动刷新窗口；非owner不受同样伤害；主岗可按与本题相关性降支持。',
 'PortalEntity.same-dimension teleport→handleLoopTracking→UUID window→abort/owner damage',ev(I,'PortalEntity','handleLoopTracking'))
add('iron-cleanse-tag-protected-effect-still-shows-fx',
 'onCast按shouldHealEntity筛活体；仅HARMFUL且非CLEANSE_IMMUNE效果被移除，随后无条件给该目标Cleanse粒子，即便没有移掉任何效果。shouldHealEntity考虑中立愤怒、自身、ALWAYS_HEAL、双方盟友、队伍、Player等。',
 '清除抗性以效果而非整目标表达；成功外观不证明清掉某个Boss效果，不能用粒子反推结果。',
 '与首批Ars Dispel是不同实际拒清策略/事件路径；同removeEffect包装不拆；未声称实际CLEANSE_IMMUNE默认内容。',
 'Cleanse.onCast→shouldHealEntity→category/tag filters→removeEffect→无条件FX',ev(I,'CleanseSpell','onCast'),ev(I,'Utils','shouldHealEntity','Entity healer, Entity target'))
add('ars-bounce-fall-source-avoidance-and-next-tick-motion',
 'Bounce onFall只有效果，客户端非Player跳过，距离>2才处理；蹲下只设damageMultiplier0，不蹲则归零fallDistance、按Player/side决定反弹速度、入对应队列再cancel。BounceTimedEvent第1tick恢复Y并hurtMarked后到期。',
 '摔伤消除与控制反弹要分别反馈；客户端玩家与服务器mob计算路径不同，不能泛称任何来源免疫。',
 '保留上游Tinkers adapted来源注释，不算原创；未与Tinkers独立计数，日后导入需去重。',
 'LivingFallEvent→BounceEffect.onFall→event zero/cancel→BounceTimedEvent.tick一次速度恢复',ev(A,'BounceEffect','onFall'),ev(A,'BounceTimedEvent','tick'),ev(A,'BounceTimedEvent','isExpired'))
add('ars-bounce-player-wall-damage-zero-plus-recoil',
 'LivingDamage.Pre只Player有Bounce且来源FLY_INTO_WALL时setNewDamage0，然后沿lookAngle反向*2写速度并hurtMarked。',
 '来源特定防伤可同时新增位移；零伤不是控制免疫；玩家限定不能套到Boss。',
 '与上一条原生fall事件不同最终生产点/来源/玩家边界；若主岗按同效果保护家族合并允许降支持；无新信用。',
 'LivingDamage.Pre→BounceEffect.onFlyWallDamage→zero damage+recoil',ev(A,'BounceEffect','onFlyWallDamage'))
add('ars-player-totem-death-cancel-resource-and-rearm',
 'LivingDeath只Player，有Totem perk holder且isActive才HP1、清效果并加regen/absorption/fireRes、广播35、置isActive false并写装备组件、发trigger消息再cancel。sleepEvent对世界Player重置isActive并写组件。',
 '保命取消发生在死亡阶段，不能标为攻击免疫；权威消耗、触发消息、恢复窗口各自需保存。',
 'PerkUtil遍历armor后保留最后一个匹配holder，maxCount计算未用于选择；初始化isActive=true。仅实际装备组件而非永久角色状态；不是Boss无敌机制。',
 'LivingDeathEvent→PerkEvents.totemEvent→写组件/feedback/cancel；SleepFinished→sleepEvent rearm',ev(A,'PerkEvents','totemEvent'),ev(A,'PerkEvents','sleepEvent'),ev(A,'PerkUtil','getHolderForPerk'),ev(A,'TotemPerk','getInitTag'))
add('ars-windshear-ground-prerequisite-counterexample',
 'Windshear仅非ground且非ItemEntity；向下找blocksMotion最多条件<=10循环，numBlocks可到11，伤害直接加numBlocks，只有attemptDamage true才发sweep粒子。',
 '落地完全无伤是触发资格，不是Boss免疫；书本文案up to10不等于代码严格10。',
 '与ColdSnap均前置条件+通用attemptDamage+FX模板，地形算伤本题相关性偏弱；降支持不因条件不同凑数。',
 'Windshear.onResolveEntity→air/ground资格→terrain distance→attemptDamage→FX',ev(A,'EffectWindshear','onResolveEntity'),status='support_only_not_effective')
add('ars-breeze-projectile-reflection-chain-unwired-limit',
 'onSpellResolve排Breeze施法者，实体命中Breeze且非FakePlayer并MethodProjectile时Pre.cancel，生成归属Breeze的orbit并入队；tick45移除orbit生成Breeze归属法术弹指向原shooter，每8tick加速。',
 '反射拒绝应保存真正Pre取消原因和后续归属，不能将反射重施法当原hit成功。',
 'BreezeEvent无事件注解，尚未证明onSpellResolve注册；本批保留完整链但不称实际生效，待主岗决定相关性。',
 'SpellResolveEvent.Pre static hook→orbit→EventQueue→BreezeEvent.tick45 recast',ev(A,'BreezeEvent','onSpellResolve'),ev(A,'BreezeEvent','tick'),ev(A,'BreezeEvent','isExpired'),status='support_only_not_effective')
# Constructor method-reference registration completes these two event chains.
for index in (10,22):
 rows[index]['status']='pending_primary_semantic_review'
 rows[index]['source_refs'].append(ev(A,'ArsNouveau','ArsNouveau'))
rows[10]['semantic_dedup_key']='ars-bubble-registered-hit-redirect-and-damage-bonus'
rows[10]['observation']+=' ArsNouveau构造器实际addListener注册onAttacked/entityHurt/preEntityRemoval（方法引用，非点调用）。'
rows[10]['limits']='注册链已补齐；普通hasPopped字段没有在pop中更新，不能以该字段证明仅一次加伤；onAttacked转发后未取消原事件。没有实际运行验证。'
rows[10]['native_chain']='ArsNouveau构造器addListener→原生AttackEntity/LivingDamage.Pre/EntityPreRemoval→Bubble静态回调'
rows[22]['semantic_dedup_key']='ars-breeze-registered-pre-resolve-reflection'
rows[22]['source_refs'].append(ev(A,'SpellResolver','resume'))
rows[22]['observation']+=' ArsNouveau构造器addListener(BreezeEvent::onSpellResolve)已核验；SpellResolver.resume发布Pre后isCanceled立即return，不继续解析效果。'
rows[22]['limits']='已确认方法引用事件注册及Pre取消调用方；反射45tick后以Breeze重建SpellContext，不等于保留玩家归属。未运行，队列时序不能以注释断言；不新增模型或字。'
rows[22]['native_chain']='ArsNouveau构造器注册→SpellResolver.resume发布Pre→BreezeEvent取消原解析→orbit→队列tick45生成Breeze归属弹'
# Main reviewer merged owner/friendly-fire family in batch001; do not re-propose it.
rows[13]['status']='support_only_not_effective'
rows[13]['deduplication']='主岗HERSCHEL-001-REVIEW已将01+04归属拒伤合并1；此处最终hurt加配置开关为该家族支持，不再建议独立计数。'
# Explicitly requested supplements, not new candidate credit.
supplements=[
 {'support_for_batch001':'herschel-001-06','research_credit':0,'suggested_credit':0,
  'observation':'addHeartstopDamage直接+=后doSync；set归零也doSync。Player走tracking+self SyncPlayerDataPacket，IMagicEntity走tracking SyncEntityDataPacket；write/read包含float债务；ClientMagicData玩家按整数entityId查表，magic mob按现有实体类型更新。Heartstop音效从该已同步float读取。',
  'limits':'未运行S2C；整数ID没有附加UUID/维度epoch。getPersistentData只保留learned和selection，不带债务；save/load NBT有债务，不可混称跨死永久。',
  'source_refs':[ev(I,'SyncedSpellData',m) for m in ['addHeartstopDamage','setHeartstopAccumulatedDamage','doSync','write','read','saveNBTData','loadNBTData','getPersistentData']]+[ev(I,'SyncPlayerDataPacket','handle'),ev(I,'SyncPlayerDataPacket','write'),ev(I,'SyncEntityDataPacket','handle'),ev(I,'SyncEntityDataPacket','write'),ev(I,'ClientMagicData','handlePlayerSyncedData'),ev(I,'ClientMagicData','handleAbstractCastingMobSyncedData'),ev(I,'ClientMagicData','getSyncedSpellData')]},
 {'support_for_batch001':'herschel-001-21','research_credit':0,'suggested_credit':0,
  'observation':'Blink WarpScroll路径通过Ender事件后PortalTile.getServerLevel再teleportEntityTo。同维若目标块已PortalBlock直接返回原entity，不移动；其他同维先regionTicket、发PacketWarpPosition，再teleport/rotation并同步乘客/控制者vehicle；跨维走DimensionTransition。Nearby是tracking chunk，不是固定32格；PacketWarpPosition客户端按当前level整数ID查找并直接setPos/rotation，实体缺失返回。',
  'limits':'未测实际收包/线程；onClientReceived未见world null门、UUID/维度/有限坐标校验；PortalTile非ServerLevel返回原entity也不代表已传送。跨维rotationVec直接解引用，不能宣称null可用。',
  'source_refs':[ev(A,'PortalTile','teleportEntityTo'),ev(A,'PortalTile','getServerLevel'),ev(A,'PacketWarpPosition','onClientReceived'),ev(A,'PacketWarpPosition','toBytes'),ev(A,'Networking','sendToNearbyClient','BlockPos pos'),ev(A,'Networking','sendToNearbyClient','Entity e'),ev(A,'Networking','handleClient'),ev(A,'Networking','register'),ev(A,'Networking','handle')]},
 {'support_for_batch001':'herschel-001-26','research_credit':0,'suggested_credit':0,
  'observation':'另一spawnIce重载按可替换位置生成角/侧碎片；碎片cancelDrop=true、hurtEntities=true且shooter字段记录施法者。EnchantedFallingBlock.tick射线命中走onHitEntity：hurt成功才knockback及doPostHurtEffects减速；失败恢复fireTicks但piercingIgnoreEntityIds已提前加入。groundBlock的cancelDrop分支discard后调用IceShard.callOnBrokenAfterFall：AOE排shooter/单向allied后hurt，并不检查结果就加slow。两种附带slow路径区别明确。',
  'limits':'碎片专用shooter字段未等同Projectile.getOwner；碰撞排getOwner未必排shooter，落地AOE另排shooter。hurt false不阻落地slow；不声明药水必施加成功。未跑游戏。',
  'source_refs':[ev(A,'EffectColdSnap','spawnIce','LivingEntity shooter, Level level'),ev(A,'EffectColdSnap','spawnIce','spawnIce(Level level'),ev(A,'EffectColdSnap','replaceableBetween'),ev(A,'IceShardEntity','callOnBrokenAfterFall'),ev(A,'IceShardEntity','doPostHurtEffects'),ev(A,'EnchantedFallingBlock','tick'),ev(A,'EnchantedFallingBlock','groundBlock'),ev(A,'EnchantedFallingBlock','onHitEntity'),ev(A,'EnchantedFallingBlock','canHitEntity'),ev(A,'EnchantedFallingBlock','getDamageSource'),ev(A,'ColoredProjectile','findHitEntity')]}
]

# No forced 30: 23 units, 19 pending and four deliberately support-only.
assert len(rows)==23
for repo in BASE:
 d=LOCAL/'sources-batch002'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo in (A,S):shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
old=json.loads((OUT/'batch-001.json').read_text());prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for r in old['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
# PlayerProtection was support-only last batch, not primary: none of the 30 primary methods repeat.
assert not overlaps,overlaps
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert len(primary)==len(set(primary))
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-002','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'target_units':30,'shortfall_to_30_reviewed_units':30-len(rows),'rows':rows,'support_for_batch001':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'No count added; SpellEngine missing bodies recovered at identical fixed commit from legacy local cache. No external request, game or production edits.'}
(OUT/'batch-002.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-002.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars and recovered SpellEngine checked against pinned Git tree/blob; Iron matches pinned archive inventory SHA256, no matching tree cached.'},ensure_ascii=False,indent=2)+'\n')
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':23,'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(len(r['source_refs']) for r in rows),'supplement_method_references':sum(len(r['source_refs']) for r in supplements),'batch_sha256':sha((OUT/'batch-002.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':0,'todo_modified':False}
(OUT/'receipt-002.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
