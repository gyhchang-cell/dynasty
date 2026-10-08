"""Build the reviewed cod3 catalogue from the supplied implementation specification.
The source is optional: the checked-in catalogue is the runtime resource, not a build dependency.
"""
import json,re,sys
from pathlib import Path
source=Path(sys.argv[1]).read_text()
def sections(start,end):
 part=source[source.index(start):source.index(end)]
 return [(int(a),b,c) for a,b,c in re.findall(r'### (\d+) ([^\n]+)\n(.*?)(?=\n### |\n## |\Z)',part,re.S)]
intros=[]
for i,title,body in sections('## 1.2','## 1.3'):
 duration=int(re.search(r'(\d+)tick',title).group(1)) if 'tick' in title else int(re.search(r'(\d+)s',title).group(1))*20
 times=sorted(set(int(x) for x in re.findall(r'(\d+)-\d+tick',body)))
 intros.append(dict(id=f'intro_{i:02}',name=title.split('（')[0].strip(),totalTicks=duration,arenaTag='dynasty:cod3/arena',bossIds=[],steps=[dict(startTick=t,duration=min(60,duration-t),type='SPAWN_CLIENT_VFX',vfx=[8,27,16,13,7,35,30,24,40,10,15,14,13,9,23,5,39,29,33,28][i-1],radius=3+((j+i)%4),detail=body) for j,t in enumerate(times)]))
