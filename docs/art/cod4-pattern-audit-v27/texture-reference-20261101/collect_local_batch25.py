"""Pinned sources: scales, feathers, fangs and shells for material readability."""
from pathlib import Path
from PIL import Image
from collect import ROOT, OUT, RAW, sheets
import json, io, hashlib, zipfile

prior = [r for p in OUT.glob('review-batch-*.json') for r in json.loads(p.read_text())['rows']]
seen = {(r.get('jar'), r.get('path')) for r in prior}
selection = {
 'iceandfire': ['scales_red', 'scales_green', 'scales_white', 'scales_blue',
    'sea_serpent_scales_green', 'sea_serpent_scales_deepblue', 'hydra_fang',
    'amphithere_feather', 'stymphalian_bird_feather', 'stymphalian_bird_feather_bundle', 'shiny_scales'],
 'alexsmobs': ['dropbear_claw', 'emu_feather', 'roadrunner_feather', 'rocky_shell', 'spiked_turtle_shell'],
 'goety': ['venomous_fang', 'ring_of_the_dragon'],
 'aether': ['accessories/golden_feather'],
 'irons_spellbooks': ['dragonskin'],
}
keys = {'iceandfire': 'iceandfire', 'alexsmobs': 'alexsmobs', 'goety': 'goety-2.5',
    'aether': 'aether-1.20', 'irons_spellbooks': 'irons_spellbooks-1.20'}
rows = []
for namespace, names in selection.items():
    jar = next(r['jar'] for r in prior if keys[namespace] in Path(r.get('jar', '')).name)
    archive_hash = hashlib.sha256(Path(jar).read_bytes()).hexdigest()
    with zipfile.ZipFile(jar) as z:
        for name in names:
            entry = f'assets/{namespace}/textures/item/{name}.png'
            assert (jar, entry) not in seen
            data = z.read(entry)
            im = Image.open(io.BytesIO(data)).convert('RGBA')
            dst = RAW / 'local-batch25' / entry
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            rows.append(dict(reference_id=f'VIS-{941 + len(rows):03}', repo=Path(jar).name,
                path=entry, jar=jar, jar_sha256=archive_hash, local_path=str(dst.relative_to(ROOT)),
                sha256=hashlib.sha256(data).hexdigest(), rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
                dimensions=list(im.size), decoded=True, status='EXTRACTED_NOT_VIEWED', distinct_family_proposed_credit=0))
sheets(rows, prefix='batch25')
(OUT / 'batch-25-candidates.json').write_text(json.dumps(dict(rows=rows,
    policy='20 source item PNGs; recolors and bundles merge. Material/shape context for cod6 four offerings, not complete four-beast identity, no production or automatic new case credit.'), ensure_ascii=False, indent=2) + '\n')
print('20 pinned primary PNGs extracted; not yet viewed.')
