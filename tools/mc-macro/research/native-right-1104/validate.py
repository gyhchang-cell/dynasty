"""Offline regression plus actual AppKit event-handler calls, without posting events."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.build/candidates/native-right-1104'
SDK='/Library/Developer/CommandLineTools/SDKs/MacOSX15.5.sdk'
FIXTURE=ROOT/'.build/candidates/cline-audit-20261104/combat-fixture.json'
RESOURCES=ROOT/'.build/candidates/cline-audit-20261104/app/mcPvPmax.app/Contents/Resources'
SWIFTC=['/usr/bin/swiftc','-sdk',SDK,'-swift-version','5']
COMMON=[ROOT/'Sources'/f'{name}.swift' for name in ['F3Model','Sprint','Anchor','Combat']]

def run(name,files,args=(),frameworks=()):
    executable=OUT/(name+'-tests')
    command=SWIFTC+list(map(str,files))+['-o',str(executable)]
    if frameworks:
        command+=['-vfsoverlay',str(ROOT/'.build/sdk-overlay.json')]
        for framework in frameworks:command+=['-framework',framework]
    result=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    (OUT/(name+'-compile.log')).write_text(result.stdout)
    if result.returncode:print(result.stdout);raise RuntimeError(name+' compile failed')
    result=subprocess.run([str(executable),*map(str,args)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    (OUT/(name+'-tests.log')).write_text(result.stdout)
    print(result.stdout,flush=True)
    if result.returncode:raise RuntimeError(name+' checks failed')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for suite in ['Combat','HeldItem','RightIndependence']:
        run(suite,COMMON+[ROOT/f'Tests/{suite}/main.swift'],[FIXTURE])
    run('ModernTelemetry',COMMON+[ROOT/'Sources/ModernTelemetry.swift',ROOT/'Tests/ModernTelemetry/main.swift'],[FIXTURE,RESOURCES])
    run('Sprint',[ROOT/'Sources/Sprint.swift',ROOT/'Tests/ForceSprint/main.swift'])
    run('Inventory',[ROOT/'Sources/InventoryPolicy.swift',ROOT/'Tests/Inventory/main.swift'])
    run('Core',[ROOT/'Sources'/f'{name}.swift' for name in ['Policy','F3Model','InventoryPolicy','GameTelemetry','TellyController']]+[ROOT/'Tests/main.swift'])
    # Reuse the actual app class and both actual event handlers. Exclude ONLY
    # production NSApplication launch; no event tap, timers, game attach or UI.
    main_source=(ROOT/'Sources/main.swift').read_text()
    marker='let app = NSApplication.shared\n'
    if main_source.count(marker)!=1:raise RuntimeError('Unexpected app entry point; do not guess')
    staging=OUT/'event-integration';staging.mkdir(exist_ok=True)
    (staging/'main.swift').write_text(main_source.split(marker)[0]+(ROOT/'Tests/RightIntegration/body.swift').read_text())
    sources=sorted(p for p in (ROOT/'Sources').glob('*.swift') if p.name!='main.swift')
    run('RightIntegration',sources+[staging/'main.swift'],[FIXTURE],['AppKit','ApplicationServices','Carbon','IOKit','Vision','ScreenCaptureKit'])

if __name__=='__main__':
    code=0
    try:main()
    except Exception as error:print(str(error),file=sys.stderr);code=1
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'validation-exit.json').write_text(json.dumps({'exit_code':code,'live_game_input':False,'event_handlers_tested':code==0})+'\n')
    sys.exit(code)