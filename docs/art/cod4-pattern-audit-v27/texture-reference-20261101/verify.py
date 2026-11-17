"""Evidence consistency only; never an automatic visual-quality or study-credit judge."""
from pathlib import Path
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from PIL import Image, ImageOps

D=Path(__file__).resolve().parent
R=D.parents[3]
errors=[];viewed=0;proposals=0;assets=0;batch_summary=[]
archive_hashes={}
origin_entries_checked=0
references={};representatives=[]
def check_archive_entry(jar,entry,expected):
    global origin_entries_checked
    try:
        with zipfile.ZipFile(jar) as z:
            actual=hashlib.sha256(z.read(entry)).hexdigest()
        origin_entries_checked+=1
        if actual!=expected:errors.append('Archive entry does not match extracted file: '+jar+' / '+entry)
    except (KeyError,FileNotFoundError,zipfile.BadZipFile) as exc:
        errors.append('Unreadable exact archive entry: '+jar+' / '+entry+' / '+str(exc))
for path in sorted(D.glob('review-batch-*.json')):
    doc=json.loads(path.read_text());actual_proposals=0;actual_pngs=0
    for row in doc['rows']:
        ref=row.get('reference_id')
        if ref:
            if ref in references:errors.append('Repeated visual reference ID: '+ref)
            references[ref]=row['semantic_family']
            representatives.append((ref,row.get('family_representative'),row['semantic_family']))
        if not row.get('observation_zh') or not row.get('limitation'):errors.append('Missing observation/limit: '+path.name+' '+str(ref))
        actual_proposals+=row['distinct_family_proposed_credit']
        sheet=row.get('inspected_detail_view',row.get('inspection_sheet'))
        if sheet and not (R/sheet).is_file():errors.append('Missing sheet: '+sheet)
        for asset in row.get('assets',[row]):
            p=R/asset['local_path'];actual_pngs+=1
            if not p.is_file():errors.append('Missing PNG: '+str(p));continue
            data=p.read_bytes()
            if hashlib.sha256(data).hexdigest()!=asset['sha256']:errors.append('PNG SHA mismatch: '+str(p))
            if asset.get('git_blob_sha'):
                h=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                if h!=asset['git_blob_sha']:errors.append('Git blob mismatch: '+str(p))
            if asset.get('jar') and asset.get('jar_sha256'):
                jar=asset['jar']
                if jar not in archive_hashes:
                    archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
                if archive_hashes[jar]!=asset['jar_sha256']:errors.append('Archive changed: '+jar)
                check_archive_entry(jar,asset['path'],asset['sha256'])
            if asset.get('rgba_sha256'):
                rgba=Image.open(p).convert('RGBA')
                if hashlib.sha256(rgba.tobytes()).hexdigest()!=asset['rgba_sha256']:errors.append('Decoded RGBA mismatch: '+str(p))
            Image.open(p).verify()
    if actual_pngs!=doc['viewed_pngs']:errors.append('Batch viewed count mismatch: '+path.name)
    if actual_proposals!=doc['proposed_distinct_design_families']:errors.append('Batch family sum mismatch: '+path.name)
    if doc['coordinator_accepted_new_visual_credit']!=0 or doc['production_gate_met'] is not False:errors.append('Unauthorized credit/gate claim: '+path.name)
    viewed+=actual_pngs;proposals+=actual_proposals
    batch_summary.append({'batch':path.name,'pngs_opened':actual_pngs,'proposed_families':actual_proposals})
for ref,rep,family in representatives:
    if rep in references and references[rep]!=family:errors.append('Family representative points to different family: '+ref+' -> '+rep)
for model in json.loads((D/'uv-model-supplement.json').read_text())['rows']:
    if hashlib.sha256((R/model['path']).read_bytes()).hexdigest()!=model['sha256']:errors.append('Model SHA mismatch: '+model['path'])
