"""Bind current COD4 recipes to existing quest nodes; writes audit evidence only.

Uses the repository's generated-list reader, not a general SNBT parser.
This checks structural integration, not natural survival or research completion.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/art'))
from quest_snbt import list_compounds, object_id

OUT = ROOT / 'docs/cod4/audit-20261022/quest-integration-20261030'
inputs = {}


def read(path):
    raw = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return raw.decode()


def field(block, name):
    match = re.search(r'^\t' + name + r':\s*"((?:\\.|[^"\\])*)"', block, re.M)
    return json.loads('"' + match[1] + '"') if match else None


quests = {}
duplicates = []
for path in sorted((ROOT / 'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
    raw = read(path)
    for block in list_compounds(raw, 'quests'):
        qid = object_id(block).lower()
        if qid in quests:
            duplicates.append(qid)
        inner = '\n'.join(line[2:] if line.startswith('\t\t') else line for line in block.splitlines())
        deps = re.search(r'^\tdependencies:\s*\[([^\]]*)\]', inner, re.M)
        quests[qid] = {
            'id': qid, 'title': field(inner, 'title'), 'chapter': path.stem,
            'source': str(path.relative_to(ROOT)), 'line': raw.count('\n', 0, raw.index(block)) + 1,
            'dependencies': [s.lower() for s in re.findall(r'"([0-9a-fA-F]{16})"', deps[1])] if deps else [],
            'tasks': list_compounds(inner, 'tasks'), 'rewards': list_compounds(inner, 'rewards'),
            'description': re.search(r'^\tdescription:.*$', inner, re.M)[0] if re.search(r'^\tdescription:.*$', inner, re.M) else '',
        }

missing = [{'quest': qid, 'dependency': dep} for qid, q in quests.items() for dep in q['dependencies'] if dep not in quests]
colors, stack, cycles = {}, [], []


def visit(qid):
    if colors.get(qid) == 1:
        cycles.append(stack[stack.index(qid):] + [qid])
        return
    if colors.get(qid) == 2 or qid not in quests:
        return
    colors[qid] = 1
    stack.append(qid)
    for dep in quests[qid]['dependencies']:
        visit(dep)
    stack.pop()
    colors[qid] = 2


for qid in quests:
    visit(qid)


def ancestors(qid):
    found, todo = set(), list(quests[qid]['dependencies'])
    while todo:
        dep = todo.pop()
        if dep not in found:
            found.add(dep)
            todo.extend(quests.get(dep, {}).get('dependencies', []))
    return sorted(found)


rows = []
errors = []
variant_reviews = []
for path in sorted((ROOT / 'src/main/resources/data/dynasty/recipes/cod4').glob('*.json')):
    recipe = json.loads(read(path))
    item = recipe['result']['item']
    advancement = 'dynasty:cod4_obtain_' + item.split(':')[1] if item.startswith('dynasty:') else None
    advpath = ROOT / 'src/main/resources/data/dynasty/advancements' / (advancement.split(':')[1] + '.json') if advancement else None
    adv = json.loads(read(advpath)) if advpath and advpath.exists() else None
    def acquisition_task(task):
        return bool((advancement and re.search(r'\badvancement:\s*"' + re.escape(advancement) + r'"', task)) or
                    re.search(r'\btype:\s*"item"', task) and re.search(r'\bitem:\s*(?:\{\s*id:\s*)?"' + re.escape(item) + r'"', task))
    nodes = [q for q in quests.values() if any(acquisition_task(t) for t in q['tasks'])]
    if not nodes:
        errors.append({'item': item, 'issue': 'no_existing_acquisition_quest'})
    if adv is None and any(advancement and advancement in t for q in nodes for t in q['tasks']):
        errors.append({'item': item, 'issue': 'missing_advancement'})
    ingredients = collections.Counter(v.get('item', '#' + v.get('tag', 'UNPARSED')) for v in recipe.get('ingredients', []))
    variant = recipe['result'].get('nbt')
    if variant:
        variant_reviews.append({'recipe': str(path.relative_to(ROOT)), 'base_item': item,
                                'variant_nbt': variant,
                                'status': 'BASE_ITEM_MATCH_DOES_NOT_VERIFY_VARIANT_TASK',
                                'required': 'Preserve NBT identity; verify original infusion/crafting receipt before adding any task or alias'})
    bound = []
    for q in nodes:
        same_reward = [r for r in q['rewards'] if item in r]
        if same_reward:
            errors.append({'item': item, 'quest': q['id'], 'issue': 'same_item_reward_requires_manual_review'})
        bound.append({k: q[k] for k in ['id', 'title', 'chapter', 'source', 'line', 'dependencies', 'description']})
        bound[-1].update(ancestor_ids=ancestors(q['id']), rewards=q['rewards'])
    rows.append({'item': item, 'recipe': str(path.relative_to(ROOT)), 'ingredients': dict(ingredients),
                 'produced': recipe['result'].get('count', 1), 'variant_nbt': variant, 'advancement': advancement,
                 'advancement_definition': adv, 'existing_nodes': bound})

# Reviewed design contracts for the six existing weapons; no new use restrictions.
contracts = {
    'repeating_crossbow': ['1000000000c40001'],
    'siege_crossbow': ['1000000000c40003', '100000000000018e'],
    'rope_dart': ['1000000000c40001'],
    'meteor_hammer': ['1000000000c40005', '100000000000018e'],
    'mandarin_duck_axe': ['1000000000c40002'],
    'flying_claw': ['1000000000c40001'],
}
for name, expected in contracts.items():
    row = next(r for r in rows if r['item'] == 'dynasty:' + name)
    if not row['existing_nodes'] or any(set(n['dependencies']) != set(expected) for n in row['existing_nodes']):
        errors.append({'item': row['item'], 'issue': 'reviewed_weapon_dependency_contract_changed'})

for name in ['ContentProgress.java', 'ProgressionMerchant.java']:
    read(ROOT / 'src/main/java/com/dynasty/expansion' / name)
report = {
    'scope': 'Current COD4 recipe outputs linked to existing FTB item or advancement acquisition objectives; recipe filename is not item identity',
    'status': 'STATIC_INTEGRATION_CHECK_PASS' if not (errors or missing or duplicates or cycles or variant_reviews) else 'REVIEW_REQUIRED',
    'quest_count': len(quests), 'cod4_recipe_count': len(rows), 'bound_quest_count': sum(len(r['existing_nodes']) for r in rows),
    'duplicate_quest_ids': duplicates, 'missing_dependencies': missing, 'dependency_cycles': cycles, 'issues': errors,
    'rows': rows, 'variant_reviews': variant_reviews, 'inputs_sha256': inputs,
    'manual_source_findings': [
        'Workshop starts after existing refined-steel quest; gear/cable precede initial weapons. Siege crossbow and meteor hammer also depend on existing story04 dragon-crystal acquisition.',
        'Siege recipe consumes repeating crossbow. Its quest text explicitly discloses this; acquisition advancements retain the earlier obtained fact.',
        'ContentProgress scans main inventory, hands, armor and active trinkets. Supplies are excluded from possession reconciliation and only awarded from actual crafting.',
        'Recipe-book discovery ranks are hints, not new basic use gates. Minister alternatives require rank3 or guard3, actual payment and saved daily per-player stock.',
        'Acquisition objectives do not prove skill use, successful combat, safe traversal or natural material reachability; those existing pending scopes remain.',
        'Four recipes produce existing base items with NBT variants. Their base-item quest matches alone are insufficient to claim variant-specific integration. Poison smoke produces vanilla lingering potion with cod4PoisonSmoke, not a separately registered poison_smoke_bomb item.',
    ],
    'research_credit_added': 0, 'native_acceptance_credit_added': 0, 'production_mutations': 0,
    'limitations': ['Generated-list structural reader only', 'No game launch or save access', 'No 2–3 hour pacing proof',
                    'No external-reference gate satisfaction inferred', 'No whole TODO removed from this static receipt'],
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'current-integration.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
lines = ['# 新增内容接入现有任务体系', '', '本表来自当前配方、任务节点与原生进度定义。仅为静态对应审查，不代替自然生存或客户端验收。', '',
         '| 物品 | 原任务节点 | 直接前置 | 配方投入 |', '|---|---|---|---|']
for row in rows:
    nodes = row['existing_nodes']
    label = row['item'] + ('（NBT变体，待核专用回执）' if row['variant_nbt'] else '')
    lines.append('| ' + label + ' | ' + ('; '.join(n['title'] + ' `' + n['id'] + '`' for n in nodes) or '未找到对应获取节点') + ' | ' +
                 '; '.join(', '.join(quests[d]['title'] for d in n['dependencies'] if d in quests) for n in nodes) + ' | ' +
                 ', '.join(f'{i}×{n}' for i, n in row['ingredients'].items()) + ' |')
lines += ['', '后续接入顺序：材料来源说明 → 现有备料/获取节点 → 制作/交易 → 使用提示 → 原生持有或制作回执。',
          '性能、特效与旧档迁移属于独立验收，不为完成任务而新增强制使用门槛或再次发奖。']
(OUT / 'integration-map.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({k: report[k] for k in ['status', 'quest_count', 'cod4_recipe_count', 'bound_quest_count', 'issues', 'missing_dependencies', 'dependency_cycles']}, ensure_ascii=False))
sys.exit(1 if report['status'] == 'REVIEW_REQUIRED' else 0)
