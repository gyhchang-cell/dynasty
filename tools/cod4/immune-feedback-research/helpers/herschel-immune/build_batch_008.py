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
B='BluSunrize__ImmersiveEngineering';U='Quek04__The-Undergarden';E='DaedalusGame__EmbersRekindled'
BASE.update({k:ROOT/'tools/cod4/immune-feedback-research/sources'/k for k in (B,U,E)})
M='DrZhark__mocreaturesdev'
BASE[M]=ROOT/'tools/cod4/immune-feedback-research/sources'/M
P='MachineMuse__MachineMusePowersuits'
BASE[P]=ROOT/'tools/cod4/immune-feedback-research/sources'/P
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
 if (BASE[repo]/'tree.json').exists():
  tree=json.loads((BASE[repo]/'tree.json').read_text());assert tree['sha']==commit;assert next(x['sha'] for x in tree['tree'] if x['path']==rel)==blob
  proof='pinned Git tree blob SHA1'
 else:
  entry=next(x for x in pin['files'] if x['path']==rel);assert entry['sha256']==sha(data);proof='pinned archive source.json SHA256 inventory'
  if 'git_blob_sha1' in entry:assert entry['git_blob_sha1']==blob;proof='pinned source inventory SHA256 and Git blob SHA1'
 dest=LOCAL/'sources-batch008'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'unit':'complete_support_resource' if method=='__complete_file__' else 'complete_method','source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-008-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与001–007及当前主账按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
def span(repo,name,start,end,label):
 ref=ev(repo,name,'__complete_file__');lines=ref['excerpt'].splitlines(keepends=True);excerpt=''.join(lines[start-1:end]);ref.update(method=label,lines=[start,end],excerpt=excerpt,excerpt_sha256=sha(excerpt.encode()),normalized_excerpt_sha256=sha(re.sub(r'\s+','',excerpt).encode()));ref['url']=ref['url'].split('#')[0]+f'#L{start}-L{end}';ref['resource_scope']='complete nested declaration or complete registration statement; not a counted method';return ref


add('ie-faraday-per-hit-slot-bitset-low-voltage-denial-high-voltage-reversal',
 'FaradaySuitItem.onStrike仅处理ElectricDamageSource。source.level<1.75时把this.type.ordinal对应bit OR进本次共享cache，等于15才把同一dmg.dmg清零；高电压分支反而每件乘1.2并在非创造时耗耐久2。IElectricEquipment.applyToEntity每次新建cache，遍历所有EquipmentSlot，持有实现接口的物品也调用。ElectricDamageSource.apply先跑装备，再仅dmg>0才调用原生hurt。注册排除BODY的四个Faraday甲型。',
 '具体免疫必须记清来源级别与完整装备组合；同一装备面对另一来源可增伤。按本次命中建立的部件位图区别持久计数，不把四件模板拆信用。',
 '静态未运行；门使用物品type而非eqSlot验证，不能声称代码强制必须在正确防具槽。高压耐久回调传入的是dmg.getEntity转ServerPlayer，不是owner；此电源构造super(tag)不带攻击者，不能声称必产生耐久动画回执。此处清零意味着不调hurt，不产生独立灰字。',
 '实际EventHandler原生LivingDamageEvent.Pre反击/IEShield.hitShield→causeTeslaDamage→ElectricDamageSource.apply→IElectricEquipment逐槽onStrike→Faraday bitmask→dmg=0拒hurt；IEItems实际四件注册',
 ev(B,'FaradaySuitItem','onStrike'),ev(B,'IEDamageSources','apply'),ev(B,'IEDamageSources','ElectricDamageSource'),ev(B,'IEDamageSources','causeTeslaDamage'),ev(B,'IElectricEquipment','applyToEntity'),ev(B,'EventHandler','onLivingAttacked'),ev(B,'IEShieldItem','hitShield'),span(B,'IEItems',332,336,'four_Faraday_types_registration'),ev(B,'ImmersiveEngineering','ImmersiveEngineering'),ev(B,'ImmersiveEngineering','setup'),
 dedup='新来源强度阈值/本次槽位mask聚合/高压反转家族合1；不重复Botania mana减伤/Goety ward点消费，也不按四件护甲分数。')
