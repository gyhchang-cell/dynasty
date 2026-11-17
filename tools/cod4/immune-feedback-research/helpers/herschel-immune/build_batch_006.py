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
 dest=LOCAL/'sources-batch006'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'unit':'complete_support_resource' if method=='__complete_file__' else 'complete_method','source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-006-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与001–005及当前主账按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
def span(repo,name,start,end,label):
 ref=ev(repo,name,'__complete_file__');lines=ref['excerpt'].splitlines(keepends=True);excerpt=''.join(lines[start-1:end]);ref.update(method=label,lines=[start,end],excerpt=excerpt,excerpt_sha256=sha(excerpt.encode()),normalized_excerpt_sha256=sha(re.sub(r'\s+','',excerpt).encode()));ref['url']=ref['url'].split('#')[0]+f'#L{start}-L{end}';ref['resource_scope']='complete nested declaration or complete registration statement; not a counted method';return ref

add('iron-shadow-slash-parry-gate-and-success-dependent-physical-followup',
 '原生ShadowSlash.onCast从Living/Projectile射线候选中取最近实体。Projectile只有!noPhysics、非落地箭且不在CANT_PARRY标签才改owner和shoot回去；标记parry成功后另发招架声/火花。其余分支仅在DamageSources.applyDamage返回true后发目标火花、附魔后效和击退；末尾整片斩击/轨迹却无条件发。招架反馈坐标用closestEntity，不保证它就是实际招架的那枚弹。',
 '灰字应在具体拒绝生产点绑定目标；可反弹资格、伤害接纳与技能出手外观要分离。泛型hurt(false)仍不能确定免疫原因。',
 '只读静态研究，未运行。CANT_PARRY不等于完全免伤：未招架弹可能进入后续伤害分支。实体判定中的isPickable读的是caster。击退scale返回值未赋回，不按注释声称已乘抗性。',
 'SpellRegistry.SHADOW_SLASH→ShadowSlash.onCast→ray候选/标签门→Projectile.setOwner/shoot或DamageSources.applyDamage→成功后效；技能结束外观独立',
 ev(I,'ShadowSlashSpell','onCast'),ev(I,'DamageSources','applyDamage','DamageSource damageSource'),ev(I,'SpellRegistry','registerSpell'),span(I,'SpellRegistry',114,114,'SHADOW_SLASH_registration'),
 dedup='区别既有Iron友伤拒绝与Boss受伤模板：此处是真实抛射物反制资格及两个不同结果生产点。整片粒子/招架声与helper不再各拆计。')
add('iron-true-invisibility-native-target-acquisition-refusal-and-break-on-attempt',
 '真实InvisibilitySpell赋TRUE_INVIS；onEffectAdded扫描40格正在以施法者为目标的Mob，清target、停targetSelector全部goal、抹Brain ATTACK_TARGET。ServerPlayerEvents.onLivingChangeTarget又对新目标携此效果直接event.setCanceled(true)。LivingIncomingDamageEvent中攻击源实体若有此效果即移除，不等待最终伤害完成。',
 '拒控可由原生目标更换事件硬拒绝，同时清既有AI状态；解除触发若处于incoming阶段，应如实称攻击尝试破隐，不能称成功伤害回执。',
 '无游戏验证；40格外已有目标不在首次扫描内；事件拒绝新目标不是最终伤害无敌，也未证明直接调用伤害全部被拦。该原生链只参考目标控制，不复制守卫策略或计入旧guard1000。',
 'SpellRegistry.INVISIBILITY→InvisibilitySpell.onCast→MobEffectRegistry.TRUE_INVISIBILITY→TrueInvisibilityEffect.onEffectAdded；原生LivingChangeTargetEvent→ServerPlayerEvents.onLivingChangeTarget；攻击尝试→onDealDamage撤销',
 ev(I,'ServerPlayerEvents','onLivingChangeTarget'),ev(I,'InvisibilitySpell','onCast'),ev(I,'TrueInvisibilityEffect','onEffectAdded'),ev(I,'TrueInvisibilityEffect','onDealDamage'),span(I,'MobEffectRegistry',34,34,'TRUE_INVISIBILITY_registration'),span(I,'SpellRegistry',124,124,'INVISIBILITY_registration'),
 dedup='区别001Root乘骑免控/002Bubble重挂：禁止后续AI获取目标并清Brain/selector且攻击尝试解除。MobEffect注册、扫描、监听共同1条不逐门计。')
