"""Historical Apugli gameplay review, text evidence only, no upstream execution."""
import datetime
import json
from evidence_003 import CACHE, DOCS, WORKSPACE, PINS, ROOTS, METADATA, REPO, method, dump, sha

BRANCH = 'architectury116'
PINS[BRANCH] = 'c465103bbb607a1b96e09f00b9a1443d7d810838'
ROOTS[BRANCH] = CACHE / 'architectury116-tree-004'
METADATA[BRANCH] = CACHE / 'architectury116-commit-004.json'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
ROWS = []


def ev(short, signatures):
    platform, name = short.split(':', 1)
    path = f'{platform}/src/main/java/com/github/merchantpug/apugli/{name}.java'
    return [method(BRANCH, path, sig, role) for sig, role in signatures]


def add(key, evidence, observation, application, limits, proposal=False, duplicate_of=None):
    x = dict(evidence[0])
    x.update(candidate_id='apugli-rpginventory-004-' + key, chain_id=key,
             batch='004', status='reviewed', credit=0, proposed_credit=int(proposal),
             decision='reviewed_valid_pending_carson' if proposal else 'reviewed_excluded_zero_credit',
             final_count_owner='Carson', reviewed_at=NOW, evidence=evidence,
             observation=observation, application=application, limits=limits,
             duplicate_of=duplicate_of, dedup_key=REPO + ':' + key,
             counting_unit='One complete gameplay state lifecycle; historical versions and loader mirrors never multiply credit.',
             external_runtime_tested=False, downloaded_code_executed=False)
    ROWS.append(x)


add('temporary-food-component-lease-and-slot-revoke',
    ev('common:powers/EdibleItemPower', [
        ('public void onRemoved()', 'producer checks old component ownership then sends slot-addressed revocations'),
        ('public void tempTick()', 'actual periodic per-hand grant/revoke state machine'),
        ('public void sendFoodComponentRemovePacket(', 'actual target entity/slot payload'),
        ('public EdibleItemPower(', 'retains component instance and enables ticking'),
        ('public static PowerFactory<?> getFactory()', 'registered concrete gameplay configuration')]) +
    ev('common:mixin/LivingEntityMixin', [('private void tick(', 'real baseTick calls inactive and active Edible powers')]) +
    ev('common:util/ItemStackFoodComponentUtil', [
        ('public static void setStackFood(', 'grant concrete four-field item state'),
        ('public static void removeStackFood(', 'revoke concrete item state')]) +
    ev('common:mixin/ItemStackMixin', [
        ('public void setItemStackFoodComponent(', 'actual food-component state setter'),
        ('public FoodComponent getItemStackFoodComponent()', 'component identity read'),
        ('public boolean isItemStackFood()', 'actual gameplay availability'),
        ('public void setFoodUseAction(', 'null cleanup is ignored'),
        ('public void setReturnStack(', 'actual return-item state setter'),
        ('public void setStackEatSound(', 'actual sound state setter'),
        ('private void getUseAction(', 'real gameplay consumes temporary component'),
        ('private void getMaxUseTime(', 'temporary food determines actual use duration'),
        ('private void finishUsing(', 'actual food consumption hook'),
        ('private void copyFoodComponent(', 'copied item inherits temporary component')]) +
    ev('fabric:powers/fabric/EdibleItemPowerImpl', [('public static void sendPackets(', 'real platform sender, all worlds plus self')]) +
    ev('common:networking/ApugliPacketsS2C', [
        ('private static void onFoodComponentSync(', 'queue decodes slot address then mutates current slot item'),
        ('public static void register()', 'actual receiver registration')]) +
    ev('common:ApugliClient', [('public static void register()', 'client initialization reaches receiver')]) +
    ev('common:registry/ApugliPowerFactories', [('public static void register()', 'actual Edible power registration')]) +
    ev('common:Apugli', [('public static void init()', 'initializer connects gameplay registry')]),
    'architectury/1.16固定提交，配置Minecraft 1.16.5/Apugli 1.7.0+1.16.5。LivingEntity.baseTick对Player包含inactive的Edible power调用tempTick；每age%tickRate==0按当前手持物品、predicate、active与现有component决定附加/撤销食物组件。归属用同一FoodComponent对象引用核对。power.onRemoved扫描背包/护甲/副手，先验证predicate和旧component身份，删本地状态，再向客户端发targetId+EquipmentSlot或InventoryLocation/index。实际Fabric sender广播各世界玩家并单独发本人；注册过的S2C接收器context.queue后查当前世界目标Player，重新取当前槽位物品并无条件removeStackFood。整个组件租用、使用、复制、撤销与延后同步只建议一条。',
    '区别于后续版本的原版use/finish钩子，本版本拥有临时组件本身的授权、周期复核、归属清理与真实延后撤销。新观察是生产端核对过的身份不能在消费端只剩槽坐标：旧撤销任务若遇到已换槽或重新授予的新组件，可能误清新状态。借鉴把原任务/状态代次随撤销证据一起保存，并在终端再次核对；不能用“源端曾检查过”替代消费前身份检查。',
    '历史开发分支，无编译/运行验证。不是战斗伤害回执，不推定TTL值。客户端没有原stack身份、component/power ID、UUID、维度或代次校验，也无inventoryIndex/枚举范围显式校验；本人可能收到广播与单发两份。tempTick副手授予分支检查的是主手是否food，且predicate变false时不撤销；只轮询双手，不覆盖全部背包。tick_rate未夹到正值。removeStackFood将useAction置null，但真实setter只接EAT/DRINK，旧action可能保留；copy沿用同一组件引用，移除又要求当前predicate成立，不能宣称全部旧授权都已回收。物品finishUsing有两个HEAD入口，不能证明动作严格一次；下列单独重复回调审阅不加信用。',
    True, 'batch003:edible-use-finish-mutable-input is zero-credit; this older branch adds its own component lease/revoke state, not a renamed vanilla timer')

