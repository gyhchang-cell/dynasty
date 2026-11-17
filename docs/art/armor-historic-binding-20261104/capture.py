"""D24 freeze the missing texture/slot bootstrap and three complete armor geometry families."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil,sys
D=Path(__file__).resolve().parent;R=D.parents[2];PRE=R/'docs/art/armor-historic-compact-reference-20261104'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (D/'class-provenance.json').exists()
    p=json.loads((PRE/'provenance.json').read_text());a=p['archives'][0];jar=Path(a['path']);assert sha(jar)==a['sha256']
    targets=json.loads(next(PRE.glob('texture-requirements-receipt-*.json')).read_text())['targets']
    subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D24不扩大名称数，补齐D23未读的纹理字符串拼接bootstrap、normal/slim选择、模型槽位supplier及三套完整穿戴UV源上下文。保持618名称/211学习组累计，静态对应不计新设计；只读圣甲/铁板甲之外的圣甲、日本轻甲、百夫长甲三套四槽模型及共享provider，不执行mod/开游戏，不动289保护路径或精致稿，不改主清单或共享Jar。'],check=True,capture_output=True)
    save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
    base='org/dawnoftime/armoroftheages/'
    ctx=['registry/ItemRegistry','registry/ModelProviderRegistry','client/ArmorModelProvider','client/ArmorModelProvider$MixedArmorModelProvider','client/AnimatedArmorModelProvider','client/AnimatedArmorModelProvider$AnimatedMixedArmorModelProvider','item/HumanoidArmorItem','item/ForgeHumanoidArmorItem','item/AotAMaterials']
    geo=[f'client/models/{family}/{slot}{name}Model' for family,name in [('holy_armor','HolyArmor'),('japanese_light_armor','JapaneseLightArmor'),('centurion_armor','CenturionArmor')] for slot in ['Head','Chest','Legs','Feet']]
    exe=Path(shutil.which('javap')).resolve();rows=[]
    with zipfile.ZipFile(jar) as z:
        for n in ctx+geo:
            e=base+n+'.class';b=z.read(e);h=hashlib.sha256(b).hexdigest();local=Path('classes')/(h[:12]+'-'+Path(e).name);(D/local).parent.mkdir(exist_ok=True);(D/local).write_bytes(b)
            out=subprocess.check_output([str(exe),'-v','-c','-p',str(D/local)],text=True);text=Path('disassembly')/(Path(e).name+'.txt');(D/text).parent.mkdir(exist_ok=True);(D/text).write_text(out)
            rows.append({'jar':str(jar),'entry':e,'local':str(local),'sha256':h,'disassembly':str(text),'disassembly_sha256':sha(D/text),'scope':'GEOMETRY_UV_CONTEXT' if n in geo else 'TEXTURE_SLOT_CONTEXT'})
    save('class-provenance.json',{'archive':a,'javap':str(exe),'javap_sha256':sha(exe),'classes':rows,'execution_mode':'STATIC_JAVAP_ONLY_NOT_CLASS_LOADING_OR_MOD_EXECUTION'})
    paths={'capture':Path(__file__).resolve(),'prior_progress':PRE/'progress.json','prior_ledger':PRE/'combined-semantic-ledger.json','prior_provenance':PRE/'provenance.json','prior_declarations':PRE/'resource-declarations.json','prior_language':PRE/'language-provenance.json'}
    save('context.json',{k:str(v.relative_to(R)) for k,v in paths.items()}|{k+'_sha256':sha(v) for k,v in paths.items()}|{'selected_complete_families':['holy_armor','japanese_light_armor','centurion_armor'],'new_design_credit':0})
    print('21 exact static class payloads captured; three complete geometry families; no new design credit')
if __name__=='__main__':main()
