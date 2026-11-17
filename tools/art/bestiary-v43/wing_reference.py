"""Prepare pinned avian/winged creature model-and-texture research, not art exports.

One base creature per source; skins, poses and gender variants are not extra
references. Cards are literal source anatomy plus the matching atlas, or an
author-published textured model image. Nothing is automatically marked reviewed.
"""
from pathlib import Path
import hashlib, importlib.util, json, re, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
LIB = ROOT / 'build/creature-reference-1000'
OUT = ROOT / 'build/bestiary-v43/wing-reference'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(LIB))
spec = importlib.util.spec_from_file_location('wing_parser', ROOT / 'tools/art/bestiary-v43/research_candidates.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
font = lambda n: ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', n)

PICKS = {
 'AlexModGuy__AlexsMobs': 'BaldEagle BlueJay Crow Hummingbird Roadrunner Seagull SoulVulture Sunbird TarantulaHawk CrimsonMosquito Fly Enderiophage'.split(),
 'AlexModGuy__AlexsCaves': 'Gloomoth Subterranodon Vesper Notor'.split(),
 'TeamTwilight__twilightforest': 'Raven TinyBird Penguin MosquitoSwarm'.split(),
 'itsmeow__betteranimalsplus': 'Goose Quetzal Songbird Hoatzin Lammergeier Pheasant Turkey Butterfly Dragonfly'.split(),
 'Angry-Pixel__The-Betweenlands': 'Puffin Chiromaw ChiromawMatriarch DragonFly Firefly'.split(),
 'AlexModGuy__Ice_and_Fire': 'Cockatrice StymphalianBird'.split(),
 'samedifferent__Ecologics': ['Penguin'],
 'team-abnormals__environmental': ['Duck'],
 'team-abnormals__upgrade-aquatic': ['Goose'],
 'TeamFossilsArcheology__FossilsArcheologyRevival': ['confuciusornis.geo', 'dodo.geo', 'dimorphodon.geo', 'quetzalcoatlus.geo'],
 'peeko32213__Unusual-Prehistory': ['anuro.geo', 'pterodaustro.geo'],
 'starfish-studios__Naturalist-Archive': ['bird.geo', 'vulture.geo'],
 'DivineRPG__DivineRPG': ['Alicanto', 'JungleBat'],
 'Polarice3__Goety-2': ['CarrionFly', 'PhantomServant'],
}

def digest(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()

def fit(im, size):
 im = im.convert('RGBA')
 factor = min(size[0]/im.width, size[1]/im.height)
 return im.resize((max(1, round(im.width*factor)), max(1, round(im.height*factor))), Image.Resampling.NEAREST)

def main():
 rows, excluded = [], []
 # A family page contributes one representative image, never every species skin.
 bird_root = ROOT / 'build/bestiary-v41/research/birds'
 seen = set()
 for record in json.loads((bird_root/'candidates.json').read_text()):
  identity = record['identity']
  if identity in seen:
   continue
  seen.add(identity)
  p = bird_root/record['file']
  card = Image.new('RGB', (760, 420), '#e9ebe4'); d = ImageDraw.Draw(card)
  d.text((10, 8), 'Frikinzis Fauna / '+identity, font=font(19), fill='#23312d')
  im = fit(Image.open(p), (730, 335)); card.paste(im, ((760-im.width)//2, 38), im)
  d.text((10, 390), 'Author model + texture illustration / one family, not extra skins', font=font(14), fill='#23312d')
  filename = 'fauna-'+re.sub('[^a-z0-9]+', '-', identity.lower())+'.png'
  card.save(OUT/filename)
  rows.append(dict(identity='FrikinzisFauna:'+identity, family=identity, category='avian',
   source=record['source'], image_source=record['url'], source_image_sha256=digest(p), card=filename,
   limits='Author illustration; no claims about game scaling, renderer or rig independence.', viewed=False))
 for directory, wanted in PICKS.items():
  base = LIB/directory; meta=json.loads((base/'source.json').read_text())
  models = {p.stem:p for p in base.rglob('*.java') if p.name.endswith('Model.java') or p.name.startswith('Model')}
  for short in wanted:
   try:
    paths = [p for p in base.rglob('*') if p.is_file() and helpers.normalized(helpers.name(p)) == helpers.normalized(short) and p.suffix in ('.java', '.json') and ('/model/' in str(p) or '/geo/' in str(p))]
    if not paths:
     raise ValueError('model missing')
    path = sorted(paths, key=lambda p:(p.suffix != '.json', len(str(p))))[0]
    if path.suffix == '.json':
     parts, warnings = helpers.parser.extra_formats.geo(path)
    else:
     parts, warnings, _ = helpers.java_parts(path, models)
    if warnings:
     raise ValueError('; '.join(warnings[:3]))
    faces, points = helpers.g.geometry(parts)
    if len(faces) < 12:
     raise ValueError('incomplete geometry')
    textures = [p for p in base.rglob('*.png') if '/textures/entity/' in str(p) or '/textures/models/' in str(p)]
    key = helpers.normalized(short.removesuffix('.geo'))
    exact = [p for p in textures if helpers.normalized(p.stem) == key]
    matches = exact or [p for p in textures if helpers.normalized(p.stem).startswith(key)]
    # Hummingbird's base plumage is a numbered variant; pick one, count one.
    matches = [p for p in matches if not re.search('eyes|glow|shine|hood|hatch|egg|baby|tame|overlay|barb|lightning|petrif',p.stem,re.I)]
    if not matches:
     raise ValueError('matching original atlas missing')
    texture = sorted(matches, key=lambda p:(len(p.stem), str(p)))[0]
    card=Image.new('RGB',(760,420),'#e9ebe4');d=ImageDraw.Draw(card)
    d.text((10,8),meta['repo'].split('/')[-1]+' / '+short,font=font(19),fill='#23312d')
    card.paste(helpers.g.render(faces,points,38,(370,320)),(0,38))
    im=fit(Image.open(texture),(365,320));card.paste(im,(390+(365-im.width)//2,38),im)
    d.text((10,370),'Literal source anatomy + original atlas / no layers or animation',font=font(15),fill='#23312d')
    d.text((10,393),'Not an author gameplay screenshot; texture binding still reviewed manually',font=font(14),fill='#23312d')
    filename=directory+'-'+short+'.png';card.save(OUT/filename)
    rows.append(dict(identity=meta['repo']+':'+short,category='avian-or-winged',
     family=short,commit=meta['sha'],model_source=helpers.url(meta,base,path),texture_source=helpers.url(meta,base,texture),
     model_sha256=digest(path),texture_sha256=digest(texture),card=filename,viewed=False,
     limits='Source constructor pose and raw atlas, not a fully textured game capture; exact species binding manually checked.'))
   except Exception as e:
    excluded.append(dict(repo=meta['repo'],creature=short,reason=str(e)))
 for i,row in enumerate(rows):
  row['number']=i+1;row['card_sha256']=digest(OUT/row['card'])
 for start in range(0,len(rows),6):
  sheet=Image.new('RGB',(1520,1290),'#e9ebe4')
  for j,row in enumerate(rows[start:start+6]):
   sheet.paste(Image.open(OUT/row['card']),(j%2*760,j//2*430))
   ImageDraw.Draw(sheet).text((j%2*760+5,j//2*430+30),f'#{row["number"]:03}',font=font(16),fill='#9a342b')
  sheet.save(OUT/f'sheet-{start//6+1:02}.png')
 (OUT/'candidates.json').write_text(json.dumps(dict(items=rows,excluded=excluded,status='UNREVIEWED_CANDIDATES'),ensure_ascii=False,indent=2)+'\n')
 print('Prepared',len(rows),'distinct family/source candidates; no automatic acceptance. Excluded:',len(excluded))
 for row in excluded:print(row)

if __name__ == '__main__':
 main()
