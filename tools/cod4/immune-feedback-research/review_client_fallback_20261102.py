"""Main semantic review of the previously unaccepted Herschel060 candidate.

The source was read before this serialization. Hash replay is not the reading.
"""
from datetime import datetime, timezone
import hashlib
import json
from ledger import B, O, R, record, verify


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    out = O / 'coordinator-client-fallback-observation-review-20261102.json'
    assert not out.exists(), 'Preserve the existing acceptance receipt'
    ledger_path = O / 'reviewed.json'
    initial = ledger_path.read_bytes()
    rows = json.loads(initial)
    assert len(rows) == 455, 'Review concurrent research progress before writing'
    old_key = 'damageengine-level-source-merge-and-targeted-worldtext'
    old = next(x for x in rows if x['id'] == old_key)
    assert all('ClientHealthTracker.java' not in ref['source_path'] and
               'ClientAttackTracker.java' not in ref['source_path'] and
               'LivingEntityClientMixin.java' not in ref['source_path']
               for ref in old['source_refs'])
    helper = O / 'helpers/herschel-immune/batch-060.json'
    proposal = json.loads(helper.read_text())
    assert proposal['research_credit'] == 0
    assert proposal['rows'][0]['status'] == 'pending_primary_semantic_review'
    repo = 'Ovear-Mitama/Damage-Engine'
    root = B / 'sources/Ovear-Mitama__Damage-Engine'
    meta_path = root / 'source.json'
    meta = json.loads(meta_path.read_text())
    assert meta['commit'] == '3bcb595a681729c3a9ab18c4e3d052f2a9958a74'
    manifest = {x['path']: x['sha256'] for x in meta['files']}
    p = 'common/src/client/java/damage/engine/'
    refs = [(p + name, 1, len((root / (p + name)).read_text().splitlines())) for name in [
        'client/ClientAttackTracker.java', 'client/ClientHealthTracker.java',
        'mixin/client/LivingEntityClientMixin.java', 'mixin/client/ClientTickMixin.java',
        'mixin/client/PlayerAttackMixin.java', 'mixin/client/ProjectileHitMixin.java',
        'client/IndicatorPos.java', 'hud/session/DamageSessionManager.java']]
    refs += [
        ('neoforge/src/main/java/damage/engine/DamageEngineClient.java', 1, 94),
        ('neoforge/src/main/java/damage/engine/network/NetworkSetup.java', 1, 151),
        ('neoforge/src/main/resources/damage-engine.client.mixins.json', 1, 16),
        ('neoforge/src/main/resources/META-INF/neoforge.mods.toml', 1, 54),
        ('neoforge/build.gradle', 1, 199),
        ('common/src/main/java/damage/engine/DamageEngineConfig.java', 317, 332),
        ('common/src/main/java/damage/engine/DamageEngineConfig.java', 375, 377),
        ('common/src/main/java/damage/engine/DamageEngineConfig.java', 417, 453),
        (p + 'hud/indicator/DamageIndicator.java', 405, 456),
    ]
    checks = []
    for rel, lo, hi in refs:
        raw = (root / rel).read_bytes()
        assert sha(raw) == manifest[rel]
        lines = raw.decode().splitlines(keepends=True)
        checks.append({'path': str((root / rel).relative_to(R)),
                       'file_sha256': sha(raw), 'start_line': lo, 'end_line': hi,
                       'range_sha256': sha(''.join(lines[lo - 1:hi]).encode())})
    for ref in proposal['rows'][0]['source_refs']:
        rel = ref['source_key'].split('/', 1)[1]
        raw = (root / rel).read_bytes()
        assert sha(raw) == ref['file_sha256'] == manifest[rel]
        lo, hi = ref['lines']
        excerpt = ''.join(raw.decode().splitlines(keepends=True)[lo - 1:hi])
        assert sha(excerpt.encode()) == ref['excerpt_sha256']
    key = 'damageengine-native-client-fallback-attempt-lease-observation-debounce-loss-before-feedback-creation'
    assert ledger_path.read_bytes() == initial
    item = record(key, repo, refs,
        '实际完整读取六个客户端tracker/mixin、IndicatorPos、SessionManager、NeoForge客户端入口和NetworkSetup。'
        'Player.attack HEAD与本地玩家所有的Projectile.onHitEntity HEAD把原始target integerID写静态Singleton的2秒wallclock租约，未等hurt结果。'
        'LivingEntity.tick TAIL首次保存health+absorption；以后正差>0.001或死亡且serverHasMod=false时，严格距上次>50ms才调用ClientHealthTracker。'
        '调用后即更新时间，即使下游因serverModChecked=false或配置拒绝；尾部总更新血量基线，50ms内被抑制的差值不排队/补发/合并。'
        'ClientHealthTracker最终只在server确认无mod且showDamage时准入，租约命中把整个观察血差归本机，自路径先更新session再按距离和伤害/击杀开关创建指标；'
        '非自路径可按实体配置距离出全局指标。调用现有addIndicator可选合并并trim到容量；该渲染/合并链复用旧账0。'
        '实际Mixin JSON列出四项且NeoForge mods.toml引用，build.gradle接common两个source roots；登录仅重置检测flags和40tick检查。'
        '非暂停tick清理租约；可选DamagePayload网络接收立即写serverHasMod/serverModChecked再排clienttask。未执行游戏或验证真正注入。',
        '一条真正不同的客户端fallback战斗反馈资格/采样政策计1，不把2秒/50ms/每种mixin各算一条。'
        '同库旧账只读服务端实损及S2C到绘制，虽然含ClientTick，未包含这三个核心tracker/采样生产类；新信用不覆盖重读的renderer/merge/packet。'
        '与实际重新读过的ImmersiveDamageIndicators两mixin相比，后者要求getLastDamageSource.entity是LocalPlayer并按tick保留待显示伤害，'
        '不是本例原始ID尝试租约+wallclock采样丢弃政策；与DNP已账首次WeakHashMap血差也不同。'
        '租约不能证明这次伤害由本机造成；原始部件ID不由SessionManager的dragon-parent目标比较反向规范化。'
        '两个gate均是观测/归属资格，不是Boss语义拒绝或免疫防刷。',
        'Boss灰字必须来自明确服务端拒控原因，不能由客户端零血差、一次尝试租约、收到hp同步或指标缺失推断。'
        '观测防抖、指标合并和语义拒绝节流应分别核查；若确需采样，应明确被抑制数据是合并还是丢弃。'
        '迟包/跨维度应使用有作用域的稳定身份，不能把raw entityID或wallclock租约当来源回执。不改普通阴阳灰字需求。',
        '固定源码为较新版NeoForge/JAVA_25上下文，不是Forge1.20.1可直接移植或构建通过。'
        '没有执行上游源码/原生输入/网络/渲染；不同步或误归属是静态条件边界，不宣称实机复现。'
        '死亡分支可同时请求普通伤害和kill指标，不声称仅一个。Healing分支不受serverHasMod和50ms伤害gate约束，不能把整类统称仅fallback。'
        'RatingManager/CombatContext内部未本批重读，不以session调用宣称评分准确；旧完整绘制链重用且0额外。'
        '客户端fallback不含immune reason，0新生产改动/0游戏/0清单删除。',
        'native_client_observation_qualification_before_combat_feedback')
    dedup_path = O / 'semantic-dedup.json'
    dedup = json.loads(dedup_path.read_text())
    dedup['groups'].append({
        'family': 'client-fallback-attempt-lease-and-lossy-observation-admission-20261102',
        'credited_chains': [key],
        'rationale': 'One newly reviewed native client observation qualification site. Old server-to-worldtext, actual lastDamageSource local attribution, generic health-delta and renderer/merge wrappers remain separate old evidence with zero repeated credit.'})
    dedup_path.write_text(json.dumps(dedup, ensure_ascii=False, indent=2) + '\n')
    comparison = B / 'sources/txnimc__ImmersiveDamageIndicators'
    comparisons = []
    for name in ['LivingEntityMixin.java', 'PlayerMixin.java']:
        path = comparison / ('src/main/java/toni/immersivedamageindicators/mixins/' + name)
        comparisons.append({'path': str(path.relative_to(R)), 'sha256': sha(path.read_bytes()),
                            'whole_file_reread_for_dedup_only': True, 'new_credit': 0})
    receipt = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'decision': 'ACCEPT_ONE_SEMANTICALLY_DISTINCT_CLIENT_OBSERVATION_IMPLEMENTATION',
        'helper': str(helper.relative_to(R)), 'helper_sha256': sha(helper.read_bytes()),
        'helper_credit_unchanged': 0, 'independent_main_review': True,
        'promoted_key': key, 'new_effective_credit': 1,
        'source_manifest_sha256': sha(meta_path.read_bytes()),
        'source_archive_sha256': meta['archive_sha256'], 'source_commit': meta['commit'],
        'actual_source_ranges': checks, 'prior_ledger_sha256': sha(initial),
        'prior_same_repo_accepted_record_sha256': sha(json.dumps(old, sort_keys=True, ensure_ascii=False).encode()),
        'prior_same_repo_rendering_chain_credit_reused': 0,
        'semantic_comparison_source_rereads': comparisons,
        'concrete_observation': item['concrete_observation'],
        'additional_limits': item['limitations'],
        'production_mutations': 0, 'game_starts': 0, 'checklist_deletions': 0,
        'duration_hours_claimed': 0,
    }
    with out.open('x') as f:
        f.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    verify()
    print(json.dumps({'receipt': str(out.relative_to(R)), 'sha256': sha(out.read_bytes()),
                      'accepted_total': 456, 'gap': 544}))


if __name__ == '__main__':
    main()
