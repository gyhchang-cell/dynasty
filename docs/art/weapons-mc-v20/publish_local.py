"""Asset-only publication. Patch nine weapon/atlas payloads, preserving every other JAR/archive payload."""
from pathlib import Path
import json,hashlib,zipfile,io,os,shutil,tempfile
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'src/main/resources/assets/dynasty';BASE=Path('/Users/a15356015027/Public/.minecraft')
sha=lambda b:hashlib.sha256(b).hexdigest()
def atomic(p,data):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.weapons-v20-pending');tmp.write_bytes(data);os.replace(tmp,p)
def backup(p,old):
 q=D/'deployment-before'/sha(old)/p.name
 if not q.exists():q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(old)
cache={};reports=[]
def patch_bytes(blob,replacements,label):
 key=(sha(blob),tuple((k,sha(v)) for k,v in sorted(replacements.items())))
 if key in cache:return cache[key]
 with zipfile.ZipFile(io.BytesIO(blob)) as zin:
  if any(k.startswith('assets/') for k in replacements):assert 'com/dynasty/client/OriginalItemGeometry.class' in zin.namelist(),label+' missing loader'
  assert len(zin.namelist())==len(set(zin.namelist())),label
  assert all(k in zin.namelist() for k in replacements),label
  sig=[n for n in zin.namelist() if n.startswith('META-INF/') and n.endswith(('.SF','.RSA','.DSA'))];assert not sig,'Signed archive '+label
  out=io.BytesIO();hashes={}
  with zipfile.ZipFile(out,'w') as zout:
   zout.comment=zin.comment
   for info in zin.infolist():
    payload=zin.read(info.filename);hashes[info.filename]=sha(payload);zout.writestr(info,replacements.get(info.filename,payload))
  result=out.getvalue()
 with zipfile.ZipFile(io.BytesIO(result)) as z:
  assert z.testzip() is None
  assert set(z.namelist())==set(hashes)
  for n,h in hashes.items():assert sha(z.read(n))==(sha(replacements[n]) if n in replacements else h),(label,n)
 row={'label':label,'beforeSha256':sha(blob),'afterSha256':sha(result),'changedEntries':list(replacements),'otherPayloadsUnchanged':len(hashes)-len(replacements),'crc':'PASS'}
 reports.append(row);cache[key]=result;return result
rows=json.loads((D/'selection.json').read_text());baseline=json.loads((D/'baseline.json').read_text());files={}
for row in rows:
 for sub,ext in [('textures/item','png'),('models/item','json')]:
  member='assets/dynasty/'+sub+'/'+row['id']+'.'+ext
  files[member]=(R/'src/main/resources'/member).read_bytes()
files['assets/minecraft/atlases/blocks.json']=(R/'src/main/resources/assets/minecraft/atlases/blocks.json').read_bytes()
assert 'PASS 4 original PNGs' in (D/'native.log').read_text()
for member,data in files.items():
 built=R/'build/resources/main'/member
 if built.parent.exists():atomic(built,data)
core=R/'build/libs/dynasty-1.4.0.jar';targetdirs=[R/'modpack/mods',R/'整合包实例/mods',Path('/Users/a15356015027/Desktop/导出/Dynasty模组'),BASE/'mods']
if (BASE/'versions').exists():targetdirs += [p/'mods' for p in (BASE/'versions').iterdir() if p.is_dir() and 'Dynasty' in p.name]
jarpaths=[core]+[p/'dynasty-1.4.0.jar' for p in targetdirs if (p/'dynasty-1.4.0.jar').exists()]
installed=[]
for p in jarpaths:
 old=p.read_bytes();new=patch_bytes(old,files,str(p));backup(p,old);assert sha(p.read_bytes())==sha(old),'Concurrent JAR edit '+str(p);atomic(p,new);installed.append({'path':str(p),'sha256':sha(new),'patchedResources':len(files)});print('Patched JAR',p,flush=True)
# Patch the original core member of each existing export independently; do not replace its other classes or any manifests/config/mods.
packnames=['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip'];exports=[R/'dist'/n for n in packnames]+[Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')/n for n in packnames];member='overrides/mods/dynasty-1.4.0.jar'
for p in exports:
 if not p.exists():continue
 old=p.read_bytes()
 with zipfile.ZipFile(io.BytesIO(old)) as z:original=z.read(member)
 patched=patch_bytes(original,files,str(p)+'!'+member);new=patch_bytes(old,{member:patched},str(p));backup(p,old);assert sha(p.read_bytes())==sha(old),'Concurrent export edit '+str(p);atomic(p,new);installed.append({'path':str(p),'sha256':sha(new),'patchedResources':len(files),'onlyOuterMemberChanged':member});print('Patched export',p,flush=True)
other=[];unchanged=0
selected={f'src/main/resources/{n}' for n in files}
for rel,digest in baseline.items():
 if rel in selected:continue
 p=R/rel
 if p.exists() and sha(p.read_bytes())==digest:unchanged+=1
 else:other.append(rel)
report={'status':'PUBLISHED_LOCAL','weapons':4,'originalPixelsUnchanged':True,'otherTexturePngsUnchanged':unchanged,'concurrentOtherTextureChangesNotOverwritten':other,'archivePayloadChecks':reports,'installed':installed,'publication':'Resource-only patch, nine exact entries; all other payloads preserved','nativeCheck':'NativeImage+ItemModelGenerator PASS, not graphical acceptance','savesSoundBrightnessClientTouched':False}
(D/'DELIVERY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('COMPLETE',len(installed),'local JAR/export files;',unchanged,'other source PNGs unchanged')
