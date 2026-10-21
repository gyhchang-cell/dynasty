"""Final entity PNG/UV exporter: real 16x16, white margin, 2x2 color islands.

The larger material drafts made by the geometry builders are intermediate files.
This exporter remaps their face materials into original front-facing portraits;
Other than the material_atlas and human_atlas targets superseded by the user's
2026-10-11 requirements, final resources retain this strict 16px policy.
No filtering, image generation, gradients or copied artwork.
"""
import json
from collections import Counter
from PIL import Image, ImageDraw, ImageColor
from build_models import ASSET, OUT

# Six by six authored macro-pixels, each exactly 2x2 real pixels. Surround with
# one white macro-pixel (2px). A=dark, B=body, C=highlight; .=white background.
PORTRAITS = {
 'river_imp': ['.CCCC.', 'BABBAB', '.BCCB.', 'BBBBBB', '.B..B.', 'CC..CC'],
 'tree_spirit': ['CC..CC', '.BBBB.', 'BCABCB', '.BAAB.', 'BBBBBB', 'BB..BB'],
 'shrimp_soldier': ['C....C', '.BBBB.', 'CBABBC', 'CBBBB C'.replace(' ',''), '.BCCB.', '..CC..'],
 'carp_spirit': ['..BB..', '.BAAB.', 'CBCCBC', 'CBBBB C'.replace(' ',''), '.BBBB.', '..CC..'],
 'snail_maiden': ['.C..C.', '.BAAB.', '.BCCB.', 'BCC CCB'.replace(' ',''), 'BCAACB', '.CCCC.'],
 'lantern_ghost': ['..BB..', '.BBBB.', '.BCCB.', '.BCCB.', '.BBBB.', '..AA..'],
 'stone_sprite': ['..BB..', '.BBBB.', 'BAABAB', 'BCC CCB'.replace(' ',''), '.BBBB.', 'BB..BB'],
 'crab_soldier': ['.A..A.', 'CBBBB C'.replace(' ',''), 'CBCCBC', '.BBBB.', 'B.BB.B', 'B....B'],
 'corpse_beetle': ['.A..A.', '..BB..', 'BBCCBB', 'BBCCBB', 'BBCCBB', '.B..B.'],
 'venom_scorpion': ['..CC..', '..BB..', 'CBAABC', 'CBCCBC', '.BBBB.', 'B.BB.B'],
 'clockwork_rat': ['CC..CC', 'BAABAB', '.BCCB.', '..AA..', '.BBBB.', 'BB..BB'],
 'gray_wolf': ['B....B', 'BBCCBB', 'BABBAB', '.BCCB.', '..AA..', '.BBBB.'],
 'wild_boar': ['.B..B.', 'BBBBBB', 'BABBAB', 'CBCCBC', 'CCAA CC'.replace(' ',''), '.BBBB.'],
 'golden_leopard': ['C....C', 'BBC CBB'.replace(' ',''), 'BABBAB', 'CBCCBC', '.BAAB.', '.BBBB.'],
 'red_fox': ['B....B', 'BBC CBB'.replace(' ',''), 'BABBAB', '.BCCB.', '..AA..', '..CC..'],
 'gray_falcon': ['..BB..', '.BAAB.', '..CC..', 'BBBBBB', 'BBCCBB', '..BB..'],
 'jingwei_bird': ['..CC..', '.BAAB.', '..CC..', 'BBBBBB', 'BBCCBB', '..CC..'],
 'wooden_magpie': ['..BB..', '.BAAB.', '..CC..', 'BBCCBB', 'ABCCBA', '..BB..'],
 'bat_demon': ['.B..B.', '.BAAB.', 'BBCCBB', 'BB..BB', 'B....B', '..CC..'],
 'giant_python': ['..BB..', '.BAAB.', '.BCCB.', 'BBBBBB', 'BAAAAB', '.BBBB.'],
 'stone_worm': ['.BBBB.', 'BBCCBB', 'BCAACB', 'BCAACB', 'BBCCBB', '.BBBB.'],
 'locust_swarm': ['B....B', 'AC..CA', '..BB..', '..AA..', 'B....B', 'AC..CA'],
 'drowning_ghost': ['.AAAA.', 'ABCCBA', 'ABC CBA'.replace(' ',''), '.BCCB.', '.BBBB.', 'BB..BB'],
 'paper_money_ghost': ['.CCCC.', '.CAAC.', '.CCCC.', 'CBC CBC'.replace(' ',''), 'CBC CBC'.replace(' ',''), '..BB..'],
 'wandering_spirit': ['..AA..', '.ABBA.', 'ABCCBA', 'ABCCBA', '.BBBB.', 'BB..BB'],
 'bandit_thug': ['..AA..', '.ACCA.', '.BAAB.', 'ABBBBC', '.BBBB.', 'AA..AA'],
 'night_watchman': ['.AAAA.', '..CC..', '.BAAB.', 'BBB BBC'.replace(' ',''), '.BBBB.', 'AA..AA'],
 'herb_picker': ['..CC..', 'CCCCCC', '..BB..', 'BABBAB', '.BBBB.', 'AA..AA'],
 'famished_refugee': ['..BB..', '.BCCB.', '.B..B.', 'ABBBBA', '.B..B.', 'AA..AA'],
 'swindler': ['..CC..', '.AAAA.', '..CC..', 'CBBCBC', '.BBBB.', '.AAAA.'],
 'paper_cut_child': ['CC..CC', '.BBBB.', '.BAAB.', 'BB..BB', '.BBBB.', 'CC..CC'],
}