add('ie-electric-retaliation-boolean-is-positive-post-equipment-budget-not-native-hurt-receipt',
 'ElectricDamageSource.apply先改写dmg，dmg>0才调用e.hurt，但完全不读hurt的bool，最终返回dmg>0。实际onLivingAttacked的TESLA背包反击对近距Living、可模拟取够整笔能量时先扣费；if(apply(attacker))才尝试STUNNED60，但即使原生拒伤，只要装备未清零仍进此分支。spark声音在整次供能分支内无条件产生。注释说33%，实际该分支没有概率门。',
 '检查实际返回语义比看apply命名可靠；正伤害预算/原生接纳/控制状态接纳是三件事。声音和扣费只能证明尝试发生。',
 '与上一条同链支持方法共享，独立提出的是实际反击消费者误把budget bool作为命中门。STUNNED状态定义本缓存缺失，不能推定原生动作被禁；只证明addEffect被尝试且其bool未读。未实机复现任何伤害绕过。',
 '@Mod构造注册setup→setup注册EventHandler→LivingDamageEvent.Pre→onLivingAttacked背包TESLA→能量模拟/扣除→ElectricDamageSource.apply budget bool→STUNNED尝试与spark声',
 ev(B,'IEDamageSources','apply'),ev(B,'EventHandler','onLivingAttacked'),ev(B,'IElectricEquipment','applyToEntity'),ev(B,'IEDamageSources','causeTeslaDamage'),ev(B,'ImmersiveEngineering','setup'),ev(B,'ImmersiveEngineering','ImmersiveEngineering'),
 dedup='不是为同电源包装再计：上一条是Faraday最终拒伤生产，本条是具体反击反馈消费者的返回值边界；与Ars SpellDamageEvent.Post不等HP差同为回执风险但这里有实际budget bool触发眩晕源。主岗仍可合并。')
add('ie-shock-shield-projectile-destruction-and-damage-zero-with-contact-retaliation',
 '真实onLivingAttacked仅Player正在用IEShield、originalDamage>=3且Utils.canBlockDamageSource通过时调用hitShield。该方向门要求非BYPASSES_ARMOR、isBlocking、来源位置非null和水平点积<0。SHOCK升级非冷却时若projectile tag且directEntity存在，直接discard投射物并newDamage=0；近距Living来源另外调用电伤。任一动作发生便写Cooldown40并spark声，不依电伤apply结果。FLASH独立分支可先给锥内非自身目标FLASHED100/amp1并清Mob target。',
 '最终拒绝可同时消灭载体和置零当前伤害，两者要分别留证；来源位置、方向和伤害阶段影响是否能进入，不凭持盾外观推定免疫。',
 '静态非原生运行。Pre是否会在所有原版已格挡路径调用未验证，不能声称全部弹丸/格挡必触发；不是取消原生damage方法。hitShield本身没有再次核对玩家方向。FLASH addEffect结果未读，清target不依状态接纳；仅现存行为，不转守卫账。',
 'IEItems.SHIELD注册→IEShieldItem.use/startUsingItem→原生LivingDamageEvent.Pre→EventHandler.onLivingAttacked→Utils方向门→hitShield→discard+setNewDamage0+升级cooldown/sound',
 ev(B,'IEShieldItem','hitShield'),ev(B,'EventHandler','onLivingAttacked'),ev(B,'Utils','canBlockDamageSource'),ev(B,'IEShieldItem','use'),ev(B,'IEShieldItem','getUseAnimation'),span(B,'IEItems',301,301,'shield_registration'),ev(B,'ImmersiveEngineering','setup'),
 dedup='不同于已有原版方向格挡家族：具体Pre入口消灭direct projectile并清零当前container，附独立反击/升级冷却；方向判定包装不另计。')
