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
DEST = HERE / 'sources/SlimeKnights__TinkersConstruct-011'
NOW = datetime.now(timezone.utc).isoformat()
META = json.loads((ORIGIN/'source.json').read_text())
TREE = json.loads((ORIGIN/'tree.json').read_text())
assert META['repo'] == REPO and META['sha'] == TREE['sha'] == PIN and not TREE['truncated']
BLOBS = {x['path']: x['sha'] for x in TREE['tree'] if x['type'] == 'blob'}
DEST.mkdir(parents=True, exist_ok=True)
for name in ['source.json', 'tree.json']:
    (DEST/name).write_bytes((ORIGIN/name).read_bytes())
ROOTS['tinkers011'] = DEST
PINS['tinkers011'] = PIN
METADATA['tinkers011'] = DEST/'source.json'
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
    e = method('tinkers011', path, signature, role)
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

def methods(short,pairs):
    return [m(short,s,r) for s,r in pairs]

ev = methods('smeltery/block/entity/module/EntityMeltingModule',[
    ('public boolean interactWithEntities(', 'Actual per-scan hurt fact, fluid side effect and aggregate receipt'),
    ('private Level getLevel(', 'Resolve actual parent world'),
    ('private DamageSource smelteryMagic(', 'Actual fire-immune target damage source'),
    ('private DamageSource smelteryHeat(', 'Actual normal target damage source'),
    ('private EntityMeltingRecipe findRecipe(', 'Per-controller last recipe lookup'),
    ('public static FluidStack getDefaultFluid(', 'Real fallback liquid soul output'),
    ('private boolean canMeltEntity(', 'Invulnerability/player creative/fire resistance gates')])
ev += methods('smeltery/block/entity/controller/SmelteryBlockEntity',[
    ('protected void heat(', 'tick12 scans before phase0 shared fuel consumption decision')])
ev += methods('smeltery/block/entity/controller/FoundryBlockEntity',[
    ('protected void heat(', 'Same entity-melt phase and shared module; mirror zero extra credit')])
ev += methods('smeltery/block/entity/controller/HeatingStructureBlockEntity',[
    ('protected void serverTick(', 'Server/formed structure gate and modulo20 phase lifetime'),
    ('private boolean canMeltEntities(', 'Fuel already present or simulate-only positive temperature; not tank capacity'),
    ('private ItemStack insertIntoInventory(', 'Real item collection callback; not independent credit'),
    ('public static <HAVE extends HeatingStructureBlockEntity, RET extends BlockEntity> BlockEntityTicker<RET> getTicker(', 'Server ticker only for matching block entity type')])
ev += [statement('smeltery/block/entity/controller/HeatingStructureBlockEntity',75,75,'Actual SERVER_TICKER lambda declaration, not a standalone method'),
    statement('smeltery/block/entity/controller/HeatingStructureBlockEntity',109,115,'Actual fuel/EntityMeltingModule suppliers; declarations, not complete methods'),
    statement('smeltery/TinkerSmeltery',338,338,'Actual smeltery block entity registration; no extra credit')]
ev += methods('smeltery/block/controller/SmelteryControllerBlock',[
    ('public BlockEntity newBlockEntity(', 'Actual world block creates the audited controller'),
    ('public <T extends BlockEntity> BlockEntityTicker<T> getTicker(', 'Actual block ticker wired to registered smeltery type')])
ev += methods('smeltery/block/entity/module/FuelModule',[
    ('protected MeltingFuel findRecipe(', 'Current liquid-fuel recipe lookup'),
    ('public boolean hasFuel(', 'Check stored fuel balance >0'),
    ('public void decreaseFuel(', 'Later phase3 debit clamps zero and marks parent changed'),
    ('protected int tryLiquidFuel(', 'Simulation reads temperature; execute drains and increments stored fuel')])
ev += methods('smeltery/block/entity/module/MultitankFuelModule',[
    ('public int findFuel(', 'Resolve one fuel tank and return actual temperature'),
    ('private int tryFuelPosition(', 'Current loaded capability attempt and handler tracking'),
    ('private Map<BlockPos,LazyOptional<IFluidHandler>> getTankHandlers(', 'Actual structure-supplied tank capabilities'),
    ('private void clearLastListener(', 'Clear old handler before storing new selected source')])
ev += [m('smeltery/block/entity/tank/SmelteryTank','public int fill(', 'Output reception can be zero/partial; returned amount not checked by receipt producer'),
    m('library/recipe/entitymelting/EntityMeltingRecipe','public boolean matches(EntityType<?> type)', 'Actual recipe entity eligibility'),
    m('library/recipe/entitymelting/EntityMeltingRecipe','public FluidStack getOutput(LivingEntity entity)', 'Actual default recipe produces independent fluid copy'),
    m('library/recipe/entitymelting/EntityMeltingRecipeCache','public static EntityMeltingRecipe findRecipe(', 'Specific real gameplay recipe resolver; zero independent cache credit'),
    statement('library/recipe/entitymelting/EntityMeltingRecipe',29,42,'Complete recipe LOADER and fields: damage FROM_ONE/default2; declarations only, generated getter not claimed hand-written method')]

