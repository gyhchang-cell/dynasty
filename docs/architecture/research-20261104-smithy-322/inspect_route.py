"""Bounded source-only route supplement; never starts Java or edits source assets."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


assert not (OUT / 'RECEIPT.json').exists(), 'Sealed batch must remain immutable'
old = ROOT / 'docs/architecture/research-20261104-smithy-206'
manual_raw = (old / 'manual-review.json').read_bytes()
manual = json.loads(manual_raw)
source = manual['source']
archive = Path(source['source_archive'])
assert sha(archive.read_bytes()) == source['source_archive_sha256']
with zipfile.ZipFile(archive) as z:
    raw = z.read(source['member'])
assert sha(raw) == source['nbt_sha256']
n = read(raw)
cells = {tuple(b['pos']): b for b in n['blocks']}
assert len(cells) == len(n['blocks'])

# Ordered supports, not a native pathfinding result. +Z is south, +X east.
route = [(2,2,5),(2,3,6),(2,4,7),(2,5,8),(3,5,8),
         (4,6,8),(5,6,8),(6,6,8),(7,5,8),(8,5,8),
         (9,5,8),(9,5,7),(9,5,6),(10,5,6),(10,5,5)]
coords = {(x,y+d,z) for x,y,z in route for d in range(4)}
coords.update((8,y,7) for y in range(5,9))
records = []
for p in sorted(coords):
    b = cells.get(p)
    records.append({'pos': list(p), 'stored': b is not None,
                    'palette_index': b['state'] if b else None,
                    'state': n['palette'][b['state']] if b else None,
                    'block_entity': b.get('nbt') if b else None})
assert all(r['stored'] for r in records)
save('selected-original-states.json', records)
save('source-binding.json', {
    'archive': str(archive), 'archive_sha256': source['source_archive_sha256'],
    'member': source['member'], 'nbt_sha256': sha(raw),
    'old_manual_sha256': sha(manual_raw), 'positions': len(records),
    'images': [{'path': str(old / name), 'sha256': sha((old/name).read_bytes()),
                'actually_viewed_this_batch': True}
               for name in ['F01-cutaway.png','F01-vertical.png','F01-y6.png']],
    'new_whole_building_study': False, 'new_generator_context_read': 0})

bad = '345省略非air'
good = '345省略unknown（不能判air或nonair）'
assert manual['seven_dimensions']['proportion'].count(bad) == 1
effective = copy.deepcopy(manual)
effective['seven_dimensions']['proportion'] = effective['seven_dimensions']['proportion'].replace(bad, good)
restored = copy.deepcopy(effective)
restored['seven_dimensions']['proportion'] = restored['seven_dimensions']['proportion'].replace(good,bad)
assert restored == manual
save('separate-206-erratum.json', {
    'target': str(old/'manual-review.json'), 'target_sha256': sha(manual_raw),
    'field': 'seven_dimensions.proportion', 'replace_exact_once': bad,
    'replacement': good, 'original_file_modified': False,
    'effective_copy_only_exact_phrase_changes': restored == manual,
    'reason': '2618 declared minus 2273 stored leaves 345 unknown, not classified nonair.'})

support_heights = [3,4,5,6,6,6.5,6.5,6.5,6,6,6,6,6,6,6]
save('manual-route-review.json', {
    'batch': 322, 'case': 'existing 206 F01',
    'question': '低室floor2至东侧floor5工作区是否有此前漏查的静态候选绕行线',
    'ordered_supports': [list(p) for p in route],
    'nominal_full_support_top_heights': support_heights,
    'observations': [
        '低室2,2,5顶面3；沿+Z的2,3,6、2,4,7、2,5,8三块south/bottom/straight阶梯，逐级高1，其低半/高半组合提示连续阶梯，而非孤立装饰阶。各阶上方三格保存为air。',
        '2,5,8后向东到3,5,8 west/top阶，顶面同为6；4/5/6,6,8为bottom半砖，名义顶面6.5，非整方块7。它们上方y7/8/9为air。',
        '向东降至7,5,8 east/top阶、8,5,8 y轴去皮云杉木、9,5,8 south/top阶，顶面6。再向北到9,5,7和9,5,6的top半砖；可转10,5,6及10,5,5两块top半砖，靠近双锅工作带。',
        '8,6,7栅栏仅north=true/south=false；候选走z8中心再在x9转北，绕过末端，没有声称穿过栅栏。8,7,7是air仍不能把下方栅栏视作可穿越air。',
        '路线只从低室内部一处地面开始；没有补证外部生成地形、门外到地面全过程、NPC寻路、实际碰撞或付款交互。',
        '旧类色图将薄阶/半砖按方格示意，不能从图片读出半格表面；本次以原palette属性补充。'
    ],
    'bounded_conclusion': '发现有连续支撑与上方显式air的南侧阶梯—檐边绕行候选；旧未证登临原因得到更具体的静态补充，但实际可行路线仍未验收。',
    'limits': ['No native collision/pathfinding test; no Java/game.',
               'Not an accessible safe public staircase certification; narrow exposed ledge and half-step transitions remain.',
               'No new complete building, no new formal/reference credit, no production gate opened.',
               'No NPC06 credit transfer from NPC01/NPC05 or old COD4 references.'],
    'formal_credit_added': 0, 'new_reference_proposal': 0,
    'applicable_total': None, 'applicable_gap': None,
    'historical_cod4_total_unchanged': 153, 'historical_cod4_gap_unchanged': 847,
    'production_gate_met': False, 'native_acceptance': False,
    'status': 'STATIC_ROUTE_CANDIDATE_NATIVE_UNVERIFIED_HOLD_ZERO'})

checks = {
    'archive_and_member_pins_match': True,
    'all_selected_positions_explicitly_stored': all(r['stored'] for r in records),
    'route_supports_are_not_air': all(n['palette'][cells[p]['state']]['Name'] != 'minecraft:air' for p in route),
    'route_above_supports_explicit_air': all(n['palette'][cells[(x,y+d,z)]['state']]['Name'] == 'minecraft:air' for x,y,z in route for d in (1,2,3)),
    'route_axis_adjacent': all(abs(a[0]-b[0])+abs(a[2]-b[2]) == 1 for a,b in zip(route,route[1:])),
    'nominal_support_height_change_at_most_one': all(abs(a-b)<=1 for a,b in zip(support_heights,support_heights[1:])),
    'erratum_only_exact_phrase': restored == manual,
    'old_manual_unchanged': (old/'manual-review.json').read_bytes() == manual_raw,
}
assert all(checks.values()), checks
save('verification.json', {'scope': 'Source-state consistency only, not native passage acceptance', 'checks': checks})
for r in records:
    print(r['pos'], r['palette_index'], json.dumps(r['state'],ensure_ascii=False,separators=(',',':')))
print('CHECKS',json.dumps(checks))
