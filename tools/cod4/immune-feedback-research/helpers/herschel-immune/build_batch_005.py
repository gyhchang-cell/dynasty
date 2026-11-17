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
 dest=LOCAL/'sources-batch005'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'unit':'complete_support_resource' if method=='__complete_file__' else 'complete_method','source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-005-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与001/002及当前主账按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
def span(repo,name,start,end,label):
 ref=ev(repo,name,'__complete_file__');lines=ref['excerpt'].splitlines(keepends=True);excerpt=''.join(lines[start-1:end]);ref.update(method=label,lines=[start,end],excerpt=excerpt,excerpt_sha256=sha(excerpt.encode()),normalized_excerpt_sha256=sha(re.sub(r'\s+','',excerpt).encode()));ref['url']=ref['url'].split('#')[0]+f'#L{start}-L{end}';ref['resource_scope']='complete nested declaration or complete registration statement; not a counted method';return ref
impact=ev(S,'SpellImpacts','performImpact')
impacts=ev(S,'SpellImpacts','performImpacts','boolean additionalTargetLookup')
area=ev(S,'SpellImpacts','lookupAndPerformAreaImpact','Float radiusOverride')
particleCodec=span(S,'Packets',215,264,'complete_ParticleEffects_record')
modelSpawn=ev(S,'ModelEffectHelper','spawn','LivingEntity contextEntity')
modelRenderer=ev(S,'ModelEffectOperations','renderEffect')
modelTransform=ev(S,'ModelEffectOperations','applyTransforms')
add('iron-counterspell-busy-own-summon-final-refusal-and-unconditional-beam',
 '已注册Counterspell实际onCast用阻方块/0.35膨胀/80格ray过滤AntiMagicSusceptible、Player或IMagicEntity，最近命中后post可取消CounterSpellEvent。未取消时自有IMagicSummon仅是Mob且getTarget()==null才反制；忙碌自有召唤物跳过onAntiMagic，却仍清其全部MagicMobEffect。其他所属召唤物调用反制；SummonedZombie.onUnSummon服务器POOF后DISCARDED。整条光束在事件取消/目标不接纳时仍发。',
 '拒绝原因需要对应具体动作，拒绝解散不等于拒绝驱散状态；已画反制光束不代表目标成功被取消或移除。',
 '静态无游戏测试；owner依赖同ServerLevel UUID查找，缺owner会按非自有处理。没有找到CounterSpellEvent实际取消监听器，所以不把事件扩展能力单列为已接活免疫；自有忙碌门有实际消费者。',
 'SpellRegistry.COUNTERSPELL注册→Counterspell.onCast→RaycastBuilder.performRaycast→Utils.validAntiMagicTarget→CounterSpellEvent→SummonManager.getOwner/IMagicSummon.onAntiMagic→SummonedZombie.onUnSummon；光束不读取最终动作结果',
 ev(I,'CounterspellSpell','onCast'),ev(I,'RaycastBuilder','performRaycast'),ev(I,'Utils','validAntiMagicTarget'),ev(I,'CounterSpellEvent','__complete_file__'),ev(I,'IMagicSummon','getSummoner'),ev(I,'SummonManager','getOwner'),ev(I,'IMagicSummon','onAntiMagic'),ev(I,'SummonedZombie','onUnSummon'),ev(I,'SpellRegistry','registerSpell'),span(I,'SpellRegistry',101,101,'COUNTERSPELL_registered_statement'),
 dedup='与已计友伤/owner伤害拒绝不同：当前攻击忙碌状态阻止自身反制移除但不阻止驱散。反制其他模板消费者仅支持，不逐实体加数。')
