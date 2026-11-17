"""Isolated full-pack production launch using installed version metadata, never JVM credentials."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,uuid
R=Path(__file__).resolve().parents[3]
BASE=Path('/Users/a15356015027/Public/.minecraft'); PROFILE=BASE/'versions/Dynasty'
RUN=sys.argv[1] if len(sys.argv)>1 else 'run-01'
ROLE=sys.argv[2] if len(sys.argv)>2 else 'host'
assert ROLE in ['host','peer']
SUITE=sys.argv[3] if len(sys.argv)>3 else 'states'
assert SUITE in ['states','reactions','neutral']
LANG='zh_cn'
assert LANG in ['zh_cn','en_us']
assert re.fullmatch(r'run-\d+',RUN),RUN
ROOT=R/'build/cod4-mob-network-20261023'/RUN/ROLE; OUT=R/'docs/cod4/audit-20261022/mob-network-acceptance'/RUN
if ROOT.exists():raise SystemExit('Fresh run required; previous evidence/world is preserved')
ROOT.mkdir(parents=True);OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'identity':'offline QA only','installed_version_json':str(PROFILE/'Dynasty.json'),'version_sha256':sha(PROFILE/'Dynasty.json'),'instance':str(ROOT),'source_files':{},'qa_overrides':{}}
for folder in ['config','defaultconfigs']:
 source=R/'modpack'/folder
 if source.exists():
  shutil.copytree(source,ROOT/folder)
  for p in sorted(source.rglob('*')):
   if p.is_file():manifest['source_files'][p.relative_to(R/'modpack').as_posix()]=sha(p)
(ROOT/'mods').mkdir()
main=R/'build/cod4-audit-20261022/verified-gradle/libs/dynasty-1.4.0.jar'
verification=json.loads((R/'docs/cod4/audit-20261022/verification.json').read_text())
assert sha(main)=='ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b','Unified artifact changed'
manifest['unified_artifact_sha256']=sha(main)
helper=R/'build/cod4-mob-network-20261023/gradle/libs/dynasty-mob-network-acceptance-1.4.0.jar'
for name in ['geckolib-forge-1.20.1-4.8.4.jar','curios-forge-5.14.1+1.20.1.jar']:
 p=R/'modpack/mods'/name;shutil.copy2(p,ROOT/'mods'/name);manifest['source_files']['mods/'+name]=sha(p)
for p in [main,helper]:
 dest=ROOT/'mods'/p.name
 if dest.exists():
  if p!=main:raise RuntimeError('Unexpected QA helper in pack: '+str(dest))
  preserved=ROOT/'source-snapshot'/dest.name;preserved.parent.mkdir(exist_ok=True);shutil.copy2(dest,preserved)
  manifest['qa_overrides'][dest.relative_to(ROOT).as_posix()]={'original_preserved_at':str(preserved),'original_sha256':sha(preserved),'replacement_sha256':sha(p)}
 shutil.copy2(p,dest)
manifest['added_jars']={p.name:sha(p) for p in [main,helper]}
# QA presentation settings only; all original mods/config/resourcepacks remain in the snapshot.
(ROOT/'options.txt').write_text('soundCategory_master:0.0\npauseOnLostFocus:false\nlang:'+LANG+'\nguiScale:3\nmaxFps:30\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\nresourcePacks:["vanilla","mod_resources"]\n')
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
variables={'natives_directory':str(PROFILE/'natives-macos-arm64'),'launcher_name':'COD4IsolatedQA','launcher_version':'1','classpath':os.pathsep.join(libs),'library_directory':str(BASE/'libraries'),'classpath_separator':os.pathsep,'version_name':'Dynasty','primary_jar_name':'Dynasty.jar','auth_player_name':'Cod4Mob'+ROLE.title(),'game_directory':str(ROOT),'assets_root':str(BASE/'assets'),'assets_index_name':V.get('assetIndex',{}).get('id','5'),'auth_uuid':hashlib.md5(('OfflinePlayer:Cod4Mob'+ROLE.title()).encode()).hexdigest(),'auth_access_token':'0','clientid':'0','auth_xuid':'0','user_type':'legacy','version_type':'release','resolution_width':'1440','resolution_height':'900'}
offline=bytearray(hashlib.md5(('OfflinePlayer:Cod4Mob'+ROLE.title()).encode()).digest());offline[6]=(offline[6]&15)|48;offline[8]=(offline[8]&63)|128
variables['auth_uuid']=str(uuid.UUID(bytes=bytes(offline))).replace('-','')
def expand(s):return re.sub(r'\$\{(.*?)\}',lambda m:variables[m[1]],s)
def args(group):
 out=[]
 for e in V['arguments'][group]:
  if isinstance(e,str):out.append(expand(e))
  elif allowed(e):out.extend(expand(x) for x in (e['value'] if isinstance(e['value'],list) else [e['value']]))
 return out
command=['/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home/bin/java','-Xmx1800m','-XX:ActiveProcessorCount=2','-Ddynasty.networkqa.output='+str(OUT),'-Ddynasty.networkqa.instance='+str(ROOT),'-Ddynasty.networkqa.role='+ROLE,'-Ddynasty.networkqa.suite='+SUITE]+args('jvm')+[V['mainClass']]+args('game')
manifest['scope']='Two automated real clients: integrated-host local connection plus remote peer TCP; four jars, not full modpack; all state/equipment fixtures server-side, no human survival claim'
manifest['total_mod_jars']=len(list((ROOT/'mods').glob('*.jar')))
(OUT/(ROLE+'-manifest.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
with (OUT/(ROLE+'-client.log')).open('w') as log:
 p=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 (OUT/(ROLE+'-pid.txt')).write_text(str(p.pid));print('Own isolated QA PID',p.pid,'mods',manifest['total_mod_jars'],flush=True)
 result=p.wait();(OUT/(ROLE+'-exit-code.txt')).write_text(str(result));print('exit',result,flush=True)
