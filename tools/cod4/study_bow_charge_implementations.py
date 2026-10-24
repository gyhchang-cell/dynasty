"""Reproducible, machine-assisted comparison of external entity item-use lifecycle and charge timing call sites.

Counts implementation sites, not mods, pictures, tests or search results. Excerpts
are for reference only; nothing from this corpus is copied into game resources.
"""
from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CORPORA = [ROOT / 'build/creature-reference-1000', ROOT / 'build/item-use-references']
OUT = ROOT / 'docs/cod4/audit-20261022'
RULES = {
'getChargeDuration':'原生弩或武器蓄力完成阈值与普通弓不同，界面应读取武器自己的时长。',
'getChargeTime':'武器专属蓄力阈值要与释放路径对照，不能按统一动画时长猜测。',
'getCrossbowChargeDuration':'弩的原生装填时长属于独立机制，不等于弓箭完整拉弓。',
'onArrowLoose':'原生放箭事件可能取消或调整蓄力，提示不能额外触发释放结算。',
'onArrowNock':'原生搭箭入口可能拒绝弹药/使用；只有实际开始使用才显示提示。',
'findAmmo':'原有弹药筛选决定能否开始射击；提示不自行制造或扣除弹药。',
'getProjectile':'原生射弹选择与主副手使用配对，不根据背包里存在一把弓就显示。',
'getArrowVelocity':'旧版/自定义箭速曲线判断实际饱和阈值，不能把起弓当满蓄。',
'getProjectileVelocity':'原释放速度曲线供满蓄阈值对照，提示不得修改箭速。',
'getPullTime':'自定义拉弓所需时长应与释放饱和条件对应，避免提前宣告满蓄。',
'getMaxChargeTime':'自定义武器最大蓄力时长只供实际阈值比较，保留原结算。',
'getChargeTicks':'真实武器蓄力计时读取，展示不新增平行计时或持续存档标志。',
'getMaxUseTime':'Fabric命名的总使用时长，需与同一活动物品和实际释放曲线对应。',
'getUseAction':'Fabric命名的动作类型，弓/弩/食物动作不能误用同一满蓄判定。',
'usageTick':'Fabric原生使用更新；反馈不新增独立的蓄力时钟。',
'onStoppedUsing':'Fabric释放入口归原生玩法所有，提示不得额外消费或发射。',
'getItemUseTime':'Fabric读取实际使用时长，暂停和取消不能留下旧读数。',
'getItemUseTimeLeft':'Fabric剩余使用时长与当前活动物品配对，不能读取闲置手。',
'setCurrentHand':'Fabric开始原生使用，展示只观察，不能主动替玩家拉弓。',
'getActiveItem':'Fabric活动物品身份与当前手配对，换手后提示立即退出。',
'getPullProgress':'Fabric拉弓曲线的实际饱和阈值，视觉蓄满必须等于真实释放能力。',
'getUseItem':'读取正在使用的原生物品，避免把闲置主手弓当成实际副手动作。',
'getUsedItemHand':'活动手用于校对当前物品身份，换手后原满蓄提示不能残留。',
'getActiveHand':'旧版活动手逻辑只供对照，实际反馈必须读取当前原生活动手。',
'getMaxItemUseDuration':'旧版总使用时长必须与剩余时长配对，不能直接当成拉弓阈值。',
'getItemUseAction':'旧版使用动画区分弓、食物和格挡，避免相似动作误触发。',
'onPlayerStoppedUsing':'旧版释放结算对照：反馈只读，不吞掉原有发射/弹药/耐久。',
'onUsingTick':'旧版原生使用更新对照：取消使用就停止更新提示。',
'getItemInUseDuration':'旧版实际使用时长对照；不能把全局世界时间当作拉弓时长。',
'isCharged':'原生弩弹仓状态与弓满蓄状态不同，不能共用提示条件。',
'getTicksUsingItem':'以原生持续使用计时读取拉弓进度，不能按持有时长推算。',
'getUseItemRemainingTicks':'剩余使用时长应与同一个活动物品配对；释放或换手后停止提示。',
'getUseDuration':'各物品的原生使用总时长不同，不能把通用食物或弩计时套到弓上。',
'isUsingItem':'只有真实持续使用状态才显示；取消使用后立即清除。',
'startUsingItem':'原输入负责开始使用；反馈不主动拉弓或绕过弹药检查。',
'releaseUsing':'释放仍归原生武器结算，满蓄提示不额外发射或扣弹。',
'getPowerForTime':'按照原生弓蓄力曲线判断满蓄，不能以动画颜色代替实际阈值。',
'getUseAnimation':'区分弓、弩、格挡、饮用，不能让无关使用动作触发满蓄提示。',
'stopUsingItem':'停止/切换物品必须同步退出展示，避免留下永久满蓄标识。',
'onUseTick':'逐次原生使用更新；反馈读取当前进度，不新增独立玩法时钟。',
'useOnRelease':'部分物品在释放后才结算，展示不能提前改变结算行为。',
'getItemInUseCount':'旧版原生使用计时仅用于生命周期对照，不能直接复制旧API。',
'isHandActive':'旧版活动手状态仅供比较，保持当前版本真实使用手一致。',
'getActiveItemStack':'旧版活动物品读取需要与主手/副手身份对应，不能误读闲置弓。',
}
CALL = re.compile(r'\b(' + '|'.join(RULES) + r')\s*\(')


