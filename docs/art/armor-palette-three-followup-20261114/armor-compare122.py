from pathlib import Path
from PIL import Image
import json,hashlib,itertools
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ks=['gravitite','obsidian','zanite'];result=[]
def imgs(k):
 b=r/'docs/art'/f'armor-{k}-whole-20261114';q=json.load(open(b/'provenance.json'));return {e['entry'].split(k+'_',1)[1]:(b/e['local']) for e in q['entries'] if e['entry'].endswith('.png')}
for a,b in itertools.combinations(ks,2):
 rows=[]
 for name,fa in imgs(a).items():
  fb=imgs(b)[name];ia=Image.open(fa).convert('RGBA');ib=Image.open(fb).convert('RGBA');pa=list(ia.getdata());pb=list(ib.getdata());assert ia.size==ib.size
  mapping={};bad=0
  for x,y in zip(pa,pb):
   if not x[3] and not y[3]:continue
   if x in mapping and mapping[x]!=y:bad+=1
   else:mapping[x]=y
  rows.append({'part':name,'a':str(fa),'a_sha256':H(fa),'b':str(fb),'b_sha256':H(fb),'size':ia.size,'same_alpha_mask':ia.getchannel('A').tobytes()==ib.getchannel('A').tobytes(),'rgba_changed_pixels':sum(x!=y for x,y in zip(pa,pb)),'single_rgba_substitution_conflicts':bad,'unique_target_colors':len(set(mapping.values())),'source_colors':len(mapping),'exact_palette_substitution':bad==0})
 result.append({'a':'aether:'+a,'b':'aether:'+b,'parts':rows,'interpretation':'source alpha/layout and exact palette substitution test supports conservative same-template treatment, not automatic global semantic acceptance; no new independent design credit'})
for k in ks:
 b=r/'docs/art'/f'armor-{k}-whole-20261114';(b/'within-batch-concrete-dedup.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');impath=b/'source/assets/aether/textures/models/armor'/f'{k}_layer_1.png';im=Image.open(impath).convert('RGBA');spec=json.load(open(r/'docs/art/armor-neptune-whole-20261114/native-hat-source-rectangles.json'));rows=[]
 for row in spec['rectangles']:
  al=list(im.crop(tuple(row['box'])).getchannel('A').getdata());rows.append({'label':row['label'],'box':row['box'],'nonzero':sum(x>0 for x in al),'fully_opaque':sum(x==255 for x in al)})
 (b/'native-hat-source-rectangles.json').write_text(json.dumps({'source':str(impath.relative_to(b)),'sha256':H(impath),'context':spec['context'],'rectangles':rows},ensure_ascii=False,indent=2)+'\n')
 old=r/'docs/art/armor-neptune-whole-20261114/seven-dimension-mc-review.json';s=json.load(open(old));(b/'prior-family-comparison.json').write_text(json.dumps({'prior':str(old),'prior_sha256':H(old),'prior_observation':s['dimensions'],'comparison':'Earlier Neptune description documents same basic silhouette and UV distribution. New originals have same tight crown/short chest/straight split legs/short boots. Do not reopen approved source PNGs or infer independent identity from colors.','credit':0},ensure_ascii=False,indent=2)+'\n')
 print(k,'hat', [x['nonzero'] for x in rows])
for q in result:print(q['a'],q['b'],[(x['part'],x['same_alpha_mask'],x['exact_palette_substitution'],x['single_rgba_substitution_conflicts']) for x in q['parts']])