add('ars-rune-filtered-collider-versus-deferred-recipient-and-attempt-consumption',
 'EffectRune实际建立临时Rune，取消原context并用剩余法术加Touch。原生entityInside对entityIn依次验证前导IFilter，但记住的是碰撞列表entities.getFirst；1tick后block tick对touchedEntity施法后清引用。RuneTile.castSpell要求已充能/Touch/服务端且非禁用，调用resolver.onCastOnEntity却忽略布尔结果，临时符文直接销毁，永久符文耗掉充能并40tick后尝试付source充能，缺source改60tick重试。',
 '延迟回执须保留同一实际接纳目标，过滤对象与延迟接收者不同会错绑；消耗一次尝试不代表目标接受控制/伤害。',
 '源码静态边界不是已复现错误。RuneTile保存spell、充能与owner等而不保存touchedEntity；它是FakePlayer/敏感在线owner上下文，不能冒称真实玩家测试。未把40/60tick常量或临时/永久两个分支拆成信用。',
 'EffectRune.onResolve→RuneBlock原生entityInside→scheduled block tick→RuneTile.castSpell→EntitySpellResolver→SpellResolver.onCastOnEntity→MethodTouch→resolveAllEffects/Pre取消；RuneTile.tick实际重充',
 ev(A,'RuneBlock','entityInside'),ev(A,'EffectRune','onResolve'),ev(A,'RuneBlock','tick'),ev(A,'RuneTile','castSpell'),ev(A,'RuneTile','tick'),ev(A,'RuneTile','saveAdditional'),ev(A,'RuneTile','loadAdditional'),ev(A,'EntitySpellResolver','__complete_file__'),ev(A,'SpellResolver','onCastOnEntity'),ev(A,'SpellResolver','onResolveEffect'),ev(A,'SpellResolver','resolveAllEffects'),ev(A,'SpellResolver','resume'),ev(A,'MethodTouch','onCastOnEntity'),ev(A,'TickableModBlock','__complete_file__'),ev(A,'ITickableBlock','__complete_file__'),
 dedup='与001 Ars pre/post damage或绿预览不同，本条为实际原生碰撞入口的过滤收件人/延迟尝试预算完整链，resolver共享只支持。')
add('spellengine-melee-server-relation-distance-final-attempt-and-request-local-sound-budget',
 '实际AttackPerform接收器将player当前世界任务交Melee.performAttackAgainstTargets。服务端夹charge、解析spell/attack，逐raw targetIds查当前世界实体，复核isAttackable/关系/距离容差，清目标regen、把attacker攻击计时设100后调用void player.attack；不检查实际扣血就播放目标位置impactSound并将目标加入后续SpellImpacts.meleeImpact。sound cap每次调用重新赋attack配置或999。',
 '服务端最终边界应给出明确拒绝原因；距离/关系拒绝不能推断成Boss免疫，尝试后声响也不能证明伤害成功。音源上限的作用域应精确到一次请求。',
 '只读未发包/未运行，不宣称漏洞可利用。当前方法不去重重复ID，也不验证客户端hitTicks/当前武器/已发行attack nonce；客户端OBB/视线筛选不是本服务端函数的重查。异常时lastAttackedTicks/目标regen恢复位于try内，临时伤害modifier与activeSkill清理在catch后。',
 'SpellDelivery.deliver MELEE→AttackAvailable→客户端队列/目标检测→AttackPerform→FabricServerNetwork注册→ServerNetwork.handleAttackPerform→Melee.performAttackAgainstTargets→player.attack→目标音/SpellImpacts.meleeImpact',
 ev(S,'Melee','performAttackAgainstTargets'),ev(S,'ServerNetwork','handleAttackPerform'),ev(S,'Melee','resolveAttackData','Identifier spellId'),ev(S,'Melee','resolveCharge'),ev(S,'Melee','focusMode'),ev(S,'Melee','largesSideLength'),ev(S,'SpellImpacts','meleeImpact'),ev(S,'SpellDelivery','deliver','boolean forceSuccess'),ev(S,'FabricServerNetwork','init'),
 dedup='区别004 per-player/per-spell trigger quota：本条为实际MELEE C2S终端的关系/距离拒绝及按请求声音预算；hurt结果未读为明确反例。包装/临时属性均不单计。')
