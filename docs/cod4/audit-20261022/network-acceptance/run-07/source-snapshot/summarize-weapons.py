"""Summarize actual weapon/broadcast evidence; partial runs remain partial."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[3]
D=R/'docs/cod4/audit-20261022/network-acceptance'/sys.argv[1]
def read(p):return json.loads(p.read_text())
rows=[]
for n in range(20):
 p=D/f'weapon-result-{n}.json'
 if not p.exists():continue
 s=read(p); row={'case':n,'kind':s['kind'],'server':True,'checks':s['checks'],'clients':{}}
 for role in ['host','peer']:
  q=D/f'{role}-weapon-{n}.json'
  if q.exists():
   c=read(q);e=c['evidence'];row['clients'][role]={'afterLevel': 'AFTER_LEVEL' in c['captureEvent'],'cameraTypeFovEntityUnchanged':e['cameraBefore']==e['cameraAfter'],'actualVfxPackets':sum(x.get('kind')=='vfx-wire' for x in e['events']),'genericFeedbackCalls':sum(x.get('kind')=='feedback-client' for x in e['events']),'screenshot':(D/f'{role}-weapon-{n}.png').exists()}
 rows.append(row)
complete=[r for r in rows if len(r['clients'])==2 and all(all(c[k] for k in ['afterLevel','cameraTypeFovEntityUnchanged','screenshot']) for c in r['clients'].values())]
fail={p.name:p.read_text() for p in D.glob('*FAIL*')}
passes={r:(D/f'{r}-PASS').exists() for r in ['server','host','peer']}
index={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.iterdir()) if p.is_file() and p.name not in ['result-weapons.json','evidence-sha256.json']}
result={'run':D.name,'suite':'native C2S weapons / original S2C broadcast','passed':len(complete)==20 and all(passes.values()) and not fail,'completedCases':len(complete),'plannedCases':20,'markers':passes,'failures':fail,'connections':read(D/'connections.json') if (D/'connections.json').exists() else None,'stableJarSha256':'ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b','cases':rows,'limits':['Four mod QA integration, not full production pack or two human players. Gear/ammo/dummies/collision blocks are supplied fixtures.','Camera assertion covers perspective/FOV/camera entity; intentional actor aiming changes yaw/pitch, no claim all raw rotation values fixed.','Wire-handler receipt plus AFTER_LEVEL frame does not prove artistic quality, every particle or original holding/model animation.','First crossbow projectile can fire on initial native loading release; see crossbow-native-release-observation.json. No separate persistence-until-second-input assertion.','Full survival acquisition, all combat sources, cooldown expiry timing and all four detailed visual rows remain outside this acceptance.']}
(D/'result-weapons.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(D/'evidence-sha256.json').write_text(json.dumps(index,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['run','passed','completedCases','plannedCases','markers','failures']},ensure_ascii=False,indent=2))
