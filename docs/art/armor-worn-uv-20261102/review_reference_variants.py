"""Reopen two fixed armor namespaces to inspect color/part/version duplication."""
from pathlib import Path
from collections import defaultdict
from io import BytesIO
import hashlib
import json
import re
import zipfile
from PIL import Image, ImageDraw, ImageFont

D=Path(__file__).resolve().parent
R=D.parents[2]
SOURCE=R/'docs/art/armor-imperial-v24/research/index.json'

def main():
    groups=defaultdict(list)
    for row in json.loads(SOURCE.read_text()):
        ns=row['entry'].split('/')[1]
        if ns not in {'iceandfire','samurai_dynasty'}:continue
        stem=Path(row['entry']).stem
        family=re.sub(r'_(helmet|helm|chestplate|chest|leggings|legs|boots|boot|pants|head)$','',stem)
        groups[(ns,family)].append(row)
    records=[]
    for (ns,family),rows in sorted(groups.items()):
        assets=[]
        for row in rows:
            with zipfile.ZipFile(row['jar']) as z:data=z.read(row['entry'])
            assert hashlib.sha256(data).hexdigest()==row['sha256']
            im=Image.open(BytesIO(data));im.load()
            p=D/'reference-variants'/ns/f"{row['sha256'][:12]}-{Path(row['entry']).name}"
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            assets.append({**row,'local':str(p.relative_to(D))})
        records.append({'case_key':f'{ns}:{family}','assets':assets,'status':'PENDING_MANUAL_VARIANT_REVIEW'})
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
    for page,start in enumerate(range(0,len(records),8),1):
        subset=records[start:start+8];im=Image.new('RGB',(1080,45+len(subset)*112),(68,73,78));d=ImageDraw.Draw(im)
        d.text((8,8),'EXISTING ARMOR REFERENCES / distinct PNG != distinct design / exact pixels / NOT NEW ART',font=font,fill='white')
        for i,row in enumerate(subset):
            y=38+i*112;d.text((8,y+22),row['case_key'],font=font,fill='white')
            for j,a in enumerate(row['assets']):
                icon=Image.open(D/a['local']).convert('RGBA');factor=max(1,72//max(icon.size));icon=icon.resize((icon.width*factor,icon.height*factor),Image.Resampling.NEAREST)
                x=390+j*160;im.paste(icon,(x,y),icon)
                d.text((x,y+77),Path(a['entry']).stem.removeprefix(row['case_key'].split(':')[1]+'_')[:18],font=font,fill='white')
        im.save(D/f'reference-variants-{page:02}.png')
    report={'source':str(SOURCE.relative_to(R)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'name_families':len(records),'png':sum(len(r['assets']) for r in records),'cases':records,'fresh_reference_credit':0,'status':'PENDING_MANUAL_REVIEW_NO_AUTOMATIC_REFERENCE_CREDIT'}
    (D/'reference-variants-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'families':len(records),'png':report['png'],'pages':(len(records)+7)//8}))

if __name__=='__main__':main()
