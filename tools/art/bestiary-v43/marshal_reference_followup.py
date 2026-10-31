"""Correct a research atlas mismatch and inspect four previously unavailable sources.
Only research cache and candidate metadata; no runtime/model/texture production.
"""
from pathlib import Path
import importlib.util,json,urllib.request,re
from PIL import Image,ImageDraw,ImageFont
s=importlib.util.spec_from_file_location('marshal_reference',Path(__file__).with_name('marshal_reference.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def fetch(directory,path):
 base=m.LIB/directory;meta=json.loads((base/'source.json').read_text());p=base/path
 if not p.exists():
  p.parent.mkdir(parents=True,exist_ok=True)
  p.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/{meta["repo"]}/{meta["sha"]}/{path}',timeout=30).read())
 return p

def main():
 data=json.loads((m.OUT/'candidates.json').read_text());rows=data['items'];changes=[]
 jobs=[('TeamTwilight__twilightforest','Lich','src/main/resources/assets/twilightforest/textures/entity/twilightlich64.png',27),('TeamTwilight__twilightforest','LowerGoblinKnight','src/main/resources/assets/twilightforest/textures/entity/doublegoblin.png',None),('lender544__new1.20.1','Draugr_','src/main/resources/assets/cataclysm/textures/entity/draugar/draugr.png',None),('lender544__new1.20.1','Royal_Draugr_','src/main/resources/assets/cataclysm/textures/entity/draugar/royal_draugr.png',None),('lender544__new1.20.1','Elite_Draugr_','src/main/resources/assets/cataclysm/textures/entity/draugar/elite_draugr.png',None)]
 for directory,short,path,replace in jobs:
  base=m.LIB/directory;meta=json.loads((base/'source.json').read_text());texture=fetch(directory,path);models={p.stem:p for p in base.rglob('*.java') if 'Model' in p.stem};model=next(p for p in models.values() if m.h.normalized(m.h.name(p))==m.h.normalized(short));parts,warnings,_=m.h.java_parts(model,models)
  if warnings:raise ValueError((short,warnings))
  root_fix=False
  if re.search(r'root\s*=\s*partdefinition\.addOrReplaceChild\("root"',model.read_text()) and parts.get('root',{}).get('parent')=='root':parts['root']['parent']=None;root_fix=True
  fs,points=m.h.g.geometry(parts);n=replace or next((r['number']for r in rows if r['identity']==meta['repo']+':'+short),len(rows)+1)
  filename=f'{n:03}-{directory}-{short}-binding-confirmed.png';card=Image.new('RGB',(760,420),'#e9ebe4');d=ImageDraw.Draw(card);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
  d.text((8,5),f'{n:03} {meta["repo"].split("/")[-1]} / {short}',font=font,fill='#23312d');card.paste(m.h.g.render(fs,points,35,(370,320)),(0,35));im=m.fit(Image.open(texture),365,315);card.paste(im,(390+(365-im.width)//2,35),im)
  d.text((8,365),'Source constructor + renderer atlas / NOT game rendering',font=font,fill='#23312d');d.text((8,392),'Mesh root alias resolved' if root_fix else 'Named renderer texture instead of similarly named file',font=font,fill='#23312d');card.save(m.OUT/filename)
  renderer=next(p for p in base.rglob('*.java') if m.h.normalized(p.stem)==m.h.normalized(short+'Renderer'))
  row=dict(number=n,identity=meta['repo']+':'+short,family=short,commit=meta['sha'],model_source=m.h.url(meta,base,model),texture_source=m.h.url(meta,base,texture),binding_source=m.h.url(meta,base,renderer),binding_kind='renderer named texture; literal declaration manually inspected',model_sha256=m.digest(model),texture_sha256=m.digest(texture),card=filename,card_sha256=m.digest(m.OUT/filename),viewed=False,root_alias_resolution=root_fix)
  if n<=len(rows):
   old=rows[n-1]
   if replace and old['texture_source']!=row['texture_source']:row['previous_candidate']=dict(card=old['card'],texture_source=old['texture_source'],reason='partial similarly named texture; NOT accepted as the full Lich atlas')
   elif old.get('previous_candidate'):row['previous_candidate']=old['previous_candidate']
   rows[n-1]=row
  else:rows.append(row)
  changes.append(dict(number=n,identity=row['identity'],card=filename))
 data['items']=rows;data['status']='CANDIDATES_REQUIRE_MANUAL_REVIEW';(m.OUT/'candidates.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 sheet=Image.new('RGB',(1520,1290),'#e9ebe4')
 for i,row in enumerate(changes):sheet.paste(Image.open(m.OUT/row['card']),(i%2*760,i//2*430))
 sheet.save(m.OUT/'binding-followup.png');print(json.dumps(changes))
if __name__=='__main__':main()
