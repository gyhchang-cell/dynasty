"""Static Minecraft lifecycle review. Only own evidence code runs; upstream Java is text."""
import datetime
import hashlib
import json
from pathlib import Path
from evidence_003 import HERE, DOCS, WORKSPACE, CACHE, PINS, ROOTS, METADATA, method, dump, sha

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
ROWS = []
PINS.update(feature='fbb5d732098ec5832b8b8922843a023ed6f8baa2',
            multiloader1192='18680b77417740415df474b1fb6f8ffb25ed4735',
            tinkers='f4e77d43f39ba1047bf93ae816b7e1beaab514c2')
for label in ['feature', 'multiloader1192']:
    ROOTS[label] = CACHE / f'{label}-tree-006'
    METADATA[label] = CACHE / f'{label}-commit-006.json'
TINKER_REPO = 'SlimeKnights/TinkersConstruct'
TINKER_ORIGIN = WORKSPACE / 'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct'
ROOTS['tinkers'] = HERE / 'sources/SlimeKnights__TinkersConstruct-006'
METADATA['tinkers'] = ROOTS['tinkers'] / 'source.json'
TINKER_META_RAW = (TINKER_ORIGIN / 'source.json').read_bytes()
TINKER_META = json.loads(TINKER_META_RAW)
TINKER_TREE_RAW = (TINKER_ORIGIN / 'tree.json').read_bytes()
TINKER_TREE = json.loads(TINKER_TREE_RAW)
assert TINKER_META['repo'] == TINKER_REPO and TINKER_META['sha'] == PINS['tinkers']
assert TINKER_TREE['sha'] == PINS['tinkers'] and not TINKER_TREE['truncated']
TINKER_BLOBS = {x['path']: x['sha'] for x in TINKER_TREE['tree'] if x['type'] == 'blob'}
COPIED = {}


def tink(name, signatures):
    path = 'src/main/java/slimeknights/tconstruct/' + name + '.java'
    raw = (TINKER_ORIGIN / path).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == TINKER_BLOBS[path]
    dest = ROOTS['tinkers'] / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert dest.read_bytes() == raw
    else:
        dest.write_bytes(raw)
    COPIED[path] = dict(path=path, source_local=str(dest.relative_to(WORKSPACE)), source_sha256=sha(raw),
                        git_blob_sha1=TINKER_BLOBS[path], origin_local=str((TINKER_ORIGIN / path).relative_to(WORKSPACE)))
    result = []
    for sig, role in signatures:
        e = method('tinkers', path, sig, role)
        e['repo'] = TINKER_REPO
        e['url'] = f'https://github.com/{TINKER_REPO}/blob/{PINS["tinkers"]}/{path}#L{e["line"]}-L{e["end_line"]}'
        result.append(e)
    return result


def ap(label, short, signatures):
    platform, name = short.split(':', 1)
    path = f'{platform}/src/main/java/net/merchantpug/apugli/{name}.java'
    return [method(label, path, sig, role) for sig, role in signatures]


def add(key, evidence, observation, application, limits, proposal=False, duplicate_of=None):
    row = dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-006-' + key, chain_id=key, batch='006',
               status='reviewed', credit=0, proposed_credit=int(proposal), final_count_owner='Carson',
               decision='reviewed_valid_pending_carson' if proposal else 'reviewed_excluded_zero_credit',
               reviewed_at=NOW, evidence=evidence, observation=observation, application=application, limits=limits,
               duplicate_of=duplicate_of, dedup_key=evidence[0]['repo'] + ':' + key,
               counting_unit='One independent gameplay lifecycle; supporting methods and mirrored implementations count zero.',
               external_runtime_tested=False, downloaded_code_executed=False)
    ROWS.append(row)


