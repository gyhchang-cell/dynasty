"""Narrow resource-only deployment; preserve every unrelated archive member."""
from pathlib import Path
from PIL import Image
import ast,json,zipfile,hashlib,shutil,os,io
R=Path(__file__).resolve().parents[3];O=R/'docs/art/swords-new-v10';A=R/'src/main/resources/assets/dynasty';B=O/'install-backup';B.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'deployment.json').exists(),'Already deployed'
node=next(n for n in ast.parse((R/'tools/art/weapons-twenty-v5/deploy.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='mesh');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh','exec'),ns);mesh=ns['mesh']
patch={};local={};snapshot={}
for r in json.loads((O/'checks.json').read_text()):
 n=r['id'];tp=A/f'textures/item/{n}.png';mp=A/f'models/item/{n}.json';assert sha(tp)==r['runtime_sha256'],n+' externally modified'
 for p in [tp,mp]:snapshot[p]=sha(p)
 local[tp]=(O/f'textures/{n}.png').read_bytes()
 if n=='zhanlu_rendao_bamian_jian':
  assert json.loads(mp.read_text())['parent']=='builtin/entity'
  icon=json.loads((A/f'models/item/{n}_icon.json').read_text())
  assert icon['textures']['layer0']==f'dynasty:item/{n}'
  continue
 m=json.loads(mp.read_text());assert m['parent']=='dynasty:item/solid_handheld'
 m.update(textures={'layer0':f'dynasty:item/{n}','particle':'#layer0'},elements=mesh(Image.open(O/f'textures/{n}.png').convert('RGBA')),render_type='minecraft:cutout',dynasty_solid_edges=True)
 local[mp]=(json.dumps(m,separators=(',',':'))+'\n').encode()
for p,data in local.items():patch['assets/dynasty/'+str(p.relative_to(A))]=data
with zipfile.ZipFile(B/'source-originals.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in local:z.write(p,str(p.relative_to(R)))
for p,data in local.items():assert sha(p)==snapshot[p];p.write_bytes(data)
records=[];cache={}
def patch_zip(p,changes):
 oldhash=sha(p);backup=B/oldhash/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup)
 tmp=p.with_name(p.name+'.swords-v10-pending')
 if oldhash in cache:shutil.copy2(cache[oldhash],tmp)
 else:
  with zipfile.ZipFile(p) as src,zipfile.ZipFile(tmp,'w') as out:
   infos=src.infolist();assert len({i.filename for i in infos})==len(infos),'duplicate ZIP members'
   assert set(changes)<=set(i.filename for i in infos),str(p)+' lacks existing resource'
   for i in infos:out.writestr(i,changes.get(i.filename,src.read(i.filename)))
   out.comment=src.comment
  with zipfile.ZipFile(p) as src,zipfile.ZipFile(tmp) as out:
   for i in src.infolist():
    if i.filename in changes:assert out.read(i.filename)==changes[i.filename]
    else:assert out.getinfo(i.filename).CRC==i.CRC and out.getinfo(i.filename).file_size==i.file_size
 assert sha(p)==oldhash,'Concurrent change, no overwrite: '+str(p)
 os.replace(tmp,p);cache[oldhash]=p;records.append({'path':str(p),'before':oldhash,'after':sha(p),'members_changed':list(changes)})
base=Path('/Users/a15356015027/Public/.minecraft')
jars=[R/'build/libs/dynasty-1.4.0.jar',R/'modpack/mods/dynasty-1.4.0.jar',R/'整合包实例/mods/dynasty-1.4.0.jar',base/'mods/dynasty-1.4.0.jar',Path('/Users/a15356015027/Desktop/导出/Dynasty模组/dynasty-1.4.0.jar')]
jars += [d/'mods/dynasty-1.4.0.jar' for d in (base/'versions').iterdir() if d.is_dir() and 'Dynasty' in d.name]
for p in jars:
 if p.exists():patch_zip(p,patch);print('Synced',p,flush=True)
# Update only the embedded jar in current exports, preserving each export's other files.
for root in [R/'dist',Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')]:
 for name in ['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']:
  p=root/name
  if not p.exists():continue
  with zipfile.ZipFile(p) as z:
   key='overrides/mods/dynasty-1.4.0.jar';blob=z.read(key)
  # Patch this export's own jar, never replace its unrelated contents with another version.
  temp=B/('embedded-'+hashlib.sha256(blob).hexdigest()+'.jar')
  if not temp.exists():temp.write_bytes(blob);patch_zip(temp,patch)
  patch_zip(p,{key:temp.read_bytes()});print('Synced',p,flush=True)
(O/'deployment.json').write_text(json.dumps({'existing_ids':[r['id'] for r in json.loads((O/'checks.json').read_text())],'source_files':{str(p.relative_to(R)):sha(p) for p in local},'archives':records,'method':'resource-only ZIP replacement; unrelated entries preserved','java_started':False,'game_tested':False,'github_pushed':False},ensure_ascii=False,indent=2))
print('Completed source + local game instances + current exports. No registrations or gameplay changes.')
