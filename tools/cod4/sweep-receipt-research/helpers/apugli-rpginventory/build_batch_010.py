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
DEST = HERE / 'sources/SlimeKnights__TinkersConstruct-010'
NOW = datetime.now(timezone.utc).isoformat()
META = json.loads((ORIGIN/'source.json').read_text())
TREE = json.loads((ORIGIN/'tree.json').read_text())
assert META['repo'] == REPO and META['sha'] == TREE['sha'] == PIN and not TREE['truncated']
BLOBS = {x['path']: x['sha'] for x in TREE['tree'] if x['type'] == 'blob'}
DEST.mkdir(parents=True, exist_ok=True)
for name in ['source.json', 'tree.json']:
    (DEST/name).write_bytes((ORIGIN/name).read_bytes())
ROOTS['tinkers010'] = DEST
PINS['tinkers010'] = PIN
METADATA['tinkers010'] = DEST/'source.json'
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
    e = method('tinkers010', path, signature, role)
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
VROOT = HERE/'sources/vanilla-forge-1.20.1-47.4.10-010'
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

fishing_parent = [vanilla('net/minecraft/world/entity/projectile/FishingHook.java',a,b,name) for a,b,name in [
    (131,227,'tick'),(229,240,'shouldStopFishing'),(251,257,'onHitEntity'),
    (264,267,'setHookedEntity'),(402,450,'retrieve'),(472,475,'remove'),
    (481,484,'setOwner'),(486,492,'updateOwnerInfo'),(495,498,'getPlayerOwner')]]
owner_parent = [vanilla('net/minecraft/world/entity/projectile/Projectile.java',a,b,name) for a,b,name in [
    (38,44,'setOwner'),(47,56,'getOwner'),(135,147,'onHit')]]

def methods(short, pairs):
    return [m(short,s,r) for s,r in pairs]

fishing = methods('tools/entity/CombatFishingHook',[
    ('protected void pullEntity(', 'Deferred actual attack; hurt result gates launcher callback and health-delta read'),
    ('public CombatFishingHook(Player player,', 'Actual launch owner and velocity initialization'),
    ('protected void onHitEntity(', 'Initial attachment captures impact velocity; not damage success'),
    ('public float getDamage(', 'Consume captured impact speed while attached'),
    ('private void damageRod(', 'Resolve current eligible held rod for durability'),
    ('protected boolean canHitEntity(', 'Actual collectable extension; support branch only'),
    ('private void pullGrapple(', 'Drill/grapple motion branch; not an extra candidate'),
    ('public int retrieve(', 'Delegate actual pull to parent and clamp tool damage, not attack result'),
    ('protected void onHitBlock(', 'Record wall state for grappling lifecycle'),
    ('private boolean shouldFall(', 'World collision invalidates wall attachment'),
    ('private void startFalling(', 'Clear wall state and wall age'),
    ('public void move(', 'Revalidate wall attachment when externally moved'),
    ('public void tick(', 'Parent lifecycle plus server wall 1200-tick expiry'),
    ('public void addAdditionalSaveData(', 'Only material custom save; parent serialization separate'),
    ('public void readAdditionalSaveData(', 'Only material custom load; no claimed full combat snapshot persistence')])
fishing += methods('tools/modules/interaction/FishingModule',[
    ('public InteractionResult onToolUse(', 'Actual server cast/retrieve producer; client swing is support only'),
    ('public void onUnequip(', 'Discard hook when replacement missing or modifier list differs'),
    ('public void onEquipmentChange(', 'Offhand fishing invalidation after main-hand gains casting ability')])
fishing += methods('tools/logic/EquipmentChangeWatcher',[
    ('private static void onEquipmentChange(', 'Actual server event source for equipment lifecycle'),
    ('private static void runModifierHooks(', 'Unequip old, equip new, notify other-slot modifiers')])
fishing += methods('library/tools/helper/ToolAttackUtil',[
    ('public static LivingEntity getLivingEntity(', 'Living target identity including PartEntity parent'),
    ('public static AttributeInstance disableKnockback(', 'Temporary knockback suppression'),
    ('public static void enableKnockback(', 'Restore suppression; caller lacks finally')])
fishing += [m('shared/TinkerEffects','static boolean needsEnderferenceOverride(@Nullable Entity entity)', 'Exact source-type override predicate'),
    statement('tools/data/ModifierProvider',913,913,'Actual fishing modifier module binding; declaration only')]