bindings={'dragon_emperor':8,'rebel_general':18,'eunuch_mastermind':3,'undead_first_emperor':4,'nine_heaven_general':8,'dragon_king':5}
for boss,i in bindings.items():intros[i-1]['bossIds'].append('dynasty:'+boss)
deaths=[]
for i,title,body in sections('## 2.2','## 2.3'):
 duration=int(re.search(r'(\d+)tick|=(\d+)t',title).group(1) or re.search(r'(\d+)tick|=(\d+)t',title).group(2)) if re.search(r'(\d+)tick|=(\d+)t',title) else int(re.search(r'(\d+)s',title).group(1))*20
 deaths.append(dict(id=f'death_{i:02}',name=title.split('（')[0].strip(),totalTicks=duration,arenaTag='dynasty:cod3/arena',bossIds=[],steps=[dict(startTick=t,duration=40,type='SPAWN_CLIENT_VFX',vfx=[8,10,5,29,15,40,30,19,27,17,37,21,28,26,14,7,6,9,33,24][i-1],radius=2+j,detail=body) for j,t in enumerate([0,duration//3,2*duration//3])]))
for boss,i in {'dragon_emperor':10,'rebel_general':4,'eunuch_mastermind':8,'undead_first_emperor':13,'nine_heaven_general':17,'dragon_king':16}.items():deaths[i-1]['bossIds'].append('dynasty:'+boss)
vfx=[]
# Reviewed values from table 3.2. A lifecycle string such as radius0→8 is an
# animation, not a zero-radius definition; do not infer geometry from its first number.
radii=[.5,8,.25,.2,2.5,1,6,6,3,1,5,8,.6,1.5,6,4,.8,3,9,10,8,1,3,1,5,12,3,.75,2,8,1,5,10,1,3,6,6,3,4,12]
lengths=[12,8,16,4,6,20,1.5,2,12,10,10,1,6,3,1,8,20,6,1,1,12,8,5,10,.5,1,4,24,6,12,3,10,10,15,2,1,3,6,12,1]
shapes=['LINE','CONE','LINE','LINE','BOX','TARGET_LOCK','ANNULUS','ANNULUS','BOX','LINE','SPHERE','CIRCLE','CHAIN','SPHERE','CIRCLE','BOX','CHAIN','LINE','CONE','CIRCLE','CIRCLE','BOX','LINE','CHAIN','CIRCLE','ANNULUS','BOX','LINE','CONE','CIRCLE','CHAIN','SPHERE','SPHERE','LINE','ANNULUS','CONE','RECT','RECT','SPHERE','CIRCLE']
for a,title,body in re.findall(r'### VFX-(\d+) ([^\n]+)\n(.*?)(?=\n### |\n=|\Z)',source[source.index('## 3.3'):source.index('COD3-4')],re.S):
 i=int(a);colors=re.findall(r'0x([0-9A-Fa-f]{6})',body);end=re.search(r'END (\d+)t',body);radius=re.search(r'(?:radius|半径|\br)(\d+(?:\.\d+)?)',body);lod=re.search(r'LOD (\d+)/(\d+)/(\d+)',body)
 vfx.append(dict(id=i,name=title,shape=shapes[i-1],duration=int(end.group(1)) if end else 26 if i==4 else 30,radius=radii[i-1],length=lengths[i-1],width={3:.3,24:2,28:.75,31:.1}.get(i,.6),color=int(colors[0],16) if colors else 0xB5E0C9,near=int(lod.group(1)) if lod else 60,medium=int(lod.group(2)) if lod else 24,far=int(lod.group(3)) if lod else 6,details=body.strip()))
def table(start,end,min_cols):
 part=source[source.index(start):source.index(end)]
 out=[]
 for line in part.splitlines():
  if not re.match(r'\| \d',line):continue
  c=[x.strip() for x in line.strip('|').split('|')]
  if len(c)>=min_cols:out.append(c)
 return out
npc_ids=['lao_chen','han_chong','qingxuanzi','baibao_jin','a_ji','hei_po','cao_chengfu','hong_ling','chu_nongyu','xiaoyuanzi','mo_jizi','sai_banxian','ba_tu','yan_chifeng','huang_laohan']
npcs=[]
for i,c in enumerate(table('## 8.1','## 8.2',5)):
 npcs.append(dict(id=npc_ids[i],name=re.sub(r'^\d+ ','',c[0]),model=c[1],costume=c[2],work=c[3],special=c[4],home=['travel_site','great_wall_gate','travel_site','travel_site','travel_site','travel_site','imperial_tomb','travel_site','music_ruin','travel_site','seal_vault','travel_site','travel_site','stone_grove','travel_site'][i]))
for i,c in enumerate(table('## 8.3','COD3-9',7)):
 npcs[i].update(first=c[3].strip('「」'),ordinary=c[4].strip('「」'),reaction=c[5],changed=c[6])
secrets=[]
for c in table('## 9.1','## 9.2',10):
 i=int(c[0]);secrets.append(dict(id=f'secret_{i:02}',name=c[1],visual=c[2],environment=c[3],sound=c[4],falseClue=c[5],condition=c[6],scope='WORLD' if c[7]=='世界级' else 'PLAYER',reward=c[8],oneTime=c[9]=='一次'))
scenic=[]
for c in table('## 10.1','## 10.2',11):
 i=int(re.search(r'\d+',c[0]).group());scenic.append(dict(id=f'scenic_{i:02}',name=c[1],region=c[2],time=c[3],weather=c[4],duration=(int(re.search(r'\d+',c[5]).group())*20 if re.search(r'\d+',c[5]) else 1200),distance=c[6],lod=c[7],sound=c[8],budget=int(re.search(r'\d+',c[9]).group()) if re.search(r'\d+',c[9]) else 0))
# Table actually has ten cells after the leading index; accept that shape too.
if not scenic:
 for c in table('## 10.1','## 10.2',10):
  i=int(re.search(r'\d+',c[0]).group());scenic.append(dict(id=f'scenic_{i:02}',name=c[1],region=c[2],time=c[3],weather=c[4],duration=(int(re.search(r'\d+',c[5]).group())*20 if re.search(r'\d+',c[5]) else 1200),distance=c[6],lod=c[7],sound=c[8],budget=int(re.search(r'\d+',c[9]).group()) if re.search(r'\d+',c[9]) else 0))
world=[]
for i,c in enumerate(table('## 11.1','## 11.2',9)):world.append(dict(id=f'world_{i+1:02}',name=re.sub(r'^\d+ ','',c[0]),sky=c[1],fog=c[2],ambience=c[3],npc=c[4],particles=c[5],decoration=c[6],merchants=c[7],animals=c[8]))
result=dict(intros=intros,deaths=deaths,vfx=vfx,npcs=npcs,secrets=secrets,scenic=scenic,worldStates=world)
assert [len(result[k]) for k in result]==[20,20,40,15,30,25,10],[(k,len(v)) for k,v in result.items()]
Path('src/main/resources/data/dynasty/cod3/catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print({k:len(v) for k,v in result.items()})