prior_opened=0
for name in ['prior-case-semantic-review.json','prior-batch07-semantic-review.json','prior-batch11-semantic-review.json','prior-batches15-16-semantic-review.json','prior-batch18-semantic-review.json','prior-batch20-semantic-review.json','prior-batch21-semantic-review.json']:
    prior=json.loads((D/name).read_text())
    for row in prior['rows']:
        if row.get('accepted_credit')!=0:errors.append('Prior reuse improperly credited: '+row['case'])
        if 'prior_local_png' in row:
            prior_opened+=1
            if hashlib.sha256((R/row['prior_local_png']).read_bytes()).hexdigest()!=row['prior']['sha256']:errors.append('Prior PNG changed: '+row['case'])
            if not (R/row['comparison_sheet']).is_file():errors.append('Prior sheet missing: '+row['case'])
            if not row.get('observation_zh'):errors.append('Missing manual prior observation: '+row['case'])
            jar=row['prior']['jar']
            if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
            if archive_hashes[jar]!=row['prior_jar_sha256']:errors.append('Prior archive changed: '+row['case'])
            check_archive_entry(jar,row['prior'].get('entry',row['prior'].get('texture')),row['prior']['sha256'])
            current_item=row.get('current_exact_item_source')
            if current_item:
                check_archive_entry(current_item['jar'],current_item['entry'],current_item['sha256'])
                if current_item['sha256']!=row['prior']['sha256']:errors.append('Current/prior exact item differs')
            animation=row.get('prior_animation_source')
            if animation:
                if hashlib.sha256((R/animation['local_path']).read_bytes()).hexdigest()!=animation['sha256']:errors.append('Prior animation metadata changed: '+row['case'])
                check_archive_entry(jar,animation['entry'],animation['sha256'])
bindings=json.loads((D/'current-weapon-uv-bindings.json').read_text())
for row in bindings['rows']:
    for key in ['model','png']:
        if hashlib.sha256((R/row[key]).read_bytes()).hexdigest()!=row[key+'_sha256']:errors.append('Current binding source changed: '+row[key])
uv_crops=json.loads((D/'uv-layer-crops.json').read_text())
uv_review=json.loads((D/'uv-layer-manual-review.json').read_text())
if set(uv_crops['sheets'])!={r['sheet'] for r in uv_review['rows']}:errors.append('UV layer review sheet coverage mismatch')
if uv_review['new_accepted_visual_credit']!=0 or uv_review['production_changes']!=0:errors.append('Unauthorized UV crop credit')
sample_count=0;zero_count=0
for row in uv_crops['rows']:
    for kind in ['model','texture']:
        if hashlib.sha256((R/row[kind]).read_bytes()).hexdigest()!=row[kind+'_sha256']:errors.append('UV source changed: '+row[kind])
    if not (R/row['inspection_sheet']).is_file():errors.append('Missing UV crop sheet: '+row['inspection_sheet'])
    im=Image.open(R/row['texture']).convert('RGBA')
    for face in row['faces']:
        if face['status']!='SIGNED_INTEGER_CROP':
            zero_count+=1
            if not 0 in face['uv_size']:errors.append('Unsampled nonzero UV face: '+str(face))
            continue
        sample_count+=1
        patch=im.crop(list(map(int,face['bounds'])))
        if face['flip_u_for_sample']:patch=ImageOps.mirror(patch)
        if face['flip_v_for_sample']:patch=ImageOps.flip(patch)
        if hashlib.sha256(patch.tobytes()).hexdigest()!=face['crop_rgba_sha256']:errors.append('UV crop pixel mismatch: '+row['bone'])
if sample_count!=uv_review['integer_nonzero_face_crops'] or zero_count!=uv_review['zero_area_faces_not_resampled']:errors.append('UV crop count mismatch')
uv_ext=json.loads((D/'reference-uv-extension.json').read_text())
uv_ext_review=json.loads((D/'reference-uv-extension-manual-review.json').read_text())
if set(uv_ext['sheets'])!={r['sheet'] for r in uv_ext_review['rows']}:errors.append('Extension UV review coverage mismatch')
if uv_ext_review['new_design_credit']!=0 or uv_ext_review['production_changes']!=0:errors.append('Unauthorized extension UV credit')
extension_models={};extension_pngs={};extension_faces=0
for src in uv_ext['sources']:
    jar=src['jar']
    if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
    if archive_hashes[jar]!=src['jar_sha256']:errors.append('Extension archive changed')
    for kind in ['model','png']:
        if hashlib.sha256((R/src[kind+'_local']).read_bytes()).hexdigest()!=src[kind+'_sha256']:errors.append('Extension source changed: '+src['name'])
        check_archive_entry(jar,src[kind+'_entry'],src[kind+'_sha256'])
    if hashlib.sha256((R/src['prior_local_png']).read_bytes()).hexdigest()!=src['png_sha256']:errors.append('Extension differs from previously reviewed PNG')
    g=json.loads((R/src['model_local']).read_text())['minecraft:geometry'][0]
    extension_models[src['name']]={(b['name'],i):c for b in g['bones'] for i,c in enumerate(b.get('cubes',[]))}
    extension_pngs[src['name']]=Image.open(R/src['png_local']).convert('RGBA')
