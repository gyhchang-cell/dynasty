"""Local-only helper receipt builder. No upstream execution or master-ledger writes."""
from pathlib import Path
import json,hashlib,re,shutil,importlib.util
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'
LOCAL=ROOT/'tools/cod4/immune-feedback-research/helpers/herschel-immune'
MASTER=ROOT/'docs/cod4/audit-20261022/immune-feedback-research'
I='iron431__irons-spells-n-spellbooks';A='baileyholl__Ars-Nouveau';S='ZsoltMolnarrr__SpellEngine'
BASE={I:ROOT/'tools/cod4/immune-feedback-research/sources'/I,A:ROOT/'tools/cod4/armor-acceptance/.work/research-sources'/A,S:ROOT/'tools/cod4/immune-feedback-research/sources'/S}
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
 if repo==A:
  tree=json.loads((BASE[repo]/'tree.json').read_text());assert tree['sha']==commit;assert next(x['sha'] for x in tree['tree'] if x['path']==rel)==blob
  proof='pinned Git tree blob SHA1'
 else:
  entry=next(x for x in pin['files'] if x['path']==rel);assert entry['sha256']==sha(data);proof='pinned archive source.json SHA256 inventory'
  if 'git_blob_sha1' in entry:assert entry['git_blob_sha1']==blob;proof='pinned source inventory SHA256 and Git blob SHA1'
 dest=LOCAL/'sources'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-001-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；本次读取的既有主账中无相同位点。调用包装和同链支持不另计。'})
add('iron-spell-event-friendlyfire-native-result',
 'applyDamage先发布可取消SpellDamageEvent，再按学派抗性缩放；NoKnockback先记目标；召唤归属友伤检查失败可返回false，原生hurt本身也可能返回false。',
 '免疫反馈须挂在明确拒绝原因分支；公共布尔结果不足以还原事件取消、友伤或原生受伤冷却。',
 '没有免疫字/拒绝原因枚举；抗性计算与事件内容只是上下文，不能将减伤认作拒伤。',
 'BlackHole.handleGravity/法术命中→DamageSources.applyDamage→SpellDamageEvent→friendlyfire→LivingEntity.hurt',
 ev(I,'DamageSources','applyDamage'),ev(I,'DamageSources','isFriendlyFireBetween'))
add('iron-one-shot-knockback-uuid-window',
 'ignoreNextKnockback以目标UUID写服务端tick；新写入时清>=10tick旧项。cancelKnockback只在差<=1tick取消并无条件消费对应项。',
 '按目标、短窗口、消费一次的拒控记录可比较；不能把多次击退/一次命中天然等同。',
 '清理仅发生在登记时；没有攻击序号，未来tick下界未校验；这是主动抑制投射物击退，并非Boss免疫。',
 'NoKnockbackProjectile→applyDamage登记→LivingKnockBackEvent→取消并消费',
 ev(I,'DamageSources','ignoreNextKnockback'),ev(I,'DamageSources','cancelKnockback'))
add('iron-post-damage-freeze-eligibility',
 '伤害Post回调按actualDamage吸血；冻结量额外检查target.canFreeze，设置冻结tick为原数+参数*2；点火是另一独立动作。',
 '伤害成功与附带控制资格分开，Boss拒绝冻结不能吞掉已完成伤害反馈。',
 'Post里未检查add冻结果，也没有拒控回执；不意味着所有Post都代表正HP损失。',
 'LivingDamageEvent.Post→postHitEffects→canFreeze→setTicksFrozen',ev(I,'DamageSources','postHitEffects'))
add('iron-summon-source-owner-incoming-rejection',
 'preHitEffects先按SpellDamageSource覆盖postattack invulnerability ticks，再从direct优先/causing来源识别召唤物；目标UUID等summoner即取消，否则按主人SUMMON_DAMAGE缩放。',
 '记录来源层级和实际取消点，区别主人保护、伤害缩放与受伤无敌帧参数。',
 '非Boss策略，不应给友伤目标显示Boss免疫；冷却参数修改在取消前。',
 'LivingIncomingDamageEvent→IMagicSummon归属→取消或伤害倍率',ev(I,'DamageSources','preHitEffects'))
