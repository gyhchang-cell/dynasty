from pathlib import Path
import json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent;v=json.loads((B/'obj-texture-review.json').read_text());checks=[]
def ck(n,b):checks.append(dict(check=n,passed=bool(b)));assert b,n
for manifest in ['asset-acquisition.json','consumer-acquisition.json']:
 for x in json.loads((B/manifest).read_text())['rows']:
  data=(B/x['local']).read_bytes();ck(x['path']+' SHA256',hashlib.sha256(data).hexdigest()==x['sha256']);ck(x['path']+' fixed Git blob',hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==x['expected_blob']);ck(x['path']+' reviewed',x['status'] not in ['ACQUIRED_NOT_YET_REVIEWED','ACQUIRED_NOT_REVIEWED'])
s={x['id']:x for x in v['sources']}
for x in s.values():
 p=B/x['local'];ck(x['id']+' source bytes',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);n=len(p.read_bytes().splitlines())
 for a,b in x['reviewed_ranges']:ck(x['id']+f' range {a}-{b}',1<=a<=b<=n)
for e in v['evidence']:
 ck(e['id']+' zero credit',e['credit_added']==0)
 for ref in e['sources']:ck(e['id']+' ref '+ref,ref in s)
x=json.loads((B/'asset-inspection.json').read_text());ck('UV within atlas',x['uv_in_0_1']);ck('all source faces covered',x['variants']['both']['faces']==x['faces']==179)
ck('native PNG 64 square',list(Image.open(B/s['texture']['local']).size)==[64,64])
for f in v['actually_viewed']:
 im=Image.open(B/f);im.verify();ck('image readable '+f,True)
ck('production untouched',not v['production_changed']);ck('no game',not v['java_game_started']);ck('same family no credit',v['new_source_families']==v['new_accepted_gate_credit']==0)
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定源完整性、阅读范围、UV及预览图片；不验证游戏烘焙/持物/运行',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
