"""Offline evidence packaging; never imports or executes downloaded repository code."""
import datetime
import hashlib
import json
import pathlib
import re

WORKSPACE = pathlib.Path(__file__).resolve().parents[5]
TOOLS = pathlib.Path(__file__).resolve().parent
DOCS = WORKSPACE / 'docs/cod4/audit-20261022/sweep-receipt-research/helpers/apugli-rpginventory'
ROOT = TOOLS / 'sources/MerchantPug__Apugli/tree'
PIN = 'fcbadb4b288996f1767ce3d954522270e88681aa'
REPO = 'ChrysanthCow/apugli'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local(p):
    return str(p.relative_to(WORKSPACE))


def path(short):
    platform, name = short.split(':', 1)
    return f'{platform}/src/main/java/net/merchantpug/apugli/{name}.java'


def method(short, signature, role):
    p = path(short)
    data = (ROOT / p).read_bytes()
    lines = data.decode().splitlines()
    starts = [i for i, line in enumerate(lines) if signature in line]
    assert len(starts) == 1, (short, signature, starts)
    start = starts[0]
    # Lex strings/comments before balancing Java bodies. Annotations retained above signature.
    body = '\n'.join(lines[start:])
    mask = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/',
                  lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), body)
    opening = mask.index('{')
    balance = 0
    endpos = None
    for i in range(opening, len(mask)):
        balance += (mask[i] == '{') - (mask[i] == '}')
        if balance == 0:
            endpos = i
            break
    assert endpos is not None
    end = start + mask[:endpos + 1].count('\n')
    while start > 0 and lines[start - 1].lstrip().startswith('@'):
        start -= 1
    excerpt = '\n'.join(lines[start:end + 1])
    return dict(repo=REPO, revision=PIN, path=p, source_local=local(ROOT / p),
                source_sha256=sha(data), line=start + 1, end_line=end + 1,
                excerpt=excerpt, snippet_sha256=sha(excerpt.encode()), role=role,
                url=f'https://github.com/{REPO}/blob/{PIN}/{p}#L{start + 1}-L{end + 1}')


ROWS = []


def add(key, primary, support, observation, application, limits, tags, valid=True, scope=None):
    ev = [method(*primary)] + [method(*x) for x in support]
    main = dict(ev[0])
    main.update(candidate_id='apugli-rpginventory-' + key, chain_id=key,
                requested_repo='MerchantPug/Apugli', canonical_repo=REPO,
                status='reviewed', decision='reviewed_valid_pending_carson' if valid else 'auxiliary_zero_credit',
                proposed_credit=int(valid), credit=0, final_count_owner='Carson',
                reviewed_at=NOW, external_runtime_tested=False,
                observation=observation, application=application, limits=limits,
                discovery_tags=tags, scope_basis=scope,
                dedup_key=f'{REPO}:{key}',
                counting_unit='One entire gameplay lifecycle; all evidence below shares this single counting unit.',
                evidence=ev)
    ROWS.append(main)


