from pathlib import Path
import subprocess,json
R=Path('/Users/a15356015027/Desktop/dynasty');O=R/'docs/maintenance/storage-cleanup-20261116/remaining-review'
needles=['packaging-20261030/snapshot/build/reobfJar/output.jar','packaging-20261030/snapshot/build/resources','snapshot/build/reobfJar/output.jar','snapshot/build/resources/main']
args=['rg','-n','--hidden','-F','-g','!.git/**','-g','!docs/maintenance/**','-g','!**/node_modules/**','-g','!**/gradle-home*/**','-g','!**/caches/**','-g','!**/sources/**','-g','!**/snapshot/src/**','-g','!**/runtime/**','-g','!**/frozen/**','-g','*.json','-g','*.py','-g','*.md','-g','*.txt','-g','*.log','-g','*.sh','-g','*.gradle']
for n in needles:args+=['-e',n]
args+=['docs','tools','src','build','build.gradle','settings.gradle','gradle.properties']
p=subprocess.run(args,cwd=R,capture_output=True,text=True);assert p.returncode in [0,1],p.stderr
(O/'做建模的-reference-check.json').write_text(json.dumps(dict(command=args,returncode=p.returncode,matches=p.stdout.splitlines(),stderr=p.stderr,scope='Project text references excluding Git, maintenance reports, raw source caches and frozen/runtime payload content; existing evidence and scripts included.'),ensure_ascii=False,indent=2)+'\n');print('reference_matches',len(p.stdout.splitlines()))