add('spellengine-native-shield-contact-receipt-before-durability-and-player-source-filter',
 'LivingEntityEvents.damage_WRAP_damageShield在原生damage调用damageShield(F)的位置派发ENTITY_SHIELD_BLOCK、Player另派PLAYER_SHIELD_BLOCK，然后才original.call消耗耐久。SpellTriggers.init实际注册玩家监听；onShieldBlock没有attacker就直接return，否则把source/critical/damageAmount填入SHIELD_BLOCK事件，交fireTriggers先走stash后passive。没有依据最终health变化再生成该格挡事件。',
 '格挡回执来源应是实际格挡接触点，不是零伤推测；先于耐久结算，不能表示盾未破。没有攻击实体的环境来源对全部实体事件与玩家被动消费策略不同。',
 'Java静态链，未原生运行。记录的是当前原生调用位置契约，不把注释“first”当所有版本保证；不证明外部装备配置真的装了SHIELD_BLOCK法术。已有stash/trigger限额逻辑仅支持，不加信用。',
 '原生LivingEntity.damage→damageShield WrapOperation→PLAYER_SHIELD_BLOCK→SpellTriggers.init listener→onShieldBlock(攻击者门)→fireTriggers→既有SpellStashHelper/useStashes和passive',
 ev(S,'LivingEntityEvents','damage_WRAP_damageShield'),ev(S,'SpellTriggers','onShieldBlock'),ev(S,'SpellTriggers','init'),ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellEngineMod','init'),
 dedup='具体原生格挡接触回执生产点与007 stash尝试扣层独立；不为泛型CombatEvents或damage RETURN包装计数，不重复既有evasion事件。')
add('undergarden-forgotten-guardian-peaceful-native-damage-denial-with-bypass',
 'ForgottenGuardian.hurtServer在传入ServerLevel的PEACEFUL难度且非creativePlayer来源、非BYPASSES_INVULNERABILITY时立即false；其他情况交super。checkDespawn先交EventHooks且若未拦截仅清noActionTime；实体注册带notInPeaceful，不能据此推断切难度后根本不会有Boss。canBeAffected无条件false另为固定状态免疫模板支持。',
 '区分世界难度拒绝与伤害来源特权，明确拒绝可在原生hurtServer最前端发生；只在环境变化时生效的保护不应描述成永久无敌。',
 '无原生服务/GUI。读取的是新版本hurtServer API，不复制至本项目1.20.1。未核查原版notInPeaceful与EventHooks运行交互，不保证自然生成/切难度实体存续；本门没有灰字/声音。',
 'UGEntityTypes实际registerWithEgg→registerWithPlacement→registerWithAttributes构造ForgottenGuardian；原生hurtServer→difficulty/source bypass判定→false或super；原生checkDespawn独立',
 ev(U,'ForgottenGuardian','hurtServer'),ev(U,'ForgottenGuardian','checkDespawn'),ev(U,'ForgottenGuardian','canBeAffected'),span(U,'UGEntityTypes',92,92,'ForgottenGuardian_registration'),ev(U,'UGEntityTypes','registerWithEgg'),ev(U,'UGEntityTypes','registerWithPlacement'),ev(U,'UGEntityTypes','registerWithAttributes'),
 dedup='独立世界难度+creative/bypass原生拒伤策略，非换名字复用phase/来源tag固定模板；无条件状态拒绝不单算。')
add('embers-powered-tool-native-damage-refusal-uses-cached-state-and-deferred-charge',
 'Embers.preInit实际注册EventManager。onEntityDamaged仅trueSource为Player且主手非空进入工具逻辑；IEmberChargedTool且非creative并hasEmber=false则取消LivingHurtEvent。未取消且amount>0才setFire，server发EmberBurstFX并设didUse。真实ItemClockworkAxe.hasEmber读NBT poweredOn；onUpdate每5次更新才以总Ember>5刷新poweredOn，didUse为bool，后续更新统一removeEmber5并在余量<5关机。',
 '原生拒伤前的资源门可能只是缓存状态；同tick多次尝试可被单个didUse标记合并，而不是严格每击原子扣费。预伤事件发的FX不能当最终HP伤害凭据。',
 '静态未运行，不宣称已复现免费多击。MessageEmberBurstFX源码本地缺，因此发包之后的client显示/维度过滤/TTL未验证，不将该缺失链计作完整浮字实现。getEmberTotal的可选Baubles实现未展开，不保证所有兼容资源路径；此候选只限实际工具最终事件取消与延后消费边界。',
 '@Mod Embers.preInit注册EventManager→原生LivingHurtEvent→onEntityDamaged→ItemClockworkAxe.hasEmber缓存门→取消或正amount点燃/FX发送/didUse→原生Item.onUpdate消耗；RegistryManager实际构造axe_clockwork',
 ev(E,'EventManager','onEntityDamaged'),ev(E,'ItemClockworkAxe','hasEmber'),ev(E,'ItemClockworkAxe','onUpdate'),ev(E,'EmberInventoryUtil','getEmberTotal'),ev(E,'EmberInventoryUtil','removeEmber'),ev(E,'Embers','preInit'),span(E,'RegistryManager',383,383,'clockwork_axe_registration'),ev(E,'IEmberChargedTool','__complete_file__'),
 dedup='具体攻击资源缓存+didUse延后合并结算，不按每种Clockwork工具拆账，不把缺失的FX接收器当第二条；与Faraday per-hit cache不同，需主岗最终判相关性。')