ROWS=[]
def add(key,evidence,observation,application,limits,nearest,distinction,proposed):
    row=dict(evidence[0]);row.update(candidate_id='apugli-rpginventory-011-'+key,
        chain_id=key,batch='011',status='reviewed',
        decision='reviewed_valid_pending_carson' if proposed else 'reviewed_zero_credit',
        credit=0,proposed_credit=int(proposed),final_count_owner='Carson',reviewed_at=NOW,
        observation=observation,application=application,limits=limits,evidence=evidence,
        semantic_dedup=dict(nearest_existing_families=nearest,independent_state_and_consumer=distinction,
            supporting_methods_increment=0,mirrored_or_version_increment=0),
        dedup_key=REPO+':'+key,downloaded_code_executed=False,external_runtime_tested=False)
    ROWS.append(row)

add('periodic-smeltery-hurt-facts-aggregate-before-fuel-debit',ev,
    '实际SmelteryControllerBlock匹配已注册BE类型才返回服务端ticker；parent serverTick在结构存在/IN_STRUCTURE且server时heat，并tick=(tick+1)%20。Smeltery与Foundry都在tick12先遍历真实bounds内活实体，普通物品单独入库存；Living需通过黑名单、伤害免疫、creative invulnerable与火抗过滤。canMeltEntities对本次scan只求值一次：已有fuel或findFuel(false)温度>0，实际不检查产物tank空间。每个目标hurt为true后立即fill产液，并把本次local melted置true；scan结束控制器phase0据此findFuel(true)，phase3再decreaseFuel。多目标合为一次entityMelted布尔，不是逐目标队列。',
    '借鉴分清成功伤害事实、产物接纳回执与共享资源结算。扫描过/尝试hurt/已hurt/已fill/已扣燃料是不同事实；方天不能用任何资源侧正数或聚合标记替代来源明确的每目标damage receipt。一次phase内的local汇总可避免每个目标都拿燃料，但不能沿用到跨tick消费而丢掉目标身份、数量和一次消费键。真实per-controller modulo时钟也说明必须写清预约相位和状态持有者，不能把全局gameTime与局部tick混用。',
    '此实现实体伤害到布尔消费在同次heat调用，绝不冒称它验证了跨tick/短TTL队列；后续phase3是燃料余额扣减，不是再执行该hurt。melted在hurt true时置位而不查tank.fill返回，满槽或部分接纳仍为true且损失余液；hurt true也不是正健康差快照。canMeltEntities只simulate燃料，后续实际drain失败只记录日志仍增加fuel，所以不是原子事务。没有source/target UUID、重复攻击序号或逐目标去重；活目标每20tick可再次参与，是玩法重复而非exactly-once。Recipe damage getter为Lombok生成，仅记录字段声明，不虚构源码方法；EntityIngredient/外部Mantle recipe enumeration及Forge drain实现未独立审阅，不把通用cache/底层库算额外链。Smeltery和Foundry共享模块/phase，不拆成2项；若主审认为同步damage事实与当前延后消费主题相关性不足，请整条0排除。',
    ['batch010 流体炮发射载荷/命中后残量预算','batch009 前次受击效果窗口',
     'main general damage fact/refund families'],
    'Actual controller phase owns per-scan aggregate damage receipt used for shared fuel acquisition, with separately unchecked output acceptance and later phase debit. One smeltery/foundry lifecycle, not recipe cache or fluid-projectile template.',True)

spit = methods('tools/modules/interaction/SpittingModule',[
    ('private void spit(', 'Actual multishot payload producer uses already-audited FluidEffectProjectile'),
    ('public InteractionResult onToolUse(', 'Held charging entry'),
    ('public void onStoppedUsing(', 'Held server release invokes same producer'),
    ('public boolean startInteract(', 'Armor charging records cosmetic finishTime'),
    ('public void stopInteract(', 'Release invokes same producer; removes cosmetic key'),
    ('public void onInventoryTick(', 'Particle end timer only; not actual deferred attack consumer')])
add('spitting-is-existing-charge-and-fluid-payload-support',spit,
    '完整读spit及手持/盔甲入口：先求amount/shots，逐弹体复制fluid、modifier与launch回调，最后统一扣amount*shots和耐久；onStoppedUsing/stopInteract调用同一spit。inventoryTick的finishTime仅控制声音粒子并删key，不执行攻击。',
    '防止把看似到期的粒子计时器错当实际伤害兑现或另一个有效调度实现。',
    '已有按键蓄力框架与010流体弹生命周期的另一发射入口；此处未继续审TANK_HELPER底层，因为已足以按同链排除，不能声称本模块整个依赖图都完成。',
    ['main InteractionHandler armor charge','batch010 fluid projectile'],
    'Duplicate actual consumer; no new receipt state machine.',False)
