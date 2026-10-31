"""Download pinned candidate text once; a download is not research credit."""
from pathlib import Path
import hashlib,json,shutil,urllib.request
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
BASE=ROOT/'tools/cod4/immune-feedback-research/sources/The-Aether-Team__The-Aether'
OUT=HERE/'acquired-aether-e07d'/'The-Aether-Team__The-Aether'
OUT.mkdir(parents=True,exist_ok=True)
for n in ['source.json','tree.json']:shutil.copyfile(BASE/n,OUT/n)
t=json.loads((BASE/'tree.json').read_text());commit=t['sha']
names=['entity/monster/Swet.java','entity/MountableMob.java','entity/EntityUtil.java','item/EquipmentUtil.java','entity/monster/Zephyr.java','entity/projectile/ZephyrSnowball.java','network/packet/clientbound/ZephyrSnowballHitPacket.java','entity/monster/AechorPlant.java','entity/miscellaneous/CloudMinion.java','network/packet/clientbound/CloudMinionPacket.java','entity/projectile/crystal/CloudCrystal.java']
rows=[]
for name in names:
 path='src/main/java/com/aetherteam/aether/'+name
 entry=next(x for x in t['tree'] if x['path']==path)
 target=OUT/path;url=f'https://raw.githubusercontent.com/The-Aether-Team/The-Aether/{commit}/{path}'
 try:
  if (BASE/path).is_file():raw=(BASE/path).read_bytes();origin='existing local pinned cache'
  elif target.is_file():raw=target.read_bytes();origin='existing owned pinned cache; not re-requested'
  else:
   with urllib.request.urlopen(url,timeout=25) as response:raw=response.read()
   origin='one HTTPS request; no retry'
  blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  if blob!=entry['sha']:raise ValueError('Git blob mismatch')
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  rows.append(dict(path=path,url=url,sha256=hashlib.sha256(raw).hexdigest(),git_blob_sha1=blob,origin=origin,research_credit=0,read_status='candidate_not_yet_semantically_reviewed'))
 except Exception as exc:
  rows.append(dict(path=path,url=url,error=repr(exc),stopped_without_retry=True,research_credit=0));break
record=dict(repo='The-Aether-Team/The-Aether',commit=commit,candidates=rows,research_credit=0,policy='Fixed Git blob checked; not counted until complete reading and native chain + semantic review. Stop at first network error, do not retry.')
(HERE/'acquisition-020.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([dict(path=x['path'],status=x.get('error','blob verified candidate only')) for x in rows],ensure_ascii=False))
