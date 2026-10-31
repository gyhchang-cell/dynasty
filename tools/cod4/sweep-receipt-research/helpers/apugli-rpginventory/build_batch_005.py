"""Package locally read Minecraft source evidence; never execute upstream code."""
import datetime
import hashlib
import json
from evidence_003 import DOCS, WORKSPACE, REPO, behavior, standard, dump, sha

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
ROWS = []


def ev(name, signatures):
    return [behavior(name, sig, role) for sig, role in signatures]


def add(key, evidence, observation, application, limits, proposal=False, duplicate_of=None):
    row = dict(evidence[0])
    row.update(candidate_id='apugli-rpginventory-005-' + key, chain_id=key,
               batch='005', status='reviewed', credit=0, proposed_credit=int(proposal),
               decision='reviewed_valid_pending_carson' if proposal else 'reviewed_excluded_zero_credit',
               final_count_owner='Carson', reviewed_at=NOW, evidence=evidence,
               observation=observation, application=application, limits=limits,
               duplicate_of=duplicate_of, dedup_key=REPO + ':' + key,
               counting_unit='One complete gameplay lifecycle; methods, versions and loader mirrors do not multiply credit.',
               external_runtime_tested=False, downloaded_code_executed=False)
    ROWS.append(row)


add('hover-continuous-use-heartbeat-and-recharge-handoff',
    ev('power/HoverPower', [
        ('public void onUse()', 'producer modifies actual falling movement and stamps current world time'),
        ('public void tick()', 'later tick consumes heartbeat, advances recharge delay and replenishes resource'),
        ('public boolean canUse()', 'concrete movement and resource eligibility'),
        ('public NbtElement toTag()', 'persists own heartbeat and pending recharge state'),
        ('public void fromTag(', 'restores raw pending state'),
        ('public HoverPower(', 'enables ticking and retains lifecycle parameters'),
        ('public static PowerFactory<?> getFactory()', 'concrete active hover gameplay configuration')]) +
    ev('registry/ApugliPowerFactories', [('public static void register()', 'registers HoverPower factory')]) +
    ev('Apugli', [('public void onInitialize()', 'real mod initializer reaches factory registration')]) +
    [standard('default', 'common:power/HoverPower', sig, role) for sig, role in [
        ('public HoverPower(', 'version comparison: current class retains only correction range'),
        ('public boolean canCorrectHeight()', 'current class has no heartbeat in this method'),
        ('public double getCorrectionRange()', 'current instance range read'),
        ('public static Optional<Double> getCorrectionRange(', 'current gameplay aggregates correction ranges')]],
    'fabric/behavior固定提交5cf41d11dbb4308b0796505e6c9d3541bad09217，Minecraft 1.18/Apugli 1.5.1。已读完整Hover类及真实工厂注册/初始化。onUse只有资源可用、正在下落且未落地才清垂直速度/fallDistance；按entity.age取模扣资源、重置rechargeTimer，再记录world.getTime并置isInUse。后续tick先可因inactive提前返回，随后lastUseTime不等当前world时间即清isInUse；不在使用时连续落地/骑乘推进充能等待，否则等待清零。达到阈值后按entity.age/rechargeRate节拍恢复资源，满值再将timer加一退出等值分支。四项状态有NBT写入/恢复。当前1.20.4同名类改为高度修正范围，不含该生命周期，作为版本辨别支持而不另计。',
    '这是持续使用心跳与后续充能任务之间的交接，独立于一次性投射物连发、BunnyHop落地容错或UI冷却进度。可借鉴先确认状态表达的是“本tick仍持续输入”还是“此前已发生的成功事实”：本链严格同刻用于心跳存活判断，而横扫真实伤害回执跨4991→4992不应直接套用此语义。保存时钟域、使用阶段和等待阶段分别评估，整个状态机只建议一条，credit仍为0。',
    'Apoli Active调用及父类实际tick派发在授权仓库之外，未阅读，不能证明onUse与tick真实先后或两端调用频率；本类没有显式side guard。不是伤害事实，不提供安全TTL数值。world时间与entity.age混用，NBT原样恢复lastUseTime、isInUse、timer，没有世界/维度/代次或范围夹取；换世界同值时钟不能证明同一心跳。inactive提前返回可冻结旧状态，timer达到阈值后充能分支不再复查落地，tick_rate/recharge_rate未防0。不是先移除后回调的一次性消费容器，不能由stamp断言回调重入安全或严格扣费一次。源码静态审阅，不编译、不运行上游代码，不声称运行验收。',
    True)

