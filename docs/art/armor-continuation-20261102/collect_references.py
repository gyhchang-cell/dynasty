"""Reopen fixed historical armor entries; parts/variants are not new credits."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import re
import zipfile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

D=Path(__file__).resolve().parent
R=D.parents[2]
SOURCE=R/'docs/art/armor-imperial-v24/research/index.json'
PICKS={
    'immersive_armors':['wither','prismarine','steampunk','wooden','bone','warrior'],
    'magistuarmory':['gothic','brigandine','gambeson','jousting','kastenbrust','maximilian'],
    'samurai_dynasty':['steel','iron_ninja'],
    'divinerpg':['angelic','bedrock','inferno','skeleman','aquastrive','seng_fur'],
    'iceandfire':['dragonsteel_fire','tide_blue','myrmex_desert','forest_troll_leather'],
}

def main():
    groups=defaultdict(list)
    rows=json.loads(SOURCE.read_text())
    for row in rows:
        ns=row['entry'].split('/')[1]
        stem=Path(row['entry']).stem
        family=re.sub(r'_(helmet|helm|chestplate|chest|leggings|legs|boots|boot|pants|head)$','',stem)
        groups[(ns,family)].append(row)
    out=[]
    for ns, families in PICKS.items():
        for family in families:
            assets=[]
            for src in groups[(ns,family)]:
                with zipfile.ZipFile(src['jar']) as z: data=z.read(src['entry'])
                assert hashlib.sha256(data).hexdigest()==src['sha256'],src['entry']
                im=Image.open(BytesIO(data)); im.load()
                # Different archive versions can reuse a name with different bytes.
                p=D/'references'/ns/f"{src['sha256'][:12]}-{Path(src['entry']).name}"
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(data)
                assets.append({**src,'local':str(p.relative_to(D))})
            assert assets,(ns,family)
            out.append({'case_key':f'{ns}:{family}','assets':assets,'status':'PENDING_ACTUAL_VISUAL_REVIEW','fresh_reference_credit':0})
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    for page,start in enumerate(range(0,len(out),8),1):
        selected=out[start:start+8]
        sheet=Image.new('RGB',(1050,55+len(selected)*120),(78,83,88));dr=ImageDraw.Draw(sheet)
        dr.text((12,8),'HISTORICAL ARMOR REFERENCES / exact source pixels x integer / study only',font=font,fill='white')
        for i,row in enumerate(selected):
            y=45+i*120
            dr.text((8,y+20),row['case_key'],font=font,fill='white')
            for j,a in enumerate(row['assets']):
                im=Image.open(D/a['local']).convert('RGBA');factor=max(1,80//max(im.size))
                big=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
                x=350+j*170;sheet.paste(big,(x,y),big)
                dr.text((x,y+83),Path(a['entry']).stem.removeprefix(row['case_key'].split(':')[1]+'_')[:20],font=font,fill='white')
        sheet.save(D/f'armor-reference-{page:02}.png')
    report={'source':str(SOURCE.relative_to(R)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'raw_entries':len(rows),'provisional_name_families':len(groups),'warning':'406 name groups are only a provisional upper bound; color variants, part aliases, shared silhouettes and unrelated assets need semantic review. Not 1000 independent armor designs. Existing evidence is reused, not reset.','cases':out,'reopened_png':sum(len(r['assets']) for r in out),'fresh_reference_credit':0}
    (D/'armor-reference-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'reopened_cases':len(out),'exact_png':report['reopened_png'],'pages':(len(out)+7)//8,'fresh_reference_credit':0}))

if __name__=='__main__':main()
