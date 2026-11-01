"""Read fixed local archive artwork, never launch a mod or fetch remote sources."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from collect import ROOT, OUT, RAW, sheets
from PIL import Image

indices = ['docs/art/armor-vanilla-v23/research/index.json', 'docs/art/armor-imperial-v24/research/index.json']
jars = sorted({r['jar'] for i in indices for r in json.loads((ROOT / i).read_text()) if Path(r['jar']).is_file()})
specs = [
    ('irons_spellbooks-1.20.1-3.15.6', 'irons_spellbooks', 'item',
     'blank_rune arcane_rune blood_rune cooldown_rune ender_rune evocation_rune fire_rune holy_rune ice_rune lightning_rune nature_rune protection_rune void_rune'.split()),
    ('irons_spellbooks-1.20.1-3.15.6', 'irons_spellbooks', 'gui/spell_icons',
     'shield starfall arrow_volley chain_lightning lightning_lance cloud_of_regeneration'.split()),
    ('[诡厄巫法]', 'goety', 'item/focus',
     'command_spell order_spell guardian_spell bulwark_spell arrow_rain_spell stellar_spell cyclone_spell whirlwind_spell razor_wind_spell lightning_spell thunderbolt_spell barricade_spell'.split()),
    ('malum-1.20.1-1.6.7', 'malum', 'block/runewood/totem_poles',
     [s + '_runewood_cutout' for s in 'aerial aqueous arcane earthen eldritch infernal sacred wicked'.split()]),
    ('twilightforest-1.20.1-4.3.2508', 'twilightforest', 'block',
     'castle_door_rune_corners castle_door_rune_ctm fiery_pattern ironwood_pattern'.split()),
    ('twilightforest-1.20.1-4.3.2508', 'twilightforest', 'item',
     'raven_feather peacock_feather_fan'.split()),
]
previous = []
for i in indices:
    previous += [dict(r, prior_index=i) for r in json.loads((ROOT / i).read_text())]
current = [r for p in OUT.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']]
rows = []
jar_hashes = {}
for key, namespace, folder, names in specs:
    jar = next(j for j in jars if key in j)
    if jar not in jar_hashes:
        jar_hashes[jar] = hashlib.sha256(Path(jar).read_bytes()).hexdigest()
    with zipfile.ZipFile(jar) as z:
        metadata = z.read('META-INF/mods.toml').decode('utf-8', errors='replace') if 'META-INF/mods.toml' in z.namelist() else ''
        for name in names:
            entry = f'assets/{namespace}/textures/{folder}/{name}.png'
            data = z.read(entry)
            im = Image.open(io.BytesIO(data)); im.verify()
            target = RAW / 'local-batch05' / namespace / (folder.replace('/', '__') + '__' + name + '.png')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            sha = hashlib.sha256(data).hexdigest()
            old = [dict(prior_index=r['prior_index'], entry=r['entry'], same_png_sha256=r.get('sha256') == sha)
                   for r in previous if r.get('entry') == entry or r.get('sha256') == sha]
            same = [r['reference_id'] for r in current if r.get('sha256') == sha]
            # These are extraction records only, not viewing/unique-design claims.
            rows.append(dict(reference_id=f'VIS-{155 + len(rows):03}', repo=namespace + ' / local archived original art',
                path=entry, local_path=str(target.relative_to(ROOT)), jar=jar, jar_sha256=jar_hashes[jar],
                source_url='local archive; exact absolute path, SHA-256 and entry recorded',
                archive_metadata_excerpt=metadata[:1800], sha256=sha,
                dimensions=list(Image.open(io.BytesIO(data)).size), decoded=True,
                historical_index_hits=old, current_exact_png_matches=same,
                status='EXTRACTED_NOT_VIEWED', distinct_family_proposed_credit=0))
sheets(rows, prefix='batch05')
(OUT / 'batch-05-candidates.json').write_text(json.dumps(dict(
    policy='Local extraction only, zero visual/semantic credit until actual viewing; no Java, no network, no game or source archive writes.',
    candidate_count=len(rows), rows=rows), ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(extracted=len(rows), source_archives=len(jar_hashes), pngs_matching_prior_indices=sum(bool(r['historical_index_hits']) for r in rows),
                     current_exact_matches=sum(bool(r['current_exact_png_matches']) for r in rows), visual_credit=0)))
