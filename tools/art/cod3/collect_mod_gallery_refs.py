#!/usr/bin/env python3
"""Fetch author gallery candidates for manual review. Does not automatically claim art review or select references."""
from pathlib import Path
import json,subprocess,concurrent.futures,hashlib,sys
from PIL import Image,ImageDraw
p=Path(sys.argv[1]);projects=json.loads((p/'projects.json').read_text());rows=[]
for slug,d in projects.items():
 for item in d.get('gallery',[]):
  rows.append({'project':d['title'],'slug':slug,'type':d['project_type'],'page':'https://modrinth.com/'+d['project_type']+'/'+slug+'/gallery','title':item.get('title'),'description':item.get('description'),'url':item['url']})
def fetch(pair):
 i,r=pair;fn=p/f'candidate-{i:03}.img'
 proc=subprocess.run(['curl','-fLsS','--max-time','40','-o',str(fn),r['url']],capture_output=True)
 try:
  with Image.open(fn) as im:r['dimensions']=im.size
  r['sha256']=hashlib.sha256(fn.read_bytes()).hexdigest();r['file']=fn.name;r['number']=i;return r
 except Exception as e:return dict(r,number=i,error=str(e))
results=list(concurrent.futures.ThreadPoolExecutor(6).map(fetch,enumerate(rows,1)));(p/'candidates.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
valid=[r for r in results if 'error' not in r];print('Valid images:',len(valid),'of',len(rows))
for start in range(0,len(valid),20):
 part=valid[start:start+20];sheet=Image.new('RGB',(1600,1250),(26,28,32));d=ImageDraw.Draw(sheet)
 for i,r in enumerate(part):
  im=Image.open(p/r['file']).convert('RGB');im.thumbnail((394,220));x=i%4*400;y=i//4*250;sheet.paste(im,(x,y));d.text((x+4,y+222),f"{r['number']:03} {r['project'][:38]}",fill='white');d.text((x+4,y+235),str(r['title'])[:50],fill='white')
 sheet.save(p/f'sheet-{start//20+1}.jpg',quality=90)
print('Sheets:',(len(valid)+19)//20)
