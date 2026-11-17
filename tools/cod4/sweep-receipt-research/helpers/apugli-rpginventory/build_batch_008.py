"""Package locally read evidence. Does not execute upstream sources or run tests."""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from evidence_003 import DOCS, HERE, WORKSPACE, ROOTS, METADATA, PINS, method, sha

REPO = 'SlimeKnights/TinkersConstruct'
PIN = 'f4e77d43f39ba1047bf93ae816b7e1beaab514c2'
ORIGIN = WORKSPACE / 'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct'
DEST = HERE / 'sources/SlimeKnights__TinkersConstruct-008'
NOW = datetime.now(timezone.utc).isoformat()
META = json.loads((ORIGIN/'source.json').read_text())
TREE = json.loads((ORIGIN/'tree.json').read_text())
assert META['repo'] == REPO and META['sha'] == TREE['sha'] == PIN and not TREE['truncated']
BLOBS = {x['path']: x['sha'] for x in TREE['tree'] if x['type'] == 'blob'}
DEST.mkdir(parents=True, exist_ok=True)
for name in ['source.json', 'tree.json']:
    (DEST/name).write_bytes((ORIGIN/name).read_bytes())
ROOTS['tinkers008'] = DEST
PINS['tinkers008'] = PIN
METADATA['tinkers008'] = DEST/'source.json'
FILES = {}

def copy(short):
    path = 'src/main/java/slimeknights/tconstruct/' + short + '.java'
    raw = (ORIGIN/path).read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert BLOBS[path] == blob, path
    target = DEST/path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    FILES[path] = dict(path=path, source_local=str(target.relative_to(WORKSPACE)),
                       source_sha256=sha(raw), git_blob_sha1=blob)
    return path

def m(short, signature, role):
    path = copy(short)
    e = method('tinkers008', path, signature, role)
    e.update(repo=REPO, evidence_kind='complete_method',
             url=f'https://github.com/{REPO}/blob/{PIN}/{path}#L{e["line"]}-L{e["end_line"]}')
    return e

def statement(short, first, last, role):
    path = copy(short)
    raw = (DEST/path).read_bytes()
    text = '\n'.join(raw.decode().splitlines()[first-1:last])
    return dict(repo=REPO, revision=PIN, path=path,
        source_local=str((DEST/path).relative_to(WORKSPACE)), source_sha256=sha(raw),
        line=first, end_line=last, excerpt=text, snippet_sha256=sha(text.encode()),
        role=role, evidence_kind='configuration_statement_not_complete_method',
        url=f'https://github.com/{REPO}/blob/{PIN}/{path}#L{first}-L{last}')

# Vanilla support has a versioned local artifact/hash, not a fabricated Git commit.
JAR = Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
VROOT = HERE/'sources/vanilla-forge-1.20.1-47.4.10-008'
VROOT.mkdir(parents=True, exist_ok=True)
VANILLA = []
def vanilla(path, first, last, name):
    with zipfile.ZipFile(JAR) as z:
        raw = z.read(path)
    target = VROOT/path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    text = '\n'.join(raw.decode().splitlines()[first-1:last])
    e = dict(repo='Minecraft vanilla via local Forge mapped source artifact',
        revision='1.20.1-47.4.10_mapped_official_1.20.1; artifact hash, not Git commit',
        path=path, source_local=str(target.relative_to(WORKSPACE)), source_sha256=sha(raw),
        line=first, end_line=last, method=name, excerpt=text, snippet_sha256=sha(text.encode()),
        url=None, url_limitation='Local source artifact only; no invented official GitHub blob URL.',
        source_artifact=str(JAR), evidence_kind='complete_method_local_vanilla_support_only',
        role='Parent lifecycle boundary, zero independent credit')
    VANILLA.append(e)
    return e

pickup_support = [
    vanilla('net/minecraft/world/entity/projectile/ThrownTrident.java',165,169,'playerTouch'),
    vanilla('net/minecraft/world/entity/projectile/ThrownTrident.java',94,96,'getPickupItem'),
    vanilla('net/minecraft/world/entity/projectile/AbstractArrow.java',507,515,'playerTouch'),
    vanilla('net/minecraft/world/entity/projectile/Projectile.java',38,44,'setOwner'),
    vanilla('net/minecraft/world/entity/projectile/Projectile.java',47,56,'getOwner'),
    vanilla('net/minecraft/world/entity/projectile/Projectile.java',74,76,'ownedBy')]

