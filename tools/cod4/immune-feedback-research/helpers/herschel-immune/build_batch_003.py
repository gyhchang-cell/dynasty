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
 if method=='__complete_file__':starts=[1]
 assert len(starts)==1,(name,method,qualifier,starts)
 start=starts[0];end=len(lines) if method=='__complete_file__' else reader.end_method(lines,start);excerpt=''.join(lines[start-1:end]);pin=meta[repo];commit=pin.get('commit',pin.get('sha'));blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if repo in (A,S):
  tree=json.loads((BASE[repo]/'tree.json').read_text());assert tree['sha']==commit;assert next(x['sha'] for x in tree['tree'] if x['path']==rel)==blob
  proof='pinned Git tree blob SHA1'
 else:
  entry=next(x for x in pin['files'] if x['path']==rel);assert entry['sha256']==sha(data);proof='pinned archive source.json SHA256 inventory'
  if 'git_blob_sha1' in entry:assert entry['git_blob_sha1']==blob;proof='pinned source inventory SHA256 and Git blob SHA1'
 dest=LOCAL/'sources-batch003'/repo/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 verified[f'{repo}/{rel}']={'repo':pin['repo'],'commit':commit,'path':rel,'sha256':sha(data),'computed_git_blob_sha1':blob,'proof':proof,'local':str(dest.relative_to(ROOT))}
 return {'unit':'complete_support_resource' if method=='__complete_file__' else 'complete_method','source_key':f'{repo}/{rel}','method':method,'lines':[start,end],'url':f"https://github.com/{pin['repo']}/blob/{commit}/{rel}#L{start}-L{end}",'file_sha256':sha(data),'excerpt_sha256':sha(excerpt.encode()),'normalized_excerpt_sha256':sha(re.sub(r'\s+','',excerpt).encode()),'excerpt':excerpt}
def ev(repo,name,method,qual=None):return evidence(repo,name,method,qual)
def add(key,obs,application,limits,chain,*refs,status='pending_primary_semantic_review',dedup=''):
 rows.append({'id':f'herschel-003-{len(rows)+1:02d}','semantic_dedup_key':key,'status':status,'research_credit':0,'suggested_credit':0,'count_unit':'independent behavior site with complete containing methods; no automatic promotion','source_refs':list(refs),'observation':obs,'native_chain':chain,'application':application,'limits':limits,'deduplication':dedup or '与本批其他行按实际决策/结果分开；与001/002及当前主账按决策语义比较，完整方法共享只作支持；晋级仍须主岗复核。调用包装和同链支持不另计。'})
add('iron-guiding-bolt-native-projectile-immunity-and-control-assignment',
 'EntityJoinLevel原生事件仅server且已有追踪目标才收Projectile，GUIDING_BOLT_IMMUNE类型不入dirty。LevelTick.Post按当前维度、向前raycast、各轴48格及目标膨胀包围盒匹配第一个非owner目标，绑定Projectile集合；EntityTick.Pre逐tick保持速度大小转向，反向dot<-0.75/removed退出。效果首次加入start，原生onEffectRemoved Mixin及server死亡回调委托stop；Start包目标UUID+弹整数ID，Stop包UUID。',
 '抗强制转向是弹种资格，不能显示成受击Boss免疫；目标/弹绑定必须由权威资格分支产生，客户端视觉状态不能反推伤害。',
 '没有默认tag内容缓存，不声称哪些实际弹种受保护；首次目标加入不会将既有全世界弹重新扫描。客户端Start仅立即查现有整数ID，缺弹丢失且无重试；客户端死亡清理调用server-only stopTracking无效，Stop/Logout才显式清map。没有运行或网络验证。',
 'GuidingBoltEffect加入→startTracking；EntityJoinLevel→onProjectileShot→LevelTick.Post serverTick→Start S2C→livingTick；效果移除→stopTracking→Stop S2C；Client LoggingOut→clear',
 ev(I,'GuidingBoltManager','onProjectileShot'),ev(I,'GuidingBoltEffect','onEffectAdded'),ev(I,'GuidingBoltEffect','onEffectRemoved'),ev(I,'LivingEntityMixin','irons_spellbooks$onEffectRemoved'),ev(I,'ServerPlayerEvents','onLivingDeathEvent'),ev(I,'MagicMobEffect','__complete_file__'),ev(I,'GuidingBoltManager','startTracking'),ev(I,'GuidingBoltManager','stopTracking'),ev(I,'GuidingBoltManager','serverTick'),ev(I,'GuidingBoltManager','livingTick'),ev(I,'GuidingBoltManager','handleClientboundStartTracking'),ev(I,'GuidingBoltManager','handleClientboundStopTracking'),ev(I,'GuidingBoltManager','handleClientLogout'),ev(I,'GuidingBoltManagerStartTrackingPacket','handle'),ev(I,'GuidingBoltManagerStartTrackingPacket','write'),ev(I,'GuidingBoltManagerStopTrackingPacket','handle'),ev(I,'GuidingBoltManagerStopTrackingPacket','write'),ev(I,'PayloadHandler','register'),ev(I,'ClientPlayerEvents','onPlayerLogOut'),
 dedup='同一Guiding控制分配/取消链合计1候选，两个packet/manager包装不拆。不同于001 Root乘骑和Telekinesis抗性；不复用Guard账。')
