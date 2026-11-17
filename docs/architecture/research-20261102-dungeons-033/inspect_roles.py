"""Read local author roles and compact raw entity evidence; never run the game."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[2] / 'tools/architecture'))
from nbt_read import read

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    src = json.loads((OUT / 'sources.json').read_text())
    rows = []
    for c in src['candidates']:
        with ZipFile(c['source_archive']) as z:
            n = read(z.read(c['member']))
            pal = n.get('palette') or n['palettes'][0]
            entities = n.get('entities', [])
            row = dict(id=c['id'], nbt_sha256=c['nbt_sha256'],
                entity_id_counts=dict(Counter(e.get('nbt', {}).get('id', '') for e in entities)),
                entity_summary=[dict(position=e.get('pos'), block_position=e.get('blockPos'),
                    id=e.get('nbt', {}).get('id'), custom_name=e.get('nbt', {}).get('CustomName'),
                    is_baby=e.get('nbt', {}).get('IsBaby')) for e in entities],
                block_entity_id_counts=dict(Counter(b['nbt'].get('id', '') for b in n['blocks'] if b.get('nbt'))),
                author_resources=[], author_images=[])
            if c['id'] == 'F04':
                names = ['assets/goety/patchouli_books/black_book/zh_cn/entries/world/strctures/rabbit_shed.json',
                    'assets/goety/patchouli_books/black_book/en_us/entries/world/strctures/rabbit_shed.json',
                    'data/goetyawaken/worldgen/structure/rabbit_shed.json',
                    'data/goetyawaken/worldgen/processor_list/rabbit_shed_loot.json']
                for member in names:
                    raw = z.read(member)
                    row['author_resources'].append(dict(member=member, sha256=sha(raw), data=json.loads(raw)))
                member = 'assets/goetyawaken/textures/gui/rabbit_shed.png'
                if member in z.namelist():
                    raw = z.read(member)
                    target = OUT / 'F04-author-reference.png'
                    target.write_bytes(raw)
                    row['author_images'].append(dict(member=member, path=str(target), sha256=sha(raw),
                        original_author_reference=True, newly_created_texture=False))
            manifest = z.read('META-INF/mods.toml')
            row['archive_manifest_sha256'] = sha(manifest)
            row['archive_manifest_identity_lines'] = [line for line in manifest.decode(errors='replace').splitlines()
                if any(k in line for k in ('version=', 'version =', 'displayName', 'authors', 'issueTrackerURL'))]
            rows.append(row)
    (OUT / 'role-evidence.json').write_text(json.dumps(dict(entries=rows, local_only=True,
        building_credit_added=0, entities_instantiated=False, java_run=False), ensure_ascii=False, indent=2)+'\n')
    for r in rows:
        print(r['id'], r['entity_id_counts'], 'block entities', r['block_entity_id_counts'], 'author images',len(r['author_images']))

if __name__ == '__main__':
    main()
