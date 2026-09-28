"""Verify source parity and package a save-free, checksummed v6 update."""
import hashlib,json,zipfile,shutil,sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    jar=ROOT/'build/libs/dynasty-1.4.0.jar'
    with zipfile.ZipFile(jar) as z:
        for p in (ROOT/'src/main/resources').rglob('*'):
            if not p.is_file(): continue
            name=p.relative_to(ROOT/'src/main/resources').as_posix()
            expected=(ROOT/'build/resources/main'/name).read_bytes() if name in ('META-INF/mods.toml','pack.mcmeta') else p.read_bytes()
            assert z.read(name)==expected, 'Stale build: '+name
    payload={'mods/'+jar.name:jar.read_bytes()}
    staged=ROOT/'modpack/mods'/jar.name
    if staged.read_bytes()!=jar.read_bytes():
        backup=ROOT/'build/backups'/('visual-v6-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
        backup.mkdir(parents=True,exist_ok=False)
        shutil.copy2(staged,backup/staged.name)
        shutil.copy2(jar,staged)
    quests=ROOT/'modpack/config/ftbquests/quests'
    payload.update({'config/ftbquests/quests/'+p.relative_to(quests).as_posix():p.read_bytes() for p in quests.rglob('*.snbt')})
    payload['update-manifest.json']=json.dumps({'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in payload.items()}},indent=2).encode()
    dest=ROOT/'dist/dynasty-visual-feedback-v6-update.zip'
    if '--output' in sys.argv:
        dest=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload.items():z.writestr(name,data)
    with zipfile.ZipFile(dest) as z: assert z.testzip() is None
    print(dest)
if __name__=='__main__':main()