add('iron-enderchain-breakable-control-window-and-part-fx-order',
 'ArcaneShackle命中Living或Part母体即生成三链，块命中按canHit或multipart及范围找目标。EnderChain server tick在victim缺失/removed、距离平方>144、age>lifetime或health<=0时break，否则加回拉速度。hurt先拒invulnerableTime>0，再拒client/nativeinvul/友伤，扣链health后设置10tick窗口；Part先发3 sparks才委托父hurt，故拒伤仍可能有受击粒子。breakChain服务端声音/分布火花/discard。',
 '控制载体自身受伤拒绝和受害目标免控要分开；统一回执应出最终分支后，Part预发粒子不能当真实扣血。破链释放应与租期、目标死亡/离距同时核对。',
 '回拉无Boss/knockback-resistance最终门；deltaV.multiply(deltaV)未接返回值。这里只研究可破坏控制载体与反馈次序；自定义10tick伤害窗与原生hurt cooldown/001FrozenHumanoid可能语义合并，绝不自动信用。',
 'ArcaneShackle.onHitEntity/onHitBlock→spawnChain→EnderChain.tick/applyRestraint；Part.hurt预FX→parent.hurt拒绝/扣链HP→breakChain→discard',
 ev(I,'EnderChain','hurt'),ev(I,'ArcaneShackleProjectile','onHitEntity'),ev(I,'ArcaneShackleProjectile','onHitBlock'),ev(I,'ArcaneShackleProjectile','spawnChainsOnEntity'),ev(I,'ArcaneShackleProjectile','spawnChainsFromBlock'),ev(I,'ArcaneShackleProjectile','spawnChain'),ev(I,'EnderChain','tick'),ev(I,'EnderChain','applyRestraint'),ev(I,'EnderChain','breakChain'),ev(I,'EnderChainPart','hurt'),
 dedup='owner/friendlyfire仅001已计家族支持；仅提可破坏控制载体的共享伤害窗/子部件先发FX这一具体链。若与001Shield/Frozen同策略则降支持，不按8个part拆。')
add('ars-wall-per-target-attempt-window-and-expiry-burst',
 'Wall对每实体WeakReference+gameTime过滤；差值>20移除旧记录并允许本次解析，但随后仅hit.isEmpty才登记，过期Optional仍present，导致这次没有重新打戳，紧邻下次可再解析。i>5才break因此可到6；第6项break前已经解析/计数但未走下面声音。每实体offset到半高、client独立发resolve粒子，不读服务端解析/实际伤害结果。',
 '同目标限流应在最终事件生产处原子更新；显示寿命、尝试频率和权威拒绝回执分别设计。客户端几何命中发光不能认定Boss受控成功。',
 '本条静态边界非已复现bug。server/client各自扫描及计时，未证明一致；LINGERING_BLACKLIST非Boss免疫字。父tick过期remove后return只退出父方法，Wall.tick仍继续castSpells，不能声称最后一tick绝无解析。',
 'APIRegistry注册EffectWall→onResolve构造Wall并取消原context→Wall.tick→父tick age/expiry→castSpells目标窗口→server resolver/client emitter→totalProcs移除',
 ev(A,'EntityWallSpell','castSpells'),ev(A,'EffectWall','onResolve'),ev(A,'EntityWallSpell','tick'),ev(A,'EntityProjectileSpell','tick'),ev(A,'EntityWallSpell','getExpirationTime'),ev(A,'EntityWallSpell','buildEmitters'),ev(A,'EntityWallSpell','EntityHit'),
 dedup='按目标持续AOE尝试限流与002Portal进出冷却不是同链；与001/002无同主方法。EffectLinger/Orbit若采用相同hitEntities骨架禁止另计。')
