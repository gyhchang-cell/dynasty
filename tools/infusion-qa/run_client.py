#!/usr/bin/env python3
"""Launch exported Forge clients without holding Gradle's shared cache locks."""
import json,os,subprocess,sys,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2]
role=sys.argv[1] if len(sys.argv)>1 else 'host'
assert role in ('host','peer','restart')
data=json.loads((root/'build/infusion-client/launch-host.json').read_text())
command=[data['executable'] or shutil.which('java')]+data['jvmArgs']+['-cp',data['classpath'],data['main']]+data['args'];cwd=Path(data['cwd'])
if role=='peer':
 command=[arg.replace('dynasty.infusionQa=host','dynasty.infusionQa=peer').replace('InfusionHost','InfusionPeer') for arg in command]
 cwd=cwd.parent/'peer'
if role=='restart':command=[arg.replace('dynasty.infusionQa.resume=false','dynasty.infusionQa.resume=true') for arg in command]
cwd.mkdir(parents=True,exist_ok=True)
env=os.environ.copy()
env.update(data['environment'])
result=subprocess.run(command,cwd=cwd,env=env)
sys.exit(result.returncode)
