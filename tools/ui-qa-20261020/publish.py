"""Narrow, backed-up delivery of verified UI fixes. Never touches player saves/options."""
from pathlib import Path
import json,zipfile,hashlib,shutil,os,io,sys
R=Path(__file__).resolve().parents[2];O=R/'docs/ui-fixes-20261020';B=O/'install-backup';B.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'tools/art'))
def release_mod(filename):
 return not Path(filename).name.lower().startswith(("dynasty-playtest-helper","dynasty-audit-","dynasty-quest-qa"))
BASE=Path('/Users/a15356015027/Public/.minecraft')
HUD='armorpointspp-forge-1.20-3.1.1.jar';HUD_BYTES=(R/'libs'/HUD).read_bytes();CFG=(R/'modpack/config/armorpointspp-client.toml').read_bytes()
assert (O/'native-final/COMPLETE.txt').is_file() and not (O/'native-final/FAIL.txt').exists()
assert 'MISSING_MODELS 0' in (O/'native-final/audit.txt').read_text()
assert '\nOK\n' in (O/'tests.txt').read_text()
OWNED=['client/DynastyHealthHud','client/DynastyVitalsOverlay','client/DynastyTooltips','client/DynastyItemInfo','client/DynastyItemUsage','client/DynastySearchAliases','client/DynastySearchJei','client/DynastyAccessorySources','DynastyTrinketTips','army/ArmyRosterScreen']
with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
 PATCH={n:z.read(n) for n in z.namelist() if any(n=='com/dynasty/'+k+'.class' or n.startswith('com/dynasty/'+k+'$') for k in OWNED)}
for p in (R/'src/main/resources/assets').rglob('*'):
 if p.is_file() and (p.as_posix().endswith(('lang/zh_cn.json','lang/en_us.json','dynasty/search_aliases.json','dynasty/accessory_sources.json','minecraft/atlases/blocks.json','dynasty/models/block/dungeon_masonry_5.json')) or '/patchouli_books/' in p.as_posix() or '/textures/gui/quests/journey/' in p.as_posix()):PATCH[p.relative_to(R/'src/main/resources').as_posix()]=p.read_bytes()
assert all(not n.startswith('assets/dynasty/textures/item/') for n in PATCH)
# Native runtime tested these exact compiled classes and resources (native manifest itself is metadata).
with zipfile.ZipFile(R/'build/ui-client-20261020-final/mods/dynasty-1.4.0.jar') as tested:
 for n,data in PATCH.items():
  if n.endswith('native-figures.json'):continue
  assert tested.read(n)==data,('not the native-tested payload',n)
QUESTS={p.relative_to(R/'modpack').as_posix():p.read_bytes() for p in (R/'modpack/config/ftbquests/quests').rglob('*.snbt')}
PACK=(R/'modpack/resourcepacks/dynasty-quest-guides-v3.zip').read_bytes()
records=[];snapshots={};options={}
def progress():
 (O/'deployment-in-progress.json').write_text(json.dumps({'records':records},ensure_ascii=False,indent=2)+'\n')
def sha(data):return hashlib.sha256(data).hexdigest()
def old(path):
 data=path.read_bytes();backup=B/sha(data)/path.name;backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():backup.write_bytes(data)
 return data

def write(path,data):
 if path.exists() and path.read_bytes()==data:return
 prior=old(path) if path.exists() else None
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.ui20-pending');temp.write_bytes(data);os.replace(temp,path)
 records.append({'path':str(path),'before':sha(prior) if prior is not None else None,'after':sha(data)});progress()

def patch_blob(blob,changes,remove=()):
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  dest=io.BytesIO()
  with zipfile.ZipFile(dest,'w') as out:
   out.comment=z.comment
   for entry in z.infolist():
    if entry.filename not in remove:out.writestr(entry,changes.get(entry.filename,z.read(entry.filename)))
   for k,v in changes.items():
    if k not in z.namelist():out.writestr(k,v,compress_type=zipfile.ZIP_DEFLATED)
  result=dest.getvalue()
  with zipfile.ZipFile(io.BytesIO(result)) as out:
   for entry in z.infolist():
    if entry.filename not in remove and entry.filename not in changes:assert out.getinfo(entry.filename).CRC==entry.CRC,entry.filename
   assert all(out.read(k)==v for k,v in changes.items())
 return result