add('iron-incoming-tomb-redirect-fireward',
 '实体伤害命中IceTomb乘客且非友伤时先取消，再将originalAmount转给墓体；Fireward仅ServerPlayer/IMagicEntity佩戴且火源时清火取消。末尾通电苦力怕配置也可取消火伤。',
 '乘客零伤是转移，戒指火保护是来源拒伤；同一事件入口必须保留原因，不能仅看cancel标志。',
 'Evasion/Shroud是主账既有链，本行明确排除，不新增信用；三个新分支作为一个完整入口建议，不拆数。',
 'LivingIncomingDamageEvent→onLivingIncomingDamage→IceTomb.hurt或clearFire/cancel',
 ev(I,'ServerPlayerEvents','onLivingIncomingDamage'),ev(I,'IceTombEntity','hurt'),ev(I,'IceTombEntity','die'),
 dedup='与既有ironspells-authoritative-evasion-and-shroud-native-receipts共享方法但排除其所有Evasion/Shroud分支，仅审伤害转移与来源保护。')
add('iron-heartstop-deferred-settlement-not-immunity',
 'Pre仅IMagicEntity/ServerPlayer有Heartstop时积累originalDamage*0.5并将newDamage置0。移除效果时tickCount>60以HEARTSTOP伤害结算，否则直接kill，最后清积累；客户端心跳按积累/HP缩短间隔。',
 '暂时不扣血可能是延期债务；清除效果不等于无代价解除免疫。',
 '移除回调结算hurt结果未读；spawn immunity分支直接kill是上游特殊做法，不推荐复制；客户端duration为效果对象字段。',
 'LivingDamage.Pre→SyncedSpellData债务→Heartstop.onEffectRemoved结算→applyEffectTick心跳',
 ev(I,'ServerPlayerEvents','onBeforeDamageTaken'),ev(I,'HeartstopEffect','onEffectRemoved'),ev(I,'HeartstopEffect','applyEffectTick'),ev(I,'HeartstopEffect','shouldApplyEffectTickThisTick'))
add('iron-telekinesis-motion-independent-of-status',
 '目标预选后记录距离；每2tick处理，玩家施法者发现目标已死/移除会取消。速度直接setDeltaMovement并hurtMarked；每10tick另加AIRBORNE/ANTIGRAVITY。阻力计算传入施法者entity而非targetEntity。',
 '控制效果拒绝与物理拉动是两条路径；应审最终速度写入，不能仅拦药水。',
 '未见Boss拒控门；min0.2意味着阻力不能完全归零，且用施法者属性是明确反例；不声称上游免疫成功。',
 'checkPreCastConditions→TelekinesisData→onServerCastTick→handleTelekinesis→motion/status writes',
 ev(I,'TelekinesisSpell','checkPreCastConditions'),ev(I,'TelekinesisSpell','onServerCastTick'),ev(I,'TelekinesisSpell','handleTelekinesis'),ev(I,'Utils','clampedKnockbackResistanceFactor'))
add('iron-blackhole-soft-boss-resistance-and-expiry-bypass',
 '常规吸引排owner/友伤/旁观/黑洞，半径筛选后按距离四次方、clamped阻力和Boss0.5缩放；伤害另有10tick/中心区域门。寿终handleClientEffects爆散对缓存近处实体直接加速度，未重复常规过滤。',
 'Boss软抗性不是免控；终止爆散也属于控制生产点，最终边界应覆盖生命周期尾部。',
 '不声称Boss零移动；distance与dmgRadius*dmgRadius比较是源码原样，不代改；方法名ClientEffects包含服务端速度写入。',
 'BlackHole.tick→缓存更新→handleGravity→handleClientEffects寿终爆散',
 ev(I,'BlackHole','tick'),ev(I,'BlackHole','handleGravity'),ev(I,'BlackHole','handleClientEffects'),ev(I,'BlackHole','updateTrackingEntities'))
add('iron-root-cant-root-mount-control',
 'onCast解析目标后以CANT_ROOT标签拒绝创建；允许时生成有HP和duration的Root，先stopRiding再强制startRiding。Root tick超时/目标死亡/失去乘客释放；远距positionRider移除而非拉回。',
 '拒控入口必须发生在卸载坐骑/创建副实体前；控制持续和异常移动应有释放路径。',
 '标签拒绝无专属灰字；不把普通预选成功提示当控制成功；startRiding结果未读。',
 'RootSpell.onCast→tag资格→RootEntity乘客锁定→tick/positionRider→removeRoot',
 ev(I,'RootSpell','onCast'),ev(I,'RootEntity','tick'),ev(I,'RootEntity','positionRider'),ev(I,'RootEntity','removeRoot'))