for row in uv_ext['rows']:
    c=extension_models[row['source_name']][(row['bone'],row['cube_index'])]
    im=extension_pngs[row['source_name']]
    if row['cube_size']!=c['size'] or {f['face'] for f in row['faces']}!=set(c['uv']):errors.append('Extension cube/face source mismatch')
    if not (R/row['inspection_sheet']).is_file():errors.append('Extension sheet missing')
    for f in row['faces']:
        source_uv=c['uv'][f['face']]
        if f['uv']!=source_uv['uv'] or f['uv_size']!=source_uv['uv_size']:errors.append('Extension crop source UV mismatch')
        u,v0=source_uv['uv'];du,dv=source_uv['uv_size']
        if f['bounds']!=[min(u,u+du),min(v0,v0+dv),max(u,u+du),max(v0,v0+dv)] or f['flip_u']!=(du<0) or f['flip_v']!=(dv<0):errors.append('Extension crop bounds/flip mismatch')
        if f['status']!='SIGNED_INTEGER_CROP':errors.append('Unexpected unsampled extension face');continue
        extension_faces+=1
        patch=im.crop(list(map(int,f['bounds'])))
        if f['flip_u']:patch=ImageOps.mirror(patch)
        if f['flip_v']:patch=ImageOps.flip(patch)
        if hashlib.sha256(patch.tobytes()).hexdigest()!=f['crop_rgba_sha256']:errors.append('Extension crop pixels changed')
if extension_faces!=uv_ext_review['signed_integer_crops'] or len(uv_ext['rows'])!=uv_ext_review['cubes']:errors.append('Extension source totals mismatch')
alpha_edges=json.loads((D/'current-weapon-alpha-edge-correspondence.json').read_text())
for row in alpha_edges['rows']:
    for key in ['model','png']:
        if hashlib.sha256((R/row[key]).read_bytes()).hexdigest()!=row[key+'_sha256']:errors.append('Alpha edge source changed: '+row[key])
    for key in ['missing_segments','extra_segments','duplicate_segments','unmapped_geometry','side_uv_wrong_owner_pixel','side_uv_spans_multiple_png_texels']:
        if row[key]:errors.append('Alpha edge correspondence unresolved: '+row['model']+' '+key)
if alpha_edges['source_cutout_rule']['minimum_byte_alpha_at_full_modulation']!=26:errors.append('Unexpected alpha rule')
layer_binding=json.loads((D/'arctic-item-layer-binding.json').read_text())
for row in layer_binding['rows']:
    if hashlib.sha256((R/row['model_local_path']).read_bytes()).hexdigest()!=row['model_sha256']:errors.append('Arctic binding JSON changed')
    for src in row['source_pngs']:
        if hashlib.sha256((R/src['local_path']).read_bytes()).hexdigest()!=src['sha256']:errors.append('Arctic item layer changed')
layer_review=json.loads((D/'arctic-layer-manual-review.json').read_text())
if not (R/layer_review['inspection_sheet']).is_file() or layer_review['new_equipment_credit']!=0:errors.append('Arctic layer evidence invalid')
held_binding=json.loads((D/'held-item-source-binding.json').read_text())
held_review=json.loads((D/'held-item-manual-review.json').read_text())
held_pngs=0
for row in held_binding['rows']:
    jar=row['source_archive']
    if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
    if archive_hashes[jar]!=row['source_archive_sha256']:errors.append('Held item archive changed: '+jar)
    if hashlib.sha256((R/row['model_local_path']).read_bytes()).hexdigest()!=row['model_sha256']:errors.append('Held item model changed: '+row['item'])
    check_archive_entry(jar,row['model_entry'],row['model_sha256'])
    for src in row['source_pngs']:
        held_pngs+=1
        if hashlib.sha256((R/src['local_path']).read_bytes()).hexdigest()!=src['sha256']:errors.append('Held item source PNG changed: '+row['item'])
        check_archive_entry(jar,src['entry'],src['sha256'])
