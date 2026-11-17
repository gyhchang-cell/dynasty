"""Read fixed local armor archives; never changes production assets or credits designs."""
from pathlib import Path
from collections import defaultdict
from contextlib import ExitStack
from io import BytesIO
import hashlib,json,re,zipfile,subprocess,sys
from PIL import Image,ImageDraw,ImageFont

D=Path(__file__).resolve().parent
R=D.parents[2]
INDEXES=[R/'docs/art/armor-imperial-v24/research/index.json',R/'docs/art/armor-vanilla-v23/research/index.json']
NAMESPACES={'irons_spellbooks','goety','goety_revelation','traveloptics','twilightforest','aquamirae','cataclysm','galosphere'}
MATERIALS=['bamboo','brocade','cloth','leather','sea_silk','bronze','general','jade','sky','xuantian','hongmeng','cinnabar']
SKIP_CASES=set()
COLLECT_WORN=True
APPLICATION='本地未读盔甲参考研究：复用已有23学习组，实际查看原生图标/穿戴图集并语义去重；为5套袖底、5套整胸旧穿戴与3套材质不配套整理原则。独立1000参考未达标前不制作；不改112受保护图标、56穿戴图、人物、Java、实例、Jar或清单。'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,a):(D/n).write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
def family(entry):
    stem=Path(entry).stem
    if stem=='wizard_helmet_hood':return 'wizard'
    return re.sub(r'_(spectral_wrapping|chestplate|brigantine|leggings|fincloak|helmet|heaume|pants|chest|boots|tiara|robe|hood|helm|head|legs|boot|hat)$','',stem)