ATTACK_SUPPORT = lambda: tink('library/tools/helper/ToolAttackUtil', [
    ('public static boolean performAttack(', 'actual hurt result gates modifier post-hit, with health snapshot and source-slot context'),
    ('public static boolean attackEntity(IToolStackView tool, Player', 'real normal tool attack dispatch')]) + tink(
    'library/modifiers/hook/interaction/EntityInteractionModifierHook', [('static boolean leftClickEntity(', 'actual held tool click reaches attack dispatch')]) + tink(
    'library/tools/item/ModifiableItem', [('public boolean onLeftClickEntity(', 'real item callback')])

add('bleeding-phase-preserving-renewal-and-late-source-read',
    tink('tools/modifiers/effect/BleedingEffect', [
        ('public void applyEffectTick(', 'actual deferred damage re-reads target mutable attacker field'),
        ('public boolean isDurationEffectTick(', 'positive duration modulo 20 is actual damage cadence')]) +
    tink('tools/modifiers/traits/melee/LaceratingModifier', [
        ('public void afterMeleeHit(', 'actual melee producer updates target attribution then grants effect'),
        ('private static void applyEffect(IToolStackView', 'captures looting value at application'),
        ('private static void applyEffect(LivingEntity', 'same-amplifier renewal preserves duration phase'),
        ('protected void registerHooks(', 'binds gameplay callbacks')]) + ATTACK_SUPPORT() +
    tink('library/tools/helper/ToolAttackUtil', [
        ('public static boolean attackEntitySecondary(', 'concrete secondary damage and knockback restoration'),
        ('public static boolean hurtNoInvulnerableTime(Entity target, @Nullable', 'actual hurt and invulnerability window restoration')]) +
    tink('common/TinkerDamageTypes', [
        ('public static DamageSource source(RegistryAccess access, ResourceKey<DamageType> type, @Nullable Entity entity)', 'single-source overload'),
        ('public static DamageSource source(RegistryAccess access, ResourceKey<DamageType> type, @Nullable Entity direct,', 'actual direct/causing damage source object')]),
    '固定匠魂提交f4e77d43f39ba1047bf93ae816b7e1beaab514c2。真实工具左击到performAttack：hurt失败先走failedMeleeHit并返回，成功路径计算health差量再调用modifier.afterMeleeHit。Lacerating在满蓄力且目标活着时把attacker写入目标lastHurtMob并授予流血。应用时把looting编码为effect amplifier；若已有相同amplifier，duration加原剩余值，等级增量为level*40，因此保留模20相位；否则额外加19。Bleeding在正duration且%20==0时再次读取目标getLastHurtMob构造伤害源，执行secondary hurt，再发送伤害粒子。',
    '独立语义是续期保留消费节拍，同时收益参数与归属使用不同快照时刻：looting在施加时捕获，攻击来源在每次后续伤害时从可变字段重读。横扫回执应清楚保留原攻击归属，不能因为在同一目标上留有某种攻击者字段，就当成该回执来源。续期不能无意重触第一次消费，也不能把成功主伤害与后续DOT结果混为同一个事实。整条只建议1条。',
    '不是普通无来源DOT模板：相关性来自实际生产与续期相位、延后归属读取的完整链。目标lastHurtMob不是不可变攻击快照，没有source/target UUID、维度或任务代次校验。Bleeding忽略secondary返回布尔，粒子不证明hurt成功；恢复无finally。主hurt成功不等于damageDealt>0，本modifier不要求差量为正。外部MobEffect调度/合并实现未读，不保证所有不同amplifier替换结果。公用hurtNoInvulnerableTime已在主账，作为支持0分，未另报。', True)

