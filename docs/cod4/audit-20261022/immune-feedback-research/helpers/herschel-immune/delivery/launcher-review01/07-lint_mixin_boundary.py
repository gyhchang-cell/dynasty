"""Reject ordinary classes inside Mixin-reserved packages before any game start."""
from pathlib import Path
import json
import zipfile
import hashlib
import argparse


def inspect(jar):
    errors=[];configs=[]
    with zipfile.ZipFile(jar) as z:
        manifest=z.read('META-INF/MANIFEST.MF').decode()
        # Jar writes continuation lines for long manifest values.
        manifest=manifest.replace('\r\n ','').replace('\n ','')
        names=next(line.split(':',1)[1].strip() for line in manifest.splitlines() if line.startswith('MixinConfigs:')).split(',')
        for name in names:
            config=json.loads(z.read(name.strip()));prefix=config['package'].replace('.','/')+'/'
            registered=[prefix+s.replace('.','/')+'.class' for side in ['mixins','client','server'] for s in config.get(side,[])]
            for item in registered:
                if item not in z.namelist():errors.append({'missing_configured_mixin':item})
            ordinary=[]
            for path in z.namelist():
                if path.startswith(prefix) and path.endswith('.class') and b'Lorg/spongepowered/asm/mixin/Mixin;' not in z.read(path):ordinary.append(path)
            if ordinary:errors.append({'reserved_prefix':prefix,'ordinary_classes':ordinary})
            configs.append({'name':name,'package':config['package'],'registered_classes':registered})
    return {'status':'PASS_MIXIN_PACKAGE_BOUNDARY_ONLY' if not errors else 'FAIL_MIXIN_PACKAGE_BOUNDARY',
        'jar_sha256':hashlib.sha256(Path(jar).read_bytes()).hexdigest(),'configs':configs,'errors':errors,
        'runtime_loading_or_gameplay_verified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('jar',type=Path);p.add_argument('output',type=Path);a=p.parse_args();result=inspect(a.jar)
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['status']);raise SystemExit(bool(result['errors']))
