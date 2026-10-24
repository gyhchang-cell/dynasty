"""Reproducible, machine-assisted comparison of external status/immunity call sites.

Counts implementation sites, not mods, pictures, tests or search results. Excerpts
are for reference only; nothing from this corpus is copied into game resources.
"""
from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / 'build/creature-reference-1000'
OUT = ROOT / 'docs/cod4/audit-20261022'
RULES = {
    'canBeAffected': '在原生效果接受入口判断免疫，避免只挡住自家施加函数。',
    'isPotionApplicable': '旧版效果接受入口；仅比较机制，不复制旧版API。',
    'isInvulnerableTo': '区分伤害免疫与状态免疫，不能用不受伤代替拒绝状态。',
    'fireImmune': '元素免疫按实际能力判定，不能根据名字猜测。',
    'addEffect': '真实效果施加可能被拒绝，后续行为应核对接受结果。',
    'addPotionEffect': '旧版施加入口仅作机制参考，保留本项目原生效果系统。',
    'removeEffect': '解除走原生入口，使固定属性和客户端清除事件一并生效。',
    'removePotionEffect': '旧版解除入口仅作生命周期参考。',
    'hasEffect': '条件直接读取实时状态，避免另存会过期的免疫布尔值。',
    'isPotionActive': '旧版实时状态条件，与本项目hasEffect作机制对照。',
    'getEffect': '比较实际层数与持续时间，刷新不能冒充新增状态。',
}
CALL = re.compile(r'\b(' + '|'.join(RULES) + r')\s*\(')


def main():
    groups = collections.defaultdict(list)
    seen = set()
    for repo in sorted(CORPUS.iterdir()):
        source = repo / 'source.json'
        if not repo.is_dir() or not source.is_file():
            continue
        meta = json.loads(source.read_text())
        if not meta.get('sha') or not meta.get('repo'):
            continue
        for path in sorted(repo.rglob('*.java')):
            if any(p in path.parts for p in ('client', 'model', 'datagen')):
                continue
            raw = path.read_text(errors='replace')
            # Mask comments and strings without changing line/character positions.
            code = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                          lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), raw)
            for match in CALL.finditer(code):
                start = raw.rfind('\n', 0, match.start()) + 1
                end = raw.find('\n', match.end())
                if end < 0:
                    end = len(raw)
                # Keep enough neighboring logic to distinguish a real guard from a call name.
                start = raw.rfind('\n', 0, max(0, start - 1)) + 1
                end = raw.find('\n', min(len(raw), end + 1))
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
    assert available >= 1000, f'Only {available} distinct applicable sites; do not pad the count'
    selected = []
    while groups and len(selected) < 1000:
        for key in list(groups):
            selected.append(groups[key].pop(0))
            if not groups[key]:
                del groups[key]
            if len(selected) == 1000:
                break
    summary = {
        'scope': 'COD4-8 native status acceptance, immunity, removal and lifecycle',
        'method': 'Machine-assisted source comparison; representative manual inspection. Not 1000 independently playtested features.',
        'count_unit': 'Distinct external implementation excerpts; whitespace-normalized SHA256 deduplication',
        'implementation_sites': len(selected), 'distinct_available': available,
        'repositories': dict(collections.Counter(r['repo'] for r in selected)),
        'operations': dict(collections.Counter(r['operation'] for r in selected)),
        'conclusions': list(RULES.values()),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'status-reference-1000.json').write_text(json.dumps({'summary': summary, 'sites': selected}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
