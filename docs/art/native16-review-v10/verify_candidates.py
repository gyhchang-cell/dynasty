"""Read-only resource verification; writes this review's manifest/report/zip only.
No builds, generators outside this review, installation, or game launch.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json, hashlib, copy
from PIL import Image

DOC=Path(__file__).resolve().parent
ROOT=DOC.parents[2]
LIVE=ROOT/'src/main/resources/assets'
CANDIDATE=DOC/'candidate'
BEFORE=DOC/'before/assets'
VANILLA=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):(DOC/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def split(ref):return ref.split(':',1) if ':' in ref else ('minecraft',ref)

def main():
    original=json.loads((DOC/'baseline-resources.json').read_text())
    for name,row in original.items():
        assert sha(ROOT/name)==row['sha256'],f'Existing source changed: {name}'
        assert sha(DOC/row['backup'])==row['sha256'],f'Backup mismatch: {name}'
    candidates=sorted((CANDIDATE/'assets').rglob('*'))
    records=[]
    images=[]
    for p in candidates:
        if not p.is_file():continue
        rel=p.relative_to(CANDIDATE)
        dest=ROOT/'src/main/resources'/rel
        old=original.get(str(dest.relative_to(ROOT)))
        rec={'candidate':str(p.relative_to(DOC)),'target_if_approved':str(dest.relative_to(ROOT)),
             'status':'review_only_not_installed','sha256':sha(p),
             'existing_sha256':old['sha256'] if old else None,
             'backup':old['backup'] if old else None}
        if p.suffix=='.png':
            im=Image.open(p).convert('RGBA')
            assert im.size==(16,16),(p,im.size)
            assert im.getchannel('A').getextrema()==(255,255),p
            colors=len(im.getcolors(256));assert colors<=12,(p,colors)
            assert not Path(str(p)+'.mcmeta').exists(),'This batch is static'
            rec.update(size=[16,16],colors=colors,alpha=[255],animation=False)
            images.append(rec)
        records.append(rec)

    z=ZipFile(VANILLA)
    used={}
    def fetch(ref,kind,suffix):
        ns,name=split(ref);rel=f'{ns}/{kind}/{name}{suffix}'
        for root in [CANDIDATE/'assets',LIVE]:
            p=root/rel
            if p.exists():
                used[f'{kind}:{ref}']=str(p.relative_to(ROOT))
                return p.read_bytes()
        name='assets/'+rel
        assert name in z.namelist(),f'Missing resource {name}'
        used[f'{kind}:{ref}']='vanilla_1.20.1:'+name
        return z.read(name)
    def model(ref,seen=()):
        assert ref not in seen,f'Parent cycle: {seen}'
        own=json.loads(fetch(ref,'models','.json'))
        parent=model(own['parent'],(*seen,ref)) if 'parent' in own else {}
        return {**parent,**own,'textures':{**parent.get('textures',{}),**own.get('textures',{})}}
    def check_model(ref):
        obj=model(ref)
        def texture(value):
            seen=set()
            while value.startswith('#'):
                assert value not in seen,f'Texture alias cycle: {value}'
                seen.add(value);value=obj['textures'][value[1:]]
            fetch(value,'textures','.png')
        for value in obj.get('textures',{}).values():texture(value)
        for e in obj.get('elements',[]):
            for f in e['faces'].values():texture(f['texture'])
        return obj
    ids=['marble_block','jade_ore','jade_mending_forge','dragon_crystal_ore']
    impacted=['herbal_basin']
    for tid in ids+impacted:
        states=json.loads(fetch('dynasty:'+tid,'blockstates','.json'))
        for value in states['variants'].values():
            for variant in value if isinstance(value,list) else [value]:check_model(variant['model'])
        check_model('dynasty:item/'+tid)
    before=json.loads((BEFORE/'dynasty/models/block/jade_mending_forge.json').read_text())
    after=json.loads((CANDIDATE/'assets/dynasty/models/block/jade_mending_forge.json').read_text())
    def without_textures(value):
        if isinstance(value,dict):return {k:without_textures(v) for k,v in value.items() if k not in ('texture','textures')}
        if isinstance(value,list):return [without_textures(v) for v in value]
        return value
    assert without_textures(before)==without_textures(after),'Geometry/UV changed'
    assert [e['faces']['up']['texture'] for e in after['elements']]==['#all','#all','#top']
    active=json.loads((CANDIDATE/'assets/dynasty/models/block/jade_mending_forge_active.json').read_text())
    assert set(active)=={'parent','textures'} and active['parent']=='dynasty:block/jade_mending_forge'
    assert set(active['textures'])=={'front','top'}
    oldstate=json.loads((BEFORE/'dynasty/blockstates/jade_mending_forge.json').read_text())
    state=json.loads((CANDIDATE/'assets/dynasty/blockstates/jade_mending_forge.json').read_text())
    expected=copy.deepcopy(oldstate)
    for key,value in expected['variants'].items():
        if 'lit=true' in key:value['model']='dynasty:block/jade_mending_forge_active'
    assert state==expected and len(state['variants'])==8
    differences={}
    for name,expected_coords in [
        ('front',{(x,y) for x in (7,8) for y in (8,9,10)}),
        ('top',{(x,y) for x in (1,14) for y in (6,7,8,9)})]:
        stem=CANDIDATE/'assets/dynasty/textures/block'/('jade_mending_forge_'+name)
        a=Image.open(str(stem)+'.png');b=Image.open(str(stem)+'_active.png')
        changed={(x,y) for x in range(16) for y in range(16) if a.getpixel((x,y))!=b.getpixel((x,y))}
        assert changed==expected_coords,(name,changed)
        differences[name]={'changed_pixels':len(changed),'coordinates':sorted(changed)}
    version=json.loads(z.read('version.json'))
    pack={'pack':{'pack_format':version['pack_version']['resource'],
        'description':'Dynasty native16 v10 REVIEW ONLY / 4 direct IDs + shared herbal basin stone'}}
    (CANDIDATE/'pack.mcmeta').write_text(json.dumps(pack,ensure_ascii=False,indent=2)+'\n')
    with ZipFile(DOC/'dynasty-native16-v10-REVIEW-ONLY.zip','w',ZIP_DEFLATED) as packzip:
        for p in sorted(CANDIDATE.rglob('*')):
            if p.is_file():packzip.write(p,p.relative_to(CANDIDATE))
    report={'result':'PASS','status':'review_only_not_installed','ids':ids,
        'indirect_shared_material_impact':{'dynasty:herbal_basin':'Uses dynasty:block/marble_block; appearance changes only if candidate enabled. Geometry, UV, jade band, state and behavior unchanged.'},
        'png_count':len(images),'json_count':len(records)-len(images),'all_png':'native 16x16, opaque, static',
        'colors_per_surface':{Path(r['candidate']).stem:r['colors'] for r in images},
        'backups_match':len(original),'existing_sources_match_baseline':len(original),
        'model_geometry_uv_unchanged':True,'forge_facing_lit_variants':8,
        'state_changes':differences,'resolved_references':used,
        'pack_format_source':'Minecraft '+version['id']+' version.json, resource pack version '+str(pack['pack']['pack_format']),
        'in_game_test':False,'real_emission_render_test':False,
        'limitations':['Offline previews are not runtime screenshots.',
            'Existing Java block light level 10 while lit is unchanged; brighter texels do not prove emissive rendering.',
            'v9 legacy verifier targets frozen v9 hashes and old JAR; not applicable to uninstalled review candidates.']}
    write('candidate-manifest.json',records);write('verification.json',report)
    print(f'PASS: {len(images)} PNG / {len(records)-len(images)} JSON; {len(original)} original resources unchanged; no installation.')

if __name__=='__main__':main()