add('armor-charge-remove-before-current-slot-release',
    tink('tools/logic/InteractionHandler', [
        ('public static boolean stopArmorInteract(', 'remove pending slot record before all release hooks'),
        ('public static boolean startArmorInteract(', 'stores selected modifier ID and player entity age')]) +
    tink('tools/ToolClientEvents', [('private static void handleKeyBindings(', 'actual START client tick edge produces START/STOP packet')]) +
    tink('tools/network/TinkerControlPacket', [('public void handleThreadsafe(', 'sender-bound HEAD/LEGS dispatch to actual interaction methods')]) +
    tink('tools/modules/interaction/sling/SlingModule', [
        ('default boolean startInteract(', 'real charge start initializes drawtime'),
        ('default void stopInteract(', 'positive captured charge invokes concrete sling')]) +
    tink('tools/modifiers/effect/HelmetChargingEffect', [('public static int startUsingHelmet(', 'actual tool drawtime and charge presentation')]) +
    tink('library/modifiers/hook/interaction/GeneralInteractionModifierHook', [
        ('static int startDrawing(', 'stored drawtime on selected tool'),
        ('static int getDrawtime(', 'derive drawtime from holder/tool stat'),
        ('static float getToolCharge(', 'consume age delta using current tool drawtime'),
        ('static void finishUsing(', 'clears current tool active ID and drawtime after release')]) +
    tink('tools/modules/interaction/sling/SlingKnockbackModule', [
        ('public void sling(', 'real server-side target selection, attack and knockback'),
        ('public float beforeMeleeHit(', 'own temporary bonking context controls knockback'),
        ('public float getMeleeDamage(', 'own temporary bonking context controls damage')]) +
    tink('library/tools/capability/TinkerDataCapability', [
        ('public static TinkerDataCapability.Holder getData(', 'state is held on actual entity capability'),
        ('public void run()', 'capability invalidation preserves previous Holder for revival')]),
    'START记录在实体cap的slot→ArmorInteractData(modifier ID,start tickCount)。STOP先核当前槽仍为ARMOR，读取当前工具，再remove该slot记录，按player.tickCount-startTime求chargeTime，随后遍历当前工具所有modifier的stopInteract，最后清当前工具drawtime。真实客户端START tick边沿发包，服务端从context.sender分派头/腿槽；SlingModule将chargeTime>0转换为SlingKnockback实际服务端光线选目标、伤害和击退。',
    '这是一条真实输入开始→跨tick挂起→松键取走→玩法效果的生命周期，先remove再调用效果可避免同一开始记录在回调重入时再次取走。新的边界是记录只保留slot和modifier ID，不是原工具身份；换同槽新工具后松键可能消费旧蓄力给新工具。适用于横扫任务用来源快照而非消费时重读当前装备，并区分一次取走与严格一次效果。整条1条，HEAD/LEGS及持物镜像不拆计。',
    '状态没有短TTL、世界/维度、物品实例、请求序号；重复START可覆盖开始时刻。STOP在spectator或当前槽非ARMOR时提前返回而不remove；cap invalidation显式保留Holder，不能宣称切维度自动清掉。停止时所有当前modifier收到回调，activeModifier仅是参数而非此处统一筛选。Sling把didBonk在调用performAttack之前设true并忽略返回；IS_BONKING清除无finally，不能当成功伤害回执。Mantle IThreadsafePacket调度器未读，不声称具体线程排队相位；这里已核真实分派与跨tick状态消费。', True)