add('ie-shield-rearm-energy-lifecycle-support-not-wall-clock-expiry',
 'IEShield.inventoryTick仅server；主手inHand参数加offhand同一对象判断，若不在手或实体不blocking才处理FLASH/SHOCK。每个冷却只有模拟取10能量恰够，才真扣10并cooldown.tick后写回UPGRADE_DATA；无能量/持盾格挡时不会按tick自然消失。hitShield成功动作写40。',
 '具体效果重新可用时间应按真正资源条件计算，40不能直接标成2秒墙钟CD。声效节流不能只看显示数字。',
 '通用装备冷却生命周期在Boss灰字范围关联有限，本条主动支持0。Cooldown定义本缓存未读，不能把tick语义更精确推定到零/负值；没有实际计时，不称等待已通过。',
 'hitShield→写FLASH/SHOCK Cooldown40→原生inventoryTick→装备/格挡门+10energy→tick/写component',
 ev(B,'IEShieldItem','inventoryTick'),ev(B,'IEShieldItem','hitShield'),status='support_only_not_effective',dedup='同电盾具体免疫链辅助生命周期，不为普通冷却组件/数据写回再计。')
add('ie-flashed-camera-effect-fog-consumer-support-with-missing-status-registration',
 '真实hitShield FLASH分支给锥内Living（除player）尝试FLASHED100/amp1；ClientEventHandler.onFogUpdate仅当前camera entity有该状态才以duration/amplifier计算fog起终距，末20tick按farPlane插值恢复；onFogColourUpdate同门把RGB都置1。不是按攻击者或最近Boss全局覆盖。',
 '特效消费者须锚定真正受影响对象，生命周期读状态剩余时间；其强制白雾是本项目禁止随意改相机方向之外的另一设计差异，也不拿来制作。',
 '支持0：缓存缺IEPotions定义/客户端注册链，不能宣称效果真实运行或完整接收链已验证；也不是浮字拒绝回执。只读源码，没有启动/修改任何相机。',
 '原生Pre→hitShield addEffect FLASHED（未读bool）→缺原生状态同步/注册证据→两client fog事件当前camera entity状态门',
 ev(B,'ClientEventHandler','onFogUpdate'),ev(B,'ClientEventHandler','onFogColourUpdate'),ev(B,'IEShieldItem','hitShield'),status='support_only_not_effective',dedup='不把白色常量/两个fog函数拆参考；客户端链缺口主动0。')
add('ie-endrod-enderman-special-source-support-missing-railgun-native-hit-consumer',
 'RailgunProjectiles.register真实EndRod匿名实现对EnderMan返回双倍基础伤；getDamageSource先尝试STUNNED200，再按shooter UUID是否能解析当前world Player选择不同damage type，构造Source以Player作为directEntity而causingEntity为null。非EnderMan返回null。',
 '改变source归属可以改变原版免弹语义；应核对hurt最终消费者后才能判定绕过成功，不能根据方法名/眩晕尝试推断。',
 '支持0：本固定缓存缺RailgunShotEntity原生命中实现及STUNNED定义，未补下载，无法证明特殊source确被消费。两个damage type命名与选择相反，不能自行纠正后陈述；这里只按代码记录，不报运行bug。',
 'RailgunProjectiles.register EndRod配置→匿名getDamage/getDamageSource→缺RailgunShotEntity实际命中消费→不提升',
 ev(B,'RailgunProjectiles','register'),status='support_only_not_effective',dedup='整个弹药注册方法只是完整包含证据；只观察EndRod分支不把材料/弹药颜色或匿名包装逐条计。')