add('iron-interrupted-cast-explicit-uuid-receipt-and-client-teardown',
 'Counterspell对ServerPlayer走cancelCast(true)。若确isCasting，先施冷却/可能消连续卷轴，然后当前spell.onServerCastComplete(cancelled=true)。基础实现重置服务器CastingState，向tracking+self发UUID/spellId/cancelled；客户端重置仅本机UUID的施法/目标/用物状态，按UUID查实际player取消其动画，取消且stopSoundOnCancel时按sound资源ID全局stop。只有本机UUID再改按键释放位。',
 '明确取消回执与预测施法失败应区分；收包后状态、动画、音源各自的归属键要真实核查，UUID仅保护部分分支不代表所有反馈按实体隔离。',
 '不是Boss受击文字。handler先访问本地player/level且远端UUID查找可null，无显式缺实体重试；动画取消helper也无player null门。声音stop仅资源ID且category=null，不保证只停止该实体音源。实际消息生产已找到，不能与孤立CastError receiver混淆；未做网络验证。',
 'Counterspell.onCast→Utils.serverSideCancelCast→CancelCastPacket.cancelCast静态本地服务调用→AbstractSpell.onServerCastComplete→OnCastFinishedPacket→注册S2C→ClientSpellCastHelper→ClientMagicData/AnimationHelper',
 ev(I,'ClientSpellCastHelper','handleClientBoundOnCastFinished'),ev(I,'CounterspellSpell','onCast'),ev(I,'Utils','serverSideCancelCast','boolean triggerCooldown'),ev(I,'CancelCastPacket','cancelCast'),ev(I,'AbstractSpell','onServerCastComplete'),ev(I,'OnCastFinishedPacket','write'),ev(I,'OnCastFinishedPacket','handle'),ev(I,'PayloadHandler','register'),ev(I,'ClientMagicData','resetClientCastState'),ev(I,'ClientMagicData','resetTargetingData'),ev(I,'AnimationHelper','cancelPlayerAnimation'),
 dedup='区别002 SpellEngine预测拒绝20tick输入去抖：实际服务端反制终止+明确cancelled/UUID回执，含远端动画及资源ID声音清退边界；各包装不另计。')
add('spellengine-impact-fx-detached-anchor-survives-source-removal',
 '实际lookupAndPerformAreaImpact对aoeSource使用sendBatchesDetached，将当前服务器origin/yaw/pitch和实体整数ID放入COORDINATE包，目标tracking+self可发送才发。客户端COORDINATE直接用sourceLocation；ENTITY则优先本地entity当前位置，缺entity再按发送坐标和固定height=2重算anchor。云命中也走detached，避免当tick销毁导致位置追随竞态。',
 '瞬时拒绝反馈可固定权威命中坐标，持续附着才追实体；保留ID不代表坐标仍依赖它，缺实体回退规则要与锚定类型对应。',
 '没有维度ID、UUID、事件序号/去重key或实体代际校验；非ENTITY分支仍把按整数ID查出的sourceEntity传给particle factory，不能声称完全无实体依赖。packet decode/convert发生在client.execute前，最终执行读当前world，无显式world切换校验；没有真实TCP测试。',
 '原生SpellCloud.tick/area impact→lookupAndPerformAreaImpact→sendBatchesDetached→Fabric注册ParticleEffects codec/receiver→ClientNetwork.handleParticleEffects→convertToInstructions→emit→SpawnInstruction.perform',
 ev(S,'ParticleHelper','sendBatchesDetached'),area,ev(S,'SpellCloud','onImpactPerformed'),particleCodec,ev(S,'FabricServerNetwork','init'),ev(S,'FabricClientNetwork','init'),ev(S,'ClientNetwork','handleParticleEffects'),ev(S,'ParticleHelper','convertToInstructions'),ev(S,'ParticleHelper','origin','Entity entity'),ev(S,'ParticleHelper','origin','World world'),ev(S,'ParticleHelper','emit'),ev(S,'ParticleHelper','perform'),
 dedup='实际战斗一次性FX的服务器坐标/实体消失竞态策略合计1，codec/平台端口/几何算法全支持0；区别003传送双坐标忽略取消及Wall本地扫描。')
