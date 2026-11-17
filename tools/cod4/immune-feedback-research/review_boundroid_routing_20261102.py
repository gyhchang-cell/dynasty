"""Serialize the coordinator's completed source reading, not automatic credit.

Only the preflight-routed two-health-pool policy is newly counted. Full classes,
registries, renderers and the Murmur comparison support that one decision.
"""
from datetime import datetime, timezone
import hashlib
import json

from ledger import B, O, R, record, verify


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    out = O / 'coordinator-boundroid-preflight-routing-review-20261102.json'
    assert not out.exists(), 'Keep prior evidence immutable'
    ledger_path = O / 'reviewed.json'
    before = ledger_path.read_bytes()
    rows = json.loads(before)
    assert len(rows) == 456, 'Inspect concurrent changes first'
    repo = 'AlexModGuy/AlexsCaves'
    source = B / 'sources/AlexModGuy__AlexsCaves'
    meta_path = source / 'source.json'
    tree_path = source / 'tree.json'
    meta = json.loads(meta_path.read_text())
    tree = json.loads(tree_path.read_text())
    assert meta['commit'] == tree['sha'] == '4718f4287c65b810aecb211789b45f54d405a94d'
    assert not tree['truncated']
    manifest = {x['path']: x for x in meta['files']}
    blobs = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    base = 'src/main/java/com/github/alexmodguy/alexscaves/'
    refs = [
        (base + 'server/entity/living/BoundroidEntity.java', 1, 265),
        (base + 'server/entity/living/BoundroidWinchEntity.java', 1, 526),
        (base + 'server/entity/ACEntityRegistry.java', 1, 33),
        (base + 'server/entity/ACEntityRegistry.java', 110, 156),
        (base + 'server/entity/ACEntityRegistry.java', 164, 164),
        (base + 'AlexsCaves.java', 91, 133),
        (base + 'client/render/entity/BoundroidWinchRenderer.java', 1, 128),
        (base + 'client/render/entity/BoundroidRenderer.java', 1, 52),
        (base + 'client/ClientProxy.java', 171, 172),
        (base + 'server/potion/ACEffectRegistry.java', 24, 24),
    ]
    checks = []
    for rel, lo, hi in refs:
        raw = (source / rel).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha(raw) == manifest[rel]['sha256']
        assert blob == manifest[rel]['git_blob_sha1'] == blobs[rel]
        lines = raw.decode().splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        checks.append({'path': str((source / rel).relative_to(R)), 'lines': [lo, hi],
                       'file_sha256': sha(raw), 'git_blob_sha1': blob,
                       'range_sha256': sha(''.join(lines[lo - 1:hi]).encode())})
    comparison_keys = [
        'alexsmobs-native-linked-body-refusal-falls-back-to-independent-head-damage',
        'alexscaves-native-multipart-client-admission-versus-generic-server-damage-relay',
        'alexscaves-native-dual-hook-live-owner-relationship-reciprocal-hit-exclusion',
        'iron-shield-multipart-parent-throttle-false-result',
        'ars-bubble-registered-hit-redirect-and-damage-bonus',
        'iron-incoming-tomb-redirect-fireward',
        'vampirism-native-immobile-boss-vulnerability-proxy-versus-rejected-source',
        'wizardry-possession-native-damage-redirect-settlement',
    ]
    comparisons = []
    for key in comparison_keys:
        old = next(x for x in rows if x['semantic_dedup_key'] == key)
        comparisons.append({'key': key,
                            'accepted_record_sha256': sha(json.dumps(old, ensure_ascii=False, sort_keys=True).encode()),
                            'whole_prior_source_chain_reread_claimed': False,
                            'repeated_credit': 0})
    murmur = next(x for x in rows if x['semantic_dedup_key'] == comparison_keys[0])
    old_ref = murmur['source_refs'][0]
    old_file = R / old_ref['path']
    old_raw = old_file.read_bytes()
    assert sha(old_raw) == old_ref['file_sha256']
    old_lines = old_raw.decode().splitlines(keepends=True)
    comparison_source = {'path': old_ref['path'], 'lines': [276, 290],
                         'file_sha256': sha(old_raw),
                         'range_sha256': sha(''.join(old_lines[275:290]).encode()),
                         'reread_actual_complete_hurt_and_isInvulnerableTo_only': True,
                         'credit': 0}
    key = 'alexscaves-native-preflight-head-immunity-routes-independent-winch-health-with-success-qualified-unlatch'
    assert all('Boundroid' not in ref['source_path'] for row in rows for ref in row['source_refs'])
    assert ledger_path.read_bytes() == before
    item = record(key, repo, refs,
        '实际注册BOUNDROID/BOUNDROID_WINCH两个独立Monster，MOD事件属性把两者均绑定BoundroidEntity.createAttributes。'
        'head原生server tick解析当前ServerLevel中的WINCH_UUID；缺失时构造winch、尝试addFreshEntity并写UUID/ID，存在时linkWithHead。'
        'winch原生hurt先自身isInvulnerableTo拒绝；若head非null且预检head.isInvulnerableTo=false，则同source/全额调用head.hurt，直接返回该bool；'
        '只有head.hurt=true才设60..119tick noLatchCooldown。若head不存在或预检已免疫，才走winch自身super.hurt。'
        '所以head在真正hurt阶段拒绝时不再转伤winch，与head预检拒绝的路由不同。'
        'tick先递减冷却；latched状态遇冷却>0累计changeLatchStateTime>5才脱钩、播dazed并复位；不立即脱钩。'
        '脱钩后MeleeGoal设head.scared，头renderer读该状态选择材质/抖动；head hurt/death计时非零才复制给winch，链renderer读winch overlay。',
        '独立1条实际最终承伤路由与成功回执驱动失衡政策。最接近Murmur的实际hurt/isInvulnerableTo已重读：'
        'Murmur先试body半伤，并在body.hurt=false后回落到head全伤；这里按head.isInvulnerableTo预检分派，进入head.hurt分支后false直接终止，'
        '只在head缺失/预检免疫时改用独立winch血池。差异是控制流与结算对象，不是实体名、倍率或冷却常量。'
        '同一source对head不受伤，不代表对关联winch也拒伤；受击反馈必须保留实际血池和拒绝阶段。'
        '归一为一条整链，独立magnetizing效果拒绝、IN_WALL常量、两个实体/注册/计时/声音/renderer均不另计。',
        'Boss拒控回执必须在权威最终拒绝处确定，不能把主体预检、附属hurt bool、血量不变、复制hurtTime或迟到的失衡动画混作同一结果。'
        '若存在多血池路由，明确预检失败与真正结算失败是否允许fallback，并以真实成功结果驱动资源或反馈；不据此直接修改王朝。',
        '本批完整读head265/winch526及两renderer180行，注册/入口如范围所列；未看模型/贴图原图、未制作资产、未执行上游或本包游戏。'
        'Monster/LivingEntity原版伤害、SynchedEntityData同步、Mob目标调度和模型helper内部未本批展开，不能声称HP/双端画面/动画实测。'
        'head getWinch和winch getHead是server当前world UUID/client当前world整数ID；hurt不验head类型/互指UUID/alive。'
        'winch保存写BodyUUID而读HeadUUID，head端持久WinchUUID后可能重新link，但不保证孤立winch重载必存活；无head的server tick直接remove(KILLED)。'
        'head重建忽略addFreshEntity结果，非null错类型不自动重建；不声称无孤儿或无重复生成。'
        'winch自身isInvulnerableTo继承父类，head另加IN_WALL，不能说两者同一个源门；MAGNETIZING拒绝只作为支持0。'
        'dazed只在latched转false且冷却仍>0时播放，已脱钩时再次有效命中并不保证新声音；scared是AI/脱钩状态而非专门拒伤提示。'
        '复制计时仅head非零，不是独立winch血量同步，无法由overlay证明伤落在哪池。'
        '旧同库generic C2S relay、双钩关系拒伤与其他转伤政策只比较既账决策，不冒充本批重读它们全部源链。'
        '0新生产/游戏/清单删除/小时声明；全部支持方法和常量0额外信用。',
        'native_preflight_damage_routing_and_success_qualified_state_feedback')
    dedup_path = O / 'semantic-dedup.json'
    dedup = json.loads(dedup_path.read_text())
    dedup['groups'].append({'family': 'preflight-routed-independent-linked-health-and-qualified-unlatch-20261102',
                            'credited_chains': [key],
                            'rationale': 'One complete native routing policy. Unlike already accepted Murmur post-hurt-false fallback, this branch chooses fallback only before head.hurt based on isInvulnerableTo; actual false does not fall through. Latch feedback, source constants, registration and renderer helpers are support0.'})
    dedup_path.write_text(json.dumps(dedup, ensure_ascii=False, indent=2) + '\n')
    receipt = {'recorded_at': datetime.now(timezone.utc).isoformat(),
               'decision': 'ACCEPT_ONE_DISTINCT_NATIVE_PREFLIGHT_ROUTING_AND_SUCCESS_FEEDBACK_POLICY',
               'new_effective_credit': 1, 'promoted_key': key, 'source_commit': meta['commit'],
               'source_manifest_sha256': sha(meta_path.read_bytes()),
               'source_tree_sha256': sha(tree_path.read_bytes()), 'actual_source_ranges': checks,
               'semantic_comparisons': comparisons, 'actual_comparison_source_reread': comparison_source,
               'prior_ledger_sha256': sha(before), 'concrete_observation': item['concrete_observation'],
               'limits': item['limitations'], 'production_mutations': 0, 'game_starts': 0,
               'checklist_deletions': 0, 'duration_hours_claimed': 0}
    with out.open('x') as f:
        f.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    verify()
    print(json.dumps({'receipt': str(out.relative_to(R)), 'sha256': sha(out.read_bytes()),
                      'accepted_total': 457, 'remaining': 543}))


if __name__ == '__main__':
    main()
