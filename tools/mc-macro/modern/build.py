from pathlib import Path
import hashlib,json,subprocess,os
root=Path(__file__).resolve().parents[1]
mc=Path(os.environ.get('MC_MODERN_HOME','/Users/a15356015027/Public/.minecraft'))
version='26.1';jdk=Path('/Library/Java/JavaVirtualMachines/liberica-jdk-25.jdk/Contents/Home/bin')
meta=json.loads((mc/'versions'/version/(version+'.json')).read_text())
libs=[mc/'libraries'/x['downloads']['artifact']['path'] for x in meta['libraries'] if 'artifact' in x.get('downloads',{})]
classpath=os.pathsep.join(map(str,[p for p in libs if p.exists()]+[mc/'versions'/version/(version+'.jar')]))
source=root/'modern/src/local/mcmacro/ModernAgent.java'
v='v'+hashlib.sha256(source.read_bytes()).hexdigest()[:12]
out=root/'.build/modern'/v;out.mkdir(parents=True,exist_ok=True)
(out/'ModernAgent.java').write_text(source.read_text().replace('package local.mcmacro;',f'package local.mcmacro.{v};'))
subprocess.run([str(jdk/'javac'),'-cp',classpath,'-d',str(out/'classes'),str(out/'ModernAgent.java')],check=True)
manifest=out/'MANIFEST.MF';manifest.write_text(f'Manifest-Version: 1.0\nAgent-Class: local.mcmacro.{v}.ModernAgent\nCan-Redefine-Classes: false\nCan-Retransform-Classes: false\n\n')
jar=out/f'modern-agent-{v}.jar'
subprocess.run([str(jdk/'jar'),'cfm',str(jar),str(manifest),'-C',str(out/'classes'),'.'],check=True)
(root/'.build/modern/runtime.json').write_text(json.dumps({'agentJar':jar.name,'version':version,'java':str(jdk/'java')}))
print(jar)
