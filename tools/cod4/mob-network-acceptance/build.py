from pathlib import Path
import hashlib,zipfile,subprocess,os,sys,json
R=Path(__file__).resolve().parents[3];B=R/'build/cod4-mob-network-20261023';O=R/'docs/cod4/audit-20261022/mob-network-acceptance'
main=R/'build/cod4-audit-20261022/verified-gradle/libs/dynasty-1.4.0.jar'
assert hashlib.sha256(main.read_bytes()).hexdigest()=='ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b'
B.mkdir(parents=True,exist_ok=True);src=R/'build/cod4-network-20261022/compile-dynasty';files=list(src.rglob('*.class'));assert files
with zipfile.ZipFile(B/'compile-dynasty.jar','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(src))
(B/'compile-class-hashes.json').write_text(json.dumps({str(f.relative_to(src)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
env=os.environ.copy();env['JAVA_HOME']='/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home'
with (O/(sys.argv[1] if len(sys.argv)>1 else 'build.log')).open('w') as log:
 subprocess.run(['./gradlew','--offline','--no-daemon','--max-workers=2','--project-cache-dir',str(B/'project-cache'),'-I',str(R/'tools/cod4/mob-network-acceptance/qa.init.gradle'),'mobNetworkAcceptanceJar','reobfMobNetworkAcceptanceJar'],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
print('Private QA Jar built; fixed production Jar unchanged')
