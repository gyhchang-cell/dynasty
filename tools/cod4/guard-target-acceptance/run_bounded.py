"""Freeze an authorized post-gate fix and run native headless AI regression once."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,time

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'tools/cod4/guard-target-acceptance/.work'
DOC=ROOT/'docs/cod4/audit-20261022/guard-target-native-acceptance'
RESEARCH=ROOT/'docs/cod4/audit-20261022/guard-ownership-research'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
ledger_raw=(RESEARCH/'references.json').read_bytes()
ledger=json.loads(ledger_raw)
assert len(ledger)>=1000,'Do not run before the required research and formal fix'
assert len({r['id'] for r in ledger})==len(ledger)
assert len({r['normalizedSha256'] for r in ledger})==len(ledger)
gate=json.loads((RESEARCH/'gate-1000.json').read_text())
assert gate['productionImplementationPermitted'] and gate['referencesSha256']==sha(ledger_raw), 'Require the final semantic gate for this exact ledger'
subprocess.run(['python3','tools/cod4/audit_guard_references.py'],cwd=ROOT,check=True)
assert not DOC.exists(),'Use a new named evidence run; never replace a previous receipt'
focus=['src/main/java/com/dynasty/expansion/SummonedGuard.java','src/main/java/com/dynasty/expansion/SecondaryMob.java']
updates={}
for rel in focus:
    source=ROOT/rel;dest=BASE/'frozen'/rel
    before=dest.read_bytes();after=source.read_bytes()
    assert before!=after,'Expected the specialist repair in both scoped files'
    updates[rel]={'baseline_sha256':sha(before),'patched_sha256':sha(after)}
    dest.write_bytes(after)
DOC.mkdir()
inputs={'date':datetime.datetime.now().astimezone().isoformat(),'research_rows':len(ledger),'research_ledger_sha256':sha(ledger_raw),
        'overlaid_fix_sources':updates,'game_clients_started':0,'real_TCP_multiplayer':False,
        'fixture':'native ServerPlayer identities with disconnected Connection, actual registered mobs and real AI ticks; not FakePlayer, not networking',
        'qa_sources':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [ROOT/'tools/cod4/guard-target-acceptance/qa.init.gradle',ROOT/'tools/cod4/guard-target-acceptance/src/GuardTargetAcceptance.java',Path(__file__).resolve()]}}
(DOC/'input-manifest.json').write_text(json.dumps(inputs,indent=2)+'\n')
(BASE/'server').mkdir(exist_ok=True)
(BASE/'server/eula.txt').write_text('eula=true\n')
env=os.environ.copy();env['JAVA_HOME']='/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home';env['GRADLE_USER_HOME']=str(ROOT/'tools/cod4/ecology-acceptance/.work/client-build/gradle-home')
cmd=['./gradlew','--offline','--no-daemon','--max-workers=1','--project-cache-dir',str(BASE/'project-cache'),'-I','tools/cod4/guard-target-acceptance/qa.init.gradle','runGameTestServer']
start=time.monotonic();timeout=False
with (DOC/'server.log').open('x') as log:
    process=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try:code=process.wait(timeout=240)
    except subprocess.TimeoutExpired:
        timeout=True;os.killpg(process.pid,signal.SIGINT)
        try:code=process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);code=process.wait(timeout=5)
log=(DOC/'server.log').read_text()
native_pass='GUARD_TARGET_NATIVE_AI_PASS ticks=80' in log
unchanged=all(sha((ROOT/rel).read_bytes())==data['patched_sha256'] for rel,data in updates.items())
receipt={'exit_code':code,'external_timeout':timeout,'elapsed_seconds':round(time.monotonic()-start,2),
         'native_AI_pass_marker':native_pass,'production_still_matches_tested_patch':unchanged,
         'game_clients_started':0,'real_TCP_multiplayer':False,'original_user_world_touched':False,
         'log_sha256':sha(log.encode()),'command':cmd,'status':'PASS' if code==0 and not timeout and native_pass and unchanged else 'FAILED'}
(DOC/'process.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(0 if receipt['status']=='PASS' else 1)
