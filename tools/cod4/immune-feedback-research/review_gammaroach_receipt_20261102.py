"""Save one completed semantic reading; no automatic per-file credit."""
from datetime import datetime, timezone
import hashlib
import json

from ledger import B, O, R, record, verify


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    target = O / 'coordinator-gammaroach-status-qualified-counter-review-20261102.json'
    assert not target.exists()
    ledger_path = O / 'reviewed.json'
    before = ledger_path.read_bytes()
    rows = json.loads(before)
    assert len(rows) == 457
    repo = 'AlexModGuy/AlexsCaves'
    source = B / 'sources/AlexModGuy__AlexsCaves'
    meta = json.loads((source / 'source.json').read_text())
    tree = json.loads((source / 'tree.json').read_text())
    assert meta['commit'] == tree['sha'] == '4718f4287c65b810aecb211789b45f54d405a94d'
    assert not tree['truncated']
    manifest = {row['path']: row for row in meta['files']}
    blobs = {row['path']: row['sha'] for row in tree['tree'] if row['type'] == 'blob'}
    base = 'src/main/java/com/github/alexmodguy/alexscaves/'
    refs = [
        (base + 'server/entity/living/GammaroachEntity.java', 1, 345),
        (base + 'server/entity/ACEntityRegistry.java', 19, 25),
        (base + 'server/entity/ACEntityRegistry.java', 58, 58),
        (base + 'server/entity/ACEntityRegistry.java', 110, 156),
        (base + 'AlexsCaves.java', 91, 133),
        (base + 'server/potion/ACEffectRegistry.java', 20, 29),
        (base + 'client/ClientProxy.java', 197, 197),
        (base + 'client/render/entity/GammaroachRenderer.java', 1, 49),
        (base + 'client/model/GammaroachModel.java', 157, 270),
    ]
    checks = []
    for path, lo, hi in refs:
        raw = (source / path).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha(raw) == manifest[path]['sha256']
        assert blob == manifest[path]['git_blob_sha1'] == blobs[path]
        lines = raw.decode().splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        checks.append({'path': str((source / path).relative_to(R)), 'lines': [lo, hi],
                       'file_sha256': sha(raw), 'git_blob_sha1': blob,
                       'excerpt_sha256': sha(''.join(lines[lo - 1:hi]).encode())})
    comparisons = [
        'domestication-native-replenishing-retaliation-stock-refusal-with-last-hit-recharge-reset',
        'bewitchment-native-volatility-consumed-pre-settlement-target-anchored-combat-cue',
        'alexscaves-native-damage-qualified-reputation-band-receipt-and-retaliation-refusal',
        'alexscaves-native-sonic-refusal-converts-to-coalesced-counterattack-charge',
        'wizardry-shadowward-retaliatory-split-and-recursion-exclusion',
    ]
    compared = []
    for key in comparisons:
        row = next(row for row in rows if row['semantic_dedup_key'] == key)
        compared.append({'key': key, 'record_sha256': sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                         'prior_source_chain_reread_claimed': False, 'extra_credit': 0})
    assert all('Gammaroach' not in ref['source_path'] for row in rows for ref in row['source_refs'])
    key = 'alexscaves-native-successful-hurt-and-unmarked-attacker-qualified-persisted-counter-spray'
    assert ledger_path.read_bytes() == before
    row = record(key, repo, refs,
        '实际GAMMAROACH实体/属性与client renderer注册；完整native hurt先执行super.hurt，保留返回值，'
        '仅成功且source.getEntity是Living且没有IRRADIATED时调用triggerSpraying。'
        'trigger仍需cooldown<=0及NO_ANIMATION，才调用喷射声、设置40tick SPRAY并消耗10000..33999tick冷却。'
        '每tick冷却递减，SprayCooldown写入并从NBT恢复；动画tick10构造无owner的IRRADIATED AreaEffectCloud，'
        '设置半径/等待/持续/缩小速度并尝试加入level；10..30其他tick产生喷雾粒子。'
        '原生模型按SPRAY作10tick抬起、20tick保持、10tick复位，setupAnim额外抖动；travel在喷射/冲撞时强制输入ZERO。'
        '自身canBeAffected拒IRRADIATED，目标goal反选已有该状态且非Raycat的Living，普通受伤报复goal另存。',
        '一条成功受伤+攻击者状态双限定、消耗持久冷却的原生行为回执实现1。'
        '不是按effect名称拆免疫：同一来伤可成功却因来源无Living/已辐射/已有动画/冷却而没有喷射回执；'
        '已标记者不触发新喷射，但仍可能被IRRADIATED目标goal追击。'
        '区别Forsaken由拒伤false预先充值合并boolean后AI消费、DeepOne成功hurt改变UUID声望跨档文字，'
        '以及Volatility伤害HEAD预结算消耗状态/网络粒子：本链按super返回成功和攻击者已有状态决定直接动作，'
        '动作一开始即扣长期冷却，未来cloud生成或任何目标实际受效失败都不回滚；动画未存档，冷却存档。'
        '喷射/粒子/声音不是免疫拒伤提示；恒定eyes材质也不是按免疫或命中状态点亮。'
        '整条限定反击/状态回执家族合并1，effect常量拒绝/目标predicate/模型帧/注册/两个动画都支持0。',
        'Boss灰字/微光须由权威拒绝结果产生，不能把既有条件反击动作当成每次hurt反馈。'
        '明确触发资格、长期冷却消费点、保存/重载中断及目标已带状态的行为，否则成功攻击与反馈缺席容易混淆。'
        '该链仅作相邻游戏实现研究，不据此改王朝免疫/生态或普通玩家体质需求。',
        '完整实体345行、完整renderer49行与model三个完整动画方法157..270已实际读。'
        '注册/属性及模组入口部分复用本轮已读固定证据，不计新链；无新下载。'
        '上游IrradiatedEffect、AreaEffectCloud原生引擎及Citadel动画网络/ACMath helper未展开，'
        '不声称受效/HP损失、喷射同步、实际像素或声音/TCP通过。'
        'entity tick/hurt/trigger没有独立server guard，addFreshEntity返回值也未检查，不能称双端只生成一次；'
        'cloud未setOwner、可能误及旁人，冷却不等于投射物受害者UUID节流。'
        '喷射声在动作入口而cloud延后10tick，被杀/动画中断时声音与冷却不证明云已生成。'
        'NBT只读写SprayCooldown；Fed未在此保存，动画也未保存。'
        'setSprayCooldown是同步字段但未验证底层网络及重载时钟，不把10000常量当真实秒数。'
        '完整旧5决策已作语义对比，不冒充本批重读其所有源链；28条retaliation关键词仅筛选不算阅读。'
        '0生产/游戏/清单删除/小时声明。',
        'native_damage_result_and_attacker_status_qualified_persisted_counter_feedback')
    dedup_path = O / 'semantic-dedup.json'
    dedup = json.loads(dedup_path.read_text())
    dedup['groups'].append({'family': 'hurt-and-attacker-mark-qualified-persisted-spray-20261102',
                            'credited_chains': [key],
                            'rationale': 'One atomic successful hurt and unmarked attacker policy with immediately consumed persistent cooldown and delayed animation consequence. Not refusal-to-charge, reputation-band cue, pre-settlement consumable status or constant-only effect immunity.'})
    dedup_path.write_text(json.dumps(dedup, ensure_ascii=False, indent=2) + '\n')
    receipt = {'recorded_at': datetime.now(timezone.utc).isoformat(),
               'decision': 'ACCEPT_ONE_NATIVE_SUCCESS_AND_ATTACKER_STATUS_QUALIFIED_COUNTER_FEEDBACK',
               'new_effective_credit': 1, 'key': key, 'source_commit': meta['commit'],
               'source_manifest_sha256': sha((source / 'source.json').read_bytes()),
               'source_tree_sha256': sha((source / 'tree.json').read_bytes()),
               'actual_source_ranges': checks, 'semantic_comparisons': compared,
               'prior_ledger_sha256': sha(before), 'observation': row['concrete_observation'],
               'limitations': row['limitations'], 'production_changes': 0, 'game_starts': 0,
               'checklist_deletions': 0, 'duration_hours_claimed': 0}
    with target.open('x') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    verify()
    print(json.dumps({'receipt': str(target.relative_to(R)), 'sha256': sha(target.read_bytes()),
                      'accepted_total': 458, 'remaining': 542}))


if __name__ == '__main__':
    main()
