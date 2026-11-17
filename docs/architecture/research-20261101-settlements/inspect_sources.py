#!/usr/bin/env python3
"""Read-only fixed-source architecture study; never awards reference credit.

Writes research images/metadata beside this script, not game assets. Sources are
read directly inside two existing archives. No extraction, network, or Java.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR, iso, plans

MODS = Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods')
SOURCES = [
    ('trek', '*远足*jar', 'https://modrinth.com/datapack/trek'),
    ('kaisyn', '*城镇与塔楼*jar', 'https://www.curseforge.com/minecraft/mc-mods/towns-and-towers'),
]
SELECTION = {
    'trek': [f'data/trek/structures/village/{b}/town_centers/{b}_market_1.nbt'
             for b in ('desert', 'plains', 'savanna', 'taiga')],
    'kaisyn': [
        'data/kaisyn/structures/village/exclusives/wandering_trader_camp/town_centers/trader_meeting_point_1.nbt',
        *[f'data/kaisyn/structures/village/forest_ruins/town_centers/forest_meeting_point_{i}.nbt' for i in (1, 2)],
        *[f'data/kaisyn/structures/village/forest_ruins/houses/forest_{n}.nbt'
          for n in ('small_house_1', 'small_house_2', 'medium_house_1', 'medium_house_2', 'large_house_1', 'library_1')],
        *[f'data/kaisyn/structures/village/exclusives/wandering_trader_camp/side/trader_tent_{c}_1.nbt' for c in ('blue', 'red')],
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--append', action='store_true', help='Only render new members; retain previously studied evidence')
    args = ap.parse_args()
    previous = json.loads((OUT/'sources.json').read_text()) if args.append else {}
    rows, sources = previous.get('candidates', []), []
    existing = {r['member']: r for r in rows}
    for namespace, pattern, url in SOURCES:
        paths = list(MODS.glob(pattern))
        assert len(paths) == 1, paths
        archive = paths[0]
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        sources.append(dict(path=str(archive), sha256=digest, publisher_url=url,
                            access='offline existing local archive; URL provenance only, not fetched this session'))
        with ZipFile(archive) as z:
            for member in SELECTION[namespace]:
                if member in existing:
                    assert existing[member]['source_sha256'] == digest, 'Source changed; explicit re-review required'
                    continue
                raw = z.read(member)
                d = read(raw)
                palette = d.get('palette') or d['palettes'][0]
                blocks = d['blocks']
                cells = {tuple(b['pos']): palette[b['state']]['Name'] for b in blocks
                         if palette[b['state']]['Name'] not in AIR}
                assert len({tuple(b['pos']) for b in blocks}) == len(blocks)
                assert all(0 <= p < s for b in blocks for p, s in zip(b['pos'], d['size']))
                sockets = [dict(position=b['pos'], state=palette[b['state']], data=b.get('nbt', {}))
                           for b in blocks if palette[b['state']]['Name'] == 'minecraft:jigsaw']
                doors = [dict(position=b['pos'], state=palette[b['state']]) for b in blocks
                         if palette[b['state']]['Name'].endswith('_door')
                         and palette[b['state']].get('Properties', {}).get('half') == 'lower']
                entrances = [s for s in sockets if s['data'].get('target') == 'minecraft:building_entrance'
                             and s['data'].get('pool') == 'minecraft:empty']
                level = Counter(v['position'][1] for v in doors).most_common(1)[0][0] if doors else (
                    entrances[0]['position'][1] if entrances and '/side/trader_tent_' in member else 1)
                ident = f'S{len(rows)+1:02d}'
                cutoff = max(level+1, round(d['size'][1]*.4))
                sheet = Image.new('RGB', (1520,1400), '#edf0f2')
                for rotation, x in ((0,0),(1,760)):
                    sheet.paste(iso(cells,d['size'],rotation,ident+' '+member.rsplit('/',1)[-1]), (x,0))
                    sheet.paste(iso(cells,d['size'],rotation,f'{ident} cutaway y <= {cutoff}',cutoff), (x,680))
                ImageDraw.Draw(sheet).text((18,1372), 'RESEARCH ONLY / cube approximation incl. stairs, slabs, vegetation / magenta = jigsaw / no credit awarded', fill='#17252c')
                sheet.save(OUT/(ident+'-whole.png'))
                levels = sorted({0, level})
                image_names = [ident+'-whole.png']
                for y in levels:
                    name = f'{ident}-y{y}.png'
                    plans(cells,d['size'],y,ident).save(OUT/name)
                    image_names.append(name)
                # Exact block states allow checking what the generic cubes hide.
                state_rows = [dict(position=b['pos'], state=palette[b['state']]) for b in blocks
                              if palette[b['state']]['Name'] not in AIR]
                (OUT/(ident+'-states.json')).write_text(json.dumps(state_rows,ensure_ascii=False,indent=2)+'\n')
                loc = namespace+':'+member.split('/structures/',1)[1][:-4]
                pool_refs = []
                for name in z.namelist():
                    if '/worldgen/template_pool/' in name and name.endswith('.json'):
                        obj = json.loads(z.read(name))
                        if loc in json.dumps(obj):
                            pool_refs.append(dict(member=name, data=obj))
                rows.append(dict(id=ident, member=member, source_archive=str(archive), source_sha256=digest,
                    publisher_url=url, nbt_sha256=hashlib.sha256(raw).hexdigest(), size=d['size'],
                    nonair_cells=len(cells), stored_blocks=len(blocks), doors=doors, sockets=sockets,
                    layer_counts=dict(sorted(Counter(p[1] for p in cells).items())),
                    materials=dict(Counter(cells.values())), selected_plan_level=level,
                    plan_level_basis='Door or tent entrance socket where present; otherwise generic y1 render selection, not proof of a real entrance',
                    images=image_names, exact_states=ident+'-states.json', pool_references=pool_refs,
                    review_status='unreviewed; no automatic credit'))
                print(ident, member.rsplit('/',1)[-1], d['size'], 'floor',level, 'sockets',len(sockets))
    (OUT/'sources.json').write_text(json.dumps(dict(sources=sources,candidates=rows,automatic_credit=0),ensure_ascii=False,indent=2)+'\n')


if __name__ == '__main__':
    main()
