"""Collect unreviewed complete item-model sets from three already frozen local archives."""
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
PRIOR = R / 'docs/art/armor-organic-reference-20261103/combined-semantic-ledger.json'
SOURCE = R / 'docs/art/armor-organic-reference-20261103/provenance.json'
CHARTS = R / 'docs/art/armor-reference-study-20261102/collect.py'
TARGETS = {
    'mutationcraft': {'metal_armor': 'diamond_damaged_', 'rusted_metal_armor': 'diamond_rust_'},
    'callfromthedepth_': {'marblearmor': 'marble_armour', 'soularmor': 'soul_armor_'},
    'the_awakening_of_the_elder_souls': {
        'bronze_armor': 'bronze_', 'bronze_ultrarite_armor': 'bronze_ultrarite_',
        'eclipse_armor': 'eclipse_armor_', 'emerald_armor': 'emerald_',
        'enderite_armor': 'enderite_', 'flaming_komodo_leather_armor': 'flaming_komodo_leather_',
        'ruby_armor': 'ruby_', 'sapphire_armor': 'sapphire_',
        'sapphire_ultrarite_armor': 'sapphire_ultrarite_', 'ultrarite_armor': 'ultrarite_',
    },
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (D / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    assert not (D / 'provenance.json').exists()
    prior, source = json.loads(PRIOR.read_text()), json.loads(SOURCE.read_text())
    m = importlib.util.module_from_spec(spec := importlib.util.spec_from_file_location('charts', CHARTS))
    spec.loader.exec_module(m)
    D.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(R / 'tools/art/snapshot_texture_requirements.py'), '--batch-dir', str(D),
                    '--targets', *[f'dynasty:textures/models/armor/{mat}_layer_{layer}.png' for mat in m.MATERIALS for layer in [1, 2]],
                    '--application', '第十二批未读完整装备参考：复用457名称/189学习组；按真实物品模型引用读取14套56图标与28原生穿戴候选图集，检查材料、轮廓、透明袖底和腰线。颜色/部件/版本不算独立设计，候选图集不当已绑定；适用1000有效独立设计未达前不制作，保护精致旧稿和289路径，不碰游戏/声音/亮度/共享Jar/主清单。'], check=True, capture_output=True)
    save('source-baseline.json', json.loads((R / 'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
    cases, decls, worn, archives = [], [], [], []
    for ns, families in TARGETS.items():
        matches = []
        for a in source['archives']:
            with zipfile.ZipFile(a['path']) as z:
                if all(f'assets/{ns}/models/item/{fam}_helmet.json' in z.namelist() for fam in families):
                    matches.append(a)
        assert len(matches) == 1
        archive = matches[0]
        assert sha(Path(archive['path'])) == archive['sha256']
        archives.append(archive)
        with zipfile.ZipFile(archive['path']) as z:
            def copy(entry, directory, png=False):
                b = z.read(entry); h = hashlib.sha256(b).hexdigest()
                local = Path(directory) / ns / f'{h[:12]}-{Path(entry).name}'
                (D / local).parent.mkdir(parents=True, exist_ok=True)
                (D / local).write_bytes(b)
                result = {'jar': archive['path'], 'entry': entry, 'sha256': h, 'local': str(local)}
                if png:
                    result['size'] = list(Image.open(BytesIO(b)).size)
                return result

            for family, atlas_prefix in families.items():
                case = ns + ':' + family
                assert case not in prior['reviewed_case_keys']
                icons = []
                for part in ['helmet', 'chestplate', 'leggings', 'boots']:
                    entry = f'assets/{ns}/models/item/{family}_{part}.json'
                    model = json.loads(z.read(entry))
                    loc = model['textures']['layer0']
                    tns, tex = loc.split(':', 1)
                    image = copy(f'assets/{tns}/textures/{tex}.png', 'references', True)
                    icons.append(image)
                    decls.append({'case_key': case, 'part': part, 'model': copy(entry, 'declarations'),
                                  'texture': image, 'parent': model['parent'], 'texture_location': loc, 'json_pointer': '/textures/layer0'})
                cases.append({'case_key': case, 'icons': icons, 'status': 'PENDING_ACTUAL_VISUAL_REVIEW'})
                for layer in [1, 2]:
                    candidate = copy(f'assets/{ns}/textures/models/armor/{atlas_prefix}_layer_{layer}.png', 'worn-references', True)
                    worn.append({**candidate, 'case_key': case, 'layer': layer,
                                 'role': 'RAW_NATIVE_ATLAS_CANDIDATE_BINDING_NOT_PROVEN', 'binding_proven': False})
    save('provenance.json', {'source_provenance': str(SOURCE.relative_to(R)), 'source_provenance_sha256': sha(SOURCE),
                            'archives': archives, 'cases': cases, 'worn_textures': worn, 'icon_name_families': 14,
                            'icon_png': 56, 'native_worn_entries': 28, 'production_mutations': 0})
    save('resource-declarations.json', decls)
    save('collection-context.json', {'collector': str(Path(__file__).resolve().relative_to(R)),
                                    'collector_sha256': sha(Path(__file__)), 'chart_collector': str(CHARTS.relative_to(R)),
                                    'chart_collector_sha256': sha(CHARTS), 'prior_ledger': str(PRIOR.relative_to(R)),
                                    'prior_ledger_sha256': sha(PRIOR), 'skipped_previously_reviewed_cases': prior['reviewed_case_keys']})
    m.D = D
    m.draw_icons(cases)
    m.draw_worn(worn)
    print(json.dumps({'complete_name_families': len(cases), 'icons': 56, 'model_declarations': len(decls), 'native_worn_candidates': len(worn)}))


if __name__ == '__main__':
    main()
