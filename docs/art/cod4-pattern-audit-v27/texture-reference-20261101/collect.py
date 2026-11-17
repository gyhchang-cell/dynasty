"""Pinned art-only reference collection. Downloads are candidates, never study credit."""
import concurrent.futures
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CACHE = ROOT / 'build/item-use-references'
RAW = ROOT / 'build/art-reference-20261101'

def choose(directory, predicate):
    meta = json.loads((directory / 'source.json').read_text())
    tree = json.loads((directory / 'tree.json').read_text())['tree']
    return [dict(repo=meta['repo'], revision=meta['sha'], path=e['path'],
                 git_blob_sha=e.get('sha'), bytes_declared=e.get('size'))
            for e in tree if e['path'].endswith('.png') and predicate(e['path'])]

def selection():
    jobs = []
    jobs += choose(CACHE / 'stal111__Forbidden-Arcanus', lambda p:
        '/textures/effect/magic_circle/' in p and
        not any(s in p for s in ['corrupt_0', 'corrupt_1', 'corrupt_interpolate']))
    jobs += choose(CACHE / 'VazkiiMods__Botania', lambda p:
        '/textures/model/armor_' in p and not any(s in p for s in ['holiday', 'invisible']))
    jobs += choose(CACHE / 'iron431__irons-spells-n-spellbooks', lambda p:
        '/textures/models/armor/' in p and not any(s in p for s in ['cape', 'test_', 'pumpkin']))
    jobs += choose(CACHE / 'Electroblob77__Wizardry', lambda p:
        '/textures/entity/' in p and Path(p).stem in
        ['arcane_workbench_rune', 'combustion_rune', 'fire_sigil', 'frost_sigil', 'lightning_sigil', 'shield'])
    jobs += choose(CACHE / 'Polarice3__Goety-2', lambda p:
        '/textures/entity/' in p and Path(p).stem in
        ['apostle_summon_circle', 'spell_rune', 'summon_circle', 'summon_circle_spirit', 'bear_servant_runes'])
    return jobs

def fetch(row):
    row = dict(row)
    target = RAW / row['repo'].replace('/', '__') / row['path']
    url = f"https://raw.githubusercontent.com/{row['repo']}/{row['revision']}/{row['path']}"
    row.update(source_url=url, local_path=str(target.relative_to(ROOT)), status='CANDIDATE_NOT_VIEWED')
    try:
        if not target.exists():
            # macOS curl uses the installed system trust store; Python's CA bundle is absent.
            # TLS verification stays enabled. No insecure TLS fallback.
            data = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                '--max-time', '25', url], check=True, capture_output=True).stdout
            Image.open(io.BytesIO(data)).verify()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        data = target.read_bytes()
        row['sha256'] = hashlib.sha256(data).hexdigest()
        actual_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        row['git_blob_verified'] = actual_blob == row['git_blob_sha']
        if not row['git_blob_verified']:
            raise ValueError('PNG does not match pinned Git tree blob')
        im = Image.open(target)
        row.update(dimensions=list(im.size), decoded=True)
    except Exception as exc:
        row.update(status='FETCH_FAILED', error=str(exc))
    return row

def sheets(rows, prefix='page'):
    good = [r for r in rows if r.get('decoded')]
    for group in range(0, len(good), 12):
        page = Image.new('RGB', (1200, 930), '#41474c')
        draw = ImageDraw.Draw(page)
        draw.text((10, 8), 'REFERENCE ONLY / pinned source PNGs / nearest enlarged / NOT Dynasty assets or game screenshots', fill='white')
        for i, row in enumerate(good[group:group+12]):
            x, y = (i % 4)*300, 35+(i//4)*295
            im = Image.open(ROOT / row['local_path']).convert('RGBA')
            # Show the full original atlas, never first-frame crop or averaged material.
            factor = max(1, min(280//im.width, 230//im.height))
            if im.width > 280 or im.height > 230:
                row['sheet_requires_fullsize_inspection'] = True
                scale = min(280/im.width, 230/im.height)
                size = (max(1, int(im.width*scale)), max(1, int(im.height*scale)))
            else:
                size = (im.width*factor, im.height*factor)
            preview = im.resize(size, Image.Resampling.NEAREST)
            page.paste(preview, (x+(300-preview.width)//2, y+5), preview)
            draw.text((x+8, y+240), f"{row['reference_id']} {Path(row['path']).name}", fill='white')
            draw.text((x+8, y+255), row['repo'][:43], fill='#bfc8ce')
            draw.text((x+8, y+270), f"{im.width}x{im.height} / full atlas", fill='#bfc8ce')
            row['review_sheet'] = str((RAW / f'{prefix}-{group//12+1:02}.png').relative_to(ROOT))
        page.save(RAW / f'{prefix}-{group//12+1:02}.png')

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    jobs = selection()
    for i, row in enumerate(jobs, 1):
        row['reference_id'] = f'VIS-{i:03}'
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fetch, jobs))
    sheets(rows)
    (OUT / 'candidates.json').write_text(json.dumps(dict(
        policy='Downloads, hashes, file counts and contact sheets add ZERO semantic study credit. Study rows require actual viewing and distinct-design review.',
        rows=rows), ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(candidates=len(rows), downloaded=sum(r.get('decoded', False) for r in rows),
                         failed=[dict(id=r['reference_id'], error=r.get('error')) for r in rows if not r.get('decoded')],
                         study_credit=0), ensure_ascii=False))
