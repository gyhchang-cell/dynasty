"""Offline QA-only javac, immutable already-frozen Forge dependencies; never runs a game/Gradle."""
from pathlib import Path
import hashlib,json,subprocess,shutil,datetime
B=Path(__file__).resolve().parent; R=B.parents[2]; O=R/'docs/cod4/audit-20261022/sweep-native-acceptance'
W=B/'.work'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'); W.mkdir(parents=True,exist_ok=False)
old=R/'tools/cod4/sweep-receipt-research/.work/receipt-fix/native-compile'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
for p in sorted((B/'src').rglob('*.java')):
 q=W/'frozen'/p.relative_to(B/'src');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);inputs[str(p.relative_to(R))]=sha(q)
cp=[old/'classes',old/'baseline']+sorted((old/'dependency-cache').glob('*.jar'))
assert cp[2].name.startswith('0000-') and len(cp)>800
classes=W/'classes';classes.mkdir();empty=W/'empty';empty.mkdir()
cmd=['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javac','-J-Djava.awt.headless=true','--release','17','-proc:none','-encoding','UTF-8','-sourcepath',str(empty),'-classpath',':'.join(map(str,cp)),'-d',str(classes)]+list(map(str,sorted((W/'frozen').rglob('*.java'))))
(W/'command.json').write_text(json.dumps(cmd,indent=2));run=subprocess.run(cmd,capture_output=True,text=True);(W/'compile.log').write_text(run.stdout+run.stderr)
receipt=dict(status='PASS' if run.returncode==0 else 'FAIL',exit_code=run.returncode,sources=inputs,classes={str(p.relative_to(classes)):sha(p) for p in sorted(classes.rglob('*.class'))},classpath_origin=str(old.relative_to(R)),classpath_snapshot_manifest='docs/cod4/audit-20261022/sweep-receipt-research/offline-compile-receipt.json',work=str(W.relative_to(R)),game_started=False,native_C2S_run=False,mixin_runtime_validated=False,reobfuscated=False,scope='QA source javac only; not native acceptance or deployable SRG validation')
O.mkdir(parents=True,exist_ok=True);(W/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(O/'offline-compile02.json').write_text(json.dumps(receipt,indent=2)+'\n');print(run.stdout+run.stderr);print(json.dumps({k:v for k,v in receipt.items() if k not in ['sources','classes']}));raise SystemExit(run.returncode)