throw = [m('tools/entity/ThrownTool', signature, role) for signature,role in [
    ('private boolean addToInventory(', 'Delayed original-slot reconciliation; successful inventory insertion'),
    ('protected boolean tryPickup(', 'Pickup-mode dispatch'),
    ('public ThrownTool(Level level,', 'Copy single item and establish projectile owner'),
    ('public void addAdditionalSaveData(', 'Save original slot and separate task state'),
    ('public void readAdditionalSaveData(', 'Restore original slot with explicit absent sentinel'),
    ('public void tickDespawn(', 'Pickup/loyalty-dependent expiry, measured in calls not wall clock'),
    ('protected void onBelowWorld(', 'Loyalty recovery branch, not blanket discard')]]
throw += [m('library/tools/item/ranged/ModifiableBowItem','public void releaseUsing(',
             'Whole actual ballista producer: identity-based original-slot capture, consume ammo, create and spawn projectile'),
          m('library/modifiers/hook/ranged/BowAmmoModifierHook',
            'static ItemStack consumeAmmo(IToolStackView tool, ItemStack bow, LivingEntity living, @Nullable Player player, @Nullable Predicate<ItemStack> predicate, int projectilesDesired)',
            'Whole actual consumption path, including creative and modifier inventory branches')]

returning = [m('shared/effect/ReturningEffect', signature, role) for signature,role in [
    ('private void onEffectAdded(', 'First effect addition snapshots position and dimension; refresh retains original anchor'),
    ('public boolean isDurationEffectTick(', 'Terminal duration gate'),
    ('public void applyEffectTick(', 'Dimension-validated deferred return consumer'),
    ('public ReturningEffect()', 'Actual Added event listener registration')]]
returning += [m('gadgets/block/FoodCakeBlock',signature,role) for signature,role in [
    ('public InteractionResult use(', 'Actual cake interaction entry'),
    ('private InteractionResult eatSlice(', 'ADD mode extends matching-level duration before addEffect'),
    ('private boolean hasAllEffects(', 'Complete alternate-mode guard, support only')]]
returning += [m('shared/TinkerFood','public static FoodProperties getCake(', 'Actual ENDER food selection'),
    statement('shared/TinkerFood',25,25,'Actual returning effect food declaration, 600 ticks; not a complete method'),
    statement('gadgets/TinkerGadgets',89,98,'Actual cake registration uses ADD for ENDER; static initializer, not a method'),
    m('library/events/teleport/ReturningTeleportEvent','public ReturningTeleportEvent(', 'Cancelable return event constructor'),
    m('library/utils/TeleportHelper','public static boolean tryTeleport(', 'Event cancellation gate before teleport'),
    m('library/utils/TeleportHelper','private static void spawnParticles(', 'Supporting visual helper, no extra credit'),
    m('library/tools/capability/PersistentDataCapability','public static ModDataNBT getOrWarn(', 'Actual persistent data lookup or detached fallback'),
    m('library/tools/capability/PersistentDataCapability','private static void playerClone(', 'Clone preserves old persistent NBT; does not clear return key'),
    m('library/tools/nbt/ModDataNBT','public void put(ResourceLocation name, Tag nbt)', 'Anchor compound storage')]

dodge = [m('tools/modules/armor/TeleportDodgeModule','public float modifyDamageTaken(', 'Teleport-success-gated damage suppression and cooldown'),
    m('library/utils/TeleportHelper','public static boolean randomNearbyTeleport(LivingEntity living, ITeleportEventFactory factory, int diameter, int chances)', 'Whole bounded event/collision retry loop'),
    m('tools/logic/ToolEvents','static void livingHurt(', 'Whole LOW priority combat event producer and cancellation consumer'),
    m('library/modifiers/hook/armor/ModifyDamageModifierHook','static float modifyDamageTaken(', 'Equipment dispatcher short-circuits nonpositive amount'),
    m('tools/modules/armor/CounterModule','static float getLevel(', 'Effective level with shield blocking adjustment'),
    m('tools/modules/armor/CounterModule','static boolean isBlocking(', 'Whole five-tick blocking qualification'),
    m('library/events/teleport/EnderdodgingTeleportEvent','public EnderdodgingTeleportEvent(Entity entity, double targetX, double targetY, double targetZ, ModifierEntry modifier)', 'Actual cancelable event subtype'),
    statement('tools/data/ModifierProvider',1089,1095,'Actual two damage-source configurations; one lifecycle, zero extra for parameter variants')]