add('iron-fireboss-parry-authoritative-receipt',
 'hurt仅服务端：交战、parryCooldown<=0、非immobile、有攻击者、非bypass、非攻击动作、来源在前方dot>=0.35，再50%概率格挡；触发动画/匕首/100tickCD/格挡声并false。其他姿态乘数及伤害上限仍进入super。',
 '用确定分支生产格挡反馈；阶段减伤和上限不要显示Immune；保留bypass来源。',
 '这是parry不等于Boss常驻免疫；未运行外部版本；随机与冷却不能由动画存在反推命中。',
 '原生hurt→资格/朝向/随机→parry回执或伤害缩放→super.hurt',ev(I,'FireBossEntity','hurt'))
add('iron-fireboss-stagger-control-rejection',
 'knockback在isStanceBroken时直接return，其他情况走super；push在spawning时不调用super；isPushable恒false。不同控制入口条件不相同。',
 '同一Boss碰撞推挤/受击击退/直接速度必须分开核查，不能以isPushable false代替所有控制拒绝。',
 '三个覆盖合并为一个Boss控制策略，不按薄常量方法拆数；未证明直接速度也被拒绝。',
 '原生collision push/knockback→FireBoss对应覆盖→阶段分支',ev(I,'FireBossEntity','knockback'),ev(I,'FireBossEntity','push'),ev(I,'FireBossEntity','isPushable'))
add('iron-ice-spider-emerging-native-invulnerability',
 'isInvulnerableTo在super之外按EMERGING姿态拒伤；同姿态isImmobile；SyncedData pose变化启动emerge动画并设置EMERGE_TIME。',
 '短阶段拒伤应由原生资格门和同步状态对应，动画只是可见状态，不是免疫来源。',
 '本行记录完整资格/同步方法；不将phase时长常量或bodypart hurt转发另计；未跑动画/计时。',
 '原生伤害资格→isInvulnerableTo→DATA_POSE更新→onSyncedDataUpdated',ev(I,'IceSpiderEntity','isInvulnerableTo'),ev(I,'IceSpiderEntity','isImmobile'),ev(I,'IceSpiderEntity','onSyncedDataUpdated'))
add('iron-frozen-decoy-once-shatter-not-health-hit',
 'hurt客户端/原生invulnerable/ invulnerableTime>0拒绝；允许后设10tick、AOE伤害、8碎片、玻璃声、discard并true，不按amount扣HP；构造器初始1tick保护，定时tick也会调用hurt引爆。',
 'true可能代表消耗诱饵/爆裂，不是HP损失；冷却false也不天然为Boss免疫。',
 '物理自爆链，不是Boss；AOE用友伤/LOS/投射物资格；方法合并不按8碎片计数。',
 'FrozenHumanoid.tick或外部hit→hurt资格→doPuffDamage/spawnIcicleShards→discard',ev(I,'FrozenHumanoid','hurt'),ev(I,'FrozenHumanoid','tick'),ev(I,'FrozenHumanoid','doPuffDamage'),ev(I,'FrozenHumanoid','spawnIcicleShards'))
add('iron-deadking-lava-rejection-distance-reduction',
 'hurt以pSource==level.damageSources().lava()拒绝；窒息时尝试破方块并40tick间隔；有攻击者则8..24格将伤害降至50%，然后super。',
 '来源免疫、逃脱窒息和远距减伤必须区分；对象相等来源条件不能误写成泛火伤。',
 '没有专属拒绝提示；继承类其他门未重建，不把hurt整体所有false解释成此lava分支。',
 'DeadKingBoss.hurt→lava identity gate→distance multiplier→super.hurt',ev(I,'DeadKingBoss','hurt'))
add('iron-apothecarist-potion-and-self-indirect-rejection',
 'canBeAffected直接排AlchemistAttackGoal.ATTACK_POTIONS，未调用super；hurt只拒自身归属INDIRECT_MAGIC。攻击列表为weakness/blindness/levitation/slow/mining fatigue，同AI可投伤害或这些效果。',
 '来源限制与效果列表不同；最终药水资格应核实真实Holder类型和父规则保留。',
 '这里未保留super.canBeAffected可能放行其他父类拒绝；药水音效是投掷声，不是目标拒绝回执。',
 'AlchemistAttackGoal.doSpellAction→ThrownPotion→Apothecarist.canBeAffected/hurt',ev(I,'ApothecaristEntity','canBeAffected'),ev(I,'ApothecaristEntity','hurt'),ev(I,'AlchemistAttackGoal','doSpellAction'))
