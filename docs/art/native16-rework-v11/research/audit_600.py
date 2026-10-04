"""Read-only, block-ID grounded native-16 reference audit for Dynasty v11.

Sources are third-party local assets for study, never Dynasty candidate assets.
One sampled image per genuine blockstate ID; global RGBA-pixel deduplication.
"""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont
from collections import Counter, defaultdict
import json, io, hashlib, math, re

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
OUT = ROOT / 'docs/art/native16-rework-v11/research'
RAW = ROOT / 'work/native16-v11/references'
VERSIONS = Path('/Users/a15356015027/Public/.minecraft/versions')
VANILLA = Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')
SOURCES = {
    '原版 Minecraft 1.20.1': ['minecraft'],
    '愚者': ['twilightforest','alexscaves','create','deeperdarker','aether','cataclysm','goety','graveyard','iceandfire','decorative_blocks'],
    '乌托邦探险之旅3.5.2': ['chipped','stoneworks','supplementaries','galosphere','twigs','meadow','bbb','ecologics','bountifulfares'],
    '登神者：天阶咏叹v1.5': ['quark','apotheosis'],
    '锻造之旅': ['undergarden','netherexp','outer_end','tetra','endergetic'],
    '涟漪之篇·如涟漪之所见': ['malum','geodes'],
}
LIMIT = 600
EXCLUDE = re.compile(r'(?:^|_)(?:waxed|infested|budding|stairs?|slabs?|walls?|buttons?|pressure_plate|fences?|gates?|doors?|trapdoors?|saplings?|potted|crops?|flowers?|torches?|banners?|panes?|carpets?|rails?|signs?|beds?|leaves|leash|vine|vines|mushrooms?|wool|concrete|terracotta|stained_glass)(?:_|$)')
PRIORITIES = ['brick','raw_stone','ore','functional','wood','metal','carved','tile','natural','other']
FUNCTIONS = ('furnace','smoker','blast','enchant','table','bench','basin','altar','pedestal','casing','machine','depot','press','mixer','anvil','crate','cabinet','barrel','chest','spawner','kiln','workstation','loom','pump','compactor','saw','grind','crusher','battery','generator','resonator','catalyst','hopper','dispenser','dropper','vault','tank','display','chute')
def digest(b): return hashlib.sha256(b).hexdigest()
def category(name):
    tokens=set(re.split('[/_]',name))
    if any(x in tokens for x in FUNCTIONS): return 'functional'
    if 'ore' in name and not any(x in name for x in ('spore','core','forest','forester')): return 'ore'
    if 'chisel' in name or 'carved' in name or 'engraved' in name: return 'carved'
    if 'brick' in name: return 'brick'
    if any(x in name for x in ('tile','polished','smooth','pillar')): return 'tile'
    if any(x in name for x in ('stone','rock','slate','cobble','basalt','marble','granite','diorite','andesite','limestone','tuff','scoria','gabbro','rhyolite','dripstone','permafrost')): return 'raw_stone'
    if any(x in tokens for x in ('plank','planks','log','wood','timber','bamboo','beam')): return 'wood'
    if any(x in name for x in ('copper','iron','gold','steel','brass','bronze','silver','lead','metal','zinc','rust','tin_')): return 'metal'
    if any(x in name for x in ('dirt','soil','sand','mud','clay','moss','root','peat','ash','gravel','snow','ice','calcite','crystal','prismarine')): return 'natural'
    return 'other'

