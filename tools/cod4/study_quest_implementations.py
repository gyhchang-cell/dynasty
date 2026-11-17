"""Read-only comparison of real external FTB objective/dependency/reward sites.

No pack files are modified or copied into the game. One quest counts once;
screenshots, descriptions and checkmark-only instructions do not count.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/art'))
from quest_snbt import list_compounds, object_id

PACKS = Path('/Users/a15356015027/Public/.minecraft/versions')
OUT = ROOT / 'docs/cod4/audit-20261022/quest-reference-1000.json'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    groups = collections.defaultdict(list)
    seen = set()
    accepted = {'item', 'advancement', 'kill', 'crafting', 'dimension', 'location', 'stat'}
    for file in sorted(PACKS.glob('*/config/ftbquests/quests/chapters/*.snbt')):
        pack = file.relative_to(PACKS).parts[0]
        if 'dynasty' in file.name.lower() or 'dynasty' in pack.lower():
            continue
        raw = file.read_text()
        for block in list_compounds(raw, 'quests'):
            inner = '\n'.join(line[2:] if line.startswith('\t\t') else line for line in block.splitlines())
            tasks = list_compounds(inner, 'tasks')
            rewards = list_compounds(inner, 'rewards')
            kinds = [m[1] for task in tasks if (m := re.search(r'\btype:\s*"([^"]+)"', task))]
            if not accepted.intersection(kinds):
                continue
            deps = re.search(r'^\tdependencies:\s*\[([^\]]*)\]', inner, re.M)
            dependencies = re.findall(r'"([0-9A-Fa-f]{16})"', deps[1]) if deps else []
            if not rewards and not dependencies:
                continue
            # Cosmetic placement, prose and fresh random object IDs cannot inflate the count.
            semantic = re.sub(r'\bid:\s*"[0-9A-Fa-f]{16}"', 'id:"OBJECT"', '\n'.join(tasks + rewards))
            fingerprint = digest(re.sub(r'\s+', '', semantic))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            comparisons = []
            if 'item' in kinds:
                consuming = any(re.search(r'\bconsume_items:\s*true', task) for task in tasks)
                comparisons.append('本例含提交消耗物品目标，检测与收取应分别核对；本项目原获得任务不应据此新增扣费。'
                                   if consuming else '本例物品目标未启用提交消耗；核对实际持有物与检测范围，不能根据说明或奖励名称判完成。')
            if 'advancement' in kinds:
                comparisons.append('原生成就完成是独立检测入口；保留既有ID和完成记录，不用描述文本代替进度。')
            if 'kill' in kinds:
                comparisons.append('击杀目标与原生击杀归属分开核对，不能由附近玩家持物冒领。')
            if dependencies:
                comparisons.append(f'本例有{len(dependencies)}个前置，前置解锁和目标检测是不同环节。')
            comparisons.append(f'本例配置{len(rewards)}个奖励对象；重复登录核对应只补进度/发现，不能主动重放奖励。')
            groups[(pack, kinds[0])].append({
                'pack': pack, 'file': str(file), 'quest': object_id(block),
                'line': raw.count('\n', 0, raw.index(block)) + 1,
                'file_sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'quest_sha256': digest(block),
                'semantic_sha256': fingerprint, 'task_types': kinds,
                'dependencies': dependencies, 'tasks': tasks, 'rewards': rewards,
                'observations': comparisons,
            })
    available = sum(map(len, groups.values()))
    assert available >= 1000, f'Only {available} applicable distinct quests; no padding permitted'
    sites = []
    while groups and len(sites) < 1000:
        for key in list(groups):
            sites.append(groups[key].pop(0))
            if not groups[key]:
                del groups[key]
            if len(sites) == 1000:
                break
    summary = {
        'scope': 'COD4-7 objective, ownership, predecessor and reward reconciliation',
        'method': 'Machine-assisted structural comparison, with representative manual source inspection; not 1000 playthroughs.',
        'count_unit': 'Distinct external quest objective/reward implementations; IDs and whitespace excluded from semantic deduplication',
        'count': len(sites), 'available': available,
        'packs': dict(collections.Counter(s['pack'] for s in sites)),
        'task_types': dict(collections.Counter(t for s in sites for t in s['task_types'])),
        'application': [
            'Read original inventories including offhand when reconciling owned gear.',
            'Keep crafted consumable objectives distinct from merely possessing consumables.',
            'Use native advancement and recipe-book receipts; never introduce a second reward ledger.',
            'Check repeated login, save/load, original counts/NBT and independent player ownership.',
        ],
    }
    OUT.write_text(json.dumps({'summary': summary, 'sites': sites}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
