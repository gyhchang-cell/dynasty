"""Read-only exhaustive PNG silhouette/explicit side-face correspondence."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import zipfile
from PIL import Image
D=Path(__file__).resolve().parent
R=D.parents[3]
bindings=json.loads((D/'current-weapon-uv-bindings.json').read_text())['rows']
directions={'west':(-1,0),'east':(1,0),'up':(0,-1),'down':(0,1)}
jar=Path('/Users/a15356015027/.gradle/caches/forge_gradle/mcp_repo/de/oceanlabs/mcp/mcp_config/1.20.1-20230612.114412/joined/downloadClient/client.jar')
jar_sha1=hashlib.sha1(jar.read_bytes()).hexdigest()
assert jar_sha1=='0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838'
shader_sources=[]
with zipfile.ZipFile(jar) as z:
    for name in ['rendertype_cutout','rendertype_entity_cutout','rendertype_entity_cutout_no_cull']:
        entry=f'assets/minecraft/shaders/core/{name}.fsh';data=z.read(entry)
        limit=float(re.search(r'color\.a\s*<\s*([0-9.]+)',data.decode())[1])
        shader_sources.append({'entry':entry,'sha256':hashlib.sha256(data).hexdigest(),'alpha_discard_below':limit})
assert {s['alpha_discard_below'] for s in shader_sources}=={0.1}
alpha_minimum=math.ceil(255*shader_sources[0]['alpha_discard_below'])
rows=[]
for binding in bindings:
    model=R/binding['model']; texture=R/binding['png']
    assert hashlib.sha256(model.read_bytes()).hexdigest()==binding['model_sha256']
    assert hashlib.sha256(texture.read_bytes()).hexdigest()==binding['png_sha256']
    doc=json.loads(model.read_text());im=Image.open(texture).convert('RGBA');w,h=im.size
    mask={(x,y) for y in range(h) for x in range(w) if im.getpixel((x,y))[3]>=alpha_minimum}
    expected={(x,y,face) for x,y in mask for face,(dx,dy) in directions.items() if (x+dx,y+dy) not in mask}
    raw_mask={(x,y) for y in range(h) for x in range(w) if im.getpixel((x,y))[3]>0}
    raw_expected={(x,y,face) for x,y in raw_mask for face,(dx,dy) in directions.items() if (x+dx,y+dy) not in raw_mask}
    observed=Counter();unmapped=[];wrong_source=[];rect_multitexel=[]
    for i,e in enumerate(doc.get('elements',[])):
        sides={k:v for k,v in e.get('faces',{}).items() if k in directions}
        if not sides:continue
        if e.get('rotation'):
            unmapped.append({'element':i,'reason':'rotated geometry not interpreted'});continue
        p=e['from'];q=e['to']
        bounds=[p[0]*w/16,(16-q[1])*h/16,q[0]*w/16,(16-p[1])*h/16]
        if not all(math.isclose(n,round(n),abs_tol=1e-7) for n in bounds):
            unmapped.append({'element':i,'reason':'geometry not on actual PNG pixel grid','bounds':bounds});continue
        x0,y0,x1,y1=map(round,bounds)
        for face,f in sides.items():
            if f.get('texture')!='#layer0' or 'uv' not in f:
                unmapped.append({'element':i,'face':face,'reason':'non-layer0 or inherited UV'});continue
            if face in ['west','east']:
                owners=[(x0 if face=='west' else x1-1,y) for y in range(y0,y1)]
            else:
                owners=[(x,y0 if face=='up' else y1-1) for x in range(x0,x1)]
            for x,y in owners:observed[x,y,face]+=1
            a,b,c,d=f['uv'];u0,u1=sorted([a*w/16,c*w/16]);v0,v1=sorted([b*h/16,d*h/16])
            # Open rectangle: integer boundary is not an extra pixel.
            texels={(x,y) for y in range(math.floor(v0),math.ceil(v1)) for x in range(math.floor(u0),math.ceil(u1))}
            if len(texels)>1:rect_multitexel.append({'element':i,'face':face,'texels':sorted(texels),'owner_pixels':owners})
            if len(owners)==1 and texels!={owners[0]}:
                wrong_source.append({'element':i,'face':face,'owners':owners,'uv_texels':sorted(texels)})
    actual=set(observed)
    rows.append({'weapon':binding['weapon'],'predicate':binding['predicate'],
        'model':binding['model'],'model_sha256':binding['model_sha256'],'png':binding['png'],'png_sha256':binding['png_sha256'],
        'png_size':[w,h],'alpha_values':sorted(set(im.getchannel('A').getdata())),
        'alpha_mask_minimum_byte':alpha_minimum,'pixels_with_alpha_1_to_25':len(raw_mask-mask),
        'raw_alpha_gt_zero_boundary_segments':len(raw_expected),
        'raw_alpha_gt_zero_is_not_correct_cutout_mask':True,
        'expected_nonzero_alpha_boundary_segments':len(expected),'observed_explicit_side_segments':sum(observed.values()),
        'missing_segments':sorted(expected-actual),'extra_segments':sorted(actual-expected),
        'duplicate_segments':[{'key':k,'count':v} for k,v in observed.items() if v>1],
        'unmapped_geometry':unmapped,'side_uv_wrong_owner_pixel':wrong_source,'side_uv_spans_multiple_png_texels':rect_multitexel,
        'conclusion':'STATIC_PIXEL_EDGE_CORRESPONDENCE_ONLY',
        'limit':'Pinned base-game 0.1 cutout alpha rule at full modulation, exact local unrotated pixel grid only; no rasterizer, effective runtime shader/resource-pack override, face winding, mip/filter, game scale, grasp or animation acceptance.'})
out={'recorded_at':datetime.now(timezone.utc).isoformat(),'purpose':'Actual existing PNG silhouette and side UV relationship, no production edit',
    'states':len(rows),'new_reference_credit':0,'production_changes':0,
    'source_cutout_rule':{'local_archive':str(jar),'archive_sha1':jar_sha1,
        'source_url':f'https://piston-data.mojang.com/v1/objects/{jar_sha1}/client.jar',
        'shader_entries':shader_sources,'minimum_byte_alpha_at_full_modulation':alpha_minimum,
        'existing_edge_generator':'tools/art/generate_handheld_edges.cjs',
        'existing_edge_generator_sha256':hashlib.sha256((R/'tools/art/generate_handheld_edges.cjs').read_bytes()).hexdigest(),
        'existing_edge_generator_rule':'data[(y*w+x)*4+3]>=26',
        'generator_was_read_not_executed':True},
    'resolved_false_positive_zh':'仅以 alpha>0 作为边界会把1..25透明残留当作边缘，产生假缺边/内边。按固定原版0.1 cutout规则重算，16状态均与现有侧面完全对应；未修改任何模型/PNG。',
    'rows':rows}
(D/'current-weapon-alpha-edge-correspondence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'states':len(rows),'boundary_segments':sum(r['expected_nonzero_alpha_boundary_segments'] for r in rows),
    'missing':sum(len(r['missing_segments']) for r in rows),'extra':sum(len(r['extra_segments']) for r in rows),
    'duplicate':sum(len(r['duplicate_segments']) for r in rows),'unmapped':sum(len(r['unmapped_geometry']) for r in rows),
    'wrong_source_pixel':sum(len(r['side_uv_wrong_owner_pixel']) for r in rows),
    'multitexel_uv':sum(len(r['side_uv_spans_multiple_png_texels']) for r in rows)}))