add('iron-shield-multipart-parent-throttle-false-result',
 'ShieldPart.hurt仅服务端且父hurtThisTick未置时转父takeDamage，然后置标记，始终return false；takeDamage非invulnerable时扣父HP，命中点火花/冲击声；Shield.tick每tick重置去重。',
 '同目标多部件合并应归父实体；false可能已实际扣护盾HP，不能作为Immune。',
 'hurtThisTick不区分攻击者和攻击次数，可能合并同tick不同攻击；拒绝时也置标记；无文字消息。',
 '命中ShieldPart→parent.takeDamage→health/impact→ShieldEntity.tick重置',ev(I,'ShieldPart','hurt'),ev(I,'ShieldEntity','takeDamage'),ev(I,'ShieldEntity','tick'))
add('ars-wilden-phase-and-defense-rejection',
 'hurt先拒仙人掌/浆果/窒息/熔岩/溺水，冻伤减半；phaseSwapping直接false；defensive可先反射近距非穿甲伤害再拒本体伤害；自己召唤来源拒绝；通过super后按25%阶段阈值抬HP并换阶段。',
 '阶段拒伤、反伤、来源资格和生命阈值截断须区分，不能看到BossHP不降就统一Immune。',
 '同一完整hurt方法诸分支合并一条，不拆同名Boss/阶段；源码有entity/entity1混用，按实际表达式记录。',
 'WildenChimera.hurt→环境/阶段/来源→defense反伤→super→phase clamp',ev(A,'WildenChimera','hurt'))
add('ars-wilden-effect-check-is-not-application',
 'canBeAffected先effect=value；Snare判断却是instance.getEffect() instanceof SnareEffect（Holder而非value）；slow和gravity只给局部instance重新赋值，再调用super资格。不能据此证明最终addEffect对象被缩短。',
 '这是资格查询不能变更调用者对象的反例；免疫/缩短时长需在实际施加路径验证。',
 '不作为有效拒控实现建议：Snare类型判断和局部重赋值都存在证据问题；未运行/编译外部仓库。',
 'LivingEntity效果资格→WildenChimera.canBeAffected→super；IPotionEffect.applyPotion的原对象未被替换',ev(A,'WildenChimera','canBeAffected'),ev(A,'IPotionEffect','applyPotion'),status='support_only_not_effective',dedup='代码完整读过，但不能证明有效Snare拒绝/时长缩短；0信用，不用方法名补数。')
add('ars-rewind-blacklist-start-and-record',
 'onResolveEntity排REWIND_BLACKLIST/非IRewindable/已rewinding后才delay并入队；Player才发附近倒带效果包。shouldRecordData客户端只记Player，关闭功能/黑名单/已倒带不记历史。',
 '开始控制与历史记录要共享资格；Boss黑名单不能仅阻止一侧；玩家专用视觉与Boss策略分开。',
 '拒绝无免疫字；已有倒带属于重复申请不一定免疫；tag数据需随上下文核实。',
 'EffectRewind.onResolveEntity→IRewindable→RewindEvent队列；实体历史→shouldRecordData',ev(A,'EffectRewind','onResolveEntity'),ev(A,'EffectRewind','shouldRecordData'),ev(A,'EntityTagProvider','addTags'))
add('ars-exchange-nonatomic-two-target-teleport-gates',
 '交换前拒TELEPORTING_NOT_SUPPORTED或FakePlayer；分别向shooter与living目标发EnderTeleport事件并独立决定两次teleport，事件拒绝可能造成只交换一半。',
 '同次双目标控制要区分每一目标的结果；不能把一个事件通过当整次交换成功。',
 '不是灰字生产；非living目标绕过Ender事件检查；与Blink共用底层事件但这里多实体非原子语义独立。',
 'EffectExchange.onResolveEntity→caster Ender hook→caster teleport→target Ender hook→target teleport',ev(A,'EffectExchange','onResolveEntity'))
