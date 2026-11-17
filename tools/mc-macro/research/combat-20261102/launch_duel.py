from pathlib import Path
import json,subprocess,os,uuid,sys
root=Path(__file__).resolve().parents[2];mc=Path('/Users/a15356015027/Public/.minecraft');meta=json.loads((mc/'versions/26.1/26.1.json').read_text())
def allowed(rules):
 if not rules:return True
 result=False
 for rule in rules:
  o=rule.get('os',{})
  if o.get('name','osx')!='osx' or o.get('arch','aarch64') not in ('aarch64','arm64') or rule.get('features'):continue
  result=rule['action']=='allow'
 return result
libs=[mc/'libraries'/x['downloads']['artifact']['path'] for x in meta['libraries'] if allowed(x.get('rules')) and 'artifact' in x.get('downloads',{})]
assert all(p.exists() for p in libs)
cp=os.pathsep.join(map(str,libs+[mc/'versions/26.1/26.1.jar']))
for letter in (sys.argv[1:] or ['a','b']):
 assert letter in ['a','b'];game=root/'.build/combat-lan'/('client-'+letter);game.mkdir(parents=True,exist_ok=True)
 if (game/'pid').exists():
  pid=(game/'pid').read_text();r=subprocess.run(['ps','-p',pid,'-o','command='],capture_output=True,text=True)
  if r.returncode==0 and str(game) in r.stdout:raise RuntimeError('test client is already running')
 optionfile=game/'options.txt'
 options=dict(line.split(':',1) for line in optionfile.read_text().splitlines() if ':' in line) if optionfile.exists() else {}
 options.update(dict(line.split(':',1) for line in ('version:4786\nsoundCategory_master:0.0\nsoundCategory_music:0.0\nlang:en_us\nfullscreen:false\nmaxFps:'+('120' if letter=='a' else '40')+'\nrenderDistance:4\nsimulationDistance:4\nentityDistanceScaling:1.0\nguiScale:2\nmouseSensitivity:0.5\nrawMouseInput:false\nautoJump:false\npauseOnLostFocus:false\nshowSubtitles:false').splitlines()))
 if letter=='b':options['key_key.attack']='key.keyboard.k'
 optionfile.write_text(''.join(k+':'+v+'\n' for k,v in options.items()))
 username='mcPvPmax'+letter.upper()
 args=['/Library/Java/JavaVirtualMachines/liberica-jdk-25.jdk/Contents/Home/bin/java','-XstartOnFirstThread','-Xmx1536M','--sun-misc-unsafe-memory-access=allow','--enable-native-access=ALL-UNNAMED','-cp',cp,meta['mainClass'],'--username',username,'--uuid',uuid.uuid3(uuid.NAMESPACE_DNS,'OfflinePlayer:'+username).hex,'--accessToken','0','--version','26.1','--gameDir',str(game),'--assetsDir',str(mc/'assets'),'--assetIndex',meta['assetIndex']['id'],'--width','960','--height','540','--quickPlayMultiplayer','127.0.0.1:25585']
 with (game/'launch.log').open('ab') as log:p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (game/'pid').write_text(str(p.pid));print(letter,p.pid,flush=True)