add('food-head-hooks-and-return-overwrite',
    ev('common:mixin/ItemStackMixin', [
        ('private void executeEntityActions(', 'one HEAD callback dispatch'),
        ('private void finishUsing(', 'second HEAD callback dispatch plus return overwrite')]) +
    ev('common:powers/EdibleItemPower', [('public void eat()', 'same configured action consumer')]),
    '同一finishUsing有两个HEAD注入：executeEntityActions在user非null时发Edible.eat，cancellable finishUsing在临时food分支再次发eat。后者若有returnStack先setReturnValue(returnStack或eatFood)，随后无条件再次setReturnValue(user.eatFood(...))，覆盖前值；creative分支在该静态路径含两次eatFood表达式。',
    '这是同链中一次性语义的具体反例：多个入口调用同一action不等于只有一次消费；返回值也不是first-write-wins。保留给上一条租用整链的限制，不能独立计数。',
    '两个同HEAD注入的实际先后顺序与取消传播未在Mixin运行时验证，不能声称所有配置下一定双发。同步入口，没有新TTL或任务容器。',
    False, 'batch004:temporary-food-component-lease-and-slot-revoke')

add('status-effect-hidden-link-preservation',
    ev('common:mixin/LivingEntityMixin', [('private StatusEffectInstance modifyStatusEffect(', 'modify top effect while retaining same hidden-link reference')]) +
    ev('common:mixin/StatusEffectInstanceMixin', [('public @Nullable StatusEffectInstance getHiddenEffect()', 'read external vanilla hidden effect field')]) +
    ev('common:powers/ModifyStatusEffectDurationPower', [('public boolean doesApply(', 'effect-type condition'), ('public static PowerFactory getFactory()', 'duration modifier factory')]) +
    ev('common:powers/ModifyStatusEffectAmplifierPower', [('public boolean doesApply(', 'same predicate shape'), ('public static PowerFactory<?> getFactory()', 'same template for amplifier')]),
    'addStatusEffect HEAD在原amplifier/duration上分别应用Origins修饰器，任一变化才构造新StatusEffectInstance，复制显示属性并传入原hiddenEffect引用。当前仓库仅提供hiddenEffect getter，没有自有hidden状态轮转/过期消费实现；两种修饰power是同一模板族。',
    '记录替换外层事实对象时仍可能共享内部旧状态链；不能因new了外层实例就认为有完整不可变快照。这里不推断隐藏效果未来激活或到期行为。',
    '延后隐藏效果消费与duration递减由原版负责，未在授权仓库阅读，不计。不是新任务队列，不能把duration/amplifier两个工厂或getter重复算实现。',
    False)