add('spellengine-melee-client-queued-hit-schedule-and-target-stamp-before-receipt',
 'AttackAvailable在client.execute中交ClientPlayerEntity.onAttacksAvailable，仅append队列。原生tick TAIL按age处理ActiveAttack：ATTACK受限时清current却保留排队；主手Item类型改变取消current也保留队列；到hitTicks才detectTargets，按每ActiveAttack整数ID集合排除已打目标（配置允许重复时除外），发送前就加入集合。激活时发AttackFxBroadcast并本地动画，不等待服务端命中回执。',
 '客户端去重记录的是已发送尝试，不能当服务器已接纳；失控/换武器取消后待执行队列是否保留需明确，短闪提示不能由技能激活动画反推命中。',
 '不做运行断言。武器快照比较Item而非具体ItemStack/UUID；目标集合是整数实体ID，不能视为跨加载代际身份校验。资源Mixin声明仅005网页支持，未进行原生Mixin启用验证。',
 'SpellDelivery MELEE生成攻击档→ClientNetwork.handleAttackAvailable→onAttacksAvailable→原生client tick_TAIL→ActiveAttack hitTicks→TargetFinder.findAttackTargetResult→onAttackHit→AttackPerform；另onAttackActivated→AttackFxBroadcast→服务端broadcastAttackFx',
 ev(S,'ClientPlayerEntityMixin','onTick_ScheduledAttacks'),ev(S,'ClientPlayerEntityMixin','onAttacksAvailable'),ev(S,'ClientPlayerEntityMixin','checkForNextAttack'),ev(S,'ClientPlayerEntityMixin','onAttackActivated'),ev(S,'ClientPlayerEntityMixin','onAttackHit'),ev(S,'ClientPlayerEntityMixin','tick_TAIL_SpellEngine'),ev(S,'ClientNetwork','handleAttackAvailable'),ev(S,'Melee','__complete_file__'),ev(S,'TargetFinder','__complete_file__'),ev(S,'ServerNetwork','handleAttackFxBroadcast'),
 dedup='与上一条服务端终端边界为独立位置/策略：本条原生客户端时序与发送前打戳；与既有wizardry链历史不同但共享整数ID去重家族允许主岗合并支持。ActiveAttack时钟/目标geometry不逐个计。')
add('iron-echoing-post-damage-qualified-recursion-filter-and-consumable-proc',
 '真实EchoingStrikesSpell赋2400tick buff并按level+2重置attachment命中数；EchoingStrikesEffect.createEcho挂LivingDamageEvent.Post，仅Living攻击者、直接近战或Arrow且非SpellDamageSource能触发。持buff且hasHits才按Post newDamage比例生成有owner/同目标的EchoSword或Arrow，随后减一次、耗尽撤buff；没有显式newDamage>0门。法术伤害类型排除避免自身echo再次生成echo。',
 '权威后置事件、来源类型与递归拒绝可以独立于展示；一个消费次数只代表通过这组触发门，若要免疫文字还需要具体拒绝原因，不能靠有无echo猜。',
 '只读未运行，不把Post名称自动当保证正伤害。addEffect返回被忽略后仍覆盖hitCount；buff移除删数据，未另核定附件跨保存策略，不能宣称预算跨死/跨档。',
 'SpellRegistry.ECHOING_STRIKES→EchoingStrikesSpell.onCast→注册MobEffect/attachment→原生LivingDamageEvent.Post→EchoingStrikesEffect.createEcho→createEchoingSword/createEchoingArrow→消耗次数/移除效果',
 ev(I,'EchoingStrikesEffect','createEcho'),ev(I,'EchoingStrikesSpell','onCast'),ev(I,'EchoingStrikesEffect','onEffectStarted'),ev(I,'EchoingStrikesEffect','onEffectRemoved'),ev(I,'EchoingStrikesEffect','createEchoingSword'),ev(I,'EchoingStrikesEffect','createEchoingArrow'),ev(I,'EchoingStrikesEffect','getDamageModifier'),ev(I,'EchoingStrikesData','__complete_file__'),span(I,'MobEffectRegistry',68,68,'ECHOING_STRIKES_registration'),span(I,'SpellRegistry',111,111,'ECHOING_STRIKES_registration'),
 dedup='区别004 reactive PRE trigger quota/概率：这里确有原生Post消费及SpellDamageSource反递归，非每同源武器模板计数。计数器小方法仅支持0。')
