"""Cache author gallery images; hash against the twelve preceding scenic batches.

Downloading does not record an image as viewed or select it as a reference.
"""
import concurrent.futures
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent
ROOT = P.parents[3]
old = json.loads((ROOT/'docs/art/cod3-dragon-palace-mirage-v2/references/prior-manifests.json').read_text())
paths = [ROOT/s['path'] for s in old['sources']]
paths.append(ROOT/'docs/art/cod3-dragon-palace-mirage-v2/references/selected-100.json')
prior = set(); sources = []
for path in paths:
    data = json.loads(path.read_text())
    rows = data if isinstance(data, list) else data['references']
    prior.update(r['sha256'] for r in rows)
    sources.append({'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'count':len(rows)})
(P/'prior-manifests.json').write_text(json.dumps({'sources':sources, 'records':sum(s['count'] for s in sources), 'hashes':sorted(prior)}, indent=2)+'\n')
rows = []; urls = set()
for slug, project in json.loads((P/'projects.json').read_text()).items():
    for gallery in project.get('gallery', []):
        if gallery['url'] in urls: continue
        urls.add(gallery['url'])
        rows.append({'number':len(rows)+1, 'project':project['title'], 'slug':slug, 'type':project['project_type'],
                     'page':f"https://modrinth.com/{project['project_type']}/{slug}/gallery", 'title':gallery.get('title'),
                     'description':gallery.get('description'), 'url':gallery['url'], 'raw_url':gallery.get('raw_url')})

def fetch(row):
    target = P/f"candidate-{row['number']:03}.img"; row['file'] = target.name
    if not target.exists():
        subprocess.run(['curl','-fLsS','--max-time','30','-o',str(target),row['url']], capture_output=True)
    try:
        with Image.open(target) as im: row['dimensions'] = im.size
        row['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        row['prior_overlap'] = row['sha256'] in prior
    except Exception as exc: row['error'] = str(exc)
    return row

rows = list(concurrent.futures.ThreadPoolExecutor(10).map(fetch, rows))
(P/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for start in range(0,len(rows),20):
    sheet = Image.new('RGB',(1600,1320),(25,28,31)); draw = ImageDraw.Draw(sheet)
    for j,row in enumerate(rows[start:start+20]):
        x=j%4*400; y=j//4*264
        if 'error' not in row:
            im=Image.open(P/row['file']).convert('RGB'); im.thumbnail((394,218)); sheet.paste(im,(x,y))
        draw.text((x+3,y+220),f"{row['number']:03} {row['slug'][:34]}", fill='white')
        draw.text((x+3,y+234),str(row['title'])[:48], fill='white')
        if row.get('prior_overlap'): draw.text((x+3,y+248),'PRIOR BATCH DUPLICATE',fill='red')
    sheet.save(P/f'sheet-{start//20+1:02}.jpg',quality=94)
print('candidates',len(rows),'downloaded',sum('error' not in r for r in rows),'prior collisions',sum(r.get('prior_overlap',False) for r in rows),flush=True)