add('ars-blink-qualified-warp-and-feedback-order',
 'onResolveEntity先拒不可传送tag，再分炮塔卷轴、自身前闪、玩家卷轴/定位施法者、符文。warpEntity的living分支先Ender事件；Level重载通过后才发portal粒子、teleport、gameEvent、位置包和声音。',
 '成功反馈应在最终资格与可用维度之后；预选命中不等于目标传送；服务端位置与反馈接收要对应。',
 '两个warp重载同链不拆；onResolveEntity无卷轴路径移动施法者，不应给目标误发被控制成功；无免疫字。',
 'onResolveEntity→warpEntity或blinkForward→Ender hook→teleport→PacketWarpPosition/FX',ev(A,'EffectBlink','onResolveEntity'),ev(A,'EffectBlink','warpEntity','WarpScrollData'),ev(A,'EffectBlink','warpEntity','Level level'),ev(A,'EffectBlink','blinkForward'))
add('ars-snare-status-rejection-does-not-stop-motion-write',
 'Snare对Living先applyConfigPotion，再不读结果直接归零速度并hurtMarked；非living可落地EnchantedFallingBlock。IPotionEffect最终addEffect的boolean被丢弃；SnareEffect减速属性为-1 total。',
 '只拒药水无法阻止一次归零速度，Boss免控必须覆盖这次实际写入；属性成功也不能反证伤害结果。',
 '负例/实际控制生产点，没有Boss拒绝门；Potion helper薄包装随主链支持，不另计。',
 'EffectSnare.onResolveEntity→IPotionEffect.applyPotion/addEffect→无条件motion ZERO',ev(A,'EffectSnare','onResolveEntity'),ev(A,'IPotionEffect','applyPotion'))
add('ars-knockback-resistance-final-motion-gate',
 'onResolveEntity经方向计算重载到最终knockback(Entity,double,..)，living strength乘1-resistance，仅strength>0时写hasImpulse及速度；调用方无条件hurtMarked。',
 '最终物理写入门可以明确说明阻力1导致无位移；拒绝运动与网络脏标记不是一回事。',
 '伤害系统未调用，零强度也可能来自配置或负amp；不能将每个不动目标都叫Boss免疫。',
 'EffectKnockback.onResolveEntity→caster/turret方向→final strength gate→setDeltaMovement',ev(A,'EffectKnockback','onResolveEntity'),ev(A,'EffectKnockback','knockback','IWrappedCaster'),ev(A,'EffectKnockback','knockback','double strength'))
add('ars-damage-pre-post-receipt-is-not-actual-hp-delta',
 'attemptDamage先dead/ally资格，计算perk/random伤害和luck，再发可改source/damage的Pre；非正量或cancel拒绝；原生hurt false拒绝；true后setLastHurtMob并Post。',
 '明确取消原因应在Pre/资格处保留；Post记录totalDamage不是实际扣HP，不能用它绘实际伤害数字。',
 '公共attemptDamage false覆盖多原因，仍无免疫回执；仅读源码未运行。',
 'ColdSnap/Flare→IDamageEffect.attemptDamage→Pre→Entity.hurt→Post',ev(A,'IDamageEffect','attemptDamage'),ev(A,'IDamageEffect','canDamage'))
add('ars-dispel-pre-deny-allow-and-post-order',
 '实体Dispel先发Pre可取消；将activeEffects快照；可牛奶清除项遇deny跳过，否则移除，不可牛奶项可allow强制移除；死亡/移除检查在效果遍历之后，存活才IDispellable及Post。',
 '清除失败不等于目标整体免疫；结果可能按每种效果不同，Post不能保证每个效果都被清除。',
 '源码blacklist比较effect.value()==e.getEffect存在value/Holder层级不一致疑点，只静态记录不声称deny实际生效；block同模板不计。',
 'EffectDispel.onResolveEntity→DispelEvent.Pre→effect cure/tag filters→onDispel→Post',ev(A,'EffectDispel','onResolveEntity'))
add('ars-coldsnap-prerequisite-vs-hit-and-snare',
 'ColdSnap仅server Living且wet/rain/slow/frozen才继续；damage仅attemptDamage成功才发SPIT并加Snare，但onResolveEntity无论伤害成功与否仍spawnIce，原有FREEZING还直接setTicksFrozen。',
 '前置资格不满足与免疫不同；命中拒伤后仍可能产生碎片/冻结，不能把一个boolean当整个法术结果。',
 'Snare addEffect结果忽略；碎片独立命中需另审，本行不声明已完成所有碎片路径。',
 'onResolveEntity→canDamage条件→damage/attemptDamage→spawnIce→conditional freeze',ev(A,'EffectColdSnap','onResolveEntity'),ev(A,'EffectColdSnap','canDamage'),ev(A,'EffectColdSnap','damage'),ev(A,'EffectColdSnap','spawnIce','spawnIce(Level level'))
