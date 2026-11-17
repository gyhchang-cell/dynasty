"""Reconstruct registry -> constructor -> slot -> JSON -> literal armor texture chains."""
from pathlib import Path
import json
import re
from PIL import Image

D = Path(__file__).resolve().parent


def main():
    prov = json.loads((D / 'provenance.json').read_text())
    cp = json.loads((D / 'binding-class-provenance.json').read_text())
    decls = json.loads((D / 'resource-declarations.json').read_text())
    classes = {(a['jar'], a['entry']): a for a in cp['classes']}
    chains, probes = [], []
    for mapping in cp['case_class_mappings']:
        case, jar = mapping['case_key'], mapping['jar']
        registry = next(a for a in cp['classes'] if a['jar'] == jar and a['verbose'])
        text = (D / registry['disassembly']).read_text()
        bootstrap = text.split('BootstrapMethods:\n')[1]
        for part, slot, kind in [('Helmet', 'HEAD', 'HELMET'), ('Chestplate', 'CHEST', 'CHESTPLATE'), ('Leggings', 'LEGS', 'LEGGINGS'), ('Boots', 'FEET', 'BOOTS')]:
            declaration = next(a for a in decls if a['case_key'] == case and a['part'] == part.lower())
            item = Path(declaration['model']['entry']).stem
            call = re.search(r'// String ' + re.escape(item) + r'\n[^\n]*// InvokeDynamic #(\d+):get:', text)
            assert call, (case, part)
            n = int(call.group(1))
            block = re.search(r'(?m)^  ' + str(n) + r':.*\n(?:(?!  \d+:).*(?:\n|$))*', bootstrap).group()
            supplier = re.search(r'\.(lambda\$static\$\d+):', block).group(1)
            method = re.search(r'private static [^\n]+ ' + re.escape(supplier) + r'\(\);[\s\S]*?areturn', text).group()
            entry = next(e for e in mapping['parts'] if e.endswith('$' + part + '.class'))
            assert '// class ' + entry.removesuffix('.class') in method
            sub = classes[(jar, entry)]
            body = (D / sub['disassembly']).read_text()
            assert ('ArmorItem$Type.' + kind in body) or ('EquipmentSlot.' + slot in body)
            armor_method = re.search(r'public java.lang.String getArmorTexture\([\s\S]*?areturn', body).group()
            literals = re.findall(r'// String ([^\n]+:textures/models/armor/[^\n]+\.png)', armor_method)
            assert len(literals) == 1
            ns, path = literals[0].split(':')
            native = next(a for a in prov['worn_textures'] if a['jar'] == jar and a['entry'] == f'assets/{ns}/{path}')
            assert native['layer'] == (2 if part == 'Leggings' else 1) and native['case_key'] == case
            chains.append({'case_key': case, 'registered_item': ns + ':' + item,
                           'slot': slot, 'part': part.lower(), 'registry_class': registry,
                           'bootstrap_index': n, 'supplier': supplier, 'constructor_class': sub,
                           'item_model': declaration['model'], 'inventory_texture': declaration['texture'],
                           'declared_worn_texture': native, 'literal_worn_location': literals[0],
                           'local_part_initialize_client': 'initializeClient(' in body,
                           'evidence_level': 'STATIC_LITERAL_REGISTRY_CONSTRUCTOR_SLOT_JSON_TEXTURE_CHAIN',
                           'global_renderer_override_excluded': False, 'game_acceptance': False})
    for native in prov['worn_textures']:
        image = Image.open(D / native['local']).convert('RGBA')
        if image.size != (64, 32):
            probes.append({'case_key': native['case_key'], 'worn': native, 'probed': False,
                           'reason': 'Non-64x32 atlas; no standard source-rectangle probe or UV compatibility inference.'})
            continue
        alpha = image.getchannel('A')
        count = lambda rect, threshold: sum(x >= threshold for x in alpha.crop(rect).get_flattened_data())
        probes.append({'case_key': native['case_key'], 'worn': native, 'probed': True,
                       'cap_source_rectangle': [48, 16, 52, 20], 'cap_alpha_gt_zero': count((48, 16, 52, 20), 1),
                       'four_side_last_rows_alpha_gt_zero': [count((x, 31, x + 4, 32), 1) for x in [40, 44, 48, 52]],
                       'body_source_strip': [16, 20, 40, 32],
                       'body_rows_alpha_ge_128': [count((16, y, 40, y + 1), 128) for y in range(20, 32)],
                       'scope': 'Native source rectangle only; no target geometry/global override/game claim or mask copy.'})
    result = {'chains': chains, 'probes': probes, 'complete_static_item_chains': len(chains),
              'name_families_with_declared_chain': len({a['case_key'] for a in chains}),
              'source_atlas_rectangles_probed': sum(a['probed'] for a in probes),
              'nonstandard_atlases_not_forced': sum(not a['probed'] for a in probes),
              'game_starts': 0, 'production_changes': 0, 'additional_independent_design_credit': 0}
    assert result['complete_static_item_chains'] == 56 and result['name_families_with_declared_chain'] == 14
    (D / 'declared-layout-study.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['chains', 'probes']}))


if __name__ == '__main__':
    main()
