"""Reconstruct literal resource declarations; alpha probes remain source-rectangle facts."""
from pathlib import Path
import hashlib
import json
import re
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent
FAMILIES = {
    'azurite_2_armor': ('azurite_2_armor', 'Azurite2'),
    'berikelt': ('berikelt_armor', 'Berikelt'),
    'pure_iron_armor': ('pur_iron_armor', 'PurIron'),
    'redgold1': ('red_armorst_st', 'Red'),
}


def main():
    prov = json.loads((D / 'provenance.json').read_text())
    declarations = json.loads((D / 'resource-declarations.json').read_text())
    source = Path('binding-disassembly/slendytubbies_craft/SlendytubbiesCraftModItems-verbose.txt')
    registry = (D / source).read_text()
    bootstrap = registry.split('BootstrapMethods:\n')[1]
    chains, probes = [], []
    for family, (prefix, cls) in FAMILIES.items():
        parent = D / f'binding-disassembly/slendytubbies_craft/{cls}ArmorItem.txt'
        assert 'extends net.minecraft.world.item.ArmorItem' in parent.read_text()
        assert 'initializeClient' not in parent.read_text() and 'getHumanoidArmorModel' not in parent.read_text()
        for part, slot in [('Helmet', 'HEAD'), ('Chestplate', 'CHEST'), ('Leggings', 'LEGS'), ('Boots', 'FEET')]:
            item = prefix + '_' + part.lower()
            decl = next(a for a in declarations if a['case_key'] == 'slendytubbies_craft:' + family and a['part'] == part.lower())
            assert Path(decl['model']['entry']).stem == item
            call = re.search(r'// String ' + re.escape(item) + r'\n[^\n]*// InvokeDynamic #(\d+):get:', registry)
            assert call
            n = call.group(1)
            block = re.search(r'(?m)^  ' + n + r':.*\n(?:(?!  \d+:).*(?:\n|$))*', bootstrap).group()
            supplier = re.search(r'SlendytubbiesCraftModItems\.(lambda\$static\$\d+):', block).group(1)
            method = re.search(r'private static [^\n]+ ' + re.escape(supplier) + r'\(\);[\s\S]*?areturn', registry).group()
            assert f'// class net/mcreator/slendytubbiescraft/item/{cls}ArmorItem${part}' in method
            sub = Path(f'binding-disassembly/slendytubbies_craft/{cls}ArmorItem${part}.txt')
            text = (D / sub).read_text()
            assert 'EquipmentSlot.' + slot in text
            assert 'getArmorTexture(' in text
            location = re.search(r'// String (slendytubbies_craft:textures/models/armor/[^\n]+\.png)', text).group(1)
            ns, path = location.split(':'); entry = f'assets/{ns}/{path}'
            worn = next(a for a in prov['worn_textures'] if a['entry'] == entry)
            assert entry.endswith(f'layer_{2 if part == "Leggings" else 1}.png')
            chains.append({'case_key': 'slendytubbies_craft:' + family, 'registered_item': ns + ':' + item,
                           'part': part.lower(), 'declared_slot': slot, 'registry_disassembly': str(source),
                           'registry_bootstrap_index': int(n), 'registry_supplier': supplier,
                           'item_model': decl['model'], 'inventory_texture': decl['texture'],
                           'armor_subclass_disassembly': str(sub), 'parent_disassembly': str(parent.relative_to(D)),
                           'declared_worn_texture': worn, 'declared_worn_location': location,
                           'evidence_level': 'STATIC_LITERAL_REGISTRY_MODEL_SLOT_TEXTURE_CHAIN',
                           'game_acceptance': False, 'global_renderer_override_excluded': False})
        for layer in [1, 2]:
            worn = next(c['declared_worn_texture'] for c in chains if c['case_key'] == 'slendytubbies_craft:' + family and c['part'] == ('leggings' if layer == 2 else 'chestplate'))
            im = Image.open(D / worn['local']).convert('RGBA')
            alpha = im.getchannel('A')
            values = lambda rect: list(alpha.crop(rect).get_flattened_data())
            count = lambda rect, threshold: sum(v >= threshold for v in values(rect))
            weak = [(x, y, im.getpixel((x, y))) for y in range(20, 27) for x in range(16, 40) if 0 < im.getpixel((x, y))[3] < 128]
            probes.append({'case_key': 'slendytubbies_craft:' + family, 'layer': layer, 'worn': worn,
                           'cap_source_rectangle': [48, 16, 52, 20], 'cap_alpha_gt_zero': count((48, 16, 52, 20), 1),
                           'four_side_last_row_alpha_gt_zero': [count((x, 31, x + 4, 32), 1) for x in [40, 44, 48, 52]],
                           'body_strip': [16, 20, 40, 32],
                           'body_rows_alpha_gt_zero': [count((16, y, 40, y + 1), 1) for y in range(20, 32)],
                           'body_rows_alpha_ge_128': [count((16, y, 40, y + 1), 128) for y in range(20, 32)],
                           'weak_alpha_pixels_in_upper_body_probe': weak,
                           'limit': '原图源矩形事实。声明默认ArmorItem不排除其他模组全局渲染覆盖，亦非1.20.1目标几何/实机证明；不复制外部alpha掩码。'})
    output = {'chains': chains, 'probes': probes, 'static_complete_item_chains': len(chains),
              'unresolved': [
                  {'case_key': 'celestial_core:guardian_ocean', 'limit': '图标JSON已明确；ocean图集与guardian_ocean材质间的外部GenericArmorItem/ArmorMat链未读完，不凭名称认定绑定。'},
                  {'case_key': 'celestial_core:sakura', 'limit': '图标JSON已明确，穿戴材质依赖外部通用装备实现，绑定仍待核。'},
                  {'case_key': 'celestial_core:virtual_gold', 'limit': 'IClientItemExtensions明确返回自定义VGArmorModel，LEGS走inner其余outer；64×64模型含下半图集偏移，禁止按64×32目标UV套用。纹理最终路径仍待外部实现核对。'},
                  {'case_key': 'spellblademod:warding', 'limit': 'WardArmorItem仅普通ArmorItem子类，DIAMOND_WARDING材质字符串与图集存在，但未追完物品注册选材及材质名命名空间拼接，不声称绑定完成。'}],
              'inspected_no_model_override_scope': '四个来源父类与十六个部位类，无本地自定义模型方法；不等于审查整个模组生态。',
              'game_starts': 0, 'production_changes': 0, 'additional_independent_design_credit': 0}
    (D / 'binding-and-rectangle-study.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    draw(prov, chains, probes)
    print(json.dumps({'static_item_chains': len(chains), 'sets_with_complete_declared_chain': 4, 'source_probes': len(probes), 'unresolved_sets': 4}))


def draw(prov, chains, probes):
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
    im = Image.new('RGB', (1550, 1120), (68, 73, 78)); dr = ImageDraw.Draw(im)
    dr.text((12, 10), 'STATIC DECLARED RESOURCE CHAINS / RAW RECTANGLE PROBES / NOT GAME / no foreign pixels applied', font=font, fill='white')
    for row, family in enumerate(FAMILIES):
        case = 'slendytubbies_craft:' + family; y = 50 + row * 265
        dr.text((12, y), case, font=font, fill='white')
        chain = [a for a in chains if a['case_key'] == case]
        for j, a in enumerate(chain):
            icon = Image.open(D / a['inventory_texture']['local']).convert('RGBA')
            s = max(1, 48 // max(icon.size)); icon = icon.resize((icon.width * s, icon.height * s), Image.Resampling.NEAREST)
            im.paste(icon, (12 + j * 68, y + 30), icon)
        for j, layer in enumerate([1, 2]):
            probe = next(a for a in probes if a['case_key'] == case and a['layer'] == layer)
            a = probe['worn']; raw = Image.open(D / a['local']).convert('RGBA').resize((256, 128), Image.Resampling.NEAREST)
            im.paste(raw, (350 + j * 350, y + 30), raw)
            dr.text((350 + j * 350, y + 170), Path(a['entry']).name, font=font, fill='white')
            values = probe['body_rows_alpha_ge_128']
            dr.text((350 + j * 350, y + 195), 'v20-25 >=128: ' + str(values[:6]), font=font, fill='#b7c0c4')
            dr.text((350 + j * 350, y + 217), 'v26-31 >=128: ' + str(values[6:]), font=font, fill='#b7c0c4')
        dr.text((1080, y + 45), 'L1 source cap: 0 / 16', font=font, fill='white')
        dr.text((1080, y + 70), 'L1 side terminal rows: 0,0,0,0', font=font, fill='white')
        dr.text((1080, y + 95), 'L2 upper three pixels: alpha 1', font=font, fill='white')
        dr.text((1080, y + 120), 'No extra set credit for color/parts', font=font, fill='white')
    im.save(D / 'binding-focus.png')


if __name__ == '__main__':
    main()
