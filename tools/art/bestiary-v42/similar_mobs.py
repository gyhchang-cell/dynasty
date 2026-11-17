"""Study actual distinct humanoid / semi-humanoid MC mobs, not skin-count padding.

Models are author source bind-pose reconstructions paired with original atlas.
No external material is used by our production exporters. Each choice has an
actual entity identity, pinned model source, texture file and renderer evidence.
"""
from pathlib import Path
import json,re,math,hashlib,importlib.util,sys,collections
from PIL import Image,ImageDraw,ImageFont
from build_models import ROOT,OUT

LIB=ROOT/'build/creature-reference-1000';CACHE=ROOT/'build/bestiary-v42/similar-mobs';CACHE.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
def font(n):return ImageFont.truetype(FONT,n)
def norm(s):return re.sub('[^a-z0-9]','',s.lower())

WHITELIST={
 'Polarice3/Goety-2':'''Blackguard Blastling Conquillager Crusher Cryologer DrownedNecromancer Enchanter Endersent Envioker Geomancer GraveGolem IceGolem Iceologer ImperialGuard Inquillager Maverick Minister Necromancer Piker Preacher Reprobate Rogueguard RoyalGuard Sorcerer SquallGolem StormCaster Vanguard Watchling Wight WindCaller WitherNecromancer RedstoneGolem RedstoneMonstrosity Ravaged Whisperer Leapleaf'''.split(),
 'AlexModGuy/AlexsMobs':'''Skreecher Bunfungus Gorilla CapuchinMonkey GeladaMonkey DropBear UnderminerDwarf'''.split(),
 'TeamTwilight/twilightforest':'''Adherent AlphaYeti CarminiteGolem Kobold Lich LowerGoblinKnight Redcap Troll Yeti'''.split(),
 'lender544/new1.20.1':'''Aptrgangr CoralGolem Coralssus DeeplingAngler DeeplingBrute Deepling DeeplingPriest DeeplingWarlock EnderGolem EnderGuardian Kobolediator Koboleton Maledictus Scylla NetheriteMonstrosity'''.split(),
 'AlexModGuy/AlexsCaves':'''Brainiac DeepOneKnight DeepOne GingerbreadMan Licowitch Teletor Underzealot'''.split(),
 'Angry-Pixel/The-Betweenlands':'''DreadfulMummy EmberlingShaman Greebling PeatMummy Stalker TarBeast Wight'''.split(),
 'DivineRPG/DivineRPG':'''DungeonConstructor DungeonDemon DungeonPrisoner Densos Dramix EternalArcher LadyLuna Raglok Reyvor SoulFiend Sunstorm TwilightDemon Wreck Groglin Gruzzorlug Rollum EnchantedArcher EnchantedWarrior Greenfeet Madivel Mage Megalith Mystic Samek SkythernFiend Sorcerer SoulStealer SunArcher TwilightArcher TwilightGolem AridWarrior DesertCrawler Kobblin Wildfire Biphron Bohemite CryptKeeper Cymesoid Dreamwrecker Ent Galroid HiveSoldier Lorga TheHunger'''.split(),
 'Quek04/The-Undergarden':'''Brute Denizen ForgottenGuardian Nargoyle Rotbeast Rotbelcher Rotling Rotwalker Stoneborn'''.split(),
 'Tslat/Advent-Of-Ascension':'''NightWatcher Bane Corallus Craexxeus Elusive Harkos Kajaros Klobber Mechbot Mirage Miskel Okazor Proshield Raxxan Smash Xxeus HealingGolem HiveSoldier MechaCyclops MechaSkellox Fiend FleshEater WebReaper Stitches ConstructOfResistance ConstructOfSpeed ConstructOfStrength LostSoul Merkyre VineWizard Banshee Silencer Mechachron Mechamaton Voltron Amphibior LelyetianCaster LelyetianWarrior Refluct RunicGolem Flamewalker Infernal AncientGolem Cyclops Fishix Goblin Hag SeaTroll TreeSpirit Trickster SkeleElder Paladin RuneTemplar RunicGuardian SpectralWizard ArcWizard ShyreKnight Soulscorne Soulvyre Destructor'''.split(),
}

def identity(row):
    s=Path(row['source']).name;s=re.sub(r'\.java$|\.geo\.json$','',s);s=re.sub(r'^Model|_?Model$','',s)
    return s

