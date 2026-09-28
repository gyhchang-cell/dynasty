"""Copy original generated artwork and mechanically resize it; never paint replacement assets."""
import json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/realm-remaster-v4'
def main():
 classes=ROOT/'build/realm-art';classes.mkdir(parents=True,exist_ok=True)
 subprocess.run(['javac','-d',str(classes),str(ROOT/'tools/art/PackRemasterAssets.java')],check=True)
 for manifest,kind in [('assets.json','block'),('weapons.json','item'),('skins.json','entity')]:
  rows=json.loads((DOC/manifest).read_text())
  for row in rows:
   local=DOC/'source'/f'{row["id"]}.png';local.parent.mkdir(parents=True,exist_ok=True)
   if not local.exists(): shutil.copy2(row['source'],local)
   target=ROOT/f'src/main/resources/assets/dynasty/textures/{kind}/{row["id"]}.png'
   mode='skin' if kind=='entity' else ('item-fixed' if '_bow' in row['id'] or row['id'].startswith('chang_gong') else kind)
   subprocess.run(['java','-cp',str(classes),'PackRemasterAssets',mode,str(local),str(target)],check=True)
   row['project_source']=str(local.relative_to(ROOT));row['texture']=str(target.relative_to(ROOT))
  (DOC/manifest).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