add('looting-source-slot-dynamic-scope-and-projectile-context',
    tink('library/tools/helper/ModifierLootingHandler', [
        ('private static void onLooting(', 'kill event resolves projectile capability or temporary source slot'),
        ('public static void setLootingSlot(', 'UUID-keyed temporary source-slot producer/reset'),
        ('public static EquipmentSlot getLootingSlot(', 'current slot lease consumer'),
        ('private static void onLeaveServer(', 'logout cleanup'),
        ('public static void init()', 'real HIGH-priority event listener')]) + ATTACK_SUPPORT() +
    tink('tools/TinkerTools', [('public TinkerTools()', 'actual module initializes looting listener')]) +
    tink('tools/modifiers/ModifierLootModifier', [('protected ObjectArrayList<ItemStack> doApply(', 'real loot result mutation uses projectile snapshot and source whitelist')]) +
    tink('library/modifiers/hook/combat/LootingModifierHook', [('static int getLooting(', 'actual tool modifier benefit computation')]) +
    tink('library/modifiers/hook/combat/ArmorLootingModifierHook', [('static int getLooting(', 'current armor benefit computation')]),
    'performAttack在调用目标hurt前按attacker UUID写入source slot，hurt返回后重置MAINHAND（删除表项）。真实LootingLevelEvent在HIGH监听中：流血按effect amplifier；其他Living来源，若direct是Projectile则读弹体modifier/persistentData构造DummyTool，否则通过临时slot查当前手持物。Global ModifierLootModifier对Projectile直接走弹体PROCESS_LOOT后return，避免再把当前持物计入；其他伤害必须在LOOT_MODIFIER_WHITELIST才按kill来源/slot取工具。登出移除该玩家UUID槽上下文。',
    '独立于横扫伤害循环或公用hurt助手，这条研究的是伤害调用期间建立的来源槽上下文如何被真实掉落事件消费。弹体以自身能力快照替代发射者当前持物；同步近战则依赖临时动态作用域。可借鉴回执携带足够来源信息，不能将一个UUID→当前槽全局表当作跨tick攻击事实。整个收益来源选择/临时范围/清理1条，多个收益钩子不拆计。',
    '本链不是短TTL队列，只能作为来源/持有者生命周期参考，最终是否足够独立相关由Carson判定。临时slot没有finally、前值栈、攻击ID或维度；同UUID嵌套攻击重置MAINHAND可能丢外层slot，异常可泄漏到后续事件。近战读取当前槽物品，盔甲也是消费时快照；不能保证延后异步事件仍有正确来源。Projectile capability生产已在现有投掷链研究，本批只核真实消费，不能额外按存储包装计数。', True)

add('projectile-reflection-window-and-impact-result-consumption',
    tink('tools/logic/ModifierEvents', [('static void projectileImpact(', 'full real callback: owner rewrite, reflect window, impact override, pierce and hurt outcome')]) +
    tink('tools/logic/InteractionHandler', [('public static boolean canBlock(', 'actual source-position and view-angle validation')]) +
    tink('library/modifiers/entity/ReusableProjectile', [
        ('static void discard(', 'terminal disposition obeys reusable policy'),
        ('static boolean isSingleUse(', 'tag/interface decides discard ownership')]) +
    tink('shared/TinkerEffects', [('public static boolean needsEnderferenceOverride(@Nullable LivingEntity', 'concrete target type and current status guard')]) +
    tink('library/modifiers/hook/interaction/GeneralInteractionModifierHook', [('static ModifierEntry getActiveModifier(', 'actual selected active modifier ID read')]),
    '完整读取projectileImpact回调（含注解409—574行，共166行）。反射只在server、弹体非黑名单、目标非owner且正在用匠魂盾时尝试，必须有active modifier、BLOCK动作、已用时>=5且<reflectingTime，并符合当前来源角度。成功分支将owner换为挡者（指定类型保留原owner），箭保存/恢复pickup，置leftOwner并重射/修正火球加速，设SKIP_ENTITY、扣盾耐久。随后同一回调还可能进入enderference箭替代处理：先在pierce ID集合占目标名额，构造MELEE_ARROW来源，hurt成功才后续效果/击杀集合/成就与终止；失败恢复火时、反弹，极低速时按pickup退款并按reusable策略终止。',
    '新的独立状态语义是反射改变仍在飞行弹体的来源身份，同时以短防御窗口和impact结果阻止本次原处理；不能继续沿用发射时持有者当作未来全部伤害来源。整份完整回调只建议1条，不把反射、箭替代、成功/失败、不同实体模板各拆加分。对横扫借鉴在消费前验证来源身份与任务阶段，并明确碰撞资格、已占pierce名额、hurt成功三种不同状态。',
    '不是4991→4992队列修复范例，窗口按当前use duration算；未核原版Arrow事件调用和外部后续优先级监听，不宣称SKIP_ENTITY等于绝对无伤害或全局取消。反射分支后没有return，同回调可继续其他逻辑。pierce目标ID在hurt前加入，失败也占名额；反射声音/扣费不证明伤害成功。与已接受ThrownShuriken退款有共同支持原则，但本候选核心是活动防御时限、弹体owner重写与impact拦截，非退款模板另报。', True)