def main():
    D.mkdir(exist_ok=True,parents=True)
    subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*[f'dynasty:textures/models/armor/{m}_layer_{i}.png' for m in MATERIALS for i in (1,2)],'--application',APPLICATION],check=True,capture_output=True)
    baseline=json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text())
    # Preserve existing frozen source hashes; do not replace with current hashes.
    target=D/'source-baseline.json'
    if target.exists():assert json.loads(target.read_text())==baseline
    else:save('source-baseline.json',baseline)
    groups=defaultdict(dict);jars=set();excluded=[]
    for index in INDEXES:
        for row in json.loads(index.read_text()):
            bits=row['entry'].split('/')
            if len(bits)<3 or bits[0]!='assets' or bits[1] not in NAMESPACES:continue
            if 'modulargolems' in Path(row['jar']).name:
                excluded.append({'jar':row['jar'],'entry':row['entry'],'reason':'傀儡装备附加来源，非本批玩家穿戴研究，不自动计入。'});continue
            fam=family(row['entry'])
            if f'{bits[1]}:{fam}' in SKIP_CASES:continue
            groups[(bits[1],fam)][row['sha256']]=row;jars.add(row['jar'])
    with ExitStack() as stack:
        archives={j:stack.enter_context(zipfile.ZipFile(j)) for j in sorted(jars)}
        def asset(jar,entry):
            data=archives[jar].read(entry);h=sha(data);im=Image.open(BytesIO(data));im.load()
            ns=entry.split('/')[1];local=Path('references')/ns/f'{h[:12]}-{Path(entry).name}'
            (D/local).parent.mkdir(exist_ok=True,parents=True);(D/local).write_bytes(data)
            return {'jar':jar,'entry':entry,'sha256':h,'size':list(im.size),'local':str(local)}
        cases=[]
        for (ns,fam),rows in sorted(groups.items()):
            assets=[]
            for h,row in rows.items():
                a=asset(row['jar'],row['entry']);assert a['sha256']==h;assets.append(a)
            cases.append({'case_key':f'{ns}:{fam}','icons':assets,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
        worn={}
        for jar,z in archives.items():
            if not COLLECT_WORN:continue
            for entry in z.namelist():
                bits=entry.split('/')
                if not(entry.endswith('.png') and len(bits)>3 and bits[0]=='assets'):continue
                ns=bits[1]
                expected=ns in NAMESPACES or (ns=='minecraft' and 'galosphere' in Path(jar).name.lower())
                if not expected or '/textures/' not in entry:continue
                is_worn=any(v in entry for v in ['/textures/models/armor/','/textures/entity/armor/','/textures/armor/'])
                if not is_worn or any(v in entry for v in ['/horse/','test_','_cape.','/trims/']):continue
                a=asset(jar,entry)
                worn.setdefault(a['sha256'],{**a,'role':'WORN_TEXTURE_CANDIDATE_NATIVE_BINDING_NOT_YET_PROVEN','aliases':[]})['aliases'].append({'jar':jar,'entry':entry})
        report={'indexes':[{'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())} for p in INDEXES],
                'archives':[{'path':j,'sha256':sha(Path(j).read_bytes())} for j in sorted(jars)],
                'cases':cases,'worn_textures':list(worn.values()),'excluded':excluded,
                'icon_name_families':len(cases),'icon_png':sum(len(c['icons']) for c in cases),
                'distinct_worn_png':len(worn),'status':'PENDING_MANUAL_REVIEW_ZERO_DESIGN_CREDIT',
                'production_mutations':0,'independent_design_credit':0,'fresh_global_reference_credit':0}
    save('provenance.json',report)
    draw_icons(cases);draw_worn(list(worn.values()))
    print(json.dumps({k:report[k] for k in ['icon_name_families','icon_png','distinct_worn_png']},ensure_ascii=False))

FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def draw_icons(cases):
    font=ImageFont.truetype(FONT,14)
    for page,start in enumerate(range(0,len(cases),7),1):
        rows=cases[start:start+7];im=Image.new('RGB',(1720,40+len(rows)*120),(68,73,78));d=ImageDraw.Draw(im)
        d.text((8,8),'LOCAL ARMOR REFERENCE ICONS / exact pixels / parts, colors and versions != independent designs',font=font,fill='white')
        for i,row in enumerate(rows):
            y=38+i*120;d.text((8,y+10),row['case_key'],font=font,fill='white')
            for j,a in enumerate(row['icons']):
                x=340+j*150;icon=Image.open(D/a['local']).convert('RGBA');s=max(1,64//max(icon.size));icon=icon.resize((icon.width*s,icon.height*s),Image.Resampling.NEAREST)
                im.paste(icon,(x,y),icon);label=Path(a['entry']).stem.removeprefix(row['case_key'].split(':')[1]+'_')
                d.text((x,y+70),label[:18],font=font,fill='white')
                d.text((x,y+88),a['sha256'][:8],font=font,fill='#b7c0c4')
        im.save(D/f'icons-{page:02}.png')

def draw_worn(rows):
    font=ImageFont.truetype(FONT,14)
    for page,start in enumerate(range(0,len(rows),6),1):
        chosen=rows[start:start+6];im=Image.new('RGB',(1440,58+len(chosen)*180),(68,73,78));d=ImageDraw.Draw(im)
        d.text((8,8),'LOCAL WORN TEXTURES / raw native UV layout, NOT GAME / not automatically mapped to vanilla',font=font,fill='white')
        for i,a in enumerate(chosen):
            y=50+i*180;icon=Image.open(D/a['local']).convert('RGBA');s=max(1,min(3,160//icon.height,600//icon.width));icon=icon.resize((icon.width*s,icon.height*s),Image.Resampling.NEAREST)
            im.paste(icon,(720,y),icon)
            ns=a['entry'].split('/')[1]
            d.text((8,y+10),ns+':'+Path(a['entry']).name,font=font,fill='white')
            d.text((8,y+34),f'{a["size"]} / {a["sha256"][:12]} / {Path(a["jar"]).name[:50]}',font=font,fill='#b7c0c4')
        im.save(D/f'worn-{page:02}.png')

if __name__=='__main__':main()