add('iron-echo-sword-last-target-position-delayed-hit-and-authoritative-expiry',
 '实际Post生成EchoSword并setHomingTarget。tick调用baseTick后每次更新缓存目标中心，若从未拿到目标且lastHomingPos仍Vec3.ZERO引用即die；目标消失后沿最后坐标继续。tickCount25实际AOE performHit，45清退；hit先播放声音再client侧return，服务端按range/LOS/canHitEntity伤害，忽略applyDamage布尔值仍有爆波。die服务端发火花并discard，shouldBeSaved=false。',
 '延迟表现应区分追踪有效目标与最后已知坐标；短时攻击载体的发声/爆波不是受害者接纳回执，目标已经卸载时也不能发错对象的免疫提示。',
 '静态未运行，无实际计时。homing getter检查removed未检查isAlive，客户端首次spawn按整数ID找不到目标不见重试；lastHomingPos是位置回退并非UUID新代际校验。这里是实际延迟伤害载体，不把同源EchoArrow去重另计。',
 'EchoingStrikesEffect.createEchoingSword→setHomingTarget→原生EchoingSword.tick→getHomingTarget/moveAndRotateTowards→tick25 performHit→DamageSources.applyDamage；tick45 die→discard；原生spawn读写owner/target integer ID',
 ev(I,'EchoingSword','tick'),ev(I,'EchoingStrikesEffect','createEchoingSword'),ev(I,'EchoingSword','moveAndRotateTowards'),ev(I,'EchoingSword','performHit'),ev(I,'EchoingSword','die'),ev(I,'EchoingSword','shouldBeSaved'),ev(I,'AbstractMagicProjectile','getHomingTarget'),ev(I,'AbstractMagicProjectile','setHomingTarget'),ev(I,'AbstractMagicProjectile','canHitEntity'),ev(I,'AbstractMagicProjectile','writeSpawnData'),ev(I,'AbstractMagicProjectile','readSpawnData'),
 dedup='区别005纯模型TTL实体：此处实际延迟AOE伤害、失靶坐标回退和原生回调。与本批Post触发资格是独立生产/消费决策；如主岗认为与已有追踪攻击家族同构可降支持。')
add('ars-touch-combat-light-fade-world-capture-and-pause-lifetime',
 '真实MethodTouch.onCastOnEntity先resolveEffects，再无条件resolveEmitter/resolveSound/addFadingLight；S2C按目标区块tracking发三个double，客户端捕获当前level创建FadeLightTimedEvent，以Config duration/luminance入EventQueue。非paused的client Post tick推进，亮度按ticksLeft/starter衰减，<=0撤本地light tracking；外部动态光context走其behavior isRemoved。注销清clientQueue。',
 '短闪反馈必须有真实战斗生产链与清退生命周期；以客户端本地tick计时会随暂停延长，捕获世界与当前收包世界不同风险需说明；光闪不携成功/immune原因。',
 '源码静态未运行；无UUID/维度/事件序号或同目标节流，重复包会新增独立event。默认动态光配置和外部context可不显示；Java中world更换Mixin清light sources，而logout仅清queue（ITimedEvent.onServerStopping默认空）。Mixin注册资源不在本地Java缓存，未因此宣称已运行。没有制作新光效/资产，通用LightManager基础设施全支持0。',
 'SpellResolver.onCastOnEntity→MethodTouch.onCastOnEntity→addFadingLight→Networking.sendToNearbyClient tracking chunk→注册PacketAddFadingLight→ClientMessageHandler→Handle.handle→FadeLightTimedEvent/EventQueue.clientTickEvent→renderWorldLastEvent/LightManager.updateAll→LevelRenderer/EntityRenderer light mixin；ClientMixin更换level时清sources',
 ev(A,'PacketAddFadingLight','handle'),ev(A,'MethodTouch','onCastOnEntity'),ev(A,'MethodTouch','addFadingLight'),ev(A,'PacketAddFadingLight','__complete_file__'),ev(A,'Networking','register'),ev(A,'Networking','handle'),ev(A,'Networking','handleClient'),ev(A,'Networking','sendToNearbyClient','BlockPos pos'),ev(A,'FadeLightTimedEvent','__complete_file__'),ev(A,'EventQueue','__complete_file__'),ev(A,'LambDynamicLight','__complete_file__'),ev(A,'LightManager','__complete_file__'),ev(A,'ClientEvents','onPlayerLoggedOut'),ev(A,'ArsNouveau','ArsNouveau'),ev(A,'ClientEvents','renderWorldLastEvent'),ev(A,'ITimedEvent','__complete_file__'),ev(A,'ClientMixin','__complete_file__'),ev(A,'src/main/java/com/hollingsworth/arsnouveau/common/mixin/light/LevelRendererMixin','__complete_file__'),ev(A,'EntityRendererMixin','__complete_file__'),
 dedup='实际Touch战斗闪光的本地世界/暂停计时/两种光源清退一条；区别005模型实体TTL，不按光源邻区块/插值算法拆数。若主岗只收拒控语义此条可降支持。')
