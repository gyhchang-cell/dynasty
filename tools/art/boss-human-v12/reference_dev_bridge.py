"""Private dev-runtime name bridge for locally installed mods; no art export or redistribution.
SRG field/method identifiers are globally numbered. Only unambiguous identifiers are replaced
in class constant pools. All assets and behavior instructions remain byte-identical.
"""
from pathlib import Path
import zipfile,struct,re,json,hashlib
R=Path(__file__).resolve().parents[3];out=R/'build/boss-human-v12-reference-mods';out.mkdir(exist_ok=True)
mapping=Path('/Users/a15356015027/Desktop/dynasty/build/createSrgToMcp/output.srg')
groups={}
for line in mapping.read_text().splitlines():
 p=line.split()
 if p[0]=='FD:':a,b=p[1].split('/')[-1],p[2].split('/')[-1]
 elif p[0]=='MD:':a,b=p[1].split('/')[-1],p[3].split('/')[-1]
 else:continue
 groups.setdefault(a,set()).add(b)
names={a:next(iter(b)) for a,b in groups.items() if len(b)==1}
pattern=re.compile(r'(?<![A-Za-z0-9_])(?:m|f)_\d+_(?![A-Za-z0-9_])')
def bridge(data):
 n=struct.unpack_from('>H',data,8)[0];parts=[data[:10]];pos=10;i=1
 lengths={3:4,4:4,5:8,6:8,7:2,8:2,9:4,10:4,11:4,12:4,15:3,16:2,17:4,18:4,19:2,20:2}
 while i<n:
  tag=data[pos];pos+=1;parts.append(bytes([tag]))
  if tag==1:
   length=struct.unpack_from('>H',data,pos)[0];pos+=2;s=data[pos:pos+length];pos+=length
   # Modified UTF8 non-ASCII bytes remain untouched. Identifiers are ASCII.
   s=re.sub(rb'(?<![A-Za-z0-9_])(?:m|f)_\d+_(?![A-Za-z0-9_])',lambda m:names.get(m.group().decode(),m.group().decode()).encode(),s)
   parts.append(struct.pack('>H',len(s))+s)
  else:
   length=lengths[tag];parts.append(data[pos:pos+length]);pos+=length
   if tag in [5,6]:i+=1
  i+=1
 parts.append(data[pos:]);return b''.join(parts)
sources=[Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods/[玩法;灾变]L_Enders_Cataclysm-3.27.jar'),Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods/[前置;灾变]lionfishapi-2.4-Fix.jar')]
report=[]
for p in sources:
 dst=out/('cataclysm-dev-study.jar' if 'Cataclysm' in p.name else 'lionfish-dev-study.jar');count=0
 with zipfile.ZipFile(p) as src,zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as target:
  for n in src.namelist():
   b=src.read(n);nb=bridge(b) if n.endswith('.class') else b;count+=b!=nb;target.writestr(n,nb)
 with zipfile.ZipFile(p) as src,zipfile.ZipFile(dst) as target:
  assets=[n for n in src.namelist() if n.startswith('assets/')]
  assert all(src.read(n)==target.read(n) for n in assets)
 report.append({'sourceName':p.name,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'devStudySha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'changedClassNamePools':count,'allAssetBytesUnchanged':len(assets),'scope':'Personal temporary dev runtime only; never ship these JARs or assets in Dynasty'})
(out/'bridge-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