add('inverted-cooldown-is-display-only',
    ev('common:powers/InvertedCooldownPower', [
        ('public float getProgress()', 'world time minus last-use produces clamped inverted fraction'),
        ('public static PowerFactory<?> getFactory()', 'actual HUD power configuration')]),
    'InvertedCooldown只override getProgress，使用world.getTime-lastUseTime后计算clamp(1-time/cooldown,0,1)。原use、canUse、过期和lastUseTime写入都继承外部Origins；当前方法不消费任何回执。',
    '区分UI进度、动作冷却资格与事件有效年龄，三者不能仅因都出现time/cooldown便替代。',
    '完整审阅了此类两个相关方法，但父类核心时钟实现未审阅；HUD比例不代表短TTL/一次消费，不计。配置未在此方法防御cooldown=0，不能据clamp保证所有数值有限。',
    False)

add('legacy-uuid-key-sync-is-not-sender-binding',
    ev('common:networking/ApugliPacketsC2S', [('private static void onSyncActiveKeys(', 'queued UUID lookup from payload, not from authenticated sender'), ('public static void register()', 'real receiver registration')]) +
    ev('common:networking/ApugliPacketsS2C', [('private static void onSyncActiveKeys(', 'queued full key-state snapshot or remove')]) +
    ev('common:mixin/ActiveKeyMixin', [('public boolean equals(', 'logical key plus continuous flag dedup'), ('public int hashCode()', 'matching semantic key hash')]) +
    ev('fabric:fabric/ApugliFabricClient', [('public void onInitializeClient()', 'actual disconnect cleanup of static maps')]),
    '旧版C2S解出payload.playerId UUID，排队后在sender当前world按该UUID查Player；没有显式验证查出的实体就是context.getPlayer。之后广播当前keys全量快照并按所查UUID覆盖静态表；空数组删除。S2C也按UUID查Player再覆盖或删除。Active.Key.equals/hashCode按key字符串与continuous字段去重，Fabric断开清静态表。',
    '新增身份观察是UUID解决稳定标识，不自动证明发包者有权替该UUID写入。仅补首批已接受按键链的版本对照，不重报该链。',
    '没有审阅本版本完整客户端按键生产/具体power消费，不把运输回调独立计数；现有参考已接受同族生命周期。无序列/维度/TTL，空快照是清除指令但没有代次，未运行网络或断开测试。',
    False, 'batch001:server-key-diff-task / main accepted UpdateKeysPressedPacket')

add('legacy-enchantment-cache-version-dedup',
    ev('common:powers/ModifyEnchantmentLevelPower', [
        ('public static void updateEnchantments(', 'real enchantment mutation updates per-owner tag map'),
        ('public static ListTag getEnchantments(', 'always computes gameplay enchantments'),
        ('public static ListTag generateEnchantments(', 'concrete configured enchantment rebuild'),
        ('private static Optional<Integer> findEnchantIndex(', 'locate tag entry')]) +
    ev('common:mixin/ItemStackMixin', [
        ('private void cacheEntity(', 'inventory tick binds holder only when null'),
        ('private void copyEntity(', 'copy preserves holder'),
        ('private void addEnchantment(', 'actual source mutation producer')]),
    '旧版按entity UUID字符串→原ListTag→新ListTag储存；getEnchantments每次compute并重建，不是短TTL命中缓存。ItemStack.inventoryTick仅在holder为null时绑定，copy复制旧holder；换持有者未必更新绑定，addEnchantment TAIL更新旧holder桶。',
    '补充可变物品与持有者生命周期边界：物品copy和转手不是同一身份事件，首次绑定后永不重绑可能把后续玩法算给旧持有者。',
    '与batch003已建议的附魔玩法状态整链同族，只记录版本差异0分；未在此版本发现独立过期/移除清理，不能因旧版String UUID和新版UUID类型不同加一条。',
    False, 'batch003:enchantment-gameplay-invalidation-and-deferred-remove')