add('hit-history-expiry',
    ('fabric:component/HitsOnTargetComponentImpl', 'public void serverTick()', 'age advancement and removal'),
    [('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$runDamageFunctions(', 'hurt success producer'),
     ('fabric:component/HitsOnTargetComponentImpl', 'public void setHits(', 'reset age on write'),
     ('fabric:component/ApugliEntityComponents', 'public void registerEntityComponentFactories(', 'living entity registration'),
     ('common:condition/factory/bientity/HitsOnTargetCondition', 'public boolean check(', 'gameplay condition consumer'),
     ('fabric:platform/FabricPlatformHelper', 'public Tuple<Integer, Integer> getHitsOnTarget(', 'actor-to-target lookup'),
     ('fabric:network/s2c/SyncHitsOnTargetLessenedPacket', 'public void handle()', 'deferred client delta application'),
     ('neoforge:capability/entity/HitsOnTargetCapability', 'public void serverTick()', 'same lifecycle on other loader; zero extra credit')],
    'Fabric在hurt RETURN且返回true后，在受伤者组件内以source.getEntity().getId()累计命中并将年龄清零；ServerTickingComponent驱动serverTick逐次加龄，在当前provider.level按ID找不到来源、来源已死或currentTime>resetTimerTicks时移除；条件随后读取相同actor/target命中表。默认resetTimerTicks=100见fabric/util/ApugliConfig.java。NeoForge相同算法不另计。',
    '回执产生刻与消费刻分离：在成功hurt之后记录结果，消费时检查有限年龄窗口及来源仍存在；以目标作用域隔离多个受害者，避免要求r.tick==now。过期比较的包含边界必须明确定义。',
    '这是可多次读取的连击历史，不是一次消费回执。ID不是UUID；查找当前维度不等于验证原始维度。currentTime>100允许100并先加至101，下次才清理。previousHits=hits是别名而非快照；S2C比较currentPair.getB().equals(currentPair.getB())恒真，年龄变化被忽略；hurt生产包使用source实体ID而组件属受伤者，不能直接套用。没有证明真实血量下降或directActor约束。',
    ['expiry_window', 'damage_success', 'identity_scope', 'deferred_gameplay_sync'],
    scope='真实hurt命中状态跨tick保留、过期清理及条件消费；整链计一。')

add('custom-projectile-entire-lifecycle',
    ('common:power/factory/CustomProjectilePowerFactory', 'default void tick(', 'delayed burst scheduler'),
    [('common:power/factory/CustomProjectilePowerFactory', 'default void reset(', 'clear burst state'),
     ('common:power/factory/CustomProjectilePowerFactory', 'default void fireProjectile(', 'server projectile creation and owner snapshot'),
     ('fabric:power/CustomProjectilePower', 'public void onUse()', 'activate and stamp cooldown'),
     ('fabric:power/CustomProjectilePower', 'public void tick()', 'power tick consumer'),
     ('fabric:power/CustomProjectilePower', 'public Tag toTag()', 'persist pending burst'),
     ('fabric:power/CustomProjectilePower', 'public void fromTag(', 'restore pending burst'),
     ('common:entity/CustomProjectile', 'public Entity getOwner()', 'current ServerLevel UUID resolution'),
     ('common:entity/CustomProjectile', 'private boolean isOwnerRemovedOrDiscarded()', 'cached owner lifecycle guard'),
     ('common:entity/CustomProjectile', 'protected boolean canHitEntity(', 'target and owner conditions'),
     ('common:entity/CustomProjectile', 'public void onHitEntity(', 'impact actions then discard'),
     ('common:entity/CustomProjectile', 'public void onHitBlock(', 'block/miss branching then discard'),
     ('common:entity/CustomProjectile', 'public void tick()', 'owner death removal')],
    'onUse设置isFiringProjectiles并use；后续power tick读取lastUseTime，以start_delay和interval的相对gameTime模值推进，count限制发射数量，reset同时清三项状态。fireProjectile在发射前动作后复核可选active条件，服务端创建带owner的实体。弹射物优先缓存owner，否则在自身ServerLevel以ownerUUID解析；实体命中或方块命中动作后discard，tick遇owner死亡/丢弃也discard。连发状态可NBT恢复。整个发射到销毁链只计一次。',
    '借鉴显式pending/finished/consumed状态和有限工作量；将来源绑定与延迟任务一起保存，在消费时复核来源/目标。横扫可以用短年龄窗口承认4991产生而4992消费，同时保证成功回执被取走后不重放。',
    '模运算是周期命中而非now>=due；不保证漏过tick后立即追赶，start_delay模值还可在年龄0命中。不是短TTL伤害回执。缓存owner仅拒KILLED/DISCARDED，换维度/卸载并未完整失效；UUID回查仅限缓存不可用时。动作先于discard，异常/重入无事务保护；NBT恢复无回执年龄上限。',
    ['deferred_combat', 'state_machine', 'source_uuid', 'single_lifecycle'],
    scope='实际自定义战斗弹射物延迟连发与来源/目标/终止生命周期；不拆分UUID、命中、NBT为额外实现。')

