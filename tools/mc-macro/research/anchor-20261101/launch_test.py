"""Isolated, muted, offline singleplayer instance. Never reads account tokens."""
from pathlib import Path
import json,subprocess,os,uuid
root=Path(__file__).resolve().parents[2];mc=Path('/Users/a15356015027/Public/.minecraft')
game=root/'.build/anchor-singleplayer';game.mkdir(parents=True,exist_ok=True)
if (game/'pid').exists():
 oldpid=(game/'pid').read_text().strip();old=subprocess.run(['ps','-p',oldpid,'-o','command='],capture_output=True,text=True)
 if old.returncode==0 and str(game) in old.stdout:raise RuntimeError('Owned test instance is already running')
meta=json.loads((mc/'versions/26.1/26.1.json').read_text())
def allowed(rules):
 if not rules:return True
 result=False
 for rule in rules:
  o=rule.get('os',{})
  if o.get('name','osx')!='osx':continue
  if o.get('arch','aarch64') not in ('aarch64','arm64'):continue
  if rule.get('features'):continue
  result=rule['action']=='allow'
 return result
libs=[mc/'libraries'/x['downloads']['artifact']['path'] for x in meta['libraries'] if allowed(x.get('rules')) and 'artifact' in x.get('downloads',{})]
assert all(p.exists() for p in libs),[str(p) for p in libs if not p.exists()]
cp=os.pathsep.join(map(str,libs+[mc/'versions/26.1/26.1.jar']))
options=game/'options.txt'
if not options.exists(): options.write_text('version:4786\nsoundCategory_master:0.0\nsoundCategory_music:0.0\nlang:en_us\nfullscreen:false\nmaxFps:120\nrenderDistance:6\nsimulationDistance:5\nentityDistanceScaling:0.5\nguiScale:2\nmouseSensitivity:0.5\nrawMouseInput:false\nautoJump:false\npauseOnLostFocus:true\nshowSubtitles:false\n')
args=['/Library/Java/JavaVirtualMachines/liberica-jdk-25.jdk/Contents/Home/bin/java','-XstartOnFirstThread','-Xmx2G','--sun-misc-unsafe-memory-access=allow','--enable-native-access=ALL-UNNAMED','-cp',cp,meta['mainClass'],'--username','mcPvPmaxTest','--uuid',uuid.uuid3(uuid.NAMESPACE_DNS,'OfflinePlayer:mcPvPmaxTest').hex,'--accessToken','0','--version','26.1','--gameDir',str(game),'--assetsDir',str(mc/'assets'),'--assetIndex',meta['assetIndex']['id'],'--width','1100','--height','720']
if (game/'saves/mcPvPmax_Anchor_Test/level.dat').exists():args += ['--quickPlaySingleplayer','mcPvPmax_Anchor_Test']
with (game/'launch.log').open('a') as log:
 p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(game/'pid').write_text(str(p.pid));print(json.dumps({'pid':p.pid,'gameDir':str(game)}))
