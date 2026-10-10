"""Check actual native states and measured baked-bone poses, not QA triggers."""
import argparse,hashlib,json,math
from pathlib import Path
from build_models import ASSET,REPO
from rig_bounds import vertices

def verify_run(run):
 root=REPO/'docs/art/secondary-cuboid-v1/native'/run
 assert (root/'PASS.txt').read_text().splitlines()[-1].startswith('PASS:')
 runtime=json.loads((root/'runtime-manifest.json').read_text());resources={e['path']:e['sha256'] for e in runtime['trees'][0]['files']}
 assert hashlib.sha256((REPO/'build/libs/dynasty-1.4.0.jar').read_bytes()).hexdigest()==runtime['production']['jarSha256'],'stale production build'
 for path,digest in runtime['production']['sources'].items():assert hashlib.sha256((REPO/path).read_bytes()).hexdigest()==digest,'stale production source'
 results={}
 for path in sorted(root.glob('*-state.json')):
  d=json.loads(path.read_text());id=d['entity'];slot=d['stage']%7
  if slot>0:assert d['serverAction']['accepted'] and 'art_check' not in d['scope']
  expected='idle' if slot==0 else 'attack' if slot==1 else 'hurt' if slot==2 else 'death'
  assert d['clip']==expected,(path,'state mismatch')
  if slot==1:assert d['swinging'] and d['health']==d['serverAction']['healthBefore']
  if slot==2:assert d['hurtTime']>0 and 0<d['serverAction']['healthAfter']<d['serverAction']['healthBefore']
  if slot in (1,2):assert d['observedMotion']['deltaRadians']>=.008 and d['clientTick']>=d['observedMotion']['firstEventClientTick']+3,'no measured articulated motion'
  entry=results.setdefault(id,{'stages':0,'deathViews':[],'nativeRigMinimumBlocks':[],'nativeMainBodyMinimumBlocks':[]})
  entry['stages']+=1
  for suffix in [f'geo/boss_cuboid/{id}.geo.json',f'animations/boss_cuboid/{id}.animation.json',f'textures/entity/boss_cuboid/{id}.png']:
   assert hashlib.sha256((ASSET/suffix).read_bytes()).hexdigest()==resources['assets/dynasty/'+suffix],(id,'stale resource')
  if slot<3:continue
  assert d['isDeadOrDying'] and d['health']==0 and d['deathTime']>=18
  bones=json.loads((ASSET/f'geo/boss_cuboid/{id}.geo.json').read_text())['minecraft:geometry'][0]['bones'];channels={}
  for b in bones:
   pose=d['runtimeBones'][b['name']];rot=[math.degrees(v)*s for v,s in zip(pose['rotationRadians'],[-1,-1,1])]
   channels[b['name']]={'rotation':[rot[i]-b.get('rotation',[0,0,0])[i] for i in range(3)],'position':pose['positionUnits']}
  scale=1.4 if id=='dragon_emperor' else 1
  low=min(v[1] for v in vertices(bones,channels,0))/16*scale
  main=[dict(b,cubes=b.get('cubes',[]) if not any(k in b['name'] for k in ['storm_ring','thunder_blade','thunder_drum','storm_wedge']) else []) for b in bones]
  body_low=min(v[1] for v in vertices(main,channels,0))/16*scale
  # Include floating-point/transition tolerance below one model unit.
  assert -.025<=low<=.04,(id,d['viewOrClip'],'rig not grounded',low)
  assert -.025<=body_low<=.04,(id,'main body floating above its decoration',body_low)
  entry['deathViews'].append(d['viewOrClip']);entry['nativeRigMinimumBlocks'].append(low);entry['nativeMainBodyMinimumBlocks'].append(body_low)
 for id,entry in results.items():
  assert entry['stages']==7 and set(entry['deathViews'])=={'front','45','side','back'},id
  entry['scope']='Actual server swing/generic hurt/lethal hurt replicated to silent native client. NoAI scene; natural skills, human gameplay and collision/damage coverage remain separate.'
 return runtime['production'],results

def main():
 p=argparse.ArgumentParser();p.add_argument('runs',nargs='+');args=p.parse_args();results={};accepted={};production=None
 for run in args.runs:
  prod,entities=verify_run(run)
  if production is not None:assert production==prod,'mixed production builds'
  production=prod;results.update(entities);accepted.update({id:run for id in entities})
 out=REPO/'docs/art/cod6-cuboid-v1/lifecycle-validation.json';out.write_text(json.dumps({'acceptedRuns':accepted,'production':production,'entities':results},indent=2)+'\n')
 print('PASS measured native lifecycle:',len(results),'bosses /',sum(v['stages'] for v in results.values()),'stages; full rig and main body grounded')

if __name__=='__main__':main()