add('projectile-hit-settlement',
    ('fabric:mixin/fabric/common/ProjectileEntityMixin', 'private void apugli$handleProjectileCollision(', 'per-power hit accumulator'),
    [('fabric:mixin/fabric/common/ProjectileEntityMixin', 'private void apugli$handleProjectileCooldown(', 'block impact settlement and clear'),
     ('fabric:mixin/fabric/common/EntityMixin', 'private void apugli$startCooldownIfDiscarded(', 'discard fallback settlement'),
     ('common:power/factory/ProjectileHitActionPowerFactory', 'default void execute(', 'stop_after gate and cooldown use'),
     ('common:power/factory/ActionOnProjectileHitPowerFactory', 'default void execute(', 'delegating wrapper; no extra credit')],
    '实体碰撞前按power ResourceLocation在单个Projectile实例的map累计命中，再调用条件/stop_after动作；达到阈值时立即use。未达阈值的已命中power可等方块碰撞或discard回调再use；方块分支结算后clear。discard fallback只查询本弹射物记录过的power并要求canUse。',
    '借鉴把实际命中证据保留到后续生命周期结算，按任务实例+power键隔离；完成主消费后清理，终止路径也处理未结算状态。回执状态与冷却状态应独立定义。',
    '碰撞记录在onHitEntity前写入，不能作为真实hurt成功证明；map计数先于条件检查。去重的是power而不是target UUID，重复命中可递增。discard分支不clear，canUse只是冷却门，不能证明严格一次消费或重入安全；未看到短TTL和维度快照。',
    ['deferred_combat_settlement', 'lifecycle_cleanup', 'per_projectile_state'],
    scope='战斗命中累积到后续方块碰撞/销毁才消费冷却；两个终止路径同链合一。')

add('cloud-effect-lease',
    ('common:entity/CustomAreaEffectCloud', 'public void tick()', 'wait/duration/reapplication lease consumer'),
    [('common:entity/CustomAreaEffectCloud', 'public void remove(', 'revoke grants on all removal reasons'),
     ('common:entity/CustomAreaEffectCloud', 'private boolean isOwnerRemovedOrDiscarded()', 'source lifetime gate'),
     ('common:action/factory/CustomEffectCloudBaseAction', 'public CustomAreaEffectCloud createCloud(', 'owner and wait/duration parameters'),
     ('common:action/factory/entity/SpawnCustomEffectCloudAction', 'public void execute(', 'spawn actual gameplay cloud'),
     ('common:action/factory/bientity/SpawnCustomEffectCloudAction', 'public void execute(', 'same cloud alternate origin wrapper; no extra credit')],
    '云由动作创建，显式带owner、wait_time、duration、reapplication_delay及power来源ID。服务端tick先判owner终止和tickCount>=wait+duration，等待期结束后每5tick扫描当前level实体；符合条件和水平半径者写victim->tickCount+delay并按来源grantPower。已到期且离开扫描AABB者revoke并移除；remove对剩余victims统一撤权。',
    '借鉴相对到期时刻与>=比较允许较晚扫描，并在任务正常到期、来源终止和实体删除路径都释放附带状态。回执应拥有明确短TTL和终止清理，而非同刻相等。',
    'reapplication_delay只影响离开AABB后的撤权，没有在命中循环跳过已登记victim；动作可每5tick重复。留在AABB但离开圆半径/条件失效者仍可能保留power。来源ID为配置ResourceLocation而非云实例UUID，多个同ID云可能干扰撤权。默认duration=600非短TTL；目标表无NBT持久化，不可声称卸载恢复完整。',
    ['deadline_comparison', 'gameplay_lease', 'source_cleanup'],
    scope='真实区域power授权/撤销的延迟等待与到期生命周期；不拆分扫描、撤权或两个spawn包装。')