add('ars-flare-analogue-to-coldsnap-no-extra-credit',
 'Flare需fire/BLAST/站火上；damage成功才烟粒子，但无论该结果均spawnCinders；BLAST存在则remove后explode。与ColdSnap共同骨架且同attemptDamage结果不传播。',
 '支持“主伤害失败不代表附带动作都拒绝”的比较；BLAST消耗爆炸与主hit语义分开。',
 '与ColdSnap高度同构，不作为新有效实现推荐；完整方法已读保留支持，不用元素换皮补数。',
 'Flare.onResolveEntity→prerequisite→attemptDamage→cinders/consume BLAST',ev(A,'EffectFlare','onResolveEntity'),ev(A,'EffectFlare','canDamage'),ev(A,'EffectFlare','damage'),status='support_only_not_effective',dedup='ColdSnap相同模版降支持；火元素条件差异不足以独立晋级。')
add('ars-gravity-duration-vs-direct-motion-control',
 'Gravity有ExtendTime则apply potion，无则直接Y速度加-1-amp并hurtMarked；GravityEffect在非地面持续下拉，Player距地<=2不下拉；PlayerPost且非creative禁flight，fall Pre双倍伤。',
 '瞬时速度与持续效果/飞行资格/摔伤倍率是不同结果，不可仅拦药水后说免控；玩家creative例外不能复制成Boss例外。',
 '方法链合并一条；下拉本身无Boss过滤，也非伤害拒绝回执；没有客户灰字。',
 'EffectGravity.onResolveEntity→direct motion 或 IPotionEffect→GravityEffect.tick/playerPost/damagePre',ev(A,'EffectGravity','onResolveEntity'),ev(A,'GravityEffect','applyEffectTick'),ev(A,'GravityEffect','entityTick'),ev(A,'GravityEffect','entityHurt'))
add('ars-rewind-control-lifecycle-crossdimension-cleanup',
 'RewindEvent tick首次服务端注册登出/换维度监听，置rewinding并弹历史，锁当前时间执行回调防重入；累计ticks满stop清rewinding、速度与失重；换维度清历史，登出移除失重并unregister。',
 '控制生命周期结束、换维度和登出清理应核实；事件入队不是长期成功回执。',
 '没有灰字；logout分支未显式stop/expired，stop未统一注销监听；保留风险，不声称完整无泄露；与起始资格条按生命周期独立。',
 'EffectRewind→EventQueue→RewindEvent.tick→stop/onChangeDimension/onEntityRemoved→removeWeightlessness',ev(A,'RewindEvent','tick'),ev(A,'RewindEvent','stop'),ev(A,'RewindEvent','onChangeDimension'),ev(A,'RewindEvent','onEntityRemoved'),ev(A,'RewindEvent','removeWeightlessness'))
add('iron-precast-target-feedback-not-control-success',
 'preCastTargetHelper真实Raycast检查blocks，识别PreventDismount乘客/普通活体/Multipart父。成功存target并给caster GREEN actionbar/非instant targeting包，目标若ServerPlayer发target通知；失败RED actionbar。PreventDismount分支未应用传入filter。',
 '这是目标锁定回执，不是控制落地；Boss后续CANT_ROOT拒绝时不能复用绿色消息当成功。实体父锚点与player定向通知可比较。',
 'wrapper重载不计；Root/Telekinesis之前已引用作为支持，本条仅独立审核预选反馈生产和父锚点解析，不重复计算控制写入。',
 '法术checkPreCast→Utils.preCastTargetHelper最终重载→target存储→actionbar/target同步',ev(I,'Utils','preCastTargetHelper','Predicate<LivingEntity>'),ev(I,'Utils','sendTargetedNotification'))