# Final manual semantic dedup against immutable master reviewed_utc 2026-10-26.
for i in (0,1,2,4,5):
 rows[i]['status']='support_only_not_effective'
 rows[i]['deduplication']='已与主账2026-10-26既有IE电盾/Faraday/Undergarden和平/Embers缓存资源链全文语义核对，包含bool非hurt结果细节，整体支持0，不再申请晋级。原观察保留便于核对；源文件/方法计数不加信用。'
add('spellengine-native-poison-health-floor-and-fixed-cadence-not-invulnerability',
 'PoisonEffectMixin在原生PoisonStatusEffect.applyUpdateEffect内包装damage调用：amount*(amplifier+1)后取min(该值,entity.health-1)，将结果仍交原生damage。另canApplyUpdateEffect HEAD直接以duration%25==0替换原返回，require=0；不是来源标签免疫或控制抗性。既有固定commit common mixins资源web全文明确列effect.PoisonEffectMixin。',
 '区分保留1HP的伤害上限与完全取消伤害；回执应读本次调用结果，不能以固定间隔/预期非致死笼统标免疫。',
 'Java+先前网页观察，未运行且没有本次外部请求。只有上界，没有Math.max(0)下界；health<1时可能传负amount，不声称实际原版一定接纳负伤害或回血。require0允许该Inject缺失时静默不应用，Mixin启用资源只有已保存转录支持，不冒称原始HTTP字节blob验证。',
 '原生PoisonStatusEffect.canApplyUpdateEffect→25tick门；原生applyUpdateEffect→damage WrapOperation→amp放大/health-1上限→original.damage返回值；固定common mixin清单列入该类',
 ev(S,'PoisonEffectMixin','applyUpdateEffect_SpellEngine'),ev(S,'PoisonEffectMixin','canApplyUpdateEffect_SpellEngine'),ev(S,'PoisonEffectMixin','__complete_file__'),
 dedup='与007 Iron毒伤时间标记免打断完全不同：本条改写原生毒伤金额与周期；一个具体非致死结算门，周期包装不另计。')
add('spellengine-harmful-velocity-resistance-suppresses-reset-and-positive-impact-receipt',
 'performImpact VELOCITY用LOOK或ORIGIN构造水平坐标系加世界y，再按基础power确定性缩放。只有intent HARMFUL且Living才乘1-knockbackResistance；只有最终impulse.lengthSquared()>0才PRE触发、可选reset_velocity清原速度、addVelocity、velocityModified=true并success=true。完全抗击退使零向量时，连reset也不发生。HELPFUL不走抗击退，非Living不读该属性。',
 '拒控门应位于清速度等副作用之前；零冲量不应误当控制成功。帮助性自发起位移与敌对推动可有不同资格，不等同状态免疫。',
 '框架实际分支未配置/运行一个外部具体技能，不推定Boss/玩家实际移动。直接velocity路径没有在这里调用StatusEffectClassification或Boss tag；仅属性门，不能据Boss免状态声称免推动。impulse为NaN时比较>0也不通过，此静态点不当输入漏洞复现。',
 'SpellDelivery→SpellImpacts.performImpacts→完整performImpact关系/条件门→VELOCITY intent属性缩放与非零门→原生速度写入+同步标记→success门声光/延迟POST',
 ev(S,'SpellImpacts','performImpact'),ev(S,'SpellImpacts','performImpacts','boolean additionalTargetLookup'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'ParticleHelper','sendBatches','Entity trackedEntity, List<ParticleGroup> effects, float'),ev(S,'SoundHelper','playSound','Entity entity'),
 dedup='004 harm_knockback_multiplier标志无实际读取降0，与本条实际VELOCITY属性拒绝门不同；Ars直接motion旁路只作对照，本条明确先抗性再副作用。完整performImpact是共享包含证据，不把整方法再次计数。')