add('legacy-hit-history-write-kind-and-queued-remove',
    ev('mixin/LivingEntityMixin', [
        ('private void addToHits(DamageSource', 'damage HEAD writes attempt count and death-path removal'),
        ('public HashMap<Entity, Integer> getHits()', 'concrete target-owned map'),
        ('public void addToHits(Entity', 'manual additive write'),
        ('public void setHits(Entity', 'manual overwrite')]) +
    ev('action/bientity/ChangeHitsOnTargetAction', [
        ('public static void action(', 'ADD falls through SET, packet operation differs from server write'),
        ('public static ActionFactory<Pair<Entity, Entity>> getFactory()', 'actual configured change operation')]) +
    ev('util/HitsOnTargetUtil', [('public static void sendPacket(', 'actual numeric actor/target IDs and SET/REMOVE payload')]) +
    ev('networking/ApugliPacketsS2C', [
        ('private static void onHitsOnTargetSync(', 'queued concrete target map mutation with both entity lookups'),
        ('public static void register()', 'real receiver registration')]) +
    ev('condition/bientity/HitsOnTargetCondition', [
        ('public static boolean condition(', 'actual gameplay consumes hit map'),
        ('public static ConditionFactory<Pair<Entity, Entity>> getFactory()', 'actual comparison configuration')]) +
    ev('registry/action/ApugliBiEntityActions', [('public static void register()', 'manual mutation action registered')]) +
    ev('registry/condition/ApugliBiEntityConditions', [('public static void register()', 'gameplay condition registered')]) +
    ev('ApugliClient', [('public void onInitializeClient()', 'initializer reaches S2C receiver')]) +
    ev('Apugli', [('public void onInitialize()', 'initializer reaches actions and conditions')]),
    '旧版目标LivingEntity拥有Entity引用→命中数HashMap，damage HEAD在部分hurtTime条件后累加并发SET，尚未观察原hurt结果。已读注册、真实生产、手动变更、传输、排队消费和玩法条件。ChangeHitsOnTargetAction冒号switch的ADD块没有break：先add并发SET累计值，接着落入SET块，将服务端值覆盖为change并发REMOVE；单独SET也写服务端值却发REMOVE。客户端execute后按捕获handler当前world解析targetId和attackerId，两者均须LivingEntity，REMOVE才按当前attacker对象引用移除；条件对死亡目标直接读0，并不清Map。',
    '新增具体观察是操作种类必须保持端到端一致，不能把SET、REMOVE与回执已消费混为同一个“状态更新”；清理消息若要求旧来源仍能按当前world数字ID解析，来源已卸载时反而不能清除旧记录。保留实际玩法证据，服务端写入与客户端删项分歧不包装成两个新实现。',
    '属于主账已接受HitsOnTarget完整族的旧版对照，独立增量为0。HEAD计数不是成功伤害，死亡路径还调用tryUseTotem，不能当无副作用观察。没有短TTL/UUID/维度/序列；未读原版实体ID复用、图腾实现与网络调度，不推定具体运行结果。ADD落穿是静态Java控制流判断，未执行上游代码。',
    False, 'batch001/main accepted: HitsOnTargetComponentImpl serverTick; whole hit-history lifecycle')