def export(ids=None):
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    records={}
    for id in ids or manifest:
        gp=ASSET/f'geo/secondary/{id}.geo.json'
        geo=json.loads(gp.read_text());g=geo['minecraft:geometry'][0]
        from human_atlas import IDS as HUMAN_IDS, export_one as export_human
        if id in HUMAN_IDS:
            record=export_human(id,geo,ASSET)
            manifest[id].update(atlas=record['atlas'],palette=record['palette'],materialPolicy=record['policy'])
            manifest[id].pop('pixelBlock',None);manifest[id].pop('whiteMargin',None)
            continue
        from material_atlas import IDS as MATERIAL_IDS, export_one
        if id in MATERIAL_IDS:
            record=export_one(id,geo,ASSET)
            manifest[id].update(atlas=record['atlas'], palette=record['palette'], materialPolicy=record['policy'])
            manifest[id].pop('pixelBlock',None);manifest[id].pop('whiteMargin',None)
            continue
        if g['description']['texture_width']==16:
            continue
        old=Image.open(ASSET/f'textures/entity/secondary/{id}.png').convert('RGB')
        original=manifest[id]['palette']
        # Three creature colors plus the user's mandatory pure white background.
        light=2 if id in {'gray_wolf','gray_falcon','golden_leopard','stone_worm','paper_money_ghost','drowning_ghost'} else 3
        chosen=[original[0],original[1],original[light]]
        palette={k:ImageColor.getrgb(c) for k,c in zip('ABC',chosen)}
        palette['.']=(255,255,255)
        rows=PORTRAITS[id];assert len(rows)==6 and all(len(r)==6 for r in rows),id
        im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im);islands={}
        for y,row in enumerate(rows,1):
            for x,k in enumerate(row,1):
                d.rectangle((x*2,y*2,x*2+1,y*2+1),fill=palette[k])
                if k!='.':islands.setdefault(k,[x*2,y*2])
        assert set(islands)==set('ABC'),id
        for bone in g['bones']:
            for cube in bone.get('cubes',[]):
                for face,uv in cube['uv'].items():
                    u,v=uv['uv'];w,h=uv['uv_size']
                    # Dominant original face color preserves material assignment,
                    # then folds its fourth creature color into the closest of 3.
                    patch=old.crop((int(u),int(v),max(int(u)+1,int(u+w)),max(int(v)+1,int(v+h))))
                    rgb=Counter(patch.getdata()).most_common(1)[0][0]
                    k=min('ABC',key=lambda c:sum((rgb[i]-palette[c][i])**2 for i in range(3)))
                    cube['uv'][face]={'uv':islands[k].copy(),'uv_size':[2,2]}
        # Reuse a real 4x4 portrait patch to retain each creature's broad pixel
        # markings. Every component color is still a full 2x2 region; no added
        # noise, fifth color, white background or hidden higher-resolution atlas.
        apply_markings(id,g,im)
        g['description'].update(texture_width=16,texture_height=16)
        from cull_internal_faces import apply_export
        apply_export(id,geo)
        im.save(ASSET/f'textures/entity/secondary/{id}.png')
        gp.write_text(json.dumps(geo,indent=2)+'\n')
        manifest[id].update(palette=chosen+['#ffffff'],atlas=[16,16],pixelBlock=2,whiteMargin=2)
        records[id]={'frontPortrait':rows,'whiteMargin':2,'pixelBlock':2,'palette':chosen+['#ffffff'],
                     'uv':'each face samples one authored 2x2 non-white island; no background on mesh'}
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    p=OUT/'pixel16-export.json';previous=json.loads(p.read_text()) if p.exists() else {}
    for id in MATERIAL_IDS:
        previous.pop(id,None)
    previous.update(records);p.write_text(json.dumps(previous,indent=2)+'\n')
    import importlib.util
    refine=ASSET.parents[4]/'tools/art/steve-fighters-v25/nonhuman.py'
    if refine.exists():
        spec=importlib.util.spec_from_file_location('dynasty_nonhuman_v25',refine);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        selected=[i for i in module.IDS if ids is None or i in ids]
        if selected:
            module.export(selected)
            # The canonical atlas, rather than the transient legacy pass, owns the manifest.
            manifest=json.loads((OUT/'model-manifest.json').read_text())
            legacy=json.loads((OUT/'pixel16-export.json').read_text())
            for target in selected:
                final=json.loads((ASSET/f'geo/secondary/{target}.geo.json').read_text())['minecraft:geometry'][0]
                manifest[target].update(atlas=[final['description']['texture_width'],final['description']['texture_height']],bones=len(final['bones']),cuboids=sum(len(b.get('cubes',[])) for b in final['bones']),materialPolicy='original directional anatomy/material atlas; steve-fighters-v25 source')
                for key in ('pixelBlock','whiteMargin'):manifest[target].pop(key,None)
                legacy.pop(target,None)
            (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
            (OUT/'pixel16-export.json').write_text(json.dumps(legacy,indent=2)+'\n')
    print('Exported strict 16x16 textures/UV:',len(records),'; scoped material atlases retain their current UV policy')

def apply_markings(id,g,im):
    for bone in g['bones']:
        for cube in bone.get('cubes',[]):
            if id=='golden_leopard' and bone['name'] in {'body','chest'}:
                for face in ['north','south','east','west','up']:
                    cube['uv'][face]={'uv':[2,4],'uv_size':[4,4]}
            if id=='paper_money_ghost' and bone['name'].startswith('paper_'):
                for face in cube['uv']:
                    cube['uv'][face]={'uv':[4,2],'uv_size':[4,4]}
    if id=='golden_leopard':
        assert im.getpixel((4,6))!=im.getpixel((2,4)),'Missing leopard spot'
    if id=='paper_money_ghost':
        assert im.getpixel((6,4))!=im.getpixel((4,2)),'Missing paper glyph'

if __name__=='__main__':export()
