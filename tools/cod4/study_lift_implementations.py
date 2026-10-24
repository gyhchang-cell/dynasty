"""Reproducible, machine-assisted comparison of external entity movement/knockback call sites.

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
RULES = {'getDeltaMovement': '读取当前真实速度；命中前后速度差与真实上移共同判断，不能只看持有武器名称。', 'setDeltaMovement': '运动修改属于原玩法入口；表现只观察既有结果，不为弧光额外修改速度。', 'knockback': '原生击退可能被抗性或事件取消；成功受伤不等于成功抬升。', 'onGround': '真实落地状态控制空中反馈结束，不能播放虚构的固定浮空轨迹。', 'isOnGround': '旧版地面条件仅供生命周期对照，不能直接复制旧API。', 'setMotion': '旧版速度设置只供机制比较；保留本项目现有原生物理结算。', 'getMotion': '旧版真实速度读取；速度与位置都要核对。', 'moveRelative': '局部方向运动与世界坐标不同，方向和速度不能混用。', 'travel': '原生移动与重力负责实际轨迹，客户端弧光跟随实体插值位置。'}
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
        'scope': 'COD4-3 longarm lift feedback: native impulse, actual displacement and landing',
        'method': 'Machine-assisted source comparison; representative manual inspection. Not 1000 independently playtested features.',
        'count_unit': 'Distinct external implementation excerpts; whitespace-normalized SHA256 deduplication',
        'implementation_sites': len(selected), 'distinct_available': available,
        'repositories': dict(collections.Counter(r['repo'] for r in selected)),
        'operations': dict(collections.Counter(r['operation'] for r in selected)),
        'conclusions': list(RULES.values()),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'lift-reference-1000.json').write_text(json.dumps({'summary': summary, 'sites': selected}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
