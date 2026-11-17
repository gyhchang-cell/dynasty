"""Author batch006 from already fully read local pinned sources only."""
from pathlib import Path
p=Path(__file__).with_name('build_batch_005.py');s=p.read_text()
head=s[:s.index('impact=ev(S')].replace('005','006')
head=head.replace('与001/002及当前主账','与001–005及当前主账')
body=r'''
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
'''
tail=s[s.index('assert len(rows)<=30'):].replace('005','006').replace("('001','002','003','004')","('001','002','003','004','005')")
tail=tail.replace('另3次web只读注册全文成功、1次urllib原始资源TLS失败并停止外部请求。','本批外部请求0；既有005注册网页全文观察支持0、原始资源TLS失败未重试。')
tail=tail.replace("'external_requests':4","'external_requests':0")
Path(__file__).with_name('build_batch_006.py').write_text(head+body+tail)
v=Path(__file__).with_name('verify_batch_005.py').read_text().replace('005','006');Path(__file__).with_name('verify_batch_006.py').write_text(v)
