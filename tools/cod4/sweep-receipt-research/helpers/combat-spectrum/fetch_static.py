"""Download pinned text only; never import/build/execute upstream content."""
import subprocess,json,tarfile,io,hashlib
from pathlib import Path
from datetime import datetime,timezone
base=Path(__file__).resolve().parent
out=Path('docs/cod4/audit-20261022/sweep-receipt-research/helpers/combat-spectrum')
records=[]
for repo,branch,rev in [('ZsoltMolnarrr/BetterCombat','1.20.1','8814f0297bb85f4513646e73d604069487ce7322'),('DaFuqs/Spectrum','1.20.1-fabric','8011b7e71db6d14eaa2dc85d35372c506e59f236')]:
 meta=json.loads(subprocess.check_output(['curl','-fsSL','https://api.github.com/repos/'+repo]))
 commit=json.loads(subprocess.check_output(['curl','-fsSL',f'https://api.github.com/repos/{repo}/commits/{rev}']))
 data=subprocess.check_output(['curl','-fsSL',f'https://codeload.github.com/{repo}/tar.gz/{rev}'])
 root=base/'sources'/repo.replace('/','__'); files=[]
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
  for member in tf:
   rel=Path(*Path(member.name).parts[1:])
   if member.isfile() and '..' not in rel.parts and (str(rel).endswith(('.java','.kt')) or rel.name.lower().startswith(('readme','license'))):
    raw=tf.extractfile(member).read(); target=root/rel; target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    files.append({'path':str(rel),'sha256':hashlib.sha256(raw).hexdigest()})
 records.append({'repo':repo,'official_url':meta['html_url'],'fork':meta['fork'],'description':meta['description'],'branch':branch,'revision':rev,'commit_sha_confirmed':commit['sha'],'commit_date':commit['commit']['committer']['date'],'retrieved_at':datetime.now(timezone.utc).isoformat(),'archive_sha256':hashlib.sha256(data).hexdigest(),'source_root':str(root.relative_to(Path.cwd())),'files':files,'upstream_code_executed':False})
 print(repo,rev,len(files))
(out/'source-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
