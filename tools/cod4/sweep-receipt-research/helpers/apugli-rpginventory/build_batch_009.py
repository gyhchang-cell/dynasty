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
DEST = HERE / 'sources/SlimeKnights__TinkersConstruct-009'
NOW = datetime.now(timezone.utc).isoformat()
META = json.loads((ORIGIN/'source.json').read_text())
TREE = json.loads((ORIGIN/'tree.json').read_text())
assert META['repo'] == REPO and META['sha'] == TREE['sha'] == PIN and not TREE['truncated']
BLOBS = {x['path']: x['sha'] for x in TREE['tree'] if x['type'] == 'blob'}
DEST.mkdir(parents=True, exist_ok=True)
for name in ['source.json', 'tree.json']:
    (DEST/name).write_bytes((ORIGIN/name).read_bytes())
ROOTS['tinkers009'] = DEST
PINS['tinkers009'] = PIN
METADATA['tinkers009'] = DEST/'source.json'
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
    e = method('tinkers009', path, signature, role)
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
VROOT = HERE/'sources/vanilla-forge-1.20.1-47.4.10-009'
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

native_support = [
    vanilla('net/minecraft/world/entity/LivingEntity.java',924,941,'addEffect'),
    vanilla('net/minecraft/world/entity/LivingEntity.java',751,803,'tickEffects'),
    vanilla('net/minecraft/world/entity/LivingEntity.java',1036,1044,'heal'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',35,37,'two-argument constructor'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',81,125,'update'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',139,141,'mapDuration'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',167,186,'tick'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',188,190,'hasRemainingDuration'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',192,200,'tickDownDuration'),
    vanilla('net/minecraft/world/effect/MobEffectInstance.java',202,207,'applyEffect'),
    vanilla('net/minecraft/world/effect/MobEffect.java',53,78,'applyEffectTick'),
    vanilla('net/minecraft/world/effect/MobEffect.java',99,124,'isDurationEffectTick')]

dispatch = [
    m('tools/logic/ToolEvents','static void livingHurt(', 'Whole LOW LivingHurt producer; can cancel before health loss'),
    m('tools/logic/ToolEvents','static void livingDamage(', 'Whole LivingDamage producer; current amount not committed health delta'),
    m('library/modifiers/hook/armor/ModifyDamageModifierHook','static float modifyDamageTaken(', 'Whole equipment dispatcher; amount <=0 stops iteration')]
slots = [m('library/modifiers/modules/technical/SlotInChargeModule',s,r) for s,r in [
    ('private boolean toolValid(', 'Whole server/unbroken/slot qualification'),
    ('public void onEquip(', 'Record slot level on equip'),
    ('public void onUnequip(', 'Remove eligible slot on unequip'),
    ('private void addSlot(', 'Overwrite per-slot contribution by delta; elect consumer'),
    ('private void removeSlot(', 'Subtract old contribution then elect remaining armor/hand'),
    ('public static int getLevel(', 'Only elected equipment slot receives total level')]]
slots += [m('library/modifiers/modules/technical/ArmorLevelModule','public static boolean validSlot(', 'Whole slot/tag eligibility'),
    m('tools/logic/EquipmentChangeWatcher','private static void onEquipmentChange(', 'Actual server equipment event entry'),
    m('tools/logic/EquipmentChangeWatcher','private static void runModifierHooks(', 'Unequip before equip, then other-slot listeners')]
recurrent = [m('tools/modules/armor/RecurrentProtectionModule','public float modifyDamageTaken(', 'Consume prior reduction then store post-reduction amount for future hits'),
    m('tools/modules/armor/RecurrentProtectionModule','public void addModules(', 'Actual SlotInCharge registration'),
    m('common/TinkerEffect','public static int getLevel(LivingEntity entity, MobEffect effect)', 'Absent effect maps to level zero'),
    m('common/TinkerEffect','public static int getAmplifier(LivingEntity entity, MobEffect effect)', 'Read entity effect amplifier, absent -1'),
    statement('tools/data/ModifierProvider',1514,1514,'Actual flat50% / five-seconds-per-level recurrent configuration'),
    statement('tools/TinkerModifiers',729,729,'Actual armor momentum NoMilkEffect registry; declaration only')]+slots+dispatch
