"""Run private native suites, preserving logs, observations, input hashes and actual verdict."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,shutil,subprocess
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
OUT=ROOT/'docs/cod4/audit-20261022/interaction-acceptance'
p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('--namespace',default='dynasty_interaction_qa');a=p.parse_args()
assert re.fullmatch(r'[A-Za-z0-9_-]+',a.label)
log=OUT/(a.label+'.log'); receipt=OUT/(a.label+'-receipt.json');assert not log.exists() and not receipt.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[BASE/'qa.init.gradle',BASE/'run.sh',OUT/'frozen-source-sha256.json',*sorted((BASE/'src').glob('*.java'))]
record={'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'finished':None,'namespace':a.namespace,'inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs},'headless':True,'human_multiplayer':False,'ticks':'actual accelerated GameTestServer world ticks; no clock-field rewrites in real_clock cases'}
receipt.write_text(json.dumps(record,indent=2)+'\n')
with log.open('w') as stream: result=subprocess.run(['sh',str(BASE/'run.sh'),a.label,a.namespace],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
s=log.read_text();failures=re.findall(r'\[minecraft/LogTestReporter\]: (.*?) failed! (.*)',s)
summary=re.search(r'(\d+) tests (?:done|finished)',s)
allpass=re.search(r'All (\d+) required tests passed',s);failed=re.search(r'(\d+) required tests failed',s)
obs=OUT/'observations.json'
if obs.exists():shutil.copy2(obs,OUT/(a.label+'-observations.json'))
record.update({'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result.returncode,'failures':[{'test':n,'reason':r} for n,r in failures],'required_all_pass':int(allpass[1]) if allpass else None,'required_failed':int(failed[1]) if failed else 0 if allpass else None,'test_batches':re.findall(r"Running test batch '(.*?)' \((\d+) tests\)",s),'native_finished':bool(allpass or failed),'build_successful':'BUILD SUCCESSFUL' in s,'log_sha256':sha(log),'inputs_unchanged':all(sha(ROOT/p)==v for p,v in record['inputs_sha256'].items())})
receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False,indent=2))
raise SystemExit(0 if allpass and result.returncode==0 else 1)