add('spellengine-area-result-last-target-not-any-and-unconditional-fx',
 'applyAreaImpact对targets逐个performImpacts，但anyPerformed每次直接赋值，最终只返回最后目标结果。lookupAndPerformAreaImpact不管result都发范围粒子/声/模型；performImpacts额外范围查找也忽略该返回后排队AREA事件，其自身any只看中心performedActionTypes。SpellCloud.tick则消费返回决定onImpactPerformed累计impactCap或onImpactFailed。',
 '范围反馈要同时保留逐目标明确结果和真正聚合结果，不能以一次外观或最后目标状态代表全部Boss免疫；不同层的success语义必须标清。',
 '静态边界不是运行复现。performImpact内部某些success本来未读取原生伤害/状态接纳返回，故即使修复聚合也不自动成为实际扣血回执；impactCap目前数的是被判performed的云循环而非每个受害者。',
 'SpellCloud.tick→lookupAndPerformAreaImpact→applyAreaImpact→performImpacts→performImpact；结果返回云success/failure回调；lookup层范围FX独立于该结果',
 ev(S,'SpellImpacts','applyAreaImpact'),area,impacts,impact,ev(S,'SpellCloud','tick'),ev(S,'SpellCloud','onImpactPerformed'),ev(S,'SpellCloud','onImpactFailed'),
 dedup='004共享performImpact全文只支持；本条新增实际AOE跨目标结果聚合/消费边界，不按中心/范围包装各加数，不把原生false原因猜成immune。')
add('spellengine-combat-attached-model-worldtime-lease-and-first-person-policy',
 '实际impact成功分支ModelEffectHelper.spawn按follow_entity+contextEntity选择附着。attach将(effect,worldTime,duration)append并把整表JSON写实体DataTracker。原生server tick TAIL按worldTime>=applied+duration移除并重发空串/新表；收tracker时清列表再解析，RuntimeException吞掉。LivingEntityRenderer TAIL对目标实体半高定位，第一人称焦点实体跳过；动画时间(worldTime+delta-applied)%duration，不做独立过期剔除。',
 '每目标附着反馈生命周期可用权威期限同步，渲染和清理须配对；过期包延迟会循环显示，不能仅靠取模动画保证移除。叠加append不是同目标节流。',
 '只有静态Java链和网页注册声明，原始Mixin JSON blob仍缺TLS下载补证，未宣称运行生效。没有维度/UUID包字段（依靠原生实体tracker），没有存档写回或数量上限；duration<=0无渲染防护。无新艺术资产制作。',
 'performImpact success→ModelEffectHelper.spawn(follow_entity)→SpellEngine_attachModelFx/DataTracker→onTrackedDataSet→LivingEntityRenderer TAIL→ModelEffectOperations；server tick期限清理',
 ev(S,'LivingEntityStatusEffectSync','SpellEngine_attachModelFx'),impact,modelSpawn,ev(S,'ModelEffectAttachment','__complete_file__'),ev(S,'LivingEntityStatusEffectSync','initDataTracker_TAIL_SpellEngine_SyncEffects'),ev(S,'LivingEntityStatusEffectSync','onTrackedDataSet_TAIL_SpellEngine_SyncEffects'),ev(S,'LivingEntityStatusEffectSync','tick_TAIL_SpellEngine_ModelFx'),ev(S,'LivingEntityModelFxRendererMixin','render_TAIL_SpellEngine_ModelFx'),modelRenderer,modelTransform,
 dedup='战斗目标实体挂载JSON期限与已有世界浮字血量变化/单槽HUD不同；与下一条独立实体模型同一个helper但持有者/时钟/同步/清退机制不同，主岗可按语义归并，不按变换/模型加数。')