restore = [m('tools/modules/armor/RestoreLostHealthModule','public float modifyDamageTaken(', 'Damage amount becomes delayed REGENERATION duration; no returned heal success'),
    m('tools/modules/armor/RestoreLostHealthModule','public RestoreLostHealthModule amount(', 'Whole builder constructs actual module defaults/parameters'),
    statement('tools/modules/armor/RestoreLostHealthModule',126,131,'Builder default effectLevel/chance/conditions, declarations not complete methods'),
    statement('tools/data/ModifierProvider',1196,1200,'Actual restore overrides to MODIFY_HURT; rebuff uses default MODIFY_DAMAGE; one shared lifecycle')]+dispatch

ROWS=[]
def add(key,evidence,observation,application,limits,nearest,distinction,proposed=True):
    row=dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-009-'+key,chain_id=key,batch='009',
        status='reviewed',decision='reviewed_valid_pending_carson' if proposed else 'reviewed_support_zero_credit',
        credit=0,proposed_credit=int(proposed),final_count_owner='Carson',reviewed_at=NOW,
        observation=observation,application=application,limits=limits,evidence=evidence,
        local_vanilla_support=native_support if proposed else [],
        semantic_dedup=dict(nearest_existing_families=nearest,independent_state_and_consumer=distinction,
                           supporting_methods_increment=0,mirrored_or_version_increment=0),
        dedup_key=REPO+':'+key,downloaded_code_executed=False,external_runtime_tested=False)
    ROWS.append(row)

add('recurrent-prior-hit-window-single-elected-armor-consumer',recurrent,
    '真实recurrentProtection绑定MODIFY_HURT。装备事件先unequip旧物再equip新物；SlotInCharge按槽保存level，重复add以新旧差值更新total，且只有一个inCharge槽读取总等级。该槽在受击时先减去实体已有armor momentum效果的level，再把减后amount*0.5取整作为后续效果等级，duration为总等级*100tick；reduction<=0不刷新。当前命中消费的是旧窗口，新窗口供后续伤害使用。原版effect更新可能保留较弱旧效果为hiddenEffect，并非简单last-write-wins。',
    '借鉴把本次事实与下次消费的派生窗口分开；多件装备的同一受击不应重复消费同一份旧状态，先选一个消费者再用累计等级。按槽替换差值比每次事件盲加更耐重复通知。横扫回执仍需独立攻击序号/目标身份与短TTL，不能把已有护甲效果强度当成本次成功损血。',
    '这是LivingHurt阶段、实际扣血之前的派生状态：后来防御归零或事件取消，并不会回滚已加momentum。效果并非一次消费，窗口内多次伤害都可用；旧强/弱效果可按vanilla hidden链复现。unequip只在toolValid(未坏/server/槽合法)为true才清slot，不能声称任何破损/换维度/克隆都能清理；本链不带source/target UUID、攻击代次或绝对deadline。NoMilk不等于无法显式移除。观察配置声明不等于运行配置验收。',
    ['batch008: enderdodge操作成功后取消伤害', 'batch006: bleeding续期相位',
     'batch007: equipment-watcher支持链（不再计）', 'main generic armor/cooldown families'],
    'New unit owns a previous-hit-derived reduction window and a single elected equipment consumer; dispatcher, slot aggregate, current cancellation and effect templates are supporting evidence only.')