add('ars-native-cast-refusal-chat-replacement-ignores-channel',
 'SpellResolver.canCast验证失败仅server&&!silent发送首错误并false；enoughMana失败再发no_mana。PortUtil仅ServerPlayer发NoSpam。包编码message/channel/overlay；客户端非overlay按唯一AN_SIGNATURE移除旧聊天、rescale、加金色消息，却完全未用解码的messageChannelId；不同频道实际共用槽。overlay走displayClientMessage。',
 '拒绝理由必须由实际失败生产；避免提示串目标需要真正参与查找的key，协议里有channel不代表正确隔离。替换历史不是发包限流。',
 '施法者屏幕聊天/overlay，无目标UUID/世界锚定；非Boss世界灰字，不将其计为已实现战斗浮字。与002SpellEngine单槽HUD概念有关，主岗可按反馈家族合并。无网络/视觉运行。',
 '原生SpellResolver.canCast/enoughMana拒绝→PortUtil.sendMessageNoSpam→Networking S2C注册/派发→NoSpam.onClientReceived→ChatComponentAccessor删除/新消息',
 ev(A,'PacketNoSpamChatMessage','onClientReceived'),ev(A,'PacketNoSpamChatMessage','toBytes'),ev(A,'PortUtil','sendMessageNoSpam'),ev(A,'PortUtil','sendMessageCenterScreen'),ev(A,'SpellResolver','canCast'),ev(A,'SpellResolver','enoughMana'),ev(A,'Networking','register'),ev(A,'Networking','handle'),ev(A,'Networking','handleClient'),ev(A,'Networking','sendToPlayerClient'),ev(A,'ChatComponentAccessor','__complete_file__'),
 dedup='单条覆盖原生失败生产与聊天签名替换；不按两类错误/两个显示分支拆条；比002HUD新增聊天历史删除及channel未消费反例，是否独立信用由主岗。')
add('iron-corpse-refused-hit-triggers-idempotent-boss-awakening',
 'DeadKingCorpse.hurt对bypass来源discard且true，其他来源无论amount都找8格最近玩家，有玩家trigger后返回false。trigger仅TRIGGERED尚false时播复活声并同步true；server tick触发动画时长>300后生成新DeadKingBoss、spawn声/粒子并discard尸体，每tick还回满HP。',
 '返回false不一定是没有 gameplay 后果：拒伤可以只推进Boss阶段。免疫字若显示也不能吞掉阶段触发；音效幂等依赖同步触发位，不靠HP变更。',
 '最近玩家未必攻击者，环境伤害也可能唤醒；hurt未显式server-only，trigger声/位可两侧调用，实体生成只server；绕过伤害返回true仅代表删除，不是扣血成功。',
 '原生corpse.hurt→bypass删除 或 nearestPlayer→trigger(flag/sound)→原生tick计时→server新Boss实体/FX→discard',
 ev(I,'DeadKingCorpseEntity','hurt'),ev(I,'DeadKingCorpseEntity','trigger'),ev(I,'DeadKingCorpseEntity','tick'),ev(I,'DeadKingCorpseEntity','defineSynchedData'),ev(I,'DeadKingCorpseEntity','mobInteract'),
 dedup='区别001静态EMERGING阶段true门：拒绝这次hurt会主动触发幂等复活链和新实体替换。若主岗仍按阶段无敌模板归并可降支持，所有尸体方法合计1候选。')