fluid = methods('tools/entity/FluidEffectProjectile',[
    ('protected void onHitEntity(', 'Deferred impact consumer; shrink by recipe return and discard only when empty'),
    ('public FluidEffectProjectile(Level level, BlockPos cannon,', 'Actual cannon source coordinate plus fluid payload initialization'),
    ('private IItemHandlerModifiable getCannonInventory(', 'Re-resolve loaded source position/current capability, not original block entity identity'),
    ('private FluidEffectContext.Builder buildContext(', 'Read current source slot copy at impact and resolve owner'),
    ('private void updateCannonStack(', 'Re-resolve source handler and overwrite current slot with context result'),
    ('public void tick(', 'Native projectile movement/impact cancellation and height cleanup'),
    ('private static Stream<Direction> orderByNearest(', 'Ordering for remaining fluid across block neighbors; not separate credit'),
    ('protected void onHitBlock(', 'Remaining fluid/block continuation and terminal discard; same lifecycle'),
    ('protected void addAdditionalSaveData(', 'Persist cannon coordinate and payload, not original block entity generation'),
    ('protected void readAdditionalSaveData(', 'Restore optional cannon source and payload')])
fluid += methods('smeltery/block/FluidCannonBlock',[
    ('public void neighborChanged(', 'Rising redstone schedules actual block tick four ticks later'),
    ('public void tick(', 'Scheduled tick resolves current cannon block entity and calls shoot')])
fluid += [m('smeltery/block/entity/FluidCannonBlockEntity','public void shoot(', 'Actual spawn producer and source tank debit; direct-block branch remains same chain')]
fluid += methods('library/modifiers/fluid/FluidEffects',[
    ('public int getAmount(', 'Fluid recipe unit amount'),
    ('public boolean hasEffects(', 'Actual producer eligibility'),
    ('public boolean hasBlockEffects(', 'Block effect eligibility'),
    ('public boolean hasEntityEffects(', 'Entity effect eligibility'),
    ('private <C extends FluidEffectContext> int apply(', 'All effects share scale; use maximum returned scale, not sum or damage receipt'),
    ('public int applyToBlock(', 'Block application delegates same fluid-budget aggregator'),
    ('public int applyToEntity(', 'Entity application delegates same fluid-budget aggregator')])
fluid += [m('library/modifiers/fluid/entity/DamageFluidEffect','public float apply(', 'Damage branch returns positive budget scale only on helper hurt true'),
    m('library/modifiers/fluid/general/DropItemFluidEffect','public float apply(', 'Independent nondamage outcome can make aggregate budget positive'),
    m('library/tools/helper/ToolAttackUtil','public static boolean attackEntitySecondary(', 'Actual attack wrapper; zero additional credit'),
    m('library/tools/helper/ToolAttackUtil','public static boolean hurtNoInvulnerableTime(Entity target, @Nullable LivingEntity living,', 'Temporarily bypass/restore timers; already main accepted support'),
    m('library/tools/helper/ModifierUtil','public static void dropItem(Level level, double x,', 'Actual drop spawn ignores addFreshEntity boolean'),
    m('library/tools/helper/ModifierUtil','public static void dropItem(Level level, Vec3 location,', 'Whole position wrapper; zero credit'),
    m('library/tools/helper/ModifierUtil','public static LivingEntity asLiving(', 'Owner/target nullable instanceof conversion'),
    m('library/tools/helper/ModifierUtil','public static Player asPlayer(', 'Player nullable instanceof conversion')]
fluid += methods('library/modifiers/fluid/FluidEffectContext',[
    ('public DamageSource createDamageSource(', 'Actual projectile/owner/generic fallback source'),
    ('private Entity(Level level,', 'Entity context holds actual target plus optional living target'),
    ('public static Builder builder(', 'Actual context creation'),
    ('public Builder user(@Nullable net.minecraft.world.entity.Entity entity)', 'Owner conversion'),
    ('public Builder user(@Nullable LivingEntity entity)', 'Set living owner and inferred player'),
    ('public Builder user(@Nullable LivingEntity entity,', 'Assign optional owner/player'),
    ('public Entity target(net.minecraft.world.entity.Entity target)', 'Convert actual collision target'),
    ('public Entity target(net.minecraft.world.entity.Entity target,', 'Build actual target context'),
    ('public Block block(', 'Build block context for same continuation chain'),
    ('private Block(Level level,', 'Whole block context constructor'),
    ('public Block withHitResult(', 'Neighbor context shares carried stack and owner'),
    ('public Vec3 getLocation() {', 'Whole block location getter used by drop effect')])