rows[-1]['decision_focus']={'lines':[779,830],'counting_rule':'Only actual HARMFUL resistance/nonzero impulse gate before reset and success feedback; complete containing method is shared with 004/005/007, not an extra count for the entire method.'}
add('spellengine-damage-ignored-native-result-still-feedback-and-offset-knockback',
 'performImpact DAMAGE调用target.damage后没有读bool。随后对Living弹出knockback multiplier并恢复timeUntilRegen，若context.hasOffset仍takeKnockback，最后无条件success=true。success共享尾部据此发目标粒子/声/模型，并对targetWasAlive且Player caster排schedule0 POST；targetWasAlive在行动前取样。原生拒伤不能阻止这些正向回执和offset击退尝试。',
 '应区分伤害尝试成功与最终目标接纳；免伤可与位移副作用并存，战斗浮字不能从该success直接标注有效伤害。PRE/POST命名也不是HP变化凭据。',
 '静态框架观察，无原生运行。takeKnockback还可能有原生抗性，不宣称实际推动；也不能由damage false推断具体免伤原因。恢复timeUntilRegen会覆盖本次调用改变，但未比较原版行为，不报已复现可利用问题。没有配置具体伤害法术。',
 'SpellDelivery实际deliver→SpellImpacts.performImpacts→performImpact DAMAGE→target.damage bool忽略→offset knockback尝试→success true→ParticleHelper/SoundHelper/ModelEffectHelper及延迟POST→SpellTriggers',
 ev(S,'SpellImpacts','performImpact'),ev(S,'SpellImpacts','performImpacts','boolean additionalTargetLookup'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'SpellTriggers','onSpellImpactSpecific'),ev(S,'SpellTriggers','fireTriggers'),ev(S,'WorldScheduler','__complete_file__'),ev(S,'ServerWorldMixin','__complete_file__'),
 dedup='005 AOE最后目标覆盖讨论的是聚合方式，本条是单个DAMAGE动作本身把hurt bool丢弃并仍做副作用/成功回执；004 PRE跳内部applyDamage不等外层false为另一决策。完整方法共享，不整段重计。')
rows[-1]['decision_focus']={'lines':[345,398],'counting_rule':'Only DAMAGE ignored native boolean and its unconditional success/offset knockback outcome; shared containing method is not another effective unit.'}
add('mocreatures-werewolf-form-qualified-held-weapon-damage-rewrite',
 'MoCEntityWerewolf.attackEntityFrom只在狼形、damageSource.entity为Player且当前持物非null时把传入int伤害先覆写为1；金锄/铲/镐/斧/剑分别覆写6/7/8/9/10，再交super。空手保留原amount，不是所有非金伤害归1；投射物也仅看归属Player当前持物，未核对发射时快照或direct source。',
 '具体弱点机制应区分降低伤害、固定覆写和免疫；不能把不符合弱点的每击标IMMUNE。装备资格应基于实际伤害来源语义，避免发射后换手导致归因变化。',
 '古老int伤害API只作概念参考，不复制代码。无游戏/服务运行。Transform有自伤和特效，但不是拒伤回执；没有新增PVP、资产或守卫计数。当前持金工具把低伤提升为常量，非伤害上限；空手和非Player不走覆写。',
 'MoCreatures.load→AddEntities实际Werewolf注册→constructor初始HumanForm→原生onLivingUpdate昼夜概率启动变身→Transform/setHumanForm→原生attackEntityFrom按同步form/current held覆写→MoCEntityMob.attackEntityFrom→原版父伤害',
 ev(M,'MoCEntityWerewolf','attackEntityFrom'),ev(M,'MoCEntityWerewolf','MoCEntityWerewolf'),ev(M,'MoCEntityWerewolf','onLivingUpdate'),ev(M,'MoCEntityWerewolf','Transform'),ev(M,'MoCEntityWerewolf','getIsHumanForm'),ev(M,'MoCEntityWerewolf','setHumanForm'),ev(M,'MoCEntityWerewolf','IsNight'),ev(M,'MoCEntityWerewolf','readEntityFromNBT'),ev(M,'MoCEntityWerewolf','writeEntityToNBT'),ev(M,'MoCEntityMob','attackEntityFrom'),ev(M,'MoCreatures','load'),span(M,'MoCreatures',421,421,'Werewolf_registration'),ev(M,'MoCreatures','registerEntity','String visibleName'),
 dedup='本仓旧账为Golem世界repair-rock空间开放核心/Croc被抓攻击者特殊拒绝；新点是形态×来源Player当前手持物覆写最终amount，一个家族不按五件金工具拆条。')
