"""Read existing armor recipes and actual FTB acquisition tasks, never icons.

Data correlation only: no survival, style, wearing, reference or gameplay credit.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools/art'))
from quest_snbt import list_compounds, object_id


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    out = ROOT / 'docs/cod4/audit-20261022/armor-acquisition-integration-20261102.json'
    assert not out.exists(), 'Preserve prior receipt'
    inputs = {}

    def read(path):
        raw = path.read_bytes()
        inputs[str(path.relative_to(ROOT))] = sha(raw)
        return raw.decode()

    inventory_path = ROOT / 'docs/cod4/audit-20261022/armor-priority-inventory-20261102.json'
    inventory = json.loads(read(inventory_path))
    families = [row['set'] for row in inventory['rows']]
    items = {'dynasty:' + family + '_' + part for family in families
             for part in ('helmet', 'chestplate', 'leggings', 'boots')}
    assert len(items) == 112 and len(families) == 28
    gear = ROOT / 'src/main/java/com/dynasty/DynastyGear.java'
    assert sha(gear.read_bytes()) == inventory['source_sha256'][str(gear.relative_to(ROOT))]
    read(gear)
    recipes = {item: [] for item in items}
    unsupported = []
    for path in sorted((ROOT / 'src/main/resources/data/dynasty/recipes').rglob('*.json')):
        raw = path.read_bytes()
        data = json.loads(raw)
        result = data.get('result', {})
        item = result.get('item') if isinstance(result, dict) else result
        if item not in items:
            continue
        inputs[str(path.relative_to(ROOT))] = sha(raw)
        kind = data.get('type')
        cost = Counter()

        def ingredient(value, times=1):
            if not isinstance(value, dict) or not ({'item', 'tag'} & value.keys()):
                unsupported.append({'recipe': str(path.relative_to(ROOT)), 'ingredient': value})
                return
            cost[value['item'] if 'item' in value else '#' + value['tag']] += times

        if kind == 'minecraft:crafting_shapeless':
            for value in data['ingredients']:
                ingredient(value)
        elif kind == 'minecraft:crafting_shaped':
            symbols = Counter(''.join(data['pattern']).replace(' ', ''))
            for symbol, times in symbols.items():
                ingredient(data['key'][symbol], times)
        elif kind == 'minecraft:smithing_transform':
            for name in ['template', 'base', 'addition']:
                ingredient(data[name])
        else:
            unsupported.append({'recipe': str(path.relative_to(ROOT)), 'type': kind})
        recipes[item].append({'path': str(path.relative_to(ROOT)), 'sha256': sha(raw),
                              'type': kind, 'result_count': result.get('count', 1) if isinstance(result, dict) else 1,
                              'direct_cost': dict(sorted(cost.items())),
                              'armor_predecessors': sorted(i for i in cost if i in items),
                              'result_nbt': result.get('nbt') if isinstance(result, dict) else None})
    quests, duplicate_ids = {}, []
    acquisition = {item: [] for item in items}
    for path in sorted((ROOT / 'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
        raw = read(path)
        for block in list_compounds(raw, 'quests'):
            qid = object_id(block).lower()
            if qid in quests:
                duplicate_ids.append(qid)
            inner = '\n'.join(line[2:] if line.startswith('\t\t') else line for line in block.splitlines())
            title = re.search(r'^\ttitle:\s*("(?:\\.|[^"\\])*")', inner, re.M)
            dep = re.search(r'^\tdependencies:\s*\[([^\]]*)\]', inner, re.M)
            tasks = list_compounds(inner, 'tasks')
            node = {'quest_id': qid, 'title': json.loads(title[1]) if title else None,
                    'source': str(path.relative_to(ROOT)), 'line': raw.count('\n', 0, raw.index(block)) + 1,
                    'dependencies': [s.lower() for s in re.findall(r'"([0-9a-fA-F]{16})"', dep[1])] if dep else [],
                    'rewards_sha256': sha('\n'.join(list_compounds(inner, 'rewards')).encode())}
            quests[qid] = node
            for task in tasks:
                if not re.search(r'\btype:\s*"item"', task):
                    continue
                match = re.search(r'\bitem:\s*\{\s*id:\s*"([^"]+)"', task)
                if match and match[1] in items:
                    acquisition[match[1]].append({**node, 'actual_item_task': task,
                                                 'task_id': object_id(task),
                                                 'explicit_consume_items': re.search(r'\bconsume_items:\s*(true|false)', task)[1]
                                                 if re.search(r'\bconsume_items:\s*(true|false)', task) else None})
    missing_deps = [{'quest': qid, 'missing': dep} for qid, q in quests.items()
                    for dep in q['dependencies'] if dep not in quests]
    rows = []
    for family in families:
        for part in ('helmet', 'chestplate', 'leggings', 'boots'):
            item = 'dynasty:' + family + '_' + part
            rows.append({'item': item, 'family': family, 'recipes': recipes[item],
                         'existing_acquisition_tasks': acquisition[item],
                         'status': 'EXISTING_RECIPE_AND_ACTUAL_ITEM_TASK' if recipes[item] and acquisition[item]
                                   else 'MISSING_RECIPE_OR_DIRECT_ITEM_TASK_REQUIRES_MANUAL_REVIEW'})
    # Recheck every captured byte before persisting a structural review.
    assert all(sha((ROOT / path).read_bytes()) == expected for path, expected in inputs.items())
    missing = [row['item'] for row in rows if not row['recipes'] or not row['existing_acquisition_tasks']]
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
              'status': 'STRUCTURAL_ARMOR_ACQUISITION_LINKS_PRESENT' if not (unsupported or duplicate_ids or missing_deps or missing) else 'REVIEW_REQUIRED',
              'sets': len(families), 'items': len(items), 'quest_nodes': len(quests),
              'matched_recipes': sum(len(r['recipes']) for r in rows),
              'matched_actual_item_tasks': sum(len(r['existing_acquisition_tasks']) for r in rows),
              'missing_recipe_or_direct_item_task': missing, 'unsupported_recipe_shapes': unsupported,
              'duplicate_quest_ids': duplicate_ids, 'missing_dependencies': missing_deps,
              'rows': rows, 'inputs_sha256': inputs,
              'tool_sha256': sha(Path(__file__).read_bytes()),
              'production_mutations': 0, 'new_quest_nodes': 0, 'art_mutations': 0,
              'research_credit': 0, 'native_acceptance_credit': 0, 'checklist_deletions': 0,
              'limitations': [
                  'Generated-list structural reader, not arbitrary SNBT parser; exact item task type required.',
                  'Task/recipe presence does not establish material natural reachability, stage pacing or wearing.',
                  'Item acquisition only, not NBT-variant acquisition, equipped detection or complete-set advancement coverage.',
                  'Absent consume_items is not interpreted as either true or false without native FTB consumer review.',
                  'No quest IDs, task IDs, rewards, prerequisites, recipes, saves or specialist art changed.',
                  'No new art/production reference-gate satisfaction inferred.'
              ]}
    with out.open('x') as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'items', 'matched_recipes', 'matched_actual_item_tasks',
                                          'missing_recipe_or_direct_item_task', 'unsupported_recipe_shapes']}))
    for family in families:
        row = next(r for r in rows if r['item'] == 'dynasty:' + family + '_helmet')
        print(family, json.dumps({'helmet_cost': [r['direct_cost'] for r in row['recipes']],
                                'direct_item_tasks_for_four_parts': [len(r['existing_acquisition_tasks']) for r in rows if r['family'] == family]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
