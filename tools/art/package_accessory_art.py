"""Package separately generated original sprites; only mechanical crop/resize."""
import json
import shutil
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/school-accessories-v2'
def main():
    classes=ROOT/'build/accessory-art';classes.mkdir(parents=True,exist_ok=True)
    subprocess.run(['javac','-d',str(classes),str(ROOT/'tools/art/PackRemasterAssets.java')],check=True)
    for manifest in ['assets.json','remasters.json']:
        p=DOC/manifest
        if not p.exists():continue
        rows=json.loads(p.read_text())
        for row in rows:
            src=DOC/'source'/f'{row["id"]}.png';src.parent.mkdir(parents=True,exist_ok=True)
            if not src.exists():shutil.copy2(row['source'],src)
            target=ROOT/f'src/main/resources/assets/dynasty/textures/item/{row["id"]}.png'
            before=DOC/'before'/target.name
            if row.get('remaster') and not before.exists():
                before.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,before)
            subprocess.run(['java','-cp',str(classes),'PackRemasterAssets','item',str(src),str(target)],check=True)
            after=DOC/'after'/target.name;after.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,after)
            row['project_source']=str(src.relative_to(ROOT));row['texture']=str(target.relative_to(ROOT))
        p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
