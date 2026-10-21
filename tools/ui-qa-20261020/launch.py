"""Offline isolated production launcher. Never reads a user's live JVM or credentials."""
from pathlib import Path
import os,json,zipfile,shutil,subprocess,re,uuid,hashlib,sys
R=Path(__file__).resolve().parents[2];O=R/'docs/ui-fixes-20261020';BASE=Path('/Users/a15356015027/Public/.minecraft');PROFILE=BASE/'versions/Dynasty';ROOT=R/('build/ui-client-20261020-'+sys.argv[1]);OUT=O/('native-'+sys.argv[1]);OUT.mkdir(exist_ok=True)
ROOT.mkdir(exist_ok=True)
OWNED=['client/DynastyHealthHud','client/DynastyVitalsOverlay','client/DynastyTooltips','client/DynastyItemInfo','client/DynastyItemUsage','client/DynastySearchAliases','client/DynastySearchJei','client/DynastyAccessorySources','DynastyTrinketTips','army/ArmyRosterScreen']
def patch():
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
  d={n:z.read(n) for n in z.namelist() if any(n=='com/dynasty/'+k+'.class' or n.startswith('com/dynasty/'+k+'$') for k in OWNED)}
 for p in (R/'src/main/resources/assets').rglob('*'):
  if p.is_file() and (p.as_posix().endswith(('lang/zh_cn.json','lang/en_us.json','dynasty/search_aliases.json','dynasty/accessory_sources.json','minecraft/atlases/blocks.json','dynasty/models/block/dungeon_masonry_5.json')) or '/patchouli_books/' in p.as_posix() or '/textures/gui/quests/journey/' in p.as_posix()):d[p.relative_to(R/'src/main/resources').as_posix()]=p.read_bytes()
 return d
PATCH=patch()
(O/'patch-members.json').write_text(json.dumps(list(PATCH),indent=2))
for folder in ['mods','config','defaultconfigs','resourcepacks']:
 shutil.copytree(PROFILE/folder,ROOT/folder,dirs_exist_ok=True) if (PROFILE/folder).exists() else None
for p in (ROOT/'mods').glob('*.jar'):
 if any(s in p.name.lower() for s in ['overflowingbars','playtest-helper','dynasty-audit','quest-qa']):p.unlink()
jar=ROOT/'mods/dynasty-1.4.0.jar';tmp=jar.with_suffix('.pending')
with zipfile.ZipFile(jar) as z,zipfile.ZipFile(tmp,'w') as w:
 for entry in z.infolist():w.writestr(entry,PATCH.get(entry.filename,z.read(entry.filename)))
 for k,v in PATCH.items():
  if k not in z.namelist():w.writestr(k,v,compress_type=zipfile.ZIP_DEFLATED)
os.replace(tmp,jar)
shutil.copy2(R/'libs/armorpointspp-forge-1.20-3.1.1.jar',ROOT/'mods')
shutil.copy2(R/'modpack/config/armorpointspp-client.toml',ROOT/'config')
shutil.copy2(R/'build/libs/dynasty-audit-ui-1.4.0.jar',ROOT/'mods')
shutil.copytree(R/'modpack/config/ftbquests',ROOT/'config/ftbquests',dirs_exist_ok=True)
shutil.copy2(R/'modpack/resourcepacks/dynasty-quest-guides-v3.zip',ROOT/'resourcepacks')
(ROOT/'options.txt').write_text('soundCategory_master:0.0\npauseOnLostFocus:false\nlang:zh_cn\nguiScale:3\ngamma:0.0\nmaxFps:30\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\nresourcePacks:["vanilla","mod_resources"]\n')
V=json.loads((PROFILE/'Dynasty.json').read_text());features={'has_custom_resolution':True}
def allowed(x):
 if 'rules' not in x:return True
 result=False
 for rule in x['rules']:
  osr=rule.get('os',{});matches=(not osr.get('name') or osr['name']=='osx') and (not osr.get('arch') or osr['arch'] in ['arm64','aarch64']) and all(features.get(k,False)==v for k,v in rule.get('features',{}).items())
  if matches:result=rule['action']=='allow'
 return result
libs=[]
for entry in V['libraries']:
 if not allowed(entry):continue
 artifact=entry.get('downloads',{}).get('artifact',{}).get('path')
 if not artifact:
  group,name,ver,*classifier=entry['name'].split(':');artifact=group.replace('.','/')+'/'+name+'/'+ver+'/'+name+'-'+ver+('-'+classifier[0] if classifier else '')+'.jar'
 p=BASE/'libraries'/artifact
 if p.exists():libs.append(str(p))
 else:raise FileNotFoundError(p)
libs.append(str(PROFILE/'Dynasty.jar'))
variables={'natives_directory':str(PROFILE/'natives-macos-arm64'),'launcher_name':'DynastyIsolatedQA','launcher_version':'1','classpath':os.pathsep.join(libs),'library_directory':str(BASE/'libraries'),'classpath_separator':os.pathsep,'version_name':'Dynasty','primary_jar_name':'Dynasty.jar','auth_player_name':'AuditPlayer','game_directory':str(ROOT),'assets_root':str(BASE/'assets'),'assets_index_name':V.get('assetIndex',{}).get('id','5'),'auth_uuid':uuid.uuid3(uuid.NAMESPACE_DNS,'OfflinePlayer:AuditPlayer').hex,'auth_access_token':'0','clientid':'0','auth_xuid':'0','user_type':'legacy','version_type':'release','resolution_width':'1280','resolution_height':'800'}
def expand(s):return re.sub(r'\$\{(.*?)\}',lambda m:variables[m[1]],s)
def args(group):
 out=[]
 for entry in V['arguments'][group]:
  if isinstance(entry,str):out.append(expand(entry))
  elif allowed(entry):out.extend(expand(x) for x in (entry['value'] if isinstance(entry['value'],list) else [entry['value']]))
 return out
command=['/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home/bin/java','-Xmx3G','-Ddynasty.audit.onlyFigures='+str(sys.argv[1]=='figures').lower(),'-XX:ActiveProcessorCount=2','-Ddynasty.audit.output='+str(OUT),'-Ddynasty.audit.figures='+('true' if sys.argv[1] in ('first','figures') else 'false')]+args('jvm')+[V['mainClass']]+args('game')
(O/('runtime-'+sys.argv[1]+'.json')).write_text(json.dumps({'profile':str(ROOT),'mods':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'mods').glob('*.jar')},'offline_identity':True},indent=2))
with (OUT/'client.log').open('w') as log:
 p=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);(OUT/'pid.txt').write_text(str(p.pid));print('Isolated full-pack QA PID',p.pid,'mods',len(list((ROOT/'mods').glob('*.jar'))),flush=True);print('exit',p.wait(),flush=True)
