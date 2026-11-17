"""Freeze bounded manual native-consumer review; this awards no research credit."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/cod4/audit-20261022'
CAPTURE = AUDIT / 'armor-itemtask-native-20261102'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    bindings = []
    for filename in ['capture.json', 'extra-capture.json']:
        capture = json.loads((CAPTURE / filename).read_text())
        for row in capture['bindings']:
            jar = ROOT / row.get('jar', 'modpack/mods/ftb-quests-forge-2001.4.22.jar')
            expected = row.get('jar_sha256', capture.get('jar_sha256'))
            assert sha(jar.read_bytes()) == expected
            with zipfile.ZipFile(jar) as archive:
                assert sha(archive.read(row['entry'])) == row['class_sha256']
            assert sha((ROOT / row['javap']).read_bytes()) == row['javap_sha256']
            bindings.append(row)
    selected = {
        'quest_task_ItemTask': ['consumesResources(', 'submitTask(', 'countMatchingItems(',
                                'boolean test(net.minecraft', 'shouldMatchNBT(',
                                'hasNBTCheckTag(', 'canInsertItem('],
        'quest_Chapter': ['boolean consumeItems('],
        'config_Tristate': ['read(net.minecraft.nbt.', 'boolean get(', 'boolean isTrue(', 'boolean isDefault('],
        'util_FTBQuestsInventoryListener': ['void detect(', 'void buildInventorySummary(',
                                            'lambda$detect$0(', 'lambda$buildInventorySummary$3('],
        'integration_item_filtering_ItemMatchingSystem': ['doesItemMatch(', 'areItemStacksEqual('],
        'util_NBTUtils': ['compareNbt(', 'lambda$compareNbt$'],
        'quest_task_ItemTask$1': ['static {}'],
        'api_FTBQuestsTags$Items': ['static {}'],
    }
    reviewed = []
    for stem, selectors in selected.items():
        path = CAPTURE / (stem + '.javap.txt')
        text = path.read_text()
        for match in re.finditer(r'^  (?:public|private|protected|static) .*?(?=^  (?:public|private|protected|static) |\Z)', text, re.M | re.S):
            block = match.group()
            if any(s in block.split('\n', 1)[0] for s in selectors):
                reviewed.append({'file': str(path.relative_to(ROOT)),
                                 'method': block.split('\n', 1)[0].strip(),
                                 'lines': [text.count('\n', 0, match.start()) + 1,
                                           text.count('\n', 0, match.end())],
                                 'excerpt_sha256': sha(block.encode())})
    native = (CAPTURE / 'quest_BaseQuestFile.javap.txt').read_text()
    assert 'String default_consume_items' in native and 'isDefaultTeamConsumeItems()' in native
    mapping = Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/de/oceanlabs/mcp/mcp_config/1.20.1-20230612.114412/srg_to_official_1.20.1.tsrg')
    assert '\tf_35974_ items' in mapping.read_text()
    config_path = ROOT / 'modpack/config/ftbquests/quests/data.snbt'
    config = config_path.read_bytes()
    assert re.search(rb'^\s*default_consume_items:\s*false\s*$', config, re.M)
    audit_path = AUDIT / 'armor-acquisition-integration-20261102.json'
    audit = json.loads(audit_path.read_text())
    tasks = []
    chapter_hashes = {}
    for item in audit['rows']:
        for task in item['existing_acquisition_tasks']:
            chapter = ROOT / task['source']
            chapter_text = chapter.read_text()
            # These generated chapter files have one top-level quests list.
            assert chapter_text.count('\tquests: [') == 1
            header = chapter_text.split('\tquests: [', 1)[0]
            overrides = re.findall(r'^\s*consume_items:\s*(true|false)\s*$', header, re.M)
            assert len(overrides) <= 1
            chapter_value = overrides[0] == 'true' if overrides else False
            explicit = task['explicit_consume_items']
            assert explicit in [None, 'true', 'false']
            value = explicit == 'true' if explicit is not None else chapter_value
            tasks.append({'item': item['item'], 'quest': task['quest_id'], 'task': task['task_id'],
                          'explicit': explicit, 'chapter_override': overrides[0] if overrides else None,
                          'effective_consume_items': value})
            chapter_hashes[task['source']] = sha(chapter.read_bytes())
    assert len(tasks) == 154 and not any(t['effective_consume_items'] for t in tasks)
    src = Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
    with zipfile.ZipFile(src) as archive:
        inventory = archive.read('net/minecraft/world/entity/player/Inventory.java')
    report = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'NATIVE_ITEMTASK_CONSUMER_BOUNDARIES_REVIEWED_ACCEPTANCE_PENDING',
        'capture_binding_count': len(bindings), 'reviewed_full_methods': reviewed,
        'partial_bytecode_review': {'file': 'quest_BaseQuestFile.javap.txt',
            'constructor_offsets': [125, 127], 'readData_offsets': [16, 24],
            'getter': 'isDefaultTeamConsumeItems',
            'note': 'Only this field initialization/read and complete getter reviewed; not whole 5000-line class.'},
        'findings': [
            'Absent consume_items reads Tristate.DEFAULT; task inherits chapter then file. Current file false and all four matching chapter headers lack override: all 154 armor item tasks are non-consuming (46 explicit false, 108 inherited).',
            'Non-consuming normal submit scans cached Inventory.items only (36 main/hotbar slots), counts matches capped at requested count and only raises progress. Worn armor/offhand are separate lists, so an item task is not wearing proof and wearing before scan can miss possession detection.',
            'Craft-only non-consuming branch adds matching supplied craft stack count. Consuming branch acts only with empty craft argument, loops Inventory.items, applies insert returned remainder and notifies inventory/menu. Acquisition evidence is not recipe ingredient payment evidence.',
            'Native submit checks taskScreenOnly, task sequence, completion and MissingItem. Outer inventory listener requires live ServerQuestFile, nonfake player, team, canStartTasks and selected submit/crafting list. Event registration/list classification and full native runtime were not expanded.',
            'Default matchNBT is item-tag conditional (ftbquests:match_nbt or itemfilters:check_nbt), not inferred from item having a tag. TRUE/FALSE/default switch independently verified. Ordinary comparator checks Item identity, then optional NBT; explicit match_nbt:true is necessary for deliberate variant tasks unless native tagged policy is independently established.',
            'NBT strict comparator requires equal compound key sets and recursively equal values/types; weak mode allows extra candidate keys. List comparison remains size/order sensitive. Null template accepts any NBT. Additional filter adapters can override comparator and are outside this review.',
            'Three cloth recipe outputs have no direct item task, but this is not proven missing required gameplay: existing catalog explicitly permits free query and cloth helmet is a prep node. No redundant reward or invented all-cloth task was added.',
        ],
        'armor_tasks': tasks,
        'unaccepted': ['natural materials and recipe payment', 'stage pacing and equipped builds',
                       'current native FTB events/save/reopen and multiplayer',
                       'four exact NBT acquisition variants and poison payment'],
        'source_bindings': {'acquisition_audit_sha256': sha(audit_path.read_bytes()),
                            'config_sha256': sha(config), 'chapter_sha256': chapter_hashes,
                            'mapping': str(mapping), 'mapping_sha256': sha(mapping.read_bytes()),
                            'mapping_line': 143249, 'mapping_value': 'f_35974_ items',
                            'inventory_source_jar': str(src), 'inventory_source_jar_sha256': sha(src.read_bytes()),
                            'inventory_entry_sha256': sha(inventory), 'inventory_inspected_lines': [1, 78]},
        'tool_sha256': sha(Path(__file__).read_bytes()),
        'game_starts': 0, 'production_mutations': 0, 'new_quest_ids': 0,
        'reference_credit': 0, 'checklist_deletions': 0,
        'limitations': ['Bytecode reading does not execute native events.',
                        'Nine captured classes do not imply nine complete source reviews or semantic references.',
                        'No current dynamic tag, filter-adapter or event behavior was claimed.'],
    }
    target = AUDIT / 'coordinator-armor-itemtask-native-review-20261102.json'
    with target.open('x') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'armor_tasks': len(tasks),
                      'effective_consume_true': 0, 'full_methods_reviewed': len(reviewed),
                      'reference_credit': 0}))


if __name__ == '__main__':
    main()
