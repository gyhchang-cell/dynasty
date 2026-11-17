"""D23 exact original four-item models with head/chest/legs/feet names, not helmet suffix."""
from pathlib import Path
from io import BytesIO
import json,hashlib,zipfile,subprocess,sys,shutil,importlib.util,math
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2]
PRIOR=R/'docs/art/armor-biome-shell-reference-20261104/combined-semantic-ledger.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (D/'provenance.json').exists()
    jar=next(Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods').glob('*Armor of the Ages*.jar'))
    prior=json.loads(PRIOR.read_text());targets=json.loads(next((R/'docs/art/armor-biome-shell-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
    subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D23复用608已读名称/208保守学习组，补看10未读ArmorOfTheAges完整四件原生16px图标和20常规/细臂图集。源图本身16px不等于将用户原稿压16；不改用户原图，不复制他人像素。常规/细臂不重复计整套；未达1000适用完整独立设计前不制作，保护289路径、认可精致旧稿、实例和共享Jar/声光。'],check=True,capture_output=True)
    save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
    cases=[];decls=[];worn=[];meta=[];classes=[];javap=Path(shutil.which('javap')).resolve()
    with zipfile.ZipFile(jar) as z:
        def copy(e,folder,png=False):
            b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path(folder)/f'{h[:12]}-{Path(e).name}';(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);a={'jar':str(jar),'entry':e,'sha256':h,'local':str(loc)}
            if png:a['size']=list(Image.open(BytesIO(b)).size)
            return a
        lang=copy('assets/armoroftheages/lang/zh_cn.json','language-declaration');labels=json.loads((D/lang['local']).read_text())
        names=sorted(n.split('/')[-1][:-len('_head.json')] for n in z.namelist() if n.startswith('assets/armoroftheages/models/item/') and n.endswith('_head.json'))
        assert len(names)==10
        for f in names:
            key='armoroftheages:'+f;assert key not in prior['reviewed_case_keys'];icons=[]
            for part,slot in [('helmet','head'),('chestplate','chest'),('leggings','legs'),('boots','feet')]:
                e=f'assets/armoroftheages/models/item/{f}_{slot}.json';m=json.loads(z.read(e));loc=m['textures']['layer0'];ns,t=loc.split(':');entry=f'assets/{ns}/textures/{t}.png';icon=copy(entry,'references',True);assert icon['size']==[16,16];icons.append(icon);decls.append({'case_key':key,'part':part,'source_slot':slot,'model':copy(e,'declarations'),'texture':icon,'texture_location':loc,'parent':m['parent'],'label':labels.get(f'item.armoroftheages.{f}_{slot}')})
                if entry+'.mcmeta' in z.namelist():meta.append({'case_key':key,'source':icon,'metadata':copy(entry+'.mcmeta','animation-declarations')})
            cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
            for suffix in ['', '_slim']:
                worn.append({**copy(f'assets/armoroftheages/textures/models/armor/{f}{suffix}.png','worn-references',True),'case_key':key,'variant':'slim' if suffix else 'normal','binding_proven':False,'role':'NATIVE_NAMED_CANDIDATE_NOT_FULL_RUNTIME_OR_STANDARD_PLAYER_UV_PROOF'})
        for e in ['org/dawnoftime/armoroftheages/registry/ModelProviderRegistry.class','org/dawnoftime/armoroftheages/registry/ItemRegistry.class','org/dawnoftime/armoroftheages/client/ArmorModelProvider.class','org/dawnoftime/armoroftheages/item/HumanoidArmorItem.class','org/dawnoftime/armoroftheages/item/ForgeHumanoidArmorItem.class']:
            a=copy(e,'classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/a['local'])],text=True);loc=Path('disassembly')/(Path(e).name+'.txt');(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=str(loc),disassembly_sha256=sha(D/loc));classes.append(a)
    save('provenance.json',{'archives':[{'path':str(jar),'sha256':sha(jar)}],'cases':cases,'worn_textures':worn,'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
    save('resource-declarations.json',decls);save('animation-candidates.json',meta);save('class-provenance.json',{'javap':str(javap),'javap_sha256':sha(javap),'classes':classes});save('language-provenance.json',lang)
    paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'icon_chart_collector':CHART}
    save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':[a['case_key'] for a in cases]})
    assert not meta
    spec=importlib.util.spec_from_file_location('chart',CHART);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.main()
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
    for page,start in enumerate(range(0,len(worn),4),1):
        group=worn[start:start+4];scales=[3]*len(group);heights=[max(130,a['size'][1]*s)+35 for a,s in zip(group,scales)];out=Image.new('RGB',(1350,55+sum(heights)),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,10),'READ-ONLY SOURCE NORMAL / SLIM VARIANTS / ONE DESIGN PER SET / NOT GAME',font=font,fill='white');y=50
        for a,h,s in zip(group,heights,scales):
            im=Image.open(D/a['local']).convert('RGBA');im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);dr.text((8,y+5),a['case_key']+' / '+a['variant'],font=font,fill='white');dr.text((8,y+27),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4');out.paste(im,(510,y),im);y+=h
        out.save(D/f'worn-{page:02}.png')
    print(json.dumps({'names':len(cases),'icons':len(decls),'normal_and_slim_atlases':len(worn),'static_context_classes':len(classes),'pages':math.ceil(len(cases)/7)+math.ceil(len(worn)/4)}))
if __name__=='__main__':main()