add('legacy-rocket-client-recomputation',
    ev('common:powers/RocketJumpPower', [
        ('private void handleRocketJump(', 'server explosion result plus self launch'),
        ('public void sendExplosionToClient(', 'actual origin/radius packet producer')]) +
    ev('common:networking/ApugliPacketsS2C', [('private static void onSyncRocketjumpExplosion(', 'queued client reconstructs explosion and calls both phases')]),
    '旧版服务端handleRocketJump创建爆炸并collectBlocksAndDamageEntities/affectWorld，再发userId/坐标/radius。客户端queue后查当前世界LivingEntity，再重建爆炸并再次调用collectBlocksAndDamageEntities和affectWorld；不是新版本只finalize表现的实现。',
    '这说明跨版本核验必须按固定提交说清消费阶段；不能将batch002当前版本“客户端只finalize”套到旧版。此处保留对照，不提供新独立建议。',
    '属于同一RocketJump/Explosion任务族，旧版客户端重算不另计。未审阅原版爆炸内部client/server权限，不能由方法名推定服务端伤害被结算两次；未启动游戏。',
    False, 'batch002:explosion-parameter-consumption-and-effect-task')


def main():
    source_index = json.loads((DOCS / 'branch-source-index-004.json').read_text())
    index = {x['source_local']: x for x in source_index['files']}
    assert source_index['revision'] == PINS[BRANCH]
    unique = set()
    for x in ROWS:
        for e in x['evidence']:
            data = (WORKSPACE / e['source_local']).read_bytes()
            assert sha(data) == e['source_sha256'] == index[e['source_local']]['source_sha256']
            assert e['excerpt'] == '\n'.join(data.decode().splitlines()[e['line'] - 1:e['end_line']])
            unique.add((e['revision'], e['path'], e['line'], e['end_line']))
    previous = []
    for name in ['reviewed.jsonl', 'reviewed-002.jsonl', 'reviewed-003.jsonl']:
        previous.extend(json.loads(line) for line in (DOCS / name).read_text().splitlines() if line)
    assert not ({x['dedup_key'] for x in ROWS} & {x['dedup_key'] for x in previous})
    main_accepted = DOCS.parents[1] / 'accepted.jsonl'
    raw = main_accepted.read_bytes()
    accepted = [json.loads(line) for line in raw.decode().splitlines() if line]
    exact = [x['candidate_id'] for x in ROWS if x['proposed_credit'] and any((x['revision'],x['path'],x['line']) == (a.get('revision'),a.get('path'),a.get('line')) for a in accepted)]
    assert not exact
    proposals = [x for x in ROWS if x['proposed_credit']]
    dump('batch-004.json', dict(schema_version=1, reviewed_at=NOW, credit_applied=0,
                              final_count_owner='Carson', proposed_valid=len(proposals), entries=proposals))
    dump('excluded-004.json', dict(schema_version=1, credit=0, entries=[x for x in ROWS if not x['proposed_credit']]))
    (DOCS / 'reviewed-004.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in ROWS))
    dump('validation-004.json', dict(valid=True, reviewed_groups=len(ROWS), proposed_valid=len(proposals),
                                   zero_credit_groups=len(ROWS)-len(proposals), distinct_complete_method_ranges=len(unique),
                                   pinned_files_verified=len(index), source_hash_and_full_ranges_verified=True,
                                   main_accepted_read_only_sha256=sha(raw), exact_main_duplicates=exact,
                                   credit_applied=0, game_started=False, server_started=False, downloaded_code_executed=False,
                                   logical_network_requests=5, http_errors=0,
                                   directory_only_leads=['feature/1.20','multiloader/1.19.2'], directory_only_lead_credit=0))
    print(json.dumps(dict(proposals=len(proposals), zero=len(ROWS)-len(proposals), methods=len(unique), credit=0)))


if __name__ == '__main__':
    main()