ROWS=[]
def add(key, evidence, observation, application, limits, nearest, distinction, support=None):
    row=dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-008-'+key,chain_id=key,batch='008',
       status='reviewed',decision='reviewed_valid_pending_carson',credit=0,proposed_credit=1,
       final_count_owner='Carson',reviewed_at=NOW,evidence=evidence,observation=observation,
       application=application,limits=limits,dedup_key=REPO+':'+key,
       semantic_dedup=dict(nearest_existing_families=nearest,independent_state_and_consumer=distinction,
                          supporting_methods_increment=0,mirrored_or_version_increment=0),
       external_runtime_tested=False,downloaded_code_executed=False)
    if support:row['local_vanilla_support']=support
    ROWS.append(row)

add('thrown-tool-owner-gated-original-slot-reconciliation',throw,
    '真实ballista释放先用对象身份找到弹药原槽，再consumeAmmo；ThrownTool复制单件并setOwner，原槽随实体NBT保存。稍后拾取先经继承的ThrownTrident.playerTouch：属于当前玩家或getOwner()==null才进入父类。tryPickup再按pickup模式处理；原槽空则放回，可合并且ItemStack.isSameItemSameTags才grow，否则回退Inventory.add。只有addToInventory返回true，AbstractArrow.playerTouch才take并discard弹体。原槽已被新物品占用时不覆盖。',
    '横扫延后记录的身份不能只是一处可复用slot：产生时绑定实体/持有者，消费时重验目的地当前状态；成功消费之后才移除待处理载体，失败要保留或明确终止。这里只提出一个归还生命周期；弹体任务、父类拾取、NBT与不同pickup分支均为支持，不拆分计数。',
    '并非严格只限原主人：父类明确允许getOwner()==null；getOwner缓存移除后仅在当前ServerLevel按UUID查找，原主人离开维度等情形可能返回null。原槽写入和discard非事务，异常/自定义Inventory.add副作用无回滚；失败时不discard。originalSlot读NBT只检查数值类型，未校验范围。tickDespawn的1200/6000是该方法累计调用，loyalty/noDespawn可能无界，不是短TTL，也不能作为成功伤害回执。原版父类仅本机Forge源Jar版本/hash支持，没有伪造固定Git提交或URL。',
    ['main 881b0bde6801d9e29840: MessageMagnetEquip原槽记录先清再交换',
     'main 8ccccc08c8be7c7ab315 / reviewed beefd446a6b0bdf43e51: ThrownTool.tick调度支持',
     'main ThrownShuriken: hurt结果驱动退款/移除'],
    'This unit is a delayed projectile-owned payload return that reconciles an occupied destination and commits removal after insertion; not a slot-swap request or the already counted projectile scheduler.',pickup_support)

add('returning-first-anchor-refresh-and-dimension-terminal-gate',returning,
    '实际ENDER蛋糕注册ADD模式，600tick返程effect；再次食用同等级时新duration加旧duration。ReturningEffect的Added监听只在server且oldEffectInstance==null时保存当前位置BlockPos和dimension；所以续期保持最初anchor。duration==1时读取持久化compound，tryParse维度且必须等于当前维度才构造ReturningTeleportEvent；TeleportHelper先post可取消事件，未取消才传送。没有在消费后删除anchor。',
    '可借鉴区分第一次登记与刷新：延长有效期不应悄悄改写产生时的事实快照。延迟消费前要验证记录所属维度；来源记录存在、到达时钟边界、允许执行与操作成功是不同状态。此链将维度不匹配和取消视为明确不执行，不能让END读当前世界后冒用旧坐标。',
    '不是伤害回执；duration==1精确触发不适合直接照搬跨tick短TTL。传送返回值被忽略，无重试或成功ACK；事件可改坐标，未验证修改后目的地，原位置只保存整数方块坐标。applyEffectTick未单独判server，数据生产在server，cap又可能sync到client，不能凭此断言永远仅服务端执行。取消/提早移除不清anchor；clone会保留NBT，未见generation/目标UUID/一次消费标记。公共传送helper只计支持；配置声明没有冒充完整datagen方法。',
    ['batch007: self-destruct terminal effect and explicit cancel',
     'batch006: bleeding refresh-phase behavior', 'main teleport/request and dimension cleanup families'],
    'Unique state is first-add position+dimension retained across ADD refresh, consumed by same-dimension terminal return; explosion terminal clock and generic teleport helpers are not proposed again.')

