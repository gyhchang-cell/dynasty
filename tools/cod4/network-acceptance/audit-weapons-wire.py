"""Independently cross-check original server source and real network arrival logs."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/network-acceptance'/sys.argv[1]
logs={r:[json.loads(s) for s in (D/f'{r}-wire.jsonl').read_text().splitlines()] for r in ['host','peer']}
server=logs['host'];checks=[];failures=[];boundary=[];overlap=[]
for p in sorted(D.glob('weapon-result-*.json'),key=lambda p:int(p.stem.split('-')[-1])):
 s=json.loads(p.read_text());n=s['case'];k=s['kind'];source=[x for x in server if x['case']==n and x['kind']=='weapon-server-source'];stops=[x for x in server if x['case']==n and x['kind']=='native-stop-server'];damage=[x for x in server if x['case']==n and x['kind']=='damage-server' and x['owner']!='none']
 for role in ['host','peer']:
  cp=D/f'{role}-weapon-{n}.json'
  if not cp.exists():failures.append(f'{n}/{role} missing rendered capture');continue
  c=json.loads(cp.read_text())['evidence'];rot=c.get('rotation')
  if rot and rot['afterIntentionalAim']!=rot['after']:failures.append(f'{n}/{role} rotation changed')
  for e in s['expectedWeaponPackets']:
   if e['role']!=role:continue
   w=[x for x in logs[role] if x['case']==n and x['kind']=='vfx-wire' and x['sequence']==e['sequence'] and x['entity']==e['entity'] and x['start']==e['start']]
   src=[x for x in source if x['entity']==e['entity'] and x['gameTick']==e['start'] and 'equipment_weapon_'+x['cue']==e['sequence']]
   if bool(w)!=e['receive'] or len(w)>1 or len(src)!=1:failures.append(f'{n}/{role} native cue routing mismatch')
   for x in w:
    if x['nano']<src[0]['nano']:failures.append(f'{n}/{role} arrived before source')
   if k in ['rope31','rope32','rope33','rope_far','rope_return'] and role=='host':boundary.append({'case':n,'kind':k,'distanceSqr':e['distanceSqr'],'received':len(w),'remoteActorTracked':e['owner'] in c.get('trackedPlayers',[])})
 if k in ['meteor_full','meteor_overlap']:
  release=[x for x in source if x['cue']=='meteor_hammer']
  if not release or not stops or not damage:failures.append(f'{n} missing native release/damage')
  for cue in release:
   same=[x for x in stops if x['owner']==cue['owner'] and x['gameTick']==cue['gameTick']]
   if not same or same[0]['nano']>cue['nano']:failures.append(f'{n} release cue before native stop')
  if k=='meteor_overlap':overlap=[{'owner':x['owner'],'entity':x['entity'],'gameTick':x['gameTick']} for x in release]
 checks.append({'case':n,'kind':k,'sourceCues':len(source),'nativeStop':len(stops),'acceptedActorDamageEvents':len(damage)})
out={'passed':not failures and len(checks)==20,'checkedServerCases':len(checks),'failures':failures,'checks':checks,'boundaryAndTracking':boundary,'overlapReleaseActors':overlap,'scope':'Actual original source -> native network packet handler, timing/owner routing, rendered acknowledgement; no direct handler invocation. Monotonic nano comparison is same-machine only.'}
(D/'wire-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','checkedServerCases','failures','boundaryAndTracking','overlapReleaseActors']},ensure_ascii=False,indent=2))