add('iron-dimension-spell-teleport-rejection-precedes-success-proof',
 '原生EntityTeleportEvent订阅在PocketDimension且ServerLevel拒绝除TeleportCommand外事件。SpellTeleportEvent确继承该事件；Utils.handleSpellTeleport post后仅未取消才teleportTo，返回值true实际表示已取消。TeleportSpell.onCast却先发出两点粒子，再可能下马，然后忽略cancel返回值，重置fall/附加数据并播完成声。',
 '拒控权威分支与预发成功外观分离；cancel boolean语义必须明确，不能用已有传送粒子/完成声推断移动成功，更不能误称Boss免疫。',
 '只覆盖走NeoForge事件的传送，不能声称所有直接teleportTo被禁止。此策略基于维度而非目标Boss标签；粒子包仅pos1/pos2无维度/目标UUID，客户端按当前player.level生成。',
 'TeleportSpell.onCast先FX→Utils.handleSpellTeleport→post SpellTeleportEvent→ServerPlayerEvents.preventPocketDimensionTeleportation取消→跳过teleportTo→调用方仍完成声；S2C粒子handler→当前level particleCloud',
 ev(I,'ServerPlayerEvents','preventPocketDimensionTeleportation'),ev(I,'Utils','handleSpellTeleport'),ev(I,'SpellTeleportEvent','SpellTeleportEvent'),ev(I,'TeleportSpell','onCast'),ev(I,'TeleportParticlesPacket','write'),ev(I,'TeleportParticlesPacket','handle'),ev(I,'ClientSpellCastHelper','handleClientboundTeleport'),ev(I,'TeleportSpell','particleCloud'),
 dedup='与002Portal目标/portal cooldown不同最终原生事件拒绝点；同一取消与预发FX链合计1，不另计API包装和粒子packet。')
add('ars-summon-native-damage-origin-whitelist-not-owner-filter',
 'Alakarkinos原生hurt短路调用SummonUtil.canSummonTakeDamage：只有BYPASSES_INVULNERABILITY或来源entity是Player才准父hurt。它没有读取召唤owner；玩家归属投射物以damageSource.getEntity为准，普通非玩家实体/无entity环境来源被拒。',
 '拒伤reason应表达来源资格，不是把所有false叫Boss无敌；允许用户攻击自己的召唤物和拒绝其他怪物攻击可以同时成立。',
 '只证这条实体伤害路径，不能推到全部召唤物；helper healOverTime不是免疫且不单独计。Nook的Player-only变体同族降支持，不按实体名单放大。',
 'Alakarkinos.hurt→SummonUtil.canSummonTakeDamage→bypass/player whitelist→super.hurt或false',
 ev(A,'Alakarkinos','hurt'),ev(A,'SummonUtil','canSummonTakeDamage'),
 dedup='区别001/002的owner/allied拒伤：此处不看owner而看来源类别+bypass；若已有主账同SummonUtil入口则必须合并。一个helper所有消费者仅1候选。')
add('iron-boss-attacker-filter-support-not-new-template',
 'CursedArmorStand.hurt若来源entity被标BOSSES直接false；其他来源先setArmorStandFrozen(false)再super.hurt，即父hurt最终失败仍可能解冻。',
 '最终伤害资格前后副作用不同；Boss标签在此标攻击者，不能看见BOSSES就当受害Boss免控。',
 '标签资格模板且与主课题间接相关，仅支持0；没有默认tag/父hurt实跑，不建议独立新增有效数。',
 '原生hurt→来源Boss tag拒绝→其他来源解冻→super',ev(I,'CursedArmorStandEntity','hurt'),status='support_only_not_effective',dedup='来源类别门的相近模板，仅支持上一条及伤害阶段副作用观察，不独立凑数。')
