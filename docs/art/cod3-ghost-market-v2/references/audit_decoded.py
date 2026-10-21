"""Final cross-task raw and available decoded-RGBA reference audit."""
import hashlib
import json
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rgba(p):
    with Image.open(p) as im:
        im=im.convert('RGBA');return hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
prior=json.loads((P/'prior-manifests.json').read_text())
extra=ROOT/'docs/art/cod3-ghost-army-v2/texture/research/selected-100.json'
paths=[ROOT/r['path'] for r in prior['sources']]
if extra.exists() and extra not in paths:paths.append(extra)
sources=[];raw=set();decoded=set();coverage=[]
for q in paths:
    d=json.loads(q.read_text());rows=d if isinstance(d,list) else d['references'];files_read=0;provided=0;missing=[]
    for r in rows:
        raw.add(r['sha256']);hv=r.get('decodedRgbaSha256')
        choices=[]
        if r.get('local_source'):choices.append(ROOT/r['local_source'])
        if r.get('file'):choices.extend([q.parent/r['file'],q.parent/'references'/r['file'],ROOT/r['file']])
        # First seven accepted batches keep their image caches in ignored build.
        stem=q.parent.name
        build_stems={'cod3-silverfall-v1':'silverfall','cod3-ancient-array-v1':'ancient-array','cod3-crystal-canopy-v2':'crystal-canopy','cod3-sun-crow-v2':'sun-crow','cod3-ice-bloom-v2':'ice-bloom','cod3-xuanwu-v2':'xuanwu','cod3-azure-dragon-v2':'azure-dragon'}
        if stem in build_stems and r.get('file'):
            cache=ROOT/f'build/cod3-{build_stems[stem]}-20261018'
            choices.extend(cache.rglob(Path(r['file']).name))
        actual=next((p for p in choices if p.is_file() and sha(p)==r['sha256']),None)
        if actual:
            calculated=rgba(actual)
            if hv:assert calculated==hv,(q,r.get('number'),'decoded metadata mismatch')
            hv=calculated;files_read+=1
        elif hv:provided+=1
        else:missing.append(r.get('number',r.get('file')))
        if hv:decoded.add(hv)
    sources.append({'path':str(q.relative_to(ROOT)),'count':len(rows),'sha256':sha(q)})
    coverage.append({'manifest':str(q.relative_to(ROOT)),'records':len(rows),'decoded_from_verified_files':files_read,'existing_decoded_hash_without_file':provided,'unavailable_decoded_records':missing})
selected=json.loads((P/'selected-100.json').read_text())
for r in selected:
    p=P/r['file'];assert sha(p)==r['sha256'];r['decodedRgbaSha256']=rgba(p)
new_raw={r['sha256'] for r in selected};new_decoded={r['decodedRgbaSha256'] for r in selected}
assert len(selected)==len(new_raw)==len(new_decoded)==100
assert not raw&new_raw and not decoded&new_decoded
dump(P/'selected-100.json',selected)
dump(P/'prior-manifests.json',{'sources':sources,'records':sum(s['count'] for s in sources),'hashes':sorted(raw)})
dedup=json.loads((P/'dedup.json').read_text());dedup.update({'prior_records':sum(s['count'] for s in sources),'raw_sha256_overlap':0,'unique_decoded_rgba':100,'available_prior_decoded_rgba_overlap':0,'decoded_audit':'decoded-rgba-audit.json'})
dump(P/'dedup.json',dedup)
report={'status':'PASS','selected':100,'prior_records':sum(s['count'] for s in sources),'raw_overlap':0,'decoded_overlap':0,'unique_selected_decoded_rgba':100,'prior_unique_decoded_hashes':len(decoded),'prior_coverage':coverage,'decoded_method':'SHA256(str(PIL_RGBA_image.size).encode() + RGBA_bytes)','limits':'Compares exact decoded dimensions and pixels; does not certify visual uniqueness of alternate views or resized/cropped variants. No old manifest or image is changed.'}
dump(P/'decoded-rgba-audit.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='prior_coverage'},ensure_ascii=False),flush=True)