add('projectile-periodic-actions',
    ('common:power/ProjectileActionOverTimePower', 'public void projectileTick(', 'periodic action and removed-target cleanup'),
    [('common:power/ProjectileActionOverTimePower', 'public boolean doesApply(', 'owner/projectile condition'),
     ('common:mixin/xplatform/common/ProjectileEntityMixin', 'private void apugli$handlePowerTick(', 'actual projectile tick invocation')],
    'Projectile.tick注入先解析LivingEntity owner，再取其PROJECTILE_ACTION_OVER_TIME powers。首次以projectile.tickCount%interval保存相位，随后用owner entity.tickCount%interval比对；在相位上执行rising、周期动作或falling，并在本次回调末尾若projectile.isRemoved清理初相表。',
    '借鉴把延后动作挂到真实任务实体生命周期，并明确保存调度相位、消费条件及结束时清理。横扫应使用单一时间域计算回执年龄，避免混用实体年龄和world时间。',
    '生产相位来自projectile年龄、消费来自owner年龄，可能不同步；interval未见正值约束。wasActive为整个power共享，而initialTicks按Projectile保存，多弹射物可能互扰。已移除实体若不再被tick则末尾清理未必触发；非一次消费，未验证UUID/维度或短TTL。',
    ['periodic_gameplay_schedule', 'target_lifecycle'],
    scope='真实Projectile.tick驱动的power动作调度，与自定义连发和命中冷却分别拥有独立状态。')

add('client-periodic-actions',
    ('common:power/ClientActionOverTime', 'public void clientTick()', 'client periodic edge actions'),
    [('fabric:mixin/fabric/client/ClientLevelMixin', 'private void apugli$tickClientActions(', 'after entity tick invocation')],
    'ClientLevel.tickNonPassenger在Entity.tick之后对LivingEntity调用CLIENT_ACTION_OVER_TIME.clientTick。首次只记entity.tickCount%interval，后续匹配相位才依据isActive执行rising/entity/falling，wasActive抑制同一激活段重复rising。',
    '借鉴显式事件阶段和初次登记/后续消费的区分；只允许阶段边沿动作一次，而持续动作按周期运行。方天回执应明确END消费与来源事件阶段的关系。',
    '客户端可配置power动作调度，不证明服务端伤害成功；rising/falling只采样周期点，中间变化可能漏掉。interval无正值检查，无TTL、持久化或目标UUID验证。与projectile周期类结构相似但此处作用对象/时间域/入口/存储不同；若主研究采用更粗的结构去重，可与projectile-periodic-actions合并。',
    ['client_gameplay_schedule', 'edge_once'],
    scope='真实客户端power周期调度；与弹射物版本区别已说明，交Carson复核结构去重。')

add('block-scheduled-tick-action',
    ('common:action/factory/block/ScheduleTickAction', 'public void execute(', 'world block tick scheduling'),
    [('common:action/factory/block/ScheduleTickAction', 'public SerializableData getSerializableData()', 'delay range'),
     ('common:registry/action/ApugliBlockActions', 'public static void registerAll()', 'gameplay action registration'),
     ('common:registry/action/ApugliBlockActions', 'private static void register(', 'loader action registration bridge')],
    '已注册的schedule_tick方块动作读取当前Level、BlockPos与该位置当前Block，以该世界随机源从min/max取整数延迟，再交Level.scheduleTick。动作实现与注册链同看，不把注册或不同配置延迟另计。',
    '借鉴将延迟工作交给其所属世界的调度入口，捕获方块类型和位置而非只存全局裸坐标；消费不要求仍处于动作产生刻。',
    '委托的Minecraft调度器实现不在这两个授权仓库内，未研究其去重/方块更换校验/异常行为；本条只证明玩法调度调用。无显式server侧、min/max合法性、来源UUID或一次伤害回执；不能推导短TTL数值。',
    ['world_scoped_schedule'],
    scope='具体方块玩法调度动作，不是纯网络库；只计执行链一次。')

