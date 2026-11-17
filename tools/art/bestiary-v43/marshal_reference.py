"""Prepare relevant model + original atlas studies. Never marks a card reviewed.
One creature/model family per mod, no skins/rotations/parts as extra references.
Source reconstructions are labelled and are not game screenshots.
"""
from pathlib import Path
import importlib.util,json,re,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];LIB=ROOT/'build/creature-reference-1000';OUT=ROOT/'build/bestiary-v43/marshal-reference';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(LIB));s=importlib.util.spec_from_file_location('helpers',ROOT/'tools/art/bestiary-v43/research_candidates.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
PICKS={
'AlexModGuy__AlexsMobs': 'Froststalker KomodoDragon Anteater DropBear SeaBear Raccoon Bison Elephant Gazelle GrizzlyBear ManedWolf Moose Rhinoceros SnowLeopard Tiger Tusklin Skelewag Straddler UnderminerDwarf Farseer'.split(),
'TeamTwilight__twilightforest': 'Deer Bighorn QuestRam Boar HostileWolf MistWolf LowerGoblinKnight UpperGoblinKnight KnightPhantomOld Wraith CarminiteGolem SkeletonDruid Lich Troll RisingZombie'.split(),
'AlexModGuy__Ice_and_Fire': 'DreadBeast DreadScuttler Hippocampus Hippogryph Cyclops Troll'.split(),
'Polarice3__Goety-2': 'SkeletonWolf BlackWolf BlackBeast BearServant Trampler HauntedArmor HauntedArmorStand SkullLord TallSkull HauntedSkull Wraith Tormentor Reaper SkeletonVillager Wight Vanguard Blackguard SunkenSkeleton ImperialGuard RoyalGuard Rogueguard GraveGolem RedstoneGolem IceGolem Damned Reprobate Crusher DrownedNecromancer Haunt BoundIllager ArmoredIllager WitherNecromancer'.split(),
'itsmeow__betteranimalsplus': 'Badger BlackBear BrownBear Boar Coyote Deer FeralWolf Gazelle Moose Reindeer'.split(),
'starfish-studios__Naturalist-Archive': 'bear.geo boar.geo deer.geo elephant.geo giraffe.geo hippo.geo lion.geo rhino.geo zebra.geo'.split(),
'lender544__new1.20.1': 'Ignis_ Ignited_Revenant_ Ender_Golem_ Ender_Guardian_ Koboleton_ Draugr_ Royal_Draugr_ Elite_Draugr_ Aptrgangr_'.split(),
'AlexModGuy__AlexsCaves': 'Candicorn Corrodent DeepOneKnight Magnetron Nucleeper Relicheirus Tremorsaurus Boundroid'.split(),
'BobMowzie__MowziesMobs-Public': 'Wroughtnaut Frostmaw'.split(),
'samedifferent__Ecologics': ['Camel'],
' team-abnormals__environmental'.strip(): 'Deer Reindeer Yak Tapir'.split(),
'Quek04__The-Undergarden': 'Brute Dweller Mog SmogMog'.split(),
'Angry-Pixel__The-Betweenlands': 'DreadfulMummy TarBeast SwampHag Wight SpiritTreeFaceLarge SludgeMenace'.split(),
}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(im,w,ht):
 im=im.convert('RGBA');factor=min(w/im.width,ht/im.height);return im.resize((max(1,int(im.width*factor)),max(1,int(im.height*factor))),Image.Resampling.NEAREST)
def main():
 rows=[];excluded=[]
 for directory,wanted in PICKS.items():
  base=LIB/directory
  if not (base/'source.json').exists():continue
  meta=json.loads((base/'source.json').read_text());files=[p for p in base.rglob('*') if p.is_file()];models={p.stem:p for p in files if p.suffix=='.java' and ('Model' in p.stem)};png=[p for p in files if p.suffix=='.png' and ('/textures/entity/' in str(p) or '/textures/models/' in str(p) or '/textures/model/entity/' in str(p))];java=[p for p in files if p.suffix=='.java']
  for short in wanted:
   try:
    paths=[p for p in files if p.suffix in ('.java','.json') and h.normalized(h.name(p))==h.normalized(short) and ('/model/' in str(p) or '/models/' in str(p) or '/geo/' in str(p)) and '/armor/' not in str(p)]
    if not paths:raise ValueError('No source model')
    model=sorted(paths,key=lambda p:(p.suffix!='.json',len(str(p))))[0]
    if '/model/block/' in str(model) or '/models/block/' in str(model):raise ValueError('Block model, not a creature')
    if model.suffix=='.json':parts,warnings=h.parser.extra_formats.geo(model)
    else:parts,warnings,_=h.java_parts(model,models)
    if warnings:raise ValueError('Unsupported reconstruction: '+'; '.join(warnings[:2]))
    # Literal mesh root named 'root' shadows the parser's synthetic root.
    # Only resolve this known getRoot() -> addOrReplaceChild pattern.
    if model.suffix=='.java' and re.search(r'root\s*=\s*partdefinition\.addOrReplaceChild\("root"',model.read_text()):
     if parts.get('root',{}).get('parent')=='root':parts['root']['parent']=None
    fs,points=h.g.geometry(parts)
    if len(fs)<12:raise ValueError('Incomplete reconstruction')
    key=h.normalized(short.removesuffix('.geo').removesuffix('Old'))
    renderers=[p for p in java if 'render' in str(p).lower() and h.normalized(p.stem) in (key+'renderer',key+'render','render'+key)]
    bindings=[]
    for p in renderers+[model]:
     for literal in re.findall(r'"(textures/[^"\s]+\.png)"',p.read_text()):
      matches=[q for q in png if str(q).endswith('/'+literal)]
      if matches and not re.search(r'glow|eyes|overlay|armor',literal) or (matches and key in ['hauntedarmor','hauntedarmorstand']):bindings.extend((q,p)for q in matches)
    # Exact species atlas used only when renderer path is assembled dynamically.
    aliases={'deer':'wilddeer','boar':'wildboar','lowergoblinknight':'doublegoblin','lich':'twilightlich64','harbingercube':'apocalypse2'} if directory=='TeamTwilight__twilightforest' else {}; alias=aliases.get(key,key)
    exact=[p for p in png if h.normalized(p.stem)==alias];matches=exact or [p for p in png if h.normalized(p.stem).startswith(key) and not re.search('eyes|glow|shine|armor|overlay|baby|egg|head',p.stem,re.I)]
    override=globals().get('ATLAS_OVERRIDES',{}).get((directory,short))
    if override:
     texture=base/override[0];binding=base/override[1];binding_kind='manually inspected renderer/entity literal; one base skin only'
     if not texture.exists() or not binding.exists():raise ValueError('Missing explicit source binding or atlas')
    elif key=='hippogryph':
     texture=base/'src/main/resources/assets/iceandfire/textures/models/hippogryph/black.png';binding=renderers[0] if renderers else model;binding_kind='one named enum skin from source registry; not GUI icon'
    elif bindings:texture,binding=sorted(bindings,key=lambda q:(h.normalized(q[0].stem)!=key,len(q[0].stem)))[0];binding_kind='literal renderer/model path'
    elif matches:texture=sorted(matches,key=lambda p:(len(p.stem),str(p)))[0];binding=None;binding_kind='matching named source atlas; binding requires manual confirmation'
    else:raise ValueError('No matching original atlas')
    n=len(rows)+1;filename=f'{n:03}-{directory}-{short}.png';card=Image.new('RGB',(760,420),'#e9ebe4');d=ImageDraw.Draw(card);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
    d.text((8,5),f'{n:03} {meta["repo"].split("/")[-1]} / {short}',font=font,fill='#23312d');card.paste(h.g.render(fs,points,35,(370,320)),(0,35));im=fit(Image.open(texture),365,315);card.paste(im,(390+(365-im.width)//2,35),im)
    d.text((8,365),'Literal source anatomy + original pixel atlas; not a game screenshot',font=font,fill='#23312d');d.text((8,392),globals().get('STUDY_LABEL','Quadruped support / bone / iron / oath-cloth material study'),font=font,fill='#23312d');card.save(OUT/filename)
    rows.append(dict(number=n,identity=meta['repo']+':'+short.removesuffix('Old'),family=short.removesuffix('Old'),commit=meta['sha'],model_source=h.url(meta,base,model),texture_source=h.url(meta,base,texture),binding_source=h.url(meta,base,binding) if binding else None,binding_kind=binding_kind,model_sha256=digest(model),texture_sha256=digest(texture),card=filename,card_sha256=digest(OUT/filename),viewed=False))
   except Exception as e:excluded.append(dict(repo=meta['repo'],creature=short,reason=str(e)))
 for start in range(0,len(rows),6):
  sheet=Image.new('RGB',(1520,1290),'#e9ebe4')
  for j,row in enumerate(rows[start:start+6]):sheet.paste(Image.open(OUT/row['card']),(j%2*760,j//2*430))
  sheet.save(OUT/f'sheet-{start//6+1:02}.png')
 (OUT/'candidates.json').write_text(json.dumps(dict(items=rows,excluded=excluded,status='UNREVIEWED_CANDIDATES'),ensure_ascii=False,indent=2)+'\n')
 print('Candidates',len(rows),'excluded',len(excluded));print(json.dumps(excluded,ensure_ascii=False))
if __name__=='__main__':main()
