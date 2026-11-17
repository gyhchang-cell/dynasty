"""Read complete, previously unviewed sets from the fixed local candidate inventory."""
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
PRIOR = R / 'docs/art/armor-material-layout-reference-20261104/combined-semantic-ledger.json'
CHARTS = R / 'docs/art/armor-reference-study-20261102/collect.py'
ICON_CHARTS = R / 'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
SELECTED = [f'dark_souls_expansion:{name}_set' for name in ['thief', 'faraam', 'hard_leather', 'artorias', 'pyromancer', 'favor', 'balder', 'catarina', 'darkwraith', 'elite_knight', 'black_iron', 'solaire']] + [
    'undergarden:utherium', 'undergarden:froststeel', 'undergarden:cloggrum', 'divinerpg:jungle',
    'twilightforest:fiery', 'deep_aether:stratus', 'traveloptics:mechanized_exoskeleton', 'enigmaticlegacy:etherium']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(n, v):
    (D / n).write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')


def load_module(name, path):
    m = importlib.util.module_from_spec(spec := importlib.util.spec_from_file_location(name, path)); spec.loader.exec_module(m)
    return m


def main():
    assert not (D / 'provenance.json').exists()
    prior = json.loads(PRIOR.read_text()); inventory = json.loads((D / 'candidate-inventory.json').read_text())
    m = load_module('charts', CHARTS)
    subprocess.run([sys.executable, str(R / 'tools/art/snapshot_texture_requirements.py'), '--batch-dir', str(D), '--targets',
                    *[f'dynasty:textures/models/armor/{mat}_layer_{layer}.png' for mat in m.MATERIALS for layer in [1, 2]],
                    '--application', '第十三批固定本地未读完整装备：复用471名称/190学习组；从原始JAR实际JSON引用读取20套完整四部件，研究布甲、护甲轮廓和材质；同名版本不复读、材料换色不算独立设计，raw图集/实体层仍是未绑定候选，不冒充穿戴验收。1000有效独立参考未达前不制作，保护精致旧稿及289路径、实例、共享Jar、声音/亮度。'], check=True, capture_output=True)
    save('source-baseline.json', json.loads((R / 'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
    cases, decls, archives, worn = [], [], {}, []
    for case in SELECTED:
        assert case not in prior['reviewed_case_keys']
        candidates = [a for a in inventory['candidate_complete_name_sets'] if a['case_key'] == case]
        if len(candidates) > 1:
            candidates = [a for a in candidates if Path(a['jar']).name == 'traveloptics-6.3.0-1.20.1.jar']
        assert len(candidates) == 1, case
        row = candidates[0]; jar = row['jar']; ns, family = case.split(':')
        assert sha(Path(jar)) == row['archive_sha256']
        archives[jar] = {'path': jar, 'sha256': row['archive_sha256']}
        with zipfile.ZipFile(jar) as z:
            def copy(entry, directory, png=False):
                b = z.read(entry); h = hashlib.sha256(b).hexdigest()
                local = Path(directory) / ns / f'{h[:12]}-{Path(entry).name}'
                (D / local).parent.mkdir(parents=True, exist_ok=True); (D / local).write_bytes(b)
                a = {'jar': jar, 'entry': entry, 'sha256': h, 'local': str(local)}
                if png:
                    a['size'] = list(Image.open(BytesIO(b)).size)
                return a

            icons = []
            for part in ['helmet', 'chestplate', 'leggings', 'boots']:
                original = next(a for a in row['parts'] if a['part'] == part)
                model = json.loads(z.read(original['model']))
                loc = model['textures']['layer0']; tns, tex = loc.split(':', 1)
                assert original['texture'] == f'assets/{tns}/textures/{tex}.png'
                image = copy(original['texture'], 'references', True)
                assert image['sha256'] == original['sha256'] and not original['previously_seen_pixels']
                icons.append(image)
                decls.append({'case_key': case, 'part': part, 'model': copy(original['model'], 'declarations'),
                              'texture': image, 'texture_location': loc, 'parent': model['parent'], 'json_pointer': '/textures/layer0'})
            cases.append({'case_key': case, 'icons': icons, 'status': 'PENDING_ACTUAL_VISUAL_REVIEW'})
            entries = []
            if ns == 'dark_souls_expansion':
                e = f'assets/{ns}/textures/entities/{family.removesuffix("_set")}_layer.png'
                if e in z.namelist(): entries = [e]
            elif ns == 'traveloptics':
                entries = [f'assets/{ns}/textures/models/armor/mechanized_exoskeleton{suffix}.png' for suffix in ['', '_layer']]
            elif ns == 'twilightforest':
                entries = [f'assets/{ns}/textures/armor/fiery_{layer}.png' for layer in [1, 2]]
            else:
                folder = 'armor' if ns == 'undergarden' else 'models/armor'
                entries = [f'assets/{ns}/textures/{folder}/{family}_layer_{layer}.png' for layer in [1, 2]]
            for e in entries:
                a = copy(e, 'worn-references', True)
                worn.append({**a, 'case_key': case, 'binding_proven': False,
                             'role': 'RAW_NATIVE_LAYER_CANDIDATE_NOT_ITEM_OR_TARGET_BINDING_PROOF'})
    save('provenance.json', {'archives': list(archives.values()), 'cases': cases, 'worn_textures': worn,
                            'icon_name_families': 20, 'icon_png': 80, 'native_layer_candidates': len(worn),
                            'status': 'PENDING_ACTUAL_VISUAL_REVIEW', 'production_mutations': 0})
    save('resource-declarations.json', decls)
    save('collection-context.json', {k: str(p.relative_to(R)) for k, p in {'collector': Path(__file__).resolve(), 'prior_ledger': PRIOR, 'chart_collector': CHARTS, 'icon_chart_collector': ICON_CHARTS, 'candidate_inventory': D / 'candidate-inventory.json'}.items()} |
         {k + '_sha256': sha(p) for k, p in {'collector': Path(__file__).resolve(), 'prior_ledger': PRIOR, 'chart_collector': CHARTS, 'icon_chart_collector': ICON_CHARTS, 'candidate_inventory': D / 'candidate-inventory.json'}.items()} |
         {'skipped_previously_reviewed_cases': prior['reviewed_case_keys'], 'selected_case_keys': SELECTED})
    m.D = D; m.draw_worn(worn)
    icons_m = load_module('icon_charts', ICON_CHARTS); icons_m.D = D; icons_m.main()
    print(json.dumps({'complete_name_families': 20, 'native_icons': 80, 'item_model_declarations': 80, 'raw_layer_candidates': len(worn)}))


if __name__ == '__main__':
    main()