def rewrite(path,changes,remove=()):
 blob=old(path);snapshots[str(path)]=sha(blob);result=patch_blob(blob,changes,remove)
 assert sha(path.read_bytes())==sha(blob),('concurrent target edit',path)
 write(path,result);print('Verified and updated',path,flush=True)

jars=[R/'modpack/mods/dynasty-1.4.0.jar',R/'整合包实例/mods/dynasty-1.4.0.jar',BASE/'mods/dynasty-1.4.0.jar',Path('/Users/a15356015027/Desktop/导出/Dynasty模组/dynasty-1.4.0.jar')]+list((BASE/'versions').glob('Dynasty*/mods/dynasty-1.4.0.jar'))
jars=[p for p in jars if p.exists()]
assert len(jars)==8,('Unexpected deployment targets; inspect before delivery',list(map(str,jars)))
roots=[R/'modpack',R/'整合包实例',BASE]+[p for p in (BASE/'versions').glob('Dynasty*') if (p/'mods/dynasty-1.4.0.jar').exists()]
previous=json.loads((R/'docs/quests-journey-v3/DELIVERY.json').read_text())
prefix='modpack/config/ftbquests/quests/';expected={k[len(prefix):]:v for k,v in previous['source_sha256'].items() if k.startswith(prefix)}
for root in roots:
 if root==R/'modpack':continue
 target=root/'config/ftbquests/quests'
 if target.exists():
  actual={p.relative_to(target).as_posix():sha(p.read_bytes()) for p in target.rglob('*.snbt')}
  assert actual==expected,('Inspect changed quest configuration before delivery',root)
 p=root/'options.txt'
 if p.exists():options[str(p)]=sha(p.read_bytes())
# Validate quest gameplay against this turn's exact source baseline, not an outdated chapter count.
a=json.loads((O/'baseline/docs/quests-remaster/book.json').read_text());b=json.loads((R/'docs/quests-remaster/book.json').read_text())
a={q['id']:q for c in a for q in c['quests']};b={q['id']:q for c in b for q in c['quests']};assert a.keys()==b.keys()
fields=('tasks','rewards','deps','target','kind','count','x','y','size','shape','optional','repeatable')
assert all(all(q.get(k)==b[i].get(k) for k in fields) for i,q in a.items()),'Quest gameplay/layout changed'
for p in jars:rewrite(p,PATCH)
for root in roots:
 for p in (root/'mods').glob('*.jar'):
  if p.name.lower().startswith('overflowingbars-') or not release_mod(p.name):
   old(p);records.append({'path':str(p),'removed':'conflicting HUD or workshop helper','before':sha(p.read_bytes())});p.unlink();progress()
 write(root/'mods'/HUD,HUD_BYTES);write(root/'config/armorpointspp-client.toml',CFG)
 # Distribution instance gains the same complete config, never a save or launcher option.
 for name,data in QUESTS.items():write(root/name,data)
 write(root/'resourcepacks/dynasty-quest-guides-v3.zip',PACK)
