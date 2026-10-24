"""Prepare candidate anatomy/atlas cards for the next light-humanoid study.

No candidate is counted as viewed automatically. Static source reconstruction is
labelled; shared humanoid rigs are disclosed, never counted as independent rigs.
"""
from pathlib import Path
import re,json,sys,importlib.util,hashlib,collections
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]
LIB=ROOT/'build/creature-reference-1000'
OUT=ROOT/'build/bestiary-v43/humanoid-candidates';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(LIB))
spec=importlib.util.spec_from_file_location('reference_parse',LIB/'render.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
g=parser.r

PICKS={
'Polarice3/Goety-2':'''Apostle WindCaller Geomancer Blastling Watchling TallSkull HauntedSkull DrownedServant Blackguard BoundIllager Conquillager Crone Crusher Cryologer Cultist Damned DrownedNecromancer DrownedServant EnderKeeper Enchanter Envioker HauntedArmor Heresiarch Heretic Iceologer IllagerServant ImperialGuard Inquillager LichMode Maverick Minister Minion ModWitch Mountaineer Necromancer Piker Preacher Prisoner Reaper Reprobate Rogueguard RoyalGuard SkeletonVillager Sorcerer StormCaster SunkenSkeleton TallSkull Tormentor Vanguard VindicatorChef Vizier Warlock Wight WitherNecromancer Wraith ZPiglin ZombieServant ZombieVillagerServant'''.split(),
'DivineRPG/DivineRPG':'''DungeonPrisoner EternalArcher LadyLuna EnchantedArcher EnchantedWarrior Mage Mystic Sorcerer SoulStealer SunArcher TwilightArcher AridWarrior Kobblin MysteriousMan Densos Raglok Wreck Groglin Gruzzorlug Greenfeet Madivel Samek HiveSoldier CryptKeeper Dreamwrecker'''.split(),
'TeamTwilight/twilightforest':'''Adherent Lich Redcap LowerGoblinKnight KnightPhantom Wraith'''.split(),
'TheDarkPeasant/Illage-and-Spillage--Respillaged':'''Absorber Engineer Faker Freakager Hinder Igniter IllagerSoul Magispeller Poker Preserver Sniper Spiritcaller Twittollager VillagerSoul'''.split(),
'iron431/Irons-Spells-n-Spellbooks':'''Apothecarist Archevoker Cryomancer Cultist DeadKing FireBoss Keeper Necromancer Priest Pyromancer SummonedSkeleton SummonedZombie'''.split(),
'Infamous-Misadventures/Dungeons-Mobs':'''DungeonsIllusioner Enchanter Geomancer Iceologer Mage Mountaineer RoyalGuard Windcaller DrownedNecromancer Necromancer SkeletonVanguard SunkenSkeleton Wraith'''.split(),
'Fuzss/illager-invasion':None,
'Tslat/Advent-Of-Ascension': 'VineWizard Silencer LelyetianCaster LelyetianWarrior Goblin Hag Paladin RuneTemplar RunicGuardian SpectralWizard ArcWizard ShyreKnight'.split(),
}

def normalized(s):return re.sub('[^a-z0-9]','',s.lower())
def name(p):return re.sub(r'^Model|Model$','',p.stem)
def url(meta,base,p):return f'https://github.com/{meta["repo"]}/blob/{meta["sha"]}/{p.relative_to(base)}'

def java_parts(path,models,seen=None):
    seen=set() if seen is None else seen
    if path in seen:raise ValueError('inheritance cycle')
    seen.add(path);text=path.read_text();clean=g.strip_comments(text)
    # Prefer literal mesh factories over a createBodyLayer wrapper returning createMesh().
    method=re.search(r'(?:public|protected) static (?:MeshDefinition|LayerDefinition) (?:createMesh|createBodyLayer|createLayer|getTexturedModelData)\s*\([^)]*\)\s*\{',clean)
    parts={};warnings=[];sources=[path]
    if method:
        body=g.block(clean,method.end()-1)
        parts,warnings=g.parse_tf(body)
        if not any(v['boxes'] for v in parts.values()):parts,warnings=parser.parse(text,path.stem)
    else:parts,warnings=parser.parse(text,path.stem)
    parent=re.search(r'extends\s+([A-Za-z0-9_]+)',clean)
    if not any(v['boxes'] for v in parts.values()) and parent and parent[1] in models:
        parts,warnings,sources2=java_parts(models[parent[1]],models,seen);sources+=sources2
    # Fully literal named factory calls may supply a body without Java inheritance.
    if method:
        for factory in re.findall(r'([A-Za-z0-9_]+)\.create(?:Mesh|BodyLayer)\(',body):
            if factory in models and (not parent or factory!=parent[1]):
                inherited,warn,other=java_parts(models[factory],models,seen.copy());inherited.update(parts);parts=inherited;warnings+=warn;sources+=other
    # Fully literal parent factory calls can define the body before local additions.
    if method and parent and parent[1] in models and re.search(re.escape(parent[1])+r'\.create\w*\(',body):
        inherited,warn,other=java_parts(models[parent[1]],models,seen);inherited.update(parts);parts=inherited;warnings+=warn;sources+=other
    return parts,warnings,sources

def main():
    directories=[LIB/'Polarice3__Goety-2',LIB/'DivineRPG__DivineRPG',LIB/'TeamTwilight__twilightforest',LIB/'Tslat__Advent-Of-Ascension-1.16.5']
    additions=ROOT/'build/bestiary-v43/references'
    directories += [p for p in additions.iterdir() if (p/'source.json').exists() and (p.name.endswith('__1.20.1') or p.name.endswith('__1.20.1-legacy') or p.name.startswith(('Infamous-','TheDarkPeasant')))]
    rows=[];excluded=[];seen=set()
    for base in directories:
        meta=json.loads((base/'source.json').read_text());repo=meta['repo'];pick=PICKS[repo]
        java=list(base.rglob('*.java'));models={p.stem:p for p in java if p.name.endswith('Model.java') or p.name.startswith('Model')}
        renderers=[p for p in java if ('render' in str(p).lower() and ('Render' in p.name)) or (repo=='DivineRPG/DivineRPG' and p.name=='EntityRegistry.java')]
        jobs=[(p,name(p),None) for p in models.values()] if repo!='Fuzss/illager-invasion' else []
        if repo=='Fuzss/illager-invasion':
            for renderer in renderers:
                entity=renderer.stem.removesuffix('Render')
                if entity not in 'Alchemist Archivist Basher Firecaller Inquisitor Invoker Marauder Necromancer Provoker Sorcerer Surrendered'.split():continue
                linked=re.findall(r'new ([A-Za-z0-9_]+)<>',renderer.read_text())
                if linked and linked[0] in models:jobs.append((models[linked[0]],entity,renderer))
        for p,short,explicit_renderer in jobs:
            if pick is not None and short not in pick:continue
            if any(w in str(p).lower() for w in ['/armor/','/item/','/block/']):continue
            texts=[(p,p.read_text())]+[(q,q.read_text()) for q in renderers if (q==explicit_renderer or normalized(short) in normalized(q.stem) or q.name=='EntityRenders.java')]
            texture_pairs=[]
            for q,text in texts:
                if q.name=='EntityRenders.java':text='\n'.join(line for line in text.splitlines() if 'new '+p.stem+'(' in line)
                for texture in re.findall(r'"((?:textures/[^"\s]+/)?[^"/\s]+\.png)"',text):
                    found=list(base.glob('**/assets/*/'+texture)) if texture.startswith('textures/') else list(base.glob('**/textures/**/'+texture))
                    if found and not any(k in texture for k in ('glow','eyes','overlay','glowing')):texture_pairs.append((found[0],q))
            if repo=='DivineRPG/DivineRPG' and not texture_pairs:
                for registry in renderers:
                    for line in registry.read_text().splitlines():
                        if p.stem not in line or 'new '+p.stem not in line:continue
                        for literal in re.findall(r'"([a-z_]+)"',line):
                            if normalized(literal)!=normalized(short):continue
                            found=list(base.glob('**/textures/entity/'+literal+'.png'))
                            if found:texture_pairs.append((found[0],registry))
            if repo=='Polarice3/Goety-2' and short=='Prisoner':texture_pairs=[]
            if not texture_pairs:
                excluded.append(dict(repo=repo,model=str(p.relative_to(base)),reason='No literal model/renderer texture binding'));continue
            texture,binding=texture_pairs[0]
            try:
                content=p.read_text();parts,warnings,sources=java_parts(p,models)
                geo=re.findall(r'"(geo/[^"\s]+\.geo\.json)"',content)
                if not geo:
                    for parent in sources[1:]:geo+=re.findall(r'"(geo/[^"\s]+\.geo\.json)"',parent.read_text())
                # Resolve a model resource referenced through its actual declaring entity.
                if not geo:
                    for owner,field in re.findall(r'([A-Za-z0-9_]+)\.(modelResource)','\n'.join(x.read_text() for x in sources)):
                        for declaration in java:
                            if declaration.stem==owner:
                                geo+=re.findall(r'"(geo/[^"\s]+\.geo\.json)"',declaration.read_text());sources.append(declaration)
                # Some GeoModels inherit the resource function, not literal boxes.
                if geo:
                    files=list(base.glob('**/assets/*/'+geo[0]));assert files
                    parts,warnings=parser.extra_formats.geo(files[0]);sources.append(files[0])
                if warnings:raise ValueError('; '.join(warnings[:3]))
                fs,points=g.geometry(parts)
                if len(fs)<36:raise ValueError('Incomplete/unsupported body reconstruction')
                sig=hashlib.sha256((json.dumps(parts,sort_keys=True)+hashlib.sha256(texture.read_bytes()).hexdigest()).encode()).hexdigest()
                if sig in seen:raise ValueError('Exact model-and-atlas duplicate')
                seen.add(sig)
            except Exception as error:
                excluded.append(dict(repo=repo,model=str(p.relative_to(base)),reason=str(error)));continue
            canonical=short.lower().replace('skeletonvanguard','vanguard')
            if repo=='Infamous-Misadventures/Dungeons-Mobs' and any(r['repo']=='Polarice3/Goety-2' and r['identity'].split(':')[-1].lower()==canonical for r in rows):
                excluded.append(dict(repo=repo,model=str(p.relative_to(base)),reason='Same Minecraft Dungeons creature in another port; not counted again'));continue
            i=len(rows)+1;key=f'{i:03}-{repo.split("/")[-1]}-{short}';card=Image.new('RGB',(720,390),'#e9ebe4');draw=ImageDraw.Draw(card)
            card.paste(g.render(fs,points,35,(345,310)),(0,35));atlas=Image.open(texture).convert('RGBA')
            factor=max(1,min(340//atlas.width,300//atlas.height));im=atlas.resize((atlas.width*factor,atlas.height*factor),Image.Resampling.NEAREST)
            if im.width>340 or im.height>300:im.thumbnail((340,300),Image.Resampling.NEAREST)
            card.paste(im,(365,40),im);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16)
            draw.text((8,5),f'{i:03} {repo.split("/")[-1]} / {short}',font=font,fill='#283936')
            draw.text((8,354),'源码静态构造 + 原始图集；非游戏画面 / 含未隐藏构造',font=font,fill='#283936')
            card.save(OUT/(key+'.png'));(OUT/(key+'.model.json')).write_text(json.dumps(parts))
            rows.append(dict(number=i,identity=repo+':'+short,repo=repo,branch=meta.get('branch'),commit=meta['sha'],model_source=url(meta,base,p),construction_sources=[url(meta,base,s) for s in sources],texture_source=url(meta,base,texture),renderer_source=url(meta,base,binding),texture_sha256=hashlib.sha256(texture.read_bytes()).hexdigest(),card=key+'.png',viewed=False))
    for start in range(0,len(rows),8):
        sheet=Image.new('RGB',(1440,1580),'#e9ebe4')
        for j,row in enumerate(rows[start:start+8]):sheet.paste(Image.open(OUT/row['card']),(j%2*720,j//2*395))
        sheet.save(OUT/f'sheet-{start//8+1:02}.png')
    (OUT/'candidates.json').write_text(json.dumps(dict(items=rows,excluded=excluded,counts=dict(collections.Counter(r['repo'] for r in rows)),status='CANDIDATES_NOT_YET_VISUALLY_REVIEWED'),ensure_ascii=False,indent=2)+'\n')
    print(len(rows),'model-and-atlas candidates; no automatic viewed counts');print(collections.Counter(r['repo'] for r in rows));print('excluded',len(excluded))

if __name__=='__main__':main()
