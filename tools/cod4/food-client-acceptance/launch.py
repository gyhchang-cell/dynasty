"""Isolated full-pack production launch using installed version metadata, never JVM credentials."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,uuid
R=Path(__file__).resolve().parents[3]
BASE=Path('/Users/a15356015027/Public/.minecraft'); PROFILE=BASE/'versions/Dynasty'
RUN=sys.argv[1] if len(sys.argv)>1 else 'run-01'
LANG=sys.argv[2] if len(sys.argv)>2 else 'zh_cn'
assert LANG in ['zh_cn','en_us']
assert re.fullmatch(r'run-\d+',RUN),RUN
ROOT=R/'tools/cod4/food-client-acceptance/.work'/RUN; OUT=R/'docs/cod4/audit-20261022/food-client-acceptance'/RUN
if ROOT.exists():raise SystemExit('Fresh run required; previous evidence/world is preserved')
ROOT.mkdir(parents=True);OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'identity':'offline QA only','installed_version_json':str(PROFILE/'Dynasty.json'),'version_sha256':sha(PROFILE/'Dynasty.json'),'instance':str(ROOT),'source_files':{},'qa_overrides':{},'helper_sources':{str(p.relative_to(R)):sha(p) for p in sorted((R/'tools/cod4/food-client-acceptance').rglob('*')) if p.is_file() and '.work' not in p.parts}}
for folder in ['mods','config','defaultconfigs','resourcepacks']:
 source=R/'modpack'/folder
 if source.exists():
  shutil.copytree(source,ROOT/folder)
  for p in sorted(source.rglob('*')):
   if p.is_file():manifest['source_files'][p.relative_to(R/'modpack').as_posix()]=sha(p)
main=R/'build/cod4-pack-20261022/language-repair/dynasty-1.4.0.jar'
provenance=json.loads((R/'docs/cod4/audit-20261022/pack-acceptance/language-repair-build.json').read_text())
assert sha(main)==provenance['repair_sha256']
manifest['production_jar_provenance']=provenance
helper=R/'tools/cod4/food-client-acceptance/.work/gradle/libs/dynasty-food-client-qa-1.4.0.jar'
for p in [main,helper]:
 dest=ROOT/'mods'/p.name
 if dest.exists():
  if p!=main:raise RuntimeError('Unexpected QA helper in pack: '+str(dest))
  preserved=ROOT/'source-snapshot'/dest.name;preserved.parent.mkdir(exist_ok=True);shutil.copy2(dest,preserved)
  manifest['qa_overrides'][dest.relative_to(ROOT).as_posix()]={'original_preserved_at':str(preserved),'original_sha256':sha(preserved),'replacement_sha256':sha(p)}
 shutil.copy2(p,dest)
manifest['added_jars']={p.name:sha(p) for p in [main,helper]}
# QA presentation settings only; all original mods/config/resourcepacks remain in the snapshot.
(ROOT/'options.txt').write_text('soundCategory_master:0.0\npauseOnLostFocus:false\nlang:'+LANG+'\nguiScale:3\nmaxFps:60\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\nresourcePacks:["vanilla","mod_resources","file/dynasty-quest-guides-v3.zip"]\n')
manifest['qa_overrides']['options.txt']=sha(ROOT/'options.txt')
V=json.loads((PROFILE/'Dynasty.json').read_text());features={'has_custom_resolution':True}
def allowed(x):
 if 'rules' not in x:return True
 result=False
 for rule in x['rules']:
  o=rule.get('os',{});match=(not o.get('name') or o['name']=='osx') and (not o.get('arch') or o['arch'] in ['arm64','aarch64']) and all(features.get(k,False)==v for k,v in rule.get('features',{}).items())
  if match:result=rule['action']=='allow'
 return result
libs=[]
for e in V['libraries']:
 if not allowed(e):continue
 path=e.get('downloads',{}).get('artifact',{}).get('path')
 if not path:
  group,name,ver,*classifier=e['name'].split(':');path=group.replace('.','/')+'/'+name+'/'+ver+'/'+name+'-'+ver+('-'+classifier[0] if classifier else '')+'.jar'
 p=BASE/'libraries'/path
 if not p.exists():raise FileNotFoundError(p)
 libs.append(str(p))
libs.append(str(PROFILE/'Dynasty.jar'))
variables={'natives_directory':str(PROFILE/'natives-macos-arm64'),'launcher_name':'COD4FoodPrivateQA','launcher_version':'1','classpath':os.pathsep.join(libs),'library_directory':str(BASE/'libraries'),'classpath_separator':os.pathsep,'version_name':'Dynasty','primary_jar_name':'Dynasty.jar','auth_player_name':'Cod4FoodQA','game_directory':str(ROOT),'assets_root':str(BASE/'assets'),'assets_index_name':V.get('assetIndex',{}).get('id','5'),'auth_uuid':uuid.uuid3(uuid.NAMESPACE_DNS,'OfflinePlayer:Cod4FoodQA').hex,'auth_access_token':'0','clientid':'0','auth_xuid':'0','user_type':'legacy','version_type':'release','resolution_width':'1280','resolution_height':'800'}
def expand(s):return re.sub(r'\$\{(.*?)\}',lambda m:variables[m[1]],s)
def args(group):
 out=[]
 for e in V['arguments'][group]:
  if isinstance(e,str):out.append(expand(e))
  elif allowed(e):out.extend(expand(x) for x in (e['value'] if isinstance(e['value'],list) else [e['value']]))
 return out
command=['/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home/bin/java','-Xmx4G','-XX:ActiveProcessorCount=2','-Ddynasty.foodqa.output='+str(OUT),'-Ddynasty.foodqa.instance='+str(ROOT)]+args('jvm')+[V['mainClass']]+args('game')
manifest['total_mod_jars']=len(list((ROOT/'mods').glob('*.jar')))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
with (OUT/'client.log').open('w') as log:
 p=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 (OUT/'pid.txt').write_text(str(p.pid));print('Own isolated QA PID',p.pid,'mods',manifest['total_mod_jars'],flush=True)
 result=p.wait();(OUT/'exit-code.txt').write_text(str(result));print('exit',result,flush=True)
