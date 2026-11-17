"""D32 fixed official Minecraft1.19.2 native bytecode and Mojang mappings; no execution."""
from pathlib import Path
import json,hashlib,re,zipfile,subprocess
D=Path(__file__).resolve().parent
NAMES=['net.minecraft.client.model.HumanoidModel','net.minecraft.client.model.geom.ModelPart$Cube','net.minecraft.client.model.geom.LayerDefinitions','net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer','net.minecraft.client.model.geom.builders.CubeListBuilder','net.minecraft.client.model.geom.builders.CubeDeformation','net.minecraft.client.model.geom.PartPose','net.minecraft.client.model.geom.builders.PartDefinition','net.minecraft.client.model.geom.builders.MeshDefinition']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 mp=D/'mojang-1.19.2-client-mappings.txt';b=mp.read_bytes();assert len(b)==7236064 and hashlib.sha1(b).hexdigest()=='8e8c9be5dc27802caba47053d4fdea328f7f89bd';s=mp.read_text();entries=[];jar=Path('/Users/a15356015027/Public/.minecraft/versions/【Abyss of Fear】恐惧深渊 v0.2.1/【Abyss of Fear】恐惧深渊 v0.2.1.jar');assert hashlib.sha1(jar.read_bytes()).hexdigest()=='055b30d860ead928cba3849ba920c88b6950b654';jp=Path('/Users/a15356015027/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/javap')
 with zipfile.ZipFile(jar) as z:
  version=json.loads(z.read('version.json'));assert version['id']=='1.19.2'
  for name in NAMES:
   m=re.search(r'^'+re.escape(name)+r' -> ([^:]+):\n(.*?)(?=^\S|\Z)',s,re.M|re.S);assert m,name;ob=m[1];data=z.read(ob+'.class');h=hashlib.sha256(data).hexdigest();loc='classes/'+h[:12]+'-'+name.split('.')[-1]+'.class';(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_bytes(data);out=subprocess.check_output([str(jp),'-c','-p',str(D/loc)],text=True);dis='disassembly/'+name.split('.')[-1]+'.txt';(D/dis).parent.mkdir(exist_ok=True);(D/dis).write_text(out);entries.append({'name':name,'obfuscated_name':ob,'mapping_excerpt':m[0],'entry':ob+'.class','local':loc,'sha256':h,'disassembly':dis,'disassembly_sha256':sha(D/dis)})
 absent='net.minecraft.client.model.HumanoidArmorModel ->' not in s;assert absent
 result={'archive':str(jar),'archive_sha1':hashlib.sha1(jar.read_bytes()).hexdigest(),'archive_sha256':sha(jar),'internal_version':version,'mapping_file':mp.name,'mapping_sha256':sha(mp),'classes':entries,'absent_1_19_HumanoidArmorModel':absent,'javap':str(jp),'javap_sha256':sha(jp),'game_starts':0,'production_changes':0}
 (D/'native-source-collection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Nine pinned native classes; version1.19.2 confirmed; newer HumanoidArmorModel absent.')
if __name__=='__main__':main()
