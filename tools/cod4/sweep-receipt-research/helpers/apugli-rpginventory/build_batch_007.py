"""Package manually read source evidence only; never load or execute upstream code."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from evidence_003 import DOCS, HERE, WORKSPACE, ROOTS, METADATA, PINS, method, sha

PIN = 'f4e77d43f39ba1047bf93ae816b7e1beaab514c2'
REPO = 'SlimeKnights/TinkersConstruct'
ORIGIN = WORKSPACE / 'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct'
DEST = HERE / 'sources/SlimeKnights__TinkersConstruct-007'
NOW = datetime.now(timezone.utc).isoformat()
META = json.loads((ORIGIN / 'source.json').read_text())
TREE_RAW = (ORIGIN / 'tree.json').read_bytes()
TREE = json.loads(TREE_RAW)
assert META['repo'] == REPO and META['sha'] == PIN
assert TREE['sha'] == PIN and not TREE['truncated']
BLOBS = {x['path']: x['sha'] for x in TREE['tree'] if x['type'] == 'blob'}
DEST.mkdir(parents=True, exist_ok=True)
(DEST / 'source.json').write_bytes((ORIGIN / 'source.json').read_bytes())
(DEST / 'tree.json').write_bytes(TREE_RAW)
ROOTS['tinkers007'] = DEST
PINS['tinkers007'] = PIN
METADATA['tinkers007'] = DEST / 'source.json'
FILES = {}
ROWS = []


def copy_file(short):
    path = 'src/main/java/slimeknights/tconstruct/' + short + '.java'
    raw = (ORIGIN / path).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == BLOBS[path], path
    target = DEST / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    FILES[path] = dict(path=path, source_local=str(target.relative_to(WORKSPACE)),
                       source_sha256=sha(raw), git_blob_sha1=blob,
                       origin_local=str((ORIGIN / path).relative_to(WORKSPACE)))
    return path


def methods(short, *specs):
    path = copy_file(short)
    out = []
    for signature, role in specs:
        item = method('tinkers007', path, signature, role)
        item['repo'] = REPO
        item['evidence_kind'] = 'complete_method'
        item['url'] = f'https://github.com/{REPO}/blob/{PIN}/{path}#L{item["line"]}-L{item["end_line"]}'
        out.append(item)
    return out


def declaration(short, first, last, role):
    """Precisely label configuration statements; never claim an enclosing method was read."""
    path = copy_file(short)
    raw = (DEST / path).read_bytes()
    excerpt = '\n'.join(raw.decode().splitlines()[first - 1:last])
    return dict(repo=REPO, revision=PIN, path=path, method=None,
                source_metadata=str((DEST / 'source.json').relative_to(WORKSPACE)),
                source_local=str((DEST / path).relative_to(WORKSPACE)), source_sha256=sha(raw),
                line=first, end_line=last, excerpt=excerpt, snippet_sha256=sha(excerpt.encode()),
                evidence_kind='configuration_statement_not_complete_method', role=role,
                url=f'https://github.com/{REPO}/blob/{PIN}/{path}#L{first}-L{last}')


def fixed_method(short, first, last, name, role):
    item = declaration(short, first, last, role)
    item.update(method=name, evidence_kind='complete_method')
    assert item['excerpt'].rstrip().endswith('}')
    assert item['excerpt'].count('{') == item['excerpt'].count('}')
    return item


def add(key, evidence, observation, application, limits, nearest, distinction, proposal):
    row = dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-007-' + key, chain_id=key, batch='007',
               status='reviewed', decision='reviewed_valid_pending_carson' if proposal else 'reviewed_excluded_zero_credit',
               credit=0, proposed_credit=int(proposal), final_count_owner='Carson', reviewed_at=NOW,
               evidence=evidence, observation=observation, application=application, limits=limits,
               dedup_key=REPO + ':' + key, external_runtime_tested=False, downloaded_code_executed=False,
               counting_unit='One independently owned gameplay lifecycle, not each supporting method, side or branch.',
               semantic_dedup=dict(nearest_existing_families=nearest,
                                   independent_state_and_consumer=distinction,
                                   supporting_methods_increment=0, mirrored_or_version_increment=0))
    ROWS.append(row)


data_support = methods('library/tools/capability/TinkerDataCapability',
    ('private static void attachCapability(', 'native entity-local Holder attachment'),
    ('public static TinkerDataCapability.Holder getData(', 'resolve actual target Holder'),
    ('public <T> void put(TinkerDataKey<T> key, T value)', 'write boxed value, including zero'),
    ('public <T> T get(TinkerDataKey<T> key)', 'read without remove; null is absence'),
    ('public void remove(TinkerDataKey<?> key)', 'available removal operation is not called by XP consumer'),
    ('public void run()', 'invalidate/revive preserves the original Holder'))
nbt_support = methods('library/tools/capability/PersistentDataCapability',
    ('public static ModDataNBT getOrWarn(', 'missing cap returns detached empty data'),
    ('private static void attachCapability(', 'living and supported projectile data attachment'))
nbt_support += methods('library/tools/nbt/ModDataNBT',
    ('public <T> T get(ResourceLocation name,', 'CompoundTag getter delegate'),
    ('public void putFloat(', 'store launch-time modifier float'))
nbt_support += methods('library/tools/nbt/IModDataView',
    ('default float getFloat(', 'float reader delegate'))
launch_support = methods('library/tools/item/ranged/ModifiableBowItem',
    ('public void releaseUsing(', 'whole bow release: consume ammunition, attach modifiers/data, dispatch hooks, spawn'))
launch_support += [fixed_method('library/modifiers/hook/ranged/ProjectileLaunchModifierHook', 41, 43,
    'onProjectileLaunch', 'complete interface default overload, excluding the separate NoShooter mirror')]
launch_support += methods('library/tools/capability/EntityModifierCapability',
    ('public static EntityModifiers getCapability(', 'real projectile cap or EMPTY fallback'),
    ('public static ModifierNBT getOrEmpty(', 'death producer requires nonempty projectile modifier list'),
    ('private static void attachCapability(', 'attach only supported entities'),
    ('public static boolean supportCapability(', 'projectile eligibility predicates'),
    ('default void addModifiers(', 'actual projectile modifier list copy/add'))
launch_support += methods('tools/TinkerModifiers',
    ('void commonSetup(', 'register capabilities and actual Projectile support predicate'))

add('death-target-projectile-xp-snapshot-presence-vs-zero',
    methods('tools/logic/ModifierEvents',
        ('static void onExperienceDrop(', 'deferred XP consumer distinguishes boxed zero from missing record'),
        ('static void onLivingDeath(', 'whole death callback records projectile XP on target before drop callback'))
    + methods('library/modifiers/modules/build/VolatileFloatModule',
        ('public void onProjectileLaunch(', 'actual launch producer adds configured float to projectile data'),
        ('public void addVolatileData(', 'held tool fallback builds same stat from present tool'))
    + launch_support + data_support + nbt_support
    + [declaration('tools/data/ModifierProvider', 511, 513,
                   'actual experienced build declaration binds 0.5 per level to VOLATILE_DATA and PROJECTILE_LAUNCH; not the whole addModifiers method')],
    '真实弓 releaseUsing 在服务端创建箭，先复制 modifier 列表，再用同一箭的 PersistentData 派发 PROJECTILE_LAUNCH。已缓存的 experienced 配置声明把每级0.5的 VolatileFloatModule 绑定到 launch 与 volatile-data 两钩子。LivingDeathEvent 看到直接来源为带非空 modifier 的 Projectile 时，把箭上的 EXPERIENCE float 写入死亡目标自身 Holder 的 PROJECTILE_EXPERIENCE。LivingExperienceDropEvent 随后读取此 boxed Float：非null就加它，包括0；只有null才回退到当前玩家 looting 槽的当前工具经验值。玩家属性/护甲值在掉落时另读，不全是发射快照。消费后不remove。',
    '可用结论：回执的存在性必须与数值分开，0不能等于没有记录，否则会误用消费时手持工具。发射、死亡、经验掉落是三个不同取值时点；横扫应在伤害事实产生时固定攻击归属和目标，不应在END回退读取当前装备。记录应写清是否已消费，别把实体局部存储天然当成一次消费。本链只提1项；既有 looting 槽记录只作0分支持。',
    '该记录是死亡事件来源快照，不是最终未取消死亡/成功经验掉落证明；该方法没有receiveCanceled=true，也没有终态确认。未读Forge事件派发完整顺序，不承诺跨tick或必定掉经验。没有TTL、source/target UUID、维度、代次或一次消费清理；死亡被后续监听取消后存活、再次死亡或重复XP回调可能读旧值。Holder未序列化且revive保留原Holder。配置JSON单次补取因本机TLS证书错误失败，未重试；只读了Java datagen中该配置声明，未声称全文读完巨大的addModifiers方法、生成资源加载器或运行时配置。候选相关性及是否独立仍待Carson。',
    ['batch006: ModifierLootingHandler attack-slot dynamic scope', 'batch006: bleeding source re-read', 'main: projectile fuse/gravity task families'],
    'New state lives on killed target and crosses death-to-XP events; explicit present-zero suppresses current-tool fallback. Slot context, DOT and projectile scheduled tasks remain support/comparison, not extra credit.', True)

input_support = methods('tools/ToolClientEvents',
    ('private static void handleKeyBindings(', 'whole client edge detector for jump/head/legs; mirrors count zero'))
input_support += methods('tools/network/TinkerControlPacket',
    ('public void handleThreadsafe(', 'whole sender-resolved control dispatcher, no claimed external Mantle queue ordering'))
armor_support = methods('tools/logic/InteractionHandler',
    ('public static boolean startArmorInteract(', 'actual armor start dispatch'),
    ('public static boolean stopArmorInteract(', 'actual stop removes slot record before calling current tool hooks'))
armor_support += methods('library/modifiers/hook/interaction/KeybindInteractModifierHook',
    ('default void stopInteract(IToolStackView tool, ModifierEntry modifier, Player player, EquipmentSlot slot, int chargeTime,', 'new stop overload delegates to old no-charge callback'))
equipment_support = methods('tools/logic/EquipmentChangeWatcher',
    ('public static void register()', 'server equipment events and client watcher registration'),
    ('private static void onEquipmentChange(', 'server equipment event enters unequip hooks'),
    ('private static void runModifierHooks(', 'old tool unequip precedes replacement equip and other slot callbacks'),
    ('private static void onPlayerTick(', 'client END event has no interval modulus despite comment'),
    ('public void update()', 'copy-before-dispatch and ItemStack.matches prevent mutation alias'),
    ('public void run()', 'client watcher invalidation reuses watcher object'))

add('self-destruct-terminal-effect-with-release-and-unequip-abort',
    methods('tools/modifiers/traits/skull/SelfDestructiveModifier',
        ('public void applyEffectTick(', 'actual delayed terminal explosion and self hurt'),
        ('public boolean isDurationEffectTick(', 'terminal duration exactly one predicate'),
        ('public boolean startInteract(', 'shift+armor key arms 30-tick effect'),
        ('public void stopInteract(', 'release removes pending effect'),
        ('public void onUnequip(', 'unequip cancels pending effect'),
        ('protected void registerHooks(', 'actual interaction/equipment hooks'),
        ('public SelfDestructiveEffect()', 'effect movement penalty while armed'))
    + input_support + armor_support + equipment_support
    + methods('tools/modifiers/effect/NoMilkEffect',
        ('public List<ItemStack> getCurativeItems()', 'empty milk-curative list does not block explicit removeEffect'))
    + [declaration('shared/TinkerEffects', 58, 58, 'actual self_destructing effect registry entry'),
       declaration('tools/TinkerModifiers', 421, 421, 'actual self_destructive modifier registry entry')],
    '真实盔甲按键上升沿经startArmorInteract派发，shift为真时添加30tick selfDestructing效果，其amplifier为2*effectiveLevel；只在剩余duration==1请求applyEffectTick。终端在服务端先explode(living,... amplifier+1,MOB)，再以SELF_DESTRUCT源hurt自己99999。松键的新版stop回调会委托到旧版stopInteract并removeEffect；装备事件先对旧工具调用onUnequip，也removeEffect。effect带-0.9移动乘数。NoMilkEffect没有奶的治愈物，但不阻止这两种显式取消。',
    '独立结论是终端任务的取消入口必须覆盖松键和装备失效，且取消任务标记与终端副作用结果应分开。横扫可借鉴同一回执生命周期有统一终止入口；不得把正常跨tick交接误当取消。这里的explode先发生，自伤失败也不会撤销已触发爆炸，正好提醒不要把尝试、自伤成功、爆炸影响混作同一个结果。整链只1项，006的按键slot挂起基础设施和头腿镜像均为0。',
    '不是可直接照抄的成功伤害回执。duration==1是效果生命周期回调条件，不证明任意外部END队列应该严格同刻；未读外部MobEffect合并/耗时调度，不承诺丢tick补执行。终端调用不检查explode受害者结果，也忽略自伤hurt返回；没有source/target UUID或dim校验。取消是按effect类型全局remove，不按slot/代次分离；旧stop可能清掉同类型较新效果。NoMilk不等于无法取消。服务端与客户端镜像只合计一链；Mantle网络实现未读，不宣称线程派发顺序。',
    ['batch006: armor START/STOP/Sling slot charge lifecycle', 'main: ProjectileFuseModule terminal fuse', 'batch006: SlimeBounceHandler age+1 momentum handoff'],
    'The independent owner is an armed effect with key-release and old-equipment cancellation before a duration-one terminal explosion; not the shared charge slot, projectile fuse transport, or a duplicated side.', True)

add('double-jump-flight-quota-not-new-receipt-chain',
    methods('tools/logic/DoubleJumpHandler',
        ('public static boolean extraJump(', 'runtime air jump quota is checked at handling'),
        ('static void onJump(', 'ground/negative-gravity ceiling jump removes quota'),
        ('static void onLand(', 'fall event resets quota'))
    + input_support
    + methods('library/tools/capability/PersistentDataCapability',
        ('private static void playerClone(', 'quota data can be copied with all persistent state at clone'),
        ('private static void playerChangeDimension(', 'dimension event syncs, not resets quota')),
    '客户端只在跳跃上升沿尝试extraJump，成功后发DOUBLE_JUMP；服务器从sender重新调用同方法。当前不在地面/攀爬/水中，JUMP_COUNT减1取floor的配额大于已用时，先jumpFromGround，再写jumps+1。地面起跳或负重力撞顶起跳、LivingFallEvent清jumps；未见flight epoch。PersistentData clone复制旧NBT，跨维度仅sync。',
    '有用的零分补证：当前资格重验优于仅信任客户端，但旧腾空周期请求没有代次绑定。这个状态是动作配额，不是已经成功的伤害事实；不能把它包装成新的横扫延迟回执实现。',
    '主账已含Enigmatic输入上升沿和Artifacts DoubleJumpPacket，且Mantle外部排队实现未读；没有足够独立的延后事实消费，保守排除。方法、平台和reset分支全部0信用。',
    ['main: EnigmaticKeybindHandler.onKeyInput', 'main: artifacts DoubleJumpPacket.apply', 'batch006: same TinkerControlPacket support'],
    'No new proposed counting unit; quota/reset comparisons are evidence only.', False)

add('equipment-watcher-support-not-new-credit', equipment_support,
    '客户端lastItems为EnumMap，每个槽位用ItemStack.matches比较；变化时先newStack.copy存快照，再派发旧工具unequip、新工具equip、其他槽回调。实际onPlayerTick仅检查END/CLIENT，没有注释所说5tick间隔。',
    '快照拷贝避免可变ItemStack引用掩盖变化；先保存再回调能限制同一状态重入。这里仅用于证明自爆卸装取消实际有派发链。',
    '属于本批自爆链支持和两端装备事件镜像，不单独提出通用缓存或方法计数。',
    ['batch007: self-destruct cancellation chain', 'prior Apugli equip mirrors excluded'],
    'Supporting dispatcher/cache only; zero incremental unit.', False)


def dump(name, value):
    (DOCS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


main = WORKSPACE / 'docs/cod4/audit-20261022/sweep-receipt-research'
comparison = []
for p in [main / 'accepted.jsonl', main / 'reviewed.jsonl']:
    for line in p.read_text().splitlines():
        if line.strip():
            comparison.append(json.loads(line))
for p in DOCS.glob('batch-00[1-6].json'):
    comparison.extend(json.loads(p.read_text())['entries'])
for row in ROWS:
    matches = [d for d in comparison if (d.get('repo'), d.get('revision'), d.get('path'), d.get('line')) ==
               (row['repo'], row['revision'], row['path'], row['line'])]
    row['semantic_dedup']['exact_primary_preexisting'] = bool(matches)
    if row['proposed_credit']:
        assert not matches, row['candidate_id']

proposed = [r for r in ROWS if r['proposed_credit']]
excluded = [r for r in ROWS if not r['proposed_credit']]
common = dict(schema_version=1, reviewed_at=NOW, credit_applied=0, final_count_owner='Carson',
              scope_authorization='Human authorized already-fixed other sources after Apugli semantic exhaustion; keep own helper-only writes.',
              source_revision=PIN, no_compilation=True, no_runtime_tests=True, upstream_code_executed=False)
dump('batch-007.json', dict(common, proposed_valid=len(proposed), entries=proposed))
dump('excluded-007.json', dict(common, proposed_valid=0, entries=excluded))
(DOCS / 'reviewed-007.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in ROWS))
dump('source-index-007.json', dict(repo=REPO, revision=PIN,
    official_source_provenance=META, provenance_reverified_online=False,
    pinned_tree_local=str((DEST / 'tree.json').relative_to(WORKSPACE)),
    pinned_tree_sha256=sha(TREE_RAW), files=list(FILES.values()),
    failed_configuration_fetch=str((HERE / 'fetch-007-error.json').relative_to(WORKSPACE)),
    http_attempts=1, http_successes=0, retries=0, upstream_code_executed=False))

errors = []
unique = {}
for row in ROWS:
    for e in row['evidence']:
        raw = (WORKSPACE / e['source_local']).read_bytes()
        actual = '\n'.join(raw.decode().splitlines()[e['line'] - 1:e['end_line']])
        if sha(raw) != e['source_sha256'] or actual != e['excerpt'] or sha(actual.encode()) != e['snippet_sha256']:
            errors.append((row['candidate_id'], e['path']))
        unique[(e['path'], e['line'], e['end_line'])] = e
assert not errors, errors
dump('validation-007.json', dict(schema_version=1, reviewed_at=NOW,
    validation_kind='Text/hash/range evidence integrity only; not compilation or gameplay test',
    errors=errors, files=len(FILES), unique_complete_method_ranges=sum(e['evidence_kind']=='complete_method' for e in unique.values()),
    configuration_statement_ranges=sum(e['evidence_kind']!='complete_method' for e in unique.values()),
    proposed_pending_carson=len(proposed), excluded_zero_credit=len(excluded), applied_credit=0,
    main_ledger_read_only_snapshots={p.name: sha(p.read_bytes()) for p in [main/'accepted.jsonl', main/'reviewed.jsonl', main/'protocol.json']},
    method_count_is_not_credit=True, compilation_performed=False, runtime_tests_performed=False,
    production_qa_or_todo_written=False, upstream_code_executed=False,
    outputs={name: sha((DOCS/name).read_bytes()) for name in ['batch-007.json','excluded-007.json','reviewed-007.jsonl','source-index-007.json']}))
print(json.dumps(dict(proposed=len(proposed), excluded=len(excluded), evidence_ranges=len(unique), files=len(FILES), errors=errors, credit=0)))