# The loose mod export also includes the small optional client HUD dependency.
write(Path('/Users/a15356015027/Desktop/导出/Dynasty模组')/HUD,HUD_BYTES)
index_file=R/'modpack/modrinth.index.json';index=json.loads(index_file.read_text());index['files']=[f for f in index['files'] if not f['path'].lower().startswith('mods/overflowingbars-') and release_mod(f['path'])];write(index_file,json.dumps(index,ensure_ascii=False,indent=2).encode()+b'\n')
hud_record={'path':'mods/'+HUD,'hashes':{a:hashlib.new(a,HUD_BYTES).hexdigest() for a in ('sha1','sha512')},'downloads':['https://cdn.modrinth.com/data/xvAim1vw/versions/Uf0tqswT/'+HUD],'fileSize':len(HUD_BYTES),'env':{'client':'required','server':'unsupported'}}
exports=[]
for folder in [R/'dist',Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')]:
 for filename in ['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']:
  p=folder/filename
  if not p.exists():continue
  with zipfile.ZipFile(p) as z:
   names=z.namelist();changes={'overrides/mods/dynasty-1.4.0.jar':patch_blob(z.read('overrides/mods/dynasty-1.4.0.jar'),PATCH),'overrides/config/armorpointspp-client.toml':CFG,'overrides/resourcepacks/dynasty-quest-guides-v3.zip':PACK}
   changes.update({'overrides/'+k:v for k,v in QUESTS.items()})
   remove=[n for n in names if n.startswith('overrides/mods/') and (Path(n).name.lower().startswith('overflowingbars-') or not release_mod(n))]
   if 'modrinth.index.json' in names:
    idx=json.loads(z.read('modrinth.index.json'));had_download=any('overflowingbars' in f['path'].lower() or 'armorpointspp' in f['path'].lower() for f in idx['files'])
    idx['files']=[f for f in idx['files'] if not any(x in f['path'].lower() for x in ['overflowingbars','armorpointspp']) and release_mod(f['path'])]
    if had_download:idx['files'].append(hud_record)
    else:changes['overrides/mods/'+HUD]=HUD_BYTES
    changes['modrinth.index.json']=json.dumps(idx,ensure_ascii=False,indent=2).encode()+b'\n'
   elif 'manifest.json' in names:
    m=json.loads(z.read('manifest.json'));m['files']=[f for f in m['files'] if f['projectID'] not in (396094,852662)];m['files'].append({'projectID':396094,'fileID':4613606,'required':True})
    changes['manifest.json']=json.dumps(m,ensure_ascii=False,indent=2).encode()+b'\n'
   else:changes['overrides/mods/'+HUD]=HUD_BYTES
  rewrite(p,changes,remove);exports.append(p)
assert len(exports)==6,('Missing expected export packages',list(map(str,exports)))
for p in jars:
 with zipfile.ZipFile(p) as z:assert all(z.read(k)==v for k,v in PATCH.items())
for root in roots:
 assert not any(p.name.lower().startswith('overflowingbars-') or not release_mod(p.name) for p in (root/'mods').glob('*.jar'))
 assert (root/'mods'/HUD).read_bytes()==HUD_BYTES
 for name,data in QUESTS.items():assert (root/name).read_bytes()==data
for p,digest in options.items():assert sha(Path(p).read_bytes())==digest,'User options changed'
report={'verified_core_jars':len(jars),'verified_exports':len(exports),'profiles_and_distribution_roots':list(map(str,roots)),'quest_count':len(b),'quest_gameplay_layout_unchanged':True,'native_figure_count':26,'native_recipe_coverage':(O/'native-final/audit.txt').read_text().strip(),'user_options_unchanged':options,'approved_item_art_unmodified':True,'github_pushed':False,'patch_members':list(PATCH),'records':records}
(O/'deployment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Keep future quest sync compatible with this verified delivery.
previous.update(status='round-20-ui-health-search-verified',quests_after=len(b),native_client_passed_runs=1,native_result=report['native_recipe_coverage']+'; native JEI/creative search, 5 HP states, tiger-tally assignment, all 1259 quest icons. Not a full campaign playthrough.',tests_passed=75,original_operation_figures=26)
previous['source_sha256']={k:sha((R/k).read_bytes()) for k in previous['source_sha256'] if (R/k).exists()}
write(R/'docs/quests-journey-v3/DELIVERY.json',json.dumps(previous,ensure_ascii=False,indent=2).encode()+b'\n')
write(R/'docs/quests-journey-v3/last-deployed-book.json',(R/'docs/quests-remaster/book.json').read_bytes())
(O/'deployment-in-progress.json').unlink(missing_ok=True)
print('Verified all deliveries; player saves, options, approved item textures and other compiled classes preserved.',flush=True)
