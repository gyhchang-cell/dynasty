import subprocess,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'.build/candidates/sword-review-20261109'
fixture=root/'.build/candidates/cline-audit-20261104/combat-fixture.json'
cases=['duel-release1100-stationary','duel-release1100-continuous-aim','duel-moving-target','duel-falling-critical','damage-jump-response-valid']
common=[root/'Sources'/f'{n}.swift' for n in ['F3Model','Sprint','Anchor']]
for name,combat in [('before',out/'baseline/Combat.swift'),('after',root/'Sources/Combat.swift')]:
 exe=out/('replay-'+name)
 subprocess.run(['swiftc','-sdk','/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk','-swift-version','5',*map(str,common),str(combat),str(root/'Tests/CombatReplay/main.swift'),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe),str(fixture),*[str(root/'research/combat-20261102'/(n+'.json')) for n in cases]],check=True,text=True,capture_output=True)
 (out/('replay-'+name+'.json')).write_text(r.stdout)
a=json.loads((out/'replay-before.json').read_text());b=json.loads((out/'replay-after.json').read_text());result=[]
for old,new in zip(a,b):
 identical=old==new
 summary={'case':Path(old['file']).stem,'samples':new['samples'],'identical_decisions':identical,'before_attack_ticks':[e['tick'] for e in old['events'] if e['event'].startswith('ATTACK ')],'after_attack_ticks':[e['tick'] for e in new['events'] if e['event'].startswith('ATTACK ')]}
 result.append(summary);print(summary)
(out/'replay-comparison.json').write_text(json.dumps({'open_loop_only':True,'inventory_assumption':'diamond sword selected; fixture hotbar/keys; empty cells','not_live_hits_or_damage':True,'results':result},indent=2))
