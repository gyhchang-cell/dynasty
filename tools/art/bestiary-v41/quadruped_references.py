"""Research cards pair actual published coat atlases with literal source anatomy.

Gray anatomy is explicitly a source reconstruction, not a game screenshot or a
claim to reproduce the author's renderer. Variants share a labelled rig family;
extra angles, overlays, costumes and baby skins never count as extra references.
External source/PNG files stay in the ignored build cache, not game resources.
"""
from pathlib import Path
import importlib.util,json,re,urllib.request,hashlib,concurrent.futures,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
CACHE=ROOT/'build/bestiary-v41/quad-reference';CACHE.mkdir(exist_ok=True)
OUT=ROOT/'build/bestiary-v41/research/quadrupeds';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('ref',ROOT/'tools/art/steve-fighters-v25/nonhuman_references.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
spec2=importlib.util.spec_from_file_location('geo_ref',ROOT/'tools/art/secondary-cuboid/review_models.py');g=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(g)
font=lambda n:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',n)
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-reference'}),timeout=25).read()
def cached(url):
    p=CACHE/hashlib.sha256(url.encode()).hexdigest()
    if not p.exists():p.write_bytes(get(url))
    return p
def tree(repo,ref):
    return json.loads(cached('https://api.github.com/repos/'+repo+'/git/trees/'+ref+'?recursive=1').read_text())
def textures(t,key):
    candidates=[]
    for x in t['tree']:
        p=x['path'];n=Path(p).stem.lower();norm=n.replace('_','')
        if not p.endswith('.png') or not any(a in p for a in ('/textures/entity/','/textures/models/')):continue
        if '/item/' in p or '/block/' in p:continue
        if '/overlay/' in p or any(s in n for s in ('tusks','koopa','hostile')):continue
        natural_lizard='/assets/naturalist/textures/entity/lizard/' in p and key=='lizard'
        natural_tortoise='/assets/naturalist/textures/entity/tortoise/' in p and key=='tortoise' and n in ('black','brown','green')
        natural_deer='/assets/naturalist/textures/entity/deer/' in p and key=='deer' and n=='white_deer'
        if not (norm.startswith(key.lower().replace('_','')) or natural_lizard or natural_tortoise or natural_deer):continue
        if key.lower()=='badger' and n=='badger_honey':
            candidates.append(p);continue
        if key.lower()=='feralwolf' and n=='feralwolf_snowy':
            candidates.append(p);continue
        if any(s in n for s in ['eye','overlay','baby','christmas','neutral','angry','collar','freddy','saddle','blank','layer','fur','armor','tame','wither','nether','easter','shoes','moss','peter','sheared','crown','chest','honey','maid','ender','snowy','headgear','perry','fedora','rigby','bandana','potion','rolling','sleeping','hooves','glow','beardie','tail','red_nose']):continue
        candidates.append(p)
    return sorted(candidates,key=lambda p:(len(Path(p).stem),p))
def main():
    ledger=json.loads((ROOT/'docs/art/steve-fighters-v25/nonhuman-references/ledger.json').read_text())
    am_repo='AlexModGuy/AlexsMobs';am_sha='09755dade2cfbdf14839e026d3af446f9d3ff843';am_tree=tree(am_repo,am_sha)
    tf_repo='TeamTwilight/twilightforest';tf_sha=r.TF_SHA;tf_tree=tree(tf_repo,tf_sha)
    bap_repo='itsmeow/BetterAnimalsPlus';bap_tree=json.loads((ROOT/'build/bestiary-v41/reference-trees/BetterAnimalsPlus.json').read_text());bap_sha=bap_tree['sha']
    jobs=[]
    for old in ledger:
        if '四' not in old['support_observation'] or old['identity'] in ('HarbingerCube','HelmetCrab','Leapleaf'):continue
        repo,sha,t=(am_repo,am_sha,am_tree) if old['mod']=='AlexsMobs' else (tf_repo,tf_sha,tf_tree)
        source=old['source'].split('/blob/'+sha+'/')[-1]
        jobs.append((old['identity'],old['mod'],repo,sha,t,source,old['layout'],old['support_observation']))
    wanted='Alligator Badger BlackBear BrownBear Boar Coyote Deer FeralWolf Fox Gazelle Moose Reindeer Squirrel Walrus'.split()
    for name in wanted:
        source=next((x['path'] for x in bap_tree['tree'] if x['path'].endswith('/entity/Model'+name+'.java')),None)
        if source:jobs.append((name,'BetterAnimalsPlus',bap_repo,bap_sha,bap_tree,source,'Native source anatomy','Limb / head / body connection'))
    natural_tree=json.loads((ROOT/'build/bestiary-v41/reference-trees/Naturalist.json').read_text())
    for name in 'alligator bear boar deer elephant giraffe hippo lion lizard rhino tortoise zebra'.split():
        src='src/main/resources/assets/naturalist/geo/entity/'+name+'.geo.json'
        jobs.append((name,'Naturalist','Starfish-Studios/Naturalist',natural_tree['sha'],natural_tree,src,'Author Geo cuboid anatomy','Quadruped head / body / limb connection'))
    critters=json.loads((ROOT/'build/bestiary-v41/reference-trees/Critters.json').read_text())
    for name in ('ferret','otter','red_panda'):
        src='common/src/main/resources/assets/crittersandcompanions/geo/entity/'+name+'.geo.json'
        jobs.append((name,'CrittersAndCompanions','bonsaistudi0s/CrittersAndCompanions',critters['sha'],critters,src,'Author Geo cuboid anatomy','Muzzle / low body / connected tail'))
    empty=CACHE/'empty.animation.json';empty.write_text('{"animations":{}}')
    def load(job):
        name,mod,repo,sha,t,src,layout,support=job
        try:
            url='https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+src;source=cached(url).read_text()
            if mod in ('Naturalist','CrittersAndCompanions'):
                quads=g.geometry(name,geo_path=cached(url),animation_path=empty);faces=[];points=[];warnings=[]
                for p,uv,bone in quads:
                    n=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(n)
                    if length>1e-8:faces.append((p,n/length,bone));points.extend(p)
                points=np.array(points)
            else:
                parts,warnings=r.parse_am(source,name) if mod=='AlexsMobs' else r.parse_tf(source)
                faces,points=r.geometry(parts)
            if not len(points) or len(faces)<6 or warnings:return []
            gray=r.render(faces,points,40,(300,260));rows=[]
            for texture in textures(t,name):
                texurl='https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+texture;file=cached(texurl);atlas=Image.open(file).convert('RGBA')
                if max(atlas.size)>512:continue
                card=Image.new('RGB',(600,330),'#ecece4');dr=ImageDraw.Draw(card)
                dr.text((8,5),mod+' / '+name+' / '+Path(texture).stem,font=font(14),fill='black');card.paste(gray,(0,28))
                scale=max(1,min(260//atlas.width,260//atlas.height));atlas=atlas.resize((atlas.width*scale,atlas.height*scale),Image.Resampling.NEAREST)
                card.paste(atlas,(310,38),atlas)
                dr.text((8,294),'SOURCE ANATOMY (GRAY) + ACTUAL ATLAS / shared rig: '+name,font=font(12),fill='black')
                dr.text((8,312),'Not an in-game render; constructor pose; no animation or renderer layers.',font=font(11),fill='black')
                filename=mod.lower()+'-'+name.lower()+'-'+Path(texture).stem+'.png';card.save(OUT/filename)
                rows.append(dict(identity=Path(texture).stem,model_family=name,mod=mod,commit=sha,model_source='https://github.com/'+repo+'/blob/'+sha+'/'+src,texture_source='https://github.com/'+repo+'/blob/'+sha+'/'+texture,texture_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),image=filename,viewed=False,layout=layout,support=support,limitations='Source reconstruction + raw atlas; not runtime textured model. Same-family coats do not imply independent rigs.'))
            return rows
        except Exception as exc:
            print('Excluded',mod,name,str(exc)[:110],flush=True);return []
    records=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for rows in ex.map(load,jobs):records+=rows
    for i,row in enumerate(records):row['index']=i+1
    (OUT/'candidates.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    for start in range(0,len(records),12):
        sheet=Image.new('RGB',(1800,1340),'#ecece4');dr=ImageDraw.Draw(sheet)
        for j,row in enumerate(records[start:start+12]):
            card=Image.open(OUT/row['image']);x=(j%3)*600;y=(j//3)*335;sheet.paste(card,(x,y));dr.text((x+3,y+25),str(row['index']),font=font(14),fill='black')
        sheet.save(OUT/f'sheet-{start//12+1:02}.jpg',quality=93)
    print('Quadruped reference entries',len(records),'independent model families',len({(row['mod'],row['model_family']) for row in records}),flush=True)
if __name__=='__main__':main()