add('mocreatures-turtle-threat-los-shell-denial-with-refused-hit-opening-roll',
 'Turtle原生onLivingUpdate服务端在非倒置且未驯服时getBoogey(4)，仅所返回候选有LOS才置hiding并首次hiss，失去该候选/LOS则清hiding。getBoogey实际在扩大AABB里迭代覆盖，返回最后一个entitiesToInclude目标，不是最近者；include排同class并要求Living且width或height>=0.5。attackEntityFrom只要hiding恒false，但1/10先flipflop(true)清hiding并倒置；本次仍拒伤。非hiding先super，之后1/3翻倒，不看父结果。',
 '拒绝本次命中同时改变下一击资格，是不同的状态转移边界；提示频率不能把每次拒伤与首次进入护甲状态的hiss混同。LOS应针对实际选择目标，不按注释推断最近威胁。',
 '无原生运行，没有证明实际概率/视觉。attackEntityFrom无server side guard，setIsHiding/setIsUpsideDown的client guard注释掉；不能声称仅服务端随机。read/write只保存UpsideDown与DisplayName，不保存hiding。驯服后原生交互和父归属门另行，不将其计为此拒伤策略。',
 'load/AddEntities实际Turtle注册→原生onLivingUpdate→getBoogey/LOS→hiding watcher22→原生attackEntityFrom→false并可能flipflop清hiding/watcher23；native interact可翻回；父Animal伤害仅非hiding路径',
 ev(M,'MoCEntityTurtle','attackEntityFrom'),ev(M,'MoCEntityTurtle','onLivingUpdate'),ev(M,'MoCEntityAnimal','getBoogey'),ev(M,'MoCEntityAnimal','entitiesToInclude'),ev(M,'MoCEntityTurtle','flipflop'),ev(M,'MoCEntityTurtle','getIsHiding'),ev(M,'MoCEntityTurtle','setIsHiding'),ev(M,'MoCEntityTurtle','setIsUpsideDown'),ev(M,'MoCEntityTurtle','interact'),ev(M,'MoCEntityTurtle','readEntityFromNBT'),ev(M,'MoCEntityTurtle','writeEntityToNBT'),ev(M,'MoCEntityAnimal','attackEntityFrom'),ev(M,'MoCreatures','load'),span(M,'MoCreatures',405,405,'Turtle_registration'),ev(M,'MoCreatures','registerEntity','String visibleName'),
 dedup='与Undergarden pot首次正伤必开再按LOS/CD回隐有相近点，明确交主岗跨项目判重：此处入壳由外部威胁LOS驱动，无CD；拒伤只概率清壳并倒置，失败父伤也可改变姿态。若只算phase模板则降0，不自动信用。')