add('iron-echoing-local-cast-hologram-is-not-target-hit-receipt-support',
 'AbstractSpell.castSpell完成onCast后向当前serverPlayer发OnClientCastPacket，客户端helper对当前Minecraft.player调用spell.onClientCast；EchoingStrikesSpell只把该本地实体attachment vfxTimestamp设tickCount+20。已注册玩家render layer按剩余/20 clamp衰减透明度，以FULL_BRIGHT画重影；不是按每个受击目标生产的包，也不是灰字。',
 '局部短闪可有独立本地期限，但必须明确归属施法者而非受害者，不能把施法完成确认冒称目标被控/免疫回执。',
 '同既有短时模型表现家族支持0，不以Vanilla/Geo renderer模板或几何算法补数。没有检查运行可见性；未声称带UUID或远端玩家同样得到时间戳。',
 'AbstractSpell.castSpell→OnClientCastPacket→ClientSpellCastHelper.handleClientboundOnClientCast→EchoingStrikesSpell.onClientCast→EchoingStrikesHologramLayer.getRenderPercent；ClientSetup.addLayerToPlayerSkin实际注册消费者',
 ev(I,'EchoingStrikesHologramLayer','getRenderPercent'),ev(I,'AbstractSpell','castSpell'),ev(I,'OnClientCastPacket','__complete_file__'),ev(I,'ClientSpellCastHelper','handleClientboundOnClientCast'),ev(I,'EchoingStrikesSpell','onClientCast'),ev(I,'EchoingStrikesHologramLayer','__complete_file__'),ev(I,'ClientSetup','addLayerToPlayerSkin'),ev(I,'PayloadHandler','register'),status='support_only_not_effective',
 dedup='已计005模型生命周期家族不再自动计；本条只补真实producer归属，不拆两renderer。')
supplements=[]
assert len(rows)<=30
for repo in BASE:
 d=LOCAL/'sources-batch006'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo in (A,S):shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for n in ('001','002','003','004','005') for r in json.loads((OUT/f'batch-{n}.json').read_text())['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
assert not overlaps,overlaps
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert len(primary)==len(set(primary))
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-006','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'max_units':30,'rows':rows,'support_for_prior_batches':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'候选不等于信用；主岗需最终相关性/语义去重。本批不按模板补到30。代码均固定本地源码审阅；本批外部请求0；既有005注册网页全文观察支持0、原始资源TLS失败未重试。无游戏/正式代码修改。'}
(OUT/'batch-006.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-006.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars/SpellEngine pinned Git tree/blob；Iron pinned archive source.json SHA256 inventory，无相同commit树，不冒称blob已独立核验。'},ensure_ascii=False,indent=2)+'\n')
allrefs=[v for r in rows+supplements for v in r['source_refs']]
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'supplement_units':len(supplements),'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(r['unit']=='complete_method' for r in allrefs),'complete_support_resource_references':sum(r['unit']=='complete_support_resource' for r in allrefs),'batch_sha256':sha((OUT/'batch-006.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':0,'todo_modified':False}
(OUT/'receipt-006.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