add('delayed-scale-power-lifecycle',
    ('common:integration/pehkui/DelayedApoliScaleModifier', 'public void tick(', 'bounded multi-tick progression'),
    [('common:integration/pehkui/DelayedApoliScaleModifier', 'protected void reset()', 'clear progression/cache state'),
     ('common:integration/pehkui/DelayedApoliScaleModifier', 'public void setTicks(', 'clamp age/progress'),
     ('common:integration/pehkui/DelayedApoliScaleModifier', 'public float modifyScale(', 'consume progress and target snapshots'),
     ('common:integration/pehkui/DelayedApoliScaleModifier', 'private float calculateScale(', 'zero-delay-safe interpolation'),
     ('common:integration/pehkui/DelayedApoliScaleModifier', 'public CompoundTag serialize(', 'persist progression'),
     ('common:integration/pehkui/DelayedApoliScaleModifier', 'public void deserialize(', 'restore progression'),
     ('common:integration/pehkui/PehkuiUtil', 'public static <P> Object createApoliScaleModifier(', 'positive-delay concrete gameplay modifier selection'),
     ('common:integration/pehkui/PehkuiUtil', 'public static void tickScalePowers(', 'UUID-keyed tick driver'),
     ('common:integration/pehkui/PehkuiUtil', 'private static void createModifiersInOrder(', 'UUID registry and empty bucket removal'),
     ('common:integration/pehkui/PehkuiUtil', 'public static <P> void onRemovedScalePower(', 'revoke installed modifiers'),
     ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$tickModifyScale(', 'living tick integration'),
     ('fabric:power/integration/pehkui/ModifyScalePower', 'public void onAdded()', 'power added hook'),
     ('fabric:power/integration/pehkui/ModifyScalePower', 'public void onRemoved()', 'power removed hook'),
     ('common:integration/pehkui/ApoliScaleModifier', 'protected void updateIfShould(', 'consume update flags')],
    '实际modify_scale power在delay>0时创建DelayedApoliScaleModifier，按实体UUID加入有序注册表，LivingEntity tick由PehkuiUtil驱动；tick将ticks夹在0..maxTicks，目标改变时更新前后快照与总时长，后续每tick推进并sync。updateIfShould执行更新后清除dirty flags，power移除时从UUID桶与ScaleData撤下，空桶删除。',
    '借鉴有界延后任务与状态快照、一次消费dirty标志、按持有者UUID隔离及明确撤销入口；伤害回执的年龄窗口应独立于表现插值进度。',
    'Pehkui体型玩法渐变而非战斗回执队列，相关性为任务生命周期；没有短TTL或维度键。maxTicks动态变化可能延长寿命；deserialize的Ticks写字符串却读int，内层读取listTag/entryTag而非valuesTag/innerTag，恢复可靠性不足；不同对象同UUID的卸载/重登清理未证明。若主研究只收战斗/队列而不收延后power任务，应降为辅助0分。',
    ['bounded_gameplay_task', 'owner_uuid', 'flag_consumption', 'lifecycle_cleanup'],
    scope='Minecraft实际modify_scale延后power任务，非通用缓存；相关性边界明示，交Carson最终裁定。')

add('key-input-deferred-lifecycle',
    ('fabric:network/c2s/UpdateKeysPressedPacket', 'public void handle(', 'server-thread consumption of gameplay key changes'),
    [('fabric:client/ApugliClientFabric', 'public static void handleActiveKeys(', 'physical key producer at START_CLIENT_TICK'),
     ('fabric:component/KeyPressComponentImpl', 'public void setPreviouslyUsedKeys()', 'copy continuous-key snapshot'),
     ('fabric:component/KeyPressComponentImpl', 'public void tick()', 'clear state on power-count change'),
     ('fabric:component/KeyPressComponentImpl', 'public void addKey(', 'set insertion'),
     ('fabric:component/KeyPressComponentImpl', 'public void removeKey(', 'set removal'),
     ('common:condition/factory/entity/KeyPressedCondition', 'public boolean check(', 'actual player power condition consumer'),
     ('fabric:platform/FabricPlatformHelper', 'public void updateKeys(', 'register subscribed gameplay key'),
     ('fabric:platform/FabricPlatformHelper', 'public boolean isCurrentlyUsingKey(', 'condition read'),
     ('fabric:component/ApugliEntityComponents', 'public void registerEntityComponentFactories(', 'player component and NEVER_COPY respawn policy'),
     ('fabric:network/ApugliPackets', 'public static void registerC2S()', 'packet registration')],
    'KeyPressedCondition为Player登记需监听的key并读取组件。客户端START_CLIENT_TICK采集物理按键增删，通过UpdateKeysPressedPacket传给真实ServerPlayer；handle用server.execute延后修改该玩家组件的Set，计算增删差集并复制continuous键快照后同步。组件tick在power总数变化时清三组键，玩家注册设置RespawnCopyStrategy.NEVER_COPY。',
    '借鉴网络事件先入服务端执行上下文再修改玩法状态，使用服务器传入player确定持有者而非客户端自报ID；Set与差集抑制重复状态写入，重生时不继承瞬态输入。方天仍需独立的每次攻击回执ID和短TTL。',
    '这是实际power按键条件链而非纯传输库；但Set幂等不等于一次动作消费，非continuous按键快照被过滤也不保证组件本身自动消费。未核验包序号、TTL、玩家退出/切维度，任务可能在状态变化后执行；仅比power数量，等量替换检测不到。',
    ['deferred_gameplay_input', 'owner_binding', 'snapshot', 'respawn_cleanup'],
    scope='真实物理按键→服务器排队→玩家power条件消费与重生清理；跨加载器不另计。')

add('packet-meta-actions-auxiliary',
    ('common:network/c2s/ExecuteBiEntityActionServerPacket', 'public void handle(', 'current-world target lookup inside scheduled task'),
    [('common:network/c2s/ExecuteBiEntityActionServerPacket', 'public static <A> ExecuteBiEntityActionServerPacket<A> decode(', 'decode mismatch'),
     ('common:network/c2s/ExecuteEntityActionServerPacket', 'public void handle(', 'same meta dispatch family'),
     ('common:action/factory/entity/meta/PacketAction', 'public void execute(', 'producer wrapper'),
     ('common:action/factory/bientity/meta/PacketAction', 'public void execute(', 'bientity producer wrapper')],
    '元动作把序列化动作发送后交server.execute，双实体在执行时从player.level按otherEntityId解析并选择actor/target；单实体直接用连接绑定player。',
    '只作反例：延迟消费时应验证原维度与target UUID；不要单凭当前level的数字ID复原旧目标。',
    '未找到具体战斗/任务配置使用该元动作的链，属于通用分派包装，不计。双实体decode读entityDataType而encode写biEntityDataType，且无null/alive/UUID/TTL验证。两个meta包装合并为一条辅助。',
    ['auxiliary_dispatch'], valid=False)

add('bunnyhop-window-auxiliary',
    ('fabric:power/BunnyHopPower', 'public void tick()', 'movement-resource grace window'),
    [('common:power/factory/BunnyHopPowerFactory', 'default void reset(', 'resource reset'),
     ('common:power/factory/BunnyHopPowerFactory', 'default void onTravel(', 'periodic gain and movement'),
     ('common:power/factory/BunnyHopPowerFactory', 'default boolean canGainResource(', 'airborne gate'),
     ('fabric:mixin/fabric/common/LivingEntityMixin', 'private void apugli$travelLivingEntity(', 'real travel hook')],
    '真实bunny_hop power连续不满足空中条件时framesOnGround累加，进入tick时>4便reset资源；重新满足条件归零。onTravel按max(1,tick_rate)周期增益并立即moveRelative。',
    '可辅助理解短暂容错窗口与服务器侧周期更新，边界应按判定/累加顺序分析。',
    '未见待消费事件或combat/task queue，只是移动资源衰减窗口，保守辅助0分；不能因出现tick计数便当回执研究信用。',
    ['auxiliary_short_window'], valid=False)

add('spawn-item-delay-auxiliary',
    ('common:action/factory/entity/SpawnItemAction', 'public void execute(', 'item spawning producer'),
    [('common:action/factory/entity/SpawnItemAction', 'private ItemEntity createItemEntity(', 'pickup delay assignment')],
    'createItemEntity设置pickUpDelay与thrower，调用者将配置的stack映射为ItemEntity加入世界；retainOwnership分支重复setThrower。',
    '辅助区分物品拾取延迟与待处理伤害回执的寿命，不混同二者。',
    '没有消费方玩法链或回执/任务队列；filter(ItemStack::isEmpty)还只保留空stack，不能宣称运行有效。保守辅助0分，未运行代码。',
    ['auxiliary_delay_assignment'], valid=False)


def dump(name, value):
    (DOCS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    scope_pending_ids = {'client-periodic-actions', 'delayed-scale-power-lifecycle'}
    for row in ROWS:
        if row['chain_id'] in scope_pending_ids:
            row['decision'] = 'reviewed_scope_pending_zero_credit'
            row['proposed_credit'] = 0
    tree_path = TOOLS / 'sources/MerchantPug__Apugli/git-tree.json'
    remote = json.loads(tree_path.read_text())
    assert not remote.get('truncated')
    remote_blobs = {x['path']: x['sha'] for x in remote['tree'] if x['type'] == 'blob'}
    commit = json.loads((TOOLS / 'sources/MerchantPug__Apugli/commit.json').read_text())
    assert commit['sha'] == PIN
    # The response echoes the requested commit in its top-level SHA. Reconstruct
    # every tree object from entries instead of mistaking that field for a tree ID.
    tree_ids = {x['path']: x['sha'] for x in remote['tree'] if x['type'] == 'tree'}
    tree_ids[''] = commit['commit']['tree']['sha']
    for directory, expected in tree_ids.items():
        children = [x for x in remote['tree']
                    if ('' if str(pathlib.PurePosixPath(x['path']).parent) == '.'
                        else str(pathlib.PurePosixPath(x['path']).parent)) == directory]
        children.sort(key=lambda x: pathlib.PurePosixPath(x['path']).name + ('/' if x['type'] == 'tree' else ''))
        payload = b''.join((x['mode'].lstrip('0') + ' ' + pathlib.PurePosixPath(x['path']).name).encode()
                           + b'\0' + bytes.fromhex(x['sha']) for x in children)
        actual_tree = hashlib.sha1(b'tree ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()
        assert actual_tree == expected, (directory, expected, actual_tree)
    source_index = []
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():
            continue
        data = p.read_bytes()
        relative = str(p.relative_to(ROOT))
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert remote_blobs[relative] == blob, relative
        source_index.append(dict(path=relative, source_local=local(p), source_sha256=sha(data), git_blob_sha1=blob))
    dump('source-index.json', source_index)
    main_ledger = WORKSPACE / 'docs/cod4/audit-20261022/sweep-receipt-research'
    duplicate_hits = []
    inputs = []
    for name in ['protocol.json', 'accepted.jsonl', 'reviewed.jsonl']:
        raw = (main_ledger / name).read_bytes()
        inputs.append(dict(path=local(main_ledger / name), sha256=sha(raw), read_only=True))
        if name.endswith('jsonl'):
            for line in raw.decode().splitlines():
                item = json.loads(line)
                if re.search(r'apugli|rpginventory', item.get('repo', ''), re.I):
                    duplicate_hits.append(dict(ledger=name, candidate_id=item.get('candidate_id'), repo=item.get('repo')))
    assert not duplicate_hits, duplicate_hits
    evidence_count = 0
    for row in ROWS:
        for ev in row['evidence']:
            actual = (WORKSPACE / ev['source_local']).read_bytes()
            assert ev['source_sha256'] == sha(actual)
            assert ev['excerpt'] == '\n'.join(actual.decode().splitlines()[ev['line'] - 1:ev['end_line']])
            evidence_count += 1
        row['pin_verification'] = dict(kind='commit_archive_and_git_tree_blobs', tree=local(tree_path),
                                       tree_sha256=sha(tree_path.read_bytes()),
                                       git_tree_sha=commit['commit']['tree']['sha'],
                                       tree_response_sha=remote['sha'], all_tree_objects_reconstructed=True)
    valid = [r for r in ROWS if r['proposed_credit']]
    pending = [r for r in ROWS if r['chain_id'] in scope_pending_ids]
    auxiliary = [r for r in ROWS if not r['proposed_credit'] and r['chain_id'] not in scope_pending_ids]
    dump('batch-001.json', dict(schema_version=1, reviewer_role='exclusive helper, not final ledger owner',
                               reviewed_at=NOW, repo=REPO, revision=PIN, entries=valid))
    dump('auxiliary-reviewed.json', dict(entries=auxiliary))
    dump('scope-pending-reviewed.json', dict(entries=pending, credit=0,
                                           reason='Full methods reviewed, but scope/structural independence requires Carson judgment. Excluded from proposed-valid count.'))
    (DOCS / 'reviewed.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in ROWS))
    dump('validation.json', dict(valid=True, entries=len(ROWS), proposed_valid=len(valid), auxiliary=len(auxiliary),
                                 scope_pending_zero_credit=len(pending),
                                 evidence_methods=evidence_count, snapshot_files_git_blob_verified=len(source_index),
                                 source_hashes_and_method_ranges_verified=True,
                                 downloaded_code_executed=False, game_started=False, server_started=False,
                                 final_credit_applied_to_main_ledger=0, main_ledger_duplicate_hits=duplicate_hits,
                                 protocol_and_main_ledger_inputs=inputs))
    dump('handoff.json', dict(target=80, fully_reviewed_independent_proposals=len(valid), gap_to_target=80-len(valid),
                              reviewed_auxiliary_zero_credit=len(auxiliary), unreviewed_credit=0,
                              reviewed_scope_pending_zero_credit=len(pending),
                              final_credit_applied=0, final_count_owner='Carson',
                              repositories=json.loads((TOOLS / 'sources.json').read_text()),
                              coverage='Pinned default branch 1.20.4; source-wide temporal/scheduling/identity search, followed by full method and call-chain review. Not a historical-branch exhaustiveness claim.',
                              candidate_is_not_credit=True,
                              dedup='Canonical transferred Apugli repo; entire lifecycle counted once; Fabric/NeoForge wrappers, NBT methods, alternative spawns and termination paths receive no extra credit.',
                              scope_review_flags=['client-periodic-actions may be structurally merged with projectile-periodic-actions by Carson',
                                                  'delayed-scale-power-lifecycle is a delayed gameplay power task, not combat; downgrade if master scope excludes it'],
                              restrictions=['Only helper directories written', 'No production Java/assets/todo/main ledgers changed', 'No downloaded code, Gradle, game or server executed']))
    print(json.dumps(dict(proposed_valid=len(valid), auxiliary=len(auxiliary), scope_pending=len(pending), evidence_methods=evidence_count,
                          git_verified_files=len(source_index), gap=80-len(valid)), ensure_ascii=False))


if __name__ == '__main__':
    main()
