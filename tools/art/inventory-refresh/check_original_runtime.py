"""Validate exact original RGBA, own model bindings, atlas filter, untouched sprites and built JAR."""
from pathlib import Path
import hashlib,json,re,zipfile
from PIL import Image
R=Path(__file__).resolve().parents[3];D=R/'docs/art/original-runtime-v7';A=R/'src/main/resources/assets/dynasty'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(strict_unrelated=True):
 rows=json.loads((D/'published.json').read_text());errors=[];matched=0
 definitions={r['id']:r for group in json.loads((R/'docs/art/inventory-refresh-v1/generated-manifest.json').read_text()).values() for r in group}
 ids={row['id'] for row in rows};atlas=R/'src/main/resources/assets/minecraft/atlases/blocks.json';sources=json.loads(atlas.read_text())['sources']
 assert sources[0]['type']=='minecraft:filter'
 assert all(s['type']=='minecraft:single' for s in sources[1:])
 pattern=re.compile(sources[0]['pattern']['path'])
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
  for row in rows:
   ident=row['id'];p=A/'textures/item'/f'{ident}.png';model=A/'models/item'/f'{ident}.json'
   with Image.open(R/row['source']) as source,Image.open(p) as target:
    source=source.convert('RGBA');target=target.convert('RGBA');crop=source.crop(definitions[ident].get('crop_bounds',source.getbbox()))
    expected=Image.new('RGBA',(crop.width+4,crop.height+4));expected.paste(crop,(2,2))
    if expected.size!=target.size or expected.tobytes()!=target.tobytes():errors.append(ident+': source pixels changed')
   data=json.loads(model.read_text())
   if data.get('loader')!='dynasty:original_item' or data.get('original_texture')!=f'dynasty:textures/item/{ident}.png' or 'parent' in data:errors.append(ident+': loader binding')
   expected_tint=0 if ident in {'dynasty_potion','dynasty_splash_potion','dynasty_lingering_potion'} else -1
   if data.get('tint_index',-1)!=expected_tint:errors.append(ident+': potion tint compatibility')
   if not pattern.fullmatch('item/'+ident):errors.append(ident+': atlas not excluded')
   for file in [p,model]:
    if jar.read('assets/dynasty/'+str(file.relative_to(A)))!=file.read_bytes():errors.append(ident+': stale jar')
    else:matched+=1
  if jar.read('assets/minecraft/atlases/blocks.json')!=atlas.read_bytes():errors.append('stale atlas in jar')
  assert 'com/dynasty/client/OriginalItemGeometry.class' in jar.namelist()
 baseline=json.loads((D/'untouched-before.json').read_text())
 parallel_file=D/'parallel-sprite-changes.json'
 parallel=json.loads(parallel_file.read_text()) if parallel_file.exists() else {}
 verified_parallel=[];unrelated_changes=[]
 for name,digest in baseline.items():
  if Path(name).stem in ids:continue  # Later approved batches become part of the canonical set.
  current=sha(A/'textures/item'/name)
  if current!=digest:
   # Only explicitly audited, exact concurrent hashes are accepted; never a broad filename exemption.
   if name in parallel and current==parallel[name]['sha256']:verified_parallel.append(name)
   else:
    unrelated_changes.append(name)
    if strict_unrelated:errors.append(name+': unrelated sprite changed')
 report={'originals':len(rows),'sourcePixels':'exact RGBA match after transparent trim and 2px padding; no resize/quantization','jarFilesMatched':matched+1,'untouchedSprites':sum(Path(n).stem not in ids for n in baseline)-len(verified_parallel)-len(unrelated_changes),'parallelSpritesPreserved':verified_parallel,'otherChangesOutsideScope':unrelated_changes,'strictUnrelated':strict_unrelated,'errors':errors,'graphicalAcceptance':'NOT_RUN; existing client not restarted; saves untouched'}
 (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));assert not errors
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--scope-originals',action='store_true',help='Report unrelated concurrent edits without treating them as failures of the original-item publication.')
 args=parser.parse_args();check(strict_unrelated=not args.scope_originals)