bonk = methods('tools/modules/interaction/sling/SlingKnockbackModule',[
    ('public void sling(', 'Temporary IS_BONKING scope wraps synchronous performAttack; didBonk set before call'),
    ('public float beforeMeleeHit(', 'Flag suppresses knockback during same attack'),
    ('public float getMeleeDamage(', 'Flag changes damage within same attack'),
    ('public InteractionResult onToolUse(', 'Charging entry alone not a new consumer')])
add('bonking-synchronous-flag-not-independent-receipt',bonk,
    'sling在performAttack前置didBonk=true和IS_BONKING，调用后remove；修改伤害和knockback读取同一bool。performAttack返回被忽略，动画/回调可因尝试攻击或force>0而触发，不是实际血差回执。',
    '只保留attempt/result差别及同步flag无finally的阅读观察，不把这种上下文布尔当延迟队列。',
    '未为此排除项展开既有performAttack201行支持或sling全部上游：同步调用与既有伤害尝试范式足以排除，未读部分零信用。',
    ['batch006 dynamic looting slot synchronous attack scope','main successful damage versus unconditional attack presentation'],
    'Synchronous flag only, no independently deferred gameplay receipt.',False)
bounce = methods('library/utils/SlimeBounceHandler',[
    ('private static void onLivingTick(', 'Existing accepted006 actual bounce consumer'),
    ('public static void addBounceHandler(LivingEntity entity, @Nullable Vec3 bounce)', 'Existing accepted006 exact next entity tick producer'),
    ('public BounceInfo(', 'Existing state constructor'),
    ('private static void serverStopping(', 'Existing shutdown cleanup')])
add('bounce-already-admitted-006-do-not-recredit',bounce,
    '复读identity map保存bounceTick=entity.tickCount+1，精确相等消费后置null/0，落地/静止5tick宽限以及serverStopping清空。主accepted已明确admit此完整链。',
    '作为真实已研究断点防重；原等号错过风险已有记录，不换主方法或支持方法重计。',
    '不是新候选；001-010和主账语义对比确认与006完全同链。',
    ['apugli-rpginventory batch006 SlimeBounceHandler'],
    'Exact already-admitted lifecycle; zero incremental credit.',False)

MAIN=WORKSPACE/'docs/cod4/audit-20261022/sweep-receipt-research'
comparison=[]
for name in ['accepted.jsonl','reviewed.jsonl']:
    comparison.extend(json.loads(x) for x in (MAIN/name).read_text().splitlines() if x.strip())
for p in sorted(DOCS.glob('batch-*.json')):
    if p.name!='batch-011.json':comparison.extend(json.loads(p.read_text())['entries'])
for r in ROWS:
    matches=[d for d in comparison if (d.get('repo'),d.get('revision'),d.get('path'),d.get('line')) ==
        (r['repo'],r['revision'],r['path'],r['line'])]
    r['semantic_dedup']['exact_primary_preexisting']=bool(matches)
    if r['proposed_credit']:assert not matches,r['candidate_id']

def dump(name,o):
    (DOCS/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
proposed=[r for r in ROWS if r['proposed_credit']];excluded=[r for r in ROWS if not r['proposed_credit']]
common=dict(schema_version=1,reviewed_at=NOW,credit_applied=0,final_count_owner='Carson',
    source_revision=PIN,no_compilation=True,no_runtime_tests=True,upstream_code_executed=False)
dump('batch-011.json',dict(common,proposed_valid=len(proposed),entries=proposed))
dump('excluded-011.json',dict(common,proposed_valid=0,entries=excluded))
(DOCS/'reviewed-011.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ROWS))
dump('source-index-011.json',dict(repo=REPO,revision=PIN,official_source_provenance=META,
    provenance_reverified_online=False,files=list(FILES.values()),network_requests=0))
errors=[];unique={}
for r in ROWS:
    for e in r['evidence']:
        raw=(WORKSPACE/e['source_local']).read_bytes()
        text='\n'.join(raw.decode().splitlines()[e['line']-1:e['end_line']])
        if sha(raw)!=e['source_sha256'] or text!=e['excerpt'] or sha(text.encode())!=e['snippet_sha256']:
            errors.append([r['candidate_id'],e['path']])
        unique[(e['source_local'],e['line'],e['end_line'])]=e
assert not errors,errors
dump('validation-011.json',dict(common,validation_kind='Evidence text/hash/range integrity only, not compilation or gameplay',
    errors=errors,unique_method_ranges=sum(e['evidence_kind']=='complete_method' for e in unique.values()),
    configuration_statement_ranges=sum(e['evidence_kind'].startswith('configuration') for e in unique.values()),
    pending_candidates=len(proposed),excluded_groups=len(excluded),applied_credit=0,method_count_is_not_credit=True,
    main_ledger_read_only_snapshots={name:sha((MAIN/name).read_bytes()) for name in ['accepted.jsonl','reviewed.jsonl','protocol.json']},
    production_qa_todo_written=False,network_requests=0))
print(json.dumps(dict(candidates=len(proposed),excluded=len(excluded),credit=0,evidence_ranges=len(unique),files=len(FILES),errors=errors)))

