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
 starts=[i for i,l in enumerate(lines,1) if re.match(r'\s*(?:public|private|protected|default|static)\s',l) and re.search(r'\b'+re.escape(method)+r'\s*\(',l) and (qualifier is None or qualifier in ''.join(lines[i-1:i+8]).split('{',1)[0]) and not l.strip().endswith(';')]
 if method=='__complete_file__':starts=[1]
 assert len(starts)==1,(name,method,qualifier,starts)
 start=starts[0];end=len(lines) if method=='__complete_file__' else reader.end_method(lines,start);excerpt=''.join(lines[start-1:end]);pin=meta[repo];commit=pin.get('commit',pin.get('sha'));blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if repo in (A,S):
  tree=json.loads((BASE[repo]/'tree.json').read_text());assert tree['sha']==commit;assert next(x['sha'] for x in tree['tree'] if x['path']==rel)==blob
  proof='pinned Git tree blob SHA1'
 else:
  entry=next(x for x in pin['files'] if x['path']==rel);assert entry['sha256']==sha(data);proof='pinned archive source.json SHA256 inventory'
  if 'git_blob_sha1' in entry:assert entry['git_blob_sha1']==blob;proof='pinned source inventory SHA256 and Git blob SHA1'
 dest=LOCAL/'sources-batch004'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'unit':'complete_support_resource' if method=='__complete_file__' else 'complete_method','source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-004-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与001/002及当前主账按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
# One complete impact dispatcher is shared support, never credited again for each branch.
impact=ev(S,'SpellImpacts','performImpact')
impacts=ev(S,'SpellImpacts','performImpacts','boolean additionalTargetLookup')
projectile=ev(S,'SpellProjectile','onEntityHit')
immunity=ev(S,'LivingEntityImmunity','__complete_file__')
add('spellengine-native-source-qualified-immunity-lease',
 'IMMUNITY实际impact分支将damage_type解析为精确DamageType或#tag，并仅duration_ticks>0调用五参apply；该重载明确effectAnyHarmful=false。Entry按类型identity、tag、显式indirect约束全部AND，无约束允许所有来源；任一entry匹配使原生isInvulnerableTo原结果OR为true。期限用实体age+ticks，tick HEAD在age>validUntil才删，查询本身不比较期限；重复施加append不合并。',
 '拒伤原因应来自实际来源匹配，不从粒子或通用damage=false猜测。期限、重复刷新与原生查询位置须成套考虑，来源维度不可退化为Boss类型常量。',
 '静态固定源码，未运行Mixin；未核验资源注册清单。查询和清理之间的具体一tick顺序未原生验证。精确伤害ID缺失可解析为null，可能退化为更宽匹配，不能自动认为缺ID会拒绝施法。无跨死/存档保证；不证明某addon默认配置实际启用。',
 '原生SpellProjectile.onEntityHit→projectileImpact→performImpacts→performImpact.IMMUNITY→五参apply→Owner.addImmunity→原生isInvulnerableTo RETURN；原生tick清过期',
 ev(S,'LivingEntityImmunity','protectsAgainst'),immunity,ev(S,'LivingEntityImmunityMixin','addImmunity'),ev(S,'LivingEntityImmunityMixin','tick_HEAD_SpellEngine_Immunity'),ev(S,'LivingEntityImmunityMixin','isInvulnerableTo_RETURN_SpellEngine_Immunity'),ev(S,'DamageSourceMixin','__complete_file__'),projectile,ev(S,'SpellImpacts','projectileImpact'),impacts,impact,
 dedup='来源资格+短租期作为同一实际动态免疫链1候选，不按damage type/tag/indirect/重载/期限拆。不同于001静态来源模板；主岗可按已有动态免疫家族合并。')
