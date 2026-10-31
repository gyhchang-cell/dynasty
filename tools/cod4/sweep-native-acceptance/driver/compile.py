"""Compile only the new opt-in driver against frozen real Forge and QA02 classes. Never launches."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
B=Path(__file__).resolve().parent;R=B.parents[3];O=R/'docs/cod4/audit-20261022/sweep-native-acceptance/driver'
W=B/'.work'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');W.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((O.parent/'offline-compile02.json').read_text());Q=R/qa['work']/'classes';old=R/'tools/cod4/sweep-receipt-research/.work/receipt-fix/native-compile'
assert all(sha(Q/p)==h for p,h in qa['classes'].items())
src=B/'src/com/dynasty/sweepdriver/SweepStageDriver.java';frozen=W/'frozen/com/dynasty/sweepdriver/SweepStageDriver.java';frozen.parent.mkdir(parents=True);shutil.copy2(src,frozen)
cp=[Q,old/'classes',old/'baseline']+sorted((old/'dependency-cache').glob('*.jar'))
classes=W/'classes';classes.mkdir();empty=W/'empty';empty.mkdir()
cmd=['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javac','-J-Djava.awt.headless=true','--release','17','-proc:none','-encoding','UTF-8','-sourcepath',str(empty),'-classpath',':'.join(map(str,cp)),'-d',str(classes),str(frozen)]
r=subprocess.run(cmd,capture_output=True,text=True);(W/'compile.log').write_text(r.stdout+r.stderr);(W/'command.json').write_text(json.dumps(cmd,indent=2))
result=dict(status='PASS' if r.returncode==0 else 'FAIL',exit_code=r.returncode,work=str(W.relative_to(R)),source=str(src.relative_to(R)),source_sha256=sha(frozen),classes_sha256={str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},native_qa_official_class_origin=str(Q.relative_to(R)),base_QA_sources_modified=False,Gradle_executed=False,game_started=False,native_actions_verified=False,SRG_packaging=False)
O.mkdir(parents=True,exist_ok=True);(W/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');(O/'compile01.json').write_text(json.dumps(result,indent=2)+'\n');print(r.stdout+r.stderr);print(json.dumps(result,indent=2));raise SystemExit(r.returncode)