add('behavior-null-target-is-not-return-cancellation',
    ev('mixin/EndermanEntityTeleportTowardsPlayerGoalMixin', [('private void cancelStart(', 'canStart RETURN clears target field without replacing return')]) +
    ev('mixin/AngerableMixin', [('private void stopAngerOnTargets(', 'anger tick performs stopAnger without cancelling caller')]) +
    ev('power/ModifyMobBehaviorPower', [
        ('public boolean doesApply(', 'actual holder/mob eligibility'),
        ('public MobBehavior getMobBehavior()', 'actual behavior retrieval'),
        ('public void tick()', 'already reviewed registration and revocation container'),
        ('public void onRemoved()', 'already reviewed power removal cleanup')]) +
    ev('behavior/MobBehavior', [
        ('public boolean isPassive(', 'base predicate is false'),
        ('public void removeGoals(', 'actual owned selector cleanup'),
        ('public boolean hasAppliedGoals(', 'registration identity membership check')]),
    '旧版Enderman目标任务在canStart RETURN注入，若ModifyMobBehaviorPower判定passive，仅targetPlayer=null；没有cir.setReturnValue(false)，也未声明cancellable。源码Mixin目标字符串含mob/EndermanEntity路径斜线，不能未经加载断言生效。Angerable.tickAngerLogic注入在getAngryAt调用前依据捕获livingEntity的power决定stopAnger，同样不取消调用方。两者属于已有行为授权/撤销链的额外入口，完整读取相关方法与容器方法。',
    '区分任务注册句柄、当前target引用、方法返回的启动资格和怒气状态：清其中一个不能自动证明另三个已撤销。把这一观察附到batch003目标撤销族，避免将每个取消入口包装成独立案例。',
    '重复batch003行为任务生命周期，0增量。外部PowerHolderComponent对null参数及原版Goal后续行为未审阅；捕获局部对象也无显式null检查。没有运行Mixin加载、游戏或测试，不能声称该路径一定阻止启动或一定崩溃。',
    False, 'batch003:behavior-goal-registration-revocation')


def main():
    index = {f['source_local']: f for f in json.loads((DOCS / 'source-index.json').read_text())}
    for branch in json.loads((DOCS / 'branch-source-index-003.json').read_text()):
        index.update({f['source_local']: f for f in branch['files']})
    unique = set()
    for row in ROWS:
        for e in row['evidence']:
            data = (WORKSPACE / e['source_local']).read_bytes()
            assert sha(data) == e['source_sha256'] == index[e['source_local']]['source_sha256']
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            assert hashlib.sha1(blob).hexdigest() == index[e['source_local']]['git_blob_sha1']
            assert e['excerpt'] == '\n'.join(data.decode().splitlines()[e['line'] - 1:e['end_line']])
            unique.add((e['revision'], e['path'], e['line'], e['end_line']))
    previous = []
    for name in ['reviewed.jsonl', 'reviewed-002.jsonl', 'reviewed-003.jsonl', 'reviewed-004.jsonl']:
        previous.extend(json.loads(s) for s in (DOCS / name).read_text().splitlines() if s)
    assert not ({r['dedup_key'] for r in ROWS} & {r['dedup_key'] for r in previous})
    ledger_raw = (DOCS.parents[1] / 'accepted.jsonl').read_bytes()
    ledger = [json.loads(s) for s in ledger_raw.decode().splitlines() if s]
    exact = [r['candidate_id'] for r in ROWS if r['proposed_credit'] and any(
        (r['revision'], r['path'], r['line']) == (a.get('revision'), a.get('path'), a.get('line')) for a in ledger)]
    assert not exact
    proposals = [r for r in ROWS if r['proposed_credit']]
    dump('batch-005.json', dict(schema_version=1, reviewed_at=NOW, credit_applied=0,
                              final_count_owner='Carson', proposed_valid=len(proposals), entries=proposals))
    dump('excluded-005.json', dict(schema_version=1, credit=0, entries=[r for r in ROWS if not r['proposed_credit']]))
    (DOCS / 'reviewed-005.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in ROWS))
    dump('validation-005.json', dict(schema_version=1, artifact='static source evidence integrity only; not runtime acceptance',
        reviewed_groups=len(ROWS), proposed_valid=len(proposals), zero_increment_groups=len(ROWS)-len(proposals),
        distinct_complete_method_ranges=len(unique), source_hash_and_full_ranges_verified=True,
        git_blob_hashes_match_previously_commit_verified_indexes=True,
        main_accepted_read_only_rows=len(ledger), main_accepted_read_only_sha256=sha(ledger_raw), exact_main_duplicates=exact,
        credit_applied=0, external_requests=0, compilation_performed=False, runtime_tests_performed=False,
        game_started=False, graphical_program_started=False, real_tcp_started=False, downloaded_code_executed=False))
    print(json.dumps(dict(proposed=len(proposals), zero_increment=len(ROWS)-len(proposals), complete_methods=len(unique), credit=0)))


if __name__ == '__main__':
    main()