def main():
    groups = collections.defaultdict(list)
    seen = set()
    for repo in sorted(path for corpus in CORPORA if corpus.exists() for path in corpus.iterdir()):
        source = repo / 'source.json'
        if not repo.is_dir() or not source.is_file():
            continue
        meta = json.loads(source.read_text())
        if not meta.get('sha') or not meta.get('repo'):
            continue
        for path in sorted(repo.rglob('*.java')):
            if any(p in path.parts for p in ('model', 'datagen')):
                continue
            raw = path.read_text(errors='replace')
            # Mask comments and strings without changing line/character positions.
            code = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                          lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), raw)
            for match in CALL.finditer(code):
                # Generic entity/energy "charged" state is not an item-draw implementation.
                if match[1] in {'isCharged','getChargeTime','getChargeDuration','getChargeTicks','getMaxChargeTime'} and not any(term in str(path.relative_to(repo)).lower() for term in ('item','bow','weapon','staff','overlay','hud')):
                    continue
                start = raw.rfind('\n', 0, match.start()) + 1
                end = raw.find('\n', match.end())
                if end < 0:
                    end = len(raw)
                # Keep enough neighboring logic to distinguish a real guard from a call name.
                start = raw.rfind('\n', 0, max(0, start - 1)) + 1
                for _ in range(7):
                    next_end = raw.find('\n', min(len(raw), end + 1))
                    if next_end < 0:
                        end = len(raw)
                        break
                    end = next_end
                if end < 0:
                    end = len(raw)
                excerpt = raw[start:end].strip()
                fingerprint = hashlib.sha256(re.sub(r'\s+', '', excerpt).encode()).hexdigest()
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                relative = path.relative_to(repo).as_posix()
                line = raw.count('\n', 0, match.start()) + 1
                key = match[1]
                groups[(meta['repo'], key)].append({
                    'repo': meta['repo'], 'revision': meta['sha'],
                    'path': relative, 'line': line, 'operation': key,
                    'url': f"https://github.com/{meta['repo']}/blob/{meta['sha']}/{relative}#L{line}",
                    'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'excerpt_sha256': fingerprint, 'excerpt': excerpt,
                    'comparison': RULES[key],
                })
    available = sum(map(len, groups.values()))
    # Persist genuine partial progress rather than inventing sites to meet the threshold.
    selected = []
    while groups and len(selected) < 1000:
        for key in list(groups):
            selected.append(groups[key].pop(0))
            if not groups[key]:
                del groups[key]
            if len(selected) == 1000:
                break
    summary = {
        'scope': 'COD4-3 bow full-draw hint: native active-use lifecycle, cancellation, draw threshold and ownership',
        'method': 'Machine-assisted source comparison; representative manual inspection. Not 1000 independently playtested features.',
        'count_unit': 'Distinct external implementation excerpts; whitespace-normalized SHA256 deduplication',
        'implementation_sites': len(selected), 'distinct_available': available, 'complete':len(selected)==1000, 'shortfall':max(0,1000-len(selected)),
        'repositories': dict(collections.Counter(r['repo'] for r in selected)),
        'operations': dict(collections.Counter(r['operation'] for r in selected)),
        'conclusions': list(RULES.values()),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'bow-charge-reference-1000.json').write_text(json.dumps({'summary': summary, 'sites': selected}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
