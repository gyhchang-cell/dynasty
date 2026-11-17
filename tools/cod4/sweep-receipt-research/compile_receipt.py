"""Offline javac of frozen affected production source against real official-mapped Forge APIs.
No Gradle invocation, cache writes, launch tasks or game process; all output and input snapshots are private.
"""
from pathlib import Path
import hashlib,json,subprocess,datetime,shutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=R/'docs/cod4/audit-20261022/sweep-receipt-research';W=B/'.work/receipt-fix/native-compile';assert not W.exists();W.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((O/'gate-1000-integrity.json').read_text())['accepted']==1000
src=R/'src/main/java/com/dynasty/cod3/FangtianSweep.java';frozen=W/'frozen/com/dynasty/cod3/FangtianSweep.java';frozen.parent.mkdir(parents=True);shutil.copy2(src,frozen)
baseline=R/'tools/cod4/guard-target-acceptance/.work/gradle-output/classes/java/main';snap=W/'baseline';shutil.copytree(baseline,snap)
cache=R/'tools/cod4/armor-acceptance/.work/gradle-home/caches';mapped=cache/'forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-recomp.jar'
deps=[mapped]+sorted((cache/'modules-2/files-2.1').rglob('*.jar'))
cp=[str(snap)];inputs={};D=W/'dependency-cache';D.mkdir()
for i,p in enumerate(deps):
 dest=D/f'{i:04d}-{p.name}';shutil.copy2(p,dest);cp.append(str(dest));inputs[str(p.relative_to(R))]=dict(sha256=sha(dest),snapshot=str(dest.relative_to(R)))
classes=W/'classes';classes.mkdir();empty=W/'empty-sourcepath';empty.mkdir();jhome=Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home');cmd=[str(jhome/'bin/javac'),'-J-Djava.awt.headless=true','--release','17','-proc:none','-encoding','UTF-8','-sourcepath',str(empty),'-classpath',':'.join(cp),'-d',str(classes),str(frozen)]
(W/'command.json').write_text(json.dumps(cmd,indent=2)+'\n');run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(W/'compile.log').write_text(run.stdout+run.stderr)
result=dict(finished_at=datetime.datetime.now().astimezone().isoformat(),exit_code=run.returncode,status='PASS' if run.returncode==0 else 'FAIL',source=str(src.relative_to(R)),source_sha256=sha(src),frozen_source_sha256=sha(frozen),source_unchanged=sha(src)==sha(frozen),compiler='javac --release 17; real official-mapped Minecraft1.20.1/Forge47.4.10 classpath',gradle_executed=False,shared_gradle_cache_written=False,private_dependency_snapshots=inputs,baseline_classes_sha256={str(p.relative_to(snap)):sha(p) for p in sorted(snap.rglob('*.class'))},affected_classes_sha256={str(p.relative_to(classes)):sha(p) for p in sorted(classes.rglob('*.class'))},log=str((W/'compile.log').relative_to(R)),game_or_server_started=False,real_C2S_verified=False)
(O/'offline-compile-receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in result.items() if not isinstance(v,dict)});print(run.stdout+run.stderr);raise SystemExit(run.returncode)
