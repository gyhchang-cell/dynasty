"""Run actual production geometry on the isolated compiled classpath, no GLFW."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'build/maintenance/flute-wave-v1'
launch=json.loads((ROOT/'build/maintenance/secondary-materials-v2/launch.json').read_text())
java=Path(launch['executable']);cp=str(BASE/'gradle/classes/java/main')+':'+launch['classpath']
folder=BASE/'checks';folder.mkdir(exist_ok=True)
log=[]
for command in [[str(java.with_name('javac')),'-cp',cp,'-d',str(folder),str(ROOT/'tools/art/flute-wave/FluteCheck.java')],
                [str(java),'-Djava.awt.headless=true','-cp',str(folder)+':'+cp,'FluteCheck',str(ROOT/'docs/art/flute-wave-v1/actual-triangles.json')]]:
    result=subprocess.run(command,capture_output=True,text=True);log.append(result.stdout+result.stderr)
    if result.returncode:
        print(log[-1]);(BASE/'geometry.log').write_text('\n'.join(log));raise SystemExit(result.returncode)
print(log[-1]);(BASE/'geometry.log').write_text('\n'.join(log))