add('mps-native-special-armor-fire-absorption-converts-to-heat-with-overheat-feedback-loop-escape',
 'ItemPowerArmor实现ISpecialArmor，getProperties在fire且非overheatDamage对象时直接返回ratio0.25/max25*damage，每件同策略；此早返不读能量，也不走后面unblockable清零门。damageArmor对Player且非overheat伤源，fire时把damage转heat（onFire且热量已满不再加），非fire按模块能耗×damage扣Player energy。getArmorDouble普通路径仅energy>enerConsum才加energyArmor。PlayerUpdateHandler原生update先cool，再currHeat>maxHeat发sqrt(差)/4 overheatDamage并setFire，否则extinguish。',
 '保护把一种伤害转为另一预算/后续伤源，不能称无代价全免。派生过热来源必须绕开同一吸收逻辑，避免把过热无限再转热；零火伤或熄火不代表控制免疫。',
 '仅静态原生回调链，未展开当前Forge ISpecialArmor聚合源码，不声称四件必定全部取消HP伤害或原生动画。OverheatDamage定义equals(DamageSource)为重载，调用点source静态类型DamageSource，不据此声称按字符串Overheat比较。热量物品列表为空时除零等风险未运行，不报利用。与lehjr现代缓存比较仅见EntityDamageEvent为TODO/打印，未把端口算第二条；Numina通用死亡工具0。',
 '@Mod preInit→SidedProxy common preInit/MPSItems.populateItems→Helmet继承ItemPowerArmor→Forge ISpecialArmor getProperties/damageArmor；ServerProxy.registerEvents注册PlayerUpdateHandler→原生LivingUpdateEvent→cool/heat limit→派生overheat source→getProperties排同一源',
 ev(P,'ItemPowerArmor','getProperties'),ev(P,'ItemPowerArmor','damageArmor'),ev(P,'ItemPowerArmor','getArmorDouble'),ev(P,'ItemPowerArmor','ItemPowerArmor'),ev(P,'ItemPowerArmorHelmet','__complete_file__'),ev(P,'MuseHeatUtils','__complete_file__'),ev(P,'PlayerUpdateHandler','onPlayerUpdate'),ev(P,'MuseItemUtils','getModularItemsInInventory','IInventory inv'),ev(P,'MuseItemUtils','getModularItemsInInventory','EntityPlayer player'),ev(P,'MPSItems','populateItems'),ev(P,'MPSRegistry','registerItem','String regName'),ev(P,'ModularPowersuits','preInit'),ev(P,'src/main/java/net/machinemuse/powersuits/common/proxy/CommonProxy','preInit'),ev(P,'src/main/java/net/machinemuse/powersuits/common/proxy/ServerProxy','registerEvents'),
 dedup='不同于普通属性减伤/现代Meka能量按次交易：原生火伤特殊吸收改结热量并明确派生来源退出环，整条合1，不按四件或source常量拆。主岗可因无最终拒绝/灰字相关性降支持，默认0信用。')

supplements=[]
assert len(rows)<=30
for repo in BASE:
 d=LOCAL/'sources-batch008'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if (BASE[repo]/'tree.json').exists():shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for n in ('001','002','003','004','005','006','007') for r in json.loads((OUT/f'batch-{n}.json').read_text())['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
assert all(next(r for r in rows if r['id']==o['new']).get('decision_focus') for o in overlaps),overlaps
for r in rows:
 if r.get('decision_focus'):
  a,b=r['source_refs'][0]['lines'];c,d=r['decision_focus']['lines'];assert a<=c<=d<=b
  ls=r['source_refs'][0]['excerpt'].splitlines(keepends=True);r['decision_focus']['excerpt_sha256']=sha(''.join(ls[c-a:d-a+1]).encode())
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert all(r.get('decision_focus') for r in rows if primary.count(r['source_refs'][0]['normalized_excerpt_sha256'])>1), 'shared containing methods require explicit decision focus'
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-008','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'max_units':30,'rows':rows,'support_for_prior_batches':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'候选不等于信用；主岗需最终相关性/语义去重。目标30为工作批次上限，实际不凑数；本批固定本地源码审阅，外部请求0，既有TLS失败未重试。缺后续处理器的链仅支持0，正式制作/运行/主账均未修改。'}
(OUT/'batch-008.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-008.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars/SpellEngine/IE/Undergarden/Embers pinned Git tree/blob；Iron pinned archive source.json SHA256 inventory，无相同commit树，不冒称blob已独立核验。'},ensure_ascii=False,indent=2)+'\n')
allrefs=[v for r in rows+supplements for v in r['source_refs']]
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'supplement_units':len(supplements),'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(r['unit']=='complete_method' for r in allrefs),'complete_support_resource_references':sum(r['unit']=='complete_support_resource' for r in allrefs),'batch_sha256':sha((OUT/'batch-008.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':0,'todo_modified':False}
(OUT/'receipt-008.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