add('slime-bounce-one-tick-motion-handoff-and-grace-expiry',
    tink('library/utils/SlimeBounceHandler', [
        ('private static void onLivingTick(', 'actual deferred bounce application and two independent grace counters'),
        ('public static void addBounceHandler(LivingEntity entity, @Nullable', 'actual producer stores velocity and entity age plus one'),
        ('public static void addBounceHandler(LivingEntity entity)', 'player path only preserves momentum'),
        ('public BounceInfo(', 'initial scheduled bounce and horizontal motion snapshot'),
        ('private static void serverStopping(', 'terminal map cleanup'),
        ('public static void init()', 'real tick and server-stop listeners')]) +
    tink('tools/logic/ModifierEvents', [('static void bounceOnFall(', 'real fall event: nonplayer defers restored velocity to next tick')]) +
    tink('shared/TinkerCommons', [('void commonSetupEvent(', 'actual lifecycle registration caller')]),
    '真实bouncy落地玩法：ModifierEvents.bounceOnFall先处理落距、潜行和属性；ServerPlayer直接重建反弹垂速并仅登记水平动量，非玩家则登记反弹Vec3。SlimeBounceHandler以实体对象身份为键，保存bounceTick=tickCount+1；后续LivingTick仅在age恰等预约时恢复Vec3、清bounce并将tick归0，以绕过落地逻辑随后清Y速度。重登已有项可覆盖非null待反弹值/预约。之后维持水平动量，静止后>stopMagTick(设now+5)才归零；落地等非空中状态持续>另一个now+5才删整项，滑翔/旁观立即删，server stop清表。',
    '这是直接相关的一tick阶段交接：产生于落地事件的事实不能立即应用而需越过原版速度重置点，消费载荷保留原Vec3。和投射物引信/重力预约、法术通用延时器不同，完整包含阶段补偿、一次性待应用向量、后续动量保留与两个宽限截止。可借鉴区分“需要等下阶段执行”和“证据已经过期”，时钟绑定实际被调实体；整条1条，不把相邻两个五tick计时拆计。',
    '这里仍用==预约age，不是建议照搬到横扫；若消费观察错过age则此路径没有>=补消费/过期拒绝。正常实体是否会跳过该age未运行验证，不能断言实测丢任务。静态IdentityHashMap没有显式死亡/卸载/换维度删项，也无维度ID；不再tick的实体可能留到server stop。bounce置null在setDeltaMovement之后，不能称回调前原子取走。FakePlayer被排除，玩家/非玩家同链不同阶段不重复计数。', True)