add('spellengine-combat-standalone-model-native-age-lifetime-and-reload-gap',
 '同一combat FX helper在不follow或无context时创建原生SpellModelEffect实体，setup把JSON写DataTracker并TTL=duration，spawn实体。server tick在age>=TTL discard；client追踪JSON后建立ModelEffect/TTL，renderer以entity.age+delta绘制。NBT保存Age/TTL/ModelEffect，加载只改字段没有写回MODEL_EFFECT_DATA，因此不能据字段恢复就宣称新追踪客户端恢复模型配置。shouldRender直接true。',
 '独立临时反馈实体需统一生命周期、载入后同步和可见性；本地字段恢复不等于跟踪数据恢复，服务器TTL也不能保证客户端不短暂错龄。',
 '未做NBT往返/客户端实验，只记录源码可见缺口。standalone路径对已偏移的location不再跟随目标；存在跟踪范围上限但shouldRender没有距离判断不等于无限广播。不是世界文字制作成果。',
 'performImpact success→ModelEffectHelper.spawn else→SpellModelEffect.setup/world.spawnEntity→registerEntityTypes→loader renderer注册→onTrackedDataSet→SpellModelEffectRenderer.render；server tick discard与NBT load独立路径',
 ev(S,'SpellModelEffect','tick'),impact,modelSpawn,ev(S,'SpellModelEffect','setup'),ev(S,'SpellModelEffect','initDataTracker'),ev(S,'SpellModelEffect','onTrackedDataSet'),ev(S,'SpellModelEffect','writeCustomDataToNbt'),ev(S,'SpellModelEffect','readCustomDataFromNbt'),ev(S,'SpellModelEffect','shouldRender'),ev(S,'SpellModelEffectRenderer','render'),modelRenderer,modelTransform,ev(S,'SpellEngineMod','registerEntityTypes'),ev(S,'FabricMod','onInitialize'),ev(S,'FabricClientMod','onInitializeClient'),ev(S,'NeoForgeClientMod','registerEntityRenderers'),
 dedup='区别上条世界时间+附着表：实体age/实体删除、Native tracking配置和NBT恢复问题；如主岗视为同FX生命周期家族允许降支持，不凭两个类自动双计。')
add('spellengine-cloud-active-only-hit-budget-and-idempotent-winddown-feedback',
 'CloudPlacer实际生成cloud，onCreated将active秒换ticks并加spawn/despawn时段。server原生tick仅ACTIVE且age%impact_tick_interval==0尝试范围，成功回调累计cap并beginDespawn；后者server且未已despawn才把TTL改为age+ticks，立即setPhase避免多一帧ACTIVE。setPhase仅阶段变化时触发despawn FX，tracker同时发布阶段结束绝对age。客户端按phase驱动spawn/idle/despawn动画，环境particles/presence声并不限定ACTIVE。',
 '有效命中窗口与外观存在期分开；权威阶段转换生产一次结束反馈，临时控制/提示退出不能凭客户端环境粒子停止来判断。',
 '该预算消费受上一条AOE返回语义影响，不代表实际伤害次数；getCloudData缺失会return而非discard，interval=0没有本地防护，不能声称任意配置安全。NBT未保存impactsPerformed/impactCap/owner/context，虽然保留时段，不能声明完整预算/所属跨加载恢复。未运行。',
 'SpellDelivery.deliver CLOUD→CloudPlacer.placeCloud→onCreatedFromSpell→world.spawnEntity→原生tick ACTIVE范围尝试→onImpactPerformed/Cap→beginDespawn→setPhase/FX→DataTracker→setupAnimationStates→TTL discard',
 ev(S,'SpellCloud','beginDespawn'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'CloudPlacer','placeCloud'),ev(S,'SpellCloud','onCreatedFromSpell'),ev(S,'SpellCloud','tick'),ev(S,'SpellCloud','setPhase'),ev(S,'SpellCloud','playDespawnFX'),ev(S,'SpellCloud','setupAnimationStates'),ev(S,'SpellCloud','onImpactPerformed'),ev(S,'SpellCloud','onImpactFailed'),ev(S,'SpellCloud','readCustomDataFromNbt'),ev(S,'SpellCloud','writeCustomDataToNbt'),ev(S,'SpellCloud','initDataTracker'),ev(S,'SpellCloud','getCloudData'),ev(S,'SpellCloud','getSpellEntry'),ev(S,'SpellCloud','radiusForAge'),ev(S,'SpellCloud','baseRadius'),
 dedup='区别003Wall逐目标20tick窗口：本条云全局三阶段/成功循环预算/幂等退出反馈合计1；成长半径与音粒子常量仅支持，生命周期动画方法不逐个计。')
