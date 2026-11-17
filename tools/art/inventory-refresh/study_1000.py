"""Read-only study of 1000 distinct installed mod items; never publish reference art."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import zipfile, json, re, hashlib, io, collections

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / 'docs/art/accessories-mc-v11/references'
D.mkdir(parents=True, exist_ok=True)
versions = Path('/Users/a15356015027/Public/.minecraft/versions')
reject = re.compile(r'(sword|pickaxe|axe|shovel|hoe|spear|bow|dagger|helmet|chestplate|leggings|boots|shield|staff|hammer|scythe|spawn_egg|wand|mace|halberd|trident|cleaver|katana|gauntlet|whip|revolver|gun|cannon|knife|bullet|rifle|debug|missing|logo|_icon|configurator|arrow)', re.I)
seen_jars = set()
found = {}
for jar in sorted(versions.glob('*/mods/*.jar')):
    if jar.name in seen_jars or jar.name.startswith('dynasty'): continue
    seen_jars.add(jar.name)
    try:
        with zipfile.ZipFile(jar) as z:
            names = set(z.namelist())
            wearable = set()
            for n in sorted(names):
                if n.startswith('data/curios/tags/items/') and n.endswith('.json'):
                    for v in json.loads(z.read(n)).get('values', []):
                        v = v.get('id', '') if isinstance(v, dict) else v
                        wearable.add(v)
            for n in sorted(names):
                if not re.fullmatch(r'assets/[^/]+/textures/items?/[^/]+\.png', n): continue
                ns, stem = n.split('/')[1], Path(n).stem
                ident = ns + ':' + stem
                if ident in found or reject.search(stem) or ns in {'dynasty', 'minecraft', 'flame_chase_artifacts', 'examplemod'}: continue
                if f'assets/{ns}/blockstates/{stem}.json' in names: continue
                mp = f'assets/{ns}/models/item/{stem}.json'
                model = json.loads(z.read(mp)) if mp in names else {}
                if ident not in wearable and model.get('parent') not in {'item/generated', 'minecraft:item/generated'}: continue
                raw = z.read(n)
                im = Image.open(io.BytesIO(raw)).convert('RGBA')
                if im.width > 64 or im.height < im.width or im.width < 16: continue
                im = im.crop((0, 0, im.width, im.width))
                found[ident] = dict(id=ident, jar=str(jar), pack=jar.parents[1].name,
                                    texture=n, sha256=hashlib.sha256(raw).hexdigest(),
                                    size=list(im.size), accessory=ident in wearable, image=im)
    except (zipfile.BadZipFile, ValueError, KeyError, OSError): continue

groups = collections.defaultdict(list)
for r in found.values(): groups[r['id'].split(':')[0]].append(r)
for g in groups.values(): g.sort(key=lambda r: (not r['accessory'], r['id']))
rows = []
while groups and len(rows) < 1000:
    for ns in list(groups):
        rows.append(groups[ns].pop(0))
        if not groups[ns]: del groups[ns]
        if len(rows) == 1000: break
assert len(rows) == 1000, len(rows)
font = ImageFont.truetype('/System/Library/Fonts/Monaco.ttf', 9)
for start in range(0, len(rows), 100):
    out = Image.new('RGB', (1200, 1040), '#565c61'); dr = ImageDraw.Draw(out)
    dr.text((10, 8), f'REFERENCE STUDY {start+1}-{start+100}: other authors, not Dynasty assets', font=font, fill='white')
    for j, r in enumerate(rows[start:start+100]):
        x, y = (j % 10)*120, 30+(j//10)*100
        im = r['image'].resize((64,64), Image.Resampling.NEAREST)
        out.paste(im, (x+28,y), im)
        ns, ident = r['id'].split(':')
        dr.text((x+3,y+66), f'{start+j+1} {ns[:17]}', font=font, fill='#d8c9a6')
        dr.text((x+3,y+79), ident[:21], font=font, fill='white')
    out.save(D/f'study-{start//100+1:02}.png')
report = dict(sampleCount=len(rows), namespaces=len({r['id'].split(':')[0] for r in rows}),
              contributingPackFolders=sorted({r['pack'] for r in rows}),
              candidateCount=len(found), jarsScanned=len(seen_jars),
              note='1000 distinct item/accessory samples from installed modpacks, NOT 1000 distinct modpacks. Read-only reference; no reference pixels in production.',
              sources=[{k:v for k,v in r.items() if k!='image'} for r in rows])
(D/'sources.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print({k:v for k,v in report.items() if k!='sources'})