add('individual-empty-stack-holder-binding-version-dedup',
    ap('feature', 'Common:util/IndividualisedEmptyStackUtil', [
        ('public static ItemStack getEntityLinkedEmptyStack(', 'real per-entity sentinel creation'),
        ('public static void addEntityToStack(', 'real tick binding and conditional removal')]) +
    ap('feature', 'Fabric:mixin/fabric/common/LivingEntityMixin', [('private void apugli$setItemStackEntities(', 'actual tick caller')]) +
    ap('feature', 'Fabric:platform/FabricPlatformHelper', [
        ('public Entity getEntityFromItemStack(', 'platform read'), ('public void setEntityToItemStack(', 'platform write')]) +
    ap('feature', 'Fabric:mixin/fabric/common/ItemStackMixin', [
        ('public void apugli$setEntity(', 'actual object field assignment'), ('public Entity apugli$getEntity()', 'actual object field read')]) +
    ap('feature', 'Common:mixin/xplatform/common/ItemStackMixin', [('private void apugli$copyNewParams(', 'copy inherits old holder')]) +
    ap('feature', 'Common:power/factory/ModifyEnchantmentLevelPowerFactory', [
        ('default ListTag getEnchantments(', 'concrete specialized cache read'),
        ('default ListTag generateEnchantments(', 'actual holder-dependent gameplay rebuild'),
        ('default boolean shouldReapplyEnchantments(', 'already reviewed dirty-consumption family')]) +
    ap('feature', 'Fabric:mixin/fabric/common/EnchantmentHelperMixin', [
        ('private static ListTag apugli$getEnchantmentsGetLevel(', 'actual gameplay consumer'),
        ('private static boolean apugli$getLevelIsEmpty(', 'individual empty item allowed to carry owner effects')]) +
    ap('multiloader1192', 'Common:util/IndividualisedEmptyStackUtil', [
        ('public static ItemStack getEntityLinkedEmptyStack(', 'older same template version'),
        ('public static void addEntityToStack(', 'older same template version')]),
    'feature/1.20固定Minecraft1.20.1/Apugli2.9.0-beta.3：tick遇全局EMPTY且没有holder时换成本实体独立empty对象，同一实体多个空槽共用该对象；BetterCombat副手直接读inventory.offhand。普通非空物品只在holder=null时绑定，copy继承holder。实体removed且map存在时才删其empty桶。真实附魔读取允许这些空stack参与持有者能力；结果仍按旧附魔cache族处理。multiloader/1.19.2的Minecraft1.19.2/Apugli2.6.7同实现，仅null构造强转类型不同。',
    '新观察是全局EMPTY不能承载每实体归属；每实体sentinel又不等于每槽/每次操作身份。转手非null持有者并不会在此重绑，复制也保留旧归属。作为已有来源绑定/附魔整链补充，不因独立empty util或版本新增信用。',
    '重复batch003附魔生命周期，0增量。清理依赖removed实体再次进入tick入口，不能声称卸载/换维度都回收；只有身份绑定，不能证明伤害成功或短TTL。没有研究/运行BetterCombat仓库，本批只读Apugli的明确兼容分支。', False,
    'batch003:enchantment-gameplay-invalidation-and-deferred-remove; batch004 legacy holder comparison')

add('area-of-effect-is-synchronous-not-receipt-lifecycle',
    ap('multiloader1192', 'Common:action/factory/block/AreaOfEffectAction', [
        ('public void execute(', 'complete actual synchronous shape loop'),
        ('public SerializableData getSerializableData()', 'concrete configured predicate/action/radius/shape')]),
    '完整execute按Shape位置同步遍历，逐块判断condition再直接executeBlock；该类没有待执行状态、时间戳、去重表或取消句柄。',
    '目录里出现area-of-effect不能当横扫延后回执实现；范围遍历只证明空间选取，不能证明成功事实与跨tick消费。',
    '外部Shape/通用executeBlock内部未审阅，不推定它们有隐含队列；本类零信用。', False)

add('offhand-parry-delegates-unreviewed-cooldown-core',
    tink('tools/modifiers/ability/tool/OffhandAttackModifier', [
        ('protected boolean canAttack(', 'actual readiness delegates Mantle tracker'),
        ('private static void applyCooldown(', 'actual writer delegates Mantle tracker'),
        ('public InteractionResult beforeEntityUse(', 'real attempt invokes performAttack but ignores result'),
        ('public InteractionResult onToolUse(', 'miss still applies cooldown')]) +
    tink('tools/modifiers/ability/tool/ParryingModifier', [
        ('public InteractionResult beforeEntityUse(', 'consumed interaction starts blocking'),
        ('public InteractionResult onToolUse(', 'same start-on-consume variant'),
        ('public void onFinishUsing(', 'vanilla item cooldown at use finish')]),
    '副手ready与apply核心委托外部Mantle OffhandCooldownTracker；本仓实际攻击入口忽略performAttack返回，无目标/失败也会扣冷却并挥副手。Parrying在交互consumed后开始BLOCK，finish添加vanilla item cooldown。',
    '保留为“交互已消费不等于hurt成功”的补证，但外部冷却核心未读，不能仅借方法名把它包装成已完成短TTL链。',
    '不算新有效实现；同类尝试/反馈区别已存在主账与主协调建议。本批没有复制外部Mantle实现，也未把Parrying子类另加一条。', False)