add('spellengine-projectile-child-history-inheritance-support',
 'onEntityHit先用impactHistory整数ID拒重，只有performed才链反应/弹跳/穿透。chainReactionFrom给子弹复制历史而非共享集合，触发数先减后复制perks；其前置impactHistory.contains(target)却拿Entity查Set<Integer>，不能视为有效重复判断。ricochet/pierce各自把target.getId写入，子弹兄弟之后各自独立。',
 '反馈去重key类型必须一致，历史复制只继承过去不互相同步；成功分支去重不覆盖原生拒绝重试。',
 '已有主账wizardry-chain-target-dedup-scope-and-resist-cadence家族，支持0，避免再数普通去重；没有复现重复命中或发包，不能仅静态类型错配推定最终必重复。',
 '原生SpellProjectile.onEntityHit→performed→chainReactionFrom历史复制/ricochetFrom/pierced各自打戳',
 ev(S,'SpellProjectile','chainReactionFrom'),ev(S,'SpellProjectile','onEntityHit'),ev(S,'SpellProjectile','ricochetFrom'),ev(S,'SpellProjectile','pierced'),status='support_only_not_effective',dedup='与既有链式命中历史作用域家族合并支持0；不将三种perk或子弹数量拆计。')
supplements=[{'support_for_batch004':'all SpellEngine native hook rows','research_credit':0,'suggested_credit':0,'status':'JAVA_ENTRYPOINTS_BLOB_VERIFIED_RESOURCE_RAW_PENDING_TLS','observation':'固定Java入口全文核验：FabricMod.onInitialize→公共init/实体/效果注册/FabricServerNetwork；FabricClientMod.onInitializeClient→公共client init/FabricClientNetwork。NeoForgeMod为@Mod(SpellEngineMod.ID)，构造器公共init并监听注册；NeoForgeClientMod有client EventBusSubscriber。web.run成功读取同commit common mixin JSON、fabric.mod.json、neoforge.mods.toml，所需五hook均在mixins声明且两loader引用common JSON；原始资源urllib首次TLS失败，停止全部外部请求，不把网页可读声称raw blob通过。详见registration-web-observations-005.json和registration-fetch-005.json。','limits':'仅支持0；未运行Mixin，原始资源Git blob核验尚待主岗可用环境，不改旧004字节；Protection/CastError未因此补活。','source_refs':[ev(S,'FabricMod','onInitialize'),ev(S,'FabricClientMod','onInitializeClient'),ev(S,'FabricServerNetwork','init'),ev(S,'FabricClientNetwork','init'),ev(S,'NeoForgeMod','NeoForgeMod'),ev(S,'NeoForgeMod','register'),ev(S,'NeoForgeClientMod','onClientSetup')]}]
assert len(rows)<=30
for repo in BASE:
 d=LOCAL/'sources-batch005'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo in (A,S):shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for n in ('001','002','003','004') for r in json.loads((OUT/f'batch-{n}.json').read_text())['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
assert not overlaps,overlaps
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert len(primary)==len(set(primary))
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-005','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'max_units':30,'rows':rows,'support_for_prior_batches':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'候选不等于信用；主岗需最终相关性/语义去重。本批不按模板补到30。代码均固定本地源码审阅；另3次web只读注册全文成功、1次urllib原始资源TLS失败并停止外部请求。无游戏/正式代码修改。'}
(OUT/'batch-005.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-005.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars/SpellEngine pinned Git tree/blob；Iron pinned archive source.json SHA256 inventory，无相同commit树，不冒称blob已独立核验。'},ensure_ascii=False,indent=2)+'\n')
allrefs=[v for r in rows+supplements for v in r['source_refs']]
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'supplement_units':len(supplements),'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(r['unit']=='complete_method' for r in allrefs),'complete_support_resource_references':sum(r['unit']=='complete_support_resource' for r in allrefs),'batch_sha256':sha((OUT/'batch-005.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':4,'todo_modified':False}
(OUT/'receipt-005.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
