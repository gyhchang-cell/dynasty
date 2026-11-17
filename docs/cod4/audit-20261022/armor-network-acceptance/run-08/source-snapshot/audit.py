"""Strict offline receipt audit of original server and two rendered real-client captures."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3]
D=R/'docs/cod4/audit-20261022/armor-network-acceptance'/sys.argv[1]
read=lambda p:json.loads(p.read_text())
rows=[]
for p in sorted(D.glob('case-result-*.json'),key=lambda p:int(p.stem.rsplit('-',1)[1])):
 x=read(p);n=x['case'];checks=list(x['checks']);peer=x['afterUnequip']['uuid']
 for role in ['host','peer']:
  q=D/f'{role}-case-{n}.json';e=D/f'{role}-equipped-frame-{n}.json'
  checks.append({'name':role+' actual AFTER_LEVEL completion','passed':q.exists() and 'AFTER_LEVEL' in read(q).get('captureEvent','')})
  if q.exists():
   z=read(q)['evidence'];entities={v['uuid']:v for v in z['trackedPlayers']}
   checks.append({'name':role+' tracks both actual players','passed':len(entities)==2 and peer in entities})
   if peer in entities:checks.append({'name':role+' replicated final equipment matches server','passed':entities[peer]['gear']==x['afterUnequip']['gear']})
   if role=='peer':
    own=z['own'];server=x['afterUnequip']
    checks.append({'name':'owner native effect ids/amplifiers match server','passed':{k:v['amp'] for k,v in own['effects'].items()}=={k:v['amp'] for k,v in server['effects'].items()}})
    diffs={k:[v['value'],own['attributes'].get(k,{}).get('value')] for k,v in server['attributes'].items() if v.get('syncable',k in ['minecraft:generic.max_health','minecraft:generic.movement_speed','minecraft:generic.armor','minecraft:generic.luck']) and k in own['attributes'] and abs(v['value']-own['attributes'][k]['value'])>.01}
    checks.append({'name':'owner synchronized native attributes match server','passed':not diffs,'differences':diffs})
  worn=False
  if e.exists():
   for v in read(e)['trackedPlayers']:
    if v['uuid']==peer:
     worn=sum(v['gear'][sl]==f"dynasty:{x['set']}_{su}" for sl,su in [('HEAD','helmet'),('CHEST','chestplate'),('LEGS','leggings'),('FEET','boots')])==x['pieces']
  checks.append({'name':role+' actual rendered equipped threshold','passed':worn})
 rows.append({'case':n,'set':x['set'],'pieces':x['pieces'],'passed':all(c['passed'] for c in checks),'checks':checks})
out={'run':sys.argv[1],'uniqueDenominator':len(rows),'passed':sum(x['passed'] for x in rows),'rows':rows,'attributePolicy':'Compare only native Attribute.isClientSyncable(): max_health, movement_speed, armor, luck. Native attack_damage and knockback_resistance are server-only; local bytecode saved as native-attributes-bytecode.txt. Server actual hurt remains authoritative for attack bonus.', 'remoteVanillaEffectsPolicy':'Full remote-player vanilla effects are not broadcast by vanilla. Only owner full effect list compared; remote equipment uses real tracked entities. No synthetic effect-list parity required.','scope':'Four jars, two real automated network clients, supplied QA gear/environment, not two human survival players or full modpack. Fixture-triggered native hurt explicitly identified per case; not all triggers are C2S.','productionSha256':read(D/'host-manifest.json')['unified_artifact_sha256']}
(D/'audit-network.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'uniqueDenominator':len(rows),'passed':out['passed'],'failed':[(x['case'],[c['name'] for c in x['checks'] if not c['passed']]) for x in rows if not x['passed']]},ensure_ascii=False))
