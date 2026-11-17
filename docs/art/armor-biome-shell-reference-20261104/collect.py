"""Read previously unseen chitin/scale four-item families. Freeze original evidence only."""
from pathlib import Path
from io import BytesIO
import json,hashlib,zipfile,subprocess,sys,shutil,importlib.util,re,math
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2]
PRIOR=R/'docs/art/armor-eastern-complete-reference-20261104/combined-semantic-ledger.json'
INV=R/'docs/art/armor-additional-design-reference-20261104/candidate-archive-scan.json'
CHART=R/'docs/art/armor-material-layout-reference-20261104/draw_review_icons.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (D/'provenance.json').exists()
    inv=json.loads(INV.read_text());src=next(a for a in inv['archives'] if 'pathogen_1.3.2_1.19.2.jar' in a['jar']);jar=src['jar'];keys=src['families'];prior=json.loads(PRIOR.read_text());assert len(keys)==17 and not set(keys)&set(prior['reviewed_case_keys'])
    targets=json.loads(next((R/'docs/art/armor-eastern-complete-reference-20261104').glob('texture-requirements-receipt-*.json')).read_text())['targets']
    subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*targets,'--application','D22从591名称/207保守组断点继续：只读17未读Pathogen四槽甲名、68源图与声明、头盔类直接纹理声明及原图集。8环境换色不算8独立设计，专用生物甲不套普通UV；1000适用完整独立设计达标前不制作。保护289路径与认可精致旧稿/实例/共享Jar/声光；静态反汇编不执行模组或开游戏。'],check=True,capture_output=True)
    save('source-baseline.json',json.loads((R/'docs/art/armor-worn-uv-20261102/source-baseline.json').read_text()))
    cases=[];decls=[];worn=[];meta=[];classes=[];bindings=[];javap=Path(shutil.which('javap')).resolve()
    with zipfile.ZipFile(jar) as z:
        def copy(e,folder,png=False):
            b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path(folder)/f'{h[:12]}-{Path(e).name}';(D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);a={'jar':jar,'entry':e,'sha256':h,'local':str(loc)}
            if png:a['size']=list(Image.open(BytesIO(b)).size)
            return a
        for key in keys:
            ns,f=key.split(':');icons=[]
            for part in ['helmet','chestplate','leggings','boots']:
                e=f'assets/{ns}/models/item/{f}_{part}.json';m=json.loads(z.read(e));loc=m['textures']['layer0'];n,t=loc.split(':');entry=f'assets/{n}/textures/{t}.png';icon=copy(entry,'references',True);icons.append(icon);decls.append({'case_key':key,'part':part,'model':copy(e,'declarations'),'texture':icon,'texture_location':loc,'parent':m['parent']})
                if entry+'.mcmeta' in z.namelist():meta.append({'case_key':key,'source':icon,'metadata':copy(entry+'.mcmeta','animation-declarations')})
            cases.append({'case_key':key,'icons':icons,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
            name=''.join(w.capitalize() for w in f.split('_'));e=f'en/predator/pathogenmonsterplague/item/{name}Item$Helmet.class';a=copy(e,'classes');out=subprocess.check_output([str(javap),'-c','-p',str(D/a['local'])],text=True);loc=Path('disassembly')/(name+'Item-Helmet.txt');(D/loc).parent.mkdir(exist_ok=True);(D/loc).write_text(out);a.update(disassembly=str(loc),disassembly_sha256=sha(D/loc));classes.append(a)
            vals=re.findall(r'// String (pathogen:textures/[^\s]+\.png)',out);assert len(set(vals))==1,(key,vals)
            v=vals[0];n,t=v.split(':');entry=f'assets/{n}/{t}';assert entry in z.namelist()
            bindings.append({'case_key':key,'kind':'HELMET_CLASS_DIRECT_TEXTURE_STRING','class_source':a,'declared_texture':v,'archive_entry':entry,'full_player_four_slot_chain_proven':False})
            worn.append({**copy(entry,'worn-references',True),'case_key':key,'binding_proven':False,'role':'HELMET_STATIC_DECLARATION_NOT_ALL_SLOTS_OR_TARGET_UV_PROOF'})
    save('provenance.json',{'archives':[{'path':jar,'sha256':sha(Path(jar))}],'cases':cases,'worn_textures':worn,'production_mutations':0,'status':'PENDING_ACTUAL_VISUAL_REVIEW'})
    save('resource-declarations.json',decls);save('animation-candidates.json',meta);save('static-declarations.json',bindings);save('class-provenance.json',{'javap':str(javap),'javap_sha256':sha(javap),'classes':classes})
    # Source-incomplete external namespace pointers are a failed local candidate, not game failure evidence.
    missing=[];other=next(a for a in inv['archives'] if 'forgotten_civilizations-1.0.2' in a['jar'])
    with zipfile.ZipFile(other['jar']) as z:
        for key in other['families']:
            ns,f=key.split(':')
            for part in ['helmet','chestplate','leggings','boots']:
                e=f'assets/{ns}/models/item/{f}_{part}.json';b=z.read(e);t=json.loads(b)['textures']['layer0'];entry='assets/'+t.replace(':','/textures/')+'.png';assert entry not in z.namelist();h=hashlib.sha256(b).hexdigest();local=Path('unresolved-declarations')/(h[:12]+'-'+Path(e).name);(D/local).parent.mkdir(exist_ok=True);(D/local).write_bytes(b);missing.append({'jar':other['jar'],'entry':e,'local':str(local),'sha256':h,'texture_location':t,'missing_in_this_archive_only':entry,'case_key':key,'part':part})
    save('unresolved-source-candidates.json',{'archive':{'path':other['jar'],'sha256':sha(Path(other['jar']))},'models':missing,'reviewed_reference_credit':0,'warning':'只证明当前归档无所指PNG；未证明依赖包/资源包缺失，也未宣称游戏贴图错误。'})
    paths={'collector':Path(__file__).resolve(),'prior_ledger':PRIOR,'candidate_inventory':INV,'icon_chart_collector':CHART}
    save('collection-context.json',{k:str(p.relative_to(R)) for k,p in paths.items()}|{k+'_sha256':sha(p) for k,p in paths.items()}|{'selected_case_keys':keys})
    assert not meta,'Read icon animation separately if present'
    spec=importlib.util.spec_from_file_location('chart',CHART);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.main()
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
    for page,start in enumerate(range(0,len(worn),3),1):
        group=worn[start:start+3];scales=[min(3,max(1,512//max(a['size']))) for a in group];heights=[max(130,a['size'][1]*s)+35 for a,s in zip(group,scales)];width=max(1250,510+max(a['size'][0]*s for a,s in zip(group,scales))+20);out=Image.new('RGB',(width,55+sum(heights)),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,10),'READ-ONLY HELMET STATIC DECLARED SOURCE ATLAS / NOT ALL SLOTS OR IN-GAME PROOF',font=font,fill='white');y=50
        for a,h,s in zip(group,heights,scales):
            im=Image.open(D/a['local']).convert('RGBA');im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);dr.text((8,y+5),a['case_key'],font=font,fill='white');dr.text((8,y+27),Path(a['entry']).name,font=font,fill='#b7c0c4');dr.text((8,y+49),str(a['size'])+' '+a['sha256'][:12],font=font,fill='#b7c0c4');out.paste(im,(510,y),im);y+=h
        out.save(D/f'worn-{page:02}.png')
    print(json.dumps({'names':len(cases),'icons':len(decls),'native_atlases':len(worn),'static_declarations':len(bindings),'classes':len(classes),'pages':math.ceil(len(cases)/7)+math.ceil(len(worn)/3),'incomplete_source_model_pointers':len(missing)}))
if __name__=='__main__':main()