add('incoming-damage-snapshot-to-nonadditive-regeneration-duration',restore,
    '实际restore显式挂MODIFY_HURT，而rebuff沿用模块默认MODIFY_DAMAGE，两配置共用一个实现。来源/防御者/工具条件及概率通过后，heal=floor(percent*当前事件amount)>0才创建再生。代码把heal*(50>>(effectLevel-1))写进duration，却调用双参数MobEffectInstance，实际amplifier固定0。原版effect按剩余duration%50==0才heal(1)，再递减；多次addEffect同等级优先较长duration，未相加。heal再经过Forge onLivingHeal，非正或生命<=0不会落实回血。',
    '这是把当前事件数值转成以后逐tick执行的载荷；登记成功不等于实际兑现，多个记录压入同一状态可能被合并而不是累计。横扫必须分别保留已观察的伤害事实、排队记录和一次消费结果，不应只靠存在某个effect/计时器就判每份回执兑现。这里两个hook绑定与所有装备不拆分信用。',
    '不保证名为heal的预算最终全部返还：effectLevel仅改变duration计算，没有传入amplifier；同等级merge不叠加、满血、显式移除、死亡与取消治疗都会改变实际输出。MODIFY_DAMAGE依然不是最终扣血之后；本模块忽略addEffect返回值，即使未接纳也能播放音效并损耗工具。没有原攻击UUID/目标代次/事务once键，装备多次调用可能重复声音/损耗；只报告真实代码行为，不修复生产、不执行上游或运行验证。',
    ['batch009 recurrent: 前次受击窗口只影响下一次伤害',
     'batch008 enderdodge: 成功传送门控取消伤害', 'main health/effect and cooldown families'],
    'New deferred output is a precomputed regeneration duration consumed by native effect ticks, with non-additive coalescing and separately cancelable heal; not another synchronous damage-reducer configuration.')

add('slot-in-charge-support-not-an-extra-chain',slots,
    '六槽数组保存各槽level；addSlot按差值更新total避免重复add直接翻倍；removeSlot先扣旧值再按armor/hand顺序选新inCharge。装备watcher旧unequip先于新equip；这些方法共同支持recurrent一次装备分派。',
    '有助于检查本次遍历内唯一消费者与装备变化，但本批不把具体容器或每个槽算额外实现。',
    '只有完整recurrent玩法链提候选；容器、Mirror、getter或注册本身不满足独立回执生命周期。',
    ['batch009 recurrent','batch007 equipment watcher'],
    'Supporting state aggregation only, zero incremental unit.',False)

MAIN=WORKSPACE/'docs/cod4/audit-20261022/sweep-receipt-research'
comparison=[]
for name in ['accepted.jsonl','reviewed.jsonl']:
    comparison.extend(json.loads(x) for x in (MAIN/name).read_text().splitlines() if x.strip())
for p in DOCS.glob('batch-00[1-8].json'):
    comparison.extend(json.loads(p.read_text())['entries'])
for r in ROWS:
    matches=[d for d in comparison if (d.get('repo'),d.get('revision'),d.get('path'),d.get('line')) ==
        (r['repo'],r['revision'],r['path'],r['line'])]
    r['semantic_dedup']['exact_primary_preexisting']=bool(matches)
    if r['proposed_credit']:assert not matches,r['candidate_id']

def dump(name,o):
    (DOCS/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
proposed=[r for r in ROWS if r['proposed_credit']]
excluded=[r for r in ROWS if not r['proposed_credit']]
common=dict(schema_version=1,reviewed_at=NOW,credit_applied=0,final_count_owner='Carson',
    source_revision=PIN,no_compilation=True,no_runtime_tests=True,upstream_code_executed=False)
dump('batch-009.json',dict(common,proposed_valid=len(proposed),entries=proposed))
dump('excluded-009.json',dict(common,proposed_valid=0,entries=excluded))
(DOCS/'reviewed-009.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ROWS))
dump('source-index-009.json',dict(repo=REPO,revision=PIN,official_source_provenance=META,
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
dump('validation-009.json',dict(common,validation_kind='Evidence text/hash/range integrity only, not compilation or gameplay',
    errors=errors,unique_method_ranges=sum(e['evidence_kind'].startswith('complete_method') for e in unique.values()),
    configuration_statement_ranges=sum(e['evidence_kind'].startswith('configuration') for e in unique.values()),
    pending_candidates=len(proposed),excluded_support=len(excluded),applied_credit=0,method_count_is_not_credit=True,
    main_ledger_read_only_snapshots={name:sha((MAIN/name).read_bytes()) for name in ['accepted.jsonl','reviewed.jsonl','protocol.json']},
    production_qa_todo_written=False,network_requests=0))
print(json.dumps(dict(candidates=len(proposed),excluded=len(excluded),credit=0,evidence_ranges=len(unique),files=len(FILES),errors=errors)))