assert len(rows)==30
# Three entrypoints were fully read, but Protection/EntityActionsAllowed bodies
# are absent from this selected local snapshot: do not promote signatures/hooks.
support_only=[{'reason':'selected cache lacks called Protection.tryProtect implementation; no complete authority chain', 'research_credit':0,'suggested_credit':0,'source_ref':ev(S,'PlayerProtectionEffectMixin','isInvulnerable_SpellEngine')},
 {'reason':'selected cache lacks EntityActionsAllowed.isImpaired; attack HEAD interception alone does not prove effect decision', 'research_credit':0,'suggested_credit':0,'source_ref':ev(S,'PlayerEntityActionImpairing','attack_HEAD_SpellEngine')},
 {'reason':'selected cache lacks EntityActionsAllowed.isImpaired; subsequent SpellChoices branch can replace FAIL with SUCCESS after cancellation (no explicit return)', 'research_credit':0,'suggested_credit':0,'source_ref':ev(S,'ServerPlayerInteractionManagerMixin','interactItem_HEAD_SpellEngine')}]
# Tag resource is support only, not another implementation.
resource_rel='src/main/resources/data/irons_spellbooks/tags/entity_type/cant_root.json'
resource_data=(BASE[I]/resource_rel).read_bytes()
assert next(x['sha256'] for x in meta[I]['files'] if x['path']==resource_rel)==sha(resource_data)
resource_dest=LOCAL/'sources'/I/resource_rel;resource_dest.parent.mkdir(parents=True,exist_ok=True);resource_dest.write_bytes(resource_data)
verified[f'{I}/{resource_rel}']={'repo':meta[I]['repo'],'commit':meta[I]['commit'],'path':resource_rel,'sha256':sha(resource_data),'computed_git_blob_sha1':hashlib.sha1(b'blob '+str(len(resource_data)).encode()+b'\0'+resource_data).hexdigest(),'proof':'pinned archive source.json SHA256 inventory','local':str(resource_dest.relative_to(ROOT))}
rows[8]['source_refs'].append({'source_key':f'{I}/{resource_rel}','unit':'complete_support_resource','lines':[1,len(resource_data.decode().splitlines())],'url':f"https://github.com/{meta[I]['repo']}/blob/{meta[I]['commit']}/{resource_rel}",'file_sha256':sha(resource_data),'excerpt_sha256':sha(resource_data),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',resource_data.decode()).encode()),'excerpt':resource_data.decode()})
rows[8]['observation']+=' 固定资源cant_root.json实际包含#c:bosses（replace false）。'
rows[18]['observation']+=' EntityTagProvider.addTags将WILDEN_BOSS列入c:bosses，并将bosses纳入rewind blacklist。'
# Fixed local source metadata copied only under helper ownership. No main source writes.
for repo in BASE:
 d=LOCAL/'sources'/repo;d.mkdir(parents=True,exist_ok=True)
 shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo==A:shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
# Per-batch exact and whitespace duplicate check of PRIMARY complete methods. Support shared by chains is deliberately allowed.
seen={};duplicates=[]
for row in rows:
 ref=row['source_refs'][0];k=ref['normalized_excerpt_sha256']
 if k in seen:duplicates.append([seen[k],row['id']])
 seen[k]=row['id']
assert not duplicates,duplicates
batch={'schema_version':1,'batch':'herschel-immune-001','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'master_credit_unchanged':True,'scope':'read-only fixed local Minecraft sources; no external code executed; no game/server/client launched','rows':rows,'additional_support_only_entrypoints':support_only}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'batch-001.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-001.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'iron_proof_limit':'Iron source bytes checked against pinned archive SHA256 inventory; no matching Git tree cached, computed blob hashes are not independently tree-verified. Ars each blob independently matches pinned tree.','metadata':{k:{x:v for x,v in meta[k].items() if x not in ('files',)} for k in meta}},ensure_ascii=False,indent=2)+'\n')
after={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()}
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','reviewed_units':30,'pending_primary_semantic_review':28,'support_only':2,'effective_credit':0,'research_credit':0,'suggested_credit':0,'unique_source_files':len(verified),'complete_method_references':sum(1 for r in rows for x in r['source_refs'] if x.get('unit')!='complete_support_resource'),'support_resource_references':1,'additional_support_method_references':3,'primary_exact_and_normalized_duplicates':duplicates,'master_files_unchanged_during_build':before==after,'master_hashes_before':before,'master_hashes_after':after,'batch_sha256':sha((OUT/'batch-001.json').read_bytes()),'production_modified':False,'todo_modified':False,'game_launches':0,'external_requests':0,'semantic_review':'Human-authored observations. Hash matching is integrity evidence only, not semantic credit.'}
(OUT/'receipt-001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if not k.startswith('master_hash')},ensure_ascii=False))