fluid += methods('library/modifiers/fluid/FluidEffectManager',[
    ('public FluidEffects find(', 'Resolve recipe on current manager state at impact'),
    ('protected void apply(', 'Reload replaces recipe list and clears cache')])
fluid += [m('shared/TinkerEffects','static boolean needsEnderferenceOverride(@Nullable LivingEntity living)', 'Damage branch current living target override predicate'),
    statement('tools/data/FluidEffectProvider',175,182,'Actual molten-clay damage+brick-drop recipe; complete configuration statement, not full provider method')]

ROWS=[]
def add(key,evidence,parents,observation,application,limits,nearest,distinction):
    row=dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-010-'+key,chain_id=key,batch='010',
        status='reviewed',decision='reviewed_valid_pending_carson',credit=0,proposed_credit=1,
        final_count_owner='Carson',reviewed_at=NOW,observation=observation,application=application,
        limits=limits,evidence=evidence,local_vanilla_support=parents,
        semantic_dedup=dict(nearest_existing_families=nearest,independent_state_and_consumer=distinction,
            supporting_methods_increment=0,mirrored_or_version_increment=0),
        dedup_key=REPO+':'+key,downloaded_code_executed=False,external_runtime_tested=False)
    ROWS.append(row)

add('hooked-target-captured-impact-to-later-reel-damage',fishing,fishing_parent+owner_parent,
    '真实fishing模块server cast创建CombatFishingHook，原版setOwner按UUID/缓存绑定玩家并登记player.fishing。碰撞仅挂住实体、记录impactVelocity和损耗当前杆；稍后玩家收线才由父retrieve调用pullEntity。后者重取owner，用已捕获速度算伤害，实际target.hurt为true后才在服务端触发LAUNCHER_HIT，并给Living目标传oldHealth-currentHealth；非Living以名义damage代替。父tick检查玩家存活/未移除/任一手可抛竿/距离<=32，并在挂钩状态检查目标未移除且同维度；正常服务端retrieve最终discard并清player.fishing。换装缺replacement或modifier列表不同即discard；offhand场景主手新获得抛竿能力也清理。',
    '借鉴把先前碰撞准备态与稍后真实伤害事实分开：准备、耐久损耗、收线返回码都不应冒充成功伤害。回执在实际hurt路径产生，并保存target身份、当时血量差和攻击代次；延迟消费前还需来源/目标生命周期校验。挂住到收线可以跨多个tick，因此不能用now==产生tick否决已发生事实。当前装备重取的漏洞边界提示需区分快照来源和消费时持有物。',
    '不是现成短TTL队列：仅着地/贴墙有1200tick计龄，空中挂住没有本实现独立绝对deadline；目标同维度检查在父tick，不是pullEntity内原子再验。hurt true仍可得到0血差，setLastHurtMob及拉拽在伤害成功判断外；retrieve正数代表杆损耗且可能钳制，不能证明损血。伤害后modifiers来自当前可抛竿的手持物，换成相同modifier列表的新杆不触发unequip清理；未绑定原ItemStack代次。正常路径discard是消费边界，不能承诺重入异常也exactly-once；临时knockback恢复无finally。自定义save仅额外存material，不能声称impactVelocity/power都持久化。外部Mantle CombatHelper.damageSource和客户端OffhandCooldownTracker实现未随本固定树审阅，不据此承诺来源序列/客户端时序；其余具体modifier回调各自业务不作为本链新增信用。',
    ['main ThrownShuriken命中成功退款/移除','batch008 ThrownTool回收原槽、Returning跨维度锚点',
     'batch007 equipment watcher支持不计','main ProjectileFuse/Gravity发射计划'],
    'Target reference and impact-speed snapshot survive initial collision until later user-triggered reel; actual damage and health-delta emission occur at that later consume, with rod/owner cleanup. Not another projectile spawn, slot refund or equipment watcher unit.')

