"""Fetch pinned primary-source Java for use/charge comparisons, never production assets."""
from pathlib import Path
import concurrent.futures, hashlib, io, json, subprocess, urllib.request, zipfile, ssl, re
CTX=ssl.create_default_context(cafile="/etc/ssl/cert.pem")
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Dynasty-implementation-study"}),context=CTX,timeout=25) as response:return response.read()
ROOT=Path(__file__).resolve().parents[2]/'build/item-use-references'
REPOS=['VazkiiMods/Botania','Creators-of-Create/Create','BluSunrize/ImmersiveEngineering','mekanism/Mekanism','CoFH/ThermalExpansion','CoFH/ThermalFoundation','SlimeKnights/TinkersConstruct','klikli-dev/occultism','baileyholl/Ars-Nouveau','TeamPneumatic/pnc-repressurized','WayofTime/BloodMagic','Mahjerion/mahou-tsukai','Shadows-of-Fire/Apotheosis','VazkiiMods/Quark','TeamTwilight/twilightforest','AlexModGuy/AlexsMobs','AlexModGuy/Ice_and_Fire','Polarice3/Goety-2','Tslat/Advent-Of-Ascension','DivineRPG/DivineRPG','Mickelus/tetra','Aizistral-Studios/Enigmatic-Legacy','TheIllusiveC4/Artifacts','CammiesCorner/Arcanus','DaedalusGame/EmbersRekindled','Team-EnderIO/EnderIO','TeamWizardry/Wizardry','The-Nexus-Project/NuclearCraft','Darkhax-Minecraft/More-Bows','Team-Roots/Roots','The-Aether-Team/The-Aether','Lothrazar/Cyclic','P3pp3rF1y/Reliquary','ochotonida/artifacts','Vazkii/Psi','iron431/irons-spells-n-spellbooks','Electroblob77/Wizardry','ZsoltMolnarrr/SpellEngine','ZsoltMolnarrr/Archers','DaedalusDev/SimplySwords','Soulslike-Weaponry/Soulslike-Weaponry','L_Ender/cataclysm','lender544/new1.20.1','TheGreyGhost/MinecraftByExample','SpartanWeapons/SpartanWeaponry','ObliviousSpartan/SpartanWeaponry','willatendo/SimplyMore','Moriyashiine/bewitchment','TeamLapen/Vampirism','TeamLapen/Werewolves','cominixo/BetterDiving','TeamTwilight/ImmersiveWeapons']
def fetch(repo):
    dest=ROOT/repo.replace('/','__');meta=dest/'source.json'
    if meta.exists():return {'repo':repo,'cached':True}
    try:
        sha=subprocess.check_output(['git','ls-remote','https://github.com/'+repo+'.git','HEAD'],text=True,stderr=subprocess.DEVNULL,timeout=30).split()[0]
        dest.mkdir(parents=True,exist_ok=True)
        tree=json.loads(get('https://api.github.com/repos/'+repo+'/git/trees/'+sha+'?recursive=1'))
        (dest/'tree.json').write_text(json.dumps(tree))
        paths=[entry['path'] for entry in tree.get('tree',[]) if entry.get('type')=='blob' and entry['path'].endswith('.java') and not any(x in Path(entry['path']).parts for x in ('generated','datagen','data','test','model')) and (re.search(r'/(item|items|equipment|weapon|weapons)/',entry['path'],re.I) or re.search(r'(Bow|Crossbow|Charge|UseItem|Player|Overlay|HUD|HeldItem|HandRender)',Path(entry['path']).name))]
        def one(rel):
            target=dest/rel
            if target.exists():return True
            try:
                data=get('https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+rel)
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);return True
            except Exception:return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as sources:count=sum(sources.map(one,paths))
        meta.write_text(json.dumps({'repo':repo,'sha':sha,'java_files':count,'candidate_files':len(paths),'fetch_mode':'Pinned recursive tree plus candidate raw Java only; no textures/models downloaded'},indent=2))
        return {'repo':repo,'files':count}
    except Exception as e:return {'repo':repo,'error':str(e)}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for task in concurrent.futures.as_completed([pool.submit(fetch,repo) for repo in REPOS]):print(json.dumps(task.result()),flush=True)
