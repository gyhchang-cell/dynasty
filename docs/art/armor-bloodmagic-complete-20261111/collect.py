from pathlib import Path
import json,zipfile,hashlib
D=Path(__file__).resolve().parent;P=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[血魔法] bloodmagic-1.20.1-3.3.7-49.jar')
def main():
 z=zipfile.ZipFile(P);names=[]
 for n in z.namelist():
  if n in [f'assets/bloodmagic/textures/item/living{s}.png' for s in ['helmet','plate','leggings','boots']]+[f'assets/bloodmagic/models/item/living{s}.json' for s in ['helmet','plate','leggings','boots']]+[f'assets/bloodmagic/models/armor/livingarmour_layer_{i}.png' for i in [1,2]]:names.append(n)
  if n in ['wayoftime/bloodmagic/common/item/ItemLivingArmor.class','wayoftime/bloodmagic/common/item/BloodMagicItems.class','wayoftime/bloodmagic/core/RegistrarBloodMagic.class']:names.append(n)
 rows=[]
 for n in names:
  p=D/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);b=z.read(n);p.write_bytes(b);rows.append({'entry':n,'local':str(p.relative_to(D)),'sha256':hashlib.sha256(b).hexdigest()})
 (D/'provenance.json').write_text(json.dumps({'archive':str(P),'archive_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'files':rows,'sentient_model_item_json_entries':[n for n in z.namelist() if '/models/item/' in n and n.endswith('.json') and 'sentient' in n.lower()],'sentient_class_entries':[n for n in z.namelist() if n.endswith('.class') and 'sentient' in n.lower()],'production_changes':0},indent=2)+'\n');print(len(rows),'fixed local entries')
if __name__=='__main__':main()