def main():
    selected_metadata = dict(TINKER_META)
    selected_metadata.update(files_saved=len(COPIED), original_cache_files_saved=TINKER_META.get('files_saved'),
        scope='Selected previously cached Java source evidence only; not a complete upstream checkout.',
        cache_scope='partial selected-files copy inside this helper',
        original_metadata_local=str((TINKER_ORIGIN / 'source.json').relative_to(WORKSPACE)),
        original_metadata_sha256=sha(TINKER_META_RAW),
        original_tree_local=str((TINKER_ORIGIN / 'tree.json').relative_to(WORKSPACE)),
        original_tree_sha256=sha(TINKER_TREE_RAW))
    METADATA['tinkers'].write_text(json.dumps(selected_metadata,ensure_ascii=False,indent=2)+'\n')
    index = {}
    for b in json.loads((DOCS / 'branch-source-index-006.json').read_text()):
        index.update({f['source_local']: f for f in b['files']})
    index.update({r['source_local']: r for r in COPIED.values()})
    unique = set()
    required = {'repo','revision','path','source_local','source_sha256','line','end_line','excerpt','observation','application','limits','url'}
    for row in ROWS:
        assert required <= row.keys() and row['credit'] == 0
        for e in row['evidence']:
            raw = (WORKSPACE / e['source_local']).read_bytes()
            assert sha(raw) == e['source_sha256'] == index[e['source_local']]['source_sha256']
            assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == index[e['source_local']]['git_blob_sha1']
            assert e['excerpt'] == '\n'.join(raw.decode().splitlines()[e['line'] - 1:e['end_line']])
            unique.add((e['repo'],e['revision'],e['path'],e['line'],e['end_line']))
    main_path = DOCS.parents[1] / 'accepted.jsonl'
    raw = main_path.read_bytes()
    accepted = [json.loads(s) for s in raw.decode().splitlines() if s]
    reviewed_raw = (DOCS.parents[1] / 'reviewed.jsonl').read_bytes()
    reviewed = [json.loads(s) for s in reviewed_raw.decode().splitlines() if s]
    exact = [r['candidate_id'] for r in ROWS if r['proposed_credit'] and any(
        (r['repo'],r['revision'],r['path'],r['line']) == (a.get('repo'),a.get('revision'),a.get('path'),a.get('line')) for a in accepted)]
    assert not exact
    prior = []
    for name in ['reviewed.jsonl','reviewed-002.jsonl','reviewed-003.jsonl','reviewed-004.jsonl','reviewed-005.jsonl']:
        prior.extend(json.loads(s) for s in (DOCS / name).read_text().splitlines() if s)
    assert not ({r['dedup_key'] for r in ROWS} & {r.get('dedup_key') for r in prior})
    proposals = [r for r in ROWS if r['proposed_credit']]
    comparisons = {
        'bleeding-phase-preserving-renewal-and-late-source-read': (
            ['main: ToolAttackUtil.hurtNoInvulnerableTime', 'reviewed excluded: Mickelus/tetra BleedingPotionEffect'],
            'Main helper is reused support only. New unit owns duration renewal phase and split snapshot times for looting/source; ordinary DOT visual template excluded.'),
        'armor-charge-remove-before-current-slot-release': (
            ['main: PlayerWeaponAbilityChannelManager', 'batch005: HoverPower heartbeat'],
            'Current unit stores slot/modifier/start age and removes it on release before dispatching current equipment hooks; distinct from continuously ticked ability channel or per-tick heartbeat.'),
        'looting-source-slot-dynamic-scope-and-projectile-context': (
            ['main: ToolAttackUtil.hurtNoInvulnerableTime', 'main: SweepWeaponAttack.afterMeleeHit', 'batch006: bleeding renewal'],
            'Source-slot dynamic scope belongs to attacker UUID and real loot event, not victim DOT duration or sweep target set. Bleeding case inside consumer is support only; never another credit.'),
        'projectile-reflection-window-and-impact-result-consumption': (
            ['main: ThrownShuriken.onHitEntity', 'main: Apugli ProjectileEntityMixin', 'coordinator-receipt twelve suggestions'],
            'Core is shield window plus mutation of existing projectile owner/pickup/flight and impact result. Refund, pierce branches and secondary helpers retained inside this single unit; no renamed failed-hit template credit.'),
        'slime-bounce-one-tick-motion-handoff-and-grace-expiry': (
            ['main: ProjectileGravityModule', 'main: DelayedSpellHandler', 'main: AdditiveMotionHandler'],
            'Concrete fall-event phase compensation owns one pending velocity vector then continuing momentum/grace state per entity identity; not generic task scheduler or weapon gravity setting.'),
    }
    for r in proposals:
        nearest, distinction = comparisons[r['chain_id']]
        r['semantic_dedup'] = dict(nearest_existing_families=nearest, independent_state_and_consumer=distinction,
                                  supporting_methods_increment=0, mirrored_or_version_increment=0,
                                  exact_primary_in_main_reviewed=any(
                                      (r['repo'],r['revision'],r['path'],r['line']) ==
                                      (a.get('repo'),a.get('revision'),a.get('path'),a.get('line')) for a in reviewed))
        assert not r['semantic_dedup']['exact_primary_in_main_reviewed']
    dump('batch-006.json', dict(schema_version=1, reviewed_at=NOW, final_count_owner='Carson', credit_applied=0,
         scope_authorization='latest human: if original related methods insufficient, use already pinned other sources; only own helper directories written',
         proposed_valid=len(proposals), entries=proposals))
    dump('excluded-006.json', dict(schema_version=1, credit=0, entries=[r for r in ROWS if not r['proposed_credit']]))
    (DOCS / 'reviewed-006.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ROWS))
    dump('tinkers-source-index-006.json', dict(repo=TINKER_REPO,revision=PINS['tinkers'],
        official_source_provenance='previously pinned project cache source.json; no fresh repository/default-branch claim',
        origin_metadata=str((TINKER_ORIGIN/'source.json').relative_to(WORKSPACE)), origin_metadata_sha256=sha(TINKER_META_RAW),
        origin_tree=str((TINKER_ORIGIN/'tree.json').relative_to(WORKSPACE)), origin_tree_sha256=sha(TINKER_TREE_RAW),
        selected_files_git_blob_verified=True, copied_text_only=True, downloaded_code_executed=False, files=list(COPIED.values())))
    dump('validation-006.json', dict(schema_version=1, artifact='source evidence integrity, not compilation or runtime acceptance',
        reviewed_groups=len(ROWS), proposed_valid=len(proposals), zero_increment_groups=len(ROWS)-len(proposals),
        distinct_complete_method_ranges=len(unique), evidence_files=len({e['source_local'] for r in ROWS for e in r['evidence']}),
        source_sha256_git_blob_and_full_ranges_verified=True, main_accepted_read_only_rows=len(accepted),
        main_accepted_read_only_sha256=sha(raw), main_reviewed_read_only_rows=len(reviewed), main_reviewed_read_only_sha256=sha(reviewed_raw),
        exact_main_primary_duplicates=exact, semantic_dedup='five distinct gameplay containers; common attack/capability/helper methods supporting only; original Apugli versions excluded',
        credit_applied=0, compilation_performed=False, tests_performed=False, game_started=False,
        screen_operated=False, real_tcp_testing_performed=False, upstream_code_executed=False,
        research_http_requests=4, http_failures=0, http_retry_count=0))
    print(json.dumps(dict(proposals=len(proposals),zero_increment=len(ROWS)-len(proposals),complete_methods=len(unique),credit=0)))


if __name__ == '__main__':
    main()