def main():
    spec=importlib.util.spec_from_file_location('refgeom',ROOT/'tools/art/steve-fighters-v25/nonhuman_references.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    rows=json.loads((ROOT/'build/bestiary-v42/humanoid-candidates.json').read_text())
    indexes={};renderer_indexes={};metadata={}
    for directory in LIB.iterdir():
        if not directory.is_dir() or not (directory/'source.json').exists():continue
        meta=json.loads((directory/'source.json').read_text());repo=meta['repo']
        if repo not in WHITELIST:continue
        metadata[repo]=(directory,meta);index=collections.defaultdict(list)
        for p in directory.rglob('*.png'):
            if '/textures/entity/' in str(p) or '/textures/entities/' in str(p):index[norm(p.stem)].append(p)
        indexes[repo]=index
        renderer_indexes[repo]=[(p,p.read_text(errors='replace')) for p in directory.rglob('*.java') if ('render' in str(p).lower() and ('Renderer' in p.name or 'Render' in p.name)) or (repo=='DivineRPG/DivineRPG' and p.name=='EntityRegistry.java')]
    candidates=[];excluded=[];seen=set();seen_shapes={}
    for row in rows:
        repo=row['repo'];name=identity(row);key=norm(name)
        if repo not in indexes or key not in {norm(n) for n in WHITELIST[repo]}:continue
        canonical=repo+':'+key
        if canonical in seen:continue
        directory,meta=metadata[repo]
        textures=sorted(indexes[repo].get(key,[]),key=lambda p:(len(str(p)),str(p)))
        # Require literal renderer linkage rather than accepting a similarly named texture alone.
        pairs=[]
        for tex in textures:
            asset_relative=str(tex).split('/textures/',1)[1];resource='textures/'+asset_relative
            matches=[(p,s) for p,s in renderer_indexes[repo] if resource in s or ('"'+tex.stem+'"') in s or ('"'+tex.name+'"') in s]
            if repo=='DivineRPG/DivineRPG':
                model_class=Path(row['source']).stem
                matches=[(p,s) for p,s in matches if any(model_class in line and ('"'+tex.stem+'"') in line for line in s.splitlines())]
            if matches:pairs.append((tex,matches[0][0]))
        if not pairs:excluded.append(dict(identity=canonical,reason='No exact matching atlas + literal renderer evidence in local source snapshot'));continue
        tex,renderer=pairs[0];partfile=LIB/'cards'/(row['name']+'.json')
        parts=json.loads(partfile.read_text());fs,points=g.geometry(parts)
        if not len(points):continue
        shape=tuple(sorted(json.dumps(part,sort_keys=True) for part in parts.values()))
        if shape in seen_shapes:
            excluded.append(dict(identity=canonical,reason='Identical constructor geometry to '+seen_shapes[shape]+'; not counted as another reference'))
            continue
        seen_shapes[shape]=canonical
        candidates.append((row,name,parts,tex,renderer,meta,directory));seen.add(canonical)
    # Round-robin across mods; never fill with one project's variants.
    groups=collections.defaultdict(list)
    for v in candidates:groups[v[0]['repo']].append(v)
    selected=[]
    while any(groups.values()) and len(selected)<100:
        for repo in WHITELIST:
            if groups[repo] and len(selected)<100:selected.append(groups[repo].pop(0))
    records=[]
    for i,(row,name,parts,tex,renderer,meta,directory) in enumerate(selected):
        fs,points=g.geometry(parts);gray=g.render(fs,points,35,(340,300));atlas=Image.open(tex).convert('RGBA')
        card=Image.new('RGB',(720,380),'#e9ebe4');card.paste(gray,(0,35));d=ImageDraw.Draw(card)
        factor=max(1,min(320//atlas.width,285//atlas.height));im=atlas.resize((atlas.width*factor,atlas.height*factor),Image.Resampling.NEAREST)
        if im.width>340 or im.height>300:im.thumbnail((340,300),Image.Resampling.NEAREST)
        card.paste(im,(365,40),im)
        title=f'{i+1:03} {meta["repo"].split("/")[-1]} / {name}'
        d.text((10,5),title,font=font(17),fill='#253b37');d.text((10,348),'源码静态体块 + 作者原始图集；非游戏画面，不复制资产',font=font(16),fill='#253b37')
        file=f'{i+1:03}-{name}.png';card.save(CACHE/file)
        source=row['source'];texture_url=f'https://github.com/{meta["repo"]}/blob/{meta["sha"]}/{tex.relative_to(directory)}'
        records.append(dict(number=i+1,identity=meta['repo']+':'+name,repo=meta['repo'],commit=meta['sha'],model_source=source,texture_source=texture_url,renderer_source=f'https://github.com/{meta["repo"]}/blob/{meta["sha"]}/{renderer.relative_to(directory)}',texture_sha256=hashlib.sha256(tex.read_bytes()).hexdigest(),study=file,viewed=False,scope='Actual distinct mob model identity; bind-pose reconstruction + original atlas, not author-native animation/equipment rendering'))
    for start in range(0,len(records),8):
        sheet=Image.new('RGB',(1440,1560),'#e9ebe4');d=ImageDraw.Draw(sheet)
        for j,row in enumerate(records[start:start+8]):sheet.paste(Image.open(CACHE/row['study']),((j%2)*720,(j//2)*390))
        sheet.save(CACHE/f'sheet-{start//8+1:02}.png')
    (CACHE/'ledger.json').write_text(json.dumps(dict(count=len(records),counts=dict(collections.Counter(r['repo'] for r in records)),items=records,excluded=excluded),ensure_ascii=False,indent=2)+'\n')
    print('Prepared actual model+atlas candidates:',len(records));print(collections.Counter(r['repo'] for r in records));print('Not yet counted as visually studied')

if __name__=='__main__':main()