add('spellengine-reactive-pre-damage-immunity-final-recheck',
 '原生damage调用内部applyDamage前先派发ENTITY/PLAYER_DAMAGE_INCOMING，回调完成后重新isInvulnerableTo，若新近免疫则直接return，连original.applyDamage都不调用。init注册onDamageIncoming，后者必须存在attacker，amount>=当前HP标fatal并stage PRE；fireTriggers服务端即时performSpell或延迟fire_delay-1。该hook没有修改外层damage返回值；另一个RETURN hook只看原生boolean派发TAKEN，故不能把跳过内部扣血等同外层false或保证不触发POST。',
 '拒绝反馈应在最后权威门记录，临界前触发可能改变资格，初始检查不可复用；明确区分扣血步骤跳过与外层函数结果。',
 '未配置/运行具体保命法术，未证明一次命中真实HP变化；延迟触发不能由这段代码保证保护当前击。performSpell还会校验来源/施法资格/弹药，不能声称PRE一定授予免疫。环境来源无attacker不进入玩家被动事件。',
 'SpellEngineMod.init→SpellTriggers.init注册→原生damage/applyDamage WrapOperation→onDamageIncoming→fireTriggers→performSpell；同步回调后重新原生isInvulnerableTo；另原生damage RETURN事件',
 ev(S,'LivingEntityHealthImpacting','damage_ApplyDamage_entity'),ev(S,'SpellEngineMod','init'),ev(S,'SpellTriggers','init'),ev(S,'SpellTriggers','onDamageIncoming'),ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellExecution','performSpell'),ev(S,'LivingEntityEvents','damage_RETURN_entity'),immunity,impact,
 dedup='与上一条动态资格存储是不同最终消费位置：初查之后、实际扣血之前的反应式再校验；未将通用PRE/POST包装独立计数。')
add('spellengine-native-evasion-eligibility-with-explicit-feedback',
 '原生LivingEntity.damage在isSleeping调用处注入，tryEvade要求未睡眠、配置允许当前施法/用物、来源EVADABLE，属性概率及水平夹角均通过才成功。随后onEvade对ServerPlayer发送闪避动画、播放坐标DODGE声并派发EVASION，再记录lastEvaded=同一source并设置原生返回false/cancel。onEvasion仅玩家且attacker非null再进入被动链。',
 '有明确闪避分支才生产闪避回执；概率/方向/忙碌资格与Boss免控分开，动画声或普通伤害失败都不是通用immune原因。',
 'EVADABLE默认tag成员和Mixin注册资源未核验；未运行概率/方向实验。角度计算仅limit>0且有直接source才做，默认角0仍受0<=limit约束；lastEvaded没有主动清空。仅证明发送动画调用，不声称客户端显示已验。',
 '原生damage injection→tryEvade→onEvade(动画/声/EVASION)→lastEvaded/source记录→false；init注册EVASION→onEvasion→fireTriggers',
 ev(S,'EvasionLogic','tryEvade'),ev(S,'LivingEntityEvasionMixin','damage_SpellEngine_Evasion'),ev(S,'EvasionLogic','onEvade'),ev(S,'AnimationHelper','sendAnimation','boolean includeAnimated'),ev(S,'AnimationHelper','sendPacketToPlayer'),ev(S,'SpellTriggers','init'),ev(S,'SpellTriggers','onEvasion'),ev(S,'SpellTriggers','fireTriggers'),
 dedup='区别002 Iron按药效层数消耗的Rapier闪避：本条原生damage属性概率/方向和忙碌条件及明确EVASION回执；主岗按最终语义复核，不按动画/声/事件拆。')
add('spellengine-projectile-evaded-source-correlation-stops-followup',
 'PersistentProjectileEntity.onEntityHit包装实际Entity.damage，先保存当前DamageSource对象再交原生；后续setFireTicks调用处仅当命中实体Evader.lastEvaded与该对象引用相同才cancel整个后续onEntityHit。它识别明确闪避原因，而非把所有damage=false当闪避。',
 '命中关联应携带本次权威原因/令牌，防止无敌、无效目标或别的失败误取消箭矢后续；收到通用false无法决定反馈类别。',
 '两字段nullable且无显式清理；未读取/执行此版本原版onEntityHit的字节码顺序，不能据null==null推定实际误判，也不宣称所有弹种通用。只针对PersistentProjectileEntity。',
 '原生onEntityHit→wrap Entity.damage保存source→LivingEntity闪避记录source→setFireTicks注入引用比较→cancel后续',
 ev(S,'ProjectileEvasionMixin','entityHit_SpellEngine_Evasion'),ev(S,'ProjectileEvasionMixin','entityHit_SpellEngine_SaveDamageSource'),ev(S,'LivingEntityEvasionMixin','damage_SpellEngine_Evasion'),ev(S,'EvasionLogic','tryEvade'),
 dedup='单列伤害后的原生箭矢副作用边界与明确命中关联，而非再计闪避判定本身；主岗如归同一闪避链可降支持。')