add('iron-keeper-source-immunity-and-reduction-support',
 'Keeper.isInvulnerableTo在父判断外拒绝IS_FALL；hurt对直接Projectile仅乘0.75不是拒绝，age<10的IN_WALL尝试拆窒息块，然后仍交父hurt。',
 '部分减伤/解除窒息不等同immune；IS_FALL是来源tag，不是Boss身份。',
 '来源常量换壳与同类hurt模板，支持0；不将0.75算免疫实现。',
 '原生isInvulnerableTo来源门；原生hurt修amount/破块→super',ev(I,'KeeperEntity','isInvulnerableTo'),ev(I,'KeeperEntity','hurt'),status='support_only_not_effective',dedup='不把每一元素/伤害tag或每实体重复包装计数。')
add('iron-cast-error-hud-receiver-without-proven-producer',
 '已注册playToClient CastErrorPacket，codec是COOLDOWN/MANA+spellId，enqueueWork进handleCastErrorMessage。COOLDOWN需hasReleasedSinceCasting才覆写红色overlay，MANA无此门。全固定Iron Java缓存未找到new CastErrorPacket实际发送消费者。',
 '接收器能展示错误不代表服务器存在该回执生产；按住防抖不能据此宣称全错误或免疫字已限流。',
 '缺发送生产链支持0，不声称接活。也无目标ID/expirykey/浮动世界锚；不重复002SpellEngine已计错误HUD。',
 'PayloadHandler注册→CastErrorPacket.handle→ClientSpellCastHelper.handleCastErrorMessage；实际new/send未找到',ev(I,'ClientSpellCastHelper','handleCastErrorMessage'),ev(I,'CastErrorPacket','write'),ev(I,'CastErrorPacket','handle'),ev(I,'PayloadHandler','register'),status='support_only_not_effective',dedup='无生产消费证据，不以孤立receiver凑数；同002 HUD仅对照。')

supplements=[
 {'support_for_batch002':'herschel-002-01','research_credit':0,'suggested_credit':0,
  'observation':'Protection.register三个重载仅向公开PROTECTIONS map加入entry。对两个相同commit SpellEngine本地cache全Java搜索Protection.register/new Protection/PROTECTIONS，只有定义与tryProtect查询，未找到实际游戏效果注册消费者。保留主岗pending0，不以API存在充接活。',
  'limits':'仅固定本地缓存搜索，未宣称全网络/所有addon没有消费者；没发外部请求。',
  'source_refs':[ev(S,'Protection','__complete_file__')]},
 {'support_for_batch002':'herschel-002-12','research_credit':0,'suggested_credit':0,
  'observation':'ArsNouveau构造器调用APIRegistry.setup注册RitualDisintegration。RitualRegistry按ID模板反射新实例；RitualBrazier.setRitual将tile回绑。方块继承TickableModBlock/ITickableBlock，其getTicker→ITickable.tick(level,state,pos)→tile.tick；红石isOff/完成/所需source及backoff可挡运行，relay分支更换tick位置。tryTick要求started&&!done并回绑tile后调用RitualDisintegration.tick；空手useItemOn→startRitual(player)→onStart设started。原始直接remove分支确在可达原生调度下。',
  'limits':'调度补证不增加信用；未实际启动仪式，source不足会return；不是普通伤害事件，不生成Boss immune的权威hurt原因。',
  'source_refs':[ev(A,'ArsNouveau','ArsNouveau'),ev(A,'APIRegistry','setup'),ev(A,'APIRegistry','registerRitual'),ev(A,'RitualRegistry','registerRitual'),ev(A,'RitualRegistry','getRitual'),ev(A,'RitualBrazierTile','setRitual'),ev(A,'TickableModBlock','__complete_file__'),ev(A,'RitualBrazierBlock','useItemOn'),ev(A,'RitualBrazierBlock','__complete_file__'),ev(A,'ITickableBlock','__complete_file__'),ev(A,'ITickable','__complete_file__'),ev(A,'RitualBrazierTile','tick'),ev(A,'RitualBrazierTile','startRitual','@Nullable Player player'),ev(A,'AbstractRitual','tryTick'),ev(A,'AbstractRitual','onStart'),ev(A,'AbstractRitual','isRunning'),ev(A,'RitualDisintegration','tick')]},
 {'support_for_batch002':'herschel-002-21','research_credit':0,'suggested_credit':0,
  'observation':'getTagForPerk返回PerkMap内部CompoundTag引用；死亡将同tag isActive=false，ArmorPerkHolder.setTagForPerk创建新holder，PerkMap.put利用copyAndPut创建新map；调用方明确holder.getA().set(ARMOR_PERKS,newHolder)。睡眠同路径写回true。ARMOR_PERKS注册persistent(ArmorPerkHolder.CODEC)，CODEC含perkTags；PerkMap.CODEC按perk registry名编码各CompoundTag。并非只修改局部临时tag。',
  'limits':'CompoundTag值没有深拷贝，不能声称组件完全不可变；本条只证明源码写回与codec可保存，不是实际存档/网络/死亡重生实验。',
  'source_refs':[ev(A,'PerkEvents','totemEvent'),ev(A,'PerkEvents','sleepEvent'),ev(A,'StackPerkHolder','getTagForPerk'),ev(A,'ArmorPerkHolder','setTagForPerk'),ev(A,'PerkMap','put'),ev(A,'ArmorPerkHolder','__complete_file__'),ev(A,'PerkMap','__complete_file__'),ev(A,'DataComponentRegistry','__complete_file__')]}
]
assert len(rows)<=30
for repo in BASE:
 d=LOCAL/'sources-batch003'/repo;d.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE[repo]/'source.json',d/'source.json')
 if repo in (A,S):shutil.copy2(BASE[repo]/'tree.json',d/'tree.json')