class Audit:
    def __init__(self):
        self.archives = {}; self.names = {}; self.origins = {}; self.resolutions = {}; self.inventory=[]
    def add(self, pack, jar, namespaces):
        z=ZipFile(jar); names=set(z.namelist())
        for ns in namespaces:
            self.archives[ns]=z; self.names[ns]=names; self.origins[ns]=(pack,str(jar))
            count=sum(n.startswith(f'assets/{ns}/blockstates/') and n.endswith('.json') for n in names)
            self.inventory.append({'pack':pack,'namespace':ns,'jar':str(jar),'blockstate_count':count})
    def locate(self, resource, kind):
        ns, path = resource.split(':',1) if ':' in resource else ('minecraft',resource)
        name=f'assets/{ns}/{kind}/{path}'
        z=self.archives.get(ns)
        if z and name in self.names[ns]: return z,name
        return None,None
    def model(self, resource, visited=None):
        if resource in self.resolutions:return self.resolutions[resource]
        if visited is None:visited=set()
        if resource in visited:return None
        visited=set(visited)|{resource}
        z,path=self.locate(resource+'.json','models')
        if not z:return None
        try:data=json.loads(z.read(path))
        except Exception:return None
        parent=self.model(data['parent'],visited) if 'parent' in data else None
        merged={'textures':dict(parent['textures']) if parent else {},'elements':list(parent['elements']) if parent else [],'chain':list(parent['chain']) if parent else []}
        merged['textures'].update(data.get('textures',{}))
        if 'elements' in data:merged['elements']=data['elements']
        merged['chain'].append({'resource':path,'sha256':digest(z.read(path))})
        self.resolutions[resource]=merged
        return merged
    def texture(self, val, bindings):
        seen=set()
        while val.startswith('#'):
            if val in seen:return None
            seen.add(val);val=bindings.get(val[1:],'')
            if not val:return None
        z,path=self.locate(val+'.png','textures')
        if not z:return None
        raw=z.read(path)
        try:im=Image.open(io.BytesIO(raw)).convert('RGBA')
        except Exception:return None
        # Deliberately static-only to keep this audit unambiguous.
        if im.size != (16,16):return None
        im.putdata([c if c[3] else (0,0,0,0) for c in im.getdata()])
        colors=Counter(im.getdata())
        if sum(n for c,n in colors.items() if c[3]==255) < 200:return None
        if any(0<c[3]<255 for c in colors):return None
        if len(colors)<4:return None
        ns=val.split(':',1)[0] if ':' in val else 'minecraft'
        top=Counter(c[:3] for c in im.getdata() if c[3])
        return {'resource':path,'texture_origin_pack':self.origins[ns][0],'texture_origin_jar':self.origins[ns][1],
                'size':[16,16],'frame_size':[16,16],'animation':'static 16×16; no strip frames sampled',
                'file_sha256':digest(raw),'rgba_sha256':digest(im.tobytes()),
                'unique_opaque_rgb':len(top),'top8_coverage':round(sum(n for c,n in top.most_common(8))/sum(top.values()),4),
                'palette_top12':[{'hex':'#%02x%02x%02x'%c,'count':n} for c,n in top.most_common(12)],
                '_raw':raw,'_image':im}
    def collect(self,ns):
        z=self.archives[ns];rows=[]
        for blockstate in sorted(n for n in self.names[ns] if n.startswith(f'assets/{ns}/blockstates/') and n.endswith('.json')):
            name=blockstate.split('/blockstates/')[1][:-5]
            if EXCLUDE.search(name):continue
            raw=z.read(blockstate)
            try:bs=json.loads(raw)
            except Exception:continue
            variants=[]
            for key,values in bs.get('variants',{}).items():
                for v in values if isinstance(values,list) else [values]:
                    if isinstance(v,dict) and 'model' in v:variants.append((key,v['model']))
            for part in bs.get('multipart',[]):
                values=part.get('apply',[])
                for v in values if isinstance(values,list) else [values]:
                    if isinstance(v,dict) and 'model' in v:variants.append((json.dumps(part.get('when',{})),v['model']))
            variants.sort(key=lambda v:('lit=true' in v[0] or 'active=true' in v[0], 'facing=north' not in v[0], v[0]))
            options=[]; hashes=set()
            for state,resource in variants:
                model=self.model(resource)
                if not model:continue
                used=[]
                for element in model['elements']:
                    for face,fd in element.get('faces',{}).items():
                        ref=fd.get('texture','')
                        if ref and (face,ref) not in used:used.append((face,ref))
                used.sort(key=lambda fr:(0 if any(x in fr[1] for x in ('front','side','all')) else 1,{'north':0,'east':1,'south':2,'west':3,'up':4,'down':5}.get(fr[0],6)))
                for face,ref in used:
                    t=self.texture(ref,model['textures'])
                    if not t or t['rgba_sha256'] in hashes:continue
                    hashes.add(t['rgba_sha256'])
                    t.update({'block_id':f'{ns}:{name}','namespace':ns,'pack':self.origins[ns][0],
                              'jar':self.origins[ns][1],'blockstate_resource':blockstate,'blockstate_sha256':digest(raw),
                              'state_or_condition':state,'model_id':resource,'model_chain':model['chain'],
                              'face':face,'face_texture_binding':ref,'resolved_texture_bindings':model['textures'],
                              'category':category(name)})
                    options.append(t)
                # Other random variants/states should not inflate candidates.
                if options:break
            if options: rows.append(options)
        return rows

