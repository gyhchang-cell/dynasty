"""Fixed local JSON-to-icon and class-to-worn study; never edits runtime assets."""
from pathlib import Path
from io import BytesIO
import hashlib
import importlib.util
import json
import subprocess
import sys
import zipfile
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]
INDEXES = [R / 'docs/art/armor-imperial-v24/research/index.json', R / 'docs/art/armor-vanilla-v23/research/index.json']
PRIOR = R / 'docs/art/armor-mixed-reference-20261103/combined-semantic-ledger.json'
JAVAP = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap')
CASES = {
    'celestial_core:guardian_ocean': ('guardian_ocean', ['helmet', 'chestplate', 'leggings', 'boots']),
    'celestial_core:sakura': ('sakura', ['helmet', 'chestplate', 'leggings', 'boots']),
    'celestial_core:virtual_gold': ('virtual_gold', ['helmet', 'chestplate', 'leggings', 'boots']),
    'slendytubbies_craft:azurite_2_armor': ('azurite_2_armor', ['helmet', 'chestplate', 'leggings', 'boots']),
    'slendytubbies_craft:berikelt': ('berikelt_armor', ['helmet', 'chestplate', 'leggings', 'boots']),
    'slendytubbies_craft:pure_iron_armor': ('pur_iron_armor', ['helmet', 'chestplate', 'leggings', 'boots']),
    'slendytubbies_craft:redgold1': ('red_armorst_st', ['helmet', 'chestplate', 'leggings', 'boots']),
    'spellblademod:warding': ('warding', ['helmet', 'chest', 'leggings', 'boots']),
}
CLASS_ENTRIES = {
    'celestial_core': [
        'com/xiaoyue/celestial_core/content/items/VirtualGoldArmorItem.class',
        'com/xiaoyue/celestial_core/content/items/VirtualGoldArmorItem$1.class',
        'com/xiaoyue/celestial_core/content/client/armor/VGArmorModel.class',
        'com/xiaoyue/celestial_core/content/series/OceanArmor.class',
        'com/xiaoyue/celestial_core/content/series/SakuraArmor.class',
        'com/xiaoyue/celestial_core/content/series/VirtualGoldArmor.class',
        'com/xiaoyue/celestial_core/register/CCMaterials.class'],
    'slendytubbies_craft': [f'net/mcreator/slendytubbiescraft/item/{family}ArmorItem${part}.class'
                           for family in ['Azurite2', 'Berikelt', 'PurIron', 'Red']
                           for part in ['Helmet', 'Chestplate', 'Leggings', 'Boots']],
    'spellblademod': ['com/cleannrooster/spellblademod/items/WardArmorItem.class',
                     'com/cleannrooster/spellblademod/items/ModArmorMaterials.class'],
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, data):
    (D / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    assert not (D / 'provenance.json').exists(), 'Keep fixed batches immutable; use a fresh batch for changed inputs.'
    D.mkdir(parents=True, exist_ok=True)
    prior = json.loads(PRIOR.read_text())
    assert not set(CASES) & set(prior['reviewed_case_keys'])
    targets = [f'dynasty:textures/models/armor/{m}_layer_{layer}.png'
               for m in ['bamboo', 'brocade', 'cloth', 'leather', 'sea_silk', 'bronze', 'general', 'jade', 'sky', 'xuantian', 'hongmeng', 'cinnabar'] for layer in [1, 2]]
    application = '第十批未读固定本地源：依据物品模型JSON明确引用归类8套图标，核查图标/原生穿戴层/类声明的对应，不从同名或同尺寸推断UV兼容。研究粗像素材料分区与袖底/腰线方法；组件、换色、版本、额外层不计新设计。沿434名称/182保守学习组，1000真实适用独立设计未达前不制作；保护289路径、精致老稿、实例、Jar、主清单与声音/亮度。'
    subprocess.run([sys.executable, str(R / 'tools/art/snapshot_texture_requirements.py'), '--batch-dir', str(D), '--targets', *targets, '--application', application], check=True, capture_output=True)
    save('source-baseline.json', json.loads((R / 'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
    jars = {}
    for index in INDEXES:
        for a in json.loads(index.read_text()):
            bits = a['entry'].split('/')
            if bits[0] == 'assets' and bits[1] in CLASS_ENTRIES:
                jars.setdefault(bits[1], set()).add(a['jar'])
    assert all(len(v) == 1 for v in jars.values())
    archives, cases, declarations, worn, classes = [], [], [], [], []
    for ns, values in sorted(jars.items()):
        jar = next(iter(values)); archives.append({'namespace': ns, 'path': jar, 'sha256': sha(Path(jar).read_bytes())})
        with zipfile.ZipFile(jar) as z:
            def asset(entry, directory):
                data = z.read(entry); h = sha(data)
                local = Path(directory) / ns / f'{h[:12]}-{Path(entry).name}'
                (D / local).parent.mkdir(parents=True, exist_ok=True); (D / local).write_bytes(data)
                row = {'jar': jar, 'entry': entry, 'sha256': h, 'local': str(local)}
                if entry.endswith('.png'):
                    im = Image.open(BytesIO(data)); im.load(); row['size'] = list(im.size)
                return row
            for key, (prefix, parts) in CASES.items():
                if not key.startswith(ns + ':'):
                    continue
                icons = []
                for part in parts:
                    entry = f'assets/{ns}/models/item/{prefix}_{part}.json'
                    declaration = asset(entry, 'declarations'); model = json.loads(z.read(entry))
                    location = model['textures']['layer0']; texns, texpath = location.split(':')
                    icon = asset(f'assets/{texns}/textures/{texpath}.png', 'references')
                    icons.append(icon)
                    declarations.append({'case_key': key, 'part': part, 'model': declaration, 'texture': icon,
                                         'json_pointer': '/textures/layer0', 'texture_location': location, 'parent': model['parent']})
                cases.append({'case_key': key, 'icons': icons, 'status': 'PENDING_ACTUAL_VISUAL_REVIEW'})
            for entry in sorted(z.namelist()):
                if entry.startswith(f'assets/{ns}/textures/models/armor/') and entry.endswith('.png'):
                    worn.append({**asset(entry, 'worn-references'), 'role': 'RAW_NATIVE_WORN_LAYOUT_BINDING_TO_BE_READ'})
            for entry in CLASS_ENTRIES[ns]:
                row = asset(entry, 'binding-classes')
                output = subprocess.run([str(JAVAP), '-p', '-c', '-classpath', jar, entry[:-6].replace('/', '.')], check=True, text=True, capture_output=True).stdout
                local = Path('binding-disassembly') / ns / (Path(entry).stem + '.txt')
                (D / local).parent.mkdir(parents=True, exist_ok=True); (D / local).write_text(output)
                classes.append({**row, 'disassembly': str(local), 'disassembly_sha256': sha(output.encode()), 'purpose': 'Static armor texture/model declaration inspection only; mod code never executed.'})
    save('provenance.json', {'indexes': [{'path': str(p.relative_to(R)), 'sha256': sha(p.read_bytes())} for p in INDEXES],
         'archives': archives, 'cases': sorted(cases, key=lambda c: c['case_key']), 'worn_textures': worn,
         'icon_name_families': len(cases), 'icon_png': sum(len(c['icons']) for c in cases),
         'status': 'PENDING_ACTUAL_VISUAL_AND_BINDING_REVIEW', 'production_mutations': 0})
    save('resource-declarations.json', declarations)
    save('binding-class-provenance.json', {'javap': str(JAVAP), 'javap_sha256': sha(JAVAP.read_bytes()), 'classes': classes})
    save('collection-context.json', {'collector': str(Path(__file__).relative_to(R)), 'collector_sha256': sha(Path(__file__).read_bytes()),
         'prior_ledger': str(PRIOR.relative_to(R)), 'prior_ledger_sha256': sha(PRIOR.read_bytes()),
         'skipped_previously_reviewed_cases': prior['reviewed_case_keys'], 'scope': application})
    spec = importlib.util.spec_from_file_location('fixed_chart_helpers', R / 'docs/art/armor-reference-study-20261102/collect.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); module.D = D
    module.draw_icons(sorted(cases, key=lambda c: c['case_key'])); module.draw_worn(worn)
    print(json.dumps({'cases': len(cases), 'icons': sum(len(c['icons']) for c in cases), 'worn_entries': len(worn), 'classes_for_static_read': len(classes)}))


if __name__ == '__main__':
    main()
