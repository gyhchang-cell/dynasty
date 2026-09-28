"""Scoped deployment: one verified launcher instance, backups, no saves/options touched."""
import hashlib
import json
import shlex
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
TARGET=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝')

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert TARGET.is_dir() and (TARGET/'mods/dynasty-1.4.0.jar').is_file()
    # macOS ps does not quote arguments containing spaces. shlex alone mistakes
    # "Dynasty 王朝" for two arguments and would miss the running target instance.
    for process in subprocess.check_output(['ps','-axo','pid=,comm='],text=True,errors='replace').splitlines():
        fields=process.strip().split(None,1)
        if len(fields)!=2 or Path(fields[1]).name!='java': continue
        command=subprocess.run(['ps','-ww','-p',fields[0],'-o','command='],capture_output=True,text=True,errors='replace').stdout
        match=re.search(r'--gameDir\s+(.+?)(?=\s+--|$)',command.strip())
        if match and Path(match.group(1).strip('"\'' )).resolve()==TARGET.resolve():
            raise SystemExit('The target game is running. Quit Minecraft before deployment; nothing changed.')
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
    backup=ROOT/'build/deployment-backups'/('growth-'+stamp)
    records=[]
    names=['dynasty-1.4.0.jar','Patchouli-1.20.1-85-FORGE.jar',
           'EquipmentCompare-1.20.1-forge-1.3.7.jar','lootr-forge-1.20-0.7.35.94.jar',
           'ftb-ultimine-forge-2001.1.8.jar','worldedit-mod-7.2.15.jar']
    pairs=[(ROOT/'modpack/mods'/name,Path('mods')/name) for name in names]
    pairs.append((ROOT/'modpack/resourcepacks/dynasty-three-pixel-samples.zip',Path('resourcepacks/dynasty-three-pixel-samples.zip')))
    quest_root=ROOT/'modpack/config/ftbquests/quests'
    pairs += [(source,Path('config/ftbquests/quests')/source.relative_to(quest_root))
              for source in quest_root.rglob('*.snbt')]
    assert all(src.is_file() for src,_ in pairs)
    before=len(list((TARGET/'mods').glob('*.jar')))
    for source,relative in pairs:
        destination=TARGET/relative
        old=digest(destination) if destination.exists() else None
        if old==digest(source): continue
        if old:
            saved=backup/relative
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(destination,saved)
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
        assert digest(source)==digest(destination)
        records.append({'path':str(relative),'before':old,'after':digest(destination)})
    backup.mkdir(parents=True,exist_ok=True)
    receipt={'instance':str(TARGET),'backup':str(backup),'jars_before':before,
             'jars_after':len(list((TARGET/'mods').glob('*.jar'))),'files':records}
    (backup/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='files'},ensure_ascii=False))
    print('Verified changed files:',len(records),'; saves and options untouched.')

if __name__=='__main__': main()
