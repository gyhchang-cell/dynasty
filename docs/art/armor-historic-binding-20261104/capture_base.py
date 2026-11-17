"""Add missing shared geometry base and vanilla UV implementation sources, without rerunning capture."""
from pathlib import Path
import json,hashlib,subprocess,zipfile
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (D/'additional-class-provenance.json').exists()
    prior=json.loads((D/'class-provenance.json').read_text());jar=Path(prior['archive']['path']);assert sha(jar)==prior['archive']['sha256']
    e='org/dawnoftime/armoroftheages/client/models/ArmorModel.class'
    with zipfile.ZipFile(jar) as z:b=z.read(e)
    h=hashlib.sha256(b).hexdigest();local=Path('classes')/(h[:12]+'-ArmorModel.class');(D/local).write_bytes(b)
    out=subprocess.check_output([prior['javap'],'-v','-c','-p',str(D/local)],text=True);text=Path('disassembly/ArmorModel.class.txt');(D/text).write_text(out)
    row={'jar':str(jar),'entry':e,'local':str(local),'sha256':h,'disassembly':str(text),'disassembly_sha256':sha(D/text),'scope':'SHARED_GEOMETRY_UV_CONTEXT'}
    src=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
    assert sha(src)=='1b3fbc4e77b7523058b8c03ee4c9f8d9db2a6c9bb41f4afc5277f968ad1070e0'
    sources=[]
    with zipfile.ZipFile(src) as z:
        for e in ['net/minecraft/client/model/geom/ModelPart.java','net/minecraft/client/model/geom/builders/CubeDefinition.java','net/minecraft/client/model/geom/builders/CubeListBuilder.java']:
            b=z.read(e);h=hashlib.sha256(b).hexdigest();local=Path('vanilla-source')/(h[:12]+'-'+Path(e).name);(D/local).parent.mkdir(exist_ok=True);(D/local).write_bytes(b);sources.append({'jar':str(src),'entry':e,'local':str(local),'sha256':h})
    save('additional-class-provenance.json',{'capture_base_sha256':sha(Path(__file__)),'class':row,'vanilla_archive':{'path':str(src),'sha256':sha(src)},'vanilla_sources':sources})
    print('Shared ArmorModel and three vanilla UV sources frozen; static only')
if __name__=='__main__':main()
