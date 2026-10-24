from pathlib import Path
import subprocess,sys,json,hashlib,datetime,shutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;D=R/'docs/cod4/audit-20261022/ecology-acceptance'
label=sys.argv[1]
if not label.replace('-','').isalnum():raise SystemExit('Invalid run label')
log=D/(label+'.log');receipt=D/(label+'-receipt.json')
if log.exists() or receipt.exists():raise SystemExit('Run label already used')
files=[B/'qa.init.gradle',B/'run.sh',B/'server.properties.template',B/'run_verified.py',*sorted((B/'src').glob('*.java')),D/'frozen-source-sha256.json']
def hashes():return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes();w=B/'.work'/label;w.mkdir()
(w/'eula.txt').write_text('eula=true\n');shutil.copy2(B/'server.properties.template',w/'server.properties')
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('w') as stream:p=subprocess.run(['sh',str(B/'run.sh'),label],cwd=R,stdout=stream,stderr=subprocess.STDOUT)
txt=log.read_text();obs=json.loads((D/'observations.json').read_text());shutil.copy2(D/'observations.json',D/(label+'-observations.json'))
frozen=B/'.work/frozen';manifest=json.loads((D/'frozen-source-sha256.json').read_text());valid=all(hashlib.sha256((frozen/k).read_bytes()).hexdigest()==v for k,v in manifest.items())
result={'started':started,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':p.returncode,'native_finished':'ECOLOGY_NATIVE_FINISHED NATIVE_BOUNDED_CHECK_COMPLETED' in txt,'build_successful':'BUILD SUCCESSFUL' in txt,'inputs_sha256':before,'inputs_unchanged':hashes()==before,'frozen_source_verified':valid,'seed':obs.get('seed'),'generator':obs.get('generator'),'status':obs.get('status'),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));sys.exit(0 if result['native_finished'] and result['inputs_unchanged'] and valid else 1)