def main():
    OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
    audit=Audit();audit.add('原版 Minecraft 1.20.1',VANILLA,['minecraft'])
    for pack,namespaces in SOURCES.items():
        if pack.startswith('原版'):continue
        pending=set(namespaces)
        for jar in sorted((VERSIONS/pack/'mods').glob('*.jar')):
            if not pending:break
            try:
                with ZipFile(jar) as z:
                    found={p.split('/')[1] for p in z.namelist() if p.startswith('assets/') and '/blockstates/' in p and p.endswith('.json')}&pending
                if found:audit.add(pack,jar,sorted(found));pending-=found
            except Exception:pass
        if pending:print('Missing namespaces',pack,pending)
    available={ns:audit.collect(ns) for ns in audit.archives}
    # Diverse category queues; deterministic hash order avoids alphabetic truncation.
    queues={}
    for ns,groups in available.items():
        cats=defaultdict(list)
        for options in groups:cats[options[0]['category']].append(options)
        for cat in cats:cats[cat].sort(key=lambda oo:digest(oo[0]['block_id'].encode()))
        queue=[]
        while any(cats.values()):
            for cat in PRIORITIES:
                if cats[cat]:queue.append(cats[cat].pop(0))
        queues[ns]=queue
    picked=[];used_hashes=set();used_ids=set();counts=Counter();categories=Counter();packs=Counter()
    def pick(ns):
        cap=80 if ns=='minecraft' else 35
        if counts[ns]>=cap:return False
        while queues[ns]:
            options=queues[ns].pop(0)
            if options[0]['block_id'] in used_ids:continue
            # Never switch to a secondary face to rescue an otherwise duplicate block.
            # Waxed/unwaxed or inactive/active aliases must not inflate the block count.
            for row in options[:1]:
                if row['rgba_sha256'] in used_hashes:continue
                if row['category']=='other' and categories['other']>=55:continue
                picked.append(row);used_ids.add(row['block_id']);used_hashes.add(row['rgba_sha256'])
                counts[ns]+=1;categories[row['category']]+=1;packs[row['pack']]+=1
                return True
        return False
    for _ in range(80):pick('minecraft')
    namespaces=[ns for ns in queues if ns!='minecraft']
    while len(picked)<LIMIT:
        progress=False
        for ns in namespaces:
            if len(picked)>=LIMIT:break
            progress=pick(ns) or progress
        if not progress:break
    # Group for visual inspection while retaining broad global sampling.
    picked.sort(key=lambda r:(list(SOURCES).index(r['pack']),list(SOURCES[r['pack']]).index(r['namespace']),PRIORITIES.index(r['category']),r['block_id']))
    for i,row in enumerate(picked,1):
        path=RAW/f'{i:03d}-{row["block_id"].replace(":","--").replace("/","-")}.png'
        path.write_bytes(row.pop('_raw'));row.pop('_image')
        row['index']=i;row['reference_png']=str(path)
        row['visual_review_page']=(i-1)//50+1
    result={'scope':'Read-only local resource study. Third-party PNGs are never output as Dynasty candidate assets.',
            'selection':'One genuine blockstate ID per sample; first renderable variant, first native-16 actual element face binding resolved through parent models. A globally duplicate first face rejects the block; secondary faces are NEVER substituted to rescue a duplicate. Excludes waxed/infested/budding aliases, decorative color families and shape-only derivatives. Global RGBA deduplication across all packs, namespaces and versions (transparent RGB normalized). Category round-robin; at most 35/mod and 80 vanilla. Static native 16×16 only.',
            'count':len(picked),'unique_block_ids':len(used_ids),'unique_pixel_hashes':len(used_hashes),
            'pack_counts':dict(packs),'namespace_counts':dict(counts),'category_counts':dict(categories),
            'eligible_block_counts':{ns:len(rows) for ns,rows in available.items()},
            'source_inventory':audit.inventory,'samples':picked,
            'limitations':'A referenced face is not a complete block render; complex model/UV geometry is recorded but not recreated. Pack provenance means the installed pack containing the exact jar, not authorship. No claim that every sampled style is suitable for Dynasty.'}
    (OUT/'reference-600-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',11)
    title=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    pages=math.ceil(len(picked)/50)
    for page in range(pages):
        canvas=Image.new('RGB',(1500,1120),'#1b2229');d=ImageDraw.Draw(canvas)
        d.text((20,12),f'Native 16 block reference audit | page {page+1}/{pages} | original 1x + nearest 7x',font=title,fill='#eeeeee')
        for j,row in enumerate(picked[page*50:(page+1)*50]):
            x=(j%10)*150;y=55+(j//10)*211
            im=Image.open(row['reference_png']).convert('RGBA')
            d.rectangle((x+1,y,x+148,y+200),fill='#252f37')
            canvas.paste(im.resize((112,112),Image.Resampling.NEAREST),(x+19,y+8),im.resize((112,112),Image.Resampling.NEAREST))
            canvas.paste(im,(x+6,y+126),im)
            d.text((x+27,y+126),f'{row["index"]:03d} / {row["category"]}',font=small,fill='#cad8dc')
            d.text((x+5,y+146),row['namespace'][:22],font=font,fill='white')
            name=row['block_id'].split(':',1)[1]
            for k in range(2):d.text((x+5,y+163+k*15),name[k*22:(k+1)*22],font=small,fill='#c0d2d9')
        canvas.save(OUT/f'contact-{page+1:02d}.png')
    (OUT/'reference-600-index.tsv').write_text('index\tblock_id\tpack\tcategory\tresource\tsize\trgba_sha256\tjar\n'+''.join(f'{r["index"]}\t{r["block_id"]}\t{r["pack"]}\t{r["category"]}\t{r["resource"]}\t16x16\t{r["rgba_sha256"]}\t{r["jar"]}\n' for r in picked))
    summary={k:v for k,v in result.items() if k not in ('samples','source_inventory','eligible_block_counts')}
    (OUT/'reference-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    assert len(picked)>=550, f'Insufficient distinct block references: {len(picked)}'
    assert len(used_ids)==len(used_hashes)==len(picked)
    assert all(n <= (80 if ns=='minecraft' else 35) for ns,n in counts.items())

if __name__=='__main__':main()