add('spellengine-boss-control-classification-final-status-gate',
 '服务器started遍历效果属性，以移动/飞行/重力属性和modifier操作阈值缓存RegistryKey；ADD_VALUE/BASE阈值0，ADD_MULTIPLIED_TOTAL原始value阈值1。另disablesMobAI读取ActionImpairing政策。实际performImpact在STATUS ADD/SET分支遇Boss tag且任一分类成立立即false，不进入addStatusEffect及成功FX。普通效果路径却忽略addStatusEffect boolean后success=true并发粒子/声/模型/POST，因此现有success不等于效果真实接纳。',
 'Boss专用拒控应与效果真实语义和最终施加点关联；分类标签与原生拒绝结果分开记录，避免把已发外观当成功证据。',
 '未核验Boss默认tag/服务器运行。缓存parse不清空；按amp0分析，且TOTAL直接用阈值1，不能照评论断言精确分类所有减速。这一原生Boss门只覆盖该dispatcher ADD/SET，不阻止其他mod直接addStatusEffect或位移。',
 'SpellEngineMod.init→StatusEffectClassification.init→serverStarted parse；原生法术弹→performImpacts→performImpact.STATUS→Boss+movement/AI分类拒绝或addStatusEffect→成功反馈',
 ev(S,'StatusEffectClassification','parse'),ev(S,'StatusEffectClassification','init'),ev(S,'StatusEffectClassification','isMovementImpairing'),ev(S,'StatusEffectClassification','disablesMobAI'),ev(S,'SpellEngineMod','init'),ev(S,'ActionImpairing','__complete_file__'),projectile,impacts,impact,
 dedup='002已计ActionImpairing政策只作支持0；本条实际Boss效果分类及施加前最终门合计1，不按两个分类/每属性/ADD和SET拆。')
add('spellengine-max-health-power-cap-rejects-status-application',
 '实际STATUS分支在ADD/SET/REMOVE共同switch之前先underApplyLimit：limit空全允，否则health_base+nonCriticalPower*mult必须>=目标maxHealth。不是当前HP、生命比例或Boss标签；超上限目标即使残血仍直接false且不进成功反馈。school形参没有参与公式。',
 '资格不足的拒绝理由应与Boss硬免控区分；提示必须使用执行时比较的数据，不能用残血或发光反推可控。',
 '共享performImpact只作完整上下文，未配置/运行具体限血法术。它也可能挡移除模式，不宣称仅新增负面控制；未验证NaN/负倍率输入实际配置。',
 '原生SpellProjectile.onEntityHit→performImpacts→performImpact.STATUS选效果→underApplyLimit→false或继续ADD/SET/REMOVE',
 ev(S,'SpellImpacts','underApplyLimit'),projectile,impacts,impact,
 dedup='独立于Boss身份+控制分类门，是按非暴击法强与最大HP的目标资格；主岗如已有等价法强/HP门须合并。不得把其他系数常量视为新机制。')
add('spellengine-per-player-spell-trigger-quota-and-shared-roll-window',
 '真实注册战斗回调进入server fireTriggers→evaluateTrigger。玩家实体自有按spellId map，cap_per_tick>0先检查已有次数，只有全部后续条件及type条件成功才写回+1；chance_batching在后续条件之前缓存随机数，因此后续不合格仍可锁本窗口抽签。原生Player.tick TAIL清map，不是全世界统一时钟，也没有按受害目标区分；同spell多个trigger共享额度/抽签。',
 '战斗反馈若需同目标节流，不能照搬只有施法者+法术的key；明确计尝试还是计成功，以及窗口清理时点，可避免AOE批次爆字或吞掉不同目标。',
 '这是实际战斗被动触发节流，不是已有浮字生产器；没有运行时突发频率证据。只研究额度/抽签及生命周期，evaluateTrigger其余条件完整附录但不逐个加信用。Player tick边界与世界tick不能直接等价。',
 'SpellEngineMod.init→SpellTriggers.init→原生伤害/闪避事件→fireTriggers→evaluateTrigger→SpellBatcher缓存→PlayerEntity.tick TAIL.clear',
 ev(S,'SpellTriggers','evaluateTrigger'),ev(S,'SpellBatcher','__complete_file__'),ev(S,'PlayerEntitySpellBatching','tick_TAIL_spell_engine_spell_batching'),ev(S,'SpellTriggers','fireTriggers'),ev(S,'SpellTriggers','init'),ev(S,'SpellTriggers','onDamageIncoming'),ev(S,'LivingEntityHealthImpacting','damage_ApplyDamage_entity'),
 dedup='区别002客户端输入20tick去抖/HUD单槽：此处真实服务器战斗事件每玩家每法术限额和共享抽签；chance和cap同一窗口合计1，不当成目标级节流。')
