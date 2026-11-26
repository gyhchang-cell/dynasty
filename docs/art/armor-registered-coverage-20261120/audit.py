from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ART = ROOT / 'docs/art'
ASSETS = ROOT / 'src/main/resources/assets/dynasty'
JAVA = ROOT / 'src/main/java/com/dynasty'
RES = ROOT / 'src/main/resources'
V15 = ART / 'remaining-textures-v15/source-install-receipt.json'
V7 = ART / 'vanilla-materials-v7/manifest.json'
INVENTORY = ART / 'armor-continuation-20261102/version-inventory.json'
VISUAL = ART / 'armor-continuation-20261102/visual-review.json'
PRIOR_ID_INDEX = ART / 'armor-target-path-index-20261114/targets.json'

def read(path):
    return json.loads(path.read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def hash_file(path):
    return sha(path.read_bytes())

def relative(path):
    return str(path.relative_to(ROOT))

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def evidence(path):
    return {'path': relative(path), 'sha256': hash_file(path)}

def file_history(path):
    rows = []
    for commit in git('log', '--follow', '--format=%H', '--', relative(path)).decode().splitlines():
        result = subprocess.run(['git', 'show', f'{commit}:{relative(path)}'], cwd=ROOT, capture_output=True)
        rows.append({'commit': commit, 'sha256': sha(result.stdout) if result.returncode == 0 else None})
    return rows

def registration():
    path = JAVA / 'DynastyGear.java'
    contents = path.read_text()
    assert 'ITEMS.register(name, () -> new ArmorItem(material, type, new Item.Properties())' in contents
    assert 'DynastyGear.ITEMS.register(modEventBus)' in (JAVA / 'DynastyContent.java').read_text()
    assert 'DynastyContent.register(modEventBus)' in (JAVA / 'Dynasty.java').read_text()
    pattern = r'armor\("([a-z_]+)", DynastyArmorMaterials\.([A-Z_]+), ArmorItem\.Type\.([A-Z]+)\)'
    registered = [(match.group(1), match.group(2), match.group(3), contents.count('\n', 0, match.start())+1)
                  for match in re.finditer(pattern, contents)]
    table = contents.split('Object[][] EXTRA_SET_TABLE = {', 1)[1].split('};', 1)[0]
    slots = re.findall(r'armor\(id \+ "_([a-z]+)", material, ArmorItem\.Type\.([A-Z]+)\)', contents)
    assert len(slots) == 4
    assert 'EXTRA_ARMOR = registerExtraSets()' in contents
    for entry in re.finditer(r'\{"([a-z_]+)", DynastyArmorMaterials\.([A-Z_]+)\}', table):
        family, material = entry.groups()
        line = contents.count('\n', 0, contents.index(entry.group())) + 1
        registered.extend((f'{family}_{suffix}', material, slot, line) for suffix, slot in slots)
    assert len(registered) == len({row[0] for row in registered}) == 112
    assert not re.search(r'getArmorTexture|getHumanoidArmorModel|initializeClient', contents)
    return registered

def main():
    registered = registration()
    mats_source = JAVA / 'DynastyArmorMaterials.java'
    mats = dict(re.findall(r'ArmorMaterial\s+([A-Z_]+)\s*=\s*make\("([a-z_]+)"', mats_source.read_text()))
    assert 'return "dynasty:" + name' in mats_source.read_text()
    install = {r['resource_path']:r for r in read(V15)['files']}
    v7 = {r['target']:r for r in read(V7)}
    historic = read(INVENTORY)
    inventory = {i['id']:i for group in historic['rows'] for i in group['icons']}
    old = set(read(VISUAL)['protected_old_sets'])
    prior_ids = {r['id'] for r in read(PRIOR_ID_INDEX)}
    source_checks = {}
    for recorded in historic['historical_sources']:
        p = ROOT / recorded['path']
        assert hash_file(p) == recorded['sha256']
        source_checks[p.parent.name] = {i['id']:i for i in read(p)['items']}
    provenance = ART / 'armor-current-bindings-20261113/consumer-provenance.json'
    consumer = 'net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java'
    layer_source = provenance.parent / 'consumer' / consumer
    assert hash_file(layer_source) == read(provenance)['entries'][consumer]
    assert re.search(r'return \w+ == EquipmentSlot\.LEGS;', layer_source.read_text())
    prompt = Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt')
    assert prompt.is_file()
    prompt_lines = prompt.read_text().splitlines()
    begin = next(i for i,line in enumerate(prompt_lines) if line.startswith('## 6.5 '))
    end = next(i for i in range(begin+1,len(prompt_lines)) if prompt_lines[i].startswith('## 6.6 '))
    families = {}
    wear = {}
    for item, material, slot, line in registered:
        family = mats[material]
        ident = 'dynasty:'+item
        model = ASSETS / 'models/item' / f'{item}.json'
        model_data = read(model)
        loader = model_data.get('loader')
        if loader == 'dynasty:original_item':
            texture_ref = model_data['original_texture']
            namespace, path = texture_ref.split(':',1)
        else:
            assert loader is None and model_data.get('parent') in ('item/generated','minecraft:item/generated')
            texture_ref = model_data['textures']['layer0']
            namespace, texture_path = texture_ref.split(':',1)
            path = 'textures/' + texture_path + '.png'
        assert namespace == 'dynasty'
        icon = ASSETS/path
        current_hash = hash_file(icon)
        previous = inventory[ident]
        layer = 2 if slot == 'LEGGINGS' else 1
        atlas = ASSETS / 'textures/models/armor' / f'{family}_layer_{layer}.png'
        if atlas not in wear:
            current_atlas = evidence(atlas)
            source_install = install.get(str(atlas.relative_to(RES)))
            if source_install and source_install['installed_sha256'] == current_atlas['sha256'] and source_install['previous_sha256'] != current_atlas['sha256']:
                current_atlas.update(status='redraw_verified_v15_install', provenance=relative(V15), install=source_install)
            else:
                history = file_history(atlas)
                changed = any(r['sha256'] not in (None,current_atlas['sha256']) for r in history)
                current_atlas.update(status='changed_bytes_in_git_redraw_unproven' if changed else 'insufficient_redraw_history', git_history=history)
            wear[atlas]=current_atlas
        selected = previous['selected']
        icon_history = {}
        if selected and current_hash == selected['sha256']:
            batch = selected['batch']
            assert current_hash == source_checks[batch][item]['sha256']
            icon_status = 'redraw_verified_selected'
            icon_history = {'record':relative(ART/batch/'source-check.json'),'batch':batch}
        elif (rec:=v7.get(relative(icon))) and rec['sha256'] == current_hash:
            assert hash_file(V7.parent/rec['source'])
            icon_status = 'redraw_verified_v7'
            icon_history = {'record':relative(V7),'native_source':relative(V7.parent/rec['source'])}
        elif (rec:=install.get(str(icon.relative_to(RES)))) and rec['installed_sha256'] == current_hash and rec['previous_sha256'] != current_hash:
            icon_status = 'redraw_verified_v15_install'
            icon_history = {'record':relative(V15),'install':rec}
        elif family in old and previous['sha256'] == current_hash:
            icon_status = 'protected_fine_old_redraw_history_incomplete'
            icon_history = {'record':relative(VISUAL),'git_history':file_history(icon)}
        else:
            icon_status = 'insufficient_redraw_history'
            icon_history = {'git_history':file_history(icon)}
        families.setdefault(family, []).append({
            'id':ident,'name':previous['name'],'material':'dynasty:'+family,'slot':slot,'registration_line':line,
            'model':evidence(model),'loader':loader or model_data['parent'],'texture_reference':texture_ref,
            'icon':evidence(icon),'icon_status':icon_status,'icon_history':icon_history,
            'protected_fine_old':family in old,'layer':layer,'worn_atlas':relative(atlas),
            'covered_by_previous_28_item_audit':ident in prior_ids,'confirmed_untouched':False,
        })
    counts = Counter(r['icon_status'] for rows in families.values() for r in rows)
    assert len(families) == 28 and len(wear) == 56
    assert all(len(rows)==4 and len({r['slot'] for r in rows})==4 for rows in families.values())
    assert sum(r['covered_by_previous_28_item_audit'] for rows in families.values() for r in rows)==28
    report = {
        'scope':'Current local Forge source registration and base asset binding. No active client or third-party resource overrides checked.',
        'counts':{'families':len(families),'registered_items':112,'newly_covered_items':84,'worn_atlases':len(wear),
                  'icons_by_status':dict(counts),'atlases_by_status':dict(Counter(r['status'] for r in wear.values()))},
        'current_pending_scope':{'external_file':str(prompt),'sha256':hash_file(prompt),'section':'6.5',
                                 'lines':[begin+1,end],'kind':'triggered_visual_behaviors_not_base_texture_remake',
                                 'base_texture_scope':'User request to prioritize never-redrawn crude armor.'},
        'confirmed_untouched_and_in_scope':[],
        'families':dict(sorted(families.items())),
        'worn_atlases':{relative(p): row for p,row in sorted(wear.items())},
        'evidence_sources':[evidence(p) for p in [V7,V15,VISUAL,INVENTORY,PRIOR_ID_INDEX,mats_source,layer_source,
                                   JAVA/'DynastyGear.java', JAVA/'DynastyContent.java', JAVA/'Dynasty.java',
                                   JAVA/'client/OriginalItemGeometry.java']],
        'gate_met':False,
    }
    (OUT/'registered-armor-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report['counts'],ensure_ascii=False))
    print('uncertain wear',[(p.name,r['status'],len(r.get('git_history',[]))) for p,r in wear.items() if not r['status'].startswith('redraw_verified')])

if __name__ == '__main__':
    main()