add('cannon-payload-flight-current-source-and-remaining-fluid-consumer',fluid,owner_parent,
    '真实FluidCannonBlock在红石上升沿scheduleTick4，再由当前BlockEntity.shoot发射。弹体携独立FluidStack预算和炮BlockPos，来源槽物品并未在发射时快照；实际命中时重新解析当前recipe、当前loaded坐标的ITEM_HANDLER和slot0副本，执行效果后consumed>0才把context.stack写回再次重取的handler。全部效果使用同一scale，消耗取各效果返回scale最大值而非相加。实体命中后按消耗扣载荷，耗空discard，否则保留继续飞；方块分支同一剩余预算可转邻块或消失。实际moltenClay配方同时有DamageFluidEffect与DropItemFluidEffect：前者hurt false返回0，但后者可返回正数，故正消耗不等于成功伤害。',
    '借鉴把发射时有限载荷、延后执行结果和来源回写分开。横扫消费成功伤害回执应采用专门damage事实，而非通用任务资源消耗/特效结果；组合效果应有清晰一次扣账策略，不能把多个支持分支算多次回执。来源只有坐标时须防旧载荷落到替换后的新对象：建议回执记录来源UUID或代次、目标UUID和维度、短TTL，再以一次消费键结算，而不在消费时把当前装备/当前方块误当原来源。',
    '本链不是防重样板：getCannonInventory仅校验坐标loaded与当前capability可修改，没有原方块实体类型/实例代次、源dimension快照或slot compare-and-set；同步回调更改来源后仍可能回写当前槽，静态风险不冒充运行复现。damage helper hurt布尔不保证正健康差；dropItem忽略spawn布尔，聚合正数也非掉落接纳凭证。击退先于recipe/damage成功；cancel projectile impact会跳过onHit，但不能据此承诺所有运动副作用取消。没有此类显式绝对age TTL/已命中target UUID账本；剩余量可多次消费，不等于一个攻击严格一次。发射addFreshEntity返回忽略，源tank仍扣量。reload时recipe cache更新，弹体不是发射配方快照。已被主审排除的同步BlockInteract/PlaceBlock效果、recipe的各分支、纯缓存、scheduleTick包装及getter均不额外计；若Carson认为资源载荷与伤害回执相关性仍不足，按0排除而不拆分凑数。',
    ['reviewed BlockInteractFluidEffect:同步消耗工具耐久，已排除','reviewed PlaceBlockFluidEffect:同步放方块，已排除',
     'main ToolAttackUtil.hurtNoInvulnerableTime:已有支持','batch008 ThrownTool原槽回收'],
    'Actual gameplay deferred fluid payload owns a remaining budget across flight and impact and rebinds source inventory at consume; damage and nondamage receipts aggregate under one debit. Not standalone generic cache, synchronous block placement or another per-effect template.')

MAIN=WORKSPACE/'docs/cod4/audit-20261022/sweep-receipt-research'
comparison=[]
for name in ['accepted.jsonl','reviewed.jsonl']:
    comparison.extend(json.loads(x) for x in (MAIN/name).read_text().splitlines() if x.strip())
for p in sorted(DOCS.glob('batch-00[1-9].json')):
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
dump('batch-010.json',dict(common,proposed_valid=len(ROWS),entries=ROWS))
(DOCS/'reviewed-010.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ROWS))
dump('source-index-010.json',dict(repo=REPO,revision=PIN,official_source_provenance=META,
    provenance_reverified_online=False,files=list(FILES.values()),network_requests=0,
    local_vanilla_artifact=dict(path=str(JAR),sha256=sha(JAR.read_bytes()),support_only=True,
        no_git_commit_claimed=True,methods=VANILLA)))
errors=[];unique={}
for r in ROWS:
    for e in r['evidence']+r['local_vanilla_support']:
        raw=(WORKSPACE/e['source_local']).read_bytes()
        text='\n'.join(raw.decode().splitlines()[e['line']-1:e['end_line']])
        if sha(raw)!=e['source_sha256'] or text!=e['excerpt'] or sha(text.encode())!=e['snippet_sha256']:
            errors.append([r['candidate_id'],e['path']])
        unique[(e['source_local'],e['line'],e['end_line'])]=e
assert not errors,errors
dump('validation-010.json',dict(common,validation_kind='Evidence text/hash/range integrity only, not compilation or gameplay',
    errors=errors,unique_method_ranges=sum(e['evidence_kind'].startswith('complete_method') for e in unique.values()),
    configuration_statement_ranges=sum(e['evidence_kind'].startswith('configuration') for e in unique.values()),
    pending_candidates=len(ROWS),applied_credit=0,method_count_is_not_credit=True,
    main_ledger_read_only_snapshots={name:sha((MAIN/name).read_bytes()) for name in ['accepted.jsonl','reviewed.jsonl','protocol.json']},
    production_qa_todo_written=False,network_requests=0))
print(json.dumps(dict(candidates=len(ROWS),credit=0,evidence_ranges=len(unique),files=len(FILES),errors=errors)))