add('spellengine-harmful-status-immunity-missing-true-producer-support',
 '原生两参addStatusEffect HEAD会在!isBeneficial且任一entry.effectAnyHarmful时返回false；但固定源码实际IMMUNITY impact生产调用五参apply，明确委托六参effectAnyHarmful=false。全文缓存搜索未找到true生产者，因此不能用这个消费者宣称实际负面状态全免疫已接活。',
 '接口/最终门与具体生产必须分别核实，孤立入口不算游戏功能。neutral也可能被!beneficial覆盖，命名不能代替语义。',
 '仅固定本地源码，不排除外部addon；支持0，不转有效。',
 '原生addStatusEffect注入有拒绝消费者；现有实际impact生产不启用effectAnyHarmful',
 ev(S,'LivingEntityImmunityMixin','addStatusEffect_HEAD_SpellEngine_Immunity'),immunity,impact,status='support_only_not_effective',dedup='同本批来源免疫链的未接活能力，仅支持0；不把每个拒绝hook当已制作功能。')
add('spellengine-knockback-immunity-cache-without-enable-consumer-support',
 '状态变化tick仅effectsChanged时重算effect集合anyImmune，takeKnockback HEAD读缓存并cancel；StatusEffect flag默认false。固定全文缓存没有外部KnockbackImmunity.configure调用或setImmuneToKnockback启用者，不能将热路径拦截视为实际注册效果。',
 '对控制免疫缓存需查真实启用者和失效更新，再决定是否可作为功能参考；临时集合变化和最终控制入口应分别保留。',
 '支持0；普通setVelocity不经过takeKnockback，且本缓存非持久化，未运行时验证。负面搜索范围只固定缓存。',
 '潜在configure→StatusEffect flag→原生tickStatusEffects变更时聚合→takeKnockback HEAD；真实启用者缺失',
 ev(S,'LivingEntityKnockbackImmunity','takeKnockback_HEAD_KnockbackImmunity_SpellEngine'),ev(S,'LivingEntityKnockbackImmunity','tickStatusEffects_HEAD_KnockbackImmunity_SpellEngine'),ev(S,'KnockbackImmunity','__complete_file__'),ev(S,'StatusEffectKnockbackImmunity','__complete_file__'),status='support_only_not_effective',dedup='缺实际启用者，与Protection同样pending原则，支持0；不挪已计护卫/抗击退账。')
supplements=[]
assert len(rows)<=30
for repo in BASE:
 d=LOCAL/'sources-batch004'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo in (A,S):shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for n in ('001','002','003') for r in json.loads((OUT/f'batch-{n}.json').read_text())['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
assert not overlaps,overlaps
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert len(primary)==len(set(primary))
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-004','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'max_units':30,'rows':rows,'support_for_prior_batches':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'候选不等于信用；主岗需最终相关性/语义去重。本批不按模板补到30。只有固定本地源码审阅，无外部请求/游戏/正式代码修改。'}
(OUT/'batch-004.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-004.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars/SpellEngine pinned Git tree/blob；Iron pinned archive source.json SHA256 inventory，无相同commit树，不冒称blob已独立核验。'},ensure_ascii=False,indent=2)+'\n')
allrefs=[v for r in rows+supplements for v in r['source_refs']]
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'supplement_units':len(supplements),'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(r['unit']=='complete_method' for r in allrefs),'complete_support_resource_references':sum(r['unit']=='complete_support_resource' for r in allrefs),'batch_sha256':sha((OUT/'batch-004.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':0,'todo_modified':False}
(OUT/'receipt-004.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