add('enderdodge-teleport-success-before-cooldown-and-hurt-cancel',dodge,
    '实际enderdodging两种damage predicate共用一个模块：若无enderference、目标/来源predicate满足且随机通过，执行最多16次随机附近传送尝试。每次先发可取消事件，必须未取消且living.randomTeleport返回true才算成功；仅成功后加200tick enderference、按amount损耗工具并返回0。所有尝试失败则返回原amount且不设置冷却。MODIFY_HURT dispatcher对<=0短路，真实livingHurt收到0后setAmount并取消该伤害事件。',
    '这是伤害事实的反例边界：攻击事件/传送尝试不能冒充成功伤害；后续modifier可能已把伤害归零并取消。副作用与冷却应基于实际操作返回值，横扫回执应在最终有效伤害路径记录，并把防御拦截与已经损血分开；不将两个概率配置或16次尝试拆成条目。',
    '本链是同步防御门控加效果冷却，不是跨tick队列；相关性供Carson保守审定。成功传送后后续工具损耗若异常没有回滚，其他监听之后改事件也不能撤销已传送/冷却。该模块自身不应用condition字段，完整外部条件包装未审，不声称所有配置条件已证明；端检查依赖事件入口，randomNearbyTeleport客户端直接返回true不能单独当服务端成功证明。200tick冷却为本地Java配置声明，不声称已读生成JSON/运行验证。',
    ['batch006: projectile impact reflection cancellation', 'main generic cooldown and successful-operation gating families'],
    'Distinct concrete combat lifecycle couples bounded cancelable teleport success to damage-event suppression and a defender-owned interference cooldown; reflection, generic retry helpers and parameter variants remain zero additional credit.')

MAIN=WORKSPACE/'docs/cod4/audit-20261022/sweep-receipt-research'
comparison=[]
for name in ['accepted.jsonl','reviewed.jsonl']:
    comparison.extend(json.loads(x) for x in (MAIN/name).read_text().splitlines() if x.strip())
for p in DOCS.glob('batch-00[1-7].json'):
    comparison.extend(json.loads(p.read_text())['entries'])
for r in ROWS:
    matches=[d for d in comparison if (d.get('repo'),d.get('revision'),d.get('path'),d.get('line')) ==
             (r['repo'],r['revision'],r['path'],r['line'])]
    r['semantic_dedup']['exact_primary_preexisting']=bool(matches)
    assert not matches,r['candidate_id']

def dump(name,o):
    (DOCS/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
common=dict(schema_version=1,reviewed_at=NOW,credit_applied=0,final_count_owner='Carson',
    source_revision=PIN,no_compilation=True,no_runtime_tests=True,upstream_code_executed=False)
dump('batch-008.json',dict(common,proposed_valid=len(ROWS),entries=ROWS))
(DOCS/'reviewed-008.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ROWS))
dump('source-index-008.json',dict(repo=REPO,revision=PIN,official_source_provenance=META,
    provenance_reverified_online=False,files=list(FILES.values()),network_requests=0,
    local_vanilla_artifact=dict(path=str(JAR),sha256=sha(JAR.read_bytes()),support_only=True,
        no_git_commit_claimed=True,methods=VANILLA)))
errors=[];unique={}
for r in ROWS:
    for e in r['evidence']+r.get('local_vanilla_support',[]):
        raw=(WORKSPACE/e['source_local']).read_bytes()
        text='\n'.join(raw.decode().splitlines()[e['line']-1:e['end_line']])
        if sha(raw)!=e['source_sha256'] or text!=e['excerpt'] or sha(text.encode())!=e['snippet_sha256']:
            errors.append([r['candidate_id'],e['path']])
        unique[(e['source_local'],e['line'],e['end_line'])]=e
assert not errors,errors
dump('validation-008.json',dict(common,validation_kind='Evidence text/hash/range integrity only, not compilation or gameplay',
    errors=errors,unique_method_ranges=sum(e['evidence_kind'].startswith('complete_method') for e in unique.values()),
    configuration_statement_ranges=sum(e['evidence_kind'].startswith('configuration') for e in unique.values()),
    pending_candidates=len(ROWS),applied_credit=0,method_count_is_not_credit=True,
    main_ledger_read_only_snapshots={name:sha((MAIN/name).read_bytes()) for name in ['accepted.jsonl','reviewed.jsonl','protocol.json']},
    production_qa_todo_written=False,network_requests=0))
print(json.dumps(dict(candidates=len(ROWS),credit=0,evidence_ranges=len(unique),files=len(FILES),errors=errors)))