if held_pngs!=held_review['source_pngs_opened'] or held_review['new_equipment_case_credit']!=0:errors.append('Held item source evidence count/credit invalid')
if not (R/held_review['inspection_sheet']).is_file():errors.append('Held item review sheet missing')
register=json.loads((D/'semantic-applicability-register.json').read_text())
animation17=json.loads((D/'batch17-animation-source.json').read_text())
animation17_review=json.loads((D/'batch17-animation-manual-review.json').read_text())
if not (R/animation17_review['inspection_sheet']).is_file():errors.append('Batch17 animation sheet missing')
animation17_tiles=0
for row in animation17['rows']:
    meta_path=R/row['metadata_local']
    if hashlib.sha256(meta_path.read_bytes()).hexdigest()!=row['metadata_sha256']:errors.append('Batch17 animation metadata changed')
    check_archive_entry(row['jar'],row['metadata_entry'],row['metadata_sha256'])
    im=Image.open(R/row['png']).convert('RGBA')
    animation=json.loads(meta_path.read_text())['animation']
    expected_sequence=[dict(index=n,time=animation.get('frametime',1)) if isinstance(n,int) else dict(index=n['index'],time=n.get('time',animation.get('frametime',1))) for n in animation.get('frames',list(range(im.height//im.width)))]
    if row['playback_sequence']!=expected_sequence or row['interpolate']!=animation.get('interpolate',False):errors.append('Batch17 animation schedule differs from source metadata')
    if hashlib.sha256((R/row['png']).read_bytes()).hexdigest()!=row['png_sha256']:errors.append('Batch17 animation PNG changed')
    used={r['index'] for r in row['playback_sequence']}
    for tile in row['tiles']:
        animation17_tiles+=1
        i=tile['index'];patch=im.crop((0,i*im.width,im.width,(i+1)*im.width))
        if hashlib.sha256(patch.tobytes()).hexdigest()!=tile['rgba_sha256']:errors.append('Batch17 frame crop changed')
        if tile['in_sequence']!=(i in used):errors.append('Batch17 source tile/schedule mismatch')
if animation17_tiles!=animation17_review['source_tiles_opened'] or animation17_review['new_design_credit']!=0:errors.append('Batch17 animation counts/credit invalid')
archery18=json.loads((D/'batch18-resource-bindings.json').read_text())
archery18_review=json.loads((D/'batch18-resource-manual-review.json').read_text())
archery_refs={r['reference_id']:r for r in json.loads((D/'review-batch-18.json').read_text())['rows']}
for model in archery18['models']:
    jar=model['jar']
    if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
    if archive_hashes[jar]!=model['jar_sha256']:errors.append('Archery18 model archive changed')
    data=(R/model['local_path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=model['sha256']:errors.append('Archery18 model JSON changed')
    check_archive_entry(jar,model['entry'],model['sha256'])
    src=json.loads(data)
    if model['parent']!=src.get('parent') or model['overrides']!=src.get('overrides',[]) or model['display']!=src.get('display',{}):errors.append('Archery18 declaration differs from source')
    for layer in model['direct_texture_layers']:
        if src['textures'][layer['layer']]!=layer['texture']:errors.append('Archery18 texture declaration mismatch')
        for ref in layer['source_references']:
            if archery_refs[ref]['jar']!=jar or archery_refs[ref]['path']!=layer['entry']:errors.append('Archery18 exact PNG reference mismatch')
animation=archery18['animation']
if hashlib.sha256((R/animation['metadata_local_path']).read_bytes()).hexdigest()!=animation['metadata_sha256']:errors.append('Archery18 animation metadata changed')
check_archive_entry(animation['jar'],animation['metadata_entry'],animation['metadata_sha256'])
im=Image.open(R/animation['png']).convert('RGBA')
if hashlib.sha256((R/animation['png']).read_bytes()).hexdigest()!=animation['png_sha256']:errors.append('Archery18 animated PNG changed')
for tile in animation['tiles']:
    i=tile['index'];patch=im.crop((0,i*im.width,im.width,(i+1)*im.width))
    if hashlib.sha256(patch.tobytes()).hexdigest()!=tile['rgba_sha256']:errors.append('Archery18 source animation tile changed')
if len(archery18['models'])!=archery18_review['model_jsons_read'] or archery18_review['new_design_credit']!=0:errors.append('Archery18 source binding count/credit invalid')
for sheet in archery18_review['supplemental_sheets_actually_opened']:
    if not (R/sheet).is_file():errors.append('Archery18 supplemental source sheet missing')
kimono=json.loads((D/'kimono-uv-source.json').read_text())
kimono_review=json.loads((D/'kimono-uv-manual-review.json').read_text())
jar=kimono['jar']
if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
if archive_hashes[jar]!=kimono['jar_sha256']:errors.append('Kimono archive changed')
for m in kimono['models']:
    data=(R/m['local_path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=m['sha256']:errors.append('Kimono source geometry changed')
    check_archive_entry(jar,m['entry'],m['sha256'])
geo=json.loads((R/kimono['models'][2]['local_path']).read_text())['minecraft:geometry'][0]
im=Image.open(R/kimono['png_local_path']).convert('RGBA')
if hashlib.sha256((R/kimono['png_local_path']).read_bytes()).hexdigest()!=kimono['png_sha256']:errors.append('Kimono PNG changed')
kimono_faces=0
for row in kimono['rows']:
    cube=next(b for b in geo['bones'] if b['name']==row['bone'])['cubes'][row['cube_index']]
    for f in row['faces']:
        kimono_faces+=1
        uv=cube['uv'][f['face']]
        if uv['uv']!=f['uv'] or uv['uv_size']!=f['uv_size']:errors.append('Kimono UV declaration mismatch')
        u,v=f['uv'];du,dv=f['uv_size'];bounds=[min(u,u+du),min(v,v+dv),max(u,u+du),max(v,v+dv)]
        if bounds!=f['bounds'] or f['flip_u']!=(du<0) or f['flip_v']!=(dv<0):errors.append('Kimono UV bounds/flip mismatch')
        patch=im.crop(bounds)
        if du<0:patch=ImageOps.mirror(patch)
        if dv<0:patch=ImageOps.flip(patch)
        if hashlib.sha256(patch.tobytes()).hexdigest()!=f['crop_rgba_sha256']:errors.append('Kimono exact UV crop mismatch')
for page in kimono_review['pages_actually_opened']:
    if not (R/page).is_file():errors.append('Kimono page absent')
if kimono_faces!=36 or kimono_review['new_design_credit']!=0:errors.append('Kimono count/acceptance invalid')
mask19=json.loads((D/'batch19-mask-comparison.json').read_text())
mask19_refs={r['reference_id']:r for r in json.loads((D/'review-batch-19.json').read_text())['rows']}
for pair in mask19['pairs']:
    a=mask19_refs[pair['a']];b=mask19_refs[pair['b']]
    pa=list(Image.open(R/a['local_path']).convert('RGBA').get_flattened_data())
    pb=list(Image.open(R/b['local_path']).convert('RGBA').get_flattened_data())
    expected={'all_rgba_different_pixels':sum(x!=y for x,y in zip(pa,pb)),
      'alpha_different_pixels':sum(x[3]!=y[3] for x,y in zip(pa,pb)),
      'nonzero_alpha_rgba_different_pixels':sum(x!=y for x,y in zip(pa,pb) if x[3] or y[3]),
      'both_zero_alpha_rgb_different_pixels':sum(x!=y for x,y in zip(pa,pb) if not x[3] and not y[3]),
      'mask26_different_pixels':sum((x[3]>=26)!=(y[3]>=26) for x,y in zip(pa,pb))}
    if any(pair[k]!=v for k,v in expected.items()):errors.append('Batch19 mask comparison mismatch: '+pair['a'])
for sheet in mask19['source_sheets_actually_opened']+mask19['detail_sheets_actually_opened']:
    if not (R/sheet).is_file():errors.append('Batch19 evidence sheet absent')
if mask19['formal_new_credit']!=0:errors.append('Batch19 unauthorized acceptance')
# Source PNG metadata checks: no new production/acceptance claims.
effects=json.loads((D/'existing-effect-source-check.json').read_text())
effects_review=json.loads((D/'existing-effect-manual-review.json').read_text())
for e in effects['rows']:
    for key in ['path','frozen_copy']:
        if hashlib.sha256((R/e[key]).read_bytes()).hexdigest()!=e['source_sha256']:errors.append('Existing effect source changed: '+e['name'])
    im=Image.open(R/e['path']).convert('RGBA');pix=list(im.get_flattened_data())
    expected={'dimensions':list(im.size),'alpha_bbox':list(im.getchannel('A').getbbox()) if im.getchannel('A').getbbox() else None,'nonzero_alpha_pixels':sum(p[3]>0 for p in pix),'partial_alpha_pixels':sum(0<p[3]<255 for p in pix),'visible_rgba_colors':len({p for p in pix if p[3]})}
    if any(e[k]!=v for k,v in expected.items()):errors.append('Existing effect pixel statistics changed: '+e['name'])
    if e['metadata']:
        for key in ['path','saved']:
            if hashlib.sha256((R/e['metadata'][key]).read_bytes()).hexdigest()!=e['metadata']['sha256']:errors.append('Existing effect metadata changed')
    elif Path(str(R/e['path'])+'.mcmeta').exists():errors.append('Previously absent effect metadata appeared')
    if e['name']=='tianjiang_stream' and any(len({im.getpixel((x,y)) for x in range(im.width)})!=1 for y in range(im.height)):errors.append('Water strip row-constant statement changed')
if effects['production_changes'] or effects_review['new_reference_credit']:errors.append('Unauthorized existing effect acceptance')
res22=json.loads((D/'batch22-resource-declarations.json').read_text())
for declaration in res22['declarations']:
    data=(R/declaration['local_path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=declaration['sha256'] or json.loads(data)!=declaration['content']:errors.append('Batch22 source declaration changed')
    check_archive_entry(declaration['jar'],declaration['entry'],declaration['sha256'])
if res22['formal_new_credit']:errors.append('Unauthorized batch22 acceptance')
# Additional source-only correspondence; no geometry/production changes.
face24=json.loads((D/'batch24-face-correspondence.json').read_text())
chain24=json.loads((D/'batch24-primary-model-chain.json').read_text())
for model in chain24['models']:
    data=(R/model['local_path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=model['sha256'] or json.loads(data)!=model['content']:errors.append('Batch24 source model declaration changed')
    check_archive_entry(chain24['jar'],model['entry'],model['sha256'])
van=face24['primary_vanilla_cube']
if hashlib.sha256((R/van['local_path']).read_bytes()).hexdigest()!=van['sha256']:errors.append('Batch24 primary vanilla cube changed')
check_archive_entry(van['jar'],van['entry'],van['sha256'])
refs24={r['reference_id']:r for r in json.loads((D/'review-batch-24.json').read_text())['rows']}
im=Image.open(R/refs24['VIS-934']['local_path']).convert('RGBA')
for row in face24['source_comparisons']:
    uv=chain24['models'][3]['content']['elements'][0]['faces'][row['face']]['uv']
    if uv!=row['uv']:errors.append('Batch24 UV differs from model')
    bounds=[int(min(uv[0],uv[2])*im.width/16),int(min(uv[1],uv[3])*im.height/16),int(max(uv[0],uv[2])*im.width/16),int(max(uv[1],uv[3])*im.height/16)]
    if row['pixel_bounds']!=bounds or row['flip_u']!=(uv[2]<uv[0]) or row['flip_v']!=(uv[3]<uv[1]):errors.append('Batch24 UV conversion mismatch')
    patch=im.crop(bounds)
    if row['flip_u']:patch=ImageOps.mirror(patch)
    if row['flip_v']:patch=ImageOps.flip(patch)
    if hashlib.sha256(patch.tobytes()).hexdigest()!=row['signed_crop_rgba_sha256']:errors.append('Batch24 source crop changed')
    if row['named_face_match_after']=='rotate180':patch=patch.transpose(Image.Transpose.ROTATE_180)
    target=Image.open(R/refs24[row['named_reference']]['local_path']).convert('RGBA')
    if patch.tobytes()!=target.tobytes():errors.append('Batch24 face correspondence differs')
if not face24['comparison_sheet_actually_opened'] or not (R/face24['comparison_sheet']).is_file():errors.append('Batch24 comparison evidence absent')
artifacts=json.loads((D/'existing-artifact-uv-source.json').read_text())
artifact_review=json.loads((D/'existing-artifact-uv-manual-review.json').read_text())
artifact_faces=0;artifact_comparisons=0
for row in artifacts['rows']:
    sources=[row['geo'],row['png']]+row.get('item_models',[])+([row['item_icon_png']] if row.get('item_icon_png') else [])
    for src in sources:
        for key in ['path','frozen_copy']:
            if hashlib.sha256((R/src[key]).read_bytes()).hexdigest()!=src['sha256']:errors.append('Existing artifact source changed: '+src['path'])
    geo=json.loads((R/row['geo']['path']).read_text())['minecraft:geometry'][0]
    im=Image.open(R/row['png']['path']).convert('RGBA')
    for f in row['faces']:
        artifact_faces+=1
        cube=next(b for b in geo['bones'] if b['name']==f['bone'])['cubes'][f['cube_index']]
        uv=cube['uv'][f['face']]
        if uv['uv']!=f['uv'] or uv['uv_size']!=f['uv_size']:errors.append('Existing artifact face changed')
        u,v=uv['uv'];du,dv=uv['uv_size'];tw=geo['description']['texture_width'];th=geo['description']['texture_height']
        bounds=[min(u,u+du)*im.width/tw,min(v,v+dv)*im.height/th,max(u,u+du)*im.width/tw,max(v,v+dv)*im.height/th]
        if bounds!=f['pixel_bounds']:errors.append('Existing artifact UV pixel conversion changed')
        patch=im.crop(f['pixel_bounds'])
        if f['uv_size'][0]<0:patch=ImageOps.mirror(patch)
        if f['uv_size'][1]<0:patch=ImageOps.flip(patch)
        if hashlib.sha256(patch.tobytes()).hexdigest()!=f['signed_crop_rgba_sha256']:errors.append('Existing artifact face pixels changed')
        if not f['within_atlas'] or not f['nonzero_alpha_pixels']:errors.append('Artifact UV unresolved')
    if row.get('item_models'):
        mesh=json.loads((R/row['item_models'][2]['path']).read_text())
        cubes=[c for b in geo['bones'] for c in b.get('cubes',[])]
        for c in row['item_mesh_geo_face_correspondence']:
            artifact_comparisons+=1
            guv=cubes[c['cube_flat_index']]['uv'][c['face']];u,v=guv['uv'];du,dv=guv['uv_size']
            normalized=[u*16/tw,v*16/th,(u+du)*16/tw,(v+dv)*16/th]
            actual=mesh['elements'][c['cube_flat_index']]['faces'][c['face']]['uv']
            if actual!=c['item_mesh_uv'] or normalized!=c['geo_normalized_uv'] or actual!=normalized or not c['same_rectangle']:errors.append('Artifact mesh/geo source UV mismatch')
if artifacts['face_crops']!=artifact_faces or artifacts['item_geo_uv_comparisons']!=artifact_comparisons:errors.append('Artifact source counts inconsistent')
if not artifacts['source_sheet_actually_opened'] or not (R/artifacts['source_sheet']).is_file() or artifacts['production_changes'] or artifact_review['new_art']:errors.append('Artifact manual evidence/production invalid')
def check_frozen_source(src):
    for key in ['path','frozen_copy']:
        if key in src and hashlib.sha256((R/src[key]).read_bytes()).hexdigest()!=src['sha256']:
            errors.append('Frozen/current source changed: '+src[key])
    if 'jar' in src:
        jar=src['jar']
        if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
        if archive_hashes[jar]!=src['jar_sha256']:errors.append('Pinned source archive changed: '+jar)
        check_archive_entry(jar,src['entry'],src['sha256'])
workshops=json.loads((D/'existing-workshop-material-source.json').read_text())
workshop_review=json.loads((D/'existing-workshop-material-manual-review.json').read_text())
workshop_pngs=set();workshop_faces=0
for row in workshops['rows']:
    for src in row['sources']:check_frozen_source(src)
    block=json.loads((R/row['sources'][0]['path']).read_text())
    item=json.loads((R/row['sources'][1]['path']).read_text())
    state=json.loads((R/row['sources'][2]['path']).read_text())
    faces=[f for e in block.get('elements',[]) for f in e.get('faces',{}).values()]
    workshop_faces+=len(faces)
    if len(faces)!=row['declared_faces'] or sum('uv' not in f for f in faces)!=row['faces_without_explicit_uv']:
        errors.append('Workshop face declarations changed: '+row['id'])
    if item.get('parent')!=row['item_parent'] or block.get('textures',{})!=row['block_texture_aliases']:
        errors.append('Workshop material chain changed: '+row['id'])
    if sorted({v['model'] for v in state.get('variants',{}).values()})!=row['state_model_declarations']:
        errors.append('Workshop state declaration changed: '+row['id'])
    for tex in row['textures']:
        check_frozen_source(tex['source']);workshop_pngs.add(tex['resource'])
        im=Image.open(R/tex['source']['frozen_copy']).convert('RGBA');pix=list(im.get_flattened_data())
        if list(im.size)!=tex['dimensions'] or len({p for p in pix if p[3]})!=tex['visible_rgba_colors']:
            errors.append('Workshop texture statistics changed')
if not workshops['sheet_actually_opened'] or not (R/workshops['sheet']).is_file() or workshops['production_changes']:
    errors.append('Workshop evidence/production boundary invalid')
if len(workshop_pngs)!=workshops['distinct_pngs'] or workshop_faces!=workshop_review['declared_faces']:
    errors.append('Workshop evidence counts changed')
offerings=json.loads((D/'existing-offering-source.json').read_text())
for row in offerings['rows']:
    for src in row['sources']:check_frozen_source(src)
    model=json.loads((R/row['sources'][0]['path']).read_text())
    im=Image.open(R/row['sources'][1]['path']).convert('RGBA')
    if model.get('loader')!=row['loader'] or model.get('original_texture')!=row['declared_original_texture']:
        errors.append('Offering original source declaration changed')
    if list(im.size)!=row['dimensions'] or list(im.getchannel('A').getbbox())!=row['alpha_bbox']:
        errors.append('Offering dimensions/alpha bounds changed')
    if not row['source_png_actually_opened'] or row['decision']!='PRESERVE_EXISTING_ORIGINAL_NO_REDRAW':
        errors.append('Offering manual preservation decision absent')
if offerings['production_changes'] or offerings['new_reference_credit']:errors.append('Offering unauthorized production/credit')
expanded=json.loads((D/'expanded-texture-uv-requirements.json').read_text())
expanded_source_changes=[s['file'] for s in expanded['sources'] if not Path(s['file']).is_file() or hashlib.sha256(Path(s['file']).read_bytes()).hexdigest()!=s['sha256']]
if register['original_stage_family_proposal_sum']!=proposals:errors.append('Stale stage proposal total in register')
if register['accepted_new_visual_credit']!=0 or register['production_gate_met'] is not False:errors.append('Unauthorized register acceptance')
for scope in register['scope_contribution']:
    if scope['original_threshold']!=1000 or scope['production_gate_met'] is not False or scope['new_accepted_visual_credit']!=0:errors.append('Scope gate changed: '+scope['scope'])
changed=[]
for a in json.loads((D/'production-baseline.json').read_text())['rows']:
    assets+=1
    if not (R/a['path']).is_file() or hashlib.sha256((R/a['path']).read_bytes()).hexdigest()!=a['sha256']:changed.append(a['path'])
# Shared-workspace changes are reported without assuming authorship or undoing them.
result={'checked_at':datetime.now(timezone.utc).isoformat(),'evidence_consistency':'PASS' if not errors else 'FAIL',
    'batches':batch_summary,'pngs_opened_including_exclusions':viewed,'proposed_families_pending_semantic_review':proposals,
    'formal_new_credit':0,'production_gate_met':False,'protected_source_paths':assets,
    'prior_icons_reopened_separately_not_new_credit':prior_opened,'local_archives_verified':len(archive_hashes),
    'current_weapon_model_states_checked':len(bindings['rows']),
    'reference_uv_models_flat_island_study':uv_crops['models'],'reference_uv_cubes_flat_island_study':len(uv_crops['rows']),
    'reference_uv_signed_nonzero_face_crops':sample_count,'reference_uv_zero_area_faces_not_resampled':zero_count,
    'extension_reference_uv_models':len(uv_ext['sources']),'extension_reference_uv_cubes':len(uv_ext['rows']),
    'extension_reference_uv_signed_face_crops':extension_faces,'extension_reference_uv_sheets':len(uv_ext['sheets']),
    'current_weapon_cutout_boundary_segments_checked':sum(r['expected_nonzero_alpha_boundary_segments'] for r in alpha_edges['rows']),
    'supplementary_arctic_source_item_pngs_opened_not_new_cases':layer_review['source_pngs_opened'],
    'supplementary_held_source_item_pngs_opened_not_new_cases':held_pngs,
    'batch17_animation_source_tiles_checked_not_new_cases':animation17_tiles,
    'batch18_archery_declared_source_model_jsons_checked':len(archery18['models']),
    'batch19_same_glyph_mask_pairs_compared':len(mask19['pairs']),
    'kimono_signed_face_crops':kimono_faces,
    'existing_effect_source_pngs_checked':len(effects['rows']),
    'batch22_primary_resource_jsons_checked':len(res22['declarations']),
    'batch24_source_atlas_face_comparisons':len(face24['source_comparisons']),
    'existing_artifact_source_faces_checked':artifact_faces,
    'existing_artifact_item_geo_uv_comparisons':artifact_comparisons,
    'existing_workshop_material_pngs_checked':len(workshop_pngs),
    'existing_workshop_declared_faces_not_unfolded':workshop_faces,
    'existing_offering_original_pngs_checked':len(offerings['rows']),
    'expanded_requirement_original_files':len(expanded['sources']),
    'expanded_requirement_source_files_changed_since_index':expanded_source_changes,
    'exact_local_archive_entry_payloads_checked':origin_entries_checked,
    'protected_paths_changed_since_baseline':changed,'errors':errors,
    'limits':'Hashes/counts verify evidence only, never quality, unique semantic examples, manual viewing, elapsed active hours, runtime or task completion.'}
(D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(bool(errors))
