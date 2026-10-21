from pathlib import Path
import json,hashlib,subprocess,concurrent.futures
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[3]
slugs='epic-samurais ec-es-compat samurai wizard-samurai-irons-spells-addon cherry-samurai-temple jinkaizenns-samurais nebulus-evil-samurai-battletower-for-the-cherry-grove power-rangers-samurai warrior_helmet sengoku-legends samurai-cit caving-samurai knights epic-knights-shields-armor-and-weapons death-knights death-knights-balacing-datapack-for-prominence-ii-rpg death-knights-rpg-series-pt-br-translation-unofficial epic-knightsnmages amnes-death-knights-rpg-series-spanish-translations epic-knights-addon epic-knights-antique-legacy epic-knights-slavic-armory knights-and-castles ranged-knights-medieval-boomsticks-and-sharpsticks tiny-skeletons fresh-skeleton-physics als-skeletons-revamped-x-fresh-animations skeleton-ai-fix als-skeletons-revamped-classic-faces skeleton-horse-spawn mutant-skeleton-armor-tweaks als-skeletons-revamped wither-skeleton-tweaks wither-skeleton-propagation skeleton-physics armorable-skeleton-horses undead-nights the-undead-revamped undead-unleashed zoniex undead-leather the-lunar-undead undeadpandemic tdw-ur beundead gm4-undead-players undead-horse-variants undead-armies warriors rogues-and-warriors lne-rogues roguez-and-warriorz mc-warriors-3-plugin mc-warriors-1 warriorsplits wizards-and-warriors2 e-w warriors-of-past-epoch-iron-recipes-addon these-cats-are-warriors rock-solid-warriors blasting-clay-and-clay-balls purpurpacks-re-dye-terracotta os-vibrant-retextured-glazed-terracotta guts purpurpacks-re-dye-glazed-terracotta decorative-terracotta-lattices terracotta-shingles terracotta-knights accurate-terracotta-colors waffles-terracotta-plaster terracotta-titlescreen connected-teracotta-dungeons mischief-illagers drodis-illagers-fresh-animation drodis-illagers human-era-villagers-illagers glowing-illagers illagers-wear-armor melodysillagers illagers-plus pirate-illagers axolotl-illagers fantasy-illagers mc-dungeons-illagers ukus-armor-hud immersive-armors azurelib-armor detail-armor-bar-reconstructed visual-armor-trims detail-armor-bar armor-statues armor-chroma-for-fabric cosmetic-armor more-armor-trims mcda armor-stand-arms terracotta-knights guard-villagers villager-recruits clay-soldiers human-companions epic-knights-armor-and-weapons born-in-chaos irons-spells-n-spellbooks mowzies-mobs cataclysm goety ice-and-fire-dragons minecraft-comes-alive-reborn mutant-monsters illager-invasion illage-and-spillage savage-and-ravage friends-and-foes simply-swords better-combat knights-and-mages royal-variations illager-wear-armor recruits small-ships the-graveyard undead-unleashed enemy-expansion adventurez graveyard bosses-of-mass-destruction dungeons-mobs dungeons-gear epic-samurai-mod samurai-dynasty samurai-gear'.split()
def get(slug):
 p=P/f'project-{slug}.json'
 if not p.exists():
  q=subprocess.run(['curl','-fLsS','--max-time','20','-H','User-Agent: Dynasty-art-study/1.0',f'https://api.modrinth.com/v2/project/{slug}'],capture_output=True)
  if q.returncode==0:p.write_bytes(q.stdout)
 try:return slug,json.loads(p.read_text())
 except:return slug,None
projects=dict((s,p) for s,p in concurrent.futures.ThreadPoolExecutor(8).map(get,slugs) if p)
(P/'projects.json').write_text(json.dumps(projects,ensure_ascii=False,indent=2))
prior=set();sources=[]
for p in (R/'docs/art').glob('cod3-*/references/*.json'):
 if 'ghost-army' in str(p):continue
 try:d=json.loads(p.read_text())
 except:continue
 def scan(v):
  if isinstance(v,dict):
   if isinstance(v.get('sha256'),str) and len(v['sha256'])==64:prior.add(v['sha256'])
   for a in v.values():scan(a)
  elif isinstance(v,list):
   for a in v:scan(a)
 scan(d);sources.append(str(p.relative_to(R)))
for p in (R/'docs/art').glob('cod3-*/references.json'):
 try:
  d=json.loads(p.read_text());scan(d);sources.append(str(p.relative_to(R)))
 except:pass
rows=[];urls=set()
wanted=set('terracotta-knights guard-villagers villager-recruits clay-soldiers goety wizard-samurai-irons-spells-addon samurai sengoku-legends epic-knights-shields-armor-and-weapons epic-knights-antique-legacy epic-knights-addon immersive-armors samurai-cit epic-samurais the-undead-revamped mc-dungeons-illagers drodis-illagers drodis-illagers-fresh-animation human-era-villagers-illagers undead-armies fantasy-illagers rock-solid-warriors ranged-knights-medieval-boomsticks-and-sharpsticks knights-and-castles the-graveyard'.split())
for s,p in projects.items():
 if s not in wanted:continue
 for g in p.get('gallery',[]):
  if g['url'] in urls:continue
  urls.add(g['url']);rows.append({'number':len(rows)+1,'slug':s,'title':g.get('title'),'description':g.get('description'),'page':f'https://modrinth.com/mod/{s}/gallery','url':g['url']})
def fetch(r):
 p=P/("image-"+hashlib.sha256(r["url"].encode()).hexdigest()[:20]+".img");r["file"]=p.name
 if not p.exists():subprocess.run(['curl','-fLsS','--max-time','25','-o',str(p),r['url']],capture_output=True)
 try:
  with Image.open(p) as im:r['dimensions']=im.size
  r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();r['prior_overlap']=r['sha256'] in prior
 except:r['error']='image unavailable'
 return r
rows=list(concurrent.futures.ThreadPoolExecutor(8).map(fetch,rows));(P/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(P/'prior-manifests.json').write_text(json.dumps({'sources':sources,'unique_sha256':len(prior),'hashes':sorted(prior)},indent=2))
valid=[r for r in rows if not r.get('error') and not r['prior_overlap']]
for i in range(0,len(valid),12):
 sheet=Image.new('RGB',(1800,1200),(28,30,32));d=ImageDraw.Draw(sheet)
 for j,r in enumerate(valid[i:i+12]):
  x=j%3*600;y=j//3*300;im=Image.open(P/r['file']).convert('RGB');im.thumbnail((594,264));sheet.paste(im,(x,y));d.text((x+3,y+267),f"{r['number']:03} {r['slug']}",fill='white');d.text((x+3,y+283),str(r['title'])[:70],fill='white')
 sheet.save(P/f'sheet-{i//12+1:02}.jpg',quality=94)
print('projects',len(projects),'all images',len(rows),'new nonoverlap',len(valid));print([(s,len(p.get('gallery',[]))) for s,p in projects.items()])