prior_hashes={r['source_refs'][0]['normalized_excerpt_sha256']:r['id'] for n in ('001','002') for r in json.loads((OUT/f'batch-{n}.json').read_text())['rows']}
overlaps=[{'new':r['id'],'prior':prior_hashes[r['source_refs'][0]['normalized_excerpt_sha256']]} for r in rows if r['source_refs'][0]['normalized_excerpt_sha256'] in prior_hashes]
assert not overlaps,overlaps
primary=[r['source_refs'][0]['normalized_excerpt_sha256'] for r in rows];assert len(primary)==len(set(primary))
master=(MASTER/'reviewed.json').read_bytes()
batch={'batch':'herschel-immune-003','created_utc':datetime.now(timezone.utc).isoformat(),'research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_review_units':sum(r['status']=='pending_primary_semantic_review' for r in rows),'support_only_units':sum(r['status']=='support_only_not_effective' for r in rows),'effective_promoted':0,'max_units':30,'rows':rows,'support_for_batch002':supplements,'prior_primary_exact_or_normalized_overlaps':overlaps,'master_snapshot_count':len(json.loads(master)),'master_snapshot_sha256':sha(master),'note':'候选不等于信用；主岗需最终相关性/语义去重。本批不按模板补到30。只有固定本地源码审阅，无外部请求/游戏/正式代码修改。'}
(OUT/'batch-003.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-manifest-003.json').write_text(json.dumps({'sources':list(verified.values()),'research_credit':0,'suggested_credit':0,'proof_limit':'Ars/SpellEngine pinned Git tree/blob；Iron pinned archive source.json SHA256 inventory，无相同commit树，不冒称blob已独立核验。'},ensure_ascii=False,indent=2)+'\n')
allrefs=[v for r in rows+supplements for v in r['source_refs']]
receipt={'status':'HELPER_REVIEW_COMPLETE_PENDING_PRIMARY','research_credit':0,'suggested_credit':0,'reviewed_units':len(rows),'pending_primary_semantic_review':batch['pending_primary_review_units'],'support_only':batch['support_only_units'],'supplement_units':len(supplements),'effective_credit':0,'source_files':len(verified),'complete_method_references':sum(r['unit']=='complete_method' for r in allrefs),'complete_support_resource_references':sum(r['unit']=='complete_support_resource' for r in allrefs),'batch_sha256':sha((OUT/'batch-003.json').read_bytes()),'master_files_unchanged_during_build':before=={p.name:sha(p.read_bytes()) for p in MASTER.iterdir() if p.is_file()},'production_modified':False,'game_launches':0,'external_requests':0,'todo_modified':False}
(OUT/'receipt-003.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
